"""
用户认证API - 注册、登录、个人信息
"""
from fastapi import APIRouter, Depends, Query, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
import sys
import os
import hashlib
import uuid

sys.path.append("..")

from models.database import get_db, User

router = APIRouter()

# 头像上传目录
AVATAR_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "images", "avatars")
os.makedirs(AVATAR_DIR, exist_ok=True)


# Pydantic模型
class RegisterRequest(BaseModel):
    username: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class UpdateProfileRequest(BaseModel):
    username: Optional[str] = None
    avatar_url: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    username: str
    avatar_url: Optional[str] = None
    email: Optional[str] = None
    created_at: str

    class Config:
        from_attributes = True


def hash_password(password: str) -> str:
    """密码哈希"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    """验证密码"""
    return hash_password(password) == password_hash


# 路由实现

@router.post("/register", response_model=UserResponse)
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):
    """用户注册 - 用户名唯一"""
    # 检查用户名是否已存在
    existing_user = db.query(User).filter(User.username == request.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    # 创建新用户
    user = User(
        username=request.username,
        password_hash=hash_password(request.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


@router.post("/login", response_model=UserResponse)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    """用户登录"""
    user = db.query(User).filter(User.username == request.username).first()
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    return user


@router.get("/me", response_model=UserResponse)
def get_current_user(
    user_id: int = Query(..., description="用户ID"),
    db: Session = Depends(get_db)
):
    """获取当前用户信息"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return user


@router.put("/profile", response_model=UserResponse)
def update_profile(
    request: UpdateProfileRequest,
    user_id: int = Query(..., description="用户ID"),
    db: Session = Depends(get_db)
):
    """更新用户信息（用户名、头像）"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 检查新用户名是否已存在
    if request.username and request.username != user.username:
        existing = db.query(User).filter(User.username == request.username).first()
        if existing:
            raise HTTPException(status_code=400, detail="用户名已存在")
        user.username = request.username
    
    # 更新头像URL
    if request.avatar_url:
        user.avatar_url = request.avatar_url
    
    user.updated_at = str(db.query(User).first().__class__.__dict__)
    from datetime import datetime
    user.updated_at = datetime.now().isoformat()
    
    db.commit()
    db.refresh(user)
    
    return user


@router.post("/avatar")
async def upload_avatar(
    user_id: int = Query(..., description="用户ID"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """上传头像"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 生成唯一文件名
    ext = os.path.splitext(file.filename)[1] if file.filename else '.png'
    filename = f"avatar_{user_id}_{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(AVATAR_DIR, filename)
    
    # 保存文件
    content = await file.read()
    with open(filepath, 'wb') as f:
        f.write(content)
    
    # 更新用户头像URL
    avatar_url = f"/images/avatars/{filename}"
    user.avatar_url = avatar_url
    from datetime import datetime
    user.updated_at = datetime.now().isoformat()
    db.commit()
    
    return {"avatar_url": avatar_url}


@router.post("/logout")
def logout():
    """退出登录（前端清除token即可）"""
    return {"success": True}
