"""
迁移脚本：为 travel_diaries 表添加 budget 和 companion 字段
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
        # 检查当前表中的所有列
        cursor.execute("PRAGMA table_info(travel_diaries)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # 添加 budget 字段
        if 'budget' not in columns:
            cursor.execute("""
                ALTER TABLE travel_diaries 
                ADD COLUMN budget VARCHAR(50)
            """)
            print("[OK] 成功添加 budget 字段到 travel_diaries 表")
        else:
            print("[OK] budget 字段已存在，跳过")
        
        # 添加 companion 字段
        if 'companion' not in columns:
            cursor.execute("""
                ALTER TABLE travel_diaries 
                ADD COLUMN companion VARCHAR(50)
            """)
            print("[OK] 成功添加 companion 字段到 travel_diaries 表")
        else:
            print("[OK] companion 字段已存在，跳过")
        
        conn.commit()
        print("[OK] 迁移完成！")
        
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] 迁移失败: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
