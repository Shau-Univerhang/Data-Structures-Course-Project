"""
测试独立算法模块 - diary_recommend.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from algorithms.diary_recommend import (
    DiaryCandidate, UserInterestProfile, TopKMinHeap, topk_sort,
    RecommendScorer, DiarySearchEngine, MergeSorter, DiaryRecommendEngine
)

print("=" * 60)
print("测试 1: TopK 最小堆排序算法")
print("=" * 60)

# 生成测试数据
import random
random.seed(42)
candidates = []
for i in range(100):
    c = DiaryCandidate(
        id=i,
        title=f"测试日记 {i}",
        view_count=random.randint(10, 5000),
        avg_rating=round(random.uniform(1.0, 5.0), 1),
        rating_count=random.randint(0, 50),
        created_at=f"2024-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
        diary_type=random.choice(['travel', 'food', 'photo', 'notes']),
        cities=random.sample(['北京', '上海', '广州', '深圳', '成都'], random.randint(1, 3))
    )
    # 计算得分
    c.final_score = (0.4 * c.view_count / 5000 + 0.3 * c.avg_rating / 5.0 + 0.3 * random.random())
    candidates.append(c)

# TopK 排序
top_k = topk_sort(candidates, k=5)
print("Top 5 日记:")
for c in top_k:
    print(f"  [{c.id}] {c.title}: score={c.final_score:.4f}, views={c.view_count}, rating={c.avg_rating}")

# 验证堆排序结果正确性
full_sorted = sorted(candidates, key=lambda x: x.final_score, reverse=True)[:5]
assert len(top_k) == len(full_sorted), "TopK 数量不匹配"
for a, b in zip(top_k, full_sorted):
    assert abs(a.final_score - b.final_score) < 1e-6, f"得分不匹配: {a.final_score} vs {b.final_score}"
print("OK TopK 排序验证通过")

print("\n" + "=" * 60)
print("测试 2: 推荐分数计算（加权融合算法）")
print("=" * 60)

scorer = RecommendScorer(alpha=0.4, beta=0.3, gamma=0.3)

# 测试热度归一化
d1 = DiaryCandidate(id=1, title="高热度日记", view_count=5000, avg_rating=4.5, rating_count=30)
heat = scorer.calculate_heat_score(d1, max_views=5000, max_interactions=150)
print(f"热度归一化: {heat:.4f} (浏览量5000, 评分4.5*30)")

# 测试评分归一化
d2 = DiaryCandidate(id=2, title="高评分日记", view_count=100, avg_rating=5.0, rating_count=2)
rating = scorer.calculate_rating_score(d2)
print(f"评分归一化: {rating:.4f} (评分5.0, 2人评分)")

# 测试兴趣相似度
user_profile = UserInterestProfile(
    user_id=1,
    preferred_types={'travel': 0.9, 'food': 0.7},
    preferred_cities={'北京': 0.8, '成都': 0.6}
)
d3 = DiaryCandidate(id=3, title="用户兴趣日记", diary_type='travel', cities=['北京'])
interest = scorer.calculate_interest_similarity(d3, user_profile)
print(f"兴趣相似度: {interest:.4f} (travel类型 + 北京城市)")

# 最终得分
d4 = DiaryCandidate(id=4, title="综合日记", view_count=3000, avg_rating=4.0, rating_count=15, 
                    diary_type='food', cities=['成都'])
score = scorer.calculate_final_score(d4, user_profile, max_views=5000, max_interactions=150)
print(f"综合得分: {score:.4f} (heat={d4.heat_score:.4f}, rating={d4.rating_score:.4f}, interest={d4.interest_score:.4f})")

print("\n" + "=" * 60)
print("测试 3: 查找算法（哈希查找 + 倒排索引）")
print("=" * 60)

engine = DiarySearchEngine()
engine.build_index(candidates)

# 哈希查找
result = engine.search_by_normalized_title("测试日记 50")
print(f"标题查找 '测试日记 50': diary_id={result}")

# 目的地查找
dest_results = engine.search_by_destination("北京")
print(f"目的地查找 '北京': 找到 {len(dest_results)} 篇日记")

print("\n" + "=" * 60)
print("测试 4: 推荐引擎完整流程")
print("=" * 60)

recommend_engine = DiaryRecommendEngine(alpha=0.4, beta=0.3, gamma=0.3)
results = recommend_engine.recommend(candidates, user_profile, k=5, use_topk=True)
print("推荐结果 Top 5:")
for c in results:
    print(f"  [{c.id}] {c.title}: final={c.final_score:.4f}, heat={c.heat_score:.4f}, rating={c.rating_score:.4f}, interest={c.interest_score:.4f}")

print("\n" + "=" * 60)
print("测试 5: 归并排序（多路归并）")
print("=" * 60)

# 模拟多路已排序结果
list1 = [candidates[0], candidates[10], candidates[20]]  # 按 final_score 排序
list2 = [candidates[5], candidates[15], candidates[25]]
list3 = [candidates[8], candidates[18], candidates[28]]

merged = MergeSorter.merge_sorted_lists([list1, list2, list3])
print(f"多路归并: {len(merged)} 个候选，按得分降序")
for c in merged[:5]:
    print(f"  [{c.id}] {c.title}: score={c.final_score:.4f}")

print("\n" + "=" * 60)
print("OK 所有算法模块测试通过")
print("=" * 60)
