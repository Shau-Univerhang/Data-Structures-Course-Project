"""
小红书链接解析API
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
import requests
import json
import sys
import re
sys.path.append("..")

from models.database import get_db, Trip, TripDailySchedule, ScenicSpot

router = APIRouter()


# MiniMax API配置 - 使用正确的配置
MINIMAX_API_KEY = "sk-cp-eENF_3JXbnNR0MFbfGZJqpW6Yxq-W6Qt_9YjNoI5EFCL63wekVwj0y3z1OJdugX17zIGqN51KDheUiJCp3MnrC_LJlAuOpgah92L-r4YEED2Y7h31-tTtPc"
MINIMAX_API_BASE = "https://api.minimaxi.com/anthropic"


class XiaohongshuParseRequest(BaseModel):
    url: str
    content: Optional[str] = None


def call_minimax(prompt: str, temperature: float = 0.7) -> str:
    """调用MiniMax M2.5 API"""
    url = f"{MINIMAX_API_BASE}/v1/messages"
    
    headers = {
        "Authorization": f"Bearer {MINIMAX_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "MiniMax-M2.5",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 1024,
        "temperature": temperature
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=60)
        result = response.json()
        
        # 检查错误
        if 'base_resp' in result:
            status_code = result['base_resp'].get('status_code', 0)
            if status_code != 0:
                return f"API错误: {result['base_resp'].get('status_msg', '未知错误')}"
        
        # 提取回复内容
        if 'content' in result and len(result['content']) > 0:
            for item in result['content']:
                if item.get('type') == 'text':
                    return item.get('text', '')
        
        return str(result)
    except Exception as e:
        return f"请求失败: {str(e)}"


@router.post("/parse")
def parse_xiaohongshu(
    request: XiaohongshuParseRequest,
    db: Session = Depends(get_db)
):
    """解析小红书链接，提取行程信息"""
    
    url = request.url
    
    # 构建Prompt让AI分析链接内容
    prompt = f"""你是一个专业的旅行规划助手。用户分享了一个小红书旅行链接，请分析并提取其中的行程信息。

小红书链接：{url}

请从以下方面分析提取信息：
1. 目的地城市
2. 旅行天数
3. 主要景点
4. 美食推荐
5. 住宿建议

请以JSON格式输出：
{{
    "title": "行程标题",
    "destination": "目的地城市",
    "days": 天数,
    "spots": ["景点1", "景点2", ...],
    "food": ["美食1", "美食2", ...],
    "summary": "行程摘要",
    "preferences": ["偏好标签1", "偏好标签2"]
}}

如果无法提取详细信息，请返回默认结构：
{{
    "title": "小红书行程导入",
    "destination": "北京",
    "days": 3,
    "spots": ["故宫", "天坛", "颐和园"],
    "food": [],
    "summary": "请手动完善行程信息",
    "preferences": ["必玩景点"]
}}
"""
    
    # 调用MiniMax API分析
    result = call_minimax(prompt)
    
    itinerary = None
    if result:
        try:
            # 尝试解析JSON
            json_match = re.search(r'\{[\s\S]*\}', result)
            if json_match:
                itinerary = json.loads(json_match.group())
        except Exception as e:
            print(f"Parse error: {e}")
    
    # 如果没有解析结果，提供默认结构
    if not itinerary:
        itinerary = {
            "title": "小红书行程导入",
            "destination": "北京",
            "days": 3,
            "spots": ["故宫", "天坛", "颐和园"],
            "food": [],
            "summary": "请手动完善行程信息",
            "preferences": ["必玩景点", "历史文化"]
        }
    
    return {
        "success": True,
        "url": url,
        "itinerary": itinerary,
        "content": result
    }


@router.post("/generate")
def generate_from_xiaohongshu(
    request: XiaohongshuParseRequest,
    db: Session = Depends(get_db)
):
    """根据小红书内容生成完整行程"""
    
    # 首先解析
    parse_result = parse_xiaohongshu(request, db)
    itinerary = parse_result.get("itinerary", {})
    
    # 使用解析的信息生成详细攻略
    destination = itinerary.get("destination", "北京")
    days = itinerary.get("days", 3)
    spots = itinerary.get("spots", [])
    
    # 构建生成Prompt
    prompt = f"""你是一个专业的旅行规划师。请根据以下从小红书提取的信息，生成一份详细的{destination}{days}日游行程。

小红书提取的信息：
- 目的地：{destination}
- 天数：{days}天
- 景点：{', '.join(spots) if spots else '待定'}
- 美食：{', '.join(itinerary.get('food', [])) if itinerary.get('food') else '待定'}

请生成详细的行程安排，要求：
1. 每天的行程要合理分配景点
2. 包含具体的时间安排
3. 推荐当地美食
4. 给出实用的小贴士

