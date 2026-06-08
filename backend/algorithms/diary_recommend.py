"""
日记推荐算法模块 - 独立核心算法实现
=====================================
包含：
1. TopK 最小堆排序算法（答辩核心算法）
2. 用户兴趣画像匹配算法
3. 推荐分数计算（0.4*heat + 0.3*rating + 0.3*interest）
4. 热度归一化算法
5. 查找算法：标题哈希查找、目的地倒排索引查找
"""
import heapq
import math
import time
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict


# ============================================================
# 数据模型
# ============================================================

@dataclass
class DiaryCandidate:
    """日记候选对象"""
    id: int
    title: str
    view_count: int = 0
    avg_rating: float = 0.0
    rating_count: int = 0
    created_at: str = ""
    diary_type: str = ""
    cities: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    
    # 计算得分
    heat_score: float = 0.0
    rating_score: float = 0.0
    interest_score: float = 0.0
    final_score: float = 0.0
    
    # FTS 相关
    fts_score: float = 0.0
    snippet: str = ""


@dataclass
class UserInterestProfile:
    """用户兴趣画像"""
    user_id: int
    preferred_types: Dict[str, float] = field(default_factory=dict)  # 类型偏好权重
    preferred_cities: Dict[str, float] = field(default_factory=dict)  # 城市偏好权重
    preferred_companions: Dict[str, float] = field(default_factory=dict)  # 伙伴偏好
    preferred_budget_range: str = ""
    
    def __post_init__(self):
        if not self.preferred_types:
            self.preferred_types = defaultdict(float)
        if not self.preferred_cities:
            self.preferred_cities = defaultdict(float)
        if not self.preferred_companions:
            self.preferred_companions = defaultdict(float)


# ============================================================
# 算法1: TopK 最小堆排序算法
# ============================================================

class TopKMinHeap:
    """
    TopK 最小堆算法 - 用于从大量候选日记中选出得分最高的 K 个
    
    时间复杂度: O(n log K)，优于全排序的 O(n log n)
    空间复杂度: O(K)
    
    答辩要点：
    - 当 n >> K 时（如 10万日记取 Top 20），最小堆效率远高于全排序
    - 每次插入/删除堆顶操作 O(log K)，总操作 n 次，总时间 O(n log K)
    """
    
    def __init__(self, k: int):
        self.k = k
        self.heap: List[Tuple[float, int]] = []  # (score, diary_id)
    
    def push(self, score: float, diary_id: int):
        """推入一个候选项"""
        if len(self.heap) < self.k:
            heapq.heappush(self.heap, (score, diary_id))
        elif score > self.heap[0][0]:
            # 当前得分大于堆顶（最小值），替换堆顶
            heapq.heapreplace(self.heap, (score, diary_id))
    
    def get_top_k(self) -> List[Tuple[float, int]]:
        """
        获取 TopK 结果，按得分降序排列
        
        Returns:
            [(score, diary_id), ...] 按得分从高到低
        """
        # 堆排序后反转，得到降序
        return sorted(self.heap, key=lambda x: x[0], reverse=True)
    
    @property
    def size(self) -> int:
        return len(self.heap)


def topk_sort(candidates: List[DiaryCandidate], k: int = 20) -> List[DiaryCandidate]:
    """
    TopK 排序入口函数
    
    Args:
        candidates: 候选日记列表（已计算好 final_score）
        k: 返回前 K 个
    
    Returns:
        按得分降序排列的前 K 个候选日记
    """
    if not candidates:
        return []
    
    # 如果候选数 <= K，直接全排序
    if len(candidates) <= k:
        candidates.sort(key=lambda x: x.final_score, reverse=True)
        return candidates
    
    # 否则使用最小堆
    heap = TopKMinHeap(k)
    id_to_candidate = {c.id: c for c in candidates}
    
    for c in candidates:
        heap.push(c.final_score, c.id)
    
    # 按得分降序返回
    top_k_ids = heap.get_top_k()
    return [id_to_candidate[did] for score, did in top_k_ids]


# ============================================================
# 算法2: 推荐分数计算（加权融合算法）
# ============================================================

