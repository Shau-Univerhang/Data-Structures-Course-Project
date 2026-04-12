# -*- coding: utf-8 -*-
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import SessionLocal, Trip, TripDailySchedule

def check_api():
    db = SessionLocal()
    
    try:
        # 模拟 API 返回的数据
        trips = db.query(Trip).filter(Trip.user_id == 1).order_by(Trip.created_at.desc()).all()
        
        print("=" * 60)
        print("API 应该返回的数据:")
        print("=" * 60)
        
        for trip in trips:
            # 获取景点数量
            spot_count = db.query(TripDailySchedule).filter(
                TripDailySchedule.trip_id == trip.id
            ).count()
            
            print("\n行程 ID: %d" % trip.id)
            print("  title: %s" % trip.title)
            print("  destination: %s" % trip.destination)
            print("  total_days: %d" % trip.total_days)
            print("  status: %s" % trip.status)
            print("  created_at: %s (type: %s)" % (trip.created_at, type(trip.created_at).__name__))
            print("  spot_count: %d" % spot_count)
        
        print("\n" + "=" * 60)
        
    except Exception as e:
        print("查询失败: %s" % str(e))
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_api()
