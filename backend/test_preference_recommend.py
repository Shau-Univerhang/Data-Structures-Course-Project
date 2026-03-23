"""
测试偏好推荐算法
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_recommend_with_preference():
    print("=" * 60)
    print("测试偏好推荐算法")
    print("=" * 60)
    
    # 测试1: 无偏好
    print("\n1. 北京 - 无偏好:")
    response = client.get("/api/spots/recommend?city=北京")
    data = response.json()
    print(f"   返回 {len(data['spots'])} 个景点")
    for i, spot in enumerate(data['spots'][:5]):
        print(f"   {i+1}. {spot['name']} (评分:{spot['rating']}, 热度:{spot['heat_score']})")
    
    # 测试2: 历史偏好
    print("\n2. 北京 - 偏好: history (历史人文):")
    response = client.get("/api/spots/recommend?city=北京&preferences=history")
    data = response.json()
    print(f"   返回 {len(data['spots'])} 个景点")
    for i, spot in enumerate(data['spots'][:5]):
        print(f"   {i+1}. {spot['name']} (评分:{spot['rating']}, 热度:{spot['heat_score']})")
    
    # 测试3: 必去偏好
    print("\n3. 北京 - 偏好: must_visit (必去打卡):")
    response = client.get("/api/spots/recommend?city=北京&preferences=must_visit")
    data = response.json()
    print(f"   返回 {len(data['spots'])} 个景点")
    for i, spot in enumerate(data['spots'][:5]):
        print(f"   {i+1}. {spot['name']} (评分:{spot['rating']}, 热度:{spot['heat_score']})")
    
    # 测试4: 美食偏好
    print("\n4. 北京 - 偏好: food (地道美食):")
    response = client.get("/api/spots/recommend?city=北京&preferences=food")
    data = response.json()
    print(f"   返回 {len(data['spots'])} 个景点")
    for i, spot in enumerate(data['spots'][:5]):
        print(f"   {i+1}. {spot['name']} (评分:{spot['rating']}, 热度:{spot['heat_score']})")
    
    # 测试5: 多个偏好
    print("\n5. 北京 - 偏好: history,museum (历史人文,博物馆):")
    response = client.get("/api/spots/recommend?city=北京&preferences=history,museum")
    data = response.json()
    print(f"   返回 {len(data['spots'])} 个景点")
    for i, spot in enumerate(data['spots'][:5]):
        print(f"   {i+1}. {spot['name']} (评分:{spot['rating']}, 热度:{spot['heat_score']})")

if __name__ == "__main__":
    test_recommend_with_preference()
