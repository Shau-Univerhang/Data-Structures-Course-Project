"""
使用高德地图 Geocoding API 批量获取景点真实坐标
"""
import requests
import sqlite3
import time
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 高德地图 Web 服务 API Key
AMAP_KEY = os.getenv("AMAP_WEB_SERVICE_KEY", "")

# 数据库路径
DB_PATH = Path(__file__).parent / "data" / "travel.db"


def geocode_address(address: str, city: str):
    """
    使用高德地图 Geocoding API 获取坐标
    文档：https://lbs.amap.com/api/webservice/guide/api/georegeo
    """
    url = "https://restapi.amap.com/v3/geocode/geo"
    
    params = {
        "key": AMAP_KEY,
        "address": address,
        "city": city,
        "output": "json"
    }
    
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") == "1" and data.get("geocodes"):
            geocode = data["geocodes"][0]
            location = geocode.get("location", "")
            if location:
                lng, lat = map(float, location.split(","))
                return {
                    "lng": lng,
                    "lat": lat,
                    "formatted_address": geocode.get("formatted_address", "")
                }
        
        return None
    except Exception as e:
        print(f"  ❌ Geocoding 失败：{e}")
        return None


def update_all_spots():
    """更新所有景点的坐标"""
    print("🗺️  开始使用 Geocoding 更新景点坐标...")
    print(f"📍 数据库：{DB_PATH}")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 查询所有景点
    cursor.execute("SELECT id, name, city FROM scenic_spots ORDER BY city, name")
    spots = cursor.fetchall()
    
    print(f"📊 共找到 {len(spots)} 个景点\n")
    
    success_count = 0
    fail_count = 0
    skip_count = 0
    
    for i, (spot_id, name, city) in enumerate(spots, 1):
        print(f"[{i}/{len(spots)}] {city} - {name}")
        
        # 检查是否已有坐标
        cursor.execute(
            "SELECT location_lng, location_lat FROM scenic_spots WHERE id = ?",
            (spot_id,)
        )
        row = cursor.fetchone()
        
        if row[0] and row[1]:
            print(f"  ⏭️  已有坐标，跳过")
            skip_count += 1
            continue
        
        # 调用 Geocoding API
        address = f"{city}{name}"
        result = geocode_address(address, city)
        
        if result:
            # 更新数据库
            cursor.execute(
                """UPDATE scenic_spots 
                   SET location_lng = ?, location_lat = ?, address = ? 
                   WHERE id = ?""",
                (result["lng"], result["lat"], result.get("formatted_address", ""), spot_id)
            )
            conn.commit()
            print(f"  ✅ 已更新：[{result['lng']:.6f}, {result['lat']:.6f}]")
            print(f"     地址：{result.get('formatted_address', 'N/A')}")
            success_count += 1
        else:
            print(f"  ❌ 未找到坐标")
            fail_count += 1
        
        # 避免请求过快
        if i < len(spots):
            time.sleep(0.2)
    
    conn.close()
    
    print(f"\n{'='*60}")
    print(f"✅ 更新成功：{success_count} 个")
    print(f"❌ 更新失败：{fail_count} 个")
    print(f"⏭️  已跳过：{skip_count} 个")
    print(f"📊 总计：{len(spots)} 个")


if __name__ == "__main__":
    print("="*60)
    print("高德地图 Geocoding - 批量更新景点坐标")
    print("="*60)
    print()
    print("⚠️  注意：")
    print("1. 需要有效的 Web 服务 API Key")
    print("2. 申请地址：https://lbs.amap.com/")
    print("3. 服务平台选择「Web 服务 (MCP)」")
    print()
    
    choice = input("是否继续？(y/n): ")
    if choice.lower() != 'y':
        exit(0)
    
    update_all_spots()
