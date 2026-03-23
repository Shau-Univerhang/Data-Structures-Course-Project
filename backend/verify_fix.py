"""
验证修复结果
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import SessionLocal, ScenicSpot

def verify():
    db = SessionLocal()
    
    # 要检查的景点
    check_spots = [
        ("北京", "北京大学"),
        ("北京", "清华大学"),
        ("北京", "鸟巢"),
        ("北京", "什刹海"),
        ("北京", "水立方"),
        ("长沙", "黄兴路步行街"),
        ("长沙", "中南大学"),
        ("长沙", "岳麓山"),
        ("成都", "杜甫草堂"),
        ("成都", "武侯祠"),
    ]
    
    print("验证景点是否存在:")
    print("=" * 50)
    
    all_ok = True
    for city, name in check_spots:
        spot = db.query(ScenicSpot).filter(
            ScenicSpot.city == city,
            ScenicSpot.name == name
        ).first()
        if spot:
            print(f"  [OK] {city} - {name}")
        else:
            print(f"  [MISSING] {city} - {name}")
            all_ok = False
    
    print("=" * 50)
    if all_ok:
        print("所有景点都已存在!")
    else:
        print("有景点缺失，需要补充")
    
    db.close()

if __name__ == "__main__":
    verify()
