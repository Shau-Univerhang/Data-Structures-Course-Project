"""
旅游日记API - 支持压缩存储和全文搜索
"""
import os
import uuid
import hashlib
import unicodedata
import re
from fastapi import APIRouter, Depends, Query, UploadFile, File
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import sys
sys.path.append("..")

from models.database import get_db, TravelDiary, DiaryRating, DiaryComment, User, DiaryCity, DiaryCityTag
from utils.city_extractor import CityExtractor, get_extractor
from algorithms.core import compress_diary, decompress_diary
from utils.video_compressor import compress_video as compress_video_file
from utils.diary_fts import (
    normalize_title, compute_title_hash, extract_plain_text,
    extract_city_text, extract_tag_text,
    insert_diary_to_fts, update_diary_fts, delete_diary_from_fts,
    search_diaries_fts, search_by_exact_title
)

router = APIRouter()

# 视频存储目录（与 main.py 静态文件挂载目录一致）
VIDEO_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "videos"
)
os.makedirs(VIDEO_DIR, exist_ok=True)

# 允许的视频格式
ALLOWED_VIDEO_EXTENSIONS = {'.mp4', '.mov', '.avi', '.webm', '.mkv'}
# 最大视频大小: 100MB
MAX_VIDEO_SIZE = 100 * 1024 * 1024


# ============================================
# 工具函数
# ============================================

def get_or_create_city(db: Session, city_name: str) -> DiaryCity:
    """获取或创建城市标签"""
    extractor = get_extractor()
    
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
    return new_city


# Pydantic模型
class CreateDiaryRequest(BaseModel):
    title: str
    content: str
    trip_id: Optional[int] = None
    images: List[str] = []
    videos: List[str] = []
    compress: bool = True
    diary_type: Optional[str] = "travel"
    is_public: Optional[bool] = False
    itinerary: Optional[List[dict]] = None  # 时间轴数据
    destination: Optional[str] = None  # 目的地城市（优先于文本提取）
    budget: Optional[str] = None  # 预算
    companion: Optional[str] = None  # 同行伙伴


class DiaryResponse(BaseModel):
    id: int
    title: str
    content: Optional[str] = None
    images: List[str] = []
    videos: List[str] = []
    diary_type: Optional[str] = None
    is_public: Optional[bool] = None
    itinerary: Optional[List[dict]] = None  # 时间轴数据
    budget: Optional[str] = None  # 预算
    companion: Optional[str] = None  # 同行伙伴
    view_count: int = 0
    avg_rating: float = 0
    rating_count: int = 0
    created_at: str

    class Config:
        from_attributes = True


class RateDiaryRequest(BaseModel):
    rating: int  # 1-5


class CreateCommentRequest(BaseModel):
    content: str
    parent_id: Optional[int] = None


class CommentResponse(BaseModel):
    id: int
    diary_id: int
    user_id: int
    username: Optional[str] = '已注销用户'  # 允许None，默认显示已注销用户
    parent_id: Optional[int] = None
    content: str
    like_count: int
    is_deleted: bool
    user_rating: Optional[int] = 0  # 用户对该日记的评分
    created_at: str
    replies: List[dict] = []

    class Config:
        from_attributes = True


# 路由实现

def _sync_diary_city_tags(db: Session, diary: TravelDiary, content: str, itinerary=None, destination=None):
    """同步日记的城市标签"""
    try:
        # 先删除旧关联并递减计数
        old_tags = db.query(DiaryCityTag).filter_by(diary_id=diary.id).all()
        for tag in old_tags:
            city = db.query(DiaryCity).filter_by(id=tag.city_id).first()
            if city and city.diary_count > 0:
                city.diary_count -= 1
            db.delete(tag)
        db.flush()

        cities = []
        extractor = get_extractor()

        # 优先使用明确指定的目的地
        if destination and destination.strip():
            # 解析为标准城市名（处理别名）
            city_name = extractor.resolve_alias(destination.strip())
            cities = [{"city": city_name, "confidence": 1.0}]
        else:
            # 回退到文本提取
            itin = itinerary if itinerary is not None else diary.itinerary
            cities = extractor.extract_cities(
                title=diary.title,
                content=content,
                itinerary=itin
            )
        
        for city_data in cities:
            city_name = city_data['city']
            confidence = city_data['confidence']
            
            # 获取或创建城市
            city = get_or_create_city(db, city_name)
            
            # 创建新关联
            tag = DiaryCityTag(
                diary_id=diary.id,
                city_id=city.id,
                confidence=confidence
            )
            db.add(tag)
            
            # 更新城市计数
            city.diary_count += 1
        
        db.commit()
    except Exception as e:
        print(f"城市标签同步失败: {e}")
        db.rollback()

