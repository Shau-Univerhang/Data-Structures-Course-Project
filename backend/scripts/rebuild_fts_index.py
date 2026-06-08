"""
重建 FTS5 索引：从压缩内容中解压并回填
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3
import json
import gzip
from models.database import DB_PATH
from algorithms.core import decompress_diary
from utils.diary_fts import extract_plain_text

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Get all diaries with their content (compressed or not)
cursor.execute("SELECT id, title, content, content_compressed, itinerary FROM travel_diaries WHERE title IS NOT NULL")
rows = cursor.fetchall()

print(f"共有 {len(rows)} 条日记需要重建索引")

# Clear existing FTS index
cursor.execute("DELETE FROM travel_diaries_fts")

for row in rows:
    diary_id, title, content, content_compressed, itinerary = row
    
    # Extract plain text
    if content:
        plain_text = extract_plain_text(content)
    elif content_compressed:
        try:
            decompressed = decompress_diary(content_compressed)
            plain_text = extract_plain_text(decompressed.get('content', ''))
        except Exception as e:
            print(f"  日记 {diary_id} 解压失败: {e}")
            plain_text = ""
    else:
        plain_text = ""
    
    # Insert into FTS
    try:
        cursor.execute(
            "INSERT INTO travel_diaries_fts(rowid, title, content_plain, city_text, tag_text) VALUES (?, ?, ?, '', '')",
            (diary_id, title or "", plain_text or "")
        )
    except Exception as e:
        print(f"  日记 {diary_id} 插入失败: {e}")
    
    print(f"  [{diary_id}] {title[:30]}... -> {len(plain_text)} chars indexed")

conn.commit()
conn.close()

print("\nFTS5 索引重建完成")
