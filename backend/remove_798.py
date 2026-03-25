"""
清理798艺术区景点脚本
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import SessionLocal, ScenicSpot, TripDailySchedule

def remove_798():
    db = SessionLocal()
    try:
        # 查找798艺术区
        spot = db.query(ScenicSpot).filter(ScenicSpot.name.contains('798')).first()
        if spot:
            print(f"找到景点: {spot.name} (ID: {spot.id})")
            
            # 先删除关联的行程日程
            schedules = db.query(TripDailySchedule).filter(TripDailySchedule.spot_id == spot.id).all()
            for schedule in schedules:
                print(f"  删除关联的行程日程: {schedule.id}")
                db.delete(schedule)
            
            # 删除景点
            print(f"  删除景点: {spot.name}")
            db.delete(spot)
            db.commit()
            print("清理完成！")
        else:
            print("未找到798艺术区景点")
        
    except Exception as e:
        print(f"清理失败: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    remove_798()
