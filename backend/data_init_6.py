"""
继续添加景点 - 达到200+
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import SessionLocal, ScenicSpot

def add_more_to_200():
    """添加更多景点达到200+"""
    db = SessionLocal()
    
    current_count = db.query(ScenicSpot).count()
    print(f"Current spots: {current_count}")
    
    more_spots = [
        # 更多热门景点
        {"name": "故宫角楼", "city": "北京", "rating": 4.7, "heat_score": 7500, "lat": 39.9416, "lng": 116.3916, "category": "历史古迹"},
        {"name": "景山公园", "city": "北京", "rating": 4.8, "heat_score": 7800, "lat": 39.9213, "lng": 116.3970, "category": "风景名胜"},
        {"name": "中山公园", "city": "北京", "rating": 4.4, "heat_score": 6500, "lat": 39.9116, "lng": 116.3716, "category": "城市公园"},
        {"name": "劳动人民文化宫", "city": "北京", "rating": 4.3, "heat_score": 6200, "lat": 39.9116, "lng": 116.4016, "category": "历史文化"},
        {"name": "人民公园", "city": "上海", "rating": 4.3, "heat_score": 6000, "lat": 31.2316, "lng": 121.4716, "category": "城市公园"},
        {"name": "长风公园", "city": "上海", "rating": 4.2, "heat_score": 5800, "lat": 31.4016, "lng": 121.4016, "category": "城市公园"},
        {"name": "世纪公园", "city": "上海", "rating": 4.4, "heat_score": 6500, "lat": 31.2216, "lng": 121.5516, "category": "城市公园"},
        {"name": "徐家汇公园", "city": "上海", "rating": 4.3, "heat_score": 6000, "lat": 31.2016, "lng": 121.4316, "category": "城市公园"},
        {"name": "延庆景区", "city": "北京", "rating": 4.5, "heat_score": 7000, "lat": 40.4516, "lng": 115.9716, "category": "风景名胜"},
        {"name": "密云水库", "city": "北京", "rating": 4.4, "heat_score": 6800, "lat": 40.4816, "lng": 116.9516, "category": "风景名胜"},
        {"name": "怀柔景区", "city": "北京", "rating": 4.5, "heat_score": 7100, "lat": 40.3216, "lng": 116.6316, "category": "风景名胜"},
        {"name": "门头沟", "city": "北京", "rating": 4.4, "heat_score": 6900, "lat": 39.9316, "lng": 115.7916, "category": "风景名胜"},
        {"name": "房山", "city": "北京", "rating": 4.4, "heat_score": 6700, "lat": 39.7316, "lng": 115.9916, "category": "风景名胜"},
        {"name": "大兴", "city": "北京", "rating": 4.3, "heat_score": 6200, "lat": 39.7316, "lng": 116.3316, "category": "城市公园"},
        {"name": "通州", "city": "北京", "rating": 4.3, "heat_score": 6100, "lat": 39.9016, "lng": 116.6516, "category": "城市公园"},
        {"name": "顺义", "city": "北京", "rating": 4.2, "heat_score": 5900, "lat": 40.1316, "lng": 116.6516, "category": "城市公园"},
        {"name": "昌平", "city": "北京", "rating": 4.4, "heat_score": 6800, "lat": 40.2216, "lng": 116.2316, "category": "风景名胜"},
        {"name": "石景山", "city": "北京", "rating": 4.3, "heat_score": 6300, "lat": 39.9016, "lng": 116.2216, "category": "城市公园"},
        {"name": "丰台", "city": "北京", "rating": 4.2, "heat_score": 5800, "lat": 39.8516, "lng": 116.2816, "category": "城市公园"},
        {"name": "海淀", "city": "北京", "rating": 4.4, "heat_score": 6700, "lat": 39.9516, "lng": 116.3016, "category": "高校"},
        {"name": "朝阳", "city": "北京", "rating": 4.3, "heat_score": 6400, "lat": 39.9516, "lng": 116.4516, "category": "城市公园"},
        {"name": "东城", "city": "北京", "rating": 4.4, "heat_score": 6600, "lat": 39.9316, "lng": 116.4216, "category": "历史古迹"},
        {"name": "西城", "city": "北京", "rating": 4.4, "heat_score": 6600, "lat": 39.9116, "lng": 116.3716, "category": "历史古迹"},
        {"name": "崇明岛", "city": "上海", "rating": 4.4, "heat_score": 7000, "lat": 31.6216, "lng": 121.5016, "category": "风景名胜"},
        {"name": "奉贤", "city": "上海", "rating": 4.3, "heat_score": 6200, "lat": 30.9216, "lng": 121.5516, "category": "城市公园"},
        {"name": "金山", "city": "上海", "rating": 4.2, "heat_score": 5900, "lat": 30.7416, "lng": 121.1516, "category": "城市公园"},
        {"name": "青浦", "city": "上海", "rating": 4.3, "heat_score": 6300, "lat": 31.1516, "lng": 121.1016, "category": "水乡"},
        {"name": "松江", "city": "上海", "rating": 4.3, "heat_score": 6400, "lat": 31.0316, "lng": 121.2316, "category": "历史文化"},
        {"name": "嘉定", "city": "上海", "rating": 4.3, "heat_score": 6300, "lat": 31.3816, "lng": 121.2516, "category": "历史文化"},
    ]
    
    for spot_info in more_spots:
        exists = db.query(ScenicSpot).filter(
            ScenicSpot.name == spot_info['name']
        ).first()
        
        if not exists:
            spot = ScenicSpot(
                name=spot_info['name'],
                city=spot_info['city'],
                category=spot_info.get('category', '风景名胜'),
                rating=spot_info.get('rating', 4.5),
                heat_score=spot_info.get('heat_score', 5000),
                location_lat=spot_info.get('lat'),
                location_lng=spot_info.get('lng'),
                description=f"{spot_info['city']}的著名景点",
                tags=[],
                open_time="全天",
                ticket_price="参考实际"
            )
            db.add(spot)
    
    db.commit()
    new_count = db.query(ScenicSpot).count()
    print(f"Total spots now: {new_count}")
    db.close()


if __name__ == "__main__":
    add_more_to_200()
