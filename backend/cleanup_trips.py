# -*- coding: utf-8 -*-
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import SessionLocal, Trip

def cleanup_trips():
    db = SessionLocal()
    
    try:
        # 获取所有行程
        all_trips = db.query(Trip).all()
        print("数据库中共有 %d 个行程" % len(all_trips))
        
        # 保留最新的2个行程
        trips_to_keep = db.query(Trip).order_by(Trip.created_at.desc()).limit(2).all()
        keep_ids = [t.id for t in trips_to_keep]
        
        print("将保留最新的2个行程，ID: %s" % str(keep_ids))
        
        # 删除其他行程
        trips_to_delete = db.query(Trip).filter(~Trip.id.in_(keep_ids)).all()
        print("将删除 %d 个行程" % len(trips_to_delete))
        
        for trip in trips_to_delete:
            print("  删除 ID: %d" % trip.id)
            db.delete(trip)
        
        db.commit()
        print("清理完成！保留了 %d 个行程，删除了 %d 个行程" % (len(keep_ids), len(trips_to_delete)))
        
        # 显示剩余行程
        remaining = db.query(Trip).all()
        print("数据库中现在有 %d 个行程" % len(remaining))
        for trip in remaining:
            print("  - ID: %d" % trip.id)
        
    except Exception as e:
        print("清理失败: %s" % str(e))
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    cleanup_trips()
