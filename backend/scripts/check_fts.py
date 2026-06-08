import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3
from models.database import DB_PATH
from utils.diary_fts import normalize_title, compute_title_hash, extract_plain_text, insert_diary_to_fts

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Check FTS table
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='travel_diaries_fts'")
result = cursor.fetchone()
print('FTS5 table exists:', result is not None)

# Check diary count
cursor.execute('SELECT COUNT(*) FROM travel_diaries')
count = cursor.fetchone()[0]
print('Total diaries:', count)

# Check FTS count
if result:
    cursor.execute('SELECT COUNT(*) FROM travel_diaries_fts')
    fts_count = cursor.fetchone()[0]
    print('FTS5 entries:', fts_count)
    
    # Re-populate if empty
    if fts_count == 0:
        print('Re-populating FTS5 index...')
        cursor.execute('SELECT id, title, content FROM travel_diaries WHERE title IS NOT NULL')
        rows = cursor.fetchall()
        for row in rows:
            diary_id, title, content = row
            content_plain = extract_plain_text(content)
            try:
                cursor.execute("DELETE FROM travel_diaries_fts WHERE rowid = ?", (diary_id,))
                cursor.execute(
                    "INSERT INTO travel_diaries_fts(rowid, title, content_plain, city_text, tag_text) VALUES (?, ?, ?, '', '')",
                    (diary_id, title or "", content_plain or "")
                )
            except Exception as e:
                print(f'  Failed for diary {diary_id}: {e}')
        conn.commit()
        cursor.execute('SELECT COUNT(*) FROM travel_diaries_fts')
        new_count = cursor.fetchone()[0]
        print(f'FTS5 entries after re-populate: {new_count}')

# Check new columns
cursor.execute('PRAGMA table_info(travel_diaries)')
columns = [row[1] for row in cursor.fetchall()]
print('Has normalized_title:', 'normalized_title' in columns)
print('Has title_hash:', 'title_hash' in columns)
print('Has content_plain:', 'content_plain' in columns)

conn.close()
