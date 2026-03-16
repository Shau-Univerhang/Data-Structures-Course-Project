#!/usr/bin/env python3
"""
使用 Unsplash API 下载所有 spots 和 foods 图片
"""

import os
import requests
import time
import sqlite3
from urllib.parse import quote

DB_PATH = "/Users/fangyuan/.openclaw/workspace/Data-Structures-Course-Project/backend/data/travel.db"

# 输出目录
FRONTEND_DIR = "/Users/fangyuan/.openclaw/workspace/Data-Structures-Course-Project/frontend/public/images"
BACKEND_DIR = "/Users/fangyuan/.openclaw/workspace/Data-Structures-Course-Project/backend/images"

SPOTS_FE_DIR = os.path.join(FRONTEND_DIR, "spots")
SPOTS_BE_DIR = os.path.join(BACKEND_DIR, "spots")
FOODS_FE_DIR = os.path.join(FRONTEND_DIR, "foods")
FOODS_BE_DIR = os.path.join(BACKEND_DIR, "foods")

for d in [SPOTS_FE_DIR, SPOTS_BE_DIR, FOODS_FE_DIR, FOODS_BE_DIR]:
    os.makedirs(d, exist_ok=True)

API_KEY = "CZMqUNyjf3I9SSzQp63FTqQoMCMXFkyGFo1VHVjiONE"

def get_db_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, city FROM scenic_spots')
    spots = cursor.fetchall()
    cursor.execute('SELECT id, name, cuisine_type FROM restaurants')
    foods = cursor.fetchall()
    conn.close()
    return spots, foods

def search_unsplash(query):
    url = "https://api.unsplash.com/search/photos"
    headers = {"Authorization": f"Client-ID {API_KEY}"}
    params = {"query": query, "per_page": 1, "orientation": "landscape"}
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("results"):
                return data["results"][0]["urls"]["regular"]
    except Exception as e:
        print(f"  API错误: {e}")
    return None

def download_image(url, filepath):
    try:
        resp = requests.get(url, timeout=30)
        if resp.status_code == 200:
            with open(filepath, 'wb') as f:
                f.write(resp.content)
            return True
    except:
        pass
    return False

def sanitize(name):
    return name.replace(' ', '-').replace('/', '-').replace('(', '').replace(')', '')

def main():
    spots, foods = get_db_data()
    print(f"获取到 {len(spots)} 个景点, {len(foods)} 个美食\n")

    # 下载景点
    print("=" * 50)
    print("下载景点图片...")
    print("=" * 50)
    success = 0
    for i, (sid, name, city) in enumerate(spots):
        filename = f"{city}-{sanitize(name)}.jpg"
        fe_path = os.path.join(SPOTS_FE_DIR, filename)
        be_path = os.path.join(SPOTS_BE_DIR, filename)
        
        if os.path.exists(fe_path):
            print(f"[{i+1}/{len(spots)}] {city}-{name} (已有)")
            success += 1
            continue
            
        print(f"[{i+1}/{len(spots)}] {city}-{name}", end=" ... ")
        query = f"{city} {name} China"
        url = search_unsplash(query)
        if url and download_image(url, fe_path) and download_image(url, be_path):
            print("✓")
            success += 1
        else:
            print("✗")
        time.sleep(1)

    # 下载美食
    print("\n" + "=" * 50)
    print("下载美食图片...")
    print("=" * 50)
    success2 = 0
    for i, (fid, name, cuisine) in enumerate(foods):
        filename = f"{sanitize(name)}.jpg"
        fe_path = os.path.join(FOODS_FE_DIR, filename)
        be_path = os.path.join(FOODS_BE_DIR, filename)
        
        if os.path.exists(fe_path):
            print(f"[{i+1}/{len(foods)}] {name} (已有)")
            success2 += 1
            continue
            
        print(f"[{i+1}/{len(foods)}] {name} ({cuisine})", end=" ... ")
        query = f"{cuisine} Chinese food"
        url = search_unsplash(query)
        if url and download_image(url, fe_path) and download_image(url, be_path):
            print("✓")
            success2 += 1
        else:
            print("✗")
        time.sleep(1)

    print(f"\n完成! 景点: {success}/{len(spots)}, 美食: {success2}/{len(foods)}")

if __name__ == "__main__":
    main()
