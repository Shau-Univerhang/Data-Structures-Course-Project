"""
行程照片API
"""
from fastapi import APIRouter, Depends, Query, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import sys
import os
import uuid

sys.path.append("..")

from models.database import get_db, TripPhoto, Trip

router = APIRouter()

# 照片上传目录
PHOTO_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "images", "photos")
os.makedirs(PHOTO_DIR, exist_ok=True)


# Pydantic模型
class PhotoResponse(BaseModel):
    id: int
    trip_id: int
    photo_url: str
    description: Optional[str] = None
    created_at: str
    
    class Config:
        from_attributes = True


class TripWithPhotos(BaseModel):
    trip_id: int
    trip_title: str
    photos: List[PhotoResponse]


class AddPhotoRequest(BaseModel):
    trip_id: int
    description: Optional[str] = None


# 照片路由

@router.get("/", response_model=List[TripWithPhotos])
def get_photos(
    user_id: int = Query(..., description="用户ID"),
    db: Session = Depends(get_db)
):
    """获取用户照片（按行程分组）- 返回所有行程，包括没有照片的"""
    # 获取用户的所有行程
    trips = db.query(Trip).filter(Trip.user_id == user_id).order_by(Trip.created_at.desc()).all()
    
    result = []
    for trip in trips:
        photos = db.query(TripPhoto).filter(TripPhoto.trip_id == trip.id).all()
        result.append({
            'trip_id': trip.id,
            'trip_title': trip.title,
            'photos': [{
                'id': p.id,
                'trip_id': p.trip_id,
                'photo_url': p.photo_url,
                'description': p.description,
                'created_at': p.created_at
            } for p in photos]
        })
    
    return result


@router.get("/by-trip/{trip_id}", response_model=List[PhotoResponse])
def get_photos_by_trip(
    trip_id: int,
    user_id: int = Query(..., description="用户ID"),
    db: Session = Depends(get_db)
):
    """获取某个行程的照片"""
    # 检查行程归属
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == user_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="行程不存在")
    
    photos = db.query(TripPhoto).filter(TripPhoto.trip_id == trip_id).all()
    
    return photos


@router.post("/", response_model=PhotoResponse)
async def upload_photo(
    user_id: int = Query(..., description="用户ID"),
    trip_id: int = Query(..., description="行程ID"),
    description: Optional[str] = Query(None, description="照片描述"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """上传照片到行程"""
    # 检查行程归属
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == user_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="行程不存在")
    
    # 生成唯一文件名
    ext = os.path.splitext(file.filename)[1] if file.filename else '.jpg'
    filename = f"photo_{trip_id}_{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(PHOTO_DIR, filename)
    
    # 保存文件
    content = await file.read()
    with open(filepath, 'wb') as f:
        f.write(content)
    
    # 保存到数据库
    photo = TripPhoto(
        user_id=user_id,
        trip_id=trip_id,
        photo_url=f"/images/photos/{filename}",
        description=description
    )
    db.add(photo)
    db.commit()
    db.refresh(photo)
    
    return photo


@router.delete("/{photo_id}")
def delete_photo(
    photo_id: int,
    user_id: int = Query(..., description="用户ID"),
    db: Session = Depends(get_db)
):
    """删除照片"""
    photo = db.query(TripPhoto).filter(
        TripPhoto.id == photo_id,
        TripPhoto.user_id == user_id
    ).first()
    
    if not photo:
        raise HTTPException(status_code=404, detail="照片不存在")
    
    # 删除文件
    try:
        filepath = photo.photo_url.replace("/images/photos/", "")
        full_path = os.path.join(PHOTO_DIR, filepath)
        if os.path.exists(full_path):
            os.remove(full_path)
    except:
        pass
    
    db.delete(photo)
    db.commit()
    
    return {"success": True}
