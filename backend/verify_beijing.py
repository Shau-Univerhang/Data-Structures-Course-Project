"""
验证北京景点数据
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import SessionLocal, ScenicSpot

def verify():
    db = SessionLocal()
    
    spots = db.query(ScenicSpot).filter(ScenicSpot.city == '北京').all()
    print(f"Beijing now has {len(spots)} spots:")
    for spot in spots:
        print(f"  - {spot.name}")
    
    db.close()

if __name__ == "__main__":
    verify()
