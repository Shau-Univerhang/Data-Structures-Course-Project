"""
数据初始化脚本 - 更多城市景点
"""
import sys
sys.path.append("..")

from models.database import SessionLocal, ScenicSpot, Restaurant

def init_more_spots():
    """初始化更多城市景点数据"""
    db = SessionLocal()
    
    # 检查是否已有数据
    count = db.query(ScenicSpot).filter(ScenicSpot.city == "成都").count()
    if count > 0:
        print("数据已存在，跳过")
        db.close()
        return
    
    all_spots = [
        # 成都
        {"name": "大熊猫繁育研究基地", "city": "成都", "category": "休闲娱乐", "rating": 4.9, "heat_score": 9400,
         "location_lat": 30.7416, "location_lng": 104.1277, "address": "四川省成都市成华区熊猫大道1375号",
         "description": "全球最大的大熊猫繁育研究机构",
         "tags": ["必玩景点", "亲子乐园", "动物观赏"], "open_time": "07:30-18:00", "ticket_price": "¥55"},
        {"name": "宽窄巷子", "city": "成都", "category": "地标建筑", "rating": 4.7, "heat_score": 8700,
         "location_lat": 30.6686, "location_lng": 104.0556, "address": "四川省成都市青羊区长顺上街127号",
         "description": "成都三大历史文化保护区之一",
         "tags": ["市井烟火", "citywalk", "逛吃逛喝"], "open_time": "全天", "ticket_price": "免费"},
        {"name": "锦里古街", "city": "成都", "category": "地标建筑", "rating": 4.6, "heat_score": 8300,
         "location_lat": 30.6606, "location_lng": 104.0506, "address": "四川省成都市武侯区武侯祠大街231号",
         "description": "成都知名的步行商业街",
         "tags": ["市井烟火", "逛吃逛喝", "三国文化"], "open_time": "全天", "ticket_price": "免费"},
        {"name": "都江堰", "city": "成都", "category": "历史古迹", "rating": 4.9, "heat_score": 9100,
         "location_lat": 30.9919, "location_lng": 103.5773, "address": "四川省成都市都江堰市公园路",
         "description": "世界文化遗产，古代水利工程的奇迹",
         "tags": ["必玩景点", "世界遗产", "历史文化"], "open_time": "08:00-18:00", "ticket_price": "¥80"},
        {"name": "青城山", "city": "成都", "category": "风景名胜", "rating": 4.8, "heat_score": 8800,
         "location_lat": 30.8912, "location_lng": 103.5313, "address": "四川省成都市都江堰市青城山镇",
         "description": "中国道教发源地之一",
         "tags": ["道教文化", "自然风光", "休闲养生"], "open_time": "08:00-18:00", "ticket_price": "¥80"},
        
        # 杭州
        {"name": "西湖", "city": "杭州", "category": "风景名胜", "rating": 4.9, "heat_score": 9900,
         "location_lat": 30.2467, "location_lng": 120.1481, "address": "浙江省杭州市西湖区龙井路1号",
         "description": "中国著名的风景名胜区，'欲把西湖比西子'",
         "tags": ["必玩景点", "湖光山色", "浪漫爱情"], "open_time": "全天", "ticket_price": "免费"},
        {"name": "灵隐寺", "city": "杭州", "category": "历史文化", "rating": 4.8, "heat_score": 9000,
         "location_lat": 30.2365, "location_lng": 120.0965, "address": "浙江省杭州市西湖区灵隐路法云弄1号",
         "description": "江南著名古刹",
         "tags": ["佛教文化", "历史文化", "古建绝美"], "open_time": "07:00-18:00", "ticket_price": "¥75"},
        {"name": "宋城", "city": "杭州", "category": "休闲娱乐", "rating": 4.6, "heat_score": 8200,
         "location_lat": 30.1836, "location_lng": 120.1656, "address": "浙江省杭州市西湖区之江路148号",
         "description": "以宋代历史文化为主题的大型主题公园",
         "tags": ["主题公园", "演艺表演", "穿越体验"], "open_time": "09:00-21:00", "ticket_price": "¥300"},
        {"name": "西溪湿地", "city": "杭州", "category": "风景名胜", "rating": 4.8, "heat_score": 8500,
         "location_lat": 30.0816, "location_lng": 120.0716, "address": "浙江省杭州市西湖区天目山路518号",
         "description": "国内第一个集城市湿地、农耕湿地、文化湿地于一体的国家湿地公园",
         "tags": ["自然风光", "生态休闲", "拍照出片"], "open_time": "07:30-18:30", "ticket_price": "¥80"},
        
        # 青岛
        {"name": "栈桥", "city": "青岛", "category": "地标建筑", "rating": 4.7, "heat_score": 8800,
         "location_lat": 36.0671, "location_lng": 120.3826, "address": "山东省青岛市市南区太平路12号",
         "description": "青岛的标志性建筑",
         "tags": ["地标建筑", "海景风光", "citywalk"], "open_time": "全天", "ticket_price": "免费"},
        {"name": "五四广场", "city": "青岛", "category": "地标建筑", "rating": 4.7, "heat_score": 8600,
         "location_lat": 36.0626, "location_lng": 120.3766, "address": "山东省青岛市市南区",
         "description": "青岛最具标志性的城市广场",
         "tags": ["地标建筑", "夜景绝美", "citywalk"], "open_time": "全天", "ticket_price": "免费"},
        {"name": "崂山", "city": "青岛", "category": "风景名胜", "rating": 4.8, "heat_score": 8400,
         "location_lat": 36.1075, "location_lng": 120.6512, "address": "山东省青岛市崂山区",
         "description": "中国海岸线上的最高峰",
         "tags": ["风景名胜", "道教文化", "登高望远"], "open_time": "06:00-18:00", "ticket_price": "¥90"},
        
        # 苏州
        {"name": "拙政园", "city": "苏州", "category": "风景名胜", "rating": 4.9, "heat_score": 8900,
         "location_lat": 31.3236, "location_lng": 120.5853, "address": "江苏省苏州市姑苏区东北街178号",
         "description": "中国古典园林的代表作",
         "tags": ["江南园林", "世界遗产", "古建绝美"], "open_time": "07:30-17:30", "ticket_price": "¥70"},
        {"name": "周庄", "city": "苏州", "category": "风景名胜", "rating": 4.7, "heat_score": 8200,
         "location_lat": 31.1166, "location_lng": 120.8466, "address": "江苏省苏州市昆山市周庄镇",
         "description": "中国第一水乡",
         "tags": ["水乡古镇", "休闲度假", "拍照出片"], "open_time": "08:00-17:00", "ticket_price": "¥100"},
        
        # 重庆
        {"name": "洪崖洞", "city": "重庆", "category": "地标建筑", "rating": 4.7, "heat_score": 9100,
         "location_lat": 29.5630, "location_lng": 106.5752, "address": "重庆市渝中区嘉陵江滨江路",
         "description": "巴渝传统建筑特色",
         "tags": ["夜景绝美", "地标建筑", "逛吃逛喝"], "open_time": "全天", "ticket_price": "免费"},
        {"name": "解放碑", "city": "重庆", "category": "地标建筑", "rating": 4.6, "heat_score": 8700,
         "location_lat": 29.5527, "location_lng": 106.5694, "address": "重庆市渝中区",
         "description": "重庆的地标性建筑",
         "tags": ["地标建筑", "购物天堂", "citywalk"], "open_time": "全天", "ticket_price": "免费"},
        
        # 广州
        {"name": "广州塔", "city": "广州", "category": "地标建筑", "rating": 4.7, "heat_score": 9000,
         "location_lat": 23.1067, "location_lng": 113.3323, "address": "广东省广州市海珠区阅江西路222号",
         "description": "广州的新地标",
         "tags": ["地标建筑", "登高望远", "夜景绝美"], "open_time": "09:30-22:00", "ticket_price": "¥150"},
        
        # 深圳
        {"name": "世界之窗", "city": "深圳", "category": "休闲娱乐", "rating": 4.6, "heat_score": 8500,
         "location_lat": 22.5408, "location_lng": 113.9355, "address": "广东省深圳市南山区深南大道9037号",
         "description": "将世界奇观尽收眼底",
         "tags": ["主题公园", "必玩景点", "亲子乐园"], "open_time": "09:00-22:00", "ticket_price": "¥200"},
        
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
         "tags": ["历史文化", "地标建筑", "登高望远"], "open_time": "08:00-18:00", "ticket_price": "¥70"},
        
        # 厦门
        {"name": "鼓浪屿", "city": "厦门", "category": "风景名胜", "rating": 4.8, "heat_score": 9300,
         "location_lat": 24.4408, "location_lng": 118.1068, "address": "福建省厦门市思明区",
         "description": "'海上花园'，世界文化遗产",
         "tags": ["世界遗产", "浪漫爱情", "拍照出片"], "open_time": "全天", "ticket_price": "免费"},
        
        # 哈尔滨
        {"name": "冰雪大世界", "city": "哈尔滨", "category": "休闲娱乐", "rating": 4.8, "heat_score": 8900,
         "location_lat": 45.8918, "location_lng": 126.5450, "address": "黑龙江省哈尔滨市松北区",
         "description": "世界上最大的冰雪主题乐园",
         "tags": ["冰雪奇观", "必玩景点", "亲子乐园"], "open_time": "11:00-22:00", "ticket_price": "¥200"},
        
        # 拉萨
        {"name": "布达拉宫", "city": "拉萨", "category": "历史古迹", "rating": 4.9, "heat_score": 9600,
         "location_lat": 29.6578, "location_lng": 91.1172, "address": "西藏自治区拉萨市城关区北京中路",
         "description": "世界上海拔最高的宫殿",
         "tags": ["必玩景点", "世界遗产", "宗教信仰"], "open_time": "09:00-16:00", "ticket_price": "¥200"},
        
        # 桂林
        {"name": "漓江", "city": "桂林", "category": "风景名胜", "rating": 4.9, "heat_score": 9100,
         "location_lat": 25.2966, "location_lng": 110.2965, "address": "广西桂林市灵川县",
         "description": "'桂林山水甲天下'的核心",
         "tags": ["自然风光", "必玩景点", "山水画卷"], "open_time": "全天", "ticket_price": "免费"},
        
        # 三亚
        {"name": "蜈支洲岛", "city": "三亚", "category": "风景名胜", "rating": 4.8, "heat_score": 9000,
         "location_lat": 18.6468, "location_lng": 109.7606, "address": "海南省三亚市海棠湾镇",
         "description": "中国马尔代夫",
         "tags": ["海滨度假", "必玩景点", "海岛风光"], "open_time": "08:00-18:30", "ticket_price": "¥144"},
        
        # 东京
        {"name": "东京塔", "city": "东京", "category": "地标建筑", "rating": 4.6, "heat_score": 8800,
         "location_lat": 35.6586, "location_lng": 139.7454, "address": "东京都港区芝公园4-2-8",
         "description": "东京的象征",
         "tags": ["地标建筑", "夜景绝美", "登高望远"], "open_time": "09:00-23:00", "ticket_price": "¥120"},
        
        # 香港
        {"name": "维多利亚港", "city": "香港", "category": "风景名胜", "rating": 4.8, "heat_score": 9200,
         "location_lat": 22.2855, "location_lng": 114.1577, "address": "香港岛与九龙半岛之间",
         "description": "世界三大天然良港之一",
         "tags": ["夜景绝美", "地标建筑", "海港风光"], "open_time": "全天", "ticket_price": "免费"},
        
        # 巴黎
        {"name": "埃菲尔铁塔", "city": "巴黎", "category": "地标建筑", "rating": 4.8, "heat_score": 9800,
         "location_lat": 48.8584, "location_lng": 2.2945, "address": "法国巴黎战神广场",
         "description": "巴黎的标志性建筑",
         "tags": ["地标建筑", "必玩景点", "登高望远"], "open_time": "09:00-23:59", "ticket_price": "€26"},
        
        # 纽约
        {"name": "自由女神像", "city": "纽约", "category": "地标建筑", "rating": 4.8, "heat_score": 9500,
         "location_lat": 40.6892, "location_lng": -74.0445, "address": "美国纽约自由岛",
         "description": "美国的象征",
         "tags": ["地标建筑", "世界遗产", "必玩景点"], "open_time": "08:30-16:00", "ticket_price": "$24"},
    ]
    
    for spot_data in all_spots:
        spot = ScenicSpot(**spot_data)
        db.add(spot)
    
    db.commit()
    print(f"已添加 {len(all_spots)} 个景点")
    db.close()


if __name__ == "__main__":
    init_more_spots()
    print("数据初始化完成！")
