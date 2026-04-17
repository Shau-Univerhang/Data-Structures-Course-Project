"""
迁移说明：
- 创建日记城市标签功能所需的数据表
- 完全独立，不影响现有数据
- 可安全回滚

创建时间：2024-01-XX
"""

from sqlalchemy import create_engine, text
import os
import sys

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.database import DB_PATH

def get_engine():
    """获取数据库引擎"""
    return create_engine(f'sqlite:///{DB_PATH}', echo=False)

def upgrade():
    """执行迁移：创建新表"""
    engine = get_engine()
    
    with engine.connect() as conn:
        # 检查表是否已存在
        result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='diary_cities'"))
        if result.fetchone():
            print("[OK] diary_cities 表已存在，跳过")
        else:
            # 创建 diary_cities 表
            print("[INFO] 创建 diary_cities 表...")
            conn.execute(text("""
                CREATE TABLE diary_cities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(50) NOT NULL UNIQUE,
                    diary_count INTEGER DEFAULT 0,
                    created_at VARCHAR DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.commit()
            print("[OK] diary_cities 表创建成功")
        
        result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='diary_city_tags'"))
        if result.fetchone():
            print("[OK] diary_city_tags 表已存在，跳过")
        else:
            # 创建 diary_city_tags 表
            print("[INFO] 创建 diary_city_tags 表...")
            conn.execute(text("""
                CREATE TABLE diary_city_tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    diary_id INTEGER NOT NULL,
                    city_id INTEGER NOT NULL,
                    confidence FLOAT DEFAULT 1.0,
                    created_at VARCHAR DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(diary_id, city_id),
                    FOREIGN KEY(diary_id) REFERENCES travel_diaries(id) ON DELETE CASCADE,
                    FOREIGN KEY(city_id) REFERENCES diary_cities(id) ON DELETE CASCADE
                )
            """))
            conn.commit()
            print("[OK] diary_city_tags 表创建成功")
    
    print("[OK] 迁移完成！")


def downgrade():
    """回滚迁移：删除表"""
    engine = get_engine()
    
    with engine.connect() as conn:
        # 检查表是否存在
        result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='diary_city_tags'"))
        if result.fetchone():
            print("[INFO] 删除 diary_city_tags 表...")
            conn.execute(text("DROP TABLE diary_city_tags"))
            conn.commit()
            print("[OK] diary_city_tags 表已删除")
        
        result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='diary_cities'"))
        if result.fetchone():
            print("[INFO] 删除 diary_cities 表...")
            conn.execute(text("DROP TABLE diary_cities"))
            conn.commit()
            print("[OK] diary_cities 表已删除")
    
    print("[OK] 回滚完成！")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--rollback', action='store_true', help='回滚迁移')
    args = parser.parse_args()
    
    if args.rollback:
        print("[WARN] 正在回滚...")
        downgrade()
    else:
        print("[INFO] 正在执行迁移...")
        upgrade()