@router.post("/", response_model=DiaryResponse)
def create_diary(
    request: CreateDiaryRequest,
    user_id: int = Query(1, description="用户ID"),
    db: Session = Depends(get_db)
):
    """创建旅游日记"""
    # 1. 先提取检索特征（在压缩之前！避免压缩后 content 被清空导致搜索不到）
    normalized = normalize_title(request.title)
    title_hash = compute_title_hash(request.title)
    content_plain = extract_plain_text(request.content)
    
    # 2. 提取城市标签（优先使用明确指定的 destination）
    if request.destination and request.destination.strip():
        extractor = get_extractor()
        city_name = extractor.resolve_alias(request.destination.strip())
        cities = [{"city": city_name, "confidence": 1.0}]
    else:
        cities = get_extractor().extract_cities(
            title=request.title,
            content=request.content,
            itinerary=request.itinerary
        )
    city_text = extract_city_text([c['city'] for c in cities])
    tag_text = extract_tag_text(request.diary_type, request.companion, request.budget)
    
    # 3. 压缩处理
    compression_algorithm = None
    content_compressed = None
    
    if request.compress and (request.content or request.itinerary):
        data_to_compress = {}
        if request.content:
            data_to_compress["content"] = request.content
        if request.itinerary:
            data_to_compress["itinerary"] = request.itinerary
        content_compressed = compress_diary(data_to_compress)
        compression_algorithm = "gzip"
    
    # 4. 写入数据库
    diary = TravelDiary(
        user_id=user_id,
        trip_id=request.trip_id,
        title=request.title,
        normalized_title=normalized,
        title_hash=title_hash,
        content=request.content if not request.compress else None,
        content_plain=content_plain,  # 保留纯文本用于检索
        content_compressed=content_compressed,
        compression_algorithm=compression_algorithm,
        diary_type=request.diary_type,
        is_public=request.is_public,
        images=request.images,
        videos=request.videos,
        itinerary=request.itinerary if not request.compress else None,
        destination=request.destination,
        budget=request.budget,
        companion=request.companion
    )
    db.add(diary)
    db.commit()
    db.refresh(diary)
    
    # 5. 同步城市标签（传入 itinerary 和 destination，避免压缩后 diary.itinerary 为 None）
    _sync_diary_city_tags(db, diary, request.content, request.itinerary, request.destination)
    
    # 6. 写入 FTS5 索引
    insert_diary_to_fts(diary.id, request.title, content_plain, city_text, tag_text)
    
    # 获取用户名
    user = db.query(User).filter(User.id == diary.user_id).first()
    
    return {
        'id': diary.id,
        'title': diary.title,
        'content': diary.content,
        'images': diary.images or [],
        'videos': diary.videos or [],
        'diary_type': diary.diary_type,
        'is_public': diary.is_public,
        'itinerary': diary.itinerary or [],
        'budget': diary.budget,
        'companion': diary.companion,
        'view_count': diary.view_count,
        'avg_rating': diary.avg_rating,
        'rating_count': diary.rating_count,
        'created_at': diary.created_at,
        'username': user.username if user else '匿名用户'
    }

@router.get("/footprints")
def get_user_footprints(
    user_id: int = Query(1, description="用户ID"),
    db: Session = Depends(get_db)
):
    """获取用户的旅行印痕（所有去过的城市及其坐标）"""
    # 查找用户日记关联的所有城市
    footprints = db.query(
        DiaryCity.name,
        DiaryCityTag.confidence,
        TravelDiary.id.label("diary_id"),
        TravelDiary.title.label("diary_title"),
        TravelDiary.images.label("diary_images"),
        TravelDiary.created_at
    ).join(
        DiaryCityTag, DiaryCity.id == DiaryCityTag.city_id
    ).join(
        TravelDiary, TravelDiary.id == DiaryCityTag.diary_id
    ).filter(
        TravelDiary.user_id == user_id
    ).all()

    # 按城市分组
    city_map = {}
    for f in footprints:
        if f.name not in city_map:
            city_map[f.name] = {
                "name": f.name,
                "diaries": []
            }
        
        city_map[f.name]["diaries"].append({
            "id": f.diary_id,
            "title": f.diary_title,
            "cover": f.diary_images[0] if f.diary_images else "",
            "created_at": f.created_at
        })
    
    return list(city_map.values())


