#!/usr/bin/env python3
"""
从 picsum.photos 下载城市和美食占位图片
picsum.photos 提供免费占位图片

城市和美食图片需要手动下载或使用其他图库
"""

import os
import requests
import time
import random

OUTPUT_DIR = "/Users/fangyuan/.openclaw/workspace/Data-Structures-Course-Project/frontend/public/images"

# 城市列表
CITIES = [
    'beijing', 'shanghai', 'xian', 'chengdu', 'hangzhou',
    'chongqing', 'qingdao', 'guangzhou', 'suzhou', 'xiamen',
    'nanjing', 'wuhan', 'changsha', 'shenzhen', 'sanya',
    'guilin', 'zhangjiajie', 'huangshan', 'jiuzhaigou', 'dali', 'lijiang'
]

# 美食列表
FOODS = [
    'beijing-duck', 'hot-pot', 'zha-jiang-mian', 'hong-shao-rou',
    'xiao-long-bao', 'sheng-jian-bao', 'ma-po-dofu', 'long-chao-shou',
    'chongqing-noodles', 'xi-hu-cu-yu', 'dong-po-rou', 'rou-jia-mo',
    'yang-rou-pao-mo', 'yum-cha', 'siu-mai', 'char-siu',
    'song-shu-gui-yu', 'sha-cha-mian', 'tu-sun-dong'
]

def download_image(url, filepath):
    """下载图片到本地"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            with open(filepath, 'wb') as f:
                f.write(response.content)
            return True
        else:
            return False
    except Exception as e:
        print(f"  错误: {e}")
        return False

def main():
    # 创建目录
    cities_dir = os.path.join(OUTPUT_DIR, "cities")
    foods_dir = os.path.join(OUTPUT_DIR, "foods")
    os.makedirs(cities_dir, exist_ok=True)
    os.makedirs(foods_dir, exist_ok=True)
    
    print("=" * 50)
    print("开始下载城市图片 (使用 picsum.photos)...")
    print("=" * 50)
    
    # 为每个城市下载不同但固定的图片 (使用不同的 seed)
    for i, city in enumerate(CITIES):
        # 使用固定的 seed 保证每次运行结果一致
        seed = 100 + i
        url = f"https://picsum.photos/seed/{seed}/800/600"
        filepath = os.path.join(cities_dir, f"{city}.jpg")
        print(f"正在下载: {city}...", end=" ")
        if download_image(url, filepath):
            print("✓")
        else:
            print("✗")
        time.sleep(0.3)
    
    print("\n" + "=" * 50)
    print("开始下载美食图片...")
    print("=" * 50)
    
    for i, food in enumerate(FOODS):
        seed = 200 + i
        url = f"https://picsum.photos/seed/{seed}/800/600"
        filepath = os.path.join(foods_dir, f"{food}.jpg")
        print(f"正在下载: {food}...", end=" ")
        if download_image(url, filepath):
            print("✓")
        else:
            print("✗")
        time.sleep(0.3)
    
    print("\n下载完成!")
    print(f"城市图片: {cities_dir}")
    print(f"美食图片: {foods_dir}")

if __name__ == "__main__":
    main()
