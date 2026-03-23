"""
检查景点标签
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import SessionLocal, ScenicSpot

def check_tags():
    db = SessionLocal()
    
    # 检查北京的景点
    spots = db.query(ScenicSpot).filter(ScenicSpot.city == '北京').all()
    print("北京的景点标签:")
    for spot in spots:
        print(f"  {spot.name}: {spot.tags}")
    
    db.close()

if __name__ == "__main__":
    check_tags()
