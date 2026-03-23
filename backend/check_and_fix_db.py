"""
检查并修复数据库中的景点数据
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import SessionLocal, ScenicSpot

def check_cities():
    """检查数据库中有哪些城市的数据"""
    db = SessionLocal()
    
    # 获取所有城市
    cities = db.query(ScenicSpot.city).distinct().all()
    cities = [c[0] for c in cities if c[0]]
    
    print("数据库中已有的城市:")
    for city in sorted(cities):
        count = db.query(ScenicSpot).filter(ScenicSpot.city == city).count()
        print(f"  {city}: {count}个景点")
    
    db.close()
    return cities

def add_missing_cities():
    """添加缺失的城市数据"""
    db = SessionLocal()
    
    # 需要添加的完整景点数据
    missing_cities = {
        "武汉": [
            ("黄鹤楼", "历史古迹", ["历史", "文化", "地标"]),
            ("东湖", "风景名胜", ["风景", "休闲", "公园"]),
            ("户部巷", "地标建筑", ["美食", "市井", "历史"]),
            ("武汉大学", "文化教育", ["学府", "风景", "樱花"]),
            ("湖北省博物馆", "博物展览", ["博物馆", "文化", "历史"]),
            ("江汉路步行街", "地标建筑", ["购物", "citywalk", "历史"]),
            ("古琴台", "历史古迹", ["文化", "历史", "音乐"]),
            ("晴川阁", "历史古迹", ["历史", "文化", "建筑"]),
            ("昙华林", "历史古迹", ["citywalk", "文创", "历史"]),
            ("汉口江滩", "风景名胜", ["风景", "休闲", "江景"]),
            ("武汉长江大桥", "地标建筑", ["地标", "建筑", "历史"]),
            ("归元寺", "历史古迹", ["寺庙", "文化", "历史"]),
            ("光谷步行街", "地标建筑", ["购物", "citywalk", "现代"]),
        ],
        "长沙": [
            ("岳麓山", "风景名胜", ["风景", "文化", "登山"]),
            ("橘子洲", "风景名胜", ["风景", "历史", "地标"]),
            ("湖南省博物馆", "博物展览", ["博物馆", "文化", "历史"]),
            ("太平街", "历史古迹", ["citywalk", "美食", "历史"]),
            ("天心阁", "历史古迹", ["历史", "文化", "建筑"]),
            ("世界之窗", "休闲娱乐", ["娱乐", "亲子", "主题公园"]),
            ("烈士公园", "休闲娱乐", ["公园", "休闲", "纪念"]),
            ("黄兴路步行街", "地标建筑", ["购物", "citywalk", "繁华"]),
            ("坡子街", "地标建筑", ["美食", "市井", "历史"]),
            ("爱晚亭", "风景名胜", ["风景", "文化", "历史"]),
            ("湖南大学", "文化教育", ["学府", "文化", "风景"]),
            ("中南大学", "文化教育", ["学府", "文化", "风景"]),
            ("超级文和友", "地标建筑", ["美食", "网红", "文化"]),
        ],
        "深圳": [
            ("世界之窗", "休闲娱乐", ["主题公园", "娱乐", "微缩景观"]),
            ("欢乐谷", "休闲娱乐", ["主题公园", "娱乐", "亲子"]),
            ("东部华侨城", "休闲娱乐", ["度假", "休闲", "风景"]),
            ("大梅沙", "风景名胜", ["海滩", "休闲", "度假"]),
            ("小梅沙", "风景名胜", ["海滩", "休闲", "度假"]),
            ("深圳湾公园", "休闲娱乐", ["公园", "休闲", "海景"]),
            ("莲花山公园", "休闲娱乐", ["公园", "休闲", "登山"]),
            ("梧桐山", "风景名胜", ["登山", "自然", "风景"]),
            ("中英街", "历史古迹", ["历史", "边境", "购物"]),
            ("大鹏所城", "历史古迹", ["历史", "文化", "古城"]),
            ("较场尾", "风景名胜", ["海滩", "休闲", "民宿"]),
            ("深圳大学", "文化教育", ["学府", "文化", "风景"]),
            ("华强北", "地标建筑", ["电子", "购物", "繁华"]),
        ],
    }
    
    # 城市坐标
    CITY_COORDS = {
        "武汉": (30.5928, 114.3055),
        "长沙": (28.2280, 112.9388),
        "深圳": (22.5431, 114.0579),
    }
    
    added_count = 0
    
    for city, spots in missing_cities.items():
        # 检查城市是否已存在
        existing = db.query(ScenicSpot).filter(ScenicSpot.city == city).first()
        if existing:
            print(f"{city} 已存在，跳过")
            continue
        
        print(f"添加 {city} 的 {len(spots)} 个景点...")
        base_lat, base_lng = CITY_COORDS.get(city, (30.0, 114.0))
        
        for i, (name, category, tags) in enumerate(spots):
            lat = base_lat + (i % 5 - 2) * 0.02
            lng = base_lng + (i % 5 - 2) * 0.02
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
        
        db.commit()
        print(f"  已添加 {city} 的 {len(spots)} 个景点")
    
    db.close()
    print(f"\n总共添加了 {added_count} 个景点")

if __name__ == "__main__":
    print("=== 检查数据库中的城市 ===")
    cities = check_cities()
    
    print("\n=== 添加缺失的城市数据 ===")
    add_missing_cities()
    
    print("\n=== 再次检查 ===")
    check_cities()
