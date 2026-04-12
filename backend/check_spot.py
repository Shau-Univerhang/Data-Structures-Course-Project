"""
检查数据库中是否有特定景点
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import SessionLocal, ScenicSpot

def check_spot(spot_name, city):
    db = SessionLocal()
    
    # 精确匹配
    spot = db.query(ScenicSpot).filter(
        ScenicSpot.name == spot_name,
        ScenicSpot.city == city
    ).first()
    
    if spot:
        print(f"找到精确匹配: {spot.name} (ID: {spot.id})")
    else:
        print(f"未找到精确匹配: {spot_name}")
        
        # 模糊匹配
        spots = db.query(ScenicSpot).filter(
            ScenicSpot.name.like(f"%{spot_name}%"),
            ScenicSpot.city == city
        ).all()
        
        if spots:
            print(f"找到 {len(spots)} 个模糊匹配:")
            for s in spots:
                print(f"  - {s.name}")
        else:
            print("未找到模糊匹配")
    
    db.close()

if __name__ == "__main__":
    check_spot("国家博物馆", "北京")
    print("\n" + "="*50 + "\n")
    check_spot("国家博物院", "北京")
