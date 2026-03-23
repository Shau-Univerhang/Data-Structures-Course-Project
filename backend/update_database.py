"""
更新数据库表结构
添加 favorites_count 字段和 spot_reviews 表
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import Base, engine
from sqlalchemy import text

def update_database():
    """更新数据库表结构"""
    
    with engine.connect() as conn:
        # 检查并添加 favorites_count 字段
        try:
            conn.execute(text("ALTER TABLE scenic_spots ADD COLUMN favorites_count INTEGER DEFAULT 0"))
            conn.commit()
            print("[OK] Added favorites_count column to scenic_spots")
        except Exception as e:
            if 'duplicate column name' in str(e).lower():
                print("[SKIP] favorites_count column already exists")
            else:
                print(f"[WARN] Could not add favorites_count: {e}")
        
        # 创建 spot_reviews 表
        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS spot_reviews (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    spot_id INTEGER NOT NULL,
                    user_id INTEGER,
                    rating REAL NOT NULL,
                    content TEXT,
                    images TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (spot_id) REFERENCES scenic_spots(id) ON DELETE CASCADE,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """))
            conn.commit()
            print("[OK] Created spot_reviews table")
        except Exception as e:
            if 'already exists' in str(e).lower():
                print("[SKIP] spot_reviews table already exists")
            else:
                print(f"[WARN] Could not create spot_reviews: {e}")
        
        # 将现有景点的 rating 和 favorites_count 初始化为 0
        try:
            conn.execute(text("UPDATE scenic_spots SET rating = 0, favorites_count = 0"))
            conn.commit()
            print("[OK] Initialized rating and favorites_count to 0")
        except Exception as e:
            print(f"[WARN] Could not initialize values: {e}")
        
        # 删除 review_count（如果有）
        try:
            conn.execute(text("ALTER TABLE scenic_spots DROP COLUMN review_count"))
            conn.commit()
            print("[OK] Dropped review_count column (using spot_reviews table instead)")
        except Exception as e:
            if 'no such column' in str(e).lower():
                print("[SKIP] review_count column does not exist")
            else:
                print(f"[WARN] Could not drop review_count: {e}")
    
    print("\nDatabase update completed!")

if __name__ == "__main__":
    update_database()
