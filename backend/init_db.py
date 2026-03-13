"""
数据库初始化脚本 - 一键初始化所有数据
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import SessionLocal, ScenicSpot, Restaurant, RoadNode, RoadEdge, Building, Facility
from datetime import datetime


def init_all_data():
    """初始化所有数据"""
    db = SessionLocal()
    
    # 检查是否已有数据
    if db.query(ScenicSpot).first():
        print("Data already exists, skipping init")
        db.close()
        return
    
    print("Starting data initialization...")
    
    # 1. 景点数据
    spots_data = [
        # 北京
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
         "description": "清代皇家的园林，以昆明湖、万寿山为基址",
         "tags": ["皇家园林", "湖光山色", "休闲娱乐"], "open_time": "06:30-18:00", "ticket_price": "¥30"},
        {"name": "长城-八达岭", "city": "北京", "category": "历史古迹", "rating": 4.8, "heat_score": 9800,
         "location_lat": 40.4319, "location_lng": 116.5704, "address": "北京市延庆区",
         "description": "中国古代伟大的防御工程，万里长城的重要组成部分",
         "tags": ["必玩景点", "地标建筑", "登高望远"], "open_time": "06:30-19:00", "ticket_price": "¥40"},
        {"name": "天安门广场", "city": "北京", "category": "地标建筑", "rating": 4.8, "heat_score": 9500,
         "location_lat": 39.9054, "location_lng": 116.3976, "address": "北京市东城区",
         "description": "世界上最大的城市广场之一",
         "tags": ["升旗仪式", "庄严神圣", "地标建筑"], "open_time": "全天", "ticket_price": "免费"},
        
        # 上海
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
        
        # 西安
        {"name": "秦始皇兵马俑", "city": "西安", "category": "历史古迹", "rating": 4.9, "heat_score": 9900,
         "location_lat": 34.3843, "location_lng": 109.2785, "address": "陕西省西安市临潼区秦陵北路",
         "description": "世界第八大奇迹，古代陶俑艺术的巅峰之作",
         "tags": ["必玩景点", "历史厚重", "世界遗产"], "open_time": "08:30-18:00", "ticket_price": "¥120"},
        {"name": "大雁塔", "city": "西安", "category": "历史古迹", "rating": 4.8, "heat_score": 9000,
         "location_lat": 34.2194, "location_lng": 108.9597, "address": "陕西省西安市雁塔区",
         "description": "唐代著名的佛教建筑",
         "tags": ["历史文化", "古建绝美", "地标建筑"], "open_time": "08:00-18:30", "ticket_price": "¥50"},
        
        # 成都
        {"name": "大熊猫繁育研究基地", "city": "成都", "category": "休闲娱乐", "rating": 4.9, "heat_score": 9400,
         "location_lat": 30.7416, "location_lng": 104.1277, "address": "四川省成都市成华区熊猫大道1375号",
         "description": "全球最大的大熊猫繁育研究机构",
         "tags": ["必玩景点", "亲子乐园", "动物观赏"], "open_time": "07:30-18:00", "ticket_price": "¥55"},
        {"name": "宽窄巷子", "city": "成都", "category": "地标建筑", "rating": 4.7, "heat_score": 8700,
         "location_lat": 30.6686, "location_lng": 104.0556, "address": "四川省成都市青羊区长顺上街127号",
         "description": "成都三大历史文化保护区之一",
         "tags": ["市井烟火", "citywalk", "逛吃逛喝"], "open_time": "全天", "ticket_price": "免费"},
        
        # 杭州
        {"name": "西湖", "city": "杭州", "category": "风景名胜", "rating": 4.9, "heat_score": 9900,
         "location_lat": 30.2467, "location_lng": 120.1481, "address": "浙江省杭州市西湖区",
         "description": "中国著名的风景名胜区",
         "tags": ["必玩景点", "湖光山色", "浪漫爱情"], "open_time": "全天", "ticket_price": "免费"},
        {"name": "灵隐寺", "city": "杭州", "category": "历史文化", "rating": 4.8, "heat_score": 9000,
         "location_lat": 30.2365, "location_lng": 120.0965, "address": "浙江省杭州市西湖区灵隐路",
         "description": "江南著名古刹",
         "tags": ["佛教文化", "历史文化", "古建绝美"], "open_time": "07:00-18:00", "ticket_price": "¥75"},
        
        # 青岛
        {"name": "栈桥", "city": "青岛", "category": "地标建筑", "rating": 4.7, "heat_score": 8800,
         "location_lat": 36.0671, "location_lng": 120.3826, "address": "山东省青岛市市南区太平路12号",
         "description": "青岛的标志性建筑",
         "tags": ["地标建筑", "海景风光", "citywalk"], "open_time": "全天", "ticket_price": "免费"},
        {"name": "五四广场", "city": "青岛", "category": "地标建筑", "rating": 4.7, "heat_score": 8600,
         "location_lat": 36.0626, "location_lng": 120.3766, "address": "山东省青岛市市南区",
         "description": "青岛最具标志性的城市广场",
         "tags": ["地标建筑", "夜景绝美", "citywalk"], "open_time": "全天", "ticket_price": "免费"},
    ]
    
    for spot_data in spots_data:
        spot = ScenicSpot(**spot_data)
        db.add(spot)
    
    db.commit()
    print("OK - Added {} spots".format(len(spots_data)))
    
    # 2. 餐厅数据
    restaurants_data = [
        {"name": "全聚德烤鸭店", "spot_id": 1, "cuisine_type": "京菜", "rating": 4.6, "heat_score": 8500,
         "location_lat": 39.9170, "location_lng": 116.3975, "price_range": "¥100-150", "tags": ["烤鸭", "老字号"]},
        {"name": "东来顺涮羊肉", "spot_id": 1, "cuisine_type": "火锅", "rating": 4.5, "heat_score": 7800,
         "location_lat": 39.9180, "location_lng": 116.3980, "price_range": "¥80-120", "tags": ["火锅", "老字号"]},
        {"name": "南门涮肉", "spot_id": 1, "cuisine_type": "火锅", "rating": 4.7, "heat_score": 8200,
         "location_lat": 39.9165, "location_lng": 116.3970, "price_range": "¥100-150", "tags": ["火锅", "铜锅"]},
    ]
    
    for rest_data in restaurants_data:
        rest = Restaurant(**rest_data)
        db.add(rest)
    
    db.commit()
    print("OK - Added {} restaurants".format(len(restaurants_data)))
    
    # 3. 道路节点和边（故宫示例）
    # 获取故宫的spot_id
    palace = db.query(ScenicSpot).filter(ScenicSpot.name == "故宫博物院").first()
    if palace:
        # 道路节点
        nodes_data = [
            {"spot_id": palace.id, "name": "午门", "location_lat": 39.9155, "location_lng": 116.3972, "node_type": "entrance"},
            {"spot_id": palace.id, "name": "太和殿", "location_lat": 39.9163, "location_lng": 116.3975, "node_type": "building"},
            {"spot_id": palace.id, "name": "中和殿", "location_lat": 39.9168, "location_lng": 116.3973, "node_type": "building"},
            {"spot_id": palace.id, "name": "保和殿", "location_lat": 39.9172, "location_lng": 116.3970, "node_type": "building"},
            {"spot_id": palace.id, "name": "乾清宫", "location_lat": 39.9180, "location_lng": 116.3968, "node_type": "building"},
            {"spot_id": palace.id, "name": "御花园", "location_lat": 39.9185, "location_lng": 116.3965, "node_type": "building"},
            {"spot_id": palace.id, "name": "神武门", "location_lat": 39.9190, "location_lng": 116.3970, "node_type": "exit"},
        ]
        
        nodes = []
        for node_data in nodes_data:
            node = RoadNode(**node_data)
            db.add(node)
            nodes.append(node)
        
        db.commit()
        print("OK - Added {} road nodes".format(len(nodes)))
        
        # 道路边
        edges_data = [
            {"spot_id": palace.id, "from_node_id": 1, "to_node_id": 2, "distance": 100, "road_type": "walk"},
            {"spot_id": palace.id, "from_node_id": 2, "to_node_id": 3, "distance": 80, "road_type": "walk"},
            {"spot_id": palace.id, "from_node_id": 3, "to_node_id": 4, "distance": 80, "road_type": "walk"},
            {"spot_id": palace.id, "from_node_id": 4, "to_node_id": 5, "distance": 120, "road_type": "walk"},
            {"spot_id": palace.id, "from_node_id": 5, "to_node_id": 6, "distance": 100, "road_type": "walk"},
            {"spot_id": palace.id, "from_node_id": 6, "to_node_id": 7, "distance": 90, "road_type": "walk"},
        ]
        
        for i, edge_data in enumerate(edges_data):
            edge_data['from_node_id'] = nodes[i].id
            edge_data['to_node_id'] = nodes[i+1].id
            edge = RoadEdge(**edge_data)
            db.add(edge)
        
        db.commit()
        print("OK - Added {} road edges".format(len(edges_data)))
    
    db.close()
    print("\n=== Database Init Completed! ===")


if __name__ == "__main__":
    init_all_data()
