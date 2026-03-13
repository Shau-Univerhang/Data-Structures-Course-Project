"""
继续添加更多景点数据 - 目标200+
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import SessionLocal, ScenicSpot

def add_even_more_spots():
    """继续添加更多景点"""
    db = SessionLocal()
    
    current_count = db.query(ScenicSpot).count()
    print(f"Current spots: {current_count}")
    
    # 按城市分组添加更多景点
    cities_data = {
        "北京": [
            {"name": "北海公园", "rating": 4.8, "heat_score": 8200, "lat": 39.9280, "lng": 116.3856, "category": "风景名胜", "tags": ["皇家园林", "湖光山色"]},
            {"name": "恭王府", "rating": 4.8, "heat_score": 8800, "lat": 39.9158, "lng": 116.3809, "category": "历史古迹", "tags": ["历史文化", "建筑宏伟"]},
            {"name": "798艺术区", "rating": 4.7, "heat_score": 7900, "lat": 39.9875, "lng": 116.5508, "category": "博物展览", "tags": ["博物展览", "拍照出片"]},
            {"name": "北京动物园", "rating": 4.6, "heat_score": 8100, "lat": 39.9495, "lng": 116.3381, "category": "休闲娱乐", "tags": ["亲子乐园", "动物观赏"]},
            {"name": "香山公园", "rating": 4.7, "heat_score": 7600, "lat": 39.9915, "lng": 116.1930, "category": "风景名胜", "tags": ["风景名胜", "登高望远"]},
            {"name": "雍和宫", "rating": 4.8, "heat_score": 8400, "lat": 39.9497, "lng": 116.4176, "category": "历史文化", "tags": ["历史文化", "宗教信仰"]},
            {"name": "国家博物馆", "rating": 4.9, "heat_score": 8900, "lat": 39.9056, "lng": 116.3974, "category": "博物展览", "tags": ["博物展览", "必玩景点"]},
            {"name": "南锣鼓巷", "rating": 4.6, "heat_score": 8600, "lat": 39.9326, "lng": 116.4098, "category": "地标建筑", "tags": ["市井烟火", "citywalk"]},
            {"name": "奥林匹克公园", "rating": 4.7, "heat_score": 8300, "lat": 40.0015, "lng": 116.4453, "category": "地标建筑", "tags": ["地标建筑", "城市公园"]},
            {"name": "什刹海", "rating": 4.6, "heat_score": 8000, "lat": 39.9403, "lng": 116.3756, "category": "风景名胜", "tags": ["历史文化", "citywalk"]},
        ],
        "上海": [
            {"name": "静安寺", "rating": 4.7, "heat_score": 7800, "lat": 31.2301, "lng": 121.4456, "category": "历史文化", "tags": ["历史文化", "宗教信仰"]},
            {"name": "南京路步行街", "rating": 4.7, "heat_score": 8900, "lat": 31.2356, "lng": 121.4756, "category": "地标建筑", "tags": ["购物天堂", "citywalk"]},
            {"name": "武康路", "rating": 4.7, "heat_score": 8200, "lat": 31.2086, "lng": 121.4356, "category": "地标建筑", "tags": ["历史文化", "拍照出片"]},
            {"name": "田子坊", "rating": 4.6, "heat_score": 8100, "lat": 31.2056, "lng": 121.4606, "category": "地标建筑", "tags": ["市井烟火", "文艺小资"]},
            {"name": "新天地", "rating": 4.6, "heat_score": 7700, "lat": 31.2186, "lng": 121.4706, "category": "地标建筑", "tags": ["时尚地标", "购物"]},
            {"name": "上海博物馆", "rating": 4.8, "heat_score": 8500, "lat": 31.2256, "lng": 121.4756, "category": "博物展览", "tags": ["博物展览", "历史文化"]},
            {"name": "世博园", "rating": 4.5, "heat_score": 7500, "lat": 31.1856, "lng": 121.3206, "category": "休闲娱乐", "tags": ["主题公园", "城市公园"]},
            {"name": "迪士尼小镇", "rating": 4.7, "heat_score": 8800, "lat": 31.1430, "lng": 121.6600, "category": "地标建筑", "tags": ["主题公园", "购物"]},
        ],
        "西安": [
            {"name": "西安城墙", "rating": 4.8, "heat_score": 8800, "lat": 34.2580, "lng": 108.9456, "category": "历史古迹", "tags": ["地标建筑", "登高望远"]},
            {"name": "回民街", "rating": 4.6, "heat_score": 8500, "lat": 34.2597, "lng": 108.9433, "category": "地标建筑", "tags": ["逛吃逛喝", "市井烟火"]},
            {"name": "华清宫", "rating": 4.7, "heat_score": 8600, "lat": 34.4317, "lng": 109.2111, "category": "历史古迹", "tags": ["历史文化", "温泉体验"]},
            {"name": "大唐芙蓉园", "rating": 4.6, "heat_score": 8100, "lat": 34.2156, "lng": 108.9656, "category": "风景名胜", "tags": ["主题公园", "历史文化"]},
            {"name": "陕西历史博物馆", "rating": 4.9, "heat_score": 9000, "lat": 34.2156, "lng": 108.9456, "category": "博物展览", "tags": ["博物展览", "必玩景点"]},
            {"name": "永兴坊", "rating": 4.5, "heat_score": 7400, "lat": 34.2656, "lng": 108.9556, "category": "地标建筑", "tags": ["美食街区", "市井烟火"]},
        ],
        "成都": [
            {"name": "锦里古街", "rating": 4.6, "heat_score": 8300, "lat": 30.6606, "lng": 104.0506, "category": "地标建筑", "tags": ["市井烟火", "三国文化"]},
            {"name": "都江堰", "rating": 4.9, "heat_score": 9100, "lat": 30.9919, "lng": 103.5773, "category": "历史古迹", "tags": ["世界遗产", "必玩景点"]},
            {"name": "青城山", "rating": 4.8, "heat_score": 8800, "lat": 30.8912, "lng": 103.5313, "category": "风景名胜", "tags": ["道教文化", "自然风光"]},
            {"name": "杜甫草堂", "rating": 4.7, "heat_score": 8000, "lat": 30.7456, "lng": 104.0256, "category": "历史文化", "tags": ["历史文化", "古建绝美"]},
            {"name": "武侯祠", "rating": 4.7, "heat_score": 8200, "lat": 30.6556, "lng": 104.0456, "category": "历史文化", "tags": ["三国文化", "历史古迹"]},
            {"name": "春熙路", "rating": 4.6, "heat_score": 8500, "lat": 30.6656, "lng": 104.0656, "category": "地标建筑", "tags": ["购物天堂", "citywalk"]},
            {"name": "成都大熊猫基地", "rating": 4.9, "heat_score": 9400, "lat": 30.7416, "lng": 104.1277, "category": "休闲娱乐", "tags": ["必玩景点", "亲子乐园"]},
        ],
        "杭州": [
            {"name": "宋城", "rating": 4.6, "heat_score": 8200, "lat": 30.1836, "lng": 120.1656, "category": "休闲娱乐", "tags": ["主题公园", "演艺表演"]},
            {"name": "西溪湿地", "rating": 4.8, "heat_score": 8500, "lat": 30.0816, "lng": 120.0716, "category": "风景名胜", "tags": ["自然风光", "生态休闲"]},
            {"name": "雷峰塔", "rating": 4.6, "heat_score": 7800, "lat": 30.2366, "lng": 120.1481, "category": "地标建筑", "tags": ["地标建筑", "历史文化"]},
            {"name": "断桥残雪", "rating": 4.7, "heat_score": 8100, "lat": 30.2467, "lng": 120.1581, "category": "风景名胜", "tags": ["湖光山色", "浪漫爱情"]},
            {"name": "灵隐寺", "rating": 4.8, "heat_score": 9000, "lat": 30.2365, "lng": 120.0965, "category": "历史文化", "tags": ["佛教文化", "古建绝美"]},
            {"name": "清河坊", "rating": 4.5, "heat_score": 7400, "lat": 30.2566, "lng": 120.1356, "category": "地标建筑", "tags": ["市井烟火", "逛街购物"]},
        ],
        "青岛": [
            {"name": "崂山", "rating": 4.8, "heat_score": 8400, "lat": 36.1075, "lng": 120.6512, "category": "风景名胜", "tags": ["风景名胜", "道教文化"]},
            {"name": "八大关", "rating": 4.7, "heat_score": 8100, "lat": 36.0516, "lng": 120.3666, "category": "地标建筑", "tags": ["建筑艺术", "拍照出片"]},
            {"name": "金沙滩", "rating": 4.6, "heat_score": 8000, "lat": 35.9516, "lng": 120.2516, "category": "风景名胜", "tags": ["海滨度假", "休闲娱乐"]},
            {"name": "啤酒街", "rating": 4.5, "heat_score": 7600, "lat": 36.0716, "lng": 120.3916, "category": "地标建筑", "tags": ["美食街区", "市井烟火"]},
            {"name": "小鱼山", "rating": 4.6, "heat_score": 7300, "lat": 36.0536, "lng": 120.3816, "category": "风景名胜", "tags": ["登高望远", "城市全景"]},
        ],
        "苏州": [
            {"name": "周庄古镇", "rating": 4.7, "heat_score": 8200, "lat": 31.1166, "lng": 120.8466, "category": "风景名胜", "tags": ["水乡古镇", "休闲度假"]},
            {"name": "同里古镇", "rating": 4.6, "heat_score": 7800, "lat": 31.0366, "lng": 120.8866, "category": "风景名胜", "tags": ["水乡古镇", "世界遗产"]},
            {"name": "寒山寺", "rating": 4.6, "heat_score": 8000, "lat": 31.2766, "lng": 120.5956, "category": "历史文化", "tags": ["佛教文化", "古建绝美"]},
            {"name": "山塘街", "rating": 4.6, "heat_score": 8100, "lat": 31.3066, "lng": 120.5856, "category": "地标建筑", "tags": ["水乡古镇", "市井烟火"]},
            {"name": "网师园", "rating": 4.7, "heat_score": 7600, "lat": 31.3266, "lng": 120.5656, "category": "风景名胜", "tags": ["江南园林", "世界遗产"]},
        ],
        "重庆": [
            {"name": "磁器口古镇", "rating": 4.5, "heat_score": 8000, "lat": 29.6016, "lng": 106.3516, "category": "地标建筑", "tags": ["市井烟火", "古镇风貌"]},
            {"name": "武隆天生三桥", "rating": 4.8, "heat_score": 8500, "lat": 29.3316, "lng": 107.7516, "category": "风景名胜", "tags": ["自然风光", "世界遗产"]},
            {"name": "李子坝轻轨站", "rating": 4.6, "heat_score": 8200, "lat": 29.5516, "lng": 106.5416, "category": "地标建筑", "tags": ["网红打卡", "特色体验"]},
            {"name": "南山一棵树", "rating": 4.6, "heat_score": 7900, "lat": 29.5316, "lng": 106.6016, "category": "风景名胜", "tags": ["夜景绝美", "登高望远"]},
            {"name": "鹅岭二厂", "rating": 4.5, "heat_score": 7500, "lat": 29.5516, "lng": 106.5716, "category": "地标建筑", "tags": ["文艺小资", "拍照出片"]},
        ],
        "广州": [
            {"name": "上下九步行街", "rating": 4.5, "heat_score": 7700, "lat": 23.1156, "lng": 113.2456, "category": "地标建筑", "tags": ["购物天堂", "老广州"]},
            {"name": "珠江夜游", "rating": 4.6, "heat_score": 8000, "lat": 23.1056, "lng": 113.2656, "category": "休闲娱乐", "tags": ["夜景绝美", "特色体验"]},
            {"name": "白云山", "rating": 4.6, "heat_score": 7800, "lat": 23.1856, "lng": 113.2756, "category": "风景名胜", "tags": ["登高望远", "自然风光"]},
            {"name": "陈家祠", "rating": 4.7, "heat_score": 8100, "lat": 23.1256, "lng": 113.2556, "category": "历史文化", "tags": ["古建绝美", "岭南文化"]},
            {"name": "沙面岛", "rating": 4.6, "heat_score": 7900, "lat": 23.1056, "lng": 113.2356, "category": "地标建筑", "tags": ["建筑艺术", "citywalk"]},
        ],
        "深圳": [
            {"name": "东部华侨城", "rating": 4.6, "heat_score": 8200, "lat": 22.5266, "lng": 114.0556, "category": "休闲娱乐", "tags": ["主题公园", "必玩景点"]},
            {"name": "深圳湾公园", "rating": 4.5, "heat_score": 7500, "lat": 22.5166, "lng": 114.0256, "category": "风景名胜", "tags": ["城市公园", "海滨风光"]},
            {"name": "欢乐海岸", "rating": 4.5, "heat_score": 7400, "lat": 22.5366, "lng": 114.0456, "category": "地标建筑", "tags": ["购物天堂", "休闲娱乐"]},
            {"name": "大梅沙", "rating": 4.5, "heat_score": 7700, "lat": 22.5966, "lng": 114.2756, "category": "风景名胜", "tags": ["海滨度假", "休闲娱乐"]},
        ],
        "南京": [
            {"name": "总统府", "rating": 4.7, "heat_score": 8600, "lat": 32.0276, "lng": 118.7969, "category": "历史文化", "tags": ["历史文化", "近代史"]},
            {"name": "玄武湖", "rating": 4.6, "heat_score": 8100, "lat": 32.0576, "lng": 118.7869, "category": "风景名胜", "tags": ["城市公园", "湖光山色"]},
            {"name": "明孝陵", "rating": 4.8, "heat_score": 8700, "lat": 32.0676, "lng": 118.8269, "category": "历史古迹", "tags": ["世界遗产", "历史文化"]},
            {"name": "侵华日军南京大屠杀遇难同胞纪念馆", "rating": 4.9, "heat_score": 9000, "lat": 32.0376, "lng": 118.7569, "category": "博物展览", "tags": ["爱国教育", "历史纪念馆"]},
            {"name": "中华门", "rating": 4.6, "heat_score": 7800, "lat": 32.0076, "lng": 118.7869, "category": "历史古迹", "tags": ["古城墙", "地标建筑"]},
        ],
    }
    
    for city, spots in cities_data.items():
        for spot_info in spots:
            # 检查是否存在
            exists = db.query(ScenicSpot).filter(
                ScenicSpot.name == spot_info['name']
            ).first()
            
            if not exists:
                spot = ScenicSpot(
                    name=spot_info['name'],
                    city=city,
                    category=spot_info.get('category', '风景名胜'),
                    rating=spot_info.get('rating', 4.5),
                    heat_score=spot_info.get('heat_score', 5000),
                    location_lat=spot_info.get('lat'),
                    location_lng=spot_info.get('lng'),
                    description=f"{city}的著名景点",
                    tags=spot_info.get('tags', []),
                    open_time="全天",
                    ticket_price="免费"
                )
                db.add(spot)
    
    db.commit()
    new_count = db.query(ScenicSpot).count()
    print(f"Total spots now: {new_count}")
    db.close()


if __name__ == "__main__":
    add_even_more_spots()
