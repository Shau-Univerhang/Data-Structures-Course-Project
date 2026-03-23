"""
测试推荐API返回数量
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_recommend():
    # 测试北京
    response = client.get("/api/spots/recommend?city=北京")
    data = response.json()
    print(f"北京推荐景点数量: {len(data.get('spots', []))}")
    print(f"北京总景点数: {data.get('total', 0)}")
    
    # 打印前15个景点
    print("\n北京推荐景点:")
    for i, spot in enumerate(data.get('spots', [])[:15]):
        print(f"  {i+1}. {spot['name']}")

if __name__ == "__main__":
    test_recommend()
