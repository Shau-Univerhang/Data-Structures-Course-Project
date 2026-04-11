"""
核心算法实现
1. 部分排序算法（Top 10）
2. 最短路径算法（Dijkstra）
3. TSP途经多点最短路径
4. 模糊查找算法
5. 无损压缩算法
"""
import heapq
from typing import Dict, List, Tuple, Optional
from itertools import permutations
import gzip
import json


# ==================== 1. 部分排序算法（Top 10）====================

def top_k_spots(spots: List[dict], k: int = 50, sort_by: str = 'heat') -> List[dict]:
    """
    部分排序：只返回前k个景点，不完全排序
    时间复杂度：O(n log k)
    
    Args:
        spots: 景点列表
        k: 返回数量
        sort_by: 排序依据 ('heat'热度, 'rating'评分, 'composite'综合)
    
    Returns:
        排序后的前k个景点
    """
    if sort_by == 'heat':
        key_func = lambda x: x.get('heat_score', 0)
    elif sort_by == 'rating':
        key_func = lambda x: x.get('rating', 0)
    elif sort_by == 'composite':
        # 综合热度 = 热度分 * 0.6 + 评分 * 0.4
        key_func = lambda x: x.get('heat_score', 0) * 0.6 + x.get('rating', 0) * 100 * 0.4
    else:
        key_func = lambda x: x.get('heat_score', 0)
    
    # 使用最小堆，维护前k个最大元素
    min_heap = []
    for spot in spots:
        score = key_func(spot)
        if len(min_heap) < k:
            heapq.heappush(min_heap, (score, spot.get('id', 0), spot))
        elif score > min_heap[0][0]:
            heapq.heapreplace(min_heap, (score, spot.get('id', 0), spot))
    
    # 返回排序后的结果（降序）
    result = sorted([x[2] for x in min_heap], key=lambda x: key_func(x), reverse=True)
    return result


def top_k_restaurants(restaurants: List[dict], k: int = 10) -> List[dict]:
    """餐厅Top K排序（使用部分排序）"""
    return top_k_spots(restaurants, k, sort_by='composite')


# ==================== 2. 最短路径算法（Dijkstra）====================

ROAD_TYPE_DEFAULT_SPEED = {
    'walk': 1.4,      # 步行约5km/h
    'bike': 5.0,      # 骑行约18km/h
    'shuttle': 3.5,   # 电瓶车约12km/h
    'car': 8.3        # 驾车约30km/h
}

TRANSPORT_ALLOWED_ROAD_TYPES = {
    'walk': {'walk'},
    'bike': {'bike'},
    'shuttle': {'shuttle'},
    'car': {'car'},
    'smart_campus': {'walk', 'bike'},
    'smart_scenic': {'walk', 'shuttle'},
}


TRANSPORT_MODE_LABELS = {
    'walk': '步行',
    'bike': '骑行',
    'shuttle': '电瓶车',
    'smart_campus': '智能混合',
    'smart_scenic': '智能混合',
}


def resolve_transport_mode(transport_mode: str, spot_type: str = 'scenic') -> str:
    if transport_mode == 'smart':
        return 'smart_campus' if spot_type == 'campus' else 'smart_scenic'
    return transport_mode


def build_graph(nodes: List[dict], edges: List[dict]) -> Dict[int, List[dict]]:
    """
    构建图的邻接表表示

    Returns:
        {node_id: [edge, ...]}
    """
    graph = {node['id']: [] for node in nodes}

    for edge in edges:
        from_id = edge['from_node_id']
        to_id = edge['to_node_id']
        road_type = edge.get('road_type', 'walk')
        edge_data = {
            'to': to_id,
            'distance': float(edge.get('distance', 0) or 0),
            'congestion_factor': float(edge.get('congestion_factor', 1.0) or 1.0),
            'ideal_speed': float(edge.get('ideal_speed') or ROAD_TYPE_DEFAULT_SPEED.get(road_type, 1.4)),
            'road_type': road_type,
        }

        graph.setdefault(from_id, []).append(edge_data)

        if edge.get('is_bidirectional', True):
            reverse_edge = edge_data.copy()
            reverse_edge['to'] = from_id
            graph.setdefault(to_id, []).append(reverse_edge)

    return graph



def _edge_supports_transport(edge: dict, transport_mode: str) -> bool:
    allowed_road_types = TRANSPORT_ALLOWED_ROAD_TYPES.get(transport_mode, {'walk'})
    return edge.get('road_type', 'walk') in allowed_road_types



def _edge_transport_mode(edge: dict, transport_mode: str) -> str:
    road_type = edge.get('road_type', 'walk')
    if transport_mode == 'smart_campus':
        return 'bike' if road_type == 'bike' else 'walk'
    if transport_mode == 'smart_scenic':
        return 'shuttle' if road_type == 'shuttle' else 'walk'
    return transport_mode



