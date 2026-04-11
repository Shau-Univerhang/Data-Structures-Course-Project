import sqlite3

conn = sqlite3.connect('backend/data/travel.db')
cursor = conn.cursor()

cursor.execute('SELECT id, username, avatar_url FROM users WHERE username = "shau"')
result = cursor.fetchone()

if result:
    print(f'用户 ID: {result[0]}')
    print(f'用户名：{result[1]}')
    print(f'头像 URL: {result[2] if result[2] else "无"}')
else:
    print('用户不存在')

conn.close()
