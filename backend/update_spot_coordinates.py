"""
批量更新景点坐标 - 使用高德地图 API 获取真实地理位置
"""
import requests
import sqlite3
import time
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 高德地图 Web 服务 API Key（需要在 https://lbs.amap.com/ 申请）
AMAP_WEB_SERVICE_KEY = os.getenv("AMAP_WEB_SERVICE_KEY", "")

# 数据库路径
DB_PATH = Path(__file__).parent / "data" / "travel.db"


def get_coordinates_by_name(name: str, city: str):
    """
    使用高德地图 API 根据名称和城市获取坐标
    """
    if not AMAP_WEB_SERVICE_KEY:
        print("⚠️  未配置 AMAP_WEB_SERVICE_KEY，跳过 API 调用")
        return None
    
    # 高德地图 Web 服务 API
    url = "https://restapi.amap.com/v3/place/text"
    
    params = {
        "key": AMAP_WEB_SERVICE_KEY,
        "keywords": name,
        "city": city,
        "offset": 1,
        "output": "json"
    }
    
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") == "1" and data.get("pois"):
            poi = data["pois"][0]
            location = poi.get("location", "")
            if location:
                lng, lat = map(float, location.split(","))
                return {
                    "lng": lng,
                    "lat": lat,
                    "address": poi.get("address", "")
                }
        
        return None
    except Exception as e:
        print(f"❌ 查询失败 {name}: {e}")
        return None


def update_coordinates():
    """批量更新所有景点的坐标"""
    print("🗺️  开始更新景点坐标...")
    print(f"📍 数据库：{DB_PATH}")
    
    # 连接数据库
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 查询所有缺少坐标的景点
    cursor.execute("""
        SELECT id, name, city 
        FROM scenic_spots 
        WHERE location_lng IS NULL OR location_lat IS NULL
        ORDER BY city, name
    """)
    
    spots = cursor.fetchall()
    total = len(spots)
    print(f"📊 共找到 {total} 个需要更新坐标的景点\n")
    
    if total == 0:
        print("✅ 所有景点坐标已完整！")
        conn.close()
        return
    
    success_count = 0
    fail_count = 0
    
    for i, (spot_id, name, city) in enumerate(spots, 1):
        print(f"[{i}/{total}] 正在查询：{city} - {name}")
        
        # 先尝试从已有数据中获取（同一城市的其他景点可能已经查询过）
        cursor.execute("""
            SELECT location_lng, location_lat 
            FROM scenic_spots 
            WHERE city = ? AND location_lng IS NOT NULL AND location_lat IS NOT NULL
            LIMIT 1
        """, (city,))
        
        # 调用高德 API 获取坐标
        result = get_coordinates_by_name(name, city)
        
        if result:
            # 更新数据库
            cursor.execute("""
                UPDATE scenic_spots 
                SET location_lng = ?, location_lat = ?, address = ?
                WHERE id = ?
            """, (result["lng"], result["lat"], result.get("address", ""), spot_id))
            
            conn.commit()
            print(f"   ✅ 已更新：[{result['lng']}, {result['lat']}]")
            success_count += 1
        else:
            print(f"   ❌ 未找到坐标")
            fail_count += 1
        
        # 避免请求过快，添加延迟
        if i < total:
            time.sleep(0.2)
    
    # 统计结果
    print(f"\n{'='*50}")
    print(f"✅ 更新成功：{success_count} 个")
    print(f"❌ 更新失败：{fail_count} 个")
    print(f"📊 总计处理：{total} 个")
    
    # 关闭连接
    conn.close()
    
    if fail_count > 0:
        print(f"\n⚠️  有 {fail_count} 个景点未能获取坐标，可能需要手动补充")


if __name__ == "__main__":
    if not AMAP_WEB_SERVICE_KEY:
        print("="*50)
        print("⚠️  警告：未配置高德地图 Web 服务 API Key")
        print("="*50)
        print("\n请按以下步骤操作：")
        print("1. 访问 https://lbs.amap.com/ 注册并登录")
        print("2. 进入「应用管理」> 「我的应用」")
        print("3. 点击「添加新 Key」")
        print("4. 服务平台选择「Web 服务 (MCP)」")
        print("5. 复制生成的 Key")
        print("6. 在 backend/.env 文件中添加：")
        print(f"   AMAP_WEB_SERVICE_KEY=你的 Key")
        print("\n" + "="*50)
        
        # 询问是否继续
        choice = input("\n是否使用测试模式继续（仅更新已知坐标的景点）？(y/n): ")
        if choice.lower() != 'y':
            exit(0)
    
    update_coordinates()
