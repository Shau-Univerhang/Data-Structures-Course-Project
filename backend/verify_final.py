"""
验证最终景点数据
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import SessionLocal, ScenicSpot

def verify_spots():
    db = SessionLocal()
    
    # 检查特定景点是否存在
    check_list = [
        ("北京", ["北京大学", "清华大学", "鸟巢", "什刹海", "水立方"]),
        ("长沙", ["黄兴路步行街", "中南大学", "岳麓山"]),
        ("成都", ["杜甫草堂", "武侯祠"]),
    ]
    
    print("=" * 60)
    print("验证缺失景点是否已添加")
    print("=" * 60)
    
    for city, spots in check_list:
        print(f"\n{city}:")
        for spot_name in spots:
            existing = db.query(ScenicSpot).filter(
                ScenicSpot.city == city,
                ScenicSpot.name == spot_name
            ).first()
            if existing:
                print(f"  [OK] {spot_name}")
            else:
                print(f"  [MISSING] {spot_name}")
    
    # 统计各城市景点数量
    print("\n" + "=" * 60)
    print("各城市景点数量统计")
    print("=" * 60)
    
    cities = db.query(ScenicSpot.city).distinct().all()
    for city in sorted([c[0] for c in cities if c[0]]):
        count = db.query(ScenicSpot).filter(ScenicSpot.city == city).count()
        print(f"  {city}: {count}个景点")
    
    db.close()

if __name__ == "__main__":
    verify_spots()
