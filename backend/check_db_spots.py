"""
检查数据库中的景点名称
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import SessionLocal, ScenicSpot

def list_all_spots():
    db = SessionLocal()
    
    # 获取所有城市
    cities = db.query(ScenicSpot.city).distinct().all()
    cities = [c[0] for c in cities if c[0]]
    
    print("数据库中的所有景点:")
    print("=" * 60)
    
    for city in sorted(cities):
        spots = db.query(ScenicSpot).filter(ScenicSpot.city == city).all()
        print(f"\n{city} ({len(spots)}个):")
        for spot in spots:
            print(f"  - {spot.name}")
    
    db.close()

if __name__ == "__main__":
    list_all_spots()
