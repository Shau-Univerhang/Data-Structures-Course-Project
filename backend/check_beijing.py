"""
检查北京的景点数据
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import SessionLocal, ScenicSpot

def check_beijing():
    db = SessionLocal()
    
    spots = db.query(ScenicSpot).filter(ScenicSpot.city == "北京").all()
    print(f"北京共有 {len(spots)} 个景点:\n")
    for spot in spots:
        print(f"  - {spot.name}")
    
    db.close()

if __name__ == "__main__":
    check_beijing()
