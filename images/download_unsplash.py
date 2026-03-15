#!/usr/bin/env python3
"""
从 Unsplash 官网爬取城市和美食图片
"""

import os
import requests
import time
import re
from urllib.parse import quote

OUTPUT_DIR = "/Users/fangyuan/.openclaw/workspace/Data-Structures-Course-Project/frontend/public/images"

# 城市和搜索关键词
CITIES = {
    'beijing': 'Beijing city',
    'shanghai': 'Shanghai skyline',
    'xian': 'Xi_an China',
    'chengdu': 'Chengdu city',
    'hangzhou': 'Hangzhou West Lake',
    'chongqing': 'Chengdu city',  # 重庆类似的
    'qingdao': 'Qingdao beach',
    'guangzhou': 'Guangzhou city',
    'suzhou': 'Suzhou garden',
    'xiamen': 'Xiamen coastal',
    'nanjing': 'Nanjing city',
    'wuhan': 'Wuhan city',
    'changsha': 'Changsha city',
    'shenzhen': 'Shenzhen city',
    'sanya': 'Sanya beach tropical',
    'guilin': 'Guilin landscape karst',
    'zhangjiajie': 'Zhangjiajie mountains',
    'huangshan': 'Huangshan mountain',
    'jiuzhaigou': 'Jiuzhaigou colorful lake',
    'dali': 'Dali old town Yunnan',
    'lijiang': 'Lijiang old town',
}

# 美食和搜索关键词
FOODS = {
    'beijing-duck': 'Peking duck roast duck',
    'shuan-yang-rou': 'Chinese hot pot lamb',
    'zha-jiang-mian': 'Chinese noodles',
    'hong-shao-rou': 'Braised pork',
    'xiao-long-bao': 'Soup dumplings dim sum',
    'sheng-jian-bao': 'Pan fried buns',
    'ma-po-dofu': 'Mapo tofu',
    'long-chao-shou': 'Sichuan wonton',
    'chongqing-noodles': 'Chongqing spicy noodles',
    'xi-hu-cu-yu': 'Chinese fish dish',
    'dong-po-rou': 'Dongpo pork',
    'rou-jia-mo': 'Chinese burger',
    'yang-rou-pao-mo': 'Lamb soup bread',
    'yum-cha': 'Chinese dim sum',
    'siu-mai': 'Shumai dim sum',
    'char-siu': 'Chinese bbq pork',
    'song-shu-gui-yu': 'Sweet sour fish Chinese',
    'sha-cha-mian': 'Sha cha noodles',
    'tu-sun-dong': 'Sea worm jelly',
}

def get_unsplash_images(query, count=3):
    """从 Unsplash 官网获取图片 URL"""
    url = f"https://unsplash.com/s/photos/{quote(query)}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            # 提取图片URL - 使用更精确的正则
            pattern = r'https://images\.unsplash\.com/photo-[^?"&]+'
            matches = re.findall(pattern, response.text)
            # 去重并返回
            unique_urls = list(dict.fromkeys(matches))
            # 转换格式为固定宽度
            urls = []
            for u in unique_urls[:count]:
                # 添加图片参数
                urls.append(f"{u}?w=800&auto=format&fit=crop&q=80")
            return urls
        return []
    except Exception as e:
        print(f"  获取失败: {e}")
        return []

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

def main():
    cities_dir = os.path.join(OUTPUT_DIR, "cities")
    foods_dir = os.path.join(OUTPUT_DIR, "foods")
    os.makedirs(cities_dir, exist_ok=True)
    os.makedirs(foods_dir, exist_ok=True)
    
    print("=" * 50)
    print("开始下载城市图片...")
    print("=" * 50)
    
    for city, query in CITIES.items():
        print(f"搜索: {city} ({query})", end=" ... ")
        urls = get_unsplash_images(query)
        if urls:
            filepath = os.path.join(cities_dir, f"{city}.jpg")
            if download_image(urls[0], filepath):
                print("✓")
            else:
                print("✗")
        else:
            print("✗ 未找到")
        time.sleep(1.5)  # 避免请求过快
    
    print("\n" + "=" * 50)
    print("开始下载美食图片...")
    print("=" * 50)
    
    for food, query in FOODS.items():
        print(f"搜索: {food} ({query})", end=" ... ")
        urls = get_unsplash_images(query)
        if urls:
            filepath = os.path.join(foods_dir, f"{food}.jpg")
            if download_image(urls[0], filepath):
                print("✓")
            else:
                print("✗")
        else:
            print("✗ 未找到")
        time.sleep(1.5)
    
    print("\n完成!")

if __name__ == "__main__":
    main()
