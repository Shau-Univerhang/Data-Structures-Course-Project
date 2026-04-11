"""
路线规划API - 使用Dijkstra和TSP算法
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
)

router = APIRouter()


# Pydantic模型
class RoutePlanRequest(BaseModel):
    spot_id: int
    start_node_id: int
    end_node_id: int
    strategy: str = "shortest_time"  # shortest_distance / shortest_time
    transport_mode: str = "walk"  # walk / bike / shuttle / car / smart


class RoutePlanResponse(BaseModel):
    distance: float  # 总距离（米）
    duration: int  # 总时间（秒）
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
        'id': node.id,
        'name': node.name,
        'lat': node.location_lat,
        'lng': node.location_lng,
        'type': node.node_type,
        'ref_id': node.ref_id,
    }



def _serialize_edge(edge: RoadEdge):
    return {
        'id': edge.id,
        'from_node_id': edge.from_node_id,
        'to_node_id': edge.to_node_id,
        'distance': edge.distance,
        'ideal_speed': edge.ideal_speed,
        'congestion_factor': edge.congestion_factor,
        'road_type': edge.road_type,
        'is_bidirectional': edge.is_bidirectional,
    }



def _build_graph_payload(nodes, edges):
    nodes_data = [
        {
            'id': n.id,
            'name': n.name,
            'location_lat': n.location_lat,
            'location_lng': n.location_lng,
            'node_type': n.node_type,
        }
        for n in nodes
    ]
    edges_data = [
        {
            'from_node_id': e.from_node_id,
            'to_node_id': e.to_node_id,
            'distance': e.distance,
            'ideal_speed': e.ideal_speed,
            'congestion_factor': e.congestion_factor,
            'road_type': e.road_type,
            'is_bidirectional': e.is_bidirectional,
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
    if spot_type == 'campus':
        return [
            {'value': 'walk', 'label': '步行'},
            {'value': 'bike', 'label': '骑行'},
            {'value': 'smart', 'label': '智能混合'},
        ]
    return [
        {'value': 'walk', 'label': '步行'},
        {'value': 'shuttle', 'label': '电瓶车'},
        {'value': 'smart', 'label': '智能混合'},
    ]



def _transport_label(transport_mode: str, spot_type: Optional[str]):
    resolved_mode = resolve_transport_mode(transport_mode, spot_type or 'scenic')
    return TRANSPORT_MODE_LABELS.get(resolved_mode, transport_mode)


@router.post("/plan", response_model=RoutePlanResponse)
def plan_route(
    request: RoutePlanRequest,
    db: Session = Depends(get_db)
):
    """单目标最短路径规划（Dijkstra算法）"""
    nodes = db.query(RoadNode).filter(RoadNode.spot_id == request.spot_id).all()
    edges = db.query(RoadEdge).filter(RoadEdge.spot_id == request.spot_id).all()

    if not nodes or not edges:
        return {
            "distance": 0,
            "duration": 0,
            "path": [],
            "algorithm": "dijkstra",
            "time_complexity": "O((V+E)logV)",
            "error": "道路数据不存在"
        }

    graph = _build_graph_payload(nodes, edges)
    dist, prev = dijkstra(
        graph,
        request.start_node_id,
        request.end_node_id,
        request.transport_mode,
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
            "ordered_waypoint_ids": [],
            "ordered_waypoint_names": [],
            "return_to_start": False,
            "error": f"使用{request.transport_mode}方式无法到达目标"
        }

    node_map = {n.id: n for n in nodes}
    path = []
    for node_id in path_ids:
        node = node_map.get(node_id)
        if node:
            path.append({
                'node_id': node.id,
                'lat': node.location_lat,
                'lng': node.location_lng,
                'name': node.name,
                'type': node.node_type
            })

    distance = calculate_path_distance(graph, path_ids)
    duration = int(calculate_path_duration(graph, path_ids)) if path_ids else 0

    return {
        "distance": distance,
        "duration": duration,
        "path": path,
        "algorithm": "dijkstra",
        "time_complexity": "O((V+E)logV)",
        "ordered_waypoint_ids": [request.end_node_id],
        "ordered_waypoint_names": [node_map[request.end_node_id].name] if request.end_node_id in node_map else [],
        "return_to_start": False,
        "error": None,
    }


@router.post("/plan-multi", response_model=RoutePlanResponse)
def plan_multi_point_route(
    request: MultiPointRouteRequest,
    db: Session = Depends(get_db)
):
    """途经多点最短路径规划（TSP算法）"""
    nodes = db.query(RoadNode).filter(RoadNode.spot_id == request.spot_id).all()
    edges = db.query(RoadEdge).filter(RoadEdge.spot_id == request.spot_id).all()

    if not nodes or not edges:
        return {
            "distance": 0,
            "duration": 0,
            "path": [],
            "algorithm": "tsp_greedy_2opt",
            "time_complexity": "O(n²)",
            "error": "道路数据不存在"
        }

    graph = _build_graph_payload(nodes, edges)
    full_path, ordered_point_ids, _, total_distance, total_duration = tsp_shortest_path(
        graph,
        request.start_node_id,
        request.waypoint_ids,
        request.return_to_start,
        request.transport_mode,
        request.strategy,
    )

    if not full_path:
        return {
            "distance": 0,
            "duration": 0,
            "path": [],
            "algorithm": "tsp_greedy_2opt",
            "time_complexity": "O(n²)",
            "error": "无法找到可行路径"
        }

    node_map = {n.id: n for n in nodes}
    path = []
    for node_id in full_path:
        node = node_map.get(node_id)
        if node:
            path.append({
                'node_id': node.id,
                'lat': node.location_lat,
                'lng': node.location_lng,
                'name': node.name,
                'type': node.node_type
            })

    ordered_waypoint_ids, ordered_waypoint_names = _build_ordered_waypoint_names(
        ordered_point_ids,
        request.waypoint_ids,
        node_map,
    )

    return {
        "distance": total_distance,
        "duration": int(total_duration),
        "path": path,
        "algorithm": "tsp_greedy_2opt",
        "time_complexity": "O(n²)",
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

    entrance_node = next((n for n in nodes if n.node_type == 'entrance'), None)
    available_modes = sorted({e.road_type for e in edges if e.road_type})

    return {
        "spot": {
            "id": spot.id,
            "name": spot.name,
            "city": spot.city,
            "type": spot.type,
            "category": spot.category,
        },
        "entrance_node_id": entrance_node.id if entrance_node else (nodes[0].id if nodes else None),
        "available_modes": available_modes,
        "nodes": [_serialize_node(n) for n in nodes],
        "edges": [_serialize_edge(e) for e in edges],
        "buildings": [
            {
                "id": b.id,
                "name": b.name,
                "type": b.type,
                "lat": b.location_lat,
                "lng": b.location_lng,
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


@router.get("/nodes/{spot_id}")
def get_spot_nodes(
    spot_id: int,
    node_type: Optional[str] = Query(None, description="节点类型筛选"),
    db: Session = Depends(get_db)
):
    """获取景区的道路节点"""
    query = db.query(RoadNode).filter(RoadNode.spot_id == spot_id)
    if node_type:
        query = query.filter(RoadNode.node_type == node_type)

    nodes = query.all()
    return {
        "nodes": [_serialize_node(n) for n in nodes]
    }


@router.get("/distance/{spot_id}")
def calculate_distance(
    spot_id: int,
    from_node_id: int,
    to_node_id: int,
    transport_mode: str = "walk",
    strategy: str = "shortest_time",
    db: Session = Depends(get_db)
):
    """计算两点间距离/代价"""
    nodes = db.query(RoadNode).filter(RoadNode.spot_id == spot_id).all()
    edges = db.query(RoadEdge).filter(RoadEdge.spot_id == spot_id).all()

    graph = _build_graph_payload(nodes, edges)
    dist, _ = dijkstra(graph, from_node_id, to_node_id, transport_mode, strategy)

    return {
        "distance": dist.get(to_node_id, 0),
        "from_node_id": from_node_id,
        "to_node_id": to_node_id
    }
