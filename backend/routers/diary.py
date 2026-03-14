"""
旅游日记API - 支持压缩存储和全文搜索
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from pydantic import BaseModel
import sys
sys.path.append("..")

from models.database import get_db, TravelDiary, DiaryRating, User
from algorithms.core import compress_diary, decompress_diary

router = APIRouter()


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


class DiaryResponse(BaseModel):
    id: int
    title: str
    content: Optional[str] = None
    images: List[str] = []
    videos: List[str] = []
    view_count: int = 0
    avg_rating: float = 0
    rating_count: int = 0
    created_at: str

    class Config:
        from_attributes = True


class RateDiaryRequest(BaseModel):
    rating: int  # 1-5


# 路由实现

@router.post("/", response_model=DiaryResponse)
def create_diary(
    request: CreateDiaryRequest,
    user_id: int = Query(1, description="用户ID"),
    db: Session = Depends(get_db)
):
    """创建旅游日记"""
    compression_algorithm = None
    content_compressed = None
    
    if request.compress and request.content:
        # 压缩内容
        content_data = {"content": request.content}
        content_compressed = compress_diary(content_data)
        compression_algorithm = "gzip"
    
    diary = TravelDiary(
        user_id=user_id,
        trip_id=request.trip_id,
        title=request.title,
        content=request.content if not request.compress else None,
        content_compressed=content_compressed,
        compression_algorithm=compression_algorithm,
        images=request.images,
        videos=request.videos
    )
    db.add(diary)
    db.commit()
    db.refresh(diary)
    
    return diary


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
            "likes": diary.avg_rating * 100,
            "rating": round(diary.avg_rating, 1) if diary.avg_rating else 0
        })
    
    return result


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
        # 解压内容（如果需要显示）
        content = diary.content
        if diary.content_compressed and not content:
            try:
                content = decompress_diary(diary.content_compressed).get('content', '')
            except:
                content = ''
        
        result.append({
            'id': diary.id,
            'title': diary.title,
            'content': content,
            'images': diary.images or [],
            'videos': diary.videos or [],
            'view_count': diary.view_count,
            'avg_rating': diary.avg_rating,
            'rating_count': diary.rating_count,
            'created_at': diary.created_at
        })
    
    return result


@router.get("/search")
def search_diaries(
    q: str = Query(..., description="搜索关键词"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """全文搜索日记"""
    # 简单实现：标题和内容模糊匹配
    query = db.query(TravelDiary).filter(
        or_(
            TravelDiary.title.contains(q),
            TravelDiary.content.contains(q)
        ),
        TravelDiary.status == 'published'
    )
    
    total = query.count()
    offset = (page - 1) * page_size
    diaries = query.offset(offset).limit(page_size).all()
    
    return {
        "total": total,
        "diaries": [{
            'id': d.id,
            'title': d.title,
            'view_count': d.view_count,
            'avg_rating': d.avg_rating,
            'created_at': d.created_at
        } for d in diaries]
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
    
    # 解压内容
    content = diary.content
    if diary.content_compressed and not content:
        try:
            content = decompress_diary(diary.content_compressed).get('content', '')
        except:
            content = ''
    
    return {
        'id': diary.id,
        'title': diary.title,
        'content': content,
        'images': diary.images or [],
        'videos': diary.videos or [],
        'view_count': diary.view_count,
        'avg_rating': diary.avg_rating,
        'rating_count': diary.rating_count,
        'created_at': diary.created_at
    }


@router.post("/{diary_id}/rate")
def rate_diary(
    diary_id: int,
    request: RateDiaryRequest,
    user_id: int = Query(1, description="用户ID"),
    db: Session = Depends(get_db)
):
    """为日记评分"""
    diary = db.query(TravelDiary).filter(TravelDiary.id == diary_id).first()
    if not diary:
        return {"error": "日记不存在"}
    
    # 检查是否已评分
    existing = db.query(DiaryRating).filter(
        DiaryRating.diary_id == diary_id,
        DiaryRating.user_id == user_id
    ).first()
    
    if existing:
        # 更新评分
        old_rating = existing.rating
        existing.rating = request.rating
        # 重新计算平均分
        diary.avg_rating = (diary.avg_rating * diary.rating_count - old_rating + request.rating) / diary.rating_count
    else:
        # 新增评分
        rating = DiaryRating(
            diary_id=diary_id,
            user_id=user_id,
            rating=request.rating
        )
        db.add(rating)
        diary.rating_count += 1
        diary.avg_rating = (diary.avg_rating * (diary.rating_count - 1) + request.rating) / diary.rating_count
    
    db.commit()
    
    return {
        "success": True,
        "avg_rating": diary.avg_rating,
        "rating_count": diary.rating_count
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
        db.delete(diary)
        db.commit()
        return {"success": True}
    
    return {"error": "日记不存在或无权限"}
