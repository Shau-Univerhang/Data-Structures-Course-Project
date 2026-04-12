# -*- coding: utf-8 -*-
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import SessionLocal, Trip

def check_trips():
    db = SessionLocal()
    
    try:
        # 获取所有行程
        all_trips = db.query(Trip).all()
        print("数据库中共有 %d 个行程" % len(all_trips))
        
        for trip in all_trips:
            print("  - ID: %d, 标题: %s, 目的地: %s, 创建时间: %s" % (trip.id, trip.title, trip.destination, trip.created_at))
        
    except Exception as e:
        print("查询失败: %s" % str(e))
    finally:
        db.close()

if __name__ == "__main__":
    check_trips()
