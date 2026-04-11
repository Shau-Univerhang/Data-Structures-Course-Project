"""
添加日记评论表迁移脚本
"""
import sqlite3
import os

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "travel.db")

def migrate():
    """执行迁移"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 检查表是否已存在
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='diary_comments'")
    if cursor.fetchone():
        print("diary_comments 表已存在，跳过迁移")
        conn.close()
        return
    
    # 创建日记评论表
    cursor.execute('''
        CREATE TABLE diary_comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            diary_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            parent_id INTEGER,
            content TEXT NOT NULL,
            like_count INTEGER DEFAULT 0,
            is_deleted BOOLEAN DEFAULT 0,
            created_at VARCHAR,
            updated_at VARCHAR,
            FOREIGN KEY (diary_id) REFERENCES travel_diaries(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (parent_id) REFERENCES diary_comments(id)
        )
    ''')
    
    # 创建索引
    cursor.execute('CREATE INDEX idx_diary_comments_diary_id ON diary_comments(diary_id)')
    cursor.execute('CREATE INDEX idx_diary_comments_user_id ON diary_comments(user_id)')
    cursor.execute('CREATE INDEX idx_diary_comments_parent_id ON diary_comments(parent_id)')
    
    conn.commit()
    conn.close()
    print("✅ diary_comments 表创建成功！")

if __name__ == "__main__":
    migrate()
