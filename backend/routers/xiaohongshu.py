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
    spots = itinerary.get("spots", [])
    if spots:
        for i, spot_name in enumerate(spots):
            # 查找景点
            spot = db.query(ScenicSpot).filter(
                ScenicSpot.name.like(f"%{spot_name}%")
            ).first()
            
            if spot:
                schedule = TripDailySchedule(
                    trip_id=trip.id,
                    day_number=(i // 3) + 1,
                    spot_id=spot.id,
                    order_index=i
                )
                db.add(schedule)
        
        db.commit()
    
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
