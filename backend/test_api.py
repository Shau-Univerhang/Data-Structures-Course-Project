# -*- coding: utf-8 -*-
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import SessionLocal, Trip
import json

def test_api():
    db = SessionLocal()
    
    try:
        # 模拟 API 返回的数据
        trips = db.query(Trip).filter(Trip.user_id == 1).order_by(Trip.created_at.desc()).all()
        
        result = []
        for trip in trips:
            # 获取景点数量
            from models.database import TripDailySchedule
            spot_count = db.query(TripDailySchedule).filter(
                TripDailySchedule.trip_id == trip.id
            ).count()
            
            # 检查 created_at 的类型
            created_at_value = trip.created_at
            print("created_at type: %s, value: %s" % (type(created_at_value), created_at_value))
            
            trip_data = {
                'id': trip.id,
                'title': trip.title,
                'destination': trip.destination,
                'total_days': trip.total_days,
                'status': trip.status,
                'created_at': str(created_at_value) if created_at_value else None,
                'preferences': trip.travel_preferences or [],
                'spot_count': spot_count
            }
            result.append(trip_data)
        
        print("\nAPI 返回的数据:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print("查询失败: %s" % str(e))
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_api()
