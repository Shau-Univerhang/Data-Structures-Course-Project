"""
添加新的北京景点（第二批）
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import SessionLocal, ScenicSpot

def add_beijing_spots():
    db = SessionLocal()
    
    # 新的北京景点数据（第二批）
    # (名称, 类别, 标签, 图片路径)
    new_spots = [
        ("环球影城", "休闲娱乐", ["亲子", "娱乐", "必玩"], "/images/spots/beijing/beijing_huanqiuyingcheng.jpg"),
        ("军事博物馆", "博物展览", ["博物馆", "历史", "军事"], "/images/spots/beijing/beijing_junshibowuguan.jpg"),
        ("国家博物馆", "博物展览", ["博物馆", "历史", "文化"], "/images/spots/beijing/beijing_guojiabowuguan.jpg"),
        ("人民大会堂", "地标建筑", ["地标", "建筑", "庄严"], "/images/spots/beijing/beijing_renmindahuitang.jpg"),
        ("地坛公园", "风景名胜", ["公园", "休闲", "历史"], "/images/spots/beijing/beijing_ditangongyuan.jpg"),
        ("鼓楼", "历史古迹", ["地标", "历史", "建筑"], "/images/spots/beijing/beijing_gulou.jpg"),
        ("北京动物园", "休闲娱乐", ["亲子", "动物", "休闲"], "/images/spots/beijing/beijing_beijingdongwuyuan.jpg"),
    ]
    
    # 北京基准坐标
    base_lat, base_lng = 39.9, 116.4
    
    spots_added = 0
    
    try:
        for i, (name, category, tags, image) in enumerate(new_spots):
            # 检查是否已存在
            existing = db.query(ScenicSpot).filter(
                ScenicSpot.name == name,
                ScenicSpot.city == "北京"
            ).first()
            
            if existing:
                print(f"景点已存在: {name}")
                continue
            
            # 生成略微不同的坐标
            lat = base_lat + (i % 5 - 2) * 0.02
            lng = base_lng + (i % 5 - 2) * 0.02
            
            spot_data = {
                "name": name,
                "city": "北京",
                "category": category,
                "rating": 0,
                "heat_score": 0,
                "location_lat": lat,
                "location_lng": lng,
                "address": f"北京市",
                "description": f"{name}是北京的著名景点",
                "tags": tags,
                "open_time": "08:00-18:00",
                "ticket_price": "¥50",
                "images": [image]
            }
            
            spot = ScenicSpot(**spot_data)
            db.add(spot)
            spots_added += 1
            print(f"添加景点: {name}")
        
        db.commit()
        print(f"\n成功添加 {spots_added} 个景点！")
        
    except Exception as e:
        print(f"添加失败: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_beijing_spots()
