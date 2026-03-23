"""
补充数据库中缺失的景点数据
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import SessionLocal, ScenicSpot

# 需要补充的景点数据
MISSING_SPOTS = {
    "北京": [
        ("北京大学", "文化教育", ["学府", "文化", "风景"]),
        ("清华大学", "文化教育", ["学府", "文化", "风景"]),
        ("鸟巢", "地标建筑", ["奥运", "地标", "现代建筑"]),
        ("什刹海", "风景名胜", ["胡同", "酒吧", "夜景"]),
        ("水立方", "地标建筑", ["奥运", "地标", "现代建筑"]),
    ],
    "长沙": [
        ("黄兴路步行街", "地标建筑", ["购物", "citywalk", "繁华"]),
        ("中南大学", "文化教育", ["学府", "文化", "风景"]),
        ("岳麓山", "风景名胜", ["风景", "文化", "登山"]),
    ],
    "成都": [
        ("杜甫草堂", "历史古迹", ["文化", "历史", "园林"]),
        ("武侯祠", "历史古迹", ["历史", "文化", "三国"]),
    ],
}

# 城市坐标
CITY_COORDS = {
    "北京": (39.9042, 116.4074),
    "长沙": (28.2280, 112.9388),
    "成都": (30.5728, 104.0668),
}

def add_missing_spots():
    db = SessionLocal()
    
    added_count = 0
    
    for city, spots in MISSING_SPOTS.items():
        base_lat, base_lng = CITY_COORDS.get(city, (30.0, 114.0))
        
        for i, (name, category, tags) in enumerate(spots):
            # 检查是否已存在
            existing = db.query(ScenicSpot).filter(
                ScenicSpot.city == city,
                ScenicSpot.name == name
            ).first()
            
            if existing:
                print(f"  {city} - {name}: 已存在，跳过")
                continue
            
            # 生成坐标（略微偏移）
            lat = base_lat + (i % 5 - 2) * 0.02
            lng = base_lng + (i % 5 - 2) * 0.02
            
            # 生成评分和热度
            rating = round(4.3 + (hash(name) % 7) / 10, 1)
            heat = 7000 + (hash(name) % 3000)
            
            spot = ScenicSpot(
                name=name,
                city=city,
                category=category,
                rating=rating,
                heat_score=heat,
                location_lat=lat,
                location_lng=lng,
                address=f"{city}市",
                description=f"{name}是{city}的著名景点",
                tags=tags,
                open_time="08:00-18:00",
                ticket_price="¥50"
            )
            db.add(spot)
            added_count += 1
            print(f"  {city} - {name}: 已添加")
        
        db.commit()
    
    db.close()
    print(f"\n总共添加了 {added_count} 个景点")

def check_existing_spots():
    """检查现有景点数据"""
    db = SessionLocal()
    
    print("=" * 60)
    print("检查现有景点数据")
    print("=" * 60)
    
    for city in ["北京", "长沙", "成都"]:
        spots = db.query(ScenicSpot).filter(ScenicSpot.city == city).all()
        print(f"\n{city} ({len(spots)}个景点):")
        for spot in spots:
            print(f"  - {spot.name}")
    
    db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("补充缺失的景点数据")
    print("=" * 60)
    
    add_missing_spots()
    
    print("\n" + "=" * 60)
    print("再次检查景点数据")
    print("=" * 60)
    check_existing_spots()
