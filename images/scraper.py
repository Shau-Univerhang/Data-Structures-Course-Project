#!/usr/bin/env python3
"""
图片爬虫 - 从 Pexels 下载城市和美食图片
Pexels 提供免费商用图片
"""

import os
import requests
import json
from urllib.parse import quote

# Pexels API (免费 tier 有 200 requests/hour)
PEXELS_API_KEY = "YOUR_PEXELS_API_KEY"  # 需要从 https://www.pexels.com/api/ 获取

# 城市列表
CITIES = [
    'beijing', 'shanghai', 'xian', 'chengdu', 'hangzhou',
    'chongqing', 'qingdao', 'guangzhou', 'suzhou', 'xiamen',
    'nanjing', 'wuhan', 'changsha', 'shenzhen', 'sanya',
    'guilin', 'zhangjiajie', 'huangshan', 'jiuzhaigou', 'dali', 'lijiang'
]

# 美食列表
FOODS = [
    ('beijing-duck', '北京烤鸭'),
    ('hot-pot', '火锅'),
    ('noodles', '面条'),
    ('shao-mai', '烧麦'),
    ('dumplings', '饺子'),
    ('dim-sum', '点心'),
    ('sushi', '寿司'),
    ('ramen', '拉面'),
    ('bbq', '烧烤'),
    ('peking-duck', '北京烤鸭'),
]

OUTPUT_DIR = "/Users/fangyuan/.openclaw/workspace/Data-Structures-Course-Project/frontend/public/images"

def download_image(url, filepath):
    """下载图片到本地"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            with open(filepath, 'wb') as f:
                f.write(response.content)
            print(f"✓ 下载成功: {filepath}")
            return True
        else:
            print(f"✗ 下载失败: {url} (status: {response.status_code})")
            return False
    except Exception as e:
        print(f"✗ 错误: {e}")
        return False

def search_pexels(query, per_page=3):
    """搜索 Pexels 图片"""
    url = f"https://api.pexels.com/v1/search?query={quote(query)}&per_page={per_page}"
    headers = {"Authorization": PEXELS_API_KEY}
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            data = response.json()
            return [photo['src']['large'] for photo in data.get('photos', [])]
        else:
            print(f"API 错误: {response.status_code}")
            return []
    except Exception as e:
        print(f"搜索错误: {e}")
        return []

def main():
    # 创建目录
    cities_dir = os.path.join(OUTPUT_DIR, "cities")
    foods_dir = os.path.join(OUTPUT_DIR, "foods")
    os.makedirs(cities_dir, exist_ok=True)
    os.makedirs(foods_dir, exist_ok=True)
    
    print("=" * 50)
    print("开始下载城市图片...")
    print("=" * 50)
    
    for city in CITIES:
        print(f"\n正在搜索: {city}")
        urls = search_pexels(city)
        if urls:
            filename = f"{city}.jpg"
            filepath = os.path.join(cities_dir, filename)
            download_image(urls[0], filepath)
        else:
            print(f"✗ 未找到: {city}")
    
    print("\n" + "=" * 50)
    print("开始下载美食图片...")
    print("=" * 50)
    
    for food_key, food_name in FOODS:
        print(f"\n正在搜索: {food_name}")
        urls = search_pexels(food_key)
        if urls:
            filename = f"{food_key}.jpg"
            filepath = os.path.join(foods_dir, filename)
            download_image(urls[0], filepath)
        else:
            print(f"✗ 未找到: {food_name}")

if __name__ == "__main__":
    main()
