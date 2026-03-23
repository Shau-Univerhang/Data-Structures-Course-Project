"""
景点拍照点位API
"""
from fastapi import APIRouter, Depends, Query, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import sys
import os
import uuid

sys.path.append("..")

from models.database import get_db, PhotoSpot

router = APIRouter()

# 图片上传目录
PHOTO_PLACE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "images", "photo_place")
os.makedirs(PHOTO_PLACE_DIR, exist_ok=True)


class PhotoSpotResponse(BaseModel):
    id: int
    spot_id: int
    user_id: int
    name: str
    description: Optional[str] = None
    image: Optional[str] = None
    created_at: str
    
    class Config:
        from_attributes = True


@router.get("/{spot_id}", response_model=List[PhotoSpotResponse])
def get_photo_spots(
    spot_id: int,
    db: Session = Depends(get_db)
):
    """获取景点的拍照点位列表"""
    photo_spots = db.query(PhotoSpot).filter(PhotoSpot.spot_id == spot_id).all()
    return photo_spots


@router.post("/", response_model=PhotoSpotResponse)
def add_photo_spot(
    spot_id: int = Form(...),
    name: str = Form(...),
    description: Optional[str] = Form(None),
    user_id: int = Query(..., description="用户ID"),
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """添加拍照点位（支持图片上传）"""
    # 保存上传的图片
    file_extension = os.path.splitext(image.filename)[1].lower()
    if file_extension not in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
        raise HTTPException(status_code=400, detail="不支持的图片格式")
    
    # 生成唯一文件名
    unique_filename = f"{uuid.uuid4().hex}{file_extension}"
    file_path = os.path.join(PHOTO_PLACE_DIR, unique_filename)
    
    # 保存文件
    try:
        with open(file_path, "wb") as f:
            content = image.file.read()
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"图片保存失败: {str(e)}")
    
    # 生成访问URL
    image_url = f"/images/photo_place/{unique_filename}"
    
    # 创建数据库记录
    photo_spot = PhotoSpot(
        spot_id=spot_id,
        user_id=user_id,
        name=name,
        description=description,
        image=image_url
    )
    db.add(photo_spot)
    db.commit()
    db.refresh(photo_spot)
    
    return photo_spot


@router.delete("/{photo_spot_id}")
def delete_photo_spot(
    photo_spot_id: int,
    user_id: int = Query(..., description="用户ID"),
    db: Session = Depends(get_db)
):
    """删除拍照点位"""
    photo_spot = db.query(PhotoSpot).filter(PhotoSpot.id == photo_spot_id).first()
    
    if not photo_spot:
        raise HTTPException(status_code=404, detail="拍照点位不存在")
    
    # 检查是否是上传者
    if photo_spot.user_id != user_id:
        raise HTTPException(status_code=403, detail="只能删除自己上传的拍照点位")
    
    # 删除图片文件
    if photo_spot.image:
        try:
            image_filename = os.path.basename(photo_spot.image)
            image_path = os.path.join(PHOTO_PLACE_DIR, image_filename)
            if os.path.exists(image_path):
                os.remove(image_path)
        except Exception as e:
            print(f"删除图片文件失败: {e}")
    
    db.delete(photo_spot)
    db.commit()
    
    return {"success": True, "message": "拍照点位已删除"}
