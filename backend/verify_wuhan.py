"""
验证武汉的景点名称映射
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import SessionLocal, ScenicSpot

# City.vue中的映射关键词（只包含武汉相关的）
WUHAN_MAPPINGS = {
    '黄鹤楼': '/images/spots/wuhan/wuhan_huanghelou.jpg',
    '东湖': '/images/spots/wuhan/wuhan_donghu.jpg',
    '户部巷': '/images/spots/wuhan/wuhan_hubuxiang.jpg',
    '武汉大学': '/images/spots/wuhan/wuhan_wuhan_daxue.jpg',
    '湖北省博物馆': '/images/spots/wuhan/wuhan_hubei_bowuguan.jpg',
    '江汉路': '/images/spots/wuhan/wuhan_jianghanlu_buxingjie.jpg',
    '古琴台': '/images/spots/wuhan/wuhan_guqintai.jpg',
    '晴川阁': '/images/spots/wuhan/wuhan_qingchuange.jpg',
    '昙华林': '/images/spots/wuhan/wuhan_tanhualin.jpg',
    '汉口江滩': '/images/spots/wuhan/wuhan_hankou_jiangtan.jpg',
    '长江大桥': '/images/spots/wuhan/wuhan_wuhan_changjiang_daqiao.jpg',
    '归元寺': '/images/spots/wuhan/wuhan_guiyuansi.jpg',
    '光谷': '/images/spots/wuhan/wuhan_guanggu_buxingjie.jpg',
}

def get_spot_image(spot_name):
    """模拟City.vue的getSpotImage函数"""
    if not spot_name:
        return None
    
    # 1. 完全匹配
    if spot_name in WUHAN_MAPPINGS:
        return WUHAN_MAPPINGS[spot_name]
    
    # 2. 包含匹配
    for keyword, image_path in WUHAN_MAPPINGS.items():
        if keyword in spot_name or spot_name in keyword:
            return image_path
    
    return None

def verify_wuhan():
    db = SessionLocal()
    
    spots = db.query(ScenicSpot).filter(ScenicSpot.city == "武汉").all()
    print(f"武汉共有 {len(spots)} 个景点:\n")
    
    unmatched = []
    for spot in spots:
        image = get_spot_image(spot.name)
        if image:
            print(f"[OK] {spot.name}")
        else:
            print(f"[MISSING] {spot.name}")
            unmatched.append(spot.name)
    
    if unmatched:
        print(f"\n未匹配的景点: {unmatched}")
    else:
        print("\n所有景点都能正确匹配!")
    
    db.close()

if __name__ == "__main__":
    verify_wuhan()
