"""
核心算法实现
1. 部分排序算法（Top 10）
2. 最短路径算法（Dijkstra）
3. TSP途经多点最短路径
4. 模糊查找算法
5. 无损压缩算法
"""
import heapq
import math
from typing import Dict, List, Tuple, Optional
from itertools import permutations
import gzip
import json
import math


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


def top_k_restaurants_by_sort(restaurants: List[dict], k: int = 10, sort_by: str = 'composite') -> List[dict]:
    """按指定维度对餐厅做 Top K 排序。"""
    return top_k_spots(restaurants, k, sort_by=sort_by)


def haversine_distance_m(lng1: float, lat1: float, lng2: float, lat2: float) -> float:
    """计算两点之间的球面距离，单位米。"""
    earth_radius_m = 6371000

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lng2 - lng1)

    a = (
        math.sin(delta_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return earth_radius_m * c


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



def _edge_penalty(edge: dict, start: int, end: Optional[int], current: int, neighbor: int) -> float:
    if edge.get('road_type', 'walk') != 'walk':
        return 0.0
    if current == start or neighbor == start or (end and (current == end or neighbor == end)):
        return 0.0
    if edge.get('from_node_type') == 'entrance' or edge.get('to_node_type') == 'entrance':
        return max(float(edge.get('distance', 0) or 0) * 0.6, 120.0)
    return 0.0



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



def _find_path_edge(graph: Dict[int, List[dict]], from_id: int, to_id: int, transport_mode: Optional[str] = None) -> Optional[dict]:
    fallback = None
    for edge in graph.get(from_id, []):
        if edge['to'] != to_id:
            continue
        if fallback is None:
            fallback = edge
        if transport_mode is None or _edge_supports_transport(edge, transport_mode):
            return edge
    return fallback



def calculate_path_distance(graph: Dict[int, List[dict]], path: List[int], transport_mode: Optional[str] = None) -> float:
    """计算路径总距离"""
    total = 0
    for i in range(len(path) - 1):
        from_id = path[i]
        to_id = path[i + 1]
        edge = _find_path_edge(graph, from_id, to_id, transport_mode)
        if edge:
            total += edge.get('distance', 0)
    return total



def calculate_path_duration(graph: Dict[int, List[dict]], path: List[int], transport_mode: str = 'walk') -> float:
    """计算路径总时间（秒）"""
    total = 0
    for i in range(len(path) - 1):
        from_id = path[i]
        to_id = path[i + 1]
        edge = _find_path_edge(graph, from_id, to_id, transport_mode)
        if edge and _edge_supports_transport(edge, transport_mode):
            total += _edge_weight(edge, 'shortest_time')
    return total



def extract_segment_transport_modes(graph: Dict[int, List[dict]], path: List[int], transport_mode: str = 'walk') -> List[str]:
    modes = []
    for i in range(len(path) - 1):
        from_id = path[i]
        to_id = path[i + 1]
        edge = _find_path_edge(graph, from_id, to_id, transport_mode)
        if edge:
            modes.append(_edge_transport_mode(edge, transport_mode))
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

    # 自适应 TSP 求解：n ≤ 12 用精确 DP，n > 12 用贪心+2-opt 启发式
    path, total_cost = _choose_tsp_solver(dist_matrix, n, return_to_start)
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


def _tsp_exact_dp(dist_matrix: Dict, n: int, start_idx: int = 0, return_to_start: bool = True) -> Tuple[Optional[List[int]], float]:
    """
    TSP 精确解 —— Held-Karp 状态压缩 DP

    时间复杂度：O(n²·2ⁿ)，空间复杂度：O(n·2ⁿ)
    适用于 n ≤ 15 的场景（校园/景区目的地数量通常在此范围内）

    算法原理：
      - dp[mask][i] = (min_cost, prev_node)
      - mask 的第 j 位为 1 表示节点 j 已被访问
      - 从只有一个节点的状态开始，逐步扩展访问集合
      - 最终从全集中恢复最优访问顺序

    Args:
        dist_matrix: 距离矩阵 dist_matrix[i][j] = i 到 j 的距离
        n: 节点总数（包含起点）
        start_idx: 起点在矩阵中的索引（通常为 0）
        return_to_start: 是否要求回到起点

    Returns:
        (order, total_cost)：order 为访问顺序的索引列表，total_cost 为总代价
        若无法求解则返回 (None, inf)
    """
    INF = float('inf')
    total_states = 1 << n

    # dp[mask][i] = (min_cost, prev_node)
    dp: List[List[Tuple[float, int]]] = [[(INF, -1) for _ in range(n)] for _ in range(total_states)]

    # 初始状态：只访问了起点
    dp[1 << start_idx][start_idx] = (0.0, -1)

    # 枚举所有状态
    for mask in range(total_states):
        # 起点必须在 mask 中（剪枝：跳过不可能的状态）
        if not (mask & (1 << start_idx)):
            continue

        for i in range(n):
            if not (mask & (1 << i)):
                continue
            cost_i, _ = dp[mask][i]
            if cost_i == INF:
                continue

            # 尝试扩展到未访问的节点 j
            for j in range(n):
                if mask & (1 << j):
                    continue
                edge_cost = dist_matrix[i].get(j, INF)
                if edge_cost == INF:
                    continue
                new_cost = cost_i + edge_cost
                new_mask = mask | (1 << j)
                if new_cost < dp[new_mask][j][0]:
                    dp[new_mask][j] = (new_cost, i)

    full_mask = (1 << n) - 1

    if return_to_start:
        # 找最优终点：访问完所有节点后能最低代价返回起点
        best_cost = INF
        best_end = -1
        for i in range(n):
            if i == start_idx:
                continue
            cost = dp[full_mask][i][0]
            if cost == INF:
                continue
            return_cost = dist_matrix[i].get(start_idx, INF)
            if return_cost == INF:
                continue
            total = cost + return_cost
            if total < best_cost:
                best_cost = total
                best_end = i

        if best_end == -1:
            return None, INF

        # 回溯重建路径
        order = []
        mask = full_mask
        curr = best_end
        while curr != -1:
            order.append(curr)
            _, prev = dp[mask][curr]
            mask ^= (1 << curr)
            curr = prev
        order.reverse()  # 现在是 start → ... → best_end
        order.append(start_idx)  # 回到起点
        return order, best_cost
    else:
        # 不需要回到起点：找访问完所有节点的最低代价
        best_cost = INF
        best_end = -1
        for i in range(n):
            if dp[full_mask][i][0] < best_cost:
                best_cost = dp[full_mask][i][0]
                best_end = i

        if best_end == -1:
            return None, INF

        # 回溯重建路径
        order = []
        mask = full_mask
        curr = best_end
        while curr != -1:
            order.append(curr)
            _, prev = dp[mask][curr]
            mask ^= (1 << curr)
            curr = prev
        order.reverse()
        return order, best_cost


def _choose_tsp_solver(dist_matrix: Dict, n: int, return_to_start: bool) -> Tuple[List[int], float]:
    """
    根据问题规模选择 TSP 求解策略：
      - n ≤ 12：状态压缩 DP 求精确最优解
      - n > 12：贪心 + 2-opt 启发式近似解
    """
    if n <= 12:
        order, cost = _tsp_exact_dp(dist_matrix, n, 0, return_to_start)
        if order is not None:
            return order, cost
        # DP 失败（如不连通），降级到启发式
    order = _greedy_tsp(dist_matrix, n, return_to_start)
    order = _two_opt_optimize(order, dist_matrix, return_to_start)
    return order, _calculate_tsp_distance(order, dist_matrix)


# ==================== 校园路网拥挤度模拟 ====================

import hashlib

def simulate_campus_congestion(
    edges: List[dict],
    nodes: List[dict],
    spot_name: str = "",
) -> Dict[int, float]:
    """
    为校园/景区内部路网模拟差异化拥挤度。

    设计原则：
      - 基于边 ID 做确定性哈希，同一条边每次计算结果相同
      - 不同道路类型有不同的基础拥挤范围
      - 靠近入口/食堂的区域拥挤度更高（瓶颈效应）

    拥挤度含义：∈ (0, 1]，真实速度 = 拥挤度 × 理想速度
      1.0 = 完全畅通
      0.5 = 速度减半（较拥挤）
      0.3 = 严重拥挤

    道路类型拥挤范围：
      - 主干步行道 : 0.70 ~ 1.00
      - 骑行道     : 0.65 ~ 0.95
      - 建筑间小径 : 0.45 ~ 0.85
      - 入口附近   : 0.35 ~ 0.65

    Returns:
        {edge_id: congestion_factor}
    """
    # 先找出关键区域节点（入口、食堂等）
    hotspot_node_ids = set()
    for n in nodes:
        name = (n.get('name') or '').lower()
        ntype = (n.get('node_type') or n.get('type', '')).lower()
        # 入口节点
        if ntype == 'entrance':
            hotspot_node_ids.add(n.get('id'))
        # 食堂、餐厅
        if any(kw in name for kw in ['食堂', '餐厅', 'canteen', '饭', '餐']):
            hotspot_node_ids.add(n.get('id'))
        # 校门
        if any(kw in name for kw in ['门', 'gate', '入口', '出口']):
            hotspot_node_ids.add(n.get('id'))

    congestion_map = {}

    for edge in edges:
        eid = edge.get('id', 0)
        road_type = edge.get('road_type', 'walk') or 'walk'
        from_id = edge.get('from_node_id', 0)
        to_id = edge.get('to_node_id', 0)

        # 用 edge_id 的 MD5 生成确定性种子
        seed = int(hashlib.md5(str(eid).encode()).hexdigest()[:8], 16)
        # 归一化到 [0, 1)
        base = (seed % 10000) / 10000.0

        # 根据道路类型设置基础拥挤范围
        if road_type == 'bike':
            # 骑行道：相对畅通
            lo, hi = 0.65, 0.95
        else:
            # 步行道：区分主干道和小路
            # 边长 > 80m 认为是主干道（教学楼间距），短边是小路
            dist = float(edge.get('distance', 50) or 50)
            if dist > 80:
                lo, hi = 0.70, 1.00  # 主干步行道
            else:
                lo, hi = 0.45, 0.85  # 建筑间小径

        congestion = lo + base * (hi - lo)

        # 靠近热点区域：额外降低 0.10 ~ 0.25
        if from_id in hotspot_node_ids or to_id in hotspot_node_ids:
            penalty = 0.10 + (seed % 1500) / 10000.0  # 0.10 ~ 0.25
            congestion = max(0.25, congestion - penalty)

        congestion_map[eid] = round(congestion, 4)

    return congestion_map


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


def fuzzy_search(query: str, candidates: List[str], threshold: float = 0.6) -> List[Tuple[str, float, int]]:
    """
    模糊搜索
    返回匹配度高于阈值的结果

    Args:
        query: 查询字符串
        candidates: 候选列表
        threshold: 相似度阈值

    Returns:
        [(匹配项, 相似度, 匹配优先级), ...]
        优先级: 0=完全匹配, 1=前缀匹配, 2=子串匹配, 3=模糊匹配
    """
    results = []
    query_lower = query.lower().strip()
    query_len = len(query_lower)

    if not query_lower:
        return []

    for candidate in candidates:
        candidate_lower = candidate.lower()

        if query_lower == candidate_lower:
            score = 1.0
            priority = 0
        elif candidate_lower.startswith(query_lower):
            score = 1.0
            priority = 1
        elif query_lower in candidate_lower:
            score = 1.0
            priority = 2
        else:
            distance = levenshtein_distance(query_lower, candidate_lower)
            max_len = max(query_len, len(candidate_lower))
            score = 1 - (distance / max_len) if max_len > 0 else 0
            priority = 3

        if score >= threshold:
            results.append((candidate, score, priority))

    return sorted(results, key=lambda x: (x[2], -x[1]))


def fuzzy_search_spots(spots: List[dict], query: str, threshold: float = 0.5) -> List[dict]:
    """模糊搜索景点"""
    if not query:
        return spots
    
    candidates = [s['name'] for s in spots]
    matches = fuzzy_search(query, candidates, threshold)
    
    # 构建结果
    name_to_spot = {s['name']: s for s in spots}
    result = []
    for name, score, priority in matches:
        spot = name_to_spot[name].copy()
        spot['_match_score'] = score
        spot['_match_priority'] = priority
        result.append(spot)
    
    return result


def fuzzy_search_restaurants(restaurants: List[dict], query: str, threshold: float = 0.5) -> List[dict]:
    """模糊搜索餐厅。"""
    if not query:
        return restaurants

    candidates = [r.get('name', '') for r in restaurants if r.get('name')]
    matches = fuzzy_search(query, candidates, threshold)

    name_to_restaurant = {}
    for restaurant in restaurants:
        name = restaurant.get('name')
        if name and name not in name_to_restaurant:
            name_to_restaurant[name] = restaurant

    result = []
    for name, score, priority in matches:
        restaurant = name_to_restaurant.get(name)
        if not restaurant:
            continue
        item = restaurant.copy()
        item['_match_score'] = score
        item['_match_priority'] = priority
        result.append(item)

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


# ==================== 6. 辅助工具函数 ====================

def haversine_distance_m(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    """使用 Haversine 公式计算两点之间的距离（米）"""
    R = 6371000  # 地球半径（米）
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c


def fuzzy_search_restaurants(restaurants: List[dict], query: str, threshold: float = 0.4) -> List[dict]:
    """模糊搜索餐厅（保留旧接口以兼容）"""
    return food_multi_field_search(restaurants, query)


def top_k_restaurants_by_sort(restaurants: List[dict], k: int = 10, sort_by: str = 'distance') -> List[dict]:
    """餐厅 Top K 排序（保留旧接口以兼容，内部转发到堆排序实现）"""
    return _heap_top_k_restaurants(restaurants, k, sort_by)


# ==================== 7. 附近美食模块：堆排序 Top-K（不使用全量排序）====================

class MaxHeap:
    """
    大顶堆 —— 手动实现，用于维护距离最小的 Top-K 元素

    使用场景：当需要从小到大取前 K 个时，维护一个大小为 K 的大顶堆。
    新元素若小于堆顶（当前 K 个中的最大值），则替换堆顶并下沉。
    最终堆内元素即为全局最小的 K 个。

    时间复杂度：单次插入 O(log K)，总体 O(N log K)
    """

    def __init__(self, max_size: int = 10):
        self._heap: List[Tuple] = []
        self._max_size = max_size

    def __len__(self) -> int:
        return len(self._heap)

    def peek(self) -> Optional[Tuple]:
        """返回堆顶（当前 K 个中的最大值），不弹出"""
        return self._heap[0] if self._heap else None

    def push(self, item: Tuple):
        """
        推入元素。item = (score, tiebreaker, data)

        - 堆未满：直接插入并上浮
        - 堆已满：仅当新元素 score < 堆顶 score 时替换堆顶并下沉
        """
        if len(self._heap) < self._max_size:
            self._heap.append(item)
            self._sift_up(len(self._heap) - 1)
        elif item[0] < self._heap[0][0]:
            self._heap[0] = item
            self._sift_down(0)

    def _sift_up(self, idx: int):
        """上浮操作：子节点大于父节点时交换"""
        while idx > 0:
            parent = (idx - 1) // 2
            if self._heap[idx][0] > self._heap[parent][0]:
                self._heap[idx], self._heap[parent] = (
                    self._heap[parent],
                    self._heap[idx],
                )
                idx = parent
            else:
                break

    def _sift_down(self, idx: int):
        """下沉操作：父节点小于最大子节点时交换"""
        n = len(self._heap)
        while True:
            largest = idx
            left = 2 * idx + 1
            right = 2 * idx + 2
            if left < n and self._heap[left][0] > self._heap[largest][0]:
                largest = left
            if right < n and self._heap[right][0] > self._heap[largest][0]:
                largest = right
            if largest != idx:
                self._heap[idx], self._heap[largest] = (
                    self._heap[largest],
                    self._heap[idx],
                )
                idx = largest
            else:
                break

    def get_sorted_ascending(self) -> List[Tuple]:
        """按 score 从小到大返回堆内所有元素"""
        return sorted(self._heap, key=lambda x: x[0])

    def get_data_ascending(self) -> List:
        """按 score 从小到大返回堆内所有数据（去掉 score 和 tiebreaker）"""
        return [item[2] for item in self.get_sorted_ascending()]


def _top_k_largest(restaurants: List[dict], k: int, key_func) -> List[dict]:
    """
    使用小顶堆（Python heapq）维护前 K 个最大元素

    适用场景：评分 / 热度 从大到小排序（降序）

    工作原理：
      - 维护一个大小为 K 的小顶堆，堆顶是 K 个元素中的最小值
      - 遍历所有元素，当新元素 > 堆顶时替换（堆顶是最小值，被更大的淘汰）
      - 最终堆中的 K 个元素即为全局最大的 K 个

    时间复杂度：O(N log K)，空间复杂度：O(K)
    """
    if k <= 0 or not restaurants:
        return []

    min_heap: List[Tuple] = []

    for rest in restaurants:
        score = key_func(rest)
        tiebreaker = rest.get('id', 0)

        if len(min_heap) < k:
            heapq.heappush(min_heap, (score, tiebreaker, rest))
        elif score > min_heap[0][0]:
            heapq.heapreplace(min_heap, (score, tiebreaker, rest))

    # 只对 K 个结果排序（K=10，非全量排序）
    result = [item[2] for item in min_heap]
    result.sort(key=lambda x: key_func(x), reverse=True)
    return result


def _top_k_smallest(restaurants: List[dict], k: int, key_func) -> List[dict]:
    """
    使用大顶堆（自实现 MaxHeap）维护前 K 个最小元素

    适用场景：距离从小到大排序（升序）

    工作原理：
      - 维护一个大小为 K 的大顶堆，堆顶是 K 个元素中的最大值
      - 遍历所有元素，当新元素 < 堆顶时替换（堆顶是最大值，被更小的淘汰）
      - 最终堆中的 K 个元素即为全局最小的 K 个

    时间复杂度：O(N log K)，空间复杂度：O(K)
    """
    if k <= 0 or not restaurants:
        return []

    max_heap = MaxHeap(max_size=k)

    for rest in restaurants:
        score = key_func(rest)
        tiebreaker = rest.get('id', 0)
        max_heap.push((score, tiebreaker, rest))

    return max_heap.get_data_ascending()


def _heap_top_k_restaurants(restaurants: List[dict], k: int = 10, sort_by: str = 'distance') -> List[dict]:
    """
    堆排序 Top-K 餐厅（核心调度函数）

    - sort_by='rating'：按评分降序 → 小顶堆
    - sort_by='popularity'：按热度降序 → 小顶堆
    - sort_by='distance'：按距离升序 → 大顶堆

    时间复杂度：O(N log K)，其中 K=10
    """
    if not restaurants:
        return []

    if sort_by == 'rating':
        def key_func(r):
            return float(r.get('rating') or 0)
        return _top_k_largest(restaurants, k, key_func)

    elif sort_by == 'popularity':
        def key_func(r):
            return int(r.get('heat_score') or 0)
        return _top_k_largest(restaurants, k, key_func)

    else:  # distance（默认）
        def key_func(r):
            d = r.get('distance_m')
            return float(d) if d is not None else float('inf')
        return _top_k_smallest(restaurants, k, key_func)


# ==================== 8. 多字段中文模糊搜索 ====================

def food_multi_field_search(restaurants: List[dict], keyword: str) -> List[dict]:
    """
    多字段联合模糊搜索 —— 支持中文子串匹配

    搜索字段（按优先级排序）：
      1. name（店名）—— 权重最高
      2. cuisine_type（菜系类型）
      3. window_name（窗口/档口名）

    匹配策略：
      - 子串包含（keyword in field）：天然支持中文模糊搜索
      - 完全匹配得分最高，部分匹配次之
      - 返回附带 matched_fields 和 match_score 的餐厅列表

    Args:
        restaurants: 餐厅列表
        keyword: 用户输入的搜索关键词

    Returns:
        匹配到的餐厅列表（附带 matched_fields, match_score）
    """
    if not keyword or not keyword.strip():
        return list(restaurants)

    kw = keyword.strip().lower()
    results = []

    for rest in restaurants:
        matched_fields = []
        match_score = 0.0

        name = (rest.get('name') or '').lower()
        cuisine = (rest.get('cuisine_type') or '').lower()
        window = (rest.get('window_name') or '').lower()

        # 店名匹配（优先级最高）
        if kw in name:
            matched_fields.append('name')
            if kw == name:
                match_score = max(match_score, 1.0)      # 完全匹配
            else:
                match_score = max(match_score, 0.85)     # 子串匹配

        # 菜系匹配
        if kw in cuisine:
            matched_fields.append('cuisine_type')
            match_score = max(match_score, 0.7)

        # 窗口/档口名匹配
        if window and kw in window:
            matched_fields.append('window_name')
            match_score = max(match_score, 0.65)

        if matched_fields:
            item = dict(rest)
            item['matched_fields'] = matched_fields
            item['match_score'] = match_score
            results.append(item)

    return results


# ==================== 9. 美食过滤与排序完整管线 ====================

def filter_and_rank_foods(
    foods: List[dict],
    keyword: str = None,
    cuisine: str = None,
    sort_by: str = 'distance',
    k: int = 10,
) -> Tuple[List[dict], int]:
    """
    美食过滤与排序的完整管线 —— 组合菜系过滤、模糊搜索、堆排序

    管线步骤：
      1. 菜系过滤（cuisine）：精确匹配 cuisine_type 字段
      2. 多字段模糊搜索（keyword）：搜索 name / cuisine_type / window_name
      3. 堆排序 Top-K（sort_by）：使用大/小顶堆取前 K 个，不做全量排序

    时间复杂度：O(N + N log K) ≈ O(N)，其中 K=10

    Args:
        foods: 餐厅列表
        keyword: 用户搜索关键词（可选）
        cuisine: 菜系过滤值，为 None 或 '全部' 时不过滤（可选）
        sort_by: 排序维度 — 'distance' / 'rating' / 'popularity'
        k: 返回数量，默认 10

    Returns:
        (result_list, matched_count)：
          - result_list: 经过滤、搜索、堆排序后的餐厅列表（最多 K 个）
          - matched_count: 堆排序前的匹配总数（用于前端展示"共找到N家"）
    """
    # Step 1: 菜系过滤（精确匹配）
    filtered = foods
    if cuisine and cuisine.strip() and cuisine != '全部':
        filtered = [f for f in filtered if (f.get('cuisine_type') or '') == cuisine]

    # Step 2: 多字段模糊搜索
    if keyword and keyword.strip():
        filtered = food_multi_field_search(filtered, keyword)

    # 记录堆排序前的匹配数量
    matched_count = len(filtered)

    # Step 3: 堆排序 Top-K（不使用全量排序）
    result = _heap_top_k_restaurants(filtered, k=k, sort_by=sort_by)

    return result, matched_count
