# -*- coding: utf-8 -*-
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import SessionLocal, Trip, TripDailySchedule

def debug_trips():
    db = SessionLocal()
    
    try:
        # 获取所有行程
        trips = db.query(Trip).all()
        print("=" * 60)
        print("数据库中的行程:")
        print("=" * 60)
        
        for trip in trips:
            print("\n行程 ID: %d" % trip.id)
            print("  标题: %s" % trip.title)
            print("  目的地: %s" % trip.destination)
            print("  天数: %d" % trip.total_days)
            print("  创建时间: %s" % trip.created_at)
            print("  状态: %s" % trip.status)
            
            # 获取景点数量
            spot_count = db.query(TripDailySchedule).filter(
                TripDailySchedule.trip_id == trip.id
            ).count()
            print("  景点数量: %d" % spot_count)
            
            # 获取景点详情
            schedules = db.query(TripDailySchedule).filter(
                TripDailySchedule.trip_id == trip.id
            ).all()
            
            if schedules:
                print("  景点列表:")
                for s in schedules:
                    print("    - 第%d天: spot_id=%d" % (s.day_number, s.spot_id))
            else:
                print("  景点列表: 无")
        
        print("\n" + "=" * 60)
        print("总计: %d 个行程" % len(trips))
        print("=" * 60)
        
    except Exception as e:
        print("查询失败: %s" % str(e))
    finally:
        db.close()

if __name__ == "__main__":
    debug_trips()
