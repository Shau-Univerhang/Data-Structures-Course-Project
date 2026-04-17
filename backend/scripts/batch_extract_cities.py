"""
批量处理历史日记，提取城市标签

使用方法:
    cd backend
    python scripts/batch_extract_cities.py
    
    # 仅处理未提取过的日记
    python scripts/batch_extract_cities.py --skip-existing
    
    # 强制重新提取所有日记
    python scripts/batch_extract_cities.py --force
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from models.database import get_db, TravelDiary, DiaryCity, DiaryCityTag
from utils.city_extractor import CityExtractor, get_extractor
from algorithms.core import decompress_diary
import argparse


def get_or_create_city(db: Session, city_name: str, extractor: CityExtractor) -> DiaryCity:
    """获取或创建城市标签"""
    # 检查是否已存在
    city = db.query(DiaryCity).filter(DiaryCity.name == city_name).first()
    if city:
        return city
    
    # 检查是否是别名
    canonical_name = extractor.resolve_alias(city_name)
    if canonical_name != city_name:
        city = db.query(DiaryCity).filter(DiaryCity.name == canonical_name).first()
        if city:
            return city
        city_name = canonical_name
    
    # 创建新城市
    new_city = DiaryCity(name=city_name, diary_count=0)
    db.add(new_city)
    db.commit()
    db.refresh(new_city)
    print(f"  [CITY] 创建新城市: {city_name}")
    return new_city


def extract_diary_cities(db: Session, diary: TravelDiary, extractor: CityExtractor) -> list:
    """提取单个日记的城市标签"""
    # 解压内容
    content = diary.content
    if diary.content_compressed and not content:
        try:
            content = decompress_diary(diary.content_compressed).get('content', '')
        except:
            content = ''
    
    # 提取城市
    cities = extractor.extract_cities(
        title=diary.title,
        content=content,
        itinerary=diary.itinerary
    )
    
    return cities


def process_diary(db: Session, diary: TravelDiary, extractor: CityExtractor, skip_existing: bool = True) -> bool:
    """处理单个日记，返回是否成功提取到城市"""
    
    # 检查是否已处理过
    if skip_existing:
        existing_tags = db.query(DiaryCityTag).filter(DiaryCityTag.diary_id == diary.id).first()
        if existing_tags:
            return False
    
    # 提取城市
    cities = extract_diary_cities(db, diary, extractor)
    
    if not cities:
        return False
    
    # 保存城市关联
    for city_data in cities:
        city_name = city_data['city']
        confidence = city_data['confidence']
        
        # 获取或创建城市
        city = get_or_create_city(db, city_name, extractor)
        
        # 检查是否已关联
        existing = db.query(DiaryCityTag).filter_by(
            diary_id=diary.id,
            city_id=city.id
        ).first()
        
        if not existing:
            # 创建关联
            tag = DiaryCityTag(
                diary_id=diary.id,
                city_id=city.id,
                confidence=confidence
            )
            db.add(tag)
            
            # 更新城市计数
            city.diary_count += 1
            db.commit()
    
    return True


def batch_process(db: Session, skip_existing: bool = True, limit: int = None, public_only: bool = False):
    """批量处理日记"""
    extractor = get_extractor()
    
    # 获取日记（默认所有，可选仅公开）
    query = db.query(TravelDiary)
    if public_only:
        query = query.filter(TravelDiary.is_public == True)
    
    if skip_existing:
        # 只处理没有城市标签的日记
        subquery = db.query(DiaryCityTag.diary_id).distinct()
        query = query.filter(~TravelDiary.id.in_(subquery))
    
    if limit:
        query = query.limit(limit)
    
    diaries = query.all()
    total = len(diaries)
    
    if total == 0:
        print("[OK] 没有需要处理的日记")
        return
    
    print(f"[INFO] 开始处理 {total} 篇日记...")
    print("=" * 60)
    
    processed = 0
    extracted = 0
    
    for i, diary in enumerate(diaries, 1):
        print(f"\n[{i}/{total}] 处理日记: {diary.title}")
        
        success = process_diary(db, diary, extractor, skip_existing=False)
        
        if success:
            extracted += 1
            # 显示提取到的城市
            cities = extract_diary_cities(db, diary, extractor)
            cities_str = ", ".join([f"{c['city']}({c['confidence']})" for c in cities])
            print(f"  [OK] 提取城市: {cities_str}")
        else:
            print(f"  [WARN] 未识别到城市")
        
        processed += 1
        
        # 每10篇提交一次，避免内存溢出
        if i % 10 == 0:
            db.commit()
            print(f"\n[SAVE] 已保存 {i} 篇日记的处理结果")
    
    # 最终提交
    db.commit()
    
    print("\n" + "=" * 60)
    print(f"[OK] 处理完成!")
    print(f"   总日记数: {total}")
    print(f"   成功提取: {extracted}")
    print(f"   未识别: {total - extracted}")
    
    # 统计城市分布
    cities = db.query(DiaryCity).order_by(DiaryCity.diary_count.desc()).all()
    if cities:
        print(f"\n[STAT] 城市统计（共 {len(cities)} 个城市）:")
        for city in cities[:10]:  # 显示前10个
            print(f"   {city.name}: {city.diary_count} 篇")


def main():
    parser = argparse.ArgumentParser(description='批量提取日记城市标签')
    parser.add_argument('--skip-existing', action='store_true', 
                       help='跳过已处理的日记（默认）')
    parser.add_argument('--force', action='store_true',
                       help='强制重新处理所有日记')
    parser.add_argument('--limit', type=int, default=None,
                       help='限制处理数量（用于测试）')
    
    args = parser.parse_args()
    
    skip_existing = not args.force
    
    print("[INFO] 日记城市标签批量提取工具")
    print("=" * 60)
    
    # 获取数据库会话
    db = next(get_db())
    
    try:
        batch_process(db, skip_existing=skip_existing, limit=args.limit)
    except Exception as e:
        print(f"\n[ERROR] 错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()
