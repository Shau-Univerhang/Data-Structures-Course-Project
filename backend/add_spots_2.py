"""
添加更多城市景点数据
"""
import sys
sys.path.insert(0, 'D:/travel/邮游世界/backend')
from models.database import SessionLocal, ScenicSpot

db = SessionLocal()

# 苏州
suzhou_spots = [
    {"name": "拙政园", "city": "苏州", "rating": 4.9, "heat_score": 8900, "location_lat": 31.3236, "location_lng": 120.5853, "category": "风景名胜", "tags": ["江南园林", "世界遗产"], "description": "中国古典园林的代表作", "open_time": "07:30-17:30", "ticket_price": "70元", "images": ["https://images.unsplash.com/photo-1548919973-5cef591cdbc9?w=800"]},
    {"name": "周庄", "city": "苏州", "rating": 4.7, "heat_score": 8200, "location_lat": 31.1166, "location_lng": 120.8466, "category": "风景名胜", "tags": ["水乡古镇", "休闲度假"], "description": "中国第一水乡", "open_time": "08:00-17:00", "ticket_price": "100元", "images": ["https://images.unsplash.com/photo-1548919973-5cef591cdbc9?w=800"]},
    {"name": "狮子林", "city": "苏州", "rating": 4.8, "heat_score": 7800, "location_lat": 31.3276, "location_lng": 120.5833, "category": "风景名胜", "tags": ["江南园林", "假山奇石"], "description": "元代园林的代表", "open_time": "07:30-17:30", "ticket_price": "40元", "images": ["https://images.unsplash.com/photo-1548919973-5cef591cdbc9?w=800"]},
    {"name": "平江路", "city": "苏州", "rating": 4.6, "heat_score": 8100, "location_lat": 31.3316, "location_lng": 120.6516, "category": "地标建筑", "tags": ["老街", "水乡风貌"], "description": "苏州古城保存最完整的历史街区", "open_time": "全天", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1548919973-5cef591cdbc9?w=800"]},
    {"name": "山塘街", "city": "苏州", "rating": 4.6, "heat_score": 8100, "location_lat": 31.3066, "location_lng": 120.5856, "category": "地标建筑", "tags": ["水乡古镇", "市井烟火"], "description": "被誉为姑苏第一名街", "open_time": "全天", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1548919973-5cef591cdbc9?w=800"]},
    {"name": "虎丘", "city": "苏州", "rating": 4.7, "heat_score": 8000, "location_lat": 31.3366, "location_lng": 120.5916, "category": "风景名胜", "tags": ["历史古迹", "园林"], "description": "吴中第一名胜", "open_time": "07:30-18:00", "ticket_price": "70元", "images": ["https://images.unsplash.com/photo-1548919973-5cef591cdbc9?w=800"]},
    {"name": "同里古镇", "city": "苏州", "rating": 4.6, "heat_score": 7800, "location_lat": 31.0566, "location_lng": 120.7166, "category": "风景名胜", "tags": ["水乡古镇", "世界遗产"], "description": "江南六大古镇之一", "open_time": "08:00-17:30", "ticket_price": "100元", "images": ["https://images.unsplash.com/photo-1548919973-5cef591cdbc9?w=800"]},
    {"name": "网师园", "city": "苏州", "rating": 4.7, "heat_score": 7500, "location_lat": 31.3216, "location_lng": 120.6416, "category": "风景名胜", "tags": ["江南园林", "世界遗产"], "description": "苏州园林的经典代表", "open_time": "07:30-17:30", "ticket_price": "40元", "images": ["https://images.unsplash.com/photo-1548919973-5cef591cdbc9?w=800"]},
    {"name": "苏州博物馆", "city": "苏州", "rating": 4.8, "heat_score": 8200, "location_lat": 31.3216, "location_lng": 120.5816, "category": "博物展览", "tags": ["建筑艺术", "历史文化"], "description": "贝聿铭设计的世界级博物馆", "open_time": "09:00-17:00", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1548919973-5cef591cdbc9?w=800"]},
    {"name": "寒山寺", "city": "苏州", "rating": 4.6, "heat_score": 7700, "location_lat": 31.2766, "location_lng": 120.5816, "category": "历史文化", "tags": ["佛教文化", "古建"], "description": "月落乌啼霜满天，江枫渔火对愁眠", "open_time": "07:00-18:00", "ticket_price": "20元", "images": ["https://images.unsplash.com/photo-1548919973-5cef591cdbc9?w=800"]},
]

# 厦门
xiamen_spots = [
    {"name": "鼓浪屿", "city": "厦门", "rating": 4.8, "heat_score": 9300, "location_lat": 24.4408, "location_lng": 118.1068, "category": "风景名胜", "tags": ["世界遗产", "浪漫爱情"], "description": "海上花园，世界文化遗产", "open_time": "全天", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1518459021-c8f5211a7edc?w=800"]},
    {"name": "厦门大学", "city": "厦门", "rating": 4.7, "heat_score": 8500, "location_lat": 24.4355, "location_lng": 118.1038, "category": "校园风光", "tags": ["校园风光", "拍照出片"], "description": "中国最美大学之一", "open_time": "全天", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1518459021-c8f5211a7edc?w=800"]},
    {"name": "南普陀寺", "city": "厦门", "rating": 4.6, "heat_score": 8000, "location_lat": 24.4435, "location_lng": 118.1055, "category": "历史文化", "tags": ["佛教文化", "宗教信仰"], "description": "闽南佛教胜地", "open_time": "06:00-18:00", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1518459021-c8f5211a7edc?w=800"]},
    {"name": "曾厝垵", "city": "厦门", "rating": 4.5, "heat_score": 7800, "location_lat": 24.4316, "location_lng": 118.1016, "category": "地标建筑", "tags": ["文艺小资", "逛吃逛喝"], "description": "中国最文艺的渔村", "open_time": "全天", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1518459021-c8f5211a7edc?w=800"]},
    {"name": "环岛路", "city": "厦门", "rating": 4.6, "heat_score": 8200, "location_lat": 24.4316, "location_lng": 118.1516, "category": "地标建筑", "tags": ["海景风光", "citywalk"], "description": "厦门最美的海滨公路", "open_time": "全天", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1518459021-c8f5211a7edc?w=800"]},
    {"name": "日光岩", "city": "厦门", "rating": 4.5, "heat_score": 7600, "location_lat": 24.4416, "location_lng": 118.1066, "category": "风景名胜", "tags": ["登高望远", "鼓浪屿"], "description": "鼓浪屿最高峰", "open_time": "06:00-18:30", "ticket_price": "50元", "images": ["https://images.unsplash.com/photo-1518459021-c8f5211a7edc?w=800"]},
    {"name": "菽庄花园", "city": "厦门", "rating": 4.5, "heat_score": 7400, "location_lat": 24.4416, "location_lng": 118.1066, "category": "风景名胜", "tags": ["江南园林", "海滨"], "description": "钢琴博物馆所在地", "open_time": "06:00-18:30", "ticket_price": "30元", "images": ["https://images.unsplash.com/photo-1518459021-c8f5211a7edc?w=800"]},
    {"name": "厦门白城沙滩", "city": "厦门", "rating": 4.4, "heat_score": 7200, "location_lat": 24.4316, "location_lng": 118.1216, "category": "风景名胜", "tags": ["海滨度假", "休闲娱乐"], "description": "厦门最热闹的海滨浴场", "open_time": "全天", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1518459021-c8f5211a7edc?w=800"]},
    {"name": "中山路步行街", "city": "厦门", "rating": 4.5, "heat_score": 7800, "location_lat": 24.4616, "location_lng": 118.0616, "category": "地标建筑", "tags": ["购物天堂", "老厦门"], "description": "厦门最繁华的商业街", "open_time": "全天", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1518459021-c8f5211a7edc?w=800"]},
    {"name": "集美学村", "city": "厦门", "rating": 4.5, "heat_score": 7500, "location_lat": 24.5616, "location_lng": 118.1016, "category": "校园风光", "tags": ["校园风光", "嘉庚建筑"], "description": "陈嘉庚创办的学村", "open_time": "全天", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1518459021-c8f5211a7edc?w=800"]},
]

# 丽江
lijiang_spots = [
    {"name": "丽江古城", "city": "丽江", "rating": 4.8, "heat_score": 9200, "location_lat": 26.8721, "location_lng": 100.2299, "category": "风景名胜", "tags": ["世界遗产", "古镇风貌"], "description": "世界文化遗产", "open_time": "全天", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1527838832700-5059252407fa?w=800"]},
    {"name": "玉龙雪山", "city": "丽江", "rating": 4.9, "heat_score": 9400, "location_lat": 27.089, "location_lng": 100.1743, "category": "风景名胜", "tags": ["自然风光", "必玩景点"], "description": "北半球最南的大雪山", "open_time": "06:00-18:00", "ticket_price": "130元", "images": ["https://images.unsplash.com/photo-1527838832700-5059252407fa?w=800"]},
    {"name": "泸沽湖", "city": "丽江", "rating": 4.8, "heat_score": 8900, "location_lat": 27.6916, "location_lng": 100.7516, "category": "风景名胜", "tags": ["自然风光", "高原湖泊"], "description": "川滇两省共辖的高原湖泊", "open_time": "全天", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1527838832700-5059252407fa?w=800"]},
    {"name": "束河古镇", "city": "丽江", "rating": 4.6, "heat_score": 8000, "location_lat": 26.9366, "location_lng": 100.2516, "category": "风景名胜", "tags": ["古镇风貌", "纳西文化"], "description": "丽江古城的重要组成部分", "open_time": "全天", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1527838832700-5059252407fa?w=800"]},
    {"name": "蓝月谷", "city": "丽江", "rating": 4.7, "heat_score": 8600, "location_lat": 27.089, "location_lng": 100.3043, "category": "风景名胜", "tags": ["自然风光", "高原湖泊"], "description": "玉龙雪山脚下的蓝宝石", "open_time": "全天", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1527838832700-5059252407fa?w=800"]},
    {"name": "四方街", "city": "丽江", "rating": 4.5, "heat_score": 7800, "location_lat": 26.8716, "location_lng": 100.2316, "category": "地标建筑", "tags": ["市井烟火", "酒吧街"], "description": "丽江古城的中心", "open_time": "全天", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1527838832700-5059252407fa?w=800"]},
    {"name": "木府", "city": "丽江", "rating": 4.6, "heat_score": 8200, "location_lat": 26.8766, "location_lng": 100.2616, "category": "历史文化", "tags": ["纳西文化", "古建"], "description": "丽江土司的府邸", "open_time": "08:30-18:00", "ticket_price": "60元", "images": ["https://images.unsplash.com/photo-1527838832700-5059252407fa?w=800"]},
    {"name": "拉市海", "city": "丽江", "rating": 4.5, "heat_score": 7500, "location_lat": 26.8916, "location_lng": 100.1516, "category": "风景名胜", "tags": ["自然风光", "湿地"], "description": "丽江最大的高原湖泊", "open_time": "08:00-17:00", "ticket_price": "30元", "images": ["https://images.unsplash.com/photo-1527838832700-5059252407fa?w=800"]},
    {"name": "黑龙潭", "city": "丽江", "rating": 4.5, "heat_score": 7200, "location_lat": 26.8816, "location_lng": 100.2516, "category": "风景名胜", "tags": ["园林", "玉龙雪山"], "description": "可拍摄玉龙雪山倒影", "open_time": "07:00-19:00", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1527838832700-5059252407fa?w=800"]},
    {"name": "玉水寨", "city": "丽江", "rating": 4.4, "heat_score": 6800, "location_lat": 26.9516, "location_lng": 100.2016, "category": "风景名胜", "tags": ["纳西文化", "自然风光"], "description": "纳西族东巴文化的传承地", "open_time": "08:00-17:00", "ticket_price": "35元", "images": ["https://images.unsplash.com/photo-1527838832700-5059252407fa?w=800"]},
]

for s in suzhou_spots:
    db.add(ScenicSpot(**s))
for s in xiamen_spots:
    db.add(ScenicSpot(**s))
for s in lijiang_spots:
    db.add(ScenicSpot(**s))

db.commit()
print("Added Suzhou, Xiamen, Lijiang spots")
print("Total spots:", db.query(ScenicSpot).count())
db.close()