@router.get("/public", response_model=List[dict])
def get_public_diaries(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """获取公开的精选日记（用于展示）"""
    diaries = db.query(TravelDiary).filter(
        TravelDiary.status == 'published',
        TravelDiary.is_public == True
    ).order_by(TravelDiary.avg_rating.desc(), TravelDiary.view_count.desc()).offset((page-1)*page_size).limit(page_size).all()
    
    result = []
    for diary in diaries:
        user = db.query(User).filter(User.id == diary.user_id).first()
        result.append({
            "id": diary.id,
            "title": diary.title,
            "cover": diary.images[0] if diary.images else None,
            "author": user.username if user else "匿名用户",
            "rating": round(diary.avg_rating, 1) if diary.avg_rating else 0
        })
    
    return result


# ============================================
# 日记库功能（必须放在 / 和 /{diary_id} 之前）
# ============================================

@router.get("/explore/cities")
def get_cities(
    min_count: int = Query(1, ge=0, description="最小日记数量"),
    db: Session = Depends(get_db)
):
    """获取日记城市列表"""
    cities = db.query(DiaryCity).filter(
        DiaryCity.diary_count >= min_count
    ).order_by(DiaryCity.diary_count.desc()).all()
    
    # 热门城市（日记数 >= 10）
    hot_cities = [c.name for c in cities if c.diary_count >= 10][:10]
    
    return {
        "cities": [
            {
                "id": c.id,
                "name": c.name,
                "diary_count": c.diary_count
            }
            for c in cities
        ],
        "hot_cities": hot_cities
    }


@router.get("/explore")
def get_diary_library(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=50, description="每页数量"),
    city_id: Optional[int] = Query(None, description="城市ID筛选"),
    diary_type: Optional[str] = Query(None, description="日记类型筛选"),
    sort: str = Query("hot", description="排序方式: hot/new/rating"),
    db: Session = Depends(get_db)
):
    """
    获取日记库列表
    
    支持按城市和类型筛选，支持多种排序方式
    """
    query = db.query(TravelDiary).filter(
        TravelDiary.is_public == True,
        TravelDiary.status == 'published'
    )
    
    # 城市筛选
    if city_id:
        diary_ids = db.query(DiaryCityTag.diary_id).filter(
            DiaryCityTag.city_id == city_id
        ).distinct()
        query = query.filter(TravelDiary.id.in_(diary_ids))
    
    # 类型筛选
    if diary_type:
        query = query.filter(TravelDiary.diary_type == diary_type)
    
    # 排序
    if sort == "new":
        query = query.order_by(TravelDiary.created_at.desc())
    elif sort == "rating":
        query = query.order_by(TravelDiary.avg_rating.desc())
    else:  # hot - 综合热度（浏览量+评分）
        query = query.order_by(
            (TravelDiary.view_count * 0.7 + TravelDiary.avg_rating * TravelDiary.rating_count * 10).desc()
        )
    
    # 分页
    total = query.count()
    offset = (page - 1) * page_size
    diaries = query.offset(offset).limit(page_size).all()
    
    # 构建响应
    result = []
    for diary in diaries:
        # 获取作者信息
        user = db.query(User).filter(User.id == diary.user_id).first()
        
        # 获取城市标签
        city_tags = db.query(DiaryCity).join(
            DiaryCityTag, DiaryCity.id == DiaryCityTag.city_id
        ).filter(DiaryCityTag.diary_id == diary.id).all()
        
        # 获取评论数
        comment_count = db.query(DiaryComment).filter(
            DiaryComment.diary_id == diary.id,
            DiaryComment.is_deleted == False
        ).count()
        
        result.append({
            "id": diary.id,
            "title": diary.title,
            "cover": diary.images[0] if diary.images else None,
            "author": user.username if user else "匿名用户",
            "avatar": user.avatar_url if user else None,
            "type": diary.diary_type,
            "cities": [c.name for c in city_tags],
            "rating": round(diary.avg_rating, 1) if diary.avg_rating else 0,
            "view_count": diary.view_count,
            "comment_count": comment_count,
            "created_at": diary.created_at
        })
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "diaries": result
    }


