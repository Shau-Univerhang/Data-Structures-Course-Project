"""
路线规划API - 使用Dijkstra和TSP算法
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import sys
sys.path.append("..")

from models.database import get_db, RoadNode, RoadEdge, ScenicSpot
from algorithms.core import dijkstra, get_shortest_path, build_graph, calculate_path_distance, tsp_shortest_path

router = APIRouter()


# Pydantic模型
class RoutePlanRequest(BaseModel):
    spot_id: int
    start_node_id: int
    end_node_id: int
    strategy: str = "shortest_time"  # shortest_distance / shortest_time
    transport_mode: str = "walk"  # walk / bike / shuttle / car


class RoutePlanResponse(BaseModel):
    distance: float  # 总距离（米）
    duration: int  # 总时间（秒）
    path: List[dict]
    algorithm: str
    time_complexity: str


class MultiPointRouteRequest(BaseModel):
    spot_id: int
    start_node_id: int
    waypoint_ids: List[int]
    return_to_start: bool = True
    strategy: str = "shortest_time"
    transport_mode: str = "walk"


@router.post("/plan", response_model=RoutePlanResponse)
def plan_route(
    request: RoutePlanRequest,
    db: Session = Depends(get_db)
):
    """单目标最短路径规划（Dijkstra算法）"""
    # 获取道路数据
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
    
    # 构建图
    nodes_data = [{'id': n.id, 'name': n.name, 'location_lat': n.location_lat, 
                   'location_lng': n.location_lng, 'node_type': n.node_type} for n in nodes]
    edges_data = [{'from_node_id': e.from_node_id, 'to_node_id': e.to_node_id,
                   'distance': e.distance, 'congestion_factor': e.congestion_factor,
                   'is_bidirectional': e.is_bidirectional} for e in edges]
    
    graph = build_graph(nodes_data, edges_data)
    
    # 运行Dijkstra算法
    dist, prev = dijkstra(graph, request.start_node_id, request.end_node_id, request.transport_mode)
    
    # 重建路径
    path_ids = get_shortest_path(prev, request.start_node_id, request.end_node_id)
    
    # 构建路径详情
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
    
    # 计算距离和时间
    distance = calculate_path_distance(graph, path_ids)
    duration = int(dist.get(request.end_node_id, 0))
    
    return {
        "distance": distance,
        "duration": duration,
        "path": path,
        "algorithm": "dijkstra",
        "time_complexity": "O((V+E)logV)"
    }


@router.post("/plan-multi", response_model=RoutePlanResponse)
def plan_multi_point_route(
    request: MultiPointRouteRequest,
    db: Session = Depends(get_db)
):
    """途经多点最短路径规划（TSP算法）"""
    # 获取道路数据
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
    
    # 构建图
    nodes_data = [{'id': n.id, 'name': n.name, 'location_lat': n.location_lat, 
                   'location_lng': n.location_lng, 'node_type': n.node_type} for n in nodes]
    edges_data = [{'from_node_id': e.from_node_id, 'to_node_id': e.to_node_id,
                   'distance': e.distance, 'congestion_factor': e.congestion_factor,
                   'is_bidirectional': e.is_bidirectional} for e in edges]
    
    graph = build_graph(nodes_data, edges_data)
    
    # 运行TSP算法
    full_path, total_distance = tsp_shortest_path(
        graph, 
        request.start_node_id, 
        request.waypoint_ids,
        request.return_to_start
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
    
    # 构建路径详情
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
    
    # 估算时间（假设步行）
    duration = int(total_distance / 1.4)  # 步行速度
    
    return {
        "distance": total_distance,
        "duration": duration,
        "path": path,
        "algorithm": "tsp_greedy_2opt",
        "time_complexity": "O(n²)"
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
        "nodes": [{
            'id': n.id,
            'name': n.name,
            'lat': n.location_lat,
            'lng': n.location_lng,
            'type': n.node_type
        } for n in nodes]
    }


@router.get("/distance/{spot_id}")
def calculate_distance(
    spot_id: int,
    from_node_id: int,
    to_node_id: int,
    transport_mode: str = "walk",
    db: Session = Depends(get_db)
):
    """计算两点间距离"""
    nodes = db.query(RoadNode).filter(RoadNode.spot_id == spot_id).all()
    edges = db.query(RoadEdge).filter(RoadEdge.spot_id == spot_id).all()
    
    nodes_data = [{'id': n.id} for n in nodes]
    edges_data = [{'from_node_id': e.from_node_id, 'to_node_id': e.to_node_id,
                   'distance': e.distance, 'congestion_factor': e.congestion_factor,
                   'is_bidirectional': e.is_bidirectional} for e in edges]
    
    graph = build_graph(nodes_data, edges_data)
    dist, _ = dijkstra(graph, from_node_id, to_node_id, transport_mode)
    
    return {
        "distance": dist.get(to_node_id, 0),
        "from_node_id": from_node_id,
        "to_node_id": to_node_id
    }
