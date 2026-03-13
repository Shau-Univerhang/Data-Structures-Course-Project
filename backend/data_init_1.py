"""
数据初始化脚本 - 景点数据（第一部分：北京、上海、西安）
"""
import sys
import json
sys.path.append("..")

from models.database import SessionLocal, ScenicSpot

def init_beijing_spots():
    """初始化北京景点数据"""
    db = SessionLocal()
    
    beijing_spots = [
        {"name": "故宫博物院", "city": "北京", "category": "历史古迹", "rating": 4.9, "heat_score": 9850, 
         "location_lat": 39.9163, "location_lng": 116.3972, "address": "北京市东城区景山前街4号",
         "description": "世界上现存规模最大、保存最为完整的木质结构古建筑之一",
         "tags": ["建筑宏伟", "历史厚重", "必玩景点"], "open_time": "08:30-17:00", "ticket_price": "¥60"},
        {"name": "天坛公园", "city": "北京", "category": "历史古迹", "rating": 4.9, "heat_score": 9200,
         "location_lat": 39.9022, "location_lng": 116.4106, "address": "北京市东城区天坛内东里7号",
         "description": "明清两代帝王祭祀皇天、祈五谷丰登的场所",
         "tags": ["古建绝美", "声学奇迹", "历史文化"], "open_time": "06:00-21:00", "ticket_price": "¥15"},
        {"name": "颐和园", "city": "北京", "category": "风景名胜", "rating": 4.9, "heat_score": 9100,
         "location_lat": 39.9998, "location_lng": 116.6172, "address": "北京市海淀区新建宫门路19号",
         "description": "清代皇家的园林，以昆明湖、万寿山为基址，汲取江南园林的设计手法",
         "tags": ["皇家园林", "湖光山色", "休闲娱乐"], "open_time": "06:30-18:00", "ticket_price": "¥30"},
        {"name": "长城-八达岭", "city": "北京", "category": "历史古迹", "rating": 4.8, "heat_score": 9800,
         "location_lat": 40.4319, "location_lng": 116.5704, "address": "北京市延庆区G6京藏高速58号出口",
         "description": "中国古代伟大的防御工程，万里长城的重要组成部分",
         "tags": ["必玩景点", "地标建筑", "登高望远"], "open_time": "06:30-19:00", "ticket_price": "¥40"},
        {"name": "天安门广场", "city": "北京", "category": "地标建筑", "rating": 4.8, "heat_score": 9500,
         "location_lat": 39.9054, "location_lng": 116.3976, "address": "北京市东城区",
         "description": "世界上最大的城市广场之一",
         "tags": ["升旗仪式", "庄严神圣", "地标建筑"], "open_time": "全天", "ticket_price": "免费"},
        {"name": "圆明园", "city": "北京", "category": "历史古迹", "rating": 4.7, "heat_score": 8500,
         "location_lat": 40.0094, "location_lng": 116.3063, "address": "北京市海淀区清华西路28号",
         "description": "清代著名的皇家园林，被誉为'万园之园'",
         "tags": ["历史遗址", "园林景观", "爱国教育"], "open_time": "07:00-21:00", "ticket_price": "¥10"},
        {"name": "景山公园", "city": "北京", "category": "风景名胜", "rating": 4.8, "heat_score": 7800,
         "location_lat": 39.9213, "location_lng": 116.3970, "address": "北京市西城区景山西街44号",
         "description": "可以俯瞰故宫全景的绝佳观赏点",
         "tags": ["登高望远", "古建绝美", "citywalk"], "open_time": "06:00-21:00", "ticket_price": "¥2"},
        {"name": "北海公园", "city": "北京", "category": "风景名胜", "rating": 4.8, "heat_score": 8200,
         "location_lat": 39.9280, "location_lng": 116.3856, "address": "北京市西城区文津街1号",
         "description": "中国现存最古老、最完整、最具综合性和代表性的皇家园林之一",
         "tags": ["皇家园林", "湖光山色", "休闲娱乐"], "open_time": "06:30-21:00", "ticket_price": "¥10"},
        {"name": "恭王府", "city": "北京", "category": "历史古迹", "rating": 4.8, "heat_score": 8800,
         "location_lat": 39.9158, "location_lng": 116.3809, "address": "北京市西城区前海西街17号",
         "description": "清代规模最大的一座王府建筑群",
         "tags": ["历史文化", "建筑宏伟", "非遗体验"], "open_time": "08:00-17:00", "ticket_price": "¥40"},
        {"name": "南锣鼓巷", "city": "北京", "category": "地标建筑", "rating": 4.6, "heat_score": 8600,
         "location_lat": 39.9326, "location_lng": 116.4098, "address": "北京市东城区南锣鼓巷",
         "description": "北京最古老的街区之一，是古今交融的典型代表",
         "tags": ["市井烟火", "citywalk", "逛吃逛喝"], "open_time": "全天", "ticket_price": "免费"},
        {"name": "798艺术区", "city": "北京", "category": "博物展览", "rating": 4.7, "heat_score": 7900,
         "location_lat": 39.9875, "location_lng": 116.5508, "address": "北京市朝阳区酒仙桥路4号",
         "description": "原为原国营798厂等电子工业老厂区，现为艺术区",
         "tags": ["博物展览", "拍照出片", "文艺小资"], "open_time": "全天", "ticket_price": "免费"},
        {"name": "北京动物园", "city": "北京", "category": "休闲娱乐", "rating": 4.6, "heat_score": 8100,
         "location_lat": 39.9495, "location_lng": 116.3381, "address": "北京市西城区西直门外大街137号",
         "description": "中国最大的动物园之一",
         "tags": ["亲子乐园", "休闲娱乐", "动物观赏"], "open_time": "07:30-18:00", "ticket_price": "¥15"},
        {"name": "香山公园", "city": "北京", "category": "风景名胜", "rating": 4.7, "heat_score": 7600,
         "location_lat": 39.9915, "location_lng": 116.1930, "address": "北京市海淀区香山公园",
         "description": "以香山红叶闻名的皇家园林",
         "tags": ["风景名胜", "登高望远", "自然风光"], "open_time": "06:00-18:30", "ticket_price": "¥5"},
        {"name": "雍和宫", "city": "北京", "category": "历史文化", "rating": 4.8, "heat_score": 8400,
         "location_lat": 39.9497, "location_lng": 116.4176, "address": "北京市东城区雍和宫大街12号",
         "description": "北京最大的藏传佛教寺院",
         "tags": ["历史文化", "宗教信仰", "建筑宏伟"], "open_time": "09:00-16:30", "ticket_price": "¥25"},
        {"name": "国家博物馆", "city": "北京", "category": "博物展览", "rating": 4.9, "heat_score": 8900,
         "location_lat": 39.9056, "location_lng": 116.3974, "address": "北京市东城区东长安街16号",
         "description": "中国最大的综合性博物馆",
         "tags": ["博物展览", "历史文化", "必玩景点"], "open_time": "09:00-17:00", "ticket_price": "免费"},
    ]
    
    for spot_data in beijing_spots:
        spot = ScenicSpot(**spot_data)
        db.add(spot)
    
    db.commit()
    print(f"已添加 {len(beijing_spots)} 个北京景点")
    db.close()


