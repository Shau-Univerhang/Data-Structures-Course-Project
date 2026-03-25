"""
清理数据库中的假景点脚本
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import SessionLocal, ScenicSpot, TripDailySchedule

def remove_fake_spots():
    db = SessionLocal()
    try:
        # 要删除的假景点名称列表
        fake_spots = ['王府井', '王府井步行街', '王府井小吃街', '王府井大街', '后海', '后海酒吧街']
        
        for spot_name in fake_spots:
            # 查找该景点
            spots = db.query(ScenicSpot).filter(ScenicSpot.name.contains(spot_name)).all()
            for spot in spots:
                print(f"找到假景点: {spot.name} (ID: {spot.id})")
                
                # 先删除关联的行程日程
                schedules = db.query(TripDailySchedule).filter(TripDailySchedule.spot_id == spot.id).all()
                for schedule in schedules:
                    print(f"  删除关联的行程日程: {schedule.id}")
                    db.delete(schedule)
                
                # 删除景点
                print(f"  删除景点: {spot.name}")
                db.delete(spot)
        
        db.commit()
        print("\n清理完成！")
        
    except Exception as e:
        print(f"清理失败: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    remove_fake_spots()
