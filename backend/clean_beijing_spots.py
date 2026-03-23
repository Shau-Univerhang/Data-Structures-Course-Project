"""
清理北京景点数据，只保留有图片的景点
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import SessionLocal, ScenicSpot

# 北京图片文件夹中的图片（景点英文名）
BEIJING_IMAGES = {
    'badaling_changcheng': '八达岭长城',
    'beihai_gongyuan': '北海公园',
    'beijing_daxue': '北京大学',
    'gongwangfu': '恭王府',
    'gugong_bowuyuan': '故宫博物院',
    'jingshan_gongyuan': '景山公园',
    'nanluoguxiang': '南锣鼓巷',
    'niaochao': '鸟巢',
    'qinghua_daxue': '清华大学',
    'shichahai': '什刹海',
    'shuilifang': '水立方',
    'tiananmen_guangchang': '天安门广场',
    'tiantan_gongyuan': '天坛公园',
    'yiheyuan': '颐和园',
    'yuanmingyuan': '圆明园',
}

# 有图片的景点名称列表
VALID_SPOT_NAMES = set(BEIJING_IMAGES.values())

def clean_beijing_spots():
    db = SessionLocal()
    
    # 获取所有北京景点
    spots = db.query(ScenicSpot).filter(ScenicSpot.city == '北京').all()
    
    print(f"Database has {len(spots)} Beijing spots")
    print(f"Image folder has {len(VALID_SPOT_NAMES)} spots")
    
    deleted_count = 0
    kept_count = 0
    
    for spot in spots:
        if spot.name in VALID_SPOT_NAMES:
            kept_count += 1
        else:
            db.delete(spot)
            deleted_count += 1
    
    db.commit()
    db.close()
    
    print(f"\nCleanup done:")
    print(f"  Kept: {kept_count}")
    print(f"  Deleted: {deleted_count}")

if __name__ == "__main__":
    clean_beijing_spots()
