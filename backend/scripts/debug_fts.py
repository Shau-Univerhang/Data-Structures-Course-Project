import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3
from models.database import DB_PATH

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Check FTS content
cursor.execute("SELECT rowid, title, content_plain FROM travel_diaries_fts")
rows = cursor.fetchall()
print(f"FTS5 共有 {len(rows)} 条记录:")
for row in rows:
    print(f"  [{row[0]}] title='{row[1]}' content_plain='{(row[2] or '')[:50]}'")

# Test MATCH queries
print("\n测试 MATCH 查询:")
for query in ["北京", "旅行", "延吉", "爆炸"]:
    try:
        cursor.execute("SELECT rowid, title FROM travel_diaries_fts WHERE travel_diaries_fts MATCH ?", (query,))
        results = cursor.fetchall()
        print(f"  MATCH '{query}': {len(results)} 条结果")
        for r in results:
            print(f"    [{r[0]}] {r[1]}")
    except Exception as e:
        print(f"  MATCH '{query}' 失败: {e}")

# Check tokenizer
print("\nFTS5 表信息:")
cursor.execute("SELECT sql FROM sqlite_master WHERE name='travel_diaries_fts'")
print(cursor.fetchone()[0])

conn.close()
