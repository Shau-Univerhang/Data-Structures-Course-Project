"""
旅游日记API - 支持压缩存储和全文搜索
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import sys
sys.path.append("..")

from models.database import get_db, TravelDiary, DiaryRating, DiaryComment, User
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
    itinerary: Optional[List[dict]] = None  # 时间轴数据
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
    username: str
    parent_id: Optional[int]
    content: str
    like_count: int
    is_deleted: bool
    created_at: str
    replies: List[dict] = []

    class Config:
        from_attributes = True


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
        diary_type=request.diary_type,
        is_public=request.is_public,
        images=request.images,
        videos=request.videos,
        itinerary=request.itinerary,
        budget=request.budget,
        companion=request.companion
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
            'diary_type': diary.diary_type,
            'is_public': diary.is_public,
            'itinerary': diary.itinerary or [],
            'budget': diary.budget,
            'companion': diary.companion,
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
        'diary_type': diary.diary_type,
        'is_public': diary.is_public,
        'itinerary': diary.itinerary or [],
        'budget': diary.budget,
        'companion': diary.companion,
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
    
    # 更新字段
    diary.title = request.title
    diary.diary_type = request.diary_type
    diary.images = request.images
    diary.videos = request.videos
    diary.itinerary = request.itinerary
    diary.budget = request.budget
    diary.companion = request.companion
    
    # 处理内容
    if request.compress and request.content:
        content_data = {"content": request.content}
        diary.content_compressed = compress_diary(content_data)
        diary.compression_algorithm = "gzip"
        diary.content = None
    else:
        diary.content = request.content
        diary.content_compressed = None
        diary.compression_algorithm = None
    
    diary.updated_at = datetime.now().isoformat()
    db.commit()
    db.refresh(diary)
    
    return {
        "id": diary.id,
        "title": diary.title,
        "diary_type": diary.diary_type,
        "images": diary.images or [],
        "itinerary": diary.itinerary or [],
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
    # 获取所有评论
    all_comments = db.query(DiaryComment, User.username).join(
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
            'username': username,
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
