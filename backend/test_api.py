"""
测试API是否正常工作
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import SessionLocal, ScenicSpot

def test_wuhan_api():
    """模拟API返回武汉的数据"""
    db = SessionLocal()
    
    # 查询武汉的景点
    spots = db.query(ScenicSpot).filter(ScenicSpot.city == "武汉").all()
    
    print(f"找到 {len(spots)} 个武汉的景点:")
    for spot in spots:
        print(f"  ID: {spot.id}, 名称: {spot.name}, 城市: {spot.city}")
    
    db.close()

if __name__ == "__main__":
    test_wuhan_api()
