"""
添加美食数据
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import SessionLocal, Restaurant, ScenicSpot

def add_restaurants():
    """添加美食餐厅数据"""
    db = SessionLocal()
    
    # 获取北京景点ID
    beijing_spots = db.query(ScenicSpot).filter(ScenicSpot.city == "北京").limit(10).all()
    
    restaurants = [
        # 北京美食
        {"name": "全聚德烤鸭店", "spot_id": 1, "cuisine_type": "京菜", "rating": 4.6, "heat_score": 8500, "lat": 39.9170, "lng": 116.3975, "price_range": "100-150", "tags": ["烤鸭", "老字号"]},
        {"name": "东来顺涮羊肉", "spot_id": 1, "cuisine_type": "火锅", "rating": 4.5, "heat_score": 7800, "lat": 39.9180, "lng": 116.3980, "price_range": "80-120", "tags": ["火锅", "老字号"]},
        {"name": "南门涮肉", "spot_id": 1, "cuisine_type": "火锅", "rating": 4.7, "heat_score": 8200, "lat": 39.9165, "lng": 116.3970, "price_range": "100-150", "tags": ["火锅", "铜锅"]},
        {"name": "四季民福", "spot_id": 1, "cuisine_type": "京菜", "rating": 4.6, "heat_score": 8000, "lat": 39.9190, "lng": 116.3965, "price_range": "80-120", "tags": ["烤鸭", "北京菜"]},
        {"name": "便宜坊", "spot_id": 1, "cuisine_type": "京菜", "rating": 4.5, "heat_score": 7600, "lat": 39.9160, "lng": 116.3985, "price_range": "70-100", "tags": ["烤鸭", "老字号"]},
        {"name": "护国寺小吃", "spot_id": 1, "cuisine_type": "小吃", "rating": 4.4, "heat_score": 7000, "lat": 39.9250, "lng": 116.3800, "price_range": "20-40", "tags": ["小吃", "老北京"]},
        {"name": "豆汁儿", "spot_id": 1, "cuisine_type": "小吃", "rating": 4.2, "heat_score": 5500, "lat": 39.9240, "lng": 116.3790, "price_range": "10-20", "tags": ["特色小吃", "老北京"]},
        {"name": "隆福寺小吃", "spot_id": 1, "cuisine_type": "小吃", "rating": 4.3, "heat_score": 6000, "lat": 39.9290, "lng": 116.4316, "price_range": "20-40", "tags": ["小吃", "老北京"]},
        
        # 上海美食
        {"name": "南翔小笼", "spot_id": 11, "cuisine_type": "小吃", "rating": 4.6, "heat_score": 8200, "lat": 31.2260, "lng": 121.4810, "price_range": "20-40", "tags": ["小吃", "老字号"]},
        {"name": "绿波廊", "spot_id": 11, "cuisine_type": "本帮菜", "rating": 4.5, "heat_score": 7600, "lat": 31.2270, "lng": 121.4820, "price_range": "80-120", "tags": ["本帮菜", "老字号"]},
        {"name": "上海老饭店", "spot_id": 11, "cuisine_type": "本帮菜", "rating": 4.5, "heat_score": 7500, "lat": 31.2280, "lng": 121.4800, "price_range": "80-120", "tags": ["本帮菜", "老字号"]},
        {"name": "小杨生煎", "spot_id": 11, "cuisine_type": "小吃", "rating": 4.4, "heat_score": 7000, "lat": 31.2300, "lng": 121.4750, "price_range": "15-30", "tags": ["生煎", "网红"]},
        {"name": "王家沙", "spot_id": 11, "cuisine_type": "本帮菜", "rating": 4.4, "heat_score": 6800, "lat": 31.2250, "lng": 121.4700, "price_range": "40-60", "tags": ["老字号", "点心"]},
        
        # 成都美食
        {"name": "龙抄手", "spot_id": 15, "cuisine_type": "川菜", "rating": 4.5, "heat_score": 7800, "lat": 30.6690, "lng": 104.0560, "price_range": "20-40", "tags": ["小吃", "老字号"]},
        {"name": "钟水饺", "spot_id": 15, "cuisine_type": "川菜", "rating": 4.4, "heat_score": 7200, "lat": 30.6700, "lng": 104.0550, "price_range": "15-30", "tags": ["小吃", "老字号"]},
        {"name": "夫妻肺片", "spot_id": 15, "cuisine_type": "川菜", "rating": 4.5, "heat_score": 7600, "lat": 30.6710, "lng": 104.0540, "price_range": "30-50", "tags": ["川菜", "特色"]},
        {"name": "麻婆豆腐", "spot_id": 15, "cuisine_type": "川菜", "rating": 4.6, "heat_score": 8000, "lat": 30.6720, "lng": 104.0530, "price_range": "40-60", "tags": ["川菜", "经典"]},
        {"name": "火锅", "spot_id": 15, "cuisine_type": "火锅", "rating": 4.7, "heat_score": 8500, "lat": 30.6730, "lng": 104.0520, "price_range": "80-150", "tags": ["火锅", "必吃"]},
        
        # 西安美食
        {"name": "肉夹馍", "spot_id": 18, "cuisine_type": "西北菜", "rating": 4.6, "heat_score": 8200, "lat": 34.2600, "lng": 108.9440, "price_range": "10-20", "tags": ["小吃", "必吃"]},
        {"name": "羊肉泡馍", "spot_id": 18, "cuisine_type": "西北菜", "rating": 4.5, "heat_score": 7800, "lat": 34.2590, "lng": 108.9430, "price_range": "30-50", "tags": ["特色", "必吃"]},
        {"name": "凉皮", "spot_id": 18, "cuisine_type": "小吃", "rating": 4.4, "heat_score": 7200, "lat": 34.2580, "lng": 108.9420, "price_range": "10-20", "tags": ["小吃", "特色"]},
        {"name": "biangbiang面", "spot_id": 18, "cuisine_type": "面食", "rating": 4.5, "heat_score": 7600, "lat": 34.2570, "lng": 108.9410, "price_range": "20-40", "tags": ["面食", "特色"]},
        {"name": "灌汤包", "spot_id": 18, "cuisine_type": "小吃", "rating": 4.4, "heat_score": 7000, "lat": 34.2560, "lng": 108.9400, "price_range": "20-40", "tags": ["小吃", "老字号"]},
        
        # 杭州美食
        {"name": "西湖醋鱼", "spot_id": 22, "cuisine_type": "浙菜", "rating": 4.5, "heat_score": 7800, "lat": 30.2470, "lng": 120.1490, "price_range": "60-100", "tags": ["杭帮菜", "特色"]},
        {"name": "龙井虾仁", "spot_id": 22, "cuisine_type": "浙菜", "rating": 4.6, "heat_score": 8200, "lat": 30.2480, "lng": 120.1500, "price_range": "80-120", "tags": ["杭帮菜", "特色"]},
        {"name": "东坡肉", "spot_id": 22, "cuisine_type": "浙菜", "rating": 4.5, "heat_score": 7600, "lat": 30.2490, "lng": 120.1510, "price_range": "50-80", "tags": ["杭帮菜", "经典"]},
        {"name": "叫化鸡", "spot_id": 22, "cuisine_type": "浙菜", "rating": 4.4, "heat_score": 7000, "lat": 30.2500, "lng": 120.1520, "price_range": "60-100", "tags": ["杭帮菜", "特色"]},
        {"name": "片儿川", "spot_id": 22, "cuisine_type": "面食", "rating": 4.3, "heat_score": 6500, "lat": 30.2510, "lng": 120.1530, "price_range": "20-40", "tags": ["面食", "杭州"]},
        
        # 广州美食
        {"name": "早茶", "spot_id": 25, "cuisine_type": "粤菜", "rating": 4.7, "heat_score": 8800, "lat": 23.1260, "lng": 113.2610, "price_range": "40-80", "tags": ["粤菜", "必吃"]},
        {"name": "烧腊", "spot_id": 25, "cuisine_type": "粤菜", "rating": 4.6, "heat_score": 8200, "lat": 23.1270, "lng": 113.2620, "price_range": "30-60", "tags": ["粤菜", "特色"]},
        {"name": "肠粉", "spot_id": 25, "cuisine_type": "小吃", "rating": 4.5, "heat_score": 7600, "lat": 23.1280, "lng": 113.2630, "price_range": "15-30", "tags": ["小吃", "广州"]},
        {"name": "糖水", "spot_id": 25, "cuisine_type": "甜品", "rating": 4.4, "heat_score": 7000, "lat": 23.1290, "lng": 113.2640, "price_range": "10-25", "tags": ["甜品", "糖水"]},
        {"name": "煲仔饭", "spot_id": 25, "cuisine_type": "粤菜", "rating": 4.5, "heat_score": 7400, "lat": 23.1300, "lng": 113.2650, "price_range": "30-50", "tags": ["粤菜", "特色"]},
        
        # 重庆美食
        {"name": "重庆火锅", "spot_id": 28, "cuisine_type": "火锅", "rating": 4.8, "heat_score": 9200, "lat": 29.5530, "lng": 106.5760, "price_range": "80-150", "tags": ["火锅", "必吃"]},
        {"name": "小面", "spot_id": 28, "cuisine_type": "小吃", "rating": 4.5, "heat_score": 8000, "lat": 29.5540, "lng": 106.5770, "price_range": "10-20", "tags": ["小吃", "重庆"]},
        {"name": "酸辣粉", "spot_id": 28, "cuisine_type": "小吃", "rating": 4.4, "heat_score": 7400, "lat": 29.5550, "lng": 106.5780, "price_range": "10-20", "tags": ["小吃", "重庆"]},
        {"name": "江湖菜", "spot_id": 28, "cuisine_type": "川菜", "rating": 4.5, "heat_score": 7800, "lat": 29.5560, "lng": 106.5790, "price_range": "50-100", "tags": ["川菜", "特色"]},
        {"name": "辣子鸡", "spot_id": 28, "cuisine_type": "川菜", "rating": 4.5, "heat_score": 7600, "lat": 29.5570, "lng": 106.5800, "price_range": "40-80", "tags": ["川菜", "经典"]},
        
        # 青岛美食
        {"name": "海鲜", "spot_id": 31, "cuisine_type": "海鲜", "rating": 4.6, "heat_score": 8200, "lat": 36.0680, "lng": 120.3830, "price_range": "80-200", "tags": ["海鲜", "必吃"]},
        {"name": "青岛啤酒", "spot_id": 31, "cuisine_type": "饮品", "rating": 4.7, "heat_score": 8600, "lat": 36.0690, "lng": 120.3840, "price_range": "10-30", "tags": ["啤酒", "特色"]},
        {"name": "蛤蜊", "spot_id": 31, "cuisine_type": "海鲜", "rating": 4.5, "heat_score": 7400, "lat": 36.0700, "lng": 120.3850, "price_range": "30-60", "tags": ["海鲜", "特色"]},
        {"name": "鲅鱼水饺", "spot_id": 31, "cuisine_type": "小吃", "rating": 4.4, "heat_score": 7000, "lat": 36.0710, "lng": 120.3860, "price_range": "20-40", "tags": ["小吃", "特色"]},
        
        # 苏州美食
        {"name": "松鼠桂鱼", "spot_id": 36, "cuisine_type": "苏帮菜", "rating": 4.6, "heat_score": 8000, "lat": 31.3240, "lng": 120.5860, "price_range": "80-150", "tags": ["苏帮菜", "经典"]},
        {"name": "响油鳝糊", "spot_id": 36, "cuisine_type": "苏帮菜", "rating": 4.5, "heat_score": 7600, "lat": 31.3250, "lng": 120.5870, "price_range": "60-100", "tags": ["苏帮菜", "特色"]},
        {"name": "蟹粉豆腐", "spot_id": 36, "cuisine_type": "苏帮菜", "rating": 4.4, "heat_score": 7200, "lat": 31.3260, "lng": 120.5880, "price_range": "40-80", "tags": ["苏帮菜", "特色"]},
        {"name": "糕点", "spot_id": 36, "cuisine_type": "小吃", "rating": 4.5, "heat_score": 7800, "lat": 31.3270, "lng": 120.5890, "price_range": "20-50", "tags": ["糕点", "老字号"]},
        
        # 南京美食
        {"name": "盐水鸭", "spot_id": 39, "cuisine_type": "金陵菜", "rating": 4.6, "heat_score": 8200, "lat": 32.0180, "lng": 118.7880, "price_range": "30-60", "tags": ["金陵菜", "特色"]},
        {"name": "鸭血粉丝汤", "spot_id": 39, "cuisine_type": "小吃", "rating": 4.5, "heat_score": 7600, "lat": 32.0190, "lng": 118.7890, "price_range": "15-30", "tags": ["小吃", "南京"]},
        {"name": "小笼包", "spot_id": 39, "cuisine_type": "小吃", "rating": 4.4, "heat_score": 7200, "lat": 32.0200, "lng": 118.7900, "price_range": "20-40", "tags": ["小吃", "老字号"]},
        {"name": "秦淮八绝", "spot_id": 39, "cuisine_type": "小吃", "rating": 4.5, "heat_score": 7400, "lat": 32.0210, "lng": 118.7910, "price_range": "30-60", "tags": ["小吃", "特色"]},
    ]
    
    for rest_data in restaurants:
        rest = Restaurant(
            name=rest_data['name'],
            spot_id=rest_data.get('spot_id', 1),
            cuisine_type=rest_data.get('cuisine_type', '地方菜'),
            rating=rest_data.get('rating', 4.0),
            heat_score=rest_data.get('heat_score', 5000),
            location_lat=rest_data.get('lat'),
            location_lng=rest_data.get('lng'),
            price_range=rest_data.get('price_range', '50-100'),
            tags=rest_data.get('tags', [])
        )
        db.add(rest)
    
    db.commit()
    count = db.query(Restaurant).count()
    print(f"Total restaurants: {count}")
    db.close()


if __name__ == "__main__":
    add_restaurants()