def _edge_weight(edge: dict, strategy: str = 'shortest_time') -> float:
    distance = float(edge.get('distance', 0) or 0)
    if strategy == 'shortest_distance':
        return distance

    congestion = float(edge.get('congestion_factor', 1.0) or 1.0)
    congestion = min(max(congestion, 0.01), 1.0)
    ideal_speed = float(edge.get('ideal_speed', 1.4) or 1.4)
    actual_speed = max(ideal_speed * congestion, 0.01)
    return distance / actual_speed



def dijkstra(
    graph: Dict[int, List[dict]],
    start: int,
    end: Optional[int] = None,
    transport_mode: str = 'walk',
    strategy: str = 'shortest_time'
) -> Tuple[Dict[int, float], Dict[int, Optional[int]]]:
    """
    Dijkstra最短路径算法
    """
    dist = {node: float('inf') for node in graph}
    dist[start] = 0
    prev = {node: None for node in graph}

    pq = [(0, start)]
    visited = set()

    while pq:
        current_cost, current = heapq.heappop(pq)

        if current in visited:
            continue
        visited.add(current)

        if end and current == end:
            break

        for edge in graph.get(current, []):
            neighbor = edge['to']
            if neighbor in visited:
                continue
            if not _edge_supports_transport(edge, transport_mode):
                continue

            new_cost = current_cost + _edge_weight(edge, strategy)

            if new_cost < dist[neighbor]:
                dist[neighbor] = new_cost
                prev[neighbor] = current
                heapq.heappush(pq, (new_cost, neighbor))

    return dist, prev



def get_shortest_path(prev: Dict[int, Optional[int]], start: int, end: int) -> List[int]:
    """根据前驱表重建最短路径"""
    if prev.get(end) is None and start != end:
        return []

    path = []
    current = end
    while current is not None:
        path.append(current)
        if current == start:
            break
        current = prev[current]

    return list(reversed(path))



def calculate_path_distance(graph: Dict[int, List[dict]], path: List[int]) -> float:
    """计算路径总距离"""
    total = 0
    for i in range(len(path) - 1):
        from_id = path[i]
        to_id = path[i + 1]
        for edge in graph.get(from_id, []):
            if edge['to'] == to_id:
                total += edge.get('distance', 0)
                break
    return total



def calculate_path_duration(graph: Dict[int, List[dict]], path: List[int], transport_mode: str = 'walk') -> float:
    """计算路径总时间（秒）"""
    total = 0
    for i in range(len(path) - 1):
        from_id = path[i]
        to_id = path[i + 1]
        for edge in graph.get(from_id, []):
            if edge['to'] == to_id:
                if _edge_supports_transport(edge, transport_mode):
                    total += _edge_weight(edge, 'shortest_time')
                break
    return total



def extract_segment_transport_modes(graph: Dict[int, List[dict]], path: List[int], transport_mode: str = 'walk') -> List[str]:
    modes = []
    for i in range(len(path) - 1):
        from_id = path[i]
        to_id = path[i + 1]
        for edge in graph.get(from_id, []):
            if edge['to'] == to_id:
                modes.append(_edge_transport_mode(edge, transport_mode))
                break
    return modes


# ==================== 3. TSP途经多点最短路径 ====================


def tsp_shortest_path(
    graph: Dict[int, List[dict]],
    start: int,
    waypoints: List[int],
    return_to_start: bool = True,
    transport_mode: str = 'walk',
    strategy: str = 'shortest_time'
) -> Tuple[List[int], List[int], float, float, float, List[str]]:
    """
    途经多点的最短路径（TSP变种）
    使用贪心算法 + 2-opt优化

    Returns:
        (完整路径, 访问顺序节点ID, 总优化目标成本, 总距离, 总时间, 实际使用交通方式列表)
    """
    if not waypoints:
        return [start], [start], 0, 0, 0, []

    all_points = [start] + waypoints
    n = len(all_points)

    dist_matrix = {}
    path_matrix = {}

    for i, p1 in enumerate(all_points):
        dist_matrix[i] = {}
        path_matrix[i] = {}
        for j, p2 in enumerate(all_points):
            if i != j:
                dist, prev = dijkstra(graph, p1, p2, transport_mode, strategy)
                if dist[p2] < float('inf'):
                    dist_matrix[i][j] = dist[p2]
                    path_matrix[i][j] = get_shortest_path(prev, p1, p2)

    for i in range(n):
        for j in range(n):
            if i != j and dist_matrix[i].get(j, float('inf')) == float('inf'):
                return [], [], float('inf'), 0, 0, []

    path = _greedy_tsp(dist_matrix, n, return_to_start)
    path = _two_opt_optimize(path, dist_matrix, return_to_start)

    total_cost = _calculate_tsp_distance(path, dist_matrix)
    ordered_point_ids = [all_points[idx] for idx in path]

    full_path = []
    for i in range(len(path) - 1):
        from_idx = path[i]
        to_idx = path[i + 1]
        segment = path_matrix[from_idx][to_idx]
        if full_path and full_path[-1] == segment[0]:
            full_path.extend(segment[1:])
        else:
            full_path.extend(segment)

    total_distance = calculate_path_distance(graph, full_path)
    total_duration = calculate_path_duration(graph, full_path, transport_mode)
    transport_modes = extract_segment_transport_modes(graph, full_path, transport_mode)

    return full_path, ordered_point_ids, total_cost, total_distance, total_duration, transport_modes


