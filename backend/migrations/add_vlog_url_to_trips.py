"""
迁移脚本：为 trips 表添加 vlog_url 字段
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
        cursor.execute("PRAGMA table_info(trips)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # 添加 vlog_url 字段
        if 'vlog_url' not in columns:
            cursor.execute("""
                ALTER TABLE trips 
                ADD COLUMN vlog_url VARCHAR(255)
            """)
            print("[OK] 成功添加 vlog_url 字段到 trips 表")
        else:
            print("[OK] vlog_url 字段已存在，跳过")
        
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