def init_shanghai_spots():
    """初始化上海景点数据"""
    db = SessionLocal()
    
    shanghai_spots = [
        {"name": "外滩", "city": "上海", "category": "地标建筑", "rating": 4.9, "heat_score": 9700,
         "location_lat": 31.2456, "location_lng": 121.4901, "address": "上海市黄浦区中山东一路",
         "description": "上海最具代表性的景观，汇合了万国建筑群",
         "tags": ["地标建筑", "夜景绝美", "citywalk"], "open_time": "全天", "ticket_price": "免费"},
        {"name": "东方明珠", "city": "上海", "category": "地标建筑", "rating": 4.7, "heat_score": 9300,
         "location_lat": 31.2401, "location_lng": 121.5019, "address": "上海市浦东新区世纪大道1号",
         "description": "上海标志性建筑之一",
         "tags": ["地标建筑", "登高望远", "夜景绝美"], "open_time": "08:00-21:30", "ticket_price": "¥199"},
        {"name": "豫园", "city": "上海", "category": "风景名胜", "rating": 4.8, "heat_score": 8600,
         "location_lat": 31.2256, "location_lng": 121.4806, "address": "上海市黄浦区安仁街137号",
         "description": "始建于明代的古典园林",
         "tags": ["江南园林", "历史文化", "古建绝美"], "open_time": "08:30-17:00", "ticket_price": "¥40"},
        {"name": "田子坊", "city": "上海", "category": "地标建筑", "rating": 4.6, "heat_score": 8100,
         "location_lat": 31.2056, "location_lng": 121.4606, "address": "上海市黄浦区泰康路210弄",
         "description": "最具代表性的石库门里弄文化",
         "tags": ["市井烟火", "文艺小资", "逛吃逛喝"], "open_time": "全天", "ticket_price": "免费"},
        {"name": "上海迪士尼乐园", "city": "上海", "category": "休闲娱乐", "rating": 4.8, "heat_score": 9500,
         "location_lat": 31.1430, "location_lng": 121.6600, "address": "上海市浦东新区川沙镇黄赵路310号",
         "description": "中国大陆第一个迪士尼主题乐园",
         "tags": ["亲子乐园", "必玩景点", "休闲娱乐"], "open_time": "08:30-20:30", "ticket_price": "¥475"},
        {"name": "静安寺", "city": "上海", "category": "历史文化", "rating": 4.7, "heat_score": 7800,
         "location_lat": 31.2301, "location_lng": 121.4456, "address": "上海市静安区南京西路1686号",
         "description": "上海最古老的佛寺",
         "tags": ["历史文化", "宗教信仰", "建筑宏伟"], "open_time": "07:30-17:00", "ticket_price": "¥50"},
        {"name": "南京路步行街", "city": "上海", "category": "地标建筑", "rating": 4.7, "heat_score": 8900,
         "location_lat": 31.2356, "location_lng": 121.4756, "address": "上海市黄浦区南京东路",
         "description": "中国最繁华的商业街之一",
         "tags": ["逛吃逛喝", "购物天堂", "citywalk"], "open_time": "全天", "ticket_price": "免费"},
        {"name": "武康路", "city": "上海", "category": "地标建筑", "rating": 4.7, "heat_score": 8200,
         "location_lat": 31.2086, "location_lng": 121.4356, "address": "上海市徐汇区武康路",
         "description": "被誉为'浓缩了上海近代百年历史'的名人路",
         "tags": ["历史文化", "citywalk", "拍照出片"], "open_time": "全天", "ticket_price": "免费"},
    ]
    
    for spot_data in shanghai_spots:
        spot = ScenicSpot(**spot_data)
        db.add(spot)
    
    db.commit()
    print(f"已添加 {len(shanghai_spots)} 个上海景点")
    db.close()


