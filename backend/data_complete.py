"""
添加完善景点数据 - 每个城市多个景点
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import SessionLocal, ScenicSpot

def add_complete_spots():
    """添加完整的景点数据"""
    db = SessionLocal()
    
    # 清空旧数据
    db.query(ScenicSpot).delete()
    db.commit()
    
    # 城市景点数据
    cities_data = [
        # 北京
        {"name": "故宫博物院", "city": "北京", "rating": 4.9, "heat_score": 9850, "location_lat": 39.9163, "location_lng": 116.3972, "category": "历史古迹", "tags": ["必玩景点", "世界遗产", "建筑宏伟"], "description": "世界上现存规模最大保存最为完整的木质结构古建筑之一", "open_time": "08:30-17:00", "ticket_price": "60元", "images": ["https://images.unsplash.com/photo-1599571234909-29ed5d1321d6?w=800"]},
        {"name": "天坛公园", "city": "北京", "rating": 4.9, "heat_score": 9200, "location_lat": 39.9022, "location_lng": 116.4106, "category": "历史古迹", "tags": ["古建绝美", "历史文化"], "description": "明清两代帝王祭祀皇天祈五谷丰登的场所", "open_time": "06:00-21:00", "ticket_price": "15元", "images": ["https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800"]},
        {"name": "颐和园", "city": "北京", "rating": 4.9, "heat_score": 9100, "location_lat": 39.9998, "location_lng": 116.6172, "category": "风景名胜", "tags": ["皇家园林", "湖光山色"], "description": "清代皇家园林以昆明湖万寿山为基址", "open_time": "06:30-18:00", "ticket_price": "30元", "images": ["https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800"]},
        {"name": "八达岭长城", "city": "北京", "rating": 4.8, "heat_score": 9800, "location_lat": 40.4319, "location_lng": 116.5704, "category": "历史古迹", "tags": ["必玩景点", "登高望远"], "description": "中国古代伟大的防御工程万里长城的重要组成部分", "open_time": "06:30-19:00", "ticket_price": "40元", "images": ["https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800"]},
        {"name": "天安门广场", "city": "北京", "rating": 4.8, "heat_score": 9500, "location_lat": 39.9054, "location_lng": 116.3976, "category": "地标建筑", "tags": ["升旗仪式", "地标建筑"], "description": "世界上最大的城市广场之一", "open_time": "全天", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800"]},
        
        # 上海
        {"name": "外滩", "city": "上海", "rating": 4.9, "heat_score": 9700, "location_lat": 31.2456, "location_lng": 121.4901, "category": "地标建筑", "tags": ["夜景绝美", "citywalk"], "description": "上海最具代表性的景观汇合了万国建筑群", "open_time": "全天", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1474181487882-5abf3f0ba6c2?w=800"]},
        {"name": "东方明珠", "city": "上海", "rating": 4.7, "heat_score": 9300, "location_lat": 31.2401, "location_lng": 121.5019, "category": "地标建筑", "tags": ["登高望远", "夜景绝美"], "description": "上海标志性建筑之一", "open_time": "08:00-21:30", "ticket_price": "199元", "images": ["https://images.unsplash.com/photo-1474181487882-5abf3f0ba6c2?w=800"]},
        {"name": "豫园", "city": "上海", "rating": 4.8, "heat_score": 8600, "location_lat": 31.2256, "location_lng": 121.4806, "category": "风景名胜", "tags": ["江南园林", "古建绝美"], "description": "始建于明代的古典园林", "open_time": "08:30-17:00", "ticket_price": "40元", "images": ["https://images.unsplash.com/photo-1474181487882-5abf3f0ba6c2?w=800"]},
        {"name": "上海迪士尼乐园", "city": "上海", "rating": 4.8, "heat_score": 9500, "location_lat": 31.1430, "location_lng": 121.6600, "category": "休闲娱乐", "tags": ["亲子乐园", "必玩景点"], "description": "中国大陆第一个迪士尼主题乐园", "open_time": "08:30-20:30", "ticket_price": "475元", "images": ["https://images.unsplash.com/photo-1474181487882-5abf3f0ba6c2?w=800"]},
        
        # 西安
        {"name": "秦始皇兵马俑", "city": "西安", "rating": 4.9, "heat_score": 9900, "location_lat": 34.3843, "location_lng": 109.2785, "category": "历史古迹", "tags": ["必玩景点", "世界遗产"], "description": "世界第八大奇迹古代陶俑艺术的巅峰之作", "open_time": "08:30-18:00", "ticket_price": "120元", "images": ["https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800"]},
        {"name": "大雁塔", "city": "西安", "rating": 4.8, "heat_score": 9000, "location_lat": 34.2194, "location_lng": 108.9597, "category": "历史古迹", "tags": ["古建绝美", "地标建筑"], "description": "唐代著名的佛教建筑", "open_time": "08:00-18:30", "ticket_price": "50元", "images": ["https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800"]},
        {"name": "西安城墙", "city": "西安", "rating": 4.8, "heat_score": 8800, "location_lat": 34.2580, "location_lng": 108.9456, "category": "历史古迹", "tags": ["登高望远", "citywalk"], "description": "中国现存规模最大保存最完整的古代城垣", "open_time": "08:00-22:00", "ticket_price": "54元", "images": ["https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800"]},
        
        # 成都
        {"name": "大熊猫繁育研究基地", "city": "成都", "rating": 4.9, "heat_score": 9400, "location_lat": 30.7416, "location_lng": 104.1277, "category": "休闲娱乐", "tags": ["必玩景点", "亲子乐园"], "description": "全球最大的大熊猫繁育研究机构", "open_time": "07:30-18:00", "ticket_price": "55元", "images": ["https://images.unsplash.com/photo-1528109966604-5a6a4a964e8d?w=800"]},
        {"name": "宽窄巷子", "city": "成都", "rating": 4.7, "heat_score": 8700, "location_lat": 30.6686, "location_lng": 104.0556, "category": "地标建筑", "tags": ["市井烟火", "citywalk"], "description": "成都三大历史文化保护区之一", "open_time": "全天", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1528109966604-5a6a4a964e8d?w=800"]},
        {"name": "都江堰", "city": "成都", "rating": 4.9, "heat_score": 9100, "location_lat": 30.9919, "location_lng": 103.5773, "category": "历史古迹", "tags": ["世界遗产", "必玩景点"], "description": "世界文化遗产古代水利工程的奇迹", "open_time": "08:00-18:00", "ticket_price": "80元", "images": ["https://images.unsplash.com/photo-1528109966604-5a6a4a964e8d?w=800"]},
        
        # 杭州
        {"name": "西湖", "city": "杭州", "rating": 4.9, "heat_score": 9900, "location_lat": 30.2467, "location_lng": 120.1481, "category": "风景名胜", "tags": ["必玩景点", "湖光山色"], "description": "中国著名的风景名胜区欲把西湖比西子", "open_time": "全天", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800"]},
        {"name": "灵隐寺", "city": "杭州", "rating": 4.8, "heat_score": 9000, "location_lat": 30.2365, "location_lng": 120.0965, "category": "历史文化", "tags": ["佛教文化", "古建绝美"], "description": "江南著名古刹", "open_time": "07:00-18:00", "ticket_price": "75元", "images": ["https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800"]},
        
        # 青岛
        {"name": "栈桥", "city": "青岛", "rating": 4.7, "heat_score": 8800, "location_lat": 36.0671, "location_lng": 120.3826, "category": "地标建筑", "tags": ["海景风光", "citywalk"], "description": "青岛的标志性建筑", "open_time": "全天", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800"]},
        {"name": "五四广场", "city": "青岛", "rating": 4.7, "heat_score": 8600, "location_lat": 36.0626, "location_lng": 120.3766, "category": "地标建筑", "tags": ["夜景绝美", "citywalk"], "description": "青岛最具标志性的城市广场", "open_time": "全天", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800"]},
        
        # 重庆
        {"name": "洪崖洞", "city": "重庆", "rating": 4.7, "heat_score": 9100, "location_lat": 29.5630, "location_lng": 106.5752, "category": "地标建筑", "tags": ["夜景绝美", "地标建筑"], "description": "巴渝传统建筑特色", "open_time": "全天", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1560969184-10fe8719e047?w=800"]},
        {"name": "解放碑", "city": "重庆", "rating": 4.6, "heat_score": 8700, "location_lat": 29.5527, "location_lng": 106.5694, "category": "地标建筑", "tags": ["购物天堂", "citywalk"], "description": "重庆的地标性建筑", "open_time": "全天", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1560969184-10fe8719e047?w=800"]},
        
        # 广州
        {"name": "广州塔", "city": "广州", "rating": 4.7, "heat_score": 9000, "location_lat": 23.1067, "location_lng": 113.3323, "category": "地标建筑", "tags": ["登高望远", "夜景绝美"], "description": "广州的新地标", "open_time": "09:30-22:00", "ticket_price": "150元", "images": ["https://images.unsplash.com/photo-1534054524995-69c5d4f8a5b5?w=800"]},
        {"name": "北京路步行街", "city": "广州", "rating": 4.5, "heat_score": 7800, "location_lat": 23.1257, "location_lng": 113.2606, "category": "地标建筑", "tags": ["购物天堂", "citywalk"], "description": "广州最繁华的商业街", "open_time": "全天", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1534054524995-69c5d4f8a5b5?w=800"]},
        
        # 深圳
        {"name": "世界之窗", "city": "深圳", "rating": 4.6, "heat_score": 8500, "location_lat": 22.5408, "location_lng": 113.9355, "category": "休闲娱乐", "tags": ["主题公园", "必玩景点"], "description": "将世界奇观尽收眼底", "open_time": "09:00-22:00", "ticket_price": "200元", "images": ["https://images.unsplash.com/photo-1530976161117-d1a36af4c1c8?w=800"]},
        {"name": "欢乐谷", "city": "深圳", "rating": 4.6, "heat_score": 8300, "location_lat": 22.5366, "location_lng": 113.9756, "category": "休闲娱乐", "tags": ["主题公园", "亲子乐园"], "description": "中国最佳主题乐园", "open_time": "09:30-22:00", "ticket_price": "200元", "images": ["https://images.unsplash.com/photo-1530976161117-d1a36af4c1c8?w=800"]},
        
        # 南京
        {"name": "中山陵", "city": "南京", "rating": 4.8, "heat_score": 9000, "location_lat": 32.0603, "location_lng": 118.7969, "category": "历史古迹", "tags": ["历史文化", "地标建筑"], "description": "中国近代伟大的政治家孙中山先生的陵墓", "open_time": "08:30-17:00", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1530521954074-e64f6810b32d?w=800"]},
        {"name": "夫子庙", "city": "南京", "rating": 4.6, "heat_score": 8600, "location_lat": 32.0170, "location_lng": 118.7876, "category": "地标建筑", "tags": ["市井烟火", "逛吃逛喝"], "description": "南京最繁华的旅游商业区", "open_time": "全天", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1530521954074-e64f6810b32d?w=800"]},
        
        # 苏州
        {"name": "拙政园", "city": "苏州", "rating": 4.9, "heat_score": 8900, "location_lat": 31.3236, "location_lng": 120.5853, "category": "风景名胜", "tags": ["江南园林", "世界遗产"], "description": "中国古典园林的代表作", "open_time": "07:30-17:30", "ticket_price": "70元", "images": ["https://images.unsplash.com/photo-1548919973-5cef591cdbc9?w=800"]},
        {"name": "周庄", "city": "苏州", "rating": 4.7, "heat_score": 8200, "location_lat": 31.1166, "location_lng": 120.8466, "category": "风景名胜", "tags": ["水乡古镇", "休闲度假"], "description": "中国第一水乡", "open_time": "08:00-17:00", "ticket_price": "100元", "images": ["https://images.unsplash.com/photo-1548919973-5cef591cdbc9?w=800"]},
        
        # 厦门
        {"name": "鼓浪屿", "city": "厦门", "rating": 4.8, "heat_score": 9300, "location_lat": 24.4408, "location_lng": 118.1068, "category": "风景名胜", "tags": ["世界遗产", "浪漫爱情"], "description": "海上花园世界文化遗产", "open_time": "全天", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1518459021-c8f5211a7edc?w=800"]},
        {"name": "厦门大学", "city": "厦门", "rating": 4.7, "heat_score": 8500, "location_lat": 24.4355, "location_lng": 118.1038, "category": "校园风光", "tags": ["校园风光", "拍照出片"], "description": "中国最美大学之一", "open_time": "全天", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1518459021-c8f5211a7edc?w=800"]},
    ]
    
    # 添加所有景点
    for spot_data in cities_data:
        spot = ScenicSpot(**spot_data)
        db.add(spot)
    
    db.commit()
    count = db.query(ScenicSpot).count()
    print(f"Total spots: {count}")
    db.close()


if __name__ == "__main__":
    add_complete_spots()
