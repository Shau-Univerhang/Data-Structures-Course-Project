"""
为每个城市景点更新对应城市的图片
"""
import sys
sys.path.insert(0, 'D:/travel/邮游世界/backend')
from models.database import SessionLocal, ScenicSpot

db = SessionLocal()

# 城市对应图片 - 使用各城市著名景点图片
city_images = {
    '北京': 'https://images.unsplash.com/photo-1599571234909-29ed5d1321d6?w=800',
    '上海': 'https://images.unsplash.com/photo-1474181487882-5abf3f0ba6c2?w=800', 
    '西安': 'https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800',
    '成都': 'https://images.unsplash.com/photo-1528109966604-5a6a4a964e8d?w=800',
    '杭州': 'https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800',
    '青岛': 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800',
    '重庆': 'https://images.unsplash.com/photo-1560969184-10fe8719e047?w=800',
    '广州': 'https://images.unsplash.com/photo-1534054524995-69c5d4f8a5b5?w=800',
    '深圳': 'https://images.unsplash.com/photo-1530976161117-d1a36af4c1c8?w=800',
    '南京': 'https://images.unsplash.com/photo-1530521954074-e64f6810b32d?w=800',
    '苏州': 'https://images.unsplash.com/photo-1548919973-5cef591cdbc9?w=800',
    '厦门': 'https://images.unsplash.com/photo-1518459021-c8f5211a7edc?w=800',
    '丽江': 'https://images.unsplash.com/photo-1527838832700-5059252407fa?w=800',
    '三亚': 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800',
    '桂林': 'https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800',
    '哈尔滨': 'https://images.unsplash.com/photo-1518558997970-4dadc13cbf71?w=800',
    '武汉': 'https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800',
    '长沙': 'https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800',
    '郑州': 'https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800',
    '济南': 'https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800',
}

# 为每个城市景点设置对应图片
for city, img in city_images.items():
    spots = db.query(ScenicSpot).filter(ScenicSpot.city == city).all()
    for i, spot in enumerate(spots):
        # 每个景点用同一城市的图片
        spot.images = [img]
    
print(f"Updated spots for {len(city_images)} cities")

db.commit()
db.close()
print("Done!")
