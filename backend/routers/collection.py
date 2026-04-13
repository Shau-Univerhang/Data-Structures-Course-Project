"""
收藏和照片API
"""
from fastapi import APIRouter, Depends, Query, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import sys
import os
import uuid

sys.path.append("..")

from models.database import get_db, Collection, TripPhoto, ScenicSpot, Trip, SpotReview

# 导入spots路由中的图片获取函数
from routers.spots import get_spot_image

router = APIRouter()

# 照片上传目录
PHOTO_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "images", "photos")
os.makedirs(PHOTO_DIR, exist_ok=True)


# ==================== Pydantic模型 ====================

class CollectionResponse(BaseModel):
    id: int
    spot_id: int
    created_at: str
    
    class Config:
        from_attributes = True


class SpotInfo(BaseModel):
    id: int
    name: str
    city: str
    rating: float
    images: List[str] = []
    
    class Config:
        from_attributes = True


class PhotoResponse(BaseModel):
    id: int
    trip_id: int
    photo_url: str
    description: Optional[str] = None
    created_at: str
    
    class Config:
        from_attributes = True


class AddCollectionRequest(BaseModel):
    spot_id: int


class AddPhotoRequest(BaseModel):
    trip_id: int
    description: Optional[str] = None


class ReviewResponse(BaseModel):
    id: int
    spot_id: int
    user_id: int
    rating: float
    content: Optional[str] = None
    images: Optional[list] = None
    created_at: str
    username: Optional[str] = None
    
    class Config:
        from_attributes = True


class AddReviewRequest(BaseModel):
    spot_id: int
    rating: float
    content: Optional[str] = None
    images: Optional[list] = None


# ==================== 删除评价API (放在最前面避免路由冲突) ====================

@router.delete("/reviews/delete/{review_id}")
def delete_review(
    review_id: int,
    user_id: int = Query(..., description="用户ID"),
    db: Session = Depends(get_db)
):
    """删除评价"""
    print(f"[DEBUG] 删除评价 - review_id: {review_id}, user_id: {user_id}")
    
    review = db.query(SpotReview).filter(SpotReview.id == review_id).first()
    
    if not review:
        print(f"[DEBUG] 评价不存在: {review_id}")
        raise HTTPException(status_code=404, detail="评价不存在")
    
    print(f"[DEBUG] 找到评价: {review.id}, user_id: {review.user_id}")
    
    # 检查是否是评价作者
    if review.user_id != user_id:
        raise HTTPException(status_code=403, detail="只能删除自己的评价")
    
    # 获取景点信息
    spot = db.query(ScenicSpot).filter(ScenicSpot.id == review.spot_id).first()
    
    # 先查询剩余的评价（不包括要删除的这条）
    remaining_reviews = db.query(SpotReview).filter(
        SpotReview.spot_id == review.spot_id,
        SpotReview.id != review_id
    ).all()
    
    # 删除评价
    db.delete(review)
    
    # 更新景点的评价数和平均评分
    if spot:
        spot.review_count = len(remaining_reviews)
        
        # 重新计算平均评分
        if remaining_reviews:
            total_rating = sum(r.rating for r in remaining_reviews)
            spot.rating = round(total_rating / len(remaining_reviews), 1)
        else:
            spot.rating = 0
    
    db.commit()
    
    return {"success": True, "message": "评价已删除"}


# ==================== 评价相关API ====================

@router.get("/spot-reviews/{spot_id}")
def get_reviews(
    spot_id: int,
    db: Session = Depends(get_db)
):
    """获取景点的评价列表"""
    reviews = db.query(SpotReview).filter(SpotReview.spot_id == spot_id).all()
    
    result = []
    for review in reviews:
        # 获取用户名
        from models.database import User
        user = db.query(User).filter(User.id == review.user_id).first()
        username = user.username if user else f"用户{review.user_id}"
        
        result.append({
            'id': review.id,
            'spot_id': review.spot_id,
            'user_id': review.user_id,
            'rating': review.rating,
            'content': review.content,
            'images': review.images or [],
            'created_at': review.created_at,
            'username': username
        })
    
    print(f"[DEBUG] 返回评价列表: {result}")
    return result


