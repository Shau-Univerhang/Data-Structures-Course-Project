"""
个性化旅游系统 - 后端入口
基于 FastAPI + SQLite
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import sys
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from routers import spots, trips, route, diary, ai, xiaohongshu, auth, collection, photo, photo_spot

app = FastAPI(
    title="邮游世界 - 个性化旅游系统",
    description="基于大语言模型和自研算法的个性化旅游规划系统",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
images_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "images")
app.mount("/images", StaticFiles(directory=images_dir), name="images")

# 注册路由
app.include_router(spots.router, prefix="/api/spots", tags=["景点"])
app.include_router(trips.router, prefix="/api/trips", tags=["行程"])
app.include_router(route.router, prefix="/api/route", tags=["路线"])

# 先定义日记库路由（必须在 diary router 之前）
from fastapi import Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from models.database import get_db, TravelDiary, User, DiaryCity, DiaryCityTag, DiaryComment

@app.get("/api/library/diaries/cities", tags=["日记库"])
def get_library_cities(
    min_count: int = Query(1, ge=0, description="最小日记数量"),
    db: Session = Depends(get_db)
):
    """获取日记城市列表"""
    cities = db.query(DiaryCity).filter(
        DiaryCity.diary_count >= min_count
    ).order_by(DiaryCity.diary_count.desc()).all()
    
    hot_cities = [c.name for c in cities if c.diary_count >= 10][:10]
    
    return {
        "cities": [{"id": c.id, "name": c.name, "diary_count": c.diary_count} for c in cities],
        "hot_cities": hot_cities
    }

@app.get("/api/library/diaries", tags=["日记库"])
def get_diary_library(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=50, description="每页数量"),
    city_id: Optional[int] = Query(None, description="城市ID筛选"),
    diary_type: Optional[str] = Query(None, description="日记类型筛选"),
    sort: str = Query("hot", description="排序方式: hot/new/rating"),
    db: Session = Depends(get_db)
):
    """获取日记库列表"""
    query = db.query(TravelDiary).filter(
        TravelDiary.is_public == True,
        TravelDiary.status == 'published'
    )
    
    if city_id:
        diary_ids = db.query(DiaryCityTag.diary_id).filter(
            DiaryCityTag.city_id == city_id
        ).distinct()
        query = query.filter(TravelDiary.id.in_(diary_ids))
    
    if diary_type:
        query = query.filter(TravelDiary.diary_type == diary_type)
    
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
        city_tags = db.query(DiaryCity).join(
            DiaryCityTag, DiaryCity.id == DiaryCityTag.city_id
        ).filter(DiaryCityTag.diary_id == diary.id).all()
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
    
    return {"total": total, "page": page, "page_size": page_size, "diaries": result}

# 再注册 diary router（在日记库路由之后）
app.include_router(diary.router, prefix="/api/diaries", tags=["日记"])

app.include_router(ai.router, prefix="/api/ai", tags=["AI"])
app.include_router(xiaohongshu.router, prefix="/api/xiaohongshu", tags=["小红书"])
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(collection.router, prefix="/api/collections", tags=["收藏"])
app.include_router(photo.router, prefix="/api/photos", tags=["照片"])
app.include_router(photo_spot.router, prefix="/api/photo-spots", tags=["拍照点位"])

@app.get("/")
async def root():
    return {"message": "欢迎使用邮游世界 - 个性化旅游系统", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
