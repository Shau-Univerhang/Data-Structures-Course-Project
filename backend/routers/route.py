"""
路线规划 API - 使用 Dijkstra / TSP / 图距离设施查询
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
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


def _display_modes_for_spot(spot_type: Optional[str]):
    if spot_type == "campus":
        return [
            {"value": "walk", "label": "步行"},
            {"value": "bike", "label": "骑行"},
            {"value": "smart", "label": "智能混合"},
        ]
    return [
        {"value": "walk", "label": "步行"},
        {"value": "shuttle", "label": "电瓶车"},
        {"value": "smart", "label": "智能混合"},
    ]


def _transport_label(transport_mode: str, spot_type: Optional[str]):
    resolved_mode = resolve_transport_mode(transport_mode, spot_type or "scenic")
    return TRANSPORT_MODE_LABELS.get(resolved_mode, transport_mode)


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
    duration = int(calculate_path_duration(graph, path_ids, resolved_mode)) if path_ids else 0

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
        "duration": int(total_duration),
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

    entrance_node = next((n for n in nodes if n.node_type == "entrance"), None)
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
        "entrance_node_id": entrance_node.id if entrance_node else (nodes[0].id if nodes else None),
        "available_modes": available_modes,
        "display_modes": _display_modes_for_spot(spot.type),
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

        duration = int(calculate_path_duration(graph, path_ids, resolved_mode))
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