@router.post("/spot-reviews", response_model=ReviewResponse)
def add_review(
    request: AddReviewRequest,
    user_id: int = Query(..., description="用户ID"),
    db: Session = Depends(get_db)
):
    """添加评价"""
    print(f"[DEBUG] 添加评价 - user_id: {user_id}, spot_id: {request.spot_id}, rating: {request.rating}")
    
    # 检查景点是否存在
    spot = db.query(ScenicSpot).filter(ScenicSpot.id == request.spot_id).first()
    if not spot:
        print(f"[DEBUG] 景点不存在: {request.spot_id}")
        raise HTTPException(status_code=404, detail="景点不存在")
    
    print(f"[DEBUG] 找到景点: {spot.name}")
    
    # 检查用户是否已评价
    existing = db.query(SpotReview).filter(
        SpotReview.user_id == user_id,
        SpotReview.spot_id == request.spot_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="您已经评价过该景点")
    
    # 验证评分范围
    if request.rating < 1 or request.rating > 5:
        raise HTTPException(status_code=400, detail="评分必须在1-5之间")
    
    # 创建评价
    review = SpotReview(
        user_id=user_id,
        spot_id=request.spot_id,
        rating=request.rating,
        content=request.content,
        images=request.images
    )
    db.add(review)
    
    # 更新景点的评价数和平均评分
    spot.review_count = (spot.review_count or 0) + 1
    
    # 重新计算平均评分
    all_reviews = db.query(SpotReview).filter(SpotReview.spot_id == request.spot_id).all()
    total_rating = sum(r.rating for r in all_reviews) + request.rating
    spot.rating = round(total_rating / (len(all_reviews) + 1), 1)
    
    db.commit()
    db.refresh(review)
    
    # 获取用户名
    from models.database import User
    user = db.query(User).filter(User.id == user_id).first()
    username = user.username if user else f"用户{user_id}"
    
    return {
        'id': review.id,
        'spot_id': review.spot_id,
        'user_id': review.user_id,
        'rating': review.rating,
        'content': review.content,
        'images': review.images or [],
        'created_at': review.created_at,
        'username': username
    }


@router.get("/spot-reviews/check/{spot_id}")
def check_review(
    spot_id: int,
    user_id: int = Query(..., description="用户ID"),
    db: Session = Depends(get_db)
):
    """检查用户是否已评价"""
    review = db.query(SpotReview).filter(
        SpotReview.user_id == user_id,
        SpotReview.spot_id == spot_id
    ).first()
    
    return {"has_reviewed": review is not None}


# ==================== 收藏路由 ====================

@router.get("/", response_model=List[SpotInfo])
def get_collections(
    user_id: int = Query(..., description="用户ID"),
    db: Session = Depends(get_db)
):
    """获取用户收藏的景点"""
    collections = db.query(Collection).filter(Collection.user_id == user_id).all()

    result = []
    for col in collections:
        spot = db.query(ScenicSpot).filter(ScenicSpot.id == col.spot_id).first()
        if spot:
            # 使用get_spot_image获取景点图片（与景点推荐API一致）
            spot_images = get_spot_image(spot.name, spot.city)
            result.append({
                'id': spot.id,
                'name': spot.name,
                'city': spot.city,
                'rating': spot.rating,
                'images': spot_images if spot_images else []
            })

    return result


@router.post("/", response_model=CollectionResponse)
def add_collection(
    request: AddCollectionRequest,
    user_id: int = Query(..., description="用户ID"),
    db: Session = Depends(get_db)
):
    """添加收藏"""
    print(f"[DEBUG] 添加收藏 - user_id: {user_id}, spot_id: {request.spot_id}")
    
    # 检查景点是否存在
    spot = db.query(ScenicSpot).filter(ScenicSpot.id == request.spot_id).first()
    if not spot:
        print(f"[DEBUG] 景点不存在: {request.spot_id}")
        raise HTTPException(status_code=404, detail="景点不存在")
    
    print(f"[DEBUG] 找到景点: {spot.name}, 当前收藏数: {spot.favorites_count}")
    
    # 检查是否已收藏
    existing = db.query(Collection).filter(
        Collection.user_id == user_id,
        Collection.spot_id == request.spot_id
    ).first()
    
    if existing:
        print(f"[DEBUG] 已经收藏过该景点")
        raise HTTPException(status_code=400, detail="已经收藏过该景点")
    
    # 添加收藏
    collection = Collection(
        user_id=user_id,
        spot_id=request.spot_id
    )
    db.add(collection)
    
    # 增加景点收藏数
    old_count = spot.favorites_count or 0
    spot.favorites_count = old_count + 1
    print(f"[DEBUG] 更新收藏数: {old_count} -> {spot.favorites_count}")
    
    db.commit()
    db.refresh(collection)
    
    # 验证保存是否成功
    db.refresh(spot)
    print(f"[DEBUG] 保存后的收藏数: {spot.favorites_count}")
    
    return collection


@router.delete("/{spot_id}")
def remove_collection(
    spot_id: int,
    user_id: int = Query(..., description="用户ID"),
    db: Session = Depends(get_db)
):
    """取消收藏"""
    collection = db.query(Collection).filter(
        Collection.user_id == user_id,
        Collection.spot_id == spot_id
    ).first()
    
    if not collection:
        raise HTTPException(status_code=404, detail="未收藏该景点")
    
    # 减少景点收藏数
    spot = db.query(ScenicSpot).filter(ScenicSpot.id == spot_id).first()
    if spot and spot.favorites_count and spot.favorites_count > 0:
        spot.favorites_count -= 1
    
    db.delete(collection)
    db.commit()
    
    return {"success": True}


@router.get("/check/{spot_id}")
def check_collection(
    spot_id: int,
    user_id: int = Query(..., description="用户ID"),
    db: Session = Depends(get_db)
):
    """检查是否已收藏"""
    collection = db.query(Collection).filter(
        Collection.user_id == user_id,
        Collection.spot_id == spot_id
    ).first()
    
    return {"is_collected": collection is not None}
