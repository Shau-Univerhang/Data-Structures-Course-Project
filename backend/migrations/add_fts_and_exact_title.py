"""
数据库迁移：为 travel_diaries 表添加全文检索和精确查询字段
- normalized_title: 标准化标题
- title_hash: 标题SHA256哈希
- content_plain: 纯文本内容（用于FTS检索）
同时初始化 FTS5 虚拟表并回填现有数据
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3
from models.database import DB_PATH
from utils.diary_fts import (
    init_fts5_table, normalize_title, compute_title_hash,
    extract_plain_text, insert_diary_to_fts
)


def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. 添加新字段（如果不存在）
    columns_to_add = [
        ("normalized_title", "TEXT"),
        ("title_hash", "TEXT"),
        ("content_plain", "TEXT"),
    ]

    for col_name, col_type in columns_to_add:
        try:
            cursor.execute(f"ALTER TABLE travel_diaries ADD COLUMN {col_name} {col_type}")
            print(f"[迁移] 添加字段 {col_name} 成功")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print(f"[迁移] 字段 {col_name} 已存在，跳过")
            else:
                print(f"[迁移] 添加字段 {col_name} 失败: {e}")
    
    conn.commit()

    # 2. 初始化 FTS5 虚拟表
    init_fts5_table()

    # 3. 回填现有数据
    cursor.execute("""
        SELECT id, title, content, itinerary 
        FROM travel_diaries 
        WHERE title IS NOT NULL
    """)
    rows = cursor.fetchall()
    
    updated_count = 0
    for row in rows:
        diary_id, title, content, itinerary = row
        
        # 解析 itinerary（如果是字符串）
        import json
        try:
            itin_data = json.loads(itinerary) if isinstance(itinerary, str) else itinerary
        except:
            itin_data = None
        
        # 计算标准化标题和哈希
        normalized = normalize_title(title)
        title_hash = compute_title_hash(title)
        
        # 提取纯文本
        content_plain = extract_plain_text(content)
        
        # 更新字段
        cursor.execute("""
            UPDATE travel_diaries 
            SET normalized_title = ?, title_hash = ?, content_plain = ?
            WHERE id = ?
        """, (normalized, title_hash, content_plain, diary_id))
        
        # 插入 FTS 索引（使用同一个连接）
        try:
            cursor.execute("DELETE FROM travel_diaries_fts WHERE rowid = ?", (diary_id,))
            cursor.execute(
                """
                INSERT INTO travel_diaries_fts(rowid, title, content_plain, city_text, tag_text)
                VALUES (?, ?, ?, '', '')
                """,
                (diary_id, title or "", content_plain or "")
            )
        except Exception as e:
            print(f"[FTS5] 插入索引失败 (diary_id={diary_id}): {e}")
        
        updated_count += 1
    
    conn.commit()
    conn.close()
    
    print(f"[迁移] 完成！共更新 {updated_count} 条日记数据")
    print(f"[迁移] FTS5 虚拟表已初始化")


if __name__ == "__main__":
    print("=" * 60)
    print("数据库迁移：全文检索和精确查询字段")
    print("=" * 60)
    migrate()