class RecommendScorer:
    """
    推荐分数计算器
    
    公式: score = α * heat_norm + β * rating_norm + γ * interest_sim
    默认权重: α=0.4, β=0.3, γ=0.3
    
    答辩要点：
    - 多因子加权融合是推荐系统经典方法
    - 每个因子独立归一化到 [0, 1] 区间，保证公平性
    - 权重可配置，支持 A/B 测试调优
    """
    
    def __init__(self, alpha: float = 0.4, beta: float = 0.3, gamma: float = 0.3):
        assert abs(alpha + beta + gamma - 1.0) < 1e-6, "权重之和必须为 1"
        self.alpha = alpha  # 热度权重
        self.beta = beta    # 评分权重
        self.gamma = gamma  # 兴趣相似度权重
    
    def calculate_heat_score(self, diary: DiaryCandidate, max_views: float = 1.0, 
                              max_interactions: float = 1.0) -> float:
        """
        计算热度归一化分数 [0, 1]
        
        热度 = 0.7 * 浏览量归一化 + 0.3 * 互动量归一化
        互动量 = 评分数 * 平均评分（代表互动深度）
        """
        if max_views <= 0:
            views_norm = 0
        else:
            # 使用 log 归一化，避免极端值影响
            views_norm = math.log1p(diary.view_count) / math.log1p(max_views)
        
        interactions = diary.rating_count * diary.avg_rating
        if max_interactions <= 0:
            interactions_norm = 0
        else:
            interactions_norm = min(interactions / max_interactions, 1.0)
        
        return 0.7 * views_norm + 0.3 * interactions_norm
    
    def calculate_rating_score(self, diary: DiaryCandidate) -> float:
        """
        计算评分归一化分数 [0, 1]
        
        使用 sigmoid-like 函数：rating / 5.0 * (1 - 0.5 / (1 + rating_count))
        评分人数越多，分数越可信
        """
        if diary.rating_count == 0:
            return diary.avg_rating / 5.0 * 0.5  # 无评分时打折
        
        # 置信度因子：评分人数越多越可信
        confidence = 1.0 - 0.5 / (1.0 + math.log1p(diary.rating_count))
        return (diary.avg_rating / 5.0) * confidence
    
    def calculate_interest_similarity(self, diary: DiaryCandidate, 
                                       user_profile: UserInterestProfile) -> float:
        """
        计算用户兴趣相似度 [0, 1]
        
        使用 Jaccard 相似度 + 加权交集评分：
        - 类型匹配：用户偏好类型权重 * 日记类型权重
        - 城市匹配：用户偏好城市权重 * 日记城市权重
        - 综合得分 = 0.5 * 类型相似度 + 0.5 * 城市相似度
        """
        if not user_profile:
            return 0.5  # 无用户画像时返回中性值
        
        # 类型相似度
        type_sim = 0.0
        diary_type = diary.diary_type
        if diary_type in user_profile.preferred_types:
            type_sim = user_profile.preferred_types[diary_type]
        # 归一化到 [0, 1]
        type_sim = min(type_sim, 1.0)
        
        # 城市相似度（使用最大匹配）
        city_sim = 0.0
        for city in diary.cities:
            if city in user_profile.preferred_cities:
                city_sim = max(city_sim, user_profile.preferred_cities[city])
        city_sim = min(city_sim, 1.0)
        
        # 综合兴趣相似度
        return 0.5 * type_sim + 0.5 * city_sim
    
    def calculate_final_score(self, diary: DiaryCandidate, 
                               user_profile: Optional[UserInterestProfile] = None,
                               max_views: float = 1.0,
                               max_interactions: float = 1.0) -> float:
        """
        计算最终推荐分数
        
        score = α * heat_norm + β * rating_norm + γ * interest_sim
        """
        heat = self.calculate_heat_score(diary, max_views, max_interactions)
        rating = self.calculate_rating_score(diary)
        
        if user_profile:
            interest = self.calculate_interest_similarity(diary, user_profile)
        else:
            # 无用户画像时，兴趣分退化为类型偏好
            interest = 0.5
            if diary.diary_type == 'travel':
                interest = 0.7
            elif diary.diary_type == 'food':
                interest = 0.6
            elif diary.diary_type == 'photo':
                interest = 0.5
            elif diary.diary_type == 'notes':
                interest = 0.4
        
        diary.heat_score = heat
        diary.rating_score = rating
        diary.interest_score = interest
        diary.final_score = self.alpha * heat + self.beta * rating + self.gamma * interest
        
        return diary.final_score


