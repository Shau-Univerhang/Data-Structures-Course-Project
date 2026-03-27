"""
行程相关API
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import date
import sys
sys.path.append("..")

from models.database import get_db, Trip, TripDailySchedule, ScenicSpot

router = APIRouter()


# Pydantic模型
class CreateTripRequest(BaseModel):
    title: str
    destination: str
    destination_spot_id: Optional[int] = None
    total_days: int
    travel_preferences: List[str] = []
    accommodation_address: Optional[str] = None


class TripResponse(BaseModel):
    id: int
    title: str
    destination: str
    destination_spot_id: Optional[int] = None
    total_days: int
    travel_preferences: List[str] = []
    accommodation_address: Optional[str] = None
    status: str

    class Config:
        from_attributes = True


class AddSpotRequest(BaseModel):
    spot_id: int
    day_number: int = 1
    order_index: int = 0


class DailyScheduleResponse(BaseModel):
    id: int
    day_number: int
    spot_id: int
    spot_name: Optional[str] = None
    spot_image: Optional[str] = None
    order_index: int
    visit_time_start: Optional[str] = None
    visit_time_end: Optional[str] = None
    transport_mode: Optional[str] = "walk"
    notes: Optional[str] = None

    class Config:
        from_attributes = True


# 路由实现

@router.post("/", response_model=TripResponse)
def create_trip(
    request: CreateTripRequest,
    user_id: int = Query(1, description="用户ID"),  # 简化：默认用户
    db: Session = Depends(get_db)
):
    """创建新行程"""
    trip = Trip(
        user_id=user_id,
        title=request.title,
        destination=request.destination,
        destination_spot_id=request.destination_spot_id,
        total_days=request.total_days,
        travel_preferences=request.travel_preferences,
        accommodation_address=request.accommodation_address,
        status='draft'
    )
    db.add(trip)
    db.commit()
    db.refresh(trip)
    return trip


@router.get("/", response_model=List[TripResponse])
def list_trips(
    user_id: int = Query(1, description="用户ID"),
    status: Optional[str] = Query(None, description="状态筛选"),
    db: Session = Depends(get_db)
):
    """获取用户行程列表"""
    query = db.query(Trip).filter(Trip.user_id == user_id)
    if status:
        query = query.filter(Trip.status == status)
    
    trips = query.order_by(Trip.created_at.desc()).all()
    
    result = []
    for trip in trips:
        result.append({
            'id': trip.id,
            'title': trip.title,
            'destination': trip.destination,
            'total_days': trip.total_days,
            'status': trip.status,
            'created_at': trip.created_at,
            'preferences': trip.travel_preferences or []
        })
    
    return result


@router.get("/{trip_id}")
def get_trip(trip_id: int, db: Session = Depends(get_db)):
    """获取行程详情"""
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        return {"error": "行程不存在"}
    
    # 获取每日安排
    schedules = db.query(TripDailySchedule).filter(
        TripDailySchedule.trip_id == trip_id
    ).order_by(TripDailySchedule.day_number, TripDailySchedule.order_index).all()
    
    schedules_data = []
    for s in schedules:
        spot = db.query(ScenicSpot).filter(ScenicSpot.id == s.spot_id).first()
        schedules_data.append({
            'id': s.id,
            'day_number': s.day_number,
            'spot_id': s.spot_id,
            'spot_name': spot.name if spot else None,
            'spot_image': spot.images[0] if spot and spot.images else None,
            'spot_rating': spot.rating if spot else None,
            'spot_location_lng': spot.location_lng if spot else None,
            'spot_location_lat': spot.location_lat if spot else None,
            'order_index': s.order_index,
            'visit_time_start': s.visit_time_start,
            'visit_time_end': s.visit_time_end,
            'transport_mode': s.transport_mode,
            'notes': s.notes
        })
    
    return {
        'id': trip.id,
        'title': trip.title,
        'destination': trip.destination,
        'total_days': trip.total_days,
        'travel_preferences': trip.travel_preferences or [],
        'status': trip.status,
        'created_at': trip.created_at,
        'schedules': schedules_data
    }


@router.post("/{trip_id}/spots")
def add_spot_to_trip(
    trip_id: int,
    request: AddSpotRequest,
    db: Session = Depends(get_db)
):
    """添加景点到行程"""
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        return {"error": "行程不存在"}
    
    schedule = TripDailySchedule(
        trip_id=trip_id,
        day_number=request.day_number,
        spot_id=request.spot_id,
        order_index=request.order_index
    )
    db.add(schedule)
    db.commit()
    
    # 统计已选景点数量
    count = db.query(TripDailySchedule).filter(
        TripDailySchedule.trip_id == trip_id
    ).count()
    
    return {"success": True, "selected_count": count}


@router.delete("/{trip_id}/spots/{schedule_id}")
def remove_spot_from_trip(
    trip_id: int,
    schedule_id: int,
    db: Session = Depends(get_db)
):
    """从行程中移除景点"""
    schedule = db.query(TripDailySchedule).filter(
        TripDailySchedule.id == schedule_id,
        TripDailySchedule.trip_id == trip_id
    ).first()
    
    if schedule:
        db.delete(schedule)
        db.commit()
    
    return {"success": True}


@router.put("/{trip_id}/spots/reorder")
def reorder_spots(
    trip_id: int,
    schedules: List[dict],
    db: Session = Depends(get_db)
):
    """重新排序行程中的景点"""
    for item in schedules:
        schedule = db.query(TripDailySchedule).filter(
            TripDailySchedule.id == item['id'],
            TripDailySchedule.trip_id == trip_id
        ).first()
        if schedule:
            schedule.day_number = item.get('day_number', schedule.day_number)
            schedule.order_index = item.get('order_index', schedule.order_index)
    
    db.commit()
    return {"success": True}


@router.put("/{trip_id}/status")
def update_trip_status(
    trip_id: int,
    status: str = Query(..., description="状态: draft/published/completed"),
    db: Session = Depends(get_db)
):
    """更新行程状态"""
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if trip:
        trip.status = status
        db.commit()
    return {"success": True}


@router.delete("/{trip_id}")
def delete_trip(trip_id: int, db: Session = Depends(get_db)):
    """删除行程"""
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if trip:
        db.delete(trip)
        db.commit()
    return {"success": True}
