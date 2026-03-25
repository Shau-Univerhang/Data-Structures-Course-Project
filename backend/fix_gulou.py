"""
修复北京鼓楼名称
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import SessionLocal, ScenicSpot

def fix_gulou():
    db = SessionLocal()
    try:
        # 查找北京的鼓楼
        spot = db.query(ScenicSpot).filter(
            ScenicSpot.name == '鼓楼',
            ScenicSpot.city == '北京'
        ).first()
        
        if spot:
            print(f"找到景点: {spot.name} (ID: {spot.id})")
            spot.name = '北京鼓楼'
            db.commit()
            print("已重命名为: 北京鼓楼")
        else:
            print("未找到北京的鼓楼景点")
        
    except Exception as e:
        print(f"修改失败: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_gulou()