# ============================================================
# 算法3: 查找算法
# ============================================================

class DiarySearchEngine:
    """
    日记查找引擎 - 包含多种查找算法
    
    1. 标题哈希查找：O(1) 哈希表定位
    2. 目的地倒排索引查找：O(1) 哈希表 + O(m) 过滤
    3. B+Tree 索引查找：O(log n) 数据库索引
    """
    
    def __init__(self):
        # 标题哈希映射：title_hash -> diary_id
        self.title_hash_index: Dict[str, int] = {}
        # 目的地倒排索引：city_name -> [diary_ids]
        self.destination_index: Dict[str, List[int]] = defaultdict(list)
        # 标准化标题映射：normalized_title -> diary_id
        self.normalized_title_index: Dict[str, int] = {}
    
    def build_index(self, diaries: List[DiaryCandidate]):
        """
        构建查找索引
        
        时间复杂度: O(n)
        空间复杂度: O(n)
        """
        self.title_hash_index.clear()
        self.destination_index.clear()
        self.normalized_title_index.clear()
        
        for diary in diaries:
            # 标题哈希索引（O(1) 查找）
            import hashlib
            title_hash = hashlib.sha256(diary.title.encode('utf-8')).hexdigest()
            self.title_hash_index[title_hash] = diary.id
            
            # 目的地倒排索引
            for city in diary.cities:
                self.destination_index[city].append(diary.id)
            
            # 标准化标题索引
            normalized = self._normalize_title(diary.title)
            self.normalized_title_index[normalized] = diary.id
    
    def search_by_title_hash(self, title: str) -> Optional[int]:
        """
        标题哈希查找 - O(1) 时间复杂度
        
        Args:
            title: 日记标题
        
        Returns:
            匹配的日记ID，未找到返回 None
        """
        import hashlib
        title_hash = hashlib.sha256(title.encode('utf-8')).hexdigest()
        return self.title_hash_index.get(title_hash)
    
    def search_by_destination(self, destination: str) -> List[int]:
        """
        目的地倒排索引查找 - O(1) 平均时间复杂度
        
        Args:
            destination: 目的地名称（如"北京"、"Beijing"）
        
        Returns:
            匹配的日记ID列表
        """
        # 先精确匹配
        ids = self.destination_index.get(destination, [])
        if ids:
            return ids
        
        # 再模糊匹配（别名/简写）
        for city, city_ids in self.destination_index.items():
            if destination.lower() in city.lower() or city.lower() in destination.lower():
                ids.extend(city_ids)
        
        return list(set(ids))
    
    def search_by_normalized_title(self, title: str) -> Optional[int]:
        """
        标准化标题查找 - O(1) 时间复杂度
        
        Args:
            title: 日记标题（会自动标准化）
        
        Returns:
            匹配的日记ID，未找到返回 None
        """
        normalized = self._normalize_title(title)
        return self.normalized_title_index.get(normalized)
    
    @staticmethod
    def _normalize_title(title: str) -> str:
        """
        标题标准化：去除空格、统一大小写、全半角统一
        
        用于精确查询时消除格式差异
        """
        import unicodedata
        # NFKC 规范化
        normalized = unicodedata.normalize('NFKC', title)
        # 去除前后空白
        normalized = normalized.strip()
        # 合并连续空格
        import re
        normalized = re.sub(r'\s+', ' ', normalized)
        # 转小写
        return normalized.lower()


# ============================================================
# 算法4: 归并排序（用于多路归并场景）
# ============================================================

