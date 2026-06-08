"""
测试日记模块新接口
- FTS5 全文搜索
- 标题精确查询
- 目的地查询
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests

BASE = "http://localhost:8000/api/diaries"

print("=" * 60)
print("测试 1: FTS5 全文搜索 - 搜索'重庆'")
print("=" * 60)
r = requests.get(f"{BASE}/search", params={"q": "重庆", "page": 1, "page_size": 10, "sort": "relevance"})
print(f"状态码: {r.status_code}")
data = r.json()
print(f"总数: {data['total']}")
for d in data.get("diaries", []):
    print(f"  - [{d['id']}] {d['title']} | 作者: {d['author']} | 分数: {d.get('score', 'N/A')}")
    if d.get("snippet_content"):
        print(f"    摘要: {d['snippet_content'][:80]}...")

print("\n测试 1b: FTS5 全文搜索 - 搜索'美食'")
print("=" * 60)
r = requests.get(f"{BASE}/search", params={"q": "美食", "page": 1, "page_size": 10, "sort": "relevance"})
data = r.json()
print(f"总数: {data['total']}")
for d in data.get("diaries", []):
    print(f"  - [{d['id']}] {d['title']} | 作者: {d['author']}")

print("\n" + "=" * 60)
print("测试 2: 标题精确查询")
print("=" * 60)
# 先获取一个标题来测试
r_all = requests.get(f"{BASE}/", params={"page": 1, "page_size": 1})
if r_all.status_code == 200 and r_all.json():
    first_title = r_all.json()[0]["title"]
    print(f"测试标题: {first_title}")
    r_exact = requests.get(f"{BASE}/exact-title", params={"title": first_title})
    print(f"状态码: {r_exact.status_code}")
    data = r_exact.json()
    print(f"匹配数: {data['total']}")
    for d in data.get("diaries", []):
        print(f"  - [{d['id']}] {d['title']} | normalized: {d['normalized_title'][:30]}...")
else:
    print("没有日记可供测试")

print("\n" + "=" * 60)
print("测试 3: 目的地查询")
print("=" * 60)
r_dest = requests.get(f"{BASE}/by-destination", params={"destination": "北京", "sort": "hot"})
print(f"状态码: {r_dest.status_code}")
data = r_dest.json()
print(f"城市: {data.get('city', 'N/A')}")
print(f"总数: {data['total']}")
for d in data.get("diaries", []):
    print(f"  - [{d['id']}] {d['title']} | 浏览量: {d['view_count']} | 评分: {d['avg_rating']}")

print("\n" + "=" * 60)
print("所有测试完成")
print("=" * 60)