请以JSON格式输出：
{{
    "title": "行程标题",
    "destination": "目的地",
    "days": 天数,
    "daily_plan": [
        {{
            "day": 1,
            "theme": "主题",
            "morning": {{"spot": "上午景点", "time": "时间", "tips": "提示"}},
            "noon": {{"spot": "中午用餐", "restaurant": "餐厅", "dish": "推荐菜"}},
            "afternoon": {{"spot": "下午景点", "time": "时间", "tips": "提示"}},
            "evening": {{"spot": "晚间活动", "restaurant": "晚餐", "tips": "提示"}}
        }}
    ],
    "tips": ["贴士1", "贴士2"]
}}
"""
    
    # 调用MiniMax生成详细行程
    guide_result = call_minimax(prompt)
    
    guide_data = None
    if guide_result:
        try:
            json_match = re.search(r'\{[\s\S]*\}', guide_result)
            if json_match:
                guide_data = json.loads(json_match.group())
        except Exception as e:
            print(f"Guide parse error: {e}")
    
    return {
        "success": True,
        "itinerary": itinerary,
        "guide": guide_data,
        "raw_response": guide_result
    }


@router.post("/create-trip")
def create_trip_from_xiaohongshu(
    request: XiaohongshuParseRequest,
    db: Session = Depends(get_db)
):
    """直接从小红书链接创建行程"""
    
    # 如果前端传递了content（解析后的行程数据），直接使用
    if request.content:
        try:
            itinerary = json.loads(request.content)
        except:
            # 解析失败，调用解析API
            parse_result = parse_xiaohongshu(request, db)
            itinerary = parse_result.get("itinerary", {})
    else:
        # 解析链接
        parse_result = parse_xiaohongshu(request, db)
        itinerary = parse_result.get("itinerary", {})
    
    # 创建行程
    trip = Trip(
        user_id=1,
        title=itinerary.get("title", "小红书行程"),
        destination=itinerary.get("destination", "北京"),
        total_days=itinerary.get("days", 3),
        travel_preferences=itinerary.get("preferences", []),
        status="draft"
    )
    
    db.add(trip)
    db.commit()
    db.refresh(trip)
    
    # 获取景点并添加到行程
    # 优先使用前端传递的按天数分配的景点
    day_spots = itinerary.get("daySpots", {})
    spots = itinerary.get("spots", [])
    
    print(f"Creating trip with day_spots: {day_spots}")
    print(f"Spots: {spots}")
    
    if day_spots and len(day_spots) > 0:
        # 使用前端分配的景点（按天）
        order_index = 0
        for day_num, day_spot_list in day_spots.items():
            print(f"Processing day {day_num}: {day_spot_list}")
            for spot_name in day_spot_list:
                # 查找景点
                spot = db.query(ScenicSpot).filter(
                    ScenicSpot.name.like(f"%{spot_name}%")
                ).first()
                
                if spot:
                    print(f"Found spot in DB: {spot.name}")
                    schedule = TripDailySchedule(
                        trip_id=trip.id,
                        day_number=int(day_num),
                        spot_id=spot.id,
                        order_index=order_index
                    )
                    db.add(schedule)
                    order_index += 1
                else:
                    # 如果数据库中找不到景点，创建一个虚拟景点
                    print(f"Creating virtual spot: {spot_name}")
                    
                    # 尝试查找数据库中是否有相似景点的图片
                    similar_spot = db.query(ScenicSpot).filter(
                        ScenicSpot.name.contains(spot_name[:2]),  # 使用前两个字匹配
                        ScenicSpot.images.isnot(None)
                    ).first()
                    
                    if similar_spot and similar_spot.images:
                        images = similar_spot.images
                        print(f"Using images from similar spot: {similar_spot.name}")
                    else:
                        images = ["/images/default-spot.jpg"]
                    
                    virtual_spot = ScenicSpot(
                        name=spot_name,
                        city=itinerary.get("destination", "未知"),
                        description=f"AI推荐的景点：{spot_name}",
                        rating=4.5,
                        images=images,
                        tags=["AI推荐"]
                    )
                    db.add(virtual_spot)
                    db.commit()
                    db.refresh(virtual_spot)
                    
                    schedule = TripDailySchedule(
                        trip_id=trip.id,
                        day_number=int(day_num),
                        spot_id=virtual_spot.id,
                        order_index=order_index
                    )
                    db.add(schedule)
                    order_index += 1
        
        db.commit()
        print(f"Added {order_index} schedules to trip {trip.id}")
    elif spots:
        # 使用默认分配（每3个景点一天）
        print(f"Using default distribution for {len(spots)} spots")
        for i, spot_name in enumerate(spots):
            # 查找景点
            spot = db.query(ScenicSpot).filter(
                ScenicSpot.name.like(f"%{spot_name}%")
            ).first()
            
            if spot:
                print(f"Found spot in DB: {spot.name}")
                schedule = TripDailySchedule(
                    trip_id=trip.id,
                    day_number=(i // 3) + 1,
                    spot_id=spot.id,
                    order_index=i
                )
                db.add(schedule)
            else:
                # 如果数据库中找不到景点，创建一个虚拟景点
                print(f"Creating virtual spot: {spot_name}")
                
                # 尝试查找数据库中是否有相似景点的图片
                similar_spot = db.query(ScenicSpot).filter(
                    ScenicSpot.name.contains(spot_name[:2]),  # 使用前两个字匹配
                    ScenicSpot.images.isnot(None)
                ).first()
                
                if similar_spot and similar_spot.images:
                    images = similar_spot.images
                    print(f"Using images from similar spot: {similar_spot.name}")
                else:
                    images = ["/images/default-spot.jpg"]
                
                virtual_spot = ScenicSpot(
                    name=spot_name,
                    city=itinerary.get("destination", "未知"),
                    description=f"AI推荐的景点：{spot_name}",
                    rating=4.5,
                    images=images,
                    tags=["AI推荐"]
                )
                db.add(virtual_spot)
                db.commit()
                db.refresh(virtual_spot)
                
                schedule = TripDailySchedule(
                    trip_id=trip.id,
                    day_number=(i // 3) + 1,
                    spot_id=virtual_spot.id,
                    order_index=i
                )
                db.add(schedule)
        
        db.commit()
        print(f"Added {len(spots)} schedules to trip {trip.id}")
    
    return {
        "success": True,
        "trip_id": trip.id,
        "trip": {
            "id": trip.id,
            "title": trip.title,
            "destination": trip.destination,
            "days": trip.total_days
        },
        "itinerary": itinerary
    }