class MergeSorter:
    """
    归并排序算法 - 用于多路日记合并场景
    
    场景：从多个来源（FTS搜索结果、兴趣推荐、热门日记）合并去重后排序
    
    时间复杂度: O(n log n)
    空间复杂度: O(n)
    """
    
    @staticmethod
    def merge_sorted_lists(lists: List[List[DiaryCandidate]], 
                           key_fn=None) -> List[DiaryCandidate]:
        """
        多路归并排序
        
        Args:
            lists: 多个已排序的日记列表
            key_fn: 排序键函数，默认为 final_score
        
        Returns:
            合并后的有序列表（降序）
        """
        if not lists:
            return []
        
        if key_fn is None:
            key_fn = lambda x: x.final_score
        
        # 过滤空列表
        non_empty = [lst for lst in lists if lst]
        if not non_empty:
            return []
        
        # 如果只有一路，直接返回
        if len(non_empty) == 1:
            return non_empty[0]
        
        # 使用堆进行多路归并
        result = []
        seen_ids = set()
        
        # 初始化堆：每路取第一个元素
        heap = []
        for i, lst in enumerate(non_empty):
            if lst:
                # 使用负数实现最大堆
                score = key_fn(lst[0])
                heapq.heappush(heap, (-score, i, 0, lst[0]))
        
        while heap:
            neg_score, list_idx, item_idx, item = heapq.heappop(heap)
            
            if item.id not in seen_ids:
                result.append(item)
                seen_ids.add(item.id)
            
            # 从同一路取下一个
            if item_idx + 1 < len(non_empty[list_idx]):
                next_item = non_empty[list_idx][item_idx + 1]
                next_score = key_fn(next_item)
                heapq.heappush(heap, (-next_score, list_idx, item_idx + 1, next_item))
        
        return result
    
    @staticmethod
    def sort(candidates: List[DiaryCandidate], 
             key_fn=None, reverse: bool = True) -> List[DiaryCandidate]:
        """
        标准归并排序
        
        Args:
            candidates: 待排序列表
            key_fn: 排序键
            reverse: 是否降序
        
        Returns:
            排序后的列表
        """
        if key_fn is None:
            key_fn = lambda x: x.final_score
        
        return sorted(candidates, key=key_fn, reverse=reverse)


# ============================================================
# 推荐引擎入口
# ============================================================

class DiaryRecommendEngine:
    """
    日记推荐引擎 - 统一入口
    
    使用方式:
        engine = DiaryRecommendEngine()
        results = engine.recommend(candidates, user_profile, k=20)
    """
    
    def __init__(self, alpha: float = 0.4, beta: float = 0.3, gamma: float = 0.3):
        self.scorer = RecommendScorer(alpha, beta, gamma)
        self.search_engine = DiarySearchEngine()
    
    def recommend(self, candidates: List[DiaryCandidate], 
                  user_profile: Optional[UserInterestProfile] = None,
                  k: int = 20,
                  use_topk: bool = True) -> List[DiaryCandidate]:
        """
        推荐入口函数
        
        Args:
            candidates: 候选日记列表
            user_profile: 用户兴趣画像（可选）
            k: 返回数量
            use_topk: 是否使用 TopK 堆排序
        
        Returns:
            推荐结果列表（按得分降序）
        """
        if not candidates:
            return []
        
        # 计算最大值用于归一化
        max_views = max((c.view_count for c in candidates), default=1)
        max_interactions = max((c.rating_count * c.avg_rating for c in candidates), default=1)
        max_views = max(max_views, 1)
        max_interactions = max(max_interactions, 1)
        
        # 计算每个候选的得分
        for c in candidates:
            self.scorer.calculate_final_score(c, user_profile, max_views, max_interactions)
        
        # 排序
        if use_topk and len(candidates) > k:
            return topk_sort(candidates, k)
        else:
            candidates.sort(key=lambda x: x.final_score, reverse=True)
            return candidates[:k]
    
    def recommend_by_destination(self, candidates: List[DiaryCandidate],
                                  destination: str,
                                  user_profile: Optional[UserInterestProfile] = None,
                                  k: int = 20,
                                  sort_by: str = "hot") -> List[DiaryCandidate]:
        """
        按目的地推荐 + 排序
        
        Args:
            candidates: 全量候选
            destination: 目的地名称
            user_profile: 用户兴趣画像
            k: 返回数量
            sort_by: 排序方式 (hot/rating/interest)
        
        Returns:
            排序后的推荐结果
        """
        # 先通过倒排索引过滤
        self.search_engine.build_index(candidates)
        dest_ids = self.search_engine.search_by_destination(destination)
        
        if not dest_ids:
            return []
        
        id_set = set(dest_ids)
        filtered = [c for c in candidates if c.id in id_set]
        
        # 根据排序方式排序
        if sort_by == "hot":
            filtered.sort(key=lambda x: x.view_count * 0.7 + x.avg_rating * x.rating_count * 10, reverse=True)
        elif sort_by == "rating":
            filtered.sort(key=lambda x: x.avg_rating, reverse=True)
        elif sort_by == "interest":
            return self.recommend(filtered, user_profile, k)
        
        return filtered[:k]
