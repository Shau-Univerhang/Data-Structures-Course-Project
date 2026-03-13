"""
添加更多景点数据
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import SessionLocal, ScenicSpot

db = SessionLocal()
current = db.query(ScenicSpot).count()
print(f"Current spots: {current}")
