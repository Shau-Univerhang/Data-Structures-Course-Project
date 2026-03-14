"""
景点相关API
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import sys
sys.path.append("..")

from models.database import get_db, ScenicSpot, Restaurant
from algorithms.core import top_k_spots, top_k_restaurants, fuzzy_search_spots

router = APIRouter()


# Pydantic模型
class SpotResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    address: Optional[str] = None
    city: Optional[str] = None
    category: Optional[str] = None
    rating: Optional[float] = 0
    heat_score: Optional[int] = 0
    review_count: Optional[int] = 0
    open_time: Optional[str] = None
    ticket_price: Optional[str] = None
    need_booking: Optional[bool] = False
    images: Optional[list] = []
    tags: Optional[list] = []

    class Config:
        from_attributes = True


class SpotListResponse(BaseModel):
    total: int
    spots: List[SpotResponse]


class RestaurantResponse(BaseModel):
    id: int
    name: str
    cuisine_type: Optional[str] = None
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    rating: Optional[float] = 0
    heat_score: Optional[int] = 0
    price_range: Optional[str] = None
    open_time: Optional[str] = None
    images: Optional[list] = []
    tags: Optional[list] = []

    class Config:
        from_attributes = True


# 路由实现

@router.get("/", response_model=SpotListResponse)
def list_spots(
    city: Optional[str] = Query(None, description="城市筛选"),
    category: Optional[str] = Query(None, description="类别筛选"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """获取景点列表"""
    query = db.query(ScenicSpot)
    
    if city:
        query = query.filter(ScenicSpot.city == city)
    
    if category:
        query = query.filter(ScenicSpot.category == category)
    
    total = query.count()
    offset = (page - 1) * page_size
    spots = query.offset(offset).limit(page_size).all()
    
    return {"total": total, "spots": spots}


@router.get("/search", response_model=SpotListResponse)
def search_spots(
    q: Optional[str] = Query(None, description="搜索关键词"),
    city: Optional[str] = Query(None, description="城市筛选"),
    category: Optional[str] = Query(None, description="类别筛选"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """搜索景点"""
    query = db.query(ScenicSpot)
    
    if q:
        # 模糊搜索
        spots = db.query(ScenicSpot).all()
        spots_data = [s.__dict__ for s in spots]
        filtered = fuzzy_search_spots(spots_data, q)
        spot_ids = [s['id'] for s in filtered]
        if spot_ids:
            query = query.filter(ScenicSpot.id.in_(spot_ids))
    
    if city:
        query = query.filter(ScenicSpot.city == city)
    
    if category:
        query = query.filter(ScenicSpot.category == category)
    
    total = query.count()
    offset = (page - 1) * page_size
    spots = query.offset(offset).limit(page_size).all()
    
    return {"total": total, "spots": spots}


@router.get("/recommend", response_model=SpotListResponse)
def recommend_spots(
    city: str = Query(..., description="城市"),
    preferences: str = Query("", description="偏好标签，逗号分隔"),
    k: int = Query(10, ge=1, le=50, description="返回数量"),
    db: Session = Depends(get_db)
):
    """推荐景点（使用Top K部分排序算法）"""
    query = db.query(ScenicSpot).filter(ScenicSpot.city == city)
    spots = query.all()
    
    # 转换为字典列表
    spots_data = []
    for s in spots:
        spots_data.append({
            'id': s.id,
            'name': s.name,
            'description': s.description,
            'location_lat': s.location_lat,
            'location_lng': s.location_lng,
            'address': s.address,
            'city': s.city,
            'category': s.category,
            'rating': s.rating,
            'heat_score': s.heat_score,
            'review_count': s.review_count,
            'open_time': s.open_time,
            'ticket_price': s.ticket_price,
            'need_booking': s.need_booking,
            'images': s.images or [],
            'tags': s.tags or []
        })
    
    # 偏好过滤
    if preferences:
        pref_list = [p.strip() for p in preferences.split(',')]
        filtered = []
        for spot in spots_data:
            spot_tags = spot.get('tags', [])
            if any(p in spot_tags for p in pref_list):
                filtered.append(spot)
        if filtered:
            spots_data = filtered
    
    # 使用部分排序算法获取Top K
    result = top_k_spots(spots_data, k=k, sort_by='composite')
    
    return {"total": len(result), "spots": result}


@router.get("/{spot_id}", response_model=SpotResponse)
def get_spot(spot_id: int, db: Session = Depends(get_db)):
    """获取景点详情"""
    spot = db.query(ScenicSpot).filter(ScenicSpot.id == spot_id).first()
    if not spot:
        return {"error": "景点不存在"}
    return spot


@router.get("/city/list")
def get_city_list(db: Session = Depends(get_db)):
    """获取所有城市列表"""
    cities = db.query(ScenicSpot.city).distinct().all()
    return {"cities": [c[0] for c in cities if c[0]]}


@router.get("/restaurants/recommend", response_model=List[RestaurantResponse])
def recommend_restaurants(
    spot_id: int = Query(..., description="景点ID"),
    k: int = Query(10, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """推荐美食（使用Top K部分排序算法）"""
    restaurants = db.query(Restaurant).filter(Restaurant.spot_id == spot_id).all()
    
    # 转换为字典列表
    restaurants_data = []
    for r in restaurants:
        restaurants_data.append({
            'id': r.id,
            'name': r.name,
            'cuisine_type': r.cuisine_type,
            'location_lat': r.location_lat,
            'location_lng': r.location_lng,
            'rating': r.rating,
            'heat_score': r.heat_score,
            'price_range': r.price_range,
            'open_time': r.open_time,
            'images': r.images or [],
            'tags': r.tags or []
        })
    
    # 使用部分排序
    result = top_k_restaurants(restaurants_data, k=k)
    
    return result


@router.get("/restaurants/by-city", response_model=List[RestaurantResponse])
def get_restaurants_by_city(
    city: str = Query(..., description="城市名"),
    k: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """获取城市美食推荐"""
    # 先找到该城市的景点ID范围
    city_spots = db.query(ScenicSpot).filter(ScenicSpot.city == city).all()
    if not city_spots:
        return []
    
    spot_ids = [s.id for s in city_spots]
    
    # 查询这些景点的餐厅
    restaurants = db.query(Restaurant).filter(Restaurant.spot_id.in_(spot_ids)).all()
    
    # 转换为响应格式
    result = []
    for r in restaurants:
        result.append({
            'id': r.id,
            'name': r.name,
            'cuisine_type': r.cuisine_type,
            'location_lat': r.location_lat,
            'location_lng': r.location_lng,
            'rating': r.rating,
            'heat_score': r.heat_score,
            'price_range': r.price_range,
            'open_time': r.open_time,
            'images': r.images or [],
            'tags': r.tags or []
        })
    
    # 按评分和热度排序
    result.sort(key=lambda x: (x['rating'], x['heat_score']), reverse=True)
    return result[:k]
