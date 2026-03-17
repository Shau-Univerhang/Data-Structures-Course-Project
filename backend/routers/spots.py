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

# 景点图片映射
SPOT_IMAGES = {
    # 北京
    '故宫博物院': ['/images/spots/beijing/beijing_gugong_bowuyuan.jpg'],
    '故宫': ['/images/spots/beijing/beijing_gugong_bowuyuan.jpg'],
    '天坛公园': ['/images/spots/beijing/beijing_tiantan_gongyuan.jpg'],
    '天坛': ['/images/spots/beijing/beijing_tiantan_gongyuan.jpg'],
    '长城-八达岭': ['/images/spots/beijing/beijing_badaling_changcheng.jpg'],
    '八达岭长城': ['/images/spots/beijing/beijing_badaling_changcheng.jpg'],
    '颐和园': ['/images/spots/beijing/beijing_yiheyuan.jpg'],
    '圆明园': ['/images/spots/beijing/beijing_yuanmingyuan.jpg'],
    '天安门广场': ['/images/spots/beijing/beijing_tiananmen_guangchang.jpg'],
    '天安门': ['/images/spots/beijing/beijing_tiananmen_guangchang.jpg'],
    '北海公园': ['/images/spots/beijing/beijing_beihai_gongyuan.jpg'],
    '恭王府': ['/images/spots/beijing/beijing_gongwangfu.jpg'],
    '景山公园': ['/images/spots/beijing/beijing_jingshan_gongyuan.jpg'],
    '南锣鼓巷': ['/images/spots/beijing/beijing_nanluoguxiang.jpg'],
    # 上海
    '外滩': ['/images/spots/shanghai/shanghai_waitan.jpg'],
    '东方明珠': ['/images/spots/shanghai/shanghai_dongfang_mingzhu.jpg'],
    '豫园': ['/images/spots/shanghai/shanghai_yuyuan.jpg'],
    '田子坊': ['/images/spots/shanghai/shanghai_tianzifang.jpg'],
    '武康路': ['/images/spots/shanghai/shanghai_wukanglu.jpg'],
    '南京路': ['/images/spots/shanghai/shanghai_nanjinglu_buxingjie.jpg'],
    # 西安
    '秦始皇兵马俑': ['/images/spots/xian/xian_bingmayong.jpg'],
    '兵马俑': ['/images/spots/xian/xian_bingmayong.jpg'],
    '大雁塔': ['/images/spots/xian/xian_dayanta.jpg'],
    '古城墙': ['/images/spots/xian/xian_xian_chengqiang.jpg'],
    '西安城墙': ['/images/spots/xian/xian_xian_chengqiang.jpg'],
    '华清宫': ['/images/spots/xian/xian_huaqinggong.jpg'],
    '大唐芙蓉园': ['/images/spots/xian/xian_datang_furongyuan.jpg'],
    '回民街': ['/images/spots/xian/xian_huiminjie.jpg'],
    # 成都
    '大熊猫繁育研究基地': ['/images/spots/chengdu/chengdu_xiongmao_jidi.jpg'],
    '熊猫基地': ['/images/spots/chengdu/chengdu_xiongmao_jidi.jpg'],
    '宽窄巷子': ['/images/spots/chengdu/chengdu_kuanzhai_xiangzi.jpg'],
    '锦里': ['/images/spots/chengdu/chengdu_chunxilu.jpg'],
    # 杭州
    '西湖': ['/images/spots/hangzhou/hangzhou_xihu.jpg'],
    '灵隐寺': ['/images/spots/hangzhou/hangzhou_lingyinsi.jpg'],
    '雷峰塔': ['/images/spots/hangzhou/hangzhou_leifengta.jpg'],
    # 重庆
    '洪崖洞': ['/images/spots/chongqing/chongqing_hongyadong.jpg'],
    '解放碑': ['/images/spots/chongqing/chongqing_jiefangbei.jpg'],
    '磁器口': ['/images/spots/chongqing/chongqing_ciqikou.jpg'],
    # 其他城市
    '洱海': ['/images/spots/dali/dali_erhai.jpg'],
    '大理古城': ['/images/spots/dali/dali_dali_ancient_city.jpg'],
    '漓江': ['/images/spots/guilin/guilin_lijiang.jpg'],
    '象鼻山': ['/images/spots/guilin/guilin_xiangbishan.jpg'],
    '黄山': ['/images/spots/huangshan/huangshan_huangshan_scenery.jpg'],
    '九寨沟': ['/images/spots/jiuzhaigou/jiuzhaigou_jiuzhaigou_valley.jpg'],
    '丽江古城': ['/images/spots/lijiang/lijiang_lijiang_gucheng.jpg'],
    '玉龙雪山': ['/images/spots/lijiang/lijiang_yulong_xueshan.jpg'],
    '广州塔': ['/images/spots/guangzhou/guangzhou_guangzhouta.jpg'],
    '沙面': ['/images/spots/guangzhou/guangzhou_shamian.jpg'],
    '陈家祠': ['/images/spots/guangzhou/guangzhou_chenjiaci.jpg'],
    '拙政园': ['/images/spots/suzhou/suzhou_zhuozhengyuan.jpg'],
    '虎丘': ['/images/spots/suzhou/suzhou_huqiu.jpg'],
    '鼓浪屿': ['/images/spots/xiamen/xiamen_gulangyu.jpg'],
    '厦门大学': ['/images/spots/xiamen/xiamen_xiamen_daxue.jpg'],
    '天涯海角': ['/images/spots/sanya/sanya_tianyahaijiao.jpg'],
    '亚龙湾': ['/images/spots/sanya/sanya_yalongwan.jpg'],
    '张家界': ['/images/spots/zhangjiajie/zhangjiajie_zhangjiajie_forest.jpg'],
}

