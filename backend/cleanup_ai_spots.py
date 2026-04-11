"""
清理AI创建的虚拟景点
删除标签为"AI推荐"的景点
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import SessionLocal, ScenicSpot

def cleanup_ai_spots():
    db = SessionLocal()
    
    try:
        # 查找所有标签包含"AI推荐"的景点
        ai_spots = db.query(ScenicSpot).filter(
            ScenicSpot.tags.contains(["AI推荐"])
        ).all()
        
        print(f"找到 {len(ai_spots)} 个AI推荐的虚拟景点")
        
        for spot in ai_spots:
            print(f"删除: {spot.name} ({spot.city})")
            db.delete(spot)
        
        db.commit()
        print(f"\n成功删除 {len(ai_spots)} 个虚拟景点！")
        
    except Exception as e:
        print(f"清理失败: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    cleanup_ai_spots()
