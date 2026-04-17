"""
数据库模型定义
使用 SQLite
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, Text, Date, Time, JSON, BLOB, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import json

Base = declarative_base()

# 数据库路径
import os
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "travel.db")
# 确保data目录存在
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100))
    avatar_url = Column(String(255))
    preferences = Column(JSON)  # 用户偏好设置
    created_at = Column(String, default=datetime.now().isoformat)
    updated_at = Column(String, default=datetime.now().isoformat)


class ScenicSpot(Base):
    """景区/景点表（核心）"""
    __tablename__ = "scenic_spots"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    location_lat = Column(Float)  # 纬度
    location_lng = Column(Float)  # 经度
    address = Column(String(255))
    city = Column(String(50))
    category = Column(String(50))  # 类别：历史古迹、自然风光、现代建筑等
    type = Column(String(20))  # 'scenic'景点 或 'campus'校园
    rating = Column(Float, default=0)  # 评分 0-5，根据用户评价计算
    heat_score = Column(Integer, default=0)  # 热度值
    review_count = Column(Integer, default=0)  # 评价数量
    favorites_count = Column(Integer, default=0)  # 收藏数量
    open_time = Column(String(100))  # 开放时间
    ticket_price = Column(String(50))  # 门票价格
    need_booking = Column(Boolean, default=False)  # 是否需要预约
    booking_url = Column(String(255))  # 预约链接
    images = Column(JSON)  # 图片列表
    photo_spots = Column(JSON)  # 拍照点位推荐
    tags = Column(JSON)  # 标签
    created_at = Column(String, default=datetime.now().isoformat)
    
    # 关联
    buildings = relationship("Building", back_populates="spot", cascade="all, delete-orphan")
    facilities = relationship("Facility", back_populates="spot", cascade="all, delete-orphan")
    restaurants = relationship("Restaurant", back_populates="spot", cascade="all, delete-orphan")


class Building(Base):
    """建筑物表（每个景区≥20个）"""
    __tablename__ = "buildings"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    spot_id = Column(Integer, ForeignKey("scenic_spots.id", ondelete="CASCADE"))
    name = Column(String(100), nullable=False)
    type = Column(String(50))  # 'attraction'景点, 'teaching'教学楼, 'office'办公楼, 'dorm'宿舍楼
    location_lat = Column(Float)
    location_lng = Column(Float)
    floor_count = Column(Integer)  # 楼层数
    description = Column(Text)
    open_time = Column(String(100))
    images = Column(JSON)
    
    spot = relationship("ScenicSpot", back_populates="buildings")


class Facility(Base):
    """服务设施表（≥10种，≥50个）"""
    __tablename__ = "facilities"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    spot_id = Column(Integer, ForeignKey("scenic_spots.id", ondelete="CASCADE"))
    name = Column(String(100), nullable=False)
    type = Column(String(50))  # shop商店, restaurant饭店, toilet洗手间, library图书馆, canteen食堂, supermarket超市, cafe咖啡馆, clinic医务室, bank银行, parking停车场等
    location_lat = Column(Float)
    location_lng = Column(Float)
    description = Column(Text)
    open_time = Column(String(100))
    
    spot = relationship("ScenicSpot", back_populates="facilities")


class RoadNode(Base):
    """道路节点表（用于图算法）"""
    __tablename__ = "road_nodes"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    spot_id = Column(Integer, ForeignKey("scenic_spots.id", ondelete="CASCADE"))
    name = Column(String(100))
    location_lat = Column(Float)
    location_lng = Column(Float)
    node_type = Column(String(50))  # 'entrance'入口, 'building'建筑, 'crossing'路口, 'facility'设施
    ref_id = Column(Integer)  # 关联的 building_id 或 facility_id
    
    spot = relationship("ScenicSpot")


class RoadEdge(Base):
    """道路边表（≥200条）"""
    __tablename__ = "road_edges"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    spot_id = Column(Integer, ForeignKey("scenic_spots.id", ondelete="CASCADE"))
    from_node_id = Column(Integer, ForeignKey("road_nodes.id"))
    to_node_id = Column(Integer, ForeignKey("road_nodes.id"))
    distance = Column(Float)  # 距离（米）
    ideal_speed = Column(Float)  # 理想速度（米/秒）
    congestion_factor = Column(Float, default=1.0)  # 拥挤度 0-1
    road_type = Column(String(50))  # 'walk'步行道, 'bike'自行车道, 'car'车行道, 'shuttle'电瓶车路线
    is_bidirectional = Column(Boolean, default=True)
    
    spot = relationship("ScenicSpot")


class Trip(Base):
    """行程表"""
    __tablename__ = "trips"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String(100), nullable=False)
    destination = Column(String(50))  # 目的地名称
    destination_spot_id = Column(Integer, ForeignKey("scenic_spots.id"))
    start_date = Column(Date)
    end_date = Column(Date)
    total_days = Column(Integer)
    travel_preferences = Column(JSON)  # 旅行偏好标签
    accommodation_lat = Column(Float)
    accommodation_lng = Column(Float)
    accommodation_address = Column(String(255))
    status = Column(String(20), default='draft')  # draft/published/completed
    created_at = Column(String, default=datetime.now().isoformat)
    updated_at = Column(String, default=datetime.now().isoformat)
    
    daily_schedules = relationship("TripDailySchedule", back_populates="trip", cascade="all, delete-orphan")


class TripDailySchedule(Base):
    """行程-景点关联表（每天的安排）"""
    __tablename__ = "trip_daily_schedule"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    trip_id = Column(Integer, ForeignKey("trips.id", ondelete="CASCADE"))
    day_number = Column(Integer)  # 第几天
    spot_id = Column(Integer, ForeignKey("scenic_spots.id"))
    order_index = Column(Integer)  # 当天顺序
    visit_time_start = Column(String)  # 计划到达时间
    visit_time_end = Column(String)  # 计划离开时间
    transport_mode = Column(String(20))  # walk步行、bike自行车、shuttle电瓶车
    notes = Column(Text)
    
    trip = relationship("Trip", back_populates="daily_schedules")
    spot = relationship("ScenicSpot")


class Restaurant(Base):
    """美食/餐厅表"""
    __tablename__ = "restaurants"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    spot_id = Column(Integer, ForeignKey("scenic_spots.id", ondelete="CASCADE"))
    name = Column(String(100), nullable=False)
    cuisine_type = Column(String(50))  # 菜系
    location_lat = Column(Float)
    location_lng = Column(Float)
    rating = Column(Float, default=0)
    heat_score = Column(Integer, default=0)  # 热度
    price_range = Column(String(20))  # 价格区间
    open_time = Column(String(100))
    images = Column(JSON)
    tags = Column(JSON)
    
    spot = relationship("ScenicSpot", back_populates="restaurants")


class TravelDiary(Base):
    """旅游日记表"""
    __tablename__ = "travel_diaries"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    trip_id = Column(Integer, ForeignKey("trips.id"))
    title = Column(String(200), nullable=False)
    content = Column(Text)  # 日记内容
    content_compressed = Column(BLOB)  # 压缩后的内容
    compression_algorithm = Column(String(20))  # 压缩算法
    diary_type = Column(String(20), default='travel')  # 日记类型: travel/food/photo/notes
    is_public = Column(Boolean, default=False)  # 是否公开
    images = Column(JSON)  # 图片列表
    videos = Column(JSON)  # 视频列表
    itinerary = Column(JSON)  # 时间轴行程数据 [{day, title, spots: [{time, description, location}]}]
    budget = Column(String(50))  # 预算
    companion = Column(String(50))  # 同行伙伴
    view_count = Column(Integer, default=0)  # 浏览量
    avg_rating = Column(Float, default=0)  # 平均评分
    rating_count = Column(Integer, default=0)  # 评分人数
    ai_animation_url = Column(String(255))  # AI生成的旅游动画
    status = Column(String(20), default='published')
    created_at = Column(String, default=datetime.now().isoformat)
    updated_at = Column(String, default=datetime.now().isoformat)


class DiaryRating(Base):
    """日记评分表"""
    __tablename__ = "diary_ratings"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    diary_id = Column(Integer, ForeignKey("travel_diaries.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.id"))
    rating = Column(Integer)  # 1-5星
    created_at = Column(String, default=datetime.now().isoformat)


class DiaryComment(Base):
    """日记评论表"""
    __tablename__ = "diary_comments"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    diary_id = Column(Integer, ForeignKey("travel_diaries.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.id"))
    parent_id = Column(Integer, ForeignKey("diary_comments.id"), nullable=True)  # 回复的评论ID
    content = Column(Text, nullable=False)  # 评论内容
    like_count = Column(Integer, default=0)  # 点赞数
    is_deleted = Column(Boolean, default=False)  # 是否删除
    created_at = Column(String, default=datetime.now().isoformat)
    updated_at = Column(String, default=datetime.now().isoformat)


class Collection(Base):
    """用户收藏景点表"""
    __tablename__ = "collections"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    spot_id = Column(Integer, ForeignKey("scenic_spots.id"))
    created_at = Column(String, default=datetime.now().isoformat)


class SpotReview(Base):
    """景点评价表"""
    __tablename__ = "spot_reviews"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    spot_id = Column(Integer, ForeignKey("scenic_spots.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.id"))
    rating = Column(Float, nullable=False)  # 评分 1-5
    content = Column(Text)  # 评价内容
    images = Column(JSON)  # 评价图片
    created_at = Column(String, default=datetime.now().isoformat)
    updated_at = Column(String, default=datetime.now().isoformat)


class TripPhoto(Base):
    """行程照片表"""
    __tablename__ = "trip_photos"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    trip_id = Column(Integer, ForeignKey("trips.id"))
    photo_url = Column(String(255))
    description = Column(String(255))
    created_at = Column(String, default=datetime.now().isoformat())


class PhotoSpot(Base):
    """景点拍照点位表"""
    __tablename__ = "photo_spots"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    spot_id = Column(Integer, ForeignKey("scenic_spots.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String(100), nullable=False)  # 点位名称
    description = Column(Text)  # 点位描述
    image = Column(String(255))  # 点位图片URL
    created_at = Column(String, default=datetime.now().isoformat)


# ============================================
# 日记城市标签功能（新增，完全独立）
# ============================================

class DiaryCity(Base):
    """日记城市标签库"""
    __tablename__ = "diary_cities"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)  # 城市名称
    diary_count = Column(Integer, default=0)  # 该城市日记数量
    created_at = Column(String, default=datetime.now().isoformat)
    
    # 关联：一个城市有多个标签记录
    tags = relationship("DiaryCityTag", back_populates="city", cascade="all, delete-orphan")


class DiaryCityTag(Base):
    """日记-城市关联表"""
    __tablename__ = "diary_city_tags"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    diary_id = Column(Integer, ForeignKey("travel_diaries.id", ondelete="CASCADE"))
    city_id = Column(Integer, ForeignKey("diary_cities.id", ondelete="CASCADE"))
    confidence = Column(Float, default=1.0)  # 识别置信度（0-1）
    created_at = Column(String, default=datetime.now().isoformat)
    
    # 关联
    diary = relationship("TravelDiary")
    city = relationship("DiaryCity", back_populates="tags")
    
    # 唯一约束：避免重复关联
    __table_args__ = (
        UniqueConstraint('diary_id', 'city_id', name='unique_diary_city'),
    )


# 数据库初始化
engine = create_engine(f'sqlite:///{DB_PATH}', echo=False)
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
