"""
添加三亚、桂林、哈尔滨等城市景点
"""
import sys
sys.path.insert(0, 'D:/travel/邮游世界/backend')
from models.database import SessionLocal, ScenicSpot

db = SessionLocal()

# 三亚
sanya_spots = [
    {"name": "亚龙湾", "city": "三亚", "rating": 4.8, "heat_score": 9100, "location_lat": 18.6721, "location_lng": 109.6416, "category": "风景名胜", "tags": ["海滨度假", "必玩景点"], "description": "天下第一湾", "open_time": "全天", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800"]},
    {"name": "天涯海角", "city": "三亚", "rating": 4.5, "heat_score": 8200, "location_lat": 18.2816, "location_lng": 109.4516, "category": "风景名胜", "tags": ["海景风光", "浪漫爱情"], "description": "海南最具代表性的景区", "open_time": "07:30-18:30", "ticket_price": "81元", "images": ["https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800"]},
    {"name": "蜈支洲岛", "city": "三亚", "rating": 4.7, "heat_score": 8800, "location_lat": 18.6416, "location_lng": 109.7516, "category": "风景名胜", "tags": ["海岛风情", "水上运动"], "description": "中国最佳潜水基地之一", "open_time": "08:00-17:30", "ticket_price": "144元", "images": ["https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800"]},
    {"name": "南山文化旅游区", "city": "三亚", "rating": 4.7, "heat_score": 8500, "location_lat": 18.3416, "location_lng": 109.5016, "category": "历史文化", "tags": ["佛教文化", "宗教圣地"], "description": "依托南山福泽深厚的地域文化", "open_time": "08:00-17:30", "ticket_price": "121元", "images": ["https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800"]},
    {"name": "大小洞天", "city": "三亚", "rating": 4.6, "heat_score": 7800, "location_lat": 18.3916, "location_lng": 109.5516, "category": "风景名胜", "tags": ["道教文化", "海景风光"], "description": "海山奇观", "open_time": "07:30-18:30", "ticket_price": "75元", "images": ["https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800"]},
    {"name": "鹿回头风景区", "city": "三亚", "rating": 4.5, "heat_score": 7500, "location_lat": 18.2816, "location_lng": 109.5016, "category": "风景名胜", "tags": ["登高望远", "夜景绝美"], "description": "三亚最佳观景点", "open_time": "08:00-22:00", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800"]},
    {"name": "三亚湾椰梦长廊", "city": "三亚", "rating": 4.5, "heat_score": 8000, "location_lat": 18.2516, "location_lng": 109.4516, "category": "风景名胜", "tags": ["海景风光", "日落"], "description": "三亚最美日落观赏点", "open_time": "全天", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800"]},
    {"name": "大东海", "city": "三亚", "rating": 4.4, "heat_score": 7700, "location_lat": 18.2316, "location_lng": 109.5316, "category": "风景名胜", "tags": ["海滨度假", "休闲娱乐"], "description": "三亚最著名的海滨浴场", "open_time": "全天", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800"]},
    {"name": "亚特兰蒂斯水世界", "city": "三亚", "rating": 4.6, "heat_score": 8200, "location_lat": 18.6816, "location_lng": 109.6416, "category": "休闲娱乐", "tags": ["水上乐园", "亲子"], "description": "全球顶级水上乐园", "open_time": "10:00-18:00", "ticket_price": "298元", "images": ["https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800"]},
    {"name": "三亚千古情", "city": "三亚", "rating": 4.5, "heat_score": 7600, "location_lat": 18.3216, "location_lng": 109.4716, "category": "休闲娱乐", "tags": ["演艺表演", "主题公园"], "description": "一生必看的演出", "open_time": "14:00-21:00", "ticket_price": "280元", "images": ["https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800"]},
]

# 桂林
guilin_spots = [
    {"name": "漓江", "city": "桂林", "rating": 4.9, "heat_score": 9300, "location_lat": 25.2965, "location_lng": 110.4806, "category": "风景名胜", "tags": ["自然风光", "必玩景点"], "description": "桂林山水甲天下", "open_time": "全天", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800"]},
    {"name": "象山景区", "city": "桂林", "rating": 4.6, "heat_score": 7800, "location_lat": 25.2666, "location_lng": 110.2756, "category": "风景名胜", "tags": ["地标建筑", "城市公园"], "description": "桂林山水的象征", "open_time": "06:30-18:30", "ticket_price": "55元", "images": ["https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800"]},
    {"name": "阳朔西街", "city": "桂林", "rating": 4.5, "heat_score": 8200, "location_lat": 24.7816, "location_lng": 110.4916, "category": "地标建筑", "tags": ["市井烟火", "洋人街"], "description": "阳朔最繁华的商业街", "open_time": "全天", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800"]},
    {"name": "遇龙河", "city": "桂林", "rating": 4.7, "heat_score": 8600, "location_lat": 24.7916, "location_lng": 110.5216, "category": "风景名胜", "tags": ["竹筏漂流", "自然风光"], "description": "小漓江", "open_time": "全天", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800"]},
    {"name": "芦笛岩", "city": "桂林", "rating": 4.6, "heat_score": 7800, "location_lat": 25.3216, "location_lng": 110.2916, "category": "风景名胜", "tags": ["溶洞", "地下奇观"], "description": "大自然艺术之宫", "open_time": "08:00-17:30", "ticket_price": "110元", "images": ["https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800"]},
    {"name": "叠彩山", "city": "桂林", "rating": 4.5, "heat_score": 7200, "location_lat": 25.2816, "location_lng": 110.2916, "category": "风景名胜", "tags": ["登高望远", "桂林山水"], "description": "桂林最高峰", "open_time": "06:30-18:00", "ticket_price": "35元", "images": ["https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800"]},
    {"name": "七星公园", "city": "桂林", "rating": 4.5, "heat_score": 7100, "location_lat": 25.2716, "location_lng": 110.2516, "category": "风景名胜", "tags": ["城市公园", "溶洞"], "description": "桂林最大的综合性公园", "open_time": "06:00-18:00", "ticket_price": "55元", "images": ["https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800"]},
    {"name": "十里画廊", "city": "桂林", "rating": 4.6, "heat_score": 8000, "location_lat": 24.7916, "location_lng": 110.4716, "category": "风景名胜", "tags": ["自然风光", "骑行"], "description": "阳朔最经典的骑行路线", "open_time": "全天", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800"]},
    {"name": "靖江王城", "city": "桂林", "rating": 4.5, "heat_score": 7300, "location_lat": 25.2716, "location_lng": 110.2716, "category": "历史古迹", "tags": ["历史文化", "王府"], "description": "明代藩王府", "open_time": "08:00-18:00", "ticket_price": "100元", "images": ["https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800"]},
    {"name": "两江四湖", "city": "桂林", "rating": 4.6, "heat_score": 7900, "location_lat": 25.2716, "location_lng": 110.2916, "category": "风景名胜", "tags": ["夜景绝美", "水上游"], "description": "桂林的名片", "open_time": "全天", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800"]},
]

# 哈尔滨
haerbin_spots = [
    {"name": "中央大街", "city": "哈尔滨", "rating": 4.6, "heat_score": 8400, "location_lat": 45.7636, "location_lng": 126.6016, "category": "地标建筑", "tags": ["建筑艺术", "citywalk"], "description": "亚洲最长的步行街", "open_time": "全天", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1518558997970-4dadc13cbf71?w=800"]},
    {"name": "索菲亚教堂", "city": "哈尔滨", "rating": 4.7, "heat_score": 8600, "location_lat": 45.7866, "location_lng": 126.5856, "category": "历史文化", "tags": ["建筑艺术", "宗教信仰"], "description": "远东地区最大的东正教堂", "open_time": "08:30-17:00", "ticket_price": "20元", "images": ["https://images.unsplash.com/photo-1518558997970-4dadc13cbf71?w=800"]},
    {"name": "冰雪大世界", "city": "哈尔滨", "rating": 4.8, "heat_score": 9200, "location_lat": 45.8916, "location_lng": 126.5416, "category": "休闲娱乐", "tags": ["冰雪奇缘", "必玩景点"], "description": "世界最大的冰雪主题公园", "open_time": "11:00-21:30", "ticket_price": "200元", "images": ["https://images.unsplash.com/photo-1518558997970-4dadc13cbf71?w=800"]},
    {"name": "太阳岛", "city": "哈尔滨", "rating": 4.5, "heat_score": 7800, "location_lat": 45.9316, "location_lng": 126.5916, "category": "风景名胜", "tags": ["城市公园", "自然风光"], "description": "哈尔滨著名的风景区", "open_time": "08:00-17:00", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1518558997970-4dadc13cbf71?w=800"]},
    {"name": "防洪纪念塔", "city": "哈尔滨", "rating": 4.4, "heat_score": 7200, "location_lat": 45.7616, "location_lng": 126.5916, "category": "地标建筑", "tags": ["地标建筑", "历史文化"], "description": "哈尔滨的标志性建筑", "open_time": "全天", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1518558997970-4dadc13cbf71?w=800"]},
    {"name": "松花江", "city": "哈尔滨", "rating": 4.5, "heat_score": 7500, "location_lat": 45.7516, "location_lng": 126.5516, "category": "风景名胜", "tags": ["江景", "冰雪"], "description": "哈尔滨的母亲河", "open_time": "全天", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1518558997970-4dadc13cbf71?w=800"]},
    {"name": "老道外", "city": "哈尔滨", "rating": 4.4, "heat_score": 7100, "location_lat": 45.7716, "location_lng": 126.6516, "category": "地标建筑", "tags": ["市井烟火", "老建筑"], "description": "中华巴洛克建筑群", "open_time": "全天", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1518558997970-4dadc13cbf71?w=800"]},
    {"name": "伏尔加庄园", "city": "哈尔滨", "rating": 4.5, "heat_score": 7300, "location_lat": 45.9316, "location_lng": 126.6516, "category": "风景名胜", "tags": ["俄式风情", "庄园"], "description": "哈尔滨最具俄式风情的庄园", "open_time": "08:30-17:00", "ticket_price": "120元", "images": ["https://images.unsplash.com/photo-1518558997970-4dadc13cbf71?w=800"]},
    {"name": "东北虎林园", "city": "哈尔滨", "rating": 4.5, "heat_score": 7400, "location_lat": 45.8316, "location_lng": 126.3516, "category": "休闲娱乐", "tags": ["动物世界", "亲子"], "description": "世界最大的东北虎饲养基地", "open_time": "08:00-16:00", "ticket_price": "90元", "images": ["https://images.unsplash.com/photo-1518558997970-4dadc13cbf71?w=800"]},
    {"name": "龙塔", "city": "哈尔滨", "rating": 4.4, "heat_score": 7000, "location_lat": 45.7316, "location_lng": 126.5316, "category": "地标建筑", "tags": ["登高望远", "地标建筑"], "description": "亚洲第一高钢塔", "open_time": "08:30-20:00", "ticket_price": "120元", "images": ["https://images.unsplash.com/photo-1518558997970-4dadc13cbf71?w=800"]},
]

# 武汉
wuhan_spots = [
    {"name": "黄鹤楼", "city": "武汉", "rating": 4.7, "heat_score": 8800, "location_lat": 30.5716, "location_lng": 114.3016, "category": "历史古迹", "tags": ["古建绝美", "地标建筑"], "description": "江南三大名楼之一", "open_time": "08:00-18:00", "ticket_price": "70元", "images": ["https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800"]},
    {"name": "武汉大学", "city": "武汉", "rating": 4.6, "heat_score": 8100, "location_lat": 30.5416, "location_lng": 114.3616, "category": "校园风光", "tags": ["校园风光", "樱花季"], "description": "中国最美大学之一", "open_time": "全天", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800"]},
    {"name": "户部巷", "city": "武汉", "rating": 4.5, "heat_score": 7800, "location_lat": 30.5616, "location_lng": 114.2916, "category": "地标建筑", "tags": ["市井烟火", "逛吃逛喝"], "description": "武汉著名的早点一条街", "open_time": "全天", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800"]},
    {"name": "东湖", "city": "武汉", "rating": 4.6, "heat_score": 8200, "location_lat": 30.5516, "location_lng": 114.4116, "category": "风景名胜", "tags": ["城市公园", "湖光山色"], "description": "中国最大的城中湖", "open_time": "全天", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800"]},
    {"name": "江汉路步行街", "city": "武汉", "rating": 4.5, "heat_score": 7600, "location_lat": 30.5916, "location_lng": 114.2716, "category": "地标建筑", "tags": ["购物天堂", "citywalk"], "description": "武汉最繁华的商业街", "open_time": "全天", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800"]},
    {"name": "汉口江滩", "city": "武汉", "rating": 4.4, "heat_score": 7200, "location_lat": 30.6016, "location_lng": 114.2716, "category": "风景名胜", "tags": ["江景", "夜景"], "description": "武汉最浪漫的江滩", "open_time": "全天", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800"]},
    {"name": "湖北省博物馆", "city": "武汉", "rating": 4.7, "heat_score": 7800, "location_lat": 30.5416, "location_lng": 114.3516, "category": "博物展览", "tags": ["历史文化", "镇馆之宝"], "description": "湖北省最大的综合性博物馆", "open_time": "09:00-17:00", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800"]},
    {"name": "昙华林", "city": "武汉", "rating": 4.4, "heat_score": 7000, "location_lat": 30.5616, "location_lng": 114.3116, "category": "地标建筑", "tags": ["文艺小资", "老武汉"], "description": "武汉著名的历史文化街区", "open_time": "全天", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800"]},
    {"name": "古琴台", "city": "武汉", "rating": 4.4, "heat_score": 6800, "location_lat": 30.5516, "location_lng": 114.2616, "category": "历史文化", "tags": ["古建", "知音"], "description": "伯牙子期相遇之地", "open_time": "08:00-17:30", "ticket_price": "15元", "images": ["https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800"]},
    {"name": "木兰草原", "city": "武汉", "rating": 4.5, "heat_score": 7100, "location_lat": 31.0016, "location_lng": 114.3516, "category": "风景名胜", "tags": ["草原风情", "休闲度假"], "description": "华中地区唯一的草原风情景区", "open_time": "08:00-17:00", "ticket_price": "70元", "images": ["https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800"]},
]

for s in sanya_spots:
    db.add(ScenicSpot(**s))
for s in guilin_spots:
    db.add(ScenicSpot(**s))
for s in haerbin_spots:
    db.add(ScenicSpot(**s))
for s in wuhan_spots:
    db.add(ScenicSpot(**s))

db.commit()
print("Added Sanya, Guilin, Haerbin, Wuhan spots")
print("Total spots:", db.query(ScenicSpot).count())
db.close()
