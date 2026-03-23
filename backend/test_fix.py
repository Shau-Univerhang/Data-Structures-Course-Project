"""
测试修复后的推荐API
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test():
    print("=" * 60)
    print("测试修复后的推荐API")
    print("=" * 60)
    
    # 测试1: 北京博物展览
    print("\n1. 北京 - 偏好: museum (博物展览):")
    response = client.get("/api/spots/recommend?city=北京&preferences=museum")
    data = response.json()
    print(f"   返回 {len(data['spots'])} 个景点")
    for i, spot in enumerate(data['spots'][:5]):
        tags = ', '.join(spot.get('tags', []))
        print(f"   {i+1}. {spot['name']} [标签: {tags}]")
    
    # 测试2: 北京必玩景点
    print("\n2. 北京 - 偏好: must_visit (必玩景点):")
    response = client.get("/api/spots/recommend?city=北京&preferences=must_visit")
    data = response.json()
    print(f"   返回 {len(data['spots'])} 个景点")
    for i, spot in enumerate(data['spots'][:5]):
        tags = ', '.join(spot.get('tags', []))
        print(f"   {i+1}. {spot['name']} [标签: {tags}]")
    
    # 测试3: 北京历史文化
    print("\n3. 北京 - 偏好: history (历史文化):")
    response = client.get("/api/spots/recommend?city=北京&preferences=history")
    data = response.json()
    print(f"   返回 {len(data['spots'])} 个景点")
    for i, spot in enumerate(data['spots'][:5]):
        tags = ', '.join(spot.get('tags', []))
        print(f"   {i+1}. {spot['name']} [标签: {tags}]")

if __name__ == "__main__":
    test()
