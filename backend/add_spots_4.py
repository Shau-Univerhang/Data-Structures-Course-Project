"""
添加长沙、南昌、郑州、洛阳等城市景点
"""
import sys
sys.path.insert(0, 'D:/travel/邮游世界/backend')
from models.database import SessionLocal, ScenicSpot

db = SessionLocal()

# 长沙
changsha_spots = [
    {"name": "岳麓山", "city": "长沙", "rating": 4.6, "heat_score": 8000, "location_lat": 28.6016, "location_lng": 112.9316, "category": "风景名胜", "tags": ["自然风光", "历史文化"], "description": "岳麓书院所在地", "open_time": "06:00-23:00", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800"]},
    {"name": "橘子洲", "city": "长沙", "rating": 4.6, "heat_score": 8200, "location_lat": 28.5916, "location_lng": 112.9516, "category": "风景名胜", "tags": ["城市公园", "红色旅游"], "description": "青年毛泽东雕像所在地", "open_time": "全天", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800"]},
    {"name": "火宫殿", "city": "长沙", "rating": 4.5, "heat_score": 7600, "location_lat": 28.5816, "location_lng": 112.9416, "category": "地标建筑", "tags": ["美食天堂", "老长沙"], "description": "长沙著名的小吃一条街", "open_time": "全天", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800"]},
    {"name": "岳麓书院", "city": "长沙", "rating": 4.7, "heat_score": 8200, "location_lat": 28.6016, "location_lng": 112.9316, "category": "历史文化", "tags": ["千年学府", "古建"], "description": "中国古代四大书院之一", "open_time": "07:30-18:00", "ticket_price": "50元", "images": ["https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800"]},
    {"name": "湖南省博物馆", "city": "长沙", "rating": 4.8, "heat_score": 8500, "location_lat": 28.5716, "location_lng": 112.9416, "category": "博物展览", "tags": ["历史文化", "必玩景点"], "description": "马王堆汉墓文物", "open_time": "09:00-17:00", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800"]},
    {"name": "太平街", "city": "长沙", "rating": 4.4, "heat_score": 7200, "location_lat": 28.5816, "location_lng": 112.9316, "category": "地标建筑", "tags": ["老街", "市井烟火"], "description": "长沙古城保存最完整的街区", "open_time": "全天", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800"]},
    {"name": "坡子街", "city": "长沙", "rating": 4.4, "heat_score": 7300, "location_lat": 28.5816, "location_lng": 112.9416, "category": "地标建筑", "tags": ["美食天堂", "老长沙"], "description": "长沙最古老的街道之一", "open_time": "全天", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800"]},
    {"name": "天心阁", "city": "长沙", "rating": 4.4, "heat_score": 6900, "location_lat": 28.5916, "location_lng": 112.9316, "category": "历史古迹", "tags": ["古建", "登高"], "description": "长沙古城的历史标志", "open_time": "08:00-17:30", "ticket_price": "32元", "images": ["https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800"]},
    {"name": "贾谊故居", "city": "长沙", "rating": 4.3, "heat_score": 6500, "location_lat": 28.5816, "location_lng": 112.9316, "category": "历史古迹", "tags": ["历史文化", "古建"], "description": "贾谊在长沙的故居", "open_time": "09:00-17:00", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800"]},
    {"name": "靖港古镇", "city": "长沙", "rating": 4.4, "heat_score": 6800, "location_lat": 28.5016, "location_lng": 112.8516, "category": "风景名胜", "tags": ["古镇风貌", "湘江"], "description": "湖南重要的历史文化古镇", "open_time": "全天", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800"]},
]

# 郑州/洛阳/开封
zhengzhou_spots = [
    {"name": "少林寺", "city": "郑州", "rating": 4.8, "heat_score": 9000, "location_lat": 34.5116, "location_lng": 112.9316, "category": "历史文化", "tags": ["佛教圣地", "武术之乡"], "description": "中国功夫的发源地", "open_time": "07:00-18:00", "ticket_price": "80元", "images": ["https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800"]},
    {"name": "嵩山", "city": "郑州", "rating": 4.7, "heat_score": 8200, "location_lat": 34.4516, "location_lng": 112.9516, "category": "风景名胜", "tags": ["自然风光", "道教文化"], "description": "中华五岳之一", "open_time": "07:00-18:00", "ticket_price": "80元", "images": ["https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800"]},
    {"name": "龙门石窟", "city": "洛阳", "rating": 4.9, "heat_score": 9100, "location_lat": 34.5516, "location_lng": 112.4716, "category": "历史古迹", "tags": ["世界遗产", "石窟艺术"], "description": "中国三大石窟之一", "open_time": "07:30-18:00", "ticket_price": "90元", "images": ["https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800"]},
    {"name": "白马寺", "city": "洛阳", "rating": 4.7, "heat_score": 8200, "location_lat": 34.7316, "location_lng": 112.5816, "category": "历史文化", "tags": ["佛教祖庭", "古建"], "description": "中国第一古刹", "open_time": "07:30-18:00", "ticket_price": "35元", "images": ["https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800"]},
    {"name": "洛阳古城", "city": "洛阳", "rating": 4.5, "heat_score": 7800, "location_lat": 34.6216, "location_lng": 112.4516, "category": "地标建筑", "tags": ["古城", "历史"], "description": "洛阳老城历史文化街区", "open_time": "全天", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800"]},
    {"name": "清明上河园", "city": "开封", "rating": 4.6, "heat_score": 8000, "location_lat": 34.8116, "location_lng": 114.3416, "category": "休闲娱乐", "tags": ["主题公园", "宋代文化"], "description": "以清明上河图为蓝本建造", "open_time": "08:30-22:00", "ticket_price": "120元", "images": ["https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800"]},
    {"name": "龙亭公园", "city": "开封", "rating": 4.5, "heat_score": 7500, "location_lat": 34.7916, "location_lng": 114.3516, "category": "风景名胜", "tags": ["皇家园林", "历史文化"], "description": "北宋皇宫遗址", "open_time": "07:00-19:00", "ticket_price": "45元", "images": ["https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800"]},
    {"name": "包公祠", "city": "开封", "rating": 4.4, "heat_score": 7000, "location_lat": 34.7916, "location_lng": 114.3316, "category": "历史文化", "tags": ["历史人物", "古建"], "description": "纪念包拯的祠堂", "open_time": "07:00-19:00", "ticket_price": "30元", "images": ["https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800"]},
    {"name": "开封铁塔", "city": "开封", "rating": 4.5, "heat_score": 7200, "location_lat": 34.8216, "location_lng": 114.3516, "category": "历史古迹", "tags": ["古建", "地标"], "description": "天下第一塔", "open_time": "08:00-18:00", "ticket_price": "50元", "images": ["https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800"]},
    {"name": "嵩山少林寺塔林", "city": "郑州", "rating": 4.6, "heat_score": 7800, "location_lat": 34.5116, "location_lng": 112.9216, "category": "历史古迹", "tags": ["古建", "墓塔"], "description": "中国最大的塔林", "open_time": "07:00-18:00", "ticket_price": "含在少林寺门票", "images": ["https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800"]},
]

# 济南/太原
jinan_spots = [
    {"name": "趵突泉", "city": "济南", "rating": 4.7, "heat_score": 8000, "location_lat": 36.6516, "location_lng": 117.0116, "category": "风景名胜", "tags": ["天下第一泉", "园林景观"], "description": "济南七十二名泉之首", "open_time": "07:00-18:00", "ticket_price": "40元", "images": ["https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800"]},
    {"name": "大明湖", "city": "济南", "rating": 4.6, "heat_score": 7800, "location_lat": 36.6516, "location_lng": 117.0316, "category": "风景名胜", "tags": ["城市公园", "湖光山色"], "description": "济南三大名胜之一", "open_time": "全天", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800"]},
    {"name": "千佛山", "city": "济南", "rating": 4.5, "heat_score": 7500, "location_lat": 36.6516, "location_lng": 117.0516, "category": "风景名胜", "tags": ["佛教文化", "登高望远"], "description": "济南三大名胜之一", "open_time": "06:30-18:00", "ticket_price": "30元", "images": ["https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800"]},
    {"name": "黑虎泉", "city": "济南", "rating": 4.5, "heat_score": 7200, "location_lat": 36.6616, "location_lng": 117.0216, "category": "风景名胜", "tags": ["泉水", "市井"], "description": "济南四大名泉之一", "open_time": "全天", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800"]},
    {"name": "芙蓉街", "city": "济南", "rating": 4.4, "heat_score": 7100, "location_lat": 36.6516, "location_lng": 117.0116, "category": "地标建筑", "tags": ["美食天堂", "老街"], "description": "济南最著名的小吃街", "open_time": "全天", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800"]},
    {"name": "晋祠", "city": "太原", "rating": 4.7, "heat_score": 8000, "location_lat": 37.7016, "location_lng": 112.4516, "category": "历史古迹", "tags": ["古建绝美", "园林艺术"], "description": "晋国宗祠", "open_time": "08:00-18:00", "ticket_price": "65元", "images": ["https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800"]},
    {"name": "太原古县城", "city": "太原", "rating": 4.4, "heat_score": 7000, "location_lat": 37.7016, "location_lng": 112.5016, "category": "地标建筑", "tags": ["古城", "历史"], "description": "明清时期的太原城", "open_time": "全天", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800"]},
    {"name": "双塔寺", "city": "太原", "rating": 4.5, "heat_score": 6800, "location_lat": 37.8716, "location_lng": 112.5516, "category": "历史文化", "tags": ["佛教", "古建"], "description": "太原的标志性建筑", "open_time": "08:00-17:30", "ticket_price": "30元", "images": ["https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800"]},
    {"name": "蒙山大佛", "city": "太原", "rating": 4.5, "heat_score": 7200, "location_lat": 37.7216, "location_lng": 112.4516, "category": "历史文化", "tags": ["佛教", "大佛"], "description": "世界第二大佛", "open_time": "08:00-17:00", "ticket_price": "70元", "images": ["https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800"]},
    {"name": "山西博物院", "city": "太原", "rating": 4.6, "heat_score": 7300, "location_lat": 37.8716, "location_lng": 112.5216, "category": "博物展览", "tags": ["历史文化", "文物"], "description": "山西最大的综合性博物馆", "open_time": "09:00-17:00", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800"]},
]

for s in changsha_spots:
    db.add(ScenicSpot(**s))
for s in zhengzhou_spots:
    db.add(ScenicSpot(**s))
for s in jinan_spots:
    db.add(ScenicSpot(**s))

db.commit()
print("Added Changsha, Zhengzhou, Jinan spots")
print("Total spots:", db.query(ScenicSpot).count())
db.close()
