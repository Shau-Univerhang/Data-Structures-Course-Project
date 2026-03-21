"""
日记评论和评分 API
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.database import get_db, DiaryComment, DiaryRating, TravelDiary, User

router = APIRouter()


# ==================== Pydantic 模型 ====================

class CommentCreate(BaseModel):
    content: str
    parent_id: Optional[int] = None


class CommentResponse(BaseModel):
    id: int
    diary_id: int
    user_id: int
    username: str
    parent_id: Optional[int] = None
    content: str
    like_count: int
    is_deleted: bool
    created_at: str
    updated_at: str
    replies: List['CommentResponse'] = []


class RatingCreate(BaseModel):
    rating: int  # 1-5


class RatingResponse(BaseModel):
    diary_id: int
    user_id: int
    rating: int
    avg_rating: float
    rating_count: int


# ==================== 评论 API ====================

@router.get("/diaries/{diary_id}/comments", response_model=List[CommentResponse])
def get_comments(diary_id: int, db: Session = Depends(get_db)):
    """获取日记的所有评论（包括回复）"""
    # 检查日记是否存在
    diary = db.query(TravelDiary).filter(TravelDiary.id == diary_id).first()
    if not diary:
        raise HTTPException(status_code=404, detail="日记不存在")
    
    # 获取所有顶级评论（parent_id 为 None）
    top_level_comments = db.query(DiaryComment).filter(
        DiaryComment.diary_id == diary_id,
        DiaryComment.parent_id == None,
        DiaryComment.is_deleted == False
    ).order_by(DiaryComment.created_at.desc()).all()
    
    # 构建评论树
    def build_comment_tree(comment):
        user = db.query(User).filter(User.id == comment.user_id).first()
        username = user.username if user else "已注销用户"
        
        comment_data = CommentResponse(
            id=comment.id,
            diary_id=comment.diary_id,
            user_id=comment.user_id,
            username=username,
            parent_id=comment.parent_id,
            content=comment.content,
            like_count=comment.like_count,
            is_deleted=comment.is_deleted,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
            replies=[]
        )
        
        # 获取回复
        replies = db.query(DiaryComment).filter(
            DiaryComment.parent_id == comment.id,
            DiaryComment.is_deleted == False
        ).order_by(DiaryComment.created_at.asc()).all()
        
        for reply in replies:
            comment_data.replies.append(build_comment_tree(reply))
        
        return comment_data
    
    return [build_comment_tree(comment) for comment in top_level_comments]


@router.post("/diaries/{diary_id}/comments", response_model=CommentResponse)
def create_comment(
    diary_id: int,
    comment_data: CommentCreate,
    user_id: int = Query(..., description="用户 ID"),
    db: Session = Depends(get_db)
):
    """创建评论或回复"""
    # 检查日记是否存在
    diary = db.query(TravelDiary).filter(TravelDiary.id == diary_id).first()
    if not diary:
        raise HTTPException(status_code=404, detail="日记不存在")
    
    # 如果是回复，检查父评论是否存在
    if comment_data.parent_id:
        parent_comment = db.query(DiaryComment).filter(
            DiaryComment.id == comment_data.parent_id,
            DiaryComment.diary_id == diary_id
        ).first()
        if not parent_comment:
            raise HTTPException(status_code=404, detail="父评论不存在")
    
    # 创建评论
    new_comment = DiaryComment(
        diary_id=diary_id,
        user_id=user_id,
        parent_id=comment_data.parent_id,
        content=comment_data.content,
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat()
    )
    
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    
    # 获取用户名
    user = db.query(User).filter(User.id == user_id).first()
    username = user.username if user else "未知用户"
    
    return CommentResponse(
        id=new_comment.id,
        diary_id=new_comment.diary_id,
        user_id=new_comment.user_id,
        username=username,
        parent_id=new_comment.parent_id,
        content=new_comment.content,
        like_count=new_comment.like_count,
        is_deleted=new_comment.is_deleted,
        created_at=new_comment.created_at,
        updated_at=new_comment.updated_at,
        replies=[]
    )


@router.delete("/comments/{comment_id}")
def delete_comment(
    comment_id: int,
    user_id: int = Query(..., description="用户 ID"),
    db: Session = Depends(get_db)
):
    """删除评论（软删除）"""
    comment = db.query(DiaryComment).filter(DiaryComment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")
    
    # 检查是否是评论作者
    if comment.user_id != user_id:
        raise HTTPException(status_code=403, detail="无权限删除此评论")
    
    # 软删除
    comment.is_deleted = True
    comment.content = "[评论已删除]"
    comment.updated_at = datetime.now().isoformat()
    db.commit()
    
    return {"message": "评论已删除"}


@router.post("/comments/{comment_id}/like")
def like_comment(
    comment_id: int,
    db: Session = Depends(get_db)
):
    """点赞评论"""
    comment = db.query(DiaryComment).filter(DiaryComment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")
    
    comment.like_count += 1
    comment.updated_at = datetime.now().isoformat()
    db.commit()
    
    return {"like_count": comment.like_count}


# ==================== 评分 API ====================

@router.get("/diaries/{diary_id}/rating", response_model=RatingResponse)
def get_rating(diary_id: int, user_id: Optional[int] = Query(None, description="用户 ID"), db: Session = Depends(get_db)):
    """获取日记的评分信息"""
    diary = db.query(TravelDiary).filter(TravelDiary.id == diary_id).first()
    if not diary:
        raise HTTPException(status_code=404, detail="日记不存在")
    
    return RatingResponse(
        diary_id=diary_id,
        user_id=user_id or 0,
        rating=0,
        avg_rating=diary.avg_rating or 0,
        rating_count=diary.rating_count or 0
    )


@router.post("/diaries/{diary_id}/rating", response_model=RatingResponse)
def rate_diary(
    diary_id: int,
    rating_data: RatingCreate,
    user_id: int = Query(..., description="用户 ID"),
    db: Session = Depends(get_db)
):
    """对日记进行评分"""
    # 验证评分范围
    if rating_data.rating < 1 or rating_data.rating > 5:
        raise HTTPException(status_code=400, detail="评分必须在 1-5 之间")
    
    diary = db.query(TravelDiary).filter(TravelDiary.id == diary_id).first()
    if not diary:
        raise HTTPException(status_code=404, detail="日记不存在")
    
    # 检查用户是否已经评分
    existing_rating = db.query(DiaryRating).filter(
        DiaryRating.diary_id == diary_id,
        DiaryRating.user_id == user_id
    ).first()
    
    if existing_rating:
        # 更新评分
        existing_rating.rating = rating_data.rating
        existing_rating.created_at = datetime.now().isoformat()
        db.commit()
    else:
        # 创建新评分
        new_rating = DiaryRating(
            diary_id=diary_id,
            user_id=user_id,
            rating=rating_data.rating,
            created_at=datetime.now().isoformat()
        )
        db.add(new_rating)
        db.commit()
    
    # 重新计算平均评分
    ratings = db.query(DiaryRating).filter(DiaryRating.diary_id == diary_id).all()
    avg_rating = sum(r.rating for r in ratings) / len(ratings) if ratings else 0
    rating_count = len(ratings)
    
    # 更新日记的评分统计
    diary.avg_rating = round(avg_rating, 2)
    diary.rating_count = rating_count
    db.commit()
    db.refresh(diary)
    
    return RatingResponse(
        diary_id=diary_id,
        user_id=user_id,
        rating=rating_data.rating,
        avg_rating=diary.avg_rating,
        rating_count=diary.rating_count
    )


@router.delete("/diaries/{diary_id}/rating")
def delete_rating(
    diary_id: int,
    user_id: int = Query(..., description="用户 ID"),
    db: Session = Depends(get_db)
):
    """删除用户的评分"""
    rating = db.query(DiaryRating).filter(
        DiaryRating.diary_id == diary_id,
        DiaryRating.user_id == user_id
    ).first()
    
    if not rating:
        raise HTTPException(status_code=404, detail="未找到评分记录")
    
    db.delete(rating)
    
    # 重新计算平均评分
    ratings = db.query(DiaryRating).filter(DiaryRating.diary_id == diary_id).all()
    if ratings:
        avg_rating = sum(r.rating for r in ratings) / len(ratings)
        rating_count = len(ratings)
    else:
        avg_rating = 0
        rating_count = 0
    
    # 更新日记的评分统计
    diary = db.query(TravelDiary).filter(TravelDiary.id == diary_id).first()
    diary.avg_rating = round(avg_rating, 2)
    diary.rating_count = rating_count
    db.commit()
    
    return {"message": "评分已删除", "avg_rating": avg_rating, "rating_count": rating_count}
