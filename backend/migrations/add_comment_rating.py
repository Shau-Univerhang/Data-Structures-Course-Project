"""
迁移脚本：为 diary_comments 表添加 rating 字段
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
        # 检查 rating 字段是否已存在
        cursor.execute("PRAGMA table_info(diary_comments)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'rating' in columns:
            print("[OK] rating 字段已存在，跳过迁移")
            return
        
        # 添加 rating 字段
        cursor.execute("""
            ALTER TABLE diary_comments 
            ADD COLUMN rating INTEGER
        """)
        
        conn.commit()
        print("[OK] 成功添加 rating 字段到 diary_comments 表")
        
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] 迁移失败: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