@router.get("/", response_model=List[DiaryResponse])
def list_diaries(
    user_id: Optional[int] = Query(None, description="用户ID筛选"),
    trip_id: Optional[int] = Query(None, description="行程ID筛选"),
    sort_by: str = Query("created_at", description="排序: created_at/view_count/avg_rating"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """获取日记列表"""
    query = db.query(TravelDiary).filter(TravelDiary.status == 'published')
    
    if user_id:
        query = query.filter(TravelDiary.user_id == user_id)
    if trip_id:
        query = query.filter(TravelDiary.trip_id == trip_id)
    
    # 排序
    if sort_by == 'view_count':
        query = query.order_by(TravelDiary.view_count.desc())
    elif sort_by == 'avg_rating':
        query = query.order_by(TravelDiary.avg_rating.desc())
    else:
        query = query.order_by(TravelDiary.created_at.desc())
    
    offset = (page - 1) * page_size
    diaries = query.offset(offset).limit(page_size).all()
    
    result = []
    for diary in diaries:
        # 解压内容 + 时间轴
        content = diary.content
        itinerary = diary.itinerary
        if diary.content_compressed:
            try:
                decompressed = decompress_diary(diary.content_compressed)
                content = decompressed.get('content', content)
                itinerary = decompressed.get('itinerary', itinerary)
            except:
                pass
        
        # 获取用户名
        user = db.query(User).filter(User.id == diary.user_id).first()
        
        result.append({
            'id': diary.id,
            'title': diary.title,
            'content': content,
            'images': diary.images or [],
            'videos': diary.videos or [],
            'diary_type': diary.diary_type,
            'is_public': diary.is_public,
            'itinerary': itinerary or [],
            'budget': diary.budget,
            'companion': diary.companion,
            'view_count': diary.view_count,
            'avg_rating': diary.avg_rating,
            'rating_count': diary.rating_count,
            'created_at': diary.created_at,
            'username': user.username if user else '匿名用户'
        })
    
    return result


@router.get("/search")
def search_diaries(
    q: str = Query(..., description="搜索关键词"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    sort: str = Query("relevance", description="排序方式: relevance/date/hot"),
    db: Session = Depends(get_db)
):
    """
    全文搜索日记（基于 SQLite FTS5）
    使用 BM25 相关性排序，支持高亮摘要
    """
    # 使用 FTS5 全文检索
    fts_result = search_diaries_fts(q, page=page, page_size=page_size, sort=sort)
    
    # 补充日记详情（作者、封面等）
    enriched_diaries = []
    for d in fts_result.get("diaries", []):
        diary_id = d.get("id") or d.get("rowid")
        diary = db.query(TravelDiary).filter(TravelDiary.id == diary_id).first()
        if not diary:
            continue
        user = db.query(User).filter(User.id == diary.user_id).first()
        city_tags = db.query(DiaryCity).join(
            DiaryCityTag, DiaryCity.id == DiaryCityTag.city_id
        ).filter(DiaryCityTag.diary_id == diary.id).all()
        
        enriched_diaries.append({
            "id": diary.id,
            "title": diary.title,
            "snippet_title": d.get("snippet_title", ""),
            "snippet_content": d.get("snippet_content", ""),
            "author": user.username if user else "匿名用户",
            "cover": diary.images[0] if diary.images else None,
            "cities": [c.name for c in city_tags],
            "view_count": diary.view_count,
            "avg_rating": round(diary.avg_rating, 1) if diary.avg_rating else 0,
            "score": d.get("score", 0),
            "created_at": diary.created_at
        })
    
    return {
        "total": fts_result.get("total", 0),
        "diaries": enriched_diaries,
        "query": q
    }


@router.get("/exact-title")
def search_by_title(
    title: str = Query(..., description="标题关键词"),
    db: Session = Depends(get_db)
):
    """
    标题精确查询
    使用 normalized_title + title_hash 实现接近 O(1) 的精确匹配
    """
    matched_diaries = search_by_exact_title(title)
    
    result = []
    for diary in matched_diaries:
        user = db.query(User).filter(User.id == diary.user_id).first()
        city_tags = db.query(DiaryCity).join(
            DiaryCityTag, DiaryCity.id == DiaryCityTag.city_id
        ).filter(DiaryCityTag.diary_id == diary.id).all()
        
        result.append({
            "id": diary.id,
            "title": diary.title,
            "normalized_title": diary.normalized_title,
            "title_hash": diary.title_hash,
            "author": user.username if user else "匿名用户",
            "cover": diary.images[0] if diary.images else None,
            "cities": [c.name for c in city_tags],
            "view_count": diary.view_count,
            "avg_rating": round(diary.avg_rating, 1) if diary.avg_rating else 0,
            "created_at": diary.created_at
        })
    
    return {
        "total": len(result),
        "diaries": result
    }


@router.get("/by-destination")
def search_by_destination(
    destination: str = Query(..., description="目的地名称"),
    sort: str = Query("hot", description="排序方式: hot/new/rating"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    按目的地搜索日记
    先将输入标准化为城市名，再通过城市标签倒排索引查找
    """
    extractor = get_extractor()
    
    # 标准化目的地名称
    city_name = extractor.resolve_alias(destination)
    
    # 查找城市
    city = db.query(DiaryCity).filter(DiaryCity.name == city_name).first()
    if not city:
        # 尝试模糊匹配
        all_cities = db.query(DiaryCity).all()
        matches = [c for c in all_cities if destination.lower() in c.name.lower()]
        if matches:
            city = matches[0]
        else:
            return {"total": 0, "diaries": [], "message": f"未找到城市: {destination}"}
    
    # 通过城市标签倒排索引查找日记
    diary_ids = db.query(DiaryCityTag.diary_id).filter(
        DiaryCityTag.city_id == city.id
    ).distinct().all()
    diary_ids = [r[0] for r in diary_ids]
    
    if not diary_ids:
        return {"total": 0, "diaries": []}
    
    query = db.query(TravelDiary).filter(
        TravelDiary.id.in_(diary_ids),
        TravelDiary.is_public == True,
        TravelDiary.status == 'published'
    )
    
    # 排序
    if sort == "new":
        query = query.order_by(TravelDiary.created_at.desc())
    elif sort == "rating":
        query = query.order_by(TravelDiary.avg_rating.desc())
    else:
        query = query.order_by(
            (TravelDiary.view_count * 0.7 + TravelDiary.avg_rating * TravelDiary.rating_count * 10).desc()
        )
    
    total = query.count()
    offset = (page - 1) * page_size
    diaries = query.offset(offset).limit(page_size).all()
    
    result = []
    for diary in diaries:
        user = db.query(User).filter(User.id == diary.user_id).first()
        result.append({
            "id": diary.id,
            "title": diary.title,
            "cover": diary.images[0] if diary.images else None,
            "author": user.username if user else "匿名用户",
            "cities": [city.name],
            "rating": round(diary.avg_rating, 1) if diary.avg_rating else 0,
            "view_count": diary.view_count,
            "created_at": diary.created_at
        })
    
    return {
        "total": total,
        "city": city.name,
        "diaries": result
    }


@router.get("/{diary_id}", response_model=DiaryResponse)
def get_diary(
    diary_id: int,
    db: Session = Depends(get_db)
):
    """获取日记详情"""
    diary = db.query(TravelDiary).filter(TravelDiary.id == diary_id).first()
    if not diary:
        return {"error": "日记不存在"}
    
    # 增加浏览量
    diary.view_count += 1
    db.commit()
    
    # 解压内容和时间轴
    content = diary.content
    itinerary = diary.itinerary
    if diary.content_compressed:
        try:
            decompressed = decompress_diary(diary.content_compressed)
            content = decompressed.get('content', content)
            itinerary = decompressed.get('itinerary', itinerary)
        except:
            pass
    
    # 获取用户名
    user = db.query(User).filter(User.id == diary.user_id).first()
    
    return {
        'id': diary.id,
        'title': diary.title,
        'content': content,
        'images': diary.images or [],
        'videos': diary.videos or [],
        'diary_type': diary.diary_type,
        'is_public': diary.is_public,
        'itinerary': itinerary or [],
        'budget': diary.budget,
        'companion': diary.companion,
        'view_count': diary.view_count,
        'avg_rating': diary.avg_rating,
        'rating_count': diary.rating_count,
        'created_at': diary.created_at,
        'username': user.username if user else '匿名用户'
    }


@router.post("/{diary_id}/rate")
def rate_diary(
    diary_id: int,
    request: RateDiaryRequest,
    user_id: int = Query(1, description="用户ID"),
    db: Session = Depends(get_db)
):
    """为日记评分（统一接口，委托给 /rating 逻辑）"""
    diary = db.query(TravelDiary).filter(TravelDiary.id == diary_id).first()
    if not diary:
        return {"error": "日记不存在"}
    
    # 检查是否已评分
    existing = db.query(DiaryRating).filter(
        DiaryRating.diary_id == diary_id,
        DiaryRating.user_id == user_id
    ).first()
    
    if existing:
        existing.rating = request.rating
    else:
        new_rating = DiaryRating(
            diary_id=diary_id,
            user_id=user_id,
            rating=request.rating
        )
        db.add(new_rating)
    
    db.commit()
    
    # 重新计算平均评分（从所有评分记录计算，保证准确性）
    all_ratings = db.query(DiaryRating).filter(DiaryRating.diary_id == diary_id).all()
    avg_rating = sum(r.rating for r in all_ratings) / len(all_ratings) if all_ratings else 0
    
    diary.avg_rating = round(avg_rating, 1)
    diary.rating_count = len(all_ratings)
    db.commit()
    
    return {
        "success": True,
        "avg_rating": diary.avg_rating,
        "rating_count": diary.rating_count
    }


@router.put("/{diary_id}")
def update_diary(
    diary_id: int,
    request: CreateDiaryRequest,
    user_id: int = Query(1, description="用户ID"),
    db: Session = Depends(get_db)
):
    """更新日记"""
    diary = db.query(TravelDiary).filter(
        TravelDiary.id == diary_id,
        TravelDiary.user_id == user_id
    ).first()
    
    if not diary:
        return {"error": "日记不存在或无权限"}
    
    # 更新基础字段
    diary.title = request.title
    diary.normalized_title = normalize_title(request.title)
    diary.title_hash = compute_title_hash(request.title)
    diary.diary_type = request.diary_type
    diary.images = request.images
    diary.videos = request.videos
    diary.budget = request.budget
    diary.companion = request.companion
    diary.destination = request.destination
    
    # 处理内容压缩（合并 content + itinerary）
    # 关键：先提取检索特征，再压缩
    content_plain = extract_plain_text(request.content)
    diary.content_plain = content_plain
    
    if request.destination and request.destination.strip():
        extractor = get_extractor()
        city_name = extractor.resolve_alias(request.destination.strip())
        cities = [{"city": city_name, "confidence": 1.0}]
    else:
        cities = get_extractor().extract_cities(
            title=request.title,
            content=request.content,
            itinerary=request.itinerary
        )
    city_text = extract_city_text([c['city'] for c in cities])
    tag_text = extract_tag_text(request.diary_type, request.companion, request.budget)
    
    if request.compress and (request.content or request.itinerary):
        data_to_compress = {}
        if request.content:
            data_to_compress["content"] = request.content
        if request.itinerary:
            data_to_compress["itinerary"] = request.itinerary
        diary.content_compressed = compress_diary(data_to_compress)
        diary.compression_algorithm = "gzip"
        diary.content = None
        diary.itinerary = None
    else:
        diary.content = request.content
        diary.itinerary = request.itinerary
        diary.content_compressed = None
        diary.compression_algorithm = None
    
    diary.updated_at = datetime.now().isoformat()
    db.commit()
    db.refresh(diary)
    
    # 同步城市标签（传入 itinerary 和 destination）
    _sync_diary_city_tags(db, diary, request.content, request.itinerary, request.destination)
    
    # 更新 FTS5 索引
    update_diary_fts(diary.id, request.title, content_plain, city_text, tag_text)
    
    return {
        "id": diary.id,
        "title": diary.title,
        "diary_type": diary.diary_type,
        "images": diary.images or [],
        "itinerary": request.itinerary or [],
        "budget": diary.budget,
        "companion": diary.companion,
        "updated_at": diary.updated_at
    }


@router.delete("/{diary_id}")
def delete_diary(
    diary_id: int,
    user_id: int = Query(1, description="用户ID"),
    db: Session = Depends(get_db)
):
    """删除日记"""
    diary = db.query(TravelDiary).filter(
        TravelDiary.id == diary_id,
        TravelDiary.user_id == user_id
    ).first()
    
    if diary:
        # 删除关联的视频文件
        if diary.videos:
            import json
            video_files = []
            if isinstance(diary.videos, str):
                try:
                    video_files = json.loads(diary.videos)
                except:
                    pass
            elif isinstance(diary.videos, list):
                video_files = diary.videos
            
            for video_path in video_files:
                if isinstance(video_path, str) and video_path.startswith('/videos/'):
                    filename = os.path.basename(video_path)
                    filepath = os.path.join(VIDEO_DIR, filename)
                    if os.path.exists(filepath):
                        try:
                            os.remove(filepath)
                        except Exception as e:
                            print(f"删除视频文件失败 {filename}: {e}")
        
        # 删除 FTS 索引
        delete_diary_from_fts(diary_id)
        
        # 处理城市计数
        tags = db.query(DiaryCityTag).filter_by(diary_id=diary.id).all()
        for tag in tags:
            city = db.query(DiaryCity).filter_by(id=tag.city_id).first()
            if city and city.diary_count > 0:
                city.diary_count -= 1
        
        db.delete(diary)
        db.commit()
        return {"success": True}
    
    return {"error": "日记不存在或无权限"}


# ========== 评论相关API ==========

@router.get("/{diary_id}/comments", response_model=List[CommentResponse])
def get_comments(
    diary_id: int,
    db: Session = Depends(get_db)
):
    """获取日记的评论列表（包括回复）"""
    # 获取所有评论（使用 outerjoin 保留所有评论，即使用户不存在）
    all_comments = db.query(DiaryComment, User.username).outerjoin(
        User, DiaryComment.user_id == User.id
    ).filter(
        DiaryComment.diary_id == diary_id
    ).order_by(DiaryComment.created_at.desc()).all()
    
    # 获取所有评论用户的评分信息
    user_ids = [comment.user_id for comment, _ in all_comments]
    user_ratings = {}
    if user_ids:
        ratings = db.query(DiaryRating).filter(
            DiaryRating.diary_id == diary_id,
            DiaryRating.user_id.in_(user_ids)
        ).all()
        user_ratings = {r.user_id: r.rating for r in ratings}
    
    # 分离主评论和回复
    main_comments = []
    replies_map = {}
    
    for comment, username in all_comments:
        comment_data = {
            'id': comment.id,
            'diary_id': comment.diary_id,
            'user_id': comment.user_id,
            'username': username if username else '已注销用户',
            'parent_id': comment.parent_id,
            'content': comment.content if not comment.is_deleted else '该评论已删除',
            'like_count': comment.like_count,
            'is_deleted': comment.is_deleted,
            'user_rating': user_ratings.get(comment.user_id, 0),  # 用户对该日记的评分
            'created_at': comment.created_at,
            'replies': []
        }
        
        if comment.parent_id is None:
            main_comments.append(comment_data)
        else:
            if comment.parent_id not in replies_map:
                replies_map[comment.parent_id] = []
            replies_map[comment.parent_id].append(comment_data)
    
    # 将回复关联到主评论
    for comment in main_comments:
        if comment['id'] in replies_map:
            comment['replies'] = replies_map[comment['id']]
    
    return main_comments


@router.post("/{diary_id}/comments", response_model=CommentResponse)
def create_comment(
    diary_id: int,
    request: CreateCommentRequest,
    user_id: int = Query(..., description="用户ID"),
    db: Session = Depends(get_db)
):
    """发表评论或回复"""
    # 检查日记是否存在
    diary = db.query(TravelDiary).filter(TravelDiary.id == diary_id).first()
    if not diary:
        return {"error": "日记不存在"}
    
    # 检查父评论是否存在（如果是回复）
    if request.parent_id:
        parent = db.query(DiaryComment).filter(DiaryComment.id == request.parent_id).first()
        if not parent:
            return {"error": "回复的评论不存在"}
    
    # 创建评论
    comment = DiaryComment(
        diary_id=diary_id,
        user_id=user_id,
        parent_id=request.parent_id,
        content=request.content
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    
    # 获取用户名
    user = db.query(User).filter(User.id == user_id).first()
    
    return {
        'id': comment.id,
        'diary_id': comment.diary_id,
        'user_id': comment.user_id,
        'username': user.username if user else '匿名用户',
        'parent_id': comment.parent_id,
        'content': comment.content,
        'like_count': comment.like_count,
        'is_deleted': comment.is_deleted,
        'user_rating': 0,  # 新评论默认没有评分
        'created_at': comment.created_at,
        'replies': []
    }


@router.delete("/{diary_id}/comments/{comment_id}")
def delete_comment(
    diary_id: int,
    comment_id: int,
    user_id: int = Query(..., description="用户ID"),
    db: Session = Depends(get_db)
):
    """删除评论（软删除）"""
    comment = db.query(DiaryComment).filter(
        DiaryComment.id == comment_id,
        DiaryComment.diary_id == diary_id,
        DiaryComment.user_id == user_id
    ).first()
    
    if not comment:
        return {"error": "评论不存在或无权限"}
    
    # 软删除
    comment.is_deleted = True
    db.commit()
    
    return {"success": True}


@router.post("/{diary_id}/comments/{comment_id}/like")
def like_comment(
    diary_id: int,
    comment_id: int,
    db: Session = Depends(get_db)
):
    """点赞评论"""
    comment = db.query(DiaryComment).filter(
        DiaryComment.id == comment_id,
        DiaryComment.diary_id == diary_id
    ).first()
    
    if not comment:
        return {"error": "评论不存在"}
    
    comment.like_count += 1
    db.commit()
    
    return {"success": True, "like_count": comment.like_count}


# ========== 评分查询API ==========

@router.get("/{diary_id}/rating")
def get_diary_rating(
    diary_id: int,
    user_id: Optional[int] = Query(None, description="用户ID"),
    db: Session = Depends(get_db)
):
    """获取日记的评分信息"""
    diary = db.query(TravelDiary).filter(TravelDiary.id == diary_id).first()
    if not diary:
        return {"error": "日记不存在"}
    
    result = {
        "avg_rating": diary.avg_rating,
        "rating_count": diary.rating_count
    }
    
    # 如果提供了用户ID，查询该用户的评分
    if user_id:
        user_rating = db.query(DiaryRating).filter(
            DiaryRating.diary_id == diary_id,
            DiaryRating.user_id == user_id
        ).first()
        result["user_rating"] = user_rating.rating if user_rating else 0
    
    return result


@router.post("/{diary_id}/rating")
def rate_diary(
    diary_id: int,
    request: RateDiaryRequest,
    user_id: int = Query(..., description="用户ID"),
    db: Session = Depends(get_db)
):
    """为日记评分"""
    # 检查日记是否存在
    diary = db.query(TravelDiary).filter(TravelDiary.id == diary_id).first()
    if not diary:
        return {"error": "日记不存在"}
    
    # 检查用户是否已经评分
    existing_rating = db.query(DiaryRating).filter(
        DiaryRating.diary_id == diary_id,
        DiaryRating.user_id == user_id
    ).first()
    
    if existing_rating:
        # 更新已有评分
        existing_rating.rating = request.rating
    else:
        # 创建新评分
        new_rating = DiaryRating(
            diary_id=diary_id,
            user_id=user_id,
            rating=request.rating
        )
        db.add(new_rating)
    
    db.commit()
    
    # 重新计算平均评分
    all_ratings = db.query(DiaryRating).filter(DiaryRating.diary_id == diary_id).all()
    avg_rating = sum(r.rating for r in all_ratings) / len(all_ratings) if all_ratings else 0
    
    # 更新日记的评分信息
    diary.avg_rating = round(avg_rating, 1)
    diary.rating_count = len(all_ratings)
    db.commit()
    
    return {
        "success": True,
        "avg_rating": diary.avg_rating,
        "rating_count": diary.rating_count
    }


# ========== 视频上传相关API ==========

@router.post("/upload-video")
async def upload_video(
    file: UploadFile = File(...),
    user_id: int = Query(..., description="用户ID"),
    compress: bool = Query(True, description="是否启用视频压缩")
):
    """
    上传视频文件并自动压缩（H.265 转码）
    
    Args:
        file: 视频文件
        user_id: 用户ID
        compress: 是否启用压缩（默认 True）
    
    Returns:
        视频URL、文件大小、压缩信息
    """
    # 检查文件大小
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > MAX_VIDEO_SIZE:
        return JSONResponse(
            status_code=400,
            content={"error": f"视频文件过大，最大支持 {MAX_VIDEO_SIZE // 1024 // 1024}MB"}
        )
    
    # 检查文件扩展名
    ext = os.path.splitext(file.filename)[1].lower() if file.filename else ''
    if ext not in ALLOWED_VIDEO_EXTENSIONS:
        return JSONResponse(
            status_code=400,
            content={"error": f"不支持的视频格式，仅支持: {', '.join(ALLOWED_VIDEO_EXTENSIONS)}"}
        )
    
    # 生成唯一文件名
    original_filename = f"video_{user_id}_{uuid.uuid4().hex}{ext}"
    original_filepath = os.path.join(VIDEO_DIR, original_filename)
    
    # 保存原始文件
    content = await file.read()
    with open(original_filepath, 'wb') as f:
        f.write(content)
    
    # 视频压缩处理
    compression_info = None
    final_filename = original_filename
    
    if compress and ext == '.mp4':
        # 只有 mp4 格式直接压缩，其他格式先转 mp4 再压缩
        try:
            result = compress_video_file(original_filepath, VIDEO_DIR)
            
            if result.success:
                # 压缩成功，替换原文件
                compressed_path = result.output_path
                final_filename = os.path.basename(compressed_path)
                
                # 删除原文件（节省空间）
                if os.path.exists(original_filepath):
                    os.remove(original_filepath)
                
                compression_info = {
                    "original_size": result.original_size,
                    "compressed_size": result.compressed_size,
                    "compression_ratio": result.compression_ratio,
                    "encoding_time": result.duration_seconds
                }
            else:
                # 压缩失败，保留原文件
                compression_info = {
                    "error": result.error,
                    "fallback": True
                }
        except Exception as e:
            # 压缩异常，保留原文件
            compression_info = {
                "error": str(e),
                "fallback": True
            }
    
    # 返回视频URL
    video_url = f"/videos/{final_filename}"
    response_data = {
        "success": True,
        "video_url": video_url,
        "filename": final_filename,
        "size": os.path.getsize(os.path.join(VIDEO_DIR, final_filename)),
        "compression": compression_info
    }
    
    return response_data


# ========== AIGC 动画生成API ==========

@router.post("/{diary_id}/generate-animation")
def generate_diary_animation(
    diary_id: int,
    user_id: int = Query(..., description="用户ID"),
    prompt: str = Query("", description="自定义动画提示词（可选）"),
    db: Session = Depends(get_db)
):
    """
    根据日记图片生成旅游动画视频（AIGC）
    
    流程：
    1. 获取日记的第一张图片
    2. 使用智谱 CogVideo 图生视频 API
    3. 生成 5-6 秒旅游动画
    4. 回写 ai_animation_url 到日记
    
    Returns:
        动画视频 URL 和状态
    """
    from services.aigc_animation import image_to_video
    
    # 检查日记是否存在
    diary = db.query(TravelDiary).filter(
        TravelDiary.id == diary_id,
        TravelDiary.user_id == user_id
    ).first()
    
    if not diary:
        return {"error": "日记不存在或无权限"}
    
    # 获取日记图片
    images = diary.images or []
    if not images:
        return {"error": "日记没有图片，无法生成动画"}
    
    # 取第一张图片。优先保留原始存储路径，服务层会自行处理本地路径或远程 URL。
    first_image = images[0]
    image_source = first_image if first_image.startswith("http") else first_image.lstrip("/\\")

    print(f"[AIGC] 开始为日记 {diary_id} 生成动画，图片来源: {image_source}")
    
    # 调用 AIGC 服务生成视频（同步调用，可能需要 1-2 分钟）
    result = image_to_video(image_source, prompt=prompt)
    
    if result["status"] == "success":
        # 回写动画 URL 到日记
        diary.ai_animation_url = result["video_url"]
        db.commit()
        
        return {
            "success": True,
            "animation_url": result["video_url"],
            "task_id": result["task_id"],
            "message": result["message"]
        }
    else:
        return {
            "success": False,
            "message": result["message"]
        }


@router.get("/{diary_id}/animation-status")
def get_animation_status(
    diary_id: int,
    user_id: int = Query(..., description="用户ID"),
    db: Session = Depends(get_db)
):
    """查询日记动画生成状态"""
    diary = db.query(TravelDiary).filter(
        TravelDiary.id == diary_id,
        TravelDiary.user_id == user_id
    ).first()
    
    if not diary:
        return {"error": "日记不存在或无权限"}
    
    return {
        "has_animation": bool(diary.ai_animation_url),
        "animation_url": diary.ai_animation_url
    }
