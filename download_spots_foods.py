#!/usr/bin/env python3
"""
从 Unsplash 获取所有 spots 和 foods 的图片
保存到前端 public/images 和后端 images 文件夹
"""

import os
import requests
import time
import re
import sqlite3
import json
from urllib.parse import quote

# 数据库路径
DB_PATH = "/Users/fangyuan/.openclaw/workspace/Data-Structures-Course-Project/backend/data/travel.db"

# 输出目录
FRONTEND_DIR = "/Users/fangyuan/.openclaw/workspace/Data-Structures-Course-Project/frontend/public/images"
BACKEND_DIR = "/Users/fangyuan/.openclaw/workspace/Data-Structures-Course-Project/backend/images"

# 创建输出文件夹
SPOTS_FE_DIR = os.path.join(FRONTEND_DIR, "spots")
SPOTS_BE_DIR = os.path.join(BACKEND_DIR, "spots")
FOODS_FE_DIR = os.path.join(FRONTEND_DIR, "foods")
FOODS_BE_DIR = os.path.join(BACKEND_DIR, "foods")

for d in [SPOTS_FE_DIR, SPOTS_BE_DIR, FOODS_FE_DIR, FOODS_BE_DIR]:
    os.makedirs(d, exist_ok=True)

def get_db_data():
    """从数据库获取 spots 和 foods"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 获取 scenic_spots
    cursor.execute('SELECT id, name, city FROM scenic_spots')
    spots = cursor.fetchall()
    
    # 获取 restaurants
    cursor.execute('SELECT id, name, cuisine_type FROM restaurants')
    foods = cursor.fetchall()
    
    conn.close()
    return spots, foods

def get_unsplash_image(query):
    """从 Unsplash 官网获取单张图片 URL"""
    url = f"https://unsplash.com/s/photos/{quote(query)}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            # 提取图片URL
            pattern = r'https://images\.unsplash\.com/photo-[^?"&]+'
            matches = re.findall(pattern, response.text)
            if matches:
                # 返回第一张图片，添加图片参数
                return f"{matches[0]}?w=800&auto=format&fit=crop&q=80"
    except Exception as e:
        print(f"  获取失败: {e}")
    return None

def download_image(url, filepath):
    """下载图片"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            with open(filepath, 'wb') as f:
                f.write(response.content)
            return True
    except:
        pass
    return False

def sanitize_filename(name):
    """清理文件名"""
    # 替换非法字符
    name = name.replace(' ', '-').replace('/', '-').replace('(', '').replace(')', '')
    return name

def main():
    print("=" * 60)
    print("开始获取数据...")
    print("=" * 60)
    
    spots, foods = get_db_data()
    print(f"获取到 {len(spots)} 个景点, {len(foods)} 个美食")
    
    # 下载景点图片
    print("\n" + "=" * 60)
    print("开始下载景点图片...")
    print("=" * 60)
    
    success_spot = 0
    for i, (spot_id, name, city) in enumerate(spots):
        # 跳过已存在的图片
        filename = f"{city}-{sanitize_filename(name)}.jpg"
        fe_path = os.path.join(SPOTS_FE_DIR, filename)
        be_path = os.path.join(SPOTS_BE_DIR, filename)
        
        if os.path.exists(fe_path) and os.path.exists(be_path):
            print(f"[{i+1}/{len(spots)}] {city}-{name} (已存在，跳过)")
            success_spot += 1
            continue
        
        print(f"[{i+1}/{len(spots)}] {city}-{name}", end=" ... ")
        query = f"{city} {name} scenic"
        img_url = get_unsplash_image(query)
        
        if img_url:
            if download_image(img_url, fe_path) and download_image(img_url, be_path):
                print("✓")
                success_spot += 1
            else:
                print("✗ 下载失败")
        else:
            print("✗ 未找到")
        time.sleep(1.2)  # 避免请求过快
    
    # 下载美食图片
    print("\n" + "=" * 60)
    print("开始下载美食图片...")
    print("=" * 60)
    
    success_food = 0
    for i, (food_id, name, cuisine) in enumerate(foods):
        # 跳过已存在的图片
        filename = f"{sanitize_filename(name)}.jpg"
        fe_path = os.path.join(FOODS_FE_DIR, filename)
        be_path = os.path.join(FOODS_BE_DIR, filename)
        
        if os.path.exists(fe_path) and os.path.exists(be_path):
            print(f"[{i+1}/{len(foods)}] {name} (已存在，跳过)")
            success_food += 1
            continue
        
        print(f"[{i+1}/{len(foods)}] {name} ({cuisine})", end=" ... ")
        query = f"{cuisine} Chinese food"
        img_url = get_unsplash_image(query)
        
        if img_url:
            if download_image(img_url, fe_path) and download_image(img_url, be_path):
                print("✓")
                success_food += 1
            else:
                print("✗ 下载失败")
        else:
            print("✗ 未找到")
        time.sleep(1.2)
    
    print("\n" + "=" * 60)
    print(f"完成! 景点: {success_spot}/{len(spots)}, 美食: {success_food}/{len(foods)}")
    print("=" * 60)

if __name__ == "__main__":
    main()
