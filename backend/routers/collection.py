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

from models.database import get_db, Collection, TripPhoto, ScenicSpot, Trip

router = APIRouter()

# 照片上传目录
PHOTO_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "images", "photos")
os.makedirs(PHOTO_DIR, exist_ok=True)


# Pydantic模型
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


# 收藏路由

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
            result.append({
                'id': spot.id,
                'name': spot.name,
                'city': spot.city,
                'rating': spot.rating,
                'images': spot.images or []
            })
    
    return result


@router.post("/", response_model=CollectionResponse)
def add_collection(
    request: AddCollectionRequest,
    user_id: int = Query(..., description="用户ID"),
    db: Session = Depends(get_db)
):
    """添加收藏"""
    # 检查景点是否存在
    spot = db.query(ScenicSpot).filter(ScenicSpot.id == request.spot_id).first()
    if not spot:
        raise HTTPException(status_code=404, detail="景点不存在")
    
    # 检查是否已收藏
    existing = db.query(Collection).filter(
        Collection.user_id == user_id,
        Collection.spot_id == request.spot_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="已经收藏过该景点")
    
    # 添加收藏
    collection = Collection(
        user_id=user_id,
        spot_id=request.spot_id
    )
    db.add(collection)
    db.commit()
    db.refresh(collection)
    
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
