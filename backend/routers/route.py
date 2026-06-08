"""
路线规划 API - 使用 Dijkstra / TSP / 图距离设施查询
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import math
import sys

sys.path.append("..")

from models.database import get_db, RoadNode, RoadEdge, ScenicSpot, Building, Facility
from algorithms.core import (
    dijkstra,
    get_shortest_path,
    build_graph,
    calculate_path_distance,
    tsp_shortest_path,
    calculate_path_duration,
    extract_segment_transport_modes,
    resolve_transport_mode,
    TRANSPORT_MODE_LABELS,
    fuzzy_search,
)

router = APIRouter()


def _duration_seconds(duration: float) -> int:
    """将浮点持续时间（秒）转为整数秒"""
    return max(0, int(round(duration)))


class RoutePlanRequest(BaseModel):
    spot_id: int
    start_node_id: int
    end_node_id: int
    strategy: str = "shortest_time"  # shortest_distance / shortest_time
    transport_mode: str = "walk"  # walk / bike / shuttle / smart


class RoutePlanResponse(BaseModel):
    distance: float
    duration: int
    path: List[dict]
    algorithm: str
    time_complexity: str
    transport_mode: str = "walk"
    transport_label: str = "步行"
    segment_transport_modes: List[str] = []
    start_node_id: Optional[int] = None
    start_node_name: str = ""
    ordered_stop_ids: List[int] = []
    ordered_stop_names: List[str] = []
    final_node_id: Optional[int] = None
    final_node_name: str = ""
    ordered_waypoint_ids: List[int] = []
    ordered_waypoint_names: List[str] = []
    return_to_start: bool = False
    error: Optional[str] = None


class MultiPointRouteRequest(BaseModel):
    spot_id: int
    start_node_id: int
    waypoint_ids: List[int]
    return_to_start: bool = True
    strategy: str = "shortest_time"
    transport_mode: str = "walk"


import re

EXCLUDED_FACILITY_TYPES = {"parking", "sports"}
NUMBERED_BUILDING_PATTERN = re.compile(r'^\d+号楼$')


def _is_excluded_facility(facility):
    """判断设施是否属于需要过滤的停车点或运动设施"""
    return facility.type in EXCLUDED_FACILITY_TYPES


def _is_excluded_building(building):
    """判断建筑是否属于需要过滤的几号楼"""
    return building.name and NUMBERED_BUILDING_PATTERN.match(building.name)


def _filter_nodes_and_edges(nodes, edges, facilities):
    """过滤掉停车点、运动设施和几号楼节点及相关边"""
    # Build lookup for excluded facility IDs (ref_id 关联的 Facility.id)
    excluded_facility_ids = {f.id for f in facilities if _is_excluded_facility(f)}

    # 收集需要排除的 road node IDs
    excluded_node_ids = set()
    for node in nodes:
        # 类型=facility 且关联的设施属于停车/运动
        if node.node_type == "facility" and node.ref_id in excluded_facility_ids:
            excluded_node_ids.add(node.id)
        # 类型=building 且名称匹配"数字+号楼"
        elif node.node_type == "building" and node.name and NUMBERED_BUILDING_PATTERN.match(node.name):
            excluded_node_ids.add(node.id)

    filtered_nodes = [n for n in nodes if n.id not in excluded_node_ids]
    filtered_edges = [
        e for e in edges
        if e.from_node_id not in excluded_node_ids and e.to_node_id not in excluded_node_ids
    ]

    return filtered_nodes, filtered_edges



def _serialize_node(node: RoadNode):
    return {
        "id": node.id,
        "name": node.name,
        "lat": node.location_lat,
        "lng": node.location_lng,
        "type": node.node_type,
        "ref_id": node.ref_id,
    }


def _serialize_edge(edge: RoadEdge):
    return {
        "id": edge.id,
        "from_node_id": edge.from_node_id,
        "to_node_id": edge.to_node_id,
        "distance": edge.distance,
        "ideal_speed": edge.ideal_speed,
        "congestion_factor": edge.congestion_factor,
        "road_type": edge.road_type,
        "is_bidirectional": edge.is_bidirectional,
    }


def _build_graph_payload(nodes, edges):
    nodes_data = [
        {
            "id": n.id,
            "name": n.name,
            "location_lat": n.location_lat,
            "location_lng": n.location_lng,
            "node_type": n.node_type,
        }
        for n in nodes
    ]
    edges_data = [
        {
            "from_node_id": e.from_node_id,
            "to_node_id": e.to_node_id,
            "distance": e.distance,
            "ideal_speed": e.ideal_speed,
            "congestion_factor": e.congestion_factor,
            "road_type": e.road_type,
            "is_bidirectional": e.is_bidirectional,
        }
        for e in edges
    ]
    return build_graph(nodes_data, edges_data)


def _build_ordered_waypoint_names(path_ids, waypoint_ids, node_map):
    waypoint_set = set(waypoint_ids)
    ordered_names = []
    ordered_ids = []
    for node_id in path_ids:
        if node_id in waypoint_set and (not ordered_ids or ordered_ids[-1] != node_id):
            ordered_ids.append(node_id)
            ordered_names.append(node_map[node_id].name)
    return ordered_ids, ordered_names


def _display_modes_for_spot(spot_type: Optional[str], available_modes: Optional[List[str]] = None):
    if spot_type == "campus":
        modes = [{"value": "walk", "label": "步行"}]
        available = set(available_modes or [])
        if "bike" in available:
            modes.append({"value": "bike", "label": "骑行"})
            modes.append({"value": "smart", "label": "智能混合"})
        return modes
    return [
        {"value": "walk", "label": "步行"},
        {"value": "shuttle", "label": "电瓶车"},
        {"value": "smart", "label": "智能混合"},
    ]


def _transport_label(transport_mode: str, spot_type: Optional[str]):
    resolved_mode = resolve_transport_mode(transport_mode, spot_type or "scenic")
    return TRANSPORT_MODE_LABELS.get(resolved_mode, transport_mode)


def _default_map_node_id(spot: ScenicSpot, nodes: List[RoadNode]):
    entrance_node = next((n for n in nodes if n.node_type == "entrance"), None)
    if entrance_node:
        return entrance_node.id

    anchor_nodes = [n for n in nodes if n.node_type in {"building", "facility"}]
    if not anchor_nodes:
        return nodes[0].id if nodes else None

    center_lng = spot.location_lng or 0
    center_lat = spot.location_lat or 0
    return min(
        anchor_nodes,
        key=lambda node: (node.location_lng - center_lng) ** 2 + (node.location_lat - center_lat) ** 2,
    ).id


def _serialize_path(path_ids, node_map):
    path = []
    for node_id in path_ids:
        node = node_map.get(node_id)
        if node:
            path.append({
                "node_id": node.id,
                "lat": node.location_lat,
                "lng": node.location_lng,
                "name": node.name,
                "type": node.node_type,
            })
    return path


def _build_stop_sequence(path_ids, start_node_id, terminal_node_id, waypoint_ids, node_map, return_to_start=False):
    waypoint_set = set(waypoint_ids)
    ordered_waypoint_ids = []
    ordered_waypoint_names = []
    for node_id in path_ids:
        if node_id in waypoint_set and (not ordered_waypoint_ids or ordered_waypoint_ids[-1] != node_id):
            ordered_waypoint_ids.append(node_id)
            ordered_waypoint_names.append(node_map[node_id].name)

    ordered_stop_ids = [start_node_id]
    ordered_stop_names = [node_map[start_node_id].name] if start_node_id in node_map else []
    ordered_stop_ids.extend(ordered_waypoint_ids)
    ordered_stop_names.extend(ordered_waypoint_names)

    final_node_id = terminal_node_id
    if terminal_node_id in node_map and (not ordered_stop_ids or ordered_stop_ids[-1] != terminal_node_id):
        ordered_stop_ids.append(terminal_node_id)
        ordered_stop_names.append(node_map[terminal_node_id].name)

    if return_to_start and path_ids and path_ids[-1] == start_node_id:
        final_node_id = start_node_id
        if not ordered_stop_ids or ordered_stop_ids[-1] != start_node_id:
            ordered_stop_ids.append(start_node_id)
            ordered_stop_names.append(node_map[start_node_id].name)

    final_node_name = node_map[final_node_id].name if final_node_id in node_map else ""
    return ordered_waypoint_ids, ordered_waypoint_names, ordered_stop_ids, ordered_stop_names, final_node_id, final_node_name


def _facility_categories(facilities):
    categories = []
    seen = set()
    for facility in facilities:
        if facility.type and facility.type not in seen:
            seen.add(facility.type)
            categories.append(facility.type)
    return sorted(categories)


def _normalize_facility_category(category: Optional[str], categories: List[str], keyword: str = ""):
    raw = (category or "").strip().lower()
    if not raw or raw == "all":
        return None

    alias_map = {
        "超市": "supermarket",
        "便利店": "supermarket",
        "商店": "shop",
        "食堂": "canteen",
        "餐厅": "restaurant",
        "咖啡": "cafe",
        "咖啡店": "cafe",
        "医务室": "clinic",
        "校医院": "clinic",
        "医院": "clinic",
        "卫生间": "toilet",
        "厕所": "toilet",
        "快递": "express",
        "打印": "print",
        "图文": "print",
        "银行": "bank",
        "atm": "bank",
        "取款机": "bank",
        "运动": "sports",
        "球场": "sports",
    }
    if raw in alias_map:
        return alias_map[raw]

    if raw in categories:
        return raw

    candidates = list(categories) + list(alias_map.keys())
    matches = fuzzy_search(raw, candidates, threshold=0.45)
    if matches:
        match = matches[0][0]
        return alias_map.get(match, match)

    keyword_lower = keyword.strip().lower()
    for alias, canonical in alias_map.items():
        if alias in keyword_lower:
            return canonical

    return None


def _nearby_sort_strategy(strategy: Optional[str]):
    return "shortest_distance" if strategy == "shortest_distance" else "shortest_time"


def _indoor_navigation_payload(spot: ScenicSpot):
    if not spot or spot.type != "campus" or "北京邮电大学" not in (spot.name or ""):
        return None

    return {
        "default_building_name": "主楼",
        "buildings": [
            {
                "name": "主楼",
                "default_floor_id": "1F",
                "floors": [
                    {
                        "id": "1F",
                        "label": "1F",
                        "nodes": [
                            {"id": "gate", "label": "大门", "kind": "entrance", "x": 10, "y": 78},
                            {"id": "lobby", "label": "门厅", "kind": "hall", "x": 32, "y": 78},
                            {"id": "service", "label": "服务台", "kind": "service", "x": 32, "y": 52},
                            {"id": "elevator_1", "label": "电梯", "kind": "elevator", "x": 58, "y": 78},
                            {"id": "stairs_1", "label": "楼梯", "kind": "stairs", "x": 58, "y": 52},
                            {"id": "corridor_1", "label": "走廊", "kind": "corridor", "x": 82, "y": 78},
                        ],
                        "edges": [
                            ["gate", "lobby"],
                            ["lobby", "service"],
                            ["lobby", "elevator_1"],
                            ["service", "stairs_1"],
                            ["elevator_1", "corridor_1"],
                            ["stairs_1", "corridor_1"],
                        ],
                    },
                    {
                        "id": "2F",
                        "label": "2F",
                        "nodes": [
                            {"id": "elevator_2", "label": "电梯", "kind": "elevator", "x": 58, "y": 78},
                            {"id": "stairs_2", "label": "楼梯", "kind": "stairs", "x": 58, "y": 52},
                            {"id": "corridor_2", "label": "走廊", "kind": "corridor", "x": 82, "y": 78},
                            {"id": "restroom_2", "label": "卫生间", "kind": "room", "x": 92, "y": 56},
                            {"id": "room_201", "label": "201", "kind": "room", "x": 28, "y": 52},
                        ],
                        "edges": [
                            ["elevator_2", "corridor_2"],
                            ["stairs_2", "corridor_2"],
                            ["corridor_2", "restroom_2"],
                            ["stairs_2", "room_201"],
                        ],
                    },
                    {
                        "id": "3F",
                        "label": "3F",
                        "nodes": [
                            {"id": "elevator_3", "label": "电梯", "kind": "elevator", "x": 58, "y": 78},
                            {"id": "stairs_3", "label": "楼梯", "kind": "stairs", "x": 58, "y": 52},
                            {"id": "corridor_3", "label": "走廊", "kind": "corridor", "x": 82, "y": 78},
                            {"id": "room_301", "label": "301", "kind": "room", "x": 92, "y": 78},
                            {"id": "room_305", "label": "305", "kind": "room", "x": 92, "y": 52},
                        ],
                        "edges": [
                            ["elevator_3", "corridor_3"],
                            ["stairs_3", "corridor_3"],
                            ["corridor_3", "room_301"],
                            ["corridor_3", "room_305"],
                        ],
                    },
                ],
                "scenes": [
                    {
                        "id": "gate_to_elevator",
                        "label": "大门 → 电梯",
                        "description": "从建筑入口到楼内电梯的室内导航。",
                        "steps": [
                            {"floor_id": "1F", "path": ["gate", "lobby", "elevator_1"]},
                        ],
                    },
                    {
                        "id": "gate_to_room301",
                        "label": "大门 → 301 教室",
                        "description": "先到 1F 电梯，再切换到 3F，最后沿走廊到达教室。",
                        "steps": [
                            {"floor_id": "1F", "path": ["gate", "lobby", "elevator_1"]},
                            {"floor_id": "3F", "path": ["elevator_3", "corridor_3", "room_301"]},
                        ],
                    },
                    {
                        "id": "gate_to_restroom",
                        "label": "大门 → 2F 卫生间",
                        "description": "适合演示跨楼层设施查询和电梯导航。",
                        "steps": [
                            {"floor_id": "1F", "path": ["gate", "lobby", "elevator_1"]},
                            {"floor_id": "2F", "path": ["elevator_2", "corridor_2", "restroom_2"]},
                        ],
                    },
                ],
            }
        ],
    }


@router.post("/plan", response_model=RoutePlanResponse)
def plan_route(request: RoutePlanRequest, db: Session = Depends(get_db)):
    """单目标最短路径规划（Dijkstra 算法）"""
    spot = db.query(ScenicSpot).filter(ScenicSpot.id == request.spot_id).first()
    nodes = db.query(RoadNode).filter(RoadNode.spot_id == request.spot_id).all()
    edges = db.query(RoadEdge).filter(RoadEdge.spot_id == request.spot_id).all()

    if not nodes or not edges:
        return {
            "distance": 0,
            "duration": 0,
            "path": [],
            "algorithm": "dijkstra",
            "time_complexity": "O((V+E)logV)",
            "transport_mode": request.transport_mode,
            "transport_label": _transport_label(request.transport_mode, spot.type if spot else None),
            "segment_transport_modes": [],
            "error": "道路数据不存在",
        }

    resolved_mode = resolve_transport_mode(request.transport_mode, spot.type if spot else "scenic")
    graph = _build_graph_payload(nodes, edges)
    dist, prev = dijkstra(
        graph,
        request.start_node_id,
        request.end_node_id,
        resolved_mode,
        request.strategy,
    )
    path_ids = get_shortest_path(prev, request.start_node_id, request.end_node_id)
    if not path_ids:
        return {
            "distance": 0,
            "duration": 0,
            "path": [],
            "algorithm": "dijkstra",
            "time_complexity": "O((V+E)logV)",
            "transport_mode": request.transport_mode,
            "transport_label": _transport_label(request.transport_mode, spot.type if spot else None),
            "segment_transport_modes": [],
            "ordered_waypoint_ids": [],
            "ordered_waypoint_names": [],
            "return_to_start": False,
            "error": f"使用{_transport_label(request.transport_mode, spot.type if spot else None)}无法到达目标",
        }

    node_map = {n.id: n for n in nodes}
    segment_transport_modes = extract_segment_transport_modes(graph, path_ids, resolved_mode)
    distance = calculate_path_distance(graph, path_ids)
    duration = _duration_seconds(calculate_path_duration(graph, path_ids, resolved_mode)) if path_ids else 0

    return {
        "distance": distance,
        "duration": duration,
        "path": _serialize_path(path_ids, node_map),
        "algorithm": "dijkstra",
        "time_complexity": "O((V+E)logV)",
        "transport_mode": request.transport_mode,
        "transport_label": _transport_label(request.transport_mode, spot.type if spot else None),
        "segment_transport_modes": segment_transport_modes,
        "ordered_waypoint_ids": [request.end_node_id],
        "ordered_waypoint_names": [node_map[request.end_node_id].name] if request.end_node_id in node_map else [],
        "return_to_start": False,
        "error": None,
    }


@router.post("/plan-multi", response_model=RoutePlanResponse)
def plan_multi_point_route(request: MultiPointRouteRequest, db: Session = Depends(get_db)):
    """途经多点最短路径规划（TSP 算法）"""
    spot = db.query(ScenicSpot).filter(ScenicSpot.id == request.spot_id).first()
    nodes = db.query(RoadNode).filter(RoadNode.spot_id == request.spot_id).all()
    edges = db.query(RoadEdge).filter(RoadEdge.spot_id == request.spot_id).all()

    if not nodes or not edges:
        return {
            "distance": 0,
            "duration": 0,
            "path": [],
            "algorithm": "tsp_greedy_2opt",
            "time_complexity": "O(n²)",
            "transport_mode": request.transport_mode,
            "transport_label": _transport_label(request.transport_mode, spot.type if spot else None),
            "segment_transport_modes": [],
            "error": "道路数据不存在",
        }

    resolved_mode = resolve_transport_mode(request.transport_mode, spot.type if spot else "scenic")
    graph = _build_graph_payload(nodes, edges)
    full_path, ordered_point_ids, _, total_distance, total_duration, transport_modes = tsp_shortest_path(
        graph,
        request.start_node_id,
        request.waypoint_ids,
        request.return_to_start,
        resolved_mode,
        request.strategy,
    )

    if not full_path:
        return {
            "distance": 0,
            "duration": 0,
            "path": [],
            "algorithm": "tsp_greedy_2opt",
            "time_complexity": "O(n²)",
            "transport_mode": request.transport_mode,
            "transport_label": _transport_label(request.transport_mode, spot.type if spot else None),
            "segment_transport_modes": [],
            "error": "无法找到可行路径",
        }

    node_map = {n.id: n for n in nodes}
    ordered_waypoint_ids, ordered_waypoint_names = _build_ordered_waypoint_names(
        ordered_point_ids,
        request.waypoint_ids,
        node_map,
    )

    return {
        "distance": total_distance,
        "duration": _duration_seconds(total_duration),
        "path": _serialize_path(full_path, node_map),
        "algorithm": "tsp_greedy_2opt",
        "time_complexity": "O(n²)",
        "transport_mode": request.transport_mode,
        "transport_label": _transport_label(request.transport_mode, spot.type if spot else None),
        "segment_transport_modes": transport_modes,
        "ordered_waypoint_ids": ordered_waypoint_ids,
        "ordered_waypoint_names": ordered_waypoint_names,
        "return_to_start": request.return_to_start,
        "error": None,
    }


@router.get("/navigable-spots")
def get_navigable_spots(db: Session = Depends(get_db)):
    """
    返回存在道路网络数据（RoadNode + RoadEdge）的景区/校园列表。
    前端 RoutePlan 页面用此接口获取可导航的场所。
    """
    from sqlalchemy import distinct

    # 找出所有有道路节点的 spot_id
    rows = db.query(distinct(RoadNode.spot_id)).all()
    spot_ids = [row[0] for row in rows if row[0] is not None]

    if not spot_ids:
        return {"spots": []}

    spots = db.query(ScenicSpot).filter(ScenicSpot.id.in_(spot_ids)).all()

    return {
        "spots": [
            {
                "id": s.id,
                "name": s.name,
                "city": s.city,
                "type": s.type,
                "category": s.category,
                "location_lat": s.location_lat,
                "location_lng": s.location_lng,
            }
            for s in spots
        ]
    }


class SmartRouteRequest(BaseModel):
    """智能路由请求：自动识别单目标 Dijkstra 或多目标 TSP"""
    spot_id: int
    start_node_id: int
    destination_ids: List[int]  # 1 个=直达，≥2 个=巡游
    return_to_start: bool = True  # 巡游模式默认回到起点
    strategy: str = "shortest_time"
    transport_mode: str = "walk"


@router.post("/plan-smart", response_model=RoutePlanResponse)
def plan_smart_route(request: SmartRouteRequest, db: Session = Depends(get_db)):
    """
    智能路线规划 —— 自动场景识别

    场景 A（单目标直达）：1 个 destination + return_to_start=False
      → Dijkstra 算法，O((V+E)log V)

    场景 B（单目标往返）：1 个 destination + return_to_start=True
      → Dijkstra 往返拼接

    场景 C（多点巡游）：≥2 个 destination_ids
      → 自适应 TSP 求解：
         n ≤ 12：Held-Karp 状态压缩 DP 精确解，O(n²·2ⁿ)
         n > 12：贪心 + 2-opt 启发式近似，O(n²)
    """
    spot = db.query(ScenicSpot).filter(ScenicSpot.id == request.spot_id).first()
    nodes = db.query(RoadNode).filter(RoadNode.spot_id == request.spot_id).all()
    edges = db.query(RoadEdge).filter(RoadEdge.spot_id == request.spot_id).all()

    if not nodes or not edges:
        return {
            "distance": 0, "duration": 0, "path": [],
            "algorithm": "none", "time_complexity": "-",
            "transport_mode": request.transport_mode,
            "transport_label": _transport_label(request.transport_mode, spot.type if spot else None),
            "segment_transport_modes": [],
            "error": "道路数据不存在",
        }

    resolved_mode = resolve_transport_mode(request.transport_mode, spot.type if spot else "scenic")
    graph = _build_graph_payload(nodes, edges)
    node_map = {n.id: n for n in nodes}

    n_dests = len(request.destination_ids)
    from algorithms.core import _tsp_exact_dp, _choose_tsp_solver

    # ─── 场景 A：单目标直达（Dijkstra） ───
    if n_dests == 1 and not request.return_to_start:
        end_id = request.destination_ids[0]
        dist, prev = dijkstra(graph, request.start_node_id, end_id, resolved_mode, request.strategy)
        path_ids = get_shortest_path(prev, request.start_node_id, end_id)

        if not path_ids:
            return {
                "distance": 0, "duration": 0, "path": [],
                "algorithm": "dijkstra", "time_complexity": "O((V+E)logV)",
                "transport_mode": request.transport_mode,
                "transport_label": _transport_label(request.transport_mode, spot.type if spot else None),
                "segment_transport_modes": [],
                "error": "无法到达目标",
            }

        segment_modes = extract_segment_transport_modes(graph, path_ids, resolved_mode)
        distance = calculate_path_distance(graph, path_ids)
        duration = _duration_seconds(calculate_path_duration(graph, path_ids, resolved_mode))

        return {
            "distance": distance, "duration": duration,
            "path": _serialize_path(path_ids, node_map),
            "algorithm": "dijkstra", "time_complexity": "O((V+E)logV)",
            "transport_mode": request.transport_mode,
            "transport_label": _transport_label(request.transport_mode, spot.type if spot else None),
            "segment_transport_modes": segment_modes,
            "ordered_waypoint_ids": [end_id],
            "ordered_waypoint_names": [node_map[end_id].name] if end_id in node_map else [],
            "return_to_start": False,
            "error": None,
        }

    # ─── 场景 B：单目标往返 ───
    if n_dests == 1 and request.return_to_start:
        end_id = request.destination_ids[0]
        # A → B
        dist1, prev1 = dijkstra(graph, request.start_node_id, end_id, resolved_mode, request.strategy)
        path_ab = get_shortest_path(prev1, request.start_node_id, end_id)
        # B → A
        dist2, prev2 = dijkstra(graph, end_id, request.start_node_id, resolved_mode, request.strategy)
        path_ba = get_shortest_path(prev2, end_id, request.start_node_id)

        if not path_ab or not path_ba:
            return {
                "distance": 0, "duration": 0, "path": [],
                "algorithm": "dijkstra", "time_complexity": "O((V+E)logV)",
                "transport_mode": request.transport_mode,
                "transport_label": _transport_label(request.transport_mode, spot.type if spot else None),
                "segment_transport_modes": [],
                "error": "无法完成往返路径",
            }

        # 拼接路径（去重连接点）
        full_path = list(path_ab)
        if path_ba and full_path[-1] == path_ba[0]:
            full_path.extend(path_ba[1:])
        else:
            full_path.extend(path_ba)

        segment_modes_ab = extract_segment_transport_modes(graph, path_ab, resolved_mode)
        segment_modes_ba = extract_segment_transport_modes(graph, path_ba, resolved_mode)
        distance = calculate_path_distance(graph, full_path)
        duration = _duration_seconds(
            calculate_path_duration(graph, path_ab, resolved_mode) +
            calculate_path_duration(graph, path_ba, resolved_mode)
        )

        return {
            "distance": distance, "duration": duration,
            "path": _serialize_path(full_path, node_map),
            "algorithm": "dijkstra_roundtrip", "time_complexity": "O((V+E)logV)",
            "transport_mode": request.transport_mode,
            "transport_label": _transport_label(request.transport_mode, spot.type if spot else None),
            "segment_transport_modes": segment_modes_ab + segment_modes_ba,
            "start_node_id": request.start_node_id,
            "start_node_name": node_map[request.start_node_id].name if request.start_node_id in node_map else "",
            "ordered_stop_ids": [request.start_node_id, end_id, request.start_node_id],
            "ordered_stop_names": [
                node_map[request.start_node_id].name if request.start_node_id in node_map else "",
                node_map[end_id].name if end_id in node_map else "",
                node_map[request.start_node_id].name if request.start_node_id in node_map else "",
            ],
            "ordered_waypoint_ids": [end_id],
            "ordered_waypoint_names": [node_map[end_id].name] if end_id in node_map else [],
            "final_node_id": request.start_node_id,
            "final_node_name": node_map[request.start_node_id].name if request.start_node_id in node_map else "",
            "return_to_start": True,
            "error": None,
        }

    # ─── 场景 C：多点巡游（TSP） ───
    all_points = [request.start_node_id] + request.destination_ids
    all_point_ids = all_points
    n = len(all_points)

    # 构建距离矩阵和路径矩阵
    dist_matrix = {}
    path_matrix = {}
    INF = float('inf')

    for i, p1 in enumerate(all_points):
        dist_matrix[i] = {}
        path_matrix[i] = {}
        for j, p2 in enumerate(all_points):
            if i != j:
                d, prev = dijkstra(graph, p1, p2, resolved_mode, request.strategy)
                if d.get(p2, INF) < INF:
                    dist_matrix[i][j] = d[p2]
                    path_matrix[i][j] = get_shortest_path(prev, p1, p2)

    # 检查连通性
    for i in range(n):
        for j in range(n):
            if i != j and dist_matrix[i].get(j, INF) == INF:
                return {
                    "distance": 0, "duration": 0, "path": [],
                    "algorithm": "tsp", "time_complexity": "O(n²·2ⁿ)",
                    "transport_mode": request.transport_mode,
                    "transport_label": _transport_label(request.transport_mode, spot.type if spot else None),
                    "segment_transport_modes": [],
                    "error": f"节点 {all_points[i]} 到 {all_points[j]} 不连通",
                }

    # 自适应 TSP 求解
    tsp_order, tsp_cost = _choose_tsp_solver(dist_matrix, n, request.return_to_start)
    algo_name = "tsp_exact_dp" if n <= 12 else "tsp_greedy_2opt"
    algo_complexity = "O(n²·2ⁿ)" if n <= 12 else "O(n²)"

    # 拼接完整物理路径
    ordered_point_ids = [all_points[idx] for idx in tsp_order]
    full_path = []
    for step in range(len(tsp_order) - 1):
        from_idx = tsp_order[step]
        to_idx = tsp_order[step + 1]
        segment = path_matrix[from_idx][to_idx]
        if full_path and full_path[-1] == segment[0]:
            full_path.extend(segment[1:])
        else:
            full_path.extend(segment)

    total_distance = calculate_path_distance(graph, full_path)
    total_duration = _duration_seconds(calculate_path_duration(graph, full_path, resolved_mode))
    transport_modes = extract_segment_transport_modes(graph, full_path, resolved_mode)

    # 解析目的地访问顺序（排除起点重复）
    waypoint_set = set(request.destination_ids)
    ordered_wp_ids = []
    ordered_wp_names = []
    for nid in ordered_point_ids:
        if nid in waypoint_set and (not ordered_wp_ids or ordered_wp_ids[-1] != nid):
            ordered_wp_ids.append(nid)
            ordered_wp_names.append(node_map[nid].name if nid in node_map else "")

    start_name = node_map[request.start_node_id].name if request.start_node_id in node_map else ""
    ordered_stop_ids = [request.start_node_id] + ordered_wp_ids
    ordered_stop_names = [start_name] + ordered_wp_names
    final_id = ordered_point_ids[-1] if ordered_point_ids else request.start_node_id
    final_name = node_map[final_id].name if final_id in node_map else ""

    if request.return_to_start:
        ordered_stop_ids.append(request.start_node_id)
        ordered_stop_names.append(start_name)

    return {
        "distance": total_distance, "duration": total_duration,
        "path": _serialize_path(full_path, node_map),
        "algorithm": algo_name, "time_complexity": algo_complexity,
        "transport_mode": request.transport_mode,
        "transport_label": _transport_label(request.transport_mode, spot.type if spot else None),
        "segment_transport_modes": transport_modes,
        "start_node_id": request.start_node_id,
        "start_node_name": start_name,
        "ordered_stop_ids": ordered_stop_ids,
        "ordered_stop_names": ordered_stop_names,
        "ordered_waypoint_ids": ordered_wp_ids,
        "ordered_waypoint_names": ordered_wp_names,
        "final_node_id": final_id,
        "final_node_name": final_name,
        "return_to_start": request.return_to_start,
        "error": None,
    }


@router.get("/internal-map/{spot_id}")
def get_internal_map(spot_id: int, db: Session = Depends(get_db)):
    """获取景区/校园内部导航所需的完整数据"""
    spot = db.query(ScenicSpot).filter(ScenicSpot.id == spot_id).first()
    if not spot:
        return {"error": "景点不存在"}

    nodes = db.query(RoadNode).filter(RoadNode.spot_id == spot_id).all()
    edges = db.query(RoadEdge).filter(RoadEdge.spot_id == spot_id).all()
    buildings = db.query(Building).filter(Building.spot_id == spot_id).all()
    facilities = db.query(Facility).filter(Facility.spot_id == spot_id).all()

    # 过滤掉停车点、运动设施和几号楼
    nodes, edges = _filter_nodes_and_edges(nodes, edges, facilities)
    facilities = [f for f in facilities if not _is_excluded_facility(f)]
    buildings = [b for b in buildings if not _is_excluded_building(b)]

    default_node_id = _default_map_node_id(spot, nodes)
    available_modes = sorted({e.road_type for e in edges if e.road_type})

    return {
        "spot": {
            "id": spot.id,
            "name": spot.name,
            "city": spot.city,
            "type": spot.type,
            "category": spot.category,
            "location_lat": spot.location_lat,
            "location_lng": spot.location_lng,
        },
        "entrance_node_id": default_node_id,
        "available_modes": available_modes,
        "display_modes": _display_modes_for_spot(spot.type, available_modes),
        "facility_categories": _facility_categories(facilities),
        "indoor_navigation": _indoor_navigation_payload(spot),
        "nodes": [_serialize_node(n) for n in nodes],
        "edges": [_serialize_edge(e) for e in edges],
        "buildings": [
            {
                "id": b.id,
                "name": b.name,
                "type": b.type,
                "lat": b.location_lat,
                "lng": b.location_lng,
                "floor_count": b.floor_count,
                "description": b.description,
            }
            for b in buildings
        ],
        "facilities": [
            {
                "id": f.id,
                "name": f.name,
                "type": f.type,
                "lat": f.location_lat,
                "lng": f.location_lng,
                "description": f.description,
            }
            for f in facilities
        ],
    }


@router.get("/nearby-facilities")
def get_nearby_facilities(
    spot_id: int,
    origin_node_id: int,
    category: Optional[str] = Query(None, description="设施类别过滤"),
    keyword: Optional[str] = Query(None, description="设施名称/类别关键词"),
    radius_m: Optional[float] = Query(None, ge=0, description="图距离半径（米）"),
    top_k: int = Query(10, ge=1, le=50, description="返回数量"),
    transport_mode: str = Query("walk", description="交通方式"),
    strategy: str = Query("shortest_time", description="排序策略：shortest_time / shortest_distance"),
    db: Session = Depends(get_db),
):
    """查询某个节点附近的设施，按图距离或图时间排序，不按直线距离。"""
    spot = db.query(ScenicSpot).filter(ScenicSpot.id == spot_id).first()
    if not spot:
        return {"results": [], "error": "景点不存在"}

    nodes = db.query(RoadNode).filter(RoadNode.spot_id == spot_id).all()
    edges = db.query(RoadEdge).filter(RoadEdge.spot_id == spot_id).all()
    facilities = db.query(Facility).filter(Facility.spot_id == spot_id).all()
    facility_nodes = db.query(RoadNode).filter(
        RoadNode.spot_id == spot_id,
        RoadNode.node_type == "facility",
    ).all()

    # 过滤掉停车点和运动设施
    excluded_facility_ids = {f.id for f in facilities if _is_excluded_facility(f)}
    facilities = [f for f in facilities if not _is_excluded_facility(f)]
    facility_nodes = [fn for fn in facility_nodes if fn.ref_id not in excluded_facility_ids]

    if not nodes or not edges:
        return {"results": [], "error": "道路数据不存在"}

    categories = _facility_categories(facilities)
    keyword = (keyword or "").strip()
    normalized_category = _normalize_facility_category(category, categories, keyword)
    ranking_strategy = _nearby_sort_strategy(strategy)

    resolved_mode = resolve_transport_mode(transport_mode, spot.type or "scenic")
    graph = _build_graph_payload(nodes, edges)
    node_map = {n.id: n for n in nodes}
    facility_map = {f.id: f for f in facilities}
    dist_map, prev = dijkstra(graph, origin_node_id, None, resolved_mode, ranking_strategy)

    results = []

    for facility_node in facility_nodes:
        facility = facility_map.get(facility_node.ref_id)
        if not facility:
            continue
        if normalized_category and facility.type != normalized_category:
            continue

        candidate_text = " ".join([
            facility.name or "",
            facility.type or "",
            facility.description or "",
        ]).lower()
        if keyword and keyword.lower() not in candidate_text:
            alias_category = _normalize_facility_category(keyword, categories, keyword)
            if not alias_category or facility.type != alias_category:
                continue

        if dist_map.get(facility_node.id, float("inf")) == float("inf"):
            continue

        path_ids = get_shortest_path(prev, origin_node_id, facility_node.id)
        if not path_ids:
            continue

        distance = calculate_path_distance(graph, path_ids)
        if radius_m is not None and distance > radius_m:
            continue

        duration = _duration_seconds(calculate_path_duration(graph, path_ids, resolved_mode))
        results.append({
            "facility_id": facility.id,
            "node_id": facility_node.id,
            "name": facility.name,
            "type": facility.type,
            "description": facility.description,
            "lat": facility.location_lat,
            "lng": facility.location_lng,
            "distance": distance,
            "duration": duration,
            "transport_mode": transport_mode,
            "transport_label": _transport_label(transport_mode, spot.type),
            "segment_transport_modes": extract_segment_transport_modes(graph, path_ids, resolved_mode),
            "path": _serialize_path(path_ids, node_map),
        })

    if ranking_strategy == "shortest_distance":
        results.sort(key=lambda item: (item["distance"], item["duration"], item["name"]))
    else:
        results.sort(key=lambda item: (item["duration"], item["distance"], item["name"]))

    return {
        "origin_node_id": origin_node_id,
        "category": normalized_category or "all",
        "strategy": ranking_strategy,
        "facility_categories": categories,
        "results": results[:top_k],
    }


@router.get("/nodes/{spot_id}")
def get_spot_nodes(
    spot_id: int,
    node_type: Optional[str] = Query(None, description="节点类型筛选"),
    db: Session = Depends(get_db),
):
    """获取景区的道路节点"""
    query = db.query(RoadNode).filter(RoadNode.spot_id == spot_id)
    if node_type:
        query = query.filter(RoadNode.node_type == node_type)

    nodes = query.all()
    return {"nodes": [_serialize_node(n) for n in nodes]}


@router.get("/distance/{spot_id}")
def calculate_distance(
    spot_id: int,
    from_node_id: int,
    to_node_id: int,
    transport_mode: str = "walk",
    strategy: str = "shortest_time",
    db: Session = Depends(get_db),
):
    """计算两点间距离/代价"""
    spot = db.query(ScenicSpot).filter(ScenicSpot.id == spot_id).first()
    nodes = db.query(RoadNode).filter(RoadNode.spot_id == spot_id).all()
    edges = db.query(RoadEdge).filter(RoadEdge.spot_id == spot_id).all()

    graph = _build_graph_payload(nodes, edges)
    resolved_mode = resolve_transport_mode(transport_mode, spot.type if spot else "scenic")
    dist, _ = dijkstra(graph, from_node_id, to_node_id, resolved_mode, strategy)

    return {
        "distance": dist.get(to_node_id, 0),
        "from_node_id": from_node_id,
        "to_node_id": to_node_id,
        "transport_mode": transport_mode,
        "transport_label": _transport_label(transport_mode, spot.type if spot else None),
    }