# 城市默认图片
CITY_IMAGES = {
    '北京': '/images/cities/beijing.jpg',
    '上海': '/images/cities/shanghai.jpg',
    '西安': '/images/cities/xian.jpg',
    '成都': '/images/cities/chengdu.jpg',
    '杭州': '/images/cities/hangzhou.jpg',
    '重庆': '/images/cities/chongqing.jpg',
    '青岛': '/images/cities/qingdao.jpg',
    '广州': '/images/cities/guangzhou.jpg',
    '苏州': '/images/cities/suzhou.jpg',
    '厦门': '/images/cities/xiamen.jpg',
    '南京': '/images/cities/nanjing.jpg',
    '武汉': '/images/cities/wuhan.jpg',
    '长沙': '/images/cities/changsha.jpg',
    '深圳': '/images/cities/shenzhen.jpg',
    '三亚': '/images/cities/sanya.jpg',
    '桂林': '/images/cities/guilin.jpg',
    '张家界': '/images/cities/zhangjiajie.jpg',
    '黄山': '/images/cities/huangshan.jpg',
    '九寨沟': '/images/cities/jiuzhaigou.jpg',
    '大理': '/images/cities/dali.jpg',
    '丽江': '/images/cities/lijiang.jpg',
}

def get_spot_image(spot_name: str, city: str) -> list:
    """获取景点图片"""
    if spot_name in SPOT_IMAGES:
        return SPOT_IMAGES[spot_name]
    # 尝试部分匹配
    for name, images in SPOT_IMAGES.items():
        if name in spot_name or spot_name in name:
            return images
    # 返回城市默认图片
    city_img = CITY_IMAGES.get(city, '/images/cities/beijing.jpg')
    return [city_img]


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
        # 获取景点图片 - 优先使用映射中的图片
        spot_images = get_spot_image(s.name, s.city)
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
            'images': spot_images if spot_images else [],
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
    
    # 转换为字典并添加图片
    spot_dict = {
        'id': spot.id,
        'name': spot.name,
        'description': spot.description,
        'location_lat': spot.location_lat,
        'location_lng': spot.location_lng,
        'address': spot.address,
        'city': spot.city,
        'category': spot.category,
        'rating': spot.rating,
        'heat_score': spot.heat_score,
        'review_count': spot.review_count,
        'open_time': spot.open_time,
        'ticket_price': spot.ticket_price,
        'need_booking': spot.need_booking,
        'images': get_spot_image(spot.name, spot.city),
        'tags': spot.tags or []
    }
    return spot_dict


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
