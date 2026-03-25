"""
添加新的北京景点
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import SessionLocal, ScenicSpot

def add_beijing_spots():
    db = SessionLocal()
    
    # 新的北京景点数据
    # (名称, 类别, 标签, 图片路径)
    new_spots = [
        ("王府井", "地标建筑", ["购物", "繁华", "美食"], "/images/spots/beijing/beijing_wangfujin.jpg"),
        ("奥林匹克公园", "风景名胜", ["奥运", "公园", "休闲"], "/images/spots/beijing/beijing_aolinpikegongyuan.jpg"),
        ("雍和宫", "历史古迹", ["寺庙", "文化", "历史"], "/images/spots/beijing/beijing_yonghegong.jpg"),
        ("明十三陵", "历史古迹", ["陵墓", "历史", "世界遗产"], "/images/spots/beijing/beijing_mingshisanling.jpg"),
        ("798艺术区", "地标建筑", ["艺术", "文创", "拍照"], "/images/spots/beijing/beijing_798yishuqu.jpg"),
        ("三里屯", "地标建筑", ["时尚", "夜生活", "购物"], "/images/spots/beijing/beijing_sanlitun.jpg"),
        ("国贸", "地标建筑", ["商务", "地标", "现代"], "/images/spots/beijing/beijing_guomao.jpg"),
        ("前门大街", "地标建筑", ["历史", "购物", "美食"], "/images/spots/beijing/beijing_qianmendajie.jpg"),
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
