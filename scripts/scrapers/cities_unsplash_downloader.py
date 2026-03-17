#!/usr/bin/env python3
"""
Unsplash 图片下载脚本
用于从 Unsplash 获取城市和美食图片

使用方法:
    python unsplash_downloader.py --key YOUR_UNSPLASH_API_KEY

参数:
    --key     Unsplash API Access Key (必填)
    --type    下载类型: city(城市) / food(美食) / all(全部) 默认: all
    --output  输出目录 默认: ./downloads
    --count   每个关键字下载的图片数量 默认: 1
"""

import os
import sys
import requests
import argparse
import time

# 默认配置
DEFAULT_CITIES = [
    "北京", "上海", "西安", "成都", "杭州", "重庆", "青岛", "广州", "苏州", "厦门",
    "南京", "武汉", "长沙", "深圳", "三亚", "桂林", "张家界", "黄山", "九寨沟", "大理", "丽江"
]

DEFAULT_FOODS = [
    "北京烤鸭", "涮羊肉", "炸酱面", "小笼包", "生煎包", "麻辣火锅", "麻婆豆腐",
    "龙抄手", "重庆火锅", "小面", "西湖醋鱼", "东坡肉", "肉夹馍", "羊肉泡馍",
    "早茶", "烧腊", "松鼠桂鱼", "沙茶面", "土笋冻"
]


def search_unsplash(api_key, query, per_page=5):
    """
    搜索 Unsplash 图片
    
    Args:
        api_key: Unsplash API Access Key
        query: 搜索关键词
        per_page: 返回数量
    
    Returns:
        list: 图片URL列表
    """
    url = "https://api.unsplash.com/search/photos"
    headers = {"Authorization": f"Client-ID {api_key}"}
    params = {
        "query": query,
        "per_page": per_page,
        "orientation": "landscape",
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        if response.status_code == 200:
            data = response.json()
            return [photo["urls"]["regular"] for photo in data.get("results", [])]
        else:
            print(f"  API 错误: {response.status_code}")
            return []
    except Exception as e:
        print(f"  请求错误: {e}")
        return []


def download_image(url, filepath):
    """
    下载图片到本地
    
    Args:
        url: 图片URL
        filepath: 保存路径
    
    Returns:
        bool: 是否成功
    """
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            # 确保目录存在
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, "wb") as f:
                f.write(response.content)
            return True
    except Exception as e:
        print(f"  下载错误: {e}")
    return False


def download_category(api_key, items, output_dir, category_name):
    """
    下载一类图片
    
    Args:
        api_key: API Key
        items: 关键词列表
        output_dir: 输出目录
        category_name: 分类名称
    """
    category_dir = os.path.join(output_dir, category_name)
    os.makedirs(category_dir, exist_ok=True)
    
    print(f"\n📥 开始下载 {category_name} 图片...")
    for i, item in enumerate(items):
        print(f"  [{i+1}/{len(items)}] 搜索: {item}", end=" ... ")
        
        urls = search_unsplash(api_key, item, per_page=3)
        if urls:
            # 使用拼音/英文命名
            filename = f"{item}.jpg"
            filepath = os.path.join(category_dir, filename)
            if download_image(urls[0], filepath):
                print("✓")
            else:
                print("✗")
        else:
            print("✗ 未找到")
        
        # 避免请求过快
        time.sleep(1)


def main():
    parser = argparse.ArgumentParser(
        description="从 Unsplash 下载城市和美食图片",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python unsplash_downloader.py --key YOUR_API_KEY
  python unsplash_downloader.py --key YOUR_API_KEY --type city
  python unsplash_downloader.py --key YOUR_API_KEY --type all --output ./images
        """
    )
    parser.add_argument("--key", required=True, help="Unsplash API Access Key")
    parser.add_argument(
        "--type", 
        choices=["city", "food", "all"], 
        default="all", 
        help="下载类型 (默认: all)"
    )
    parser.add_argument(
        "--output", 
        default="./downloads", 
        help="输出目录 (默认: ./downloads)"
    )
    parser.add_argument(
        "--count", 
        type=int, 
        default=1, 
        help="每个关键字下载的图片数量 (默认: 1)"
    )
    
    args = parser.parse_args()
    api_key = args.key
    output_dir = args.output

    print("=" * 50)
    print("Unsplash 图片下载器")
    print("=" * 50)

    # 下载城市图片
    if args.type in ["city", "all"]:
        download_category(api_key, DEFAULT_CITIES, output_dir, "cities")

    # 下载美食图片
    if args.type in ["food", "all"]:
        download_category(api_key, DEFAULT_FOODS, output_dir, "foods")

    print("\n" + "=" * 50)
    print("✅ 下载完成!")
    print(f"城市图片: {os.path.join(output_dir, 'cities')}")
    print(f"美食图片: {os.path.join(output_dir, 'foods')}")
    print("=" * 50)


if __name__ == "__main__":
    main()
