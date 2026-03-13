"""
添加美食数据 - 使用正确的Restaurant模型字段
"""
import sys
sys.path.insert(0, 'D:/travel/邮游世界/backend')
from models.database import SessionLocal, Restaurant

db = SessionLocal()
db.query(Restaurant).delete()

# 美食数据
restaurants = [
    # 北京
    {"name": "全聚德烤鸭店", "cuisine_type": "北京烤鸭", "rating": 4.6, "heat_score": 8500, "price_range": "¥¥¥", "location_lat": 39.9149, "location_lng": 116.4272, "open_time": "10:00-21:00", "tags": ["烤鸭", "老字号"], "images": ["https://images.unsplash.com/photo-1563245372065-b1853d23c2ed?w=800"]},
    {"name": "东来顺涮羊肉", "cuisine_type": "涮羊肉", "rating": 4.5, "heat_score": 8200, "price_range": "¥¥¥", "location_lat": 39.9149, "location_lng": 116.4072, "open_time": "11:00-22:00", "tags": ["涮肉", "铜锅"], "images": ["https://images.unsplash.com/photo-1574680096145-d05b474e2155?w=800"]},
    {"name": "护国寺小吃", "cuisine_type": "北京小吃", "rating": 4.4, "heat_score": 7800, "price_range": "¥", "location_lat": 39.9249, "location_lng": 116.3672, "open_time": "06:00-19:00", "tags": ["小吃", "老北京"], "images": ["https://images.unsplash.com/photo-1563245372065-b1853d23c2ed?w=800"]},
    {"name": "南锣鼓巷美食", "cuisine_type": "小吃", "rating": 4.3, "heat_score": 8000, "price_range": "¥", "location_lat": 39.9326, "location_lng": 116.4098, "open_time": "全天", "tags": ["网红", "小吃"], "images": ["https://images.unsplash.com/photo-1563245372065-b1853d23c2ed?w=800"]},
    {"name": "庆丰包子铺", "cuisine_type": "快餐", "rating": 4.3, "heat_score": 7500, "price_range": "¥", "location_lat": 39.9049, "location_lng": 116.4272, "open_time": "06:00-21:00", "tags": ["包子", "快餐"], "images": ["https://images.unsplash.com/photo-1563245372065-b1853d23c2ed?w=800"]},
    
    # 上海
    {"name": "绿波廊", "cuisine_type": "本帮菜", "rating": 4.5, "heat_score": 8200, "price_range": "¥¥", "location_lat": 31.2256, "location_lng": 121.4806, "open_time": "11:00-14:00 17:00-21:00", "tags": ["本帮菜", "老字号"], "images": ["https://images.unsplash.com/photo-1552566626-52f8b828add9?w=800"]},
    {"name": "南翔小笼", "cuisine_type": "小吃", "rating": 4.6, "heat_score": 8600, "price_range": "¥¥", "location_lat": 31.2256, "location_lng": 121.4706, "open_time": "10:00-20:00", "tags": ["小笼包", "老字号"], "images": ["https://images.unsplash.com/photo-1563245372065-b1853d23c2ed?w=800"]},
    {"name": "上海老饭店", "cuisine_type": "本帮菜", "rating": 4.4, "heat_score": 7800, "price_range": "¥¥¥", "location_lat": 31.2256, "location_lng": 121.4756, "open_time": "11:00-14:00 17:00-21:00", "tags": ["本帮菜", "红烧肉"], "images": ["https://images.unsplash.com/photo-1552566626-52f8b828add9?w=800"]},
    {"name": "光明邨大酒家", "cuisine_type": "本帮菜", "rating": 4.5, "heat_score": 8000, "price_range": "¥¥", "location_lat": 31.2156, "location_lng": 121.4756, "open_time": "10:00-21:00", "tags": ["本帮菜", "糟溜"], "images": ["https://images.unsplash.com/photo-1552566626-52f8b828add9?w=800"]},
    {"name": "沈大成", "cuisine_type": "糕点", "rating": 4.4, "heat_score": 7600, "price_range": "¥¥", "location_lat": 31.2256, "location_lng": 121.4756, "open_time": "08:00-20:00", "tags": ["糕团", "青团"], "images": ["https://images.unsplash.com/photo-1563245372065-b1853d23c2ed?w=800"]},
    
    # 成都
    {"name": "龙抄手", "cuisine_type": "川菜", "rating": 4.5, "heat_score": 8300, "price_range": "¥¥", "location_lat": 30.6716, "location_lng": 104.0656, "open_time": "08:00-21:00", "tags": ["抄手", "老字号"], "images": ["https://images.unsplash.com/photo-1563245372065-b1853d23c2ed?w=800"]},
    {"name": "麻婆豆腐", "cuisine_type": "川菜", "rating": 4.6, "heat_score": 8500, "price_range": "¥¥", "location_lat": 30.6616, "location_lng": 104.0556, "open_time": "11:00-21:00", "tags": ["川菜", "麻辣"], "images": ["https://images.unsplash.com/photo-1563245372065-b1853d23c2ed?w=800"]},
    {"name": "夫妻肺片", "cuisine_type": "川菜", "rating": 4.5, "heat_score": 8200, "price_range": "¥¥", "location_lat": 30.6516, "location_lng": 104.0656, "open_time": "10:00-21:00", "tags": ["川菜", "凉菜"], "images": ["https://images.unsplash.com/photo-1563245372065-b1853d23c2ed?w=800"]},
    {"name": "宽窄巷子美食", "cuisine_type": "小吃", "rating": 4.4, "heat_score": 8400, "price_range": "¥", "location_lat": 30.6686, "location_lng": 104.0556, "open_time": "全天", "tags": ["小吃", "网红"], "images": ["https://images.unsplash.com/photo-1563245372065-b1853d23c2ed?w=800"]},
    {"name": "锦里小吃", "cuisine_type": "小吃", "rating": 4.3, "heat_score": 8000, "price_range": "¥", "location_lat": 30.6606, "location_lng": 104.0506, "open_time": "全天", "tags": ["小吃", "成都"], "images": ["https://images.unsplash.com/photo-1563245372065-b1853d23c2ed?w=800"]},
    
    # 西安
    {"name": "同盛祥泡馍", "cuisine_type": "西北菜", "rating": 4.5, "heat_score": 8300, "price_range": "¥¥", "location_lat": 34.2597, "location_lng": 108.9433, "open_time": "07:00-21:00", "tags": ["泡馍", "老字号"], "images": ["https://images.unsplash.com/photo-1563245372065-b1853d23c2ed?w=800"]},
    {"name": "老孙家泡馍", "cuisine_type": "西北菜", "rating": 4.6, "heat_score": 8500, "price_range": "¥¥", "location_lat": 34.2597, "location_lng": 108.9433, "open_time": "07:00-21:00", "tags": ["泡馍", "百年老店"], "images": ["https://images.unsplash.com/photo-1563245372065-b1853d23c2ed?w=800"]},
    {"name": "回民街烤肉", "cuisine_type": "烧烤", "rating": 4.4, "heat_score": 8200, "price_range": "¥¥", "location_lat": 34.2597, "location_lng": 108.9433, "open_time": "12:00-24:00", "tags": ["烤肉", "回民"], "images": ["https://images.unsplash.com/photo-1563245372065-b1853d23c2ed?w=800"]},
    {"name": "春发生葫芦头", "cuisine_type": "西北菜", "rating": 4.4, "heat_score": 7800, "price_range": "¥¥", "location_lat": 34.2597, "location_lng": 108.9333, "open_time": "07:00-20:00", "tags": ["泡馍", "葫芦头"], "images": ["https://images.unsplash.com/photo-1563245372065-b1853d23c2ed?w=800"]},
    {"name": "贾三灌汤包", "cuisine_type": "小吃", "rating": 4.5, "heat_score": 8000, "price_range": "¥¥", "location_lat": 34.2597, "location_lng": 108.9433, "open_time": "06:00-21:00", "tags": ["灌汤包", "老字号"], "images": ["https://images.unsplash.com/photo-1563245372065-b1853d23c2ed?w=800"]},
    
    # 杭州
    {"name": "楼外楼", "cuisine_type": "杭帮菜", "rating": 4.6, "heat_score": 8600, "price_range": "¥¥¥", "location_lat": 30.2467, "location_lng": 120.1481, "open_time": "11:00-14:00 17:00-21:00", "tags": ["杭帮菜", "西湖醋鱼"], "images": ["https://images.unsplash.com/photo-1552566626-52f8b828add9?w=800"]},
    {"name": "知味观", "cuisine_type": "杭帮菜", "rating": 4.5, "heat_score": 8400, "price_range": "¥¥", "location_lat": 30.2467, "location_lng": 120.1381, "open_time": "07:00-21:00", "tags": ["点心", "小笼包"], "images": ["https://images.unsplash.com/photo-1563245372065-b1853d23c2ed?w=800"]},
    {"name": "外婆家", "cuisine_type": "杭帮菜", "rating": 4.4, "heat_score": 8200, "price_range": "¥¥", "location_lat": 30.2567, "location_lng": 120.1581, "open_time": "10:00-21:00", "tags": ["杭帮菜", "人气"], "images": ["https://images.unsplash.com/photo-1552566626-52f8b828add9?w=800"]},
    {"name": "龙井茶庄", "cuisine_type": "茶楼", "rating": 4.7, "heat_score": 8800, "price_range": "¥¥", "location_lat": 30.2365, "location_lng": 120.0565, "open_time": "08:00-20:00", "tags": ["茶楼", "龙井"], "images": ["https://images.unsplash.com/photo-1563245372065-b1853d23c2ed?w=800"]},
    {"name": "河坊街美食", "cuisine_type": "小吃", "rating": 4.3, "heat_score": 7800, "price_range": "¥", "location_lat": 30.2467, "location_lng": 120.1381, "open_time": "全天", "tags": ["小吃", "古街"], "images": ["https://images.unsplash.com/photo-1563245372065-b1853d23c2ed?w=800"]},
    
    # 重庆
    {"name": "德庄火锅", "cuisine_type": "火锅", "rating": 4.5, "heat_score": 8600, "price_range": "¥¥", "location_lat": 29.5527, "location_lng": 106.5694, "open_time": "10:00-02:00", "tags": ["火锅", "重庆"], "images": ["https://images.unsplash.com/photo-1563245372065-b1853d23c2ed?w=800"]},
    {"name": "小面一条街", "cuisine_type": "川菜", "rating": 4.4, "heat_score": 8200, "price_range": "¥", "location_lat": 29.5527, "location_lng": 106.5694, "open_time": "06:00-22:00", "tags": ["小面", "重庆"], "images": ["https://images.unsplash.com/photo-1563245372065-b1853d23c2ed?w=800"]},
    {"name": "磁器口麻花", "cuisine_type": "小吃", "rating": 4.3, "heat_score": 7800, "price_range": "¥", "location_lat": 29.6016, "location_lng": 106.3516, "open_time": "09:00-20:00", "tags": ["麻花", "特产"], "images": ["https://images.unsplash.com/photo-1563245372065-b1853d23c2ed?w=800"]},
    {"name": "南山泉水鸡", "cuisine_type": "川菜", "rating": 4.5, "heat_score": 8000, "price_range": "¥¥", "location_lat": 29.5316, "location_lng": 106.6016, "open_time": "11:00-21:00", "tags": ["泉水鸡", "特色"], "images": ["https://images.unsplash.com/photo-1563245372065-b1853d23c2ed?w=800"]},
    {"name": "江湖菜", "cuisine_type": "川菜", "rating": 4.4, "heat_score": 7900, "price_range": "¥¥", "location_lat": 29.5630, "location_lng": 106.5752, "open_time": "11:00-23:00", "tags": ["江湖菜", "辣子鸡"], "images": ["https://images.unsplash.com/photo-1563245372065-b1853d23c2ed?w=800"]},
    
    # 广州
    {"name": "陶陶居", "cuisine_type": "粤菜", "rating": 4.6, "heat_score": 8700, "price_range": "¥¥¥", "location_lat": 23.1257, "location_lng": 113.2606, "open_time": "07:00-22:00", "tags": ["早茶", "点心"], "images": ["https://images.unsplash.com/photo-1552566626-52f8b828add9?w=800"]},
    {"name": "点都德", "cuisine_type": "粤菜", "rating": 4.5, "heat_score": 8500, "price_range": "¥¥", "location_lat": 23.1156, "location_lng": 113.2456, "open_time": "08:00-22:00", "tags": ["早茶", "网红"], "images": ["https://images.unsplash.com/photo-1563245372065-b1853d23c2ed?w=800"]},
    {"name": "广州酒家", "cuisine_type": "粤菜", "rating": 4.5, "heat_score": 8400, "price_range": "¥¥¥", "location_lat": 23.1356, "location_lng": 113.2656, "open_time": "07:00-22:00", "tags": ["粤菜", "老字号"], "images": ["https://images.unsplash.com/photo-1552566626-52f8b828add9?w=800"]},
    {"name": "炳胜品味", "cuisine_type": "粤菜", "rating": 4.6, "heat_score": 8600, "price_range": "¥¥¥", "location_lat": 23.1257, "location_lng": 113.2606, "open_time": "11:00-14:00 17:00-21:00", "tags": ["粤菜", "高端"], "images": ["https://images.unsplash.com/photo-1552566626-52f8b828add9?w=800"]},
    {"name": "布拉肠粉", "cuisine_type": "小吃", "rating": 4.4, "heat_score": 8000, "price_range": "¥", "location_lat": 23.1056, "location_lng": 113.2656, "open_time": "06:00-14:00", "tags": ["肠粉", "早餐"], "images": ["https://images.unsplash.com/photo-1563245372065-b1853d23c2ed?w=800"]},
    
    # 厦门
    {"name": "沙茶面", "cuisine_type": "闽南菜", "rating": 4.5, "heat_score": 8200, "price_range": "¥¥", "location_lat": 24.4616, "location_lng": 118.0616, "open_time": "07:00-21:00", "tags": ["沙茶面", "厦门"], "images": ["https://images.unsplash.com/photo-1563245372065-b1853d23c2ed?w=800"]},
    {"name": "海蛎煎", "cuisine_type": "闽南菜", "rating": 4.4, "heat_score": 8000, "price_range": "¥¥", "location_lat": 24.4408, "location_lng": 118.1068, "open_time": "10:00-21:00", "tags": ["海蛎煎", "鼓浪屿"], "images": ["https://images.unsplash.com/photo-1563245372065-b1853d23c2ed?w=800"]},
    {"name": "花生汤", "cuisine_type": "小吃", "rating": 4.3, "heat_score": 7500, "price_range": "¥", "location_lat": 24.4316, "location_lng": 118.1016, "open_time": "08:00-20:00", "tags": ["甜品", "闽南"], "images": ["https://images.unsplash.com/photo-1563245372065-b1853d23c2ed?w=800"]},
    {"name": "1980烧肉粽", "cuisine_type": "小吃", "rating": 4.4, "heat_score": 7700, "price_range": "¥", "location_lat": 24.4616, "location_lng": 118.0616, "open_time": "08:00-21:00", "tags": ["粽子", "老字号"], "images": ["https://images.unsplash.com/photo-1563245372065-b1853d23c2ed?w=800"]},
    {"name": "土笋冻", "cuisine_type": "小吃", "rating": 4.3, "heat_score": 7400, "price_range": "¥", "location_lat": 24.4408, "location_lng": 118.1068, "open_time": "10:00-21:00", "tags": ["土笋冻", "特色"], "images": ["https://images.unsplash.com/photo-1563245372065-b1853d23c2ed?w=800"]},
    
    # 苏州
    {"name": "得月楼", "cuisine_type": "苏帮菜", "rating": 4.5, "heat_score": 8300, "price_range": "¥¥¥", "location_lat": 31.3236, "location_lng": 120.5853, "open_time": "11:00-14:00 17:00-21:00", "tags": ["苏帮菜", "松鼠桂鱼"], "images": ["https://images.unsplash.com/photo-1552566626-52f8b828add9?w=800"]},
    {"name": "松鹤楼", "cuisine_type": "苏帮菜", "rating": 4.6, "heat_score": 8500, "price_range": "¥¥¥", "location_lat": 31.3236, "location_lng": 120.5853, "open_time": "11:00-14:00 17:00-21:00", "tags": ["苏帮菜", "百年老店"], "images": ["https://images.unsplash.com/photo-1552566626-52f8b828add9?w=800"]},
    {"name": "平江路小吃", "cuisine_type": "小吃", "rating": 4.3, "heat_score": 7600, "price_range": "¥", "location_lat": 31.3316, "location_lng": 120.6516, "open_time": "全天", "tags": ["小吃", "古街"], "images": ["https://images.unsplash.com/photo-1563245372065-b1853d23c2ed?w=800"]},
    {"name": "阳澄湖大闸蟹", "cuisine_type": "河鲜", "rating": 4.7, "heat_score": 8800, "price_range": "¥¥¥", "location_lat": 31.5516, "location_lng": 120.9516, "open_time": "09:00-21:00", "tags": ["大闸蟹", "秋季"], "images": ["https://images.unsplash.com/photo-1563245372065-b1853d23c2ed?w=800"]},
    {"name": "桂花糖藕", "cuisine_type": "小吃", "rating": 4.4, "heat_score": 7500, "price_range": "¥", "location_lat": 31.3066, "location_lng": 120.5856, "open_time": "08:00-20:00", "tags": ["甜品", "苏州"], "images": ["https://images.unsplash.com/photo-1563245372065-b1853d23c2ed?w=800"]},
    
    # 丽江
    {"name": "腊排骨火锅", "cuisine_type": "纳西菜", "rating": 4.5, "heat_score": 8200, "price_range": "¥¥", "location_lat": 26.8721, "location_lng": 100.2299, "open_time": "10:00-22:00", "tags": ["腊排骨", "丽江"], "images": ["https://images.unsplash.com/photo-1563245372065-b1853d23c2ed?w=800"]},
    {"name": "纳西烤肉", "cuisine_type": "纳西菜", "rating": 4.4, "heat_score": 8000, "price_range": "¥¥", "location_lat": 26.8716, "location_lng": 100.2316, "open_time": "11:00-21:00", "tags": ["烤肉", "古城"], "images": ["https://images.unsplash.com/photo-1563245372065-b1853d23c2ed?w=800"]},
    {"name": "鸡豆凉粉", "cuisine_type": "小吃", "rating": 4.3, "heat_score": 7500, "price_range": "¥", "location_lat": 26.8721, "location_lng": 100.2299, "open_time": "09:00-21:00", "tags": ["凉粉", "纳西"], "images": ["https://images.unsplash.com/photo-1563245372065-b1853d23c2ed?w=800"]},
    {"name": "黑山羊火锅", "cuisine_type": "纳西菜", "rating": 4.5, "heat_score": 8100, "price_range": "¥¥", "location_lat": 26.9366, "location_lng": 100.2516, "open_time": "11:00-22:00", "tags": ["火锅", "束河"], "images": ["https://images.unsplash.com/photo-1563245372065-b1853d23c2ed?w=800"]},
    {"name": "云南米线", "cuisine_type": "小吃", "rating": 4.4, "heat_score": 7900, "price_range": "¥", "location_lat": 26.8721, "location_lng": 100.2299, "open_time": "07:00-21:00", "tags": ["米线", "过桥"], "images": ["https://images.unsplash.com/photo-1563245372065-b1853d23c2ed?w=800"]},
]

for r in restaurants:
    db.add(Restaurant(**r))

db.commit()
print(f"Added {len(restaurants)} restaurants")
db.close()
