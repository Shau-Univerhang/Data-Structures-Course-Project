"""
扩展景点数据 - 添加更多城市景点以达到200+要求
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import SessionLocal, ScenicSpot, Restaurant

def add_more_spots():
    """添加更多景点数据"""
    db = SessionLocal()
    
    # 检查当前数量
    current_count = db.query(ScenicSpot).count()
    print(f"Current spots: {current_count}")
    
    more_spots = [
        # 苏州
        {"name": "拙政园", "city": "苏州", "category": "风景名胜", "rating": 4.9, "heat_score": 8900,
         "location_lat": 31.3236, "location_lng": 120.5853, "address": "江苏省苏州市姑苏区东北街178号",
         "description": "中国古典园林的代表作",
         "tags": ["江南园林", "世界遗产", "古建绝美"], "open_time": "07:30-17:30", "ticket_price": "70元"},
        {"name": "周庄", "city": "苏州", "category": "风景名胜", "rating": 4.7, "heat_score": 8200,
         "location_lat": 31.1166, "location_lng": 120.8466, "address": "江苏省苏州市昆山市周庄镇",
         "description": "中国第一水乡",
         "tags": ["水乡古镇", "休闲度假", "拍照出片"], "open_time": "08:00-17:00", "ticket_price": "100元"},
        {"name": "狮子林", "city": "苏州", "category": "风景名胜", "rating": 4.8, "heat_score": 7800,
         "location_lat": 31.3276, "location_lng": 120.5833, "address": "江苏省苏州市姑苏区园林路23号",
         "description": "元代园林的代表",
         "tags": ["江南园林", "假山奇石", "世界遗产"], "open_time": "07:30-17:30", "ticket_price": "40元"},
        
        # 重庆
        {"name": "洪崖洞", "city": "重庆", "category": "地标建筑", "rating": 4.7, "heat_score": 9100,
         "location_lat": 29.5630, "location_lng": 106.5752, "address": "重庆市渝中区嘉陵江滨江路",
         "description": "巴渝传统建筑特色",
         "tags": ["夜景绝美", "地标建筑", "逛吃逛喝"], "open_time": "全天", "ticket_price": "免费"},
        {"name": "解放碑", "city": "重庆", "category": "地标建筑", "rating": 4.6, "heat_score": 8700,
         "location_lat": 29.5527, "location_lng": 106.5694, "address": "重庆市渝中区",
         "description": "重庆的地标性建筑",
         "tags": ["地标建筑", "购物天堂", "citywalk"], "open_time": "全天", "ticket_price": "免费"},
        {"name": "长江索道", "city": "重庆", "category": "休闲娱乐", "rating": 4.6, "heat_score": 8300,
         "location_lat": 29.5786, "location_lng": 106.5716, "address": "重庆市渝中区",
         "description": "万里长江第一条空中走廊",
         "tags": ["特色体验", "登高望远", "citywalk"], "open_time": "07:30-22:00", "ticket_price": "20元"},
        
        # 广州
        {"name": "广州塔", "city": "广州", "category": "地标建筑", "rating": 4.7, "heat_score": 9000,
         "location_lat": 23.1067, "location_lng": 113.3323, "address": "广东省广州市海珠区阅江西路222号",
         "description": "广州的新地标",
         "tags": ["地标建筑", "登高望远", "夜景绝美"], "open_time": "09:30-22:00", "ticket_price": "150元"},
        {"name": "北京路步行街", "city": "广州", "category": "地标建筑", "rating": 4.5, "heat_score": 7800,
         "location_lat": 23.1257, "location_lng": 113.2606, "address": "广东省广州市越秀区",
         "description": "广州最繁华的商业街",
         "tags": ["购物天堂", "逛吃逛喝", "citywalk"], "open_time": "全天", "ticket_price": "免费"},
        
        # 深圳
        {"name": "世界之窗", "city": "深圳", "category": "休闲娱乐", "rating": 4.6, "heat_score": 8500,
         "location_lat": 22.5408, "location_lng": 113.9355, "address": "广东省深圳市南山区深南大道9037号",
         "description": "将世界奇观尽收眼底",
         "tags": ["主题公园", "必玩景点", "亲子乐园"], "open_time": "09:00-22:00", "ticket_price": "200元"},
        {"name": "欢乐谷", "city": "深圳", "category": "休闲娱乐", "rating": 4.6, "heat_score": 8300,
         "location_lat": 22.5366, "location_lng": 113.9756, "address": "广东省深圳市南山区侨城西街18号",
         "description": "中国最佳主题乐园",
         "tags": ["主题公园", "亲子乐园", "休闲娱乐"], "open_time": "09:30-22:00", "ticket_price": "200元"},
        
        # 南京
        {"name": "中山陵", "city": "南京", "category": "历史古迹", "rating": 4.8, "heat_score": 9000,
         "location_lat": 32.0603, "location_lng": 118.7969, "address": "江苏省南京市玄武区中山陵园风景区",
         "description": "中国近代伟大的政治家孙中山先生的陵墓",
         "tags": ["历史文化", "地标建筑", "登高望远"], "open_time": "08:30-17:00", "ticket_price": "免费"},
        {"name": "夫子庙", "city": "南京", "category": "地标建筑", "rating": 4.6, "heat_score": 8600,
         "location_lat": 32.0170, "location_lng": 118.7876, "address": "江苏省南京市秦淮区",
         "description": "南京最繁华的旅游商业区",
         "tags": ["市井烟火", "逛吃逛喝", "历史文化"], "open_time": "全天", "ticket_price": "免费"},
        
        # 武汉
        {"name": "黄鹤楼", "city": "武汉", "category": "历史古迹", "rating": 4.7, "heat_score": 8800,
         "location_lat": 30.5558, "location_lng": 114.3096, "address": "湖北省武汉市武昌区蛇山",
         "description": "江南三大名楼之一",
         "tags": ["历史文化", "地标建筑", "登高望远"], "open_time": "08:00-18:00", "ticket_price": "70元"},
        {"name": "武汉大学", "city": "武汉", "category": "校园风光", "rating": 4.7, "heat_score": 8400,
         "location_lat": 30.5419, "location_lng": 114.3656, "address": "湖北省武汉市武昌区八一路299号",
         "description": "中国最美的大学校园之一",
         "tags": ["校园风光", "樱花季", "citywalk"], "open_time": "全天", "ticket_price": "免费"},
        
        # 长沙
        {"name": "岳麓书院", "city": "长沙", "category": "历史文化", "rating": 4.8, "heat_score": 8600,
         "location_lat": 28.6019, "location_lng": 112.9368, "address": "湖南省长沙市岳麓区麓山南路",
         "description": "中国古代四大书院之一",
         "tags": ["历史文化", "书院文化", "古建绝美"], "open_time": "07:30-18:00", "ticket_price": "50元"},
        {"name": "橘子洲", "city": "长沙", "category": "风景名胜", "rating": 4.6, "heat_score": 8200,
         "location_lat": 28.5903, "location_lng": 112.9391, "address": "湖南省长沙市岳麓区",
         "description": "湘江中的大型岛屿",
         "tags": ["自然风光", "城市公园", "citywalk"], "open_time": "全天", "ticket_price": "免费"},
        
        # 厦门
        {"name": "鼓浪屿", "city": "厦门", "category": "风景名胜", "rating": 4.8, "heat_score": 9300,
         "location_lat": 24.4408, "location_lng": 118.1068, "address": "福建省厦门市思明区",
         "description": "'海上花园'，世界文化遗产",
         "tags": ["世界遗产", "浪漫爱情", "拍照出片"], "open_time": "全天", "ticket_price": "免费"},
        {"name": "厦门大学", "city": "厦门", "category": "校园风光", "rating": 4.7, "heat_score": 8500,
         "location_lat": 24.4355, "location_lng": 118.1038, "address": "福建省厦门市思明区思明南路422号",
         "description": "中国最美大学之一",
         "tags": ["校园风光", "拍照出片", "citywalk"], "open_time": "全天", "ticket_price": "免费"},
        
        # 哈尔滨
        {"name": "冰雪大世界", "city": "哈尔滨", "category": "休闲娱乐", "rating": 4.8, "heat_score": 8900,
         "location_lat": 45.8918, "location_lng": 126.5450, "address": "黑龙江省哈尔滨市松北区",
         "description": "世界上最大的冰雪主题乐园",
         "tags": ["冰雪奇观", "必玩景点", "亲子乐园"], "open_time": "11:00-22:00", "ticket_price": "200元"},
        {"name": "中央大街", "city": "哈尔滨", "category": "地标建筑", "rating": 4.6, "heat_score": 8400,
         "location_lat": 45.7748, "location_lng": 126.6185, "address": "黑龙江省哈尔滨市道里区",
         "description": "亚洲最长的商业步行街",
         "tags": ["建筑艺术", "逛吃逛喝", "citywalk"], "open_time": "全天", "ticket_price": "免费"},
        
        # 拉萨
        {"name": "布达拉宫", "city": "拉萨", "category": "历史古迹", "rating": 4.9, "heat_score": 9600,
         "location_lat": 29.6578, "location_lng": 91.1172, "address": "西藏自治区拉萨市城关区北京中路",
         "description": "世界上海拔最高的宫殿",
         "tags": ["必玩景点", "世界遗产", "宗教信仰"], "open_time": "09:00-16:00", "ticket_price": "200元"},
        {"name": "大昭寺", "city": "拉萨", "category": "历史文化", "rating": 4.9, "heat_score": 9200,
         "location_lat": 29.6525, "location_lng": 91.1175, "address": "西藏自治区拉萨市城关区八廓街",
         "description": "藏传佛教圣地",
         "tags": ["宗教信仰", "历史文化", "非遗体验"], "open_time": "09:00-18:00", "ticket_price": "85元"},
        
        # 桂林
        {"name": "漓江", "city": "桂林", "category": "风景名胜", "rating": 4.9, "heat_score": 9100,
         "location_lat": 25.2966, "location_lng": 110.2965, "address": "广西桂林市灵川县",
         "description": "'桂林山水甲天下'的核心",
         "tags": ["自然风光", "必玩景点", "山水画卷"], "open_time": "全天", "ticket_price": "免费"},
        {"name": "阳朔西街", "city": "桂林", "category": "地标建筑", "rating": 4.6, "heat_score": 8000,
         "location_lat": 24.4736, "location_lng": 110.4965, "address": "广西桂林市阳朔县",
         "description": "阳朔最繁华的商业步行街",
         "tags": ["市井烟火", "逛吃逛喝", "休闲度假"], "open_time": "全天", "ticket_price": "免费"},
        
        # 三亚
        {"name": "蜈支洲岛", "city": "三亚", "category": "风景名胜", "rating": 4.8, "heat_score": 9000,
         "location_lat": 18.6468, "location_lng": 109.7606, "address": "海南省三亚市海棠湾镇",
         "description": "中国马尔代夫",
         "tags": ["海滨度假", "必玩景点", "海岛风光"], "open_time": "08:00-18:30", "ticket_price": "144元"},
        {"name": "天涯海角", "city": "三亚", "category": "风景名胜", "rating": 4.6, "heat_score": 8400,
         "location_lat": 18.5970, "location_lng": 109.3576, "address": "海南省三亚市天涯区",
         "description": "海南的代名词",
         "tags": ["海景风光", "地标建筑", "浪漫爱情"], "open_time": "07:30-18:20", "ticket_price": "81元"},
        
        # 东京
        {"name": "东京塔", "city": "东京", "category": "地标建筑", "rating": 4.6, "heat_score": 8800,
         "location_lat": 35.6586, "location_lng": 139.7454, "address": "东京都港区芝公园4-2-8",
         "description": "东京的象征",
         "tags": ["地标建筑", "夜景绝美", "登高望远"], "open_time": "09:00-23:00", "ticket_price": "120元"},
        
        # 香港
        {"name": "维多利亚港", "city": "香港", "category": "风景名胜", "rating": 4.8, "heat_score": 9200,
         "location_lat": 22.2855, "location_lng": 114.1577, "address": "香港岛与九龙半岛之间",
         "description": "世界三大天然良港之一",
         "tags": ["夜景绝美", "地标建筑", "海港风光"], "open_time": "全天", "ticket_price": "免费"},
        
        # 巴黎
        {"name": "埃菲尔铁塔", "city": "巴黎", "category": "地标建筑", "rating": 4.8, "heat_score": 9800,
         "location_lat": 48.8584, "location_lng": 2.2945, "address": "法国巴黎战神广场",
         "description": "巴黎的标志性建筑",
         "tags": ["地标建筑", "必玩景点", "登高望远"], "open_time": "09:00-23:59", "ticket_price": "26欧元"},
        
        # 纽约
        {"name": "自由女神像", "city": "纽约", "category": "地标建筑", "rating": 4.8, "heat_score": 9500,
         "location_lat": 40.6892, "location_lng": -74.0445, "address": "美国纽约自由岛",
         "description": "美国的象征",
         "tags": ["地标建筑", "世界遗产", "必玩景点"], "open_time": "08:30-16:00", "ticket_price": "24美元"},
    ]
    
    for spot_data in more_spots:
        # 检查是否已存在
        exists = db.query(ScenicSpot).filter(ScenicSpot.name == spot_data['name']).first()
        if not exists:
            spot = ScenicSpot(**spot_data)
            db.add(spot)
    
    db.commit()
    
    new_count = db.query(ScenicSpot).count()
    print(f"Total spots now: {new_count}")
    
    db.close()


if __name__ == "__main__":
    add_more_spots()