def _greedy_tsp(dist_matrix: Dict, n: int, return_to_start: bool) -> List[int]:
    """贪心算法：每次选择最近的未访问节点"""
    unvisited = set(range(1, n))
    path = [0]
    current = 0
    
    while unvisited:
        nearest = min(unvisited, key=lambda x: dist_matrix[current][x])
        path.append(nearest)
        unvisited.remove(nearest)
        current = nearest
    
    if return_to_start:
        path.append(0)
    
    return path


def _two_opt_optimize(path: List[int], dist_matrix: Dict, return_to_start: bool) -> List[int]:
    """2-opt局部搜索优化"""
    improved = True
    best = path[:]
    best_cost = _calculate_tsp_distance(best, dist_matrix)
    
    while improved:
        improved = False
        end_idx = len(path) - 1 if return_to_start else len(path)
        
        for i in range(1, end_idx - 1):
            for j in range(i + 1, end_idx):
                # 反转i到j之间的路径
                new_path = best[:i] + best[i:j+1][::-1] + best[j+1:]
                new_cost = _calculate_tsp_distance(new_path, dist_matrix)
                
                if new_cost < best_cost - 0.001:  # 避免浮点误差
                    best = new_path
                    best_cost = new_cost
                    improved = True
                    break
            if improved:
                break
    
    return best


def _calculate_tsp_distance(path: List[int], dist_matrix: Dict) -> float:
    """计算TSP路径总距离"""
    total = 0
    for i in range(len(path) - 1):
        total += dist_matrix[path[i]][path[i+1]]
    return total


# ==================== 4. 模糊查找算法 ====================

def levenshtein_distance(s1: str, s2: str) -> int:
    """计算编辑距离"""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]


def fuzzy_search(query: str, candidates: List[str], threshold: float = 0.6) -> List[Tuple[str, float]]:
    """
    模糊搜索
    返回匹配度高于阈值的结果
    
    Args:
        query: 查询字符串
        candidates: 候选列表
        threshold: 相似度阈值
    
    Returns:
        [(匹配项, 相似度), ...]
    """
    results = []
    query_lower = query.lower().strip()
    
    if not query_lower:
        return []
    
    for candidate in candidates:
        candidate_lower = candidate.lower()
        
        # 完全匹配（子串）
        if query_lower in candidate_lower:
            score = 1.0
        else:
            # 计算编辑距离相似度
            distance = levenshtein_distance(query_lower, candidate_lower)
            max_len = max(len(query_lower), len(candidate_lower))
            score = 1 - (distance / max_len) if max_len > 0 else 0
        
        if score >= threshold:
            results.append((candidate, score))
    
    # 按相似度降序排序
    return sorted(results, key=lambda x: x[1], reverse=True)


def fuzzy_search_spots(spots: List[dict], query: str, threshold: float = 0.5) -> List[dict]:
    """模糊搜索景点"""
    if not query:
        return spots
    
    candidates = [s['name'] for s in spots]
    matches = fuzzy_search(query, candidates, threshold)
    
    # 构建结果
    name_to_spot = {s['name']: s for s in spots}
    result = []
    for name, score in matches:
        spot = name_to_spot[name].copy()
        spot['_match_score'] = score
        result.append(spot)
    
    return result


# ==================== 5. 无损压缩算法 ====================

def compress_diary(content: dict) -> bytes:
    """
    使用 gzip 压缩日记内容
    """
    json_bytes = json.dumps(content, ensure_ascii=False).encode('utf-8')
    compressed = gzip.compress(json_bytes, compresslevel=6)
    return compressed


def decompress_diary(compressed_data: bytes) -> dict:
    """
    解压日记内容
    """
    json_bytes = gzip.decompress(compressed_data)
    return json.loads(json_bytes.decode('utf-8'))


def calculate_compression_ratio(original: dict, compressed: bytes) -> float:
    """计算压缩率"""
    original_size = len(json.dumps(original, ensure_ascii=False).encode('utf-8'))
    compressed_size = len(compressed)
    ratio = (1 - compressed_size / original_size) * 100
    return ratio
