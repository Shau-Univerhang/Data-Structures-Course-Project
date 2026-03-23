"""
检查武汉的景点
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import SessionLocal, ScenicSpot

def check_wuhan():
    db = SessionLocal()
    
    spots = db.query(ScenicSpot).filter(ScenicSpot.city == "武汉").all()
    print(f"武汉共有 {len(spots)} 个景点:")
    for spot in spots:
        print(f"  - {spot.name}")
    
    db.close()

if __name__ == "__main__":
    check_wuhan()
