"""
AI接口 - 使用MiniMax API (M2.5模型)
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import requests
import json
import sys
import re
sys.path.append("..")

from models.database import get_db, ScenicSpot, Trip, TripDailySchedule

router = APIRouter()

# MiniMax API配置 - 使用正确的配置
MINIMAX_API_KEY = "sk-cp-eENF_3JXbnNR0MFbfGZJqpW6Yxq-W6Qt_9YjNoI5EFCL63wekVwj0y3z1OJdugX17zIGqN51KDheUiJCp3MnrC_LJlAuOpgah92L-r4YEED2Y7h31-tTtPc"
MINIMAX_API_BASE = "https://api.minimaxi.com/anthropic"


# Pydantic模型
class TravelChatRequest(BaseModel):
    message: str
    context: Optional[str] = None


class GenerateGuideRequest(BaseModel):
    destination: str
    days: int
    preferences: List[str] = []
    selected_spots: List[int] = []


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


@router.post("/travel-chat")
def travel_chat_with_ai(request: TravelChatRequest):
    """与AI助手对话 - 调用MiniMax M2.5 API"""
    message = request.message
    
    # 构建提示词
    prompt = f"""你是一个热情的旅行助手"邮邮"，专门帮助用户规划旅行。

用户说：{message}

请用友好的语气回答，可以：
- 询问用户的旅行偏好
- 推荐热门目的地
- 提供旅行建议
- 帮助规划行程
- 当用户要创建行程时，引导用户选择目的地、天数和偏好

注意：
- 使用简体中文
- 适当加入emoji
- 保持简洁有趣
- 根据用户需求给出实用的建议

请直接回答用户的问题。"""
    
    # 调用MiniMax API
    result = call_minimax(prompt)
    
    return {
        "reply": result,
        "message": message
    }


@router.post("/generate")
def generate_travel_guide(
    request: GenerateGuideRequest,
    db: Session = Depends(get_db)
):
    """生成旅游攻略（AI生成）- 调用MiniMax API"""
    
    # 获取选中景点的详细信息
    spots_info = []
    if request.selected_spots:
        spots = db.query(ScenicSpot).filter(
            ScenicSpot.id.in_(request.selected_spots)
        ).all()
        
        for spot in spots:
            spots_info.append({
                'name': spot.name,
                'description': spot.description[:100] if spot.description else '',
                'rating': spot.rating,
                'tags': spot.tags or [],
                'open_time': spot.open_time,
                'ticket_price': spot.ticket_price
            })
    
    # 构建Prompt
    spots_text = ""
    if spots_info:
        spots_text = "\n".join([
            f"- {s['name']}: {s['description']}, 评分:{s['rating']}, 标签:{','.join(s['tags'])}"
            for s in spots_info
        ])
    
    preferences_text = "、".join(request.preferences) if request.preferences else "无"
    
    prompt = f"""你是一个专业的旅行规划师。请为用户规划一次{request.destination}的{request.days}日游。

用户偏好：{preferences_text}

已选景点：
{spots_text}

请生成一份详细的旅游攻略，包含：
1. 行程概要
2. 每日行程安排（包括时间、景点、交通方式）
3. 美食推荐
4. 实用贴士

要求：
- 使用简体中文
- 语气友好、专业
- 行程安排合理
- 突出AI特色，适当加入emoji

请以JSON格式输出：
{{
    "title": "行程标题",
    "days": [
        {{
            "day": 1,
            "theme": "主题",
            "spots": [
                {{"name": "景点名", "time": "时间", "tips": "小贴士"}}
            ],
            "food": "推荐美食"
        }}
    ],
    "tips": ["贴士1", "贴士2"]
}}
"""
    
    result = call_minimax(prompt)
    
    # 尝试解析JSON
    try:
        json_match = re.search(r'\{[\s\S]*\}', result)
        if json_match:
            guide_data = json.loads(json_match.group())
            return guide_data
    except:
        pass
    
    # 如果解析失败，返回原始结果
    return {
        "title": f"{request.destination}{request.days}日游",
        "raw_guide": result,
        "days": []
    }


@router.get("/recommend-destinations")
def recommend_destinations(
    preferences: Optional[str] = Query("", description="偏好标签"),
    db: Session = Depends(get_db)
):
    """AI推荐目的地"""
    
    # 获取热门城市
    cities = db.query(ScenicSpot.city).distinct().limit(20).all()
    city_list = [c[0] for c in cities if c[0]]
    
    prompt = f"""请根据用户偏好推荐旅行目的地。

用户偏好：{preferences if preferences else '无明确偏好'}

可选目的地：{', '.join(city_list)}

请推荐3-5个适合的目的地，并以JSON格式输出：
{{
    "recommendations": [
        {{"city": "城市名", "reason": "推荐理由", "best_season": "最佳旅行季节"}}
    ]
}}
"""
    
    result = call_minimax(prompt)
    
    try:
        json_match = re.search(r'\{[\s\S]*\}', result)
        if json_match:
            data = json.loads(json_match.group())
            return data
    except:
        pass
    
    return {
        "recommendations": [
            {"city": "北京", "reason": "历史文化名城", "best_season": "春秋"}
        ]
    }
