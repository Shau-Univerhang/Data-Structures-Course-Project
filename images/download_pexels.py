#!/usr/bin/env python3
"""
从 Pexels 下载城市图片
使用公开的图片URL
"""

import os
import requests
import time

OUTPUT_DIR = "/Users/fangyuan/.openclaw/workspace/Data-Structures-Course-Project/frontend/public/images"

# Pexels 和其他公开图片的直接URL
CITY_IMAGES = {
    'beijing': 'https://images.pexels.com/photos/416320/pexels-photo-416320.jpeg',
    'shanghai': 'https://images.pexels.com/photos/169647/pexels-photo-169647.jpeg',
    'xian': 'https://images.pexels.com/photos/1658967/pexels-photo-1658967.jpeg',
    'chengdu': 'https://images.pexels.com/photos/18055675/pexels-photo-18055675/free-photo-of-a-view-of-mountains-in-chengdu.jpeg',
    'hangzhou': 'https://images.pexels.com/photos/208745/pexels-photo-208745.jpeg',
    'chongqing': 'https://images.pexels.com/photos/169647/pexels-photo-169647.jpeg',
    'qingdao': 'https://images.pexels.com/photos/18067179/pexels-photo-18067179/free-photo-of-a-beach-at-sunset.jpeg',
    'guangzhou': 'https://images.pexels.com/photos/169647/pexels-photo-169647.jpeg',
    'suzhou': 'https://images.pexels.com/photos/2193300/pexels-photo-2193300.jpeg',
    'xiamen': 'https://images.pexels.com/photos/18067179/pexels-photo-18067179/free-photo-of-a-beach-at-sunset.jpeg',
    'nanjing': 'https://images.pexels.com/photos/169647/pexels-photo-169647.jpeg',
    'wuhan': 'https://images.pexels.com/photos/169647/pexels-photo-169647.jpeg',
    'changsha': 'https://images.pexels.com/photos/169647/pexels-photo-169647.jpeg',
    'shenzhen': 'https://images.pexels.com/photos/169647/pexels-photo-169647.jpeg',
    'sanya': 'https://images.pexels.com/photos/18067179/pexels-photo-18067179-free-photo-of-a-beach-at-sunset.jpeg',
    'guilin': 'https://images.pexels.com/photos/1450353/pexels-photo-1450353.jpeg',
    'zhangjiajie': 'https://images.pexels.com/photos/18055675/pexels-photo-18055675-free-photo-of-a-view-of-mountains-in-chengdu.jpeg',
    'huangshan': 'https://images.pexels.com/photos/1450353/pexels-photo-1450353.jpeg',
    'jiuzhaigou': 'https://images.pexels.com/photos/18055675/pexels-photo-18055675-free-photo-of-a-view-of-mountains-in-chengdu.jpeg',
    'dali': 'https://images.pexels.com/photos/2193300/pexels-photo-2193300.jpeg',
    'lijiang': 'https://images.pexels.com/photos/2193300/pexels-photo-2193300.jpeg',
}

FOOD_IMAGES = {
    'beijing-duck': 'https://images.pexels.com/photos/2641886/pexels-photo-2641886.jpeg',
    'shuan-yang-rou': 'https://images.pexels.com/photos/1640777/pexels-photo-1640777.jpeg',
    'zha-jiang-mian': 'https://images.pexels.com/photos/1907278/pexels-photo-1907278.jpeg',
    'hong-shao-rou': 'https://images.pexels.com/photos/1640777/pexels-photo-1640777.jpeg',
    'xiao-long-bao': 'https://images.pexels.com/photos/1907278/pexels-photo-1907278.jpeg',
    'sheng-jian-bao': 'https://images.pexels.com/photos/1907278/pexels-photo-1907278.jpeg',
    'ma-po-dofu': 'https://images.pexels.com/photos/1640777/pexels-photo-1640777.jpeg',
    'long-chao-shou': 'https://images.pexels.com/photos/1907278/pexels-photo-1907278.jpeg',
    'chongqing-noodles': 'https://images.pexels.com/photos/1907278/pexels-photo-1907278.jpeg',
    'xi-hu-cu-yu': 'https://images.pexels.com/photos/1640777/pexels-photo-1640777.jpeg',
    'dong-po-rou': 'https://images.pexels.com/photos/1640777/pexels-photo-1640777.jpeg',
    'rou-jia-mo': 'https://images.pexels.com/photos/1907278/pexels-photo-1907278.jpeg',
    'yang-rou-pao-mo': 'https://images.pexels.com/photos/1640777/pexels-photo-1640777.jpeg',
    'yum-cha': 'https://images.pexels.com/photos/1907278/pexels-photo-1907278.jpeg',
    'siu-mai': 'https://images.pexels.com/photos/1907278/pexels-photo-1907278.jpeg',
    'char-siu': 'https://images.pexels.com/photos/1640777/pexels-photo-1640777.jpeg',
    'song-shu-gui-yu': 'https://images.pexels.com/photos/1640777/pexels-photo-1640777.jpeg',
    'sha-cha-mian': 'https://images.pexels.com/photos/1907278/pexels-photo-1907278.jpeg',
    'tu-sun-dong': 'https://images.pexels.com/photos/1640777/pexels-photo-1640777.jpeg',
}

def download_image(url, filepath):
    """下载图片"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            with open(filepath, 'wb') as f:
                f.write(response.content)
            return True
    except Exception as e:
        print(f"  错误: {e}")
    return False

def main():
    cities_dir = os.path.join(OUTPUT_DIR, "cities")
    foods_dir = os.path.join(OUTPUT_DIR, "foods")
    os.makedirs(cities_dir, exist_ok=True)
    os.makedirs(foods_dir, exist_ok=True)
    
    print("=" * 50)
    print("开始下载城市图片...")
    print("=" * 50)
    
    for city, url in CITY_IMAGES.items():
        print(f"下载: {city}", end=" ... ")
        filepath = os.path.join(cities_dir, f"{city}.jpg")
        if download_image(url, filepath):
            print("✓")
        else:
            print("✗")
        time.sleep(0.5)
    
    print("\n" + "=" * 50)
    print("开始下载美食图片...")
    print("=" * 50)
    
    for food, url in FOOD_IMAGES.items():
        print(f"下载: {food}", end=" ... ")
        filepath = os.path.join(foods_dir, f"{food}.jpg")
        if download_image(url, filepath):
            print("✓")
        else:
            print("✗")
        time.sleep(0.5)
    
    print("\n完成!")

if __name__ == "__main__":
    main()
