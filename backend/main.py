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

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from routers import spots, trips, route, diary, ai, xiaohongshu, auth, collection, photo

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
app.include_router(diary.router, prefix="/api/diary", tags=["日记"])
app.include_router(ai.router, prefix="/api/ai", tags=["AI"])
app.include_router(xiaohongshu.router, prefix="/api/xiaohongshu", tags=["小红书"])
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(collection.router, prefix="/api/collections", tags=["收藏"])
app.include_router(photo.router, prefix="/api/photos", tags=["照片"])

@app.get("/")
async def root():
    return {"message": "欢迎使用邮游世界 - 个性化旅游系统", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