def init_xian_spots():
    """初始化西安景点数据"""
    db = SessionLocal()
    
    xian_spots = [
        {"name": "秦始皇兵马俑", "city": "西安", "category": "历史古迹", "rating": 4.9, "heat_score": 9900,
         "location_lat": 34.3843, "location_lng": 109.2785, "address": "陕西省西安市临潼区秦陵北路",
         "description": "世界第八大奇迹，古代陶俑艺术的巅峰之作",
         "tags": ["必玩景点", "历史厚重", "世界遗产"], "open_time": "08:30-18:00", "ticket_price": "¥120"},
        {"name": "大雁塔", "city": "西安", "category": "历史古迹", "rating": 4.8, "heat_score": 9000,
         "location_lat": 34.2194, "location_lng": 108.9597, "address": "陕西省西安市雁塔区大雁塔南广场",
         "description": "唐代著名的佛教建筑",
         "tags": ["历史文化", "古建绝美", "地标建筑"], "open_time": "08:00-18:30", "ticket_price": "¥50"},
        {"name": "西安城墙", "city": "西安", "category": "历史古迹", "rating": 4.8, "heat_score": 8800,
         "location_lat": 34.2580, "location_lng": 108.9456, "address": "陕西省西安市碑林区南大街",
         "description": "中国现存规模最大、保存最完整的古代城垣",
         "tags": ["地标建筑", "登高望远", "citywalk"], "open_time": "08:00-22:00", "ticket_price": "¥54"},
        {"name": "回民街", "city": "西安", "category": "地标建筑", "rating": 4.6, "heat_score": 8500,
         "location_lat": 34.2597, "location_lng": 108.9433, "address": "陕西省西安市莲湖区北院门",
         "description": "西安著名的美食文化街区",
         "tags": ["逛吃逛喝", "市井烟火", "美食天堂"], "open_time": "全天", "ticket_price": "免费"},
        {"name": "华清宫", "city": "西安", "category": "历史古迹", "rating": 4.7, "heat_score": 8600,
         "location_lat": 34.4317, "location_lng": 109.2111, "address": "陕西省西安市临潼区华清路38号",
         "description": "唐代皇家温泉行宫",
         "tags": ["历史文化", "皇家园林", "温泉体验"], "open_time": "07:00-19:00", "ticket_price": "¥120"},
    ]
    
    for spot_data in xian_spots:
        spot = ScenicSpot(**spot_data)
        db.add(spot)
    
    db.commit()
    print(f"已添加 {len(xian_spots)} 个西安景点")
    db.close()


if __name__ == "__main__":
    init_beijing_spots()
    init_shanghai_spots()
    init_xian_spots()
    print("数据初始化完成！")
