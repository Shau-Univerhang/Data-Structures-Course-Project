# -*- coding: utf-8 -*-
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import SessionLocal, Trip

def delete_all_trips():
    db = SessionLocal()
    
    try:
        # 获取所有行程
        all_trips = db.query(Trip).all()
        count = len(all_trips)
        
        print("数据库中共有 %d 个行程" % count)
        
        # 删除所有行程
        for trip in all_trips:
            db.delete(trip)
        
        db.commit()
        print("已清空所有行程！")
        
        # 验证
        remaining = db.query(Trip).count()
        print("数据库中现在有 %d 个行程" % remaining)
        
    except Exception as e:
        print("清空失败: %s" % str(e))
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    delete_all_trips()
