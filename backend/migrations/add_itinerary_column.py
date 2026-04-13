"""
迁移脚本：为 travel_diaries 表添加 itinerary 字段
"""
import sqlite3
import os

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "travel.db")

def migrate():
    """执行迁移"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 检查 itinerary 字段是否已存在
        cursor.execute("PRAGMA table_info(travel_diaries)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'itinerary' in columns:
            print("[OK] itinerary 字段已存在，跳过迁移")
            return
        
        # 添加 itinerary 字段 (JSON 类型在 SQLite 中存储为 TEXT)
        cursor.execute("""
            ALTER TABLE travel_diaries 
            ADD COLUMN itinerary TEXT
        """)
        
        conn.commit()
        print("[OK] 成功添加 itinerary 字段到 travel_diaries 表")
        
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] 迁移失败: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
