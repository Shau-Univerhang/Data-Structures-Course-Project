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
import urllib.parse
sys.path.append("..")

from models.database import get_db, Trip, TripDailySchedule, ScenicSpot

router = APIRouter()


# MiniMax API配置 - 使用正确的配置
MINIMAX_API_KEY = "sk-cp-eENF_3JXbnNR0MFbfGZJqpW6Yxq-W6Qt_9YjNoI5EFCL63wekVwj0y3z1OJdugX17zIGqN51KDheUiJCp3MnrC_LJlAuOpgah92L-r4YEED2Y7h31-tTtPc"
MINIMAX_API_BASE = "https://api.minimaxi.com/anthropic"


class XiaohongshuParseRequest(BaseModel):
    url: str
    content: Optional[str] = None


class ExtractItineraryRequest(BaseModel):
    content: str


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
        "max_tokens": 2048,
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


def extract_note_id_from_url(url: str) -> Optional[str]:
    """从小红书链接中提取笔记ID"""
    # 匹配 /discovery/item/xxxx 或 /item/xxxx 格式
    patterns = [
        r'/discovery/item/([a-zA-Z0-9]+)',
        r'/item/([a-zA-Z0-9]+)',
        r'item/([a-zA-Z0-9]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None


def fetch_xiaohongshu_content(url: str) -> dict:
    """
    尝试获取小红书笔记内容
    由于小红书有反爬机制，这里使用多种策略尝试获取内容
    """
    result = {
        "success": False,
        "title": "",
        "content": "",
        "images": [],
        "error": ""
    }
    
    # 提取笔记ID
    note_id = extract_note_id_from_url(url)
    if not note_id:
        result["error"] = "无法从链接中提取笔记ID"
        return result
    
    result["note_id"] = note_id
    
    # 策略1: 尝试直接请求（通常会被反爬阻止）
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': 'https://www.xiaohongshu.com/',
        }
        
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        
        if response.status_code == 200:
            html = response.text
            
            # 尝试提取标题
            title_match = re.search(r'<title>(.*?)</title>', html, re.DOTALL)
            if title_match:
                title = title_match.group(1).strip()
                # 清理标题
                title = re.sub(r'\s+', ' ', title)
                if title and title != '小红书':
                    result["title"] = title
            
            # 尝试提取meta description作为内容
            desc_match = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']+)', html, re.IGNORECASE)
            if desc_match:
                result["content"] = desc_match.group(1).strip()
            
            # 如果获取到了内容，标记成功
            if result["title"] or result["content"]:
                result["success"] = True
                return result
                
    except Exception as e:
        result["error"] = f"直接请求失败: {str(e)}"
    
    # 策略2: 尝试使用无头浏览器方案（需要额外安装 playwright）
    # 这里返回需要手动输入的提示
    result["error"] = "小红书有反爬保护，无法自动获取内容"
    result["need_manual_input"] = True
    
    return result


def analyze_content_with_ai(title: str, content: str, url: str) -> dict:
    """使用AI分析小红书内容，提取行程信息"""
    
    prompt = f"""你是一个专业的旅行规划助手。请分析以下小红书旅行笔记内容，提取其中的行程信息。

小红书链接：{url}
笔记标题：{title}
笔记内容：{content}

请仔细阅读内容，从以下方面提取信息：
1. 目的地城市（根据内容判断具体城市）
2. 旅行天数（根据内容提到的天数，默认3天）
3. 主要景点（列出所有提到的景点名称）
4. 美食推荐（列出推荐的美食）
5. 行程摘要（简要描述这个行程）

请以JSON格式输出，只返回JSON，不要有其他文字：
{{
    "title": "行程标题",
    "destination": "目的地城市",
    "days": 天数,
    "spots": ["景点1", "景点2", ...],
    "food": ["美食1", "美食2", ...],
    "summary": "行程摘要",
    "preferences": ["偏好标签1", "偏好标签2"]
}}

如果内容不足以提取完整信息，请根据已有信息合理推断，返回最佳猜测结果。"""
    
    result = call_minimax(prompt, temperature=0.3)
    
    itinerary = None
    if result:
        try:
            # 尝试解析JSON
            json_match = re.search(r'\{{[\s\S]*?\}}', result)
            if json_match:
                itinerary = json.loads(json_match.group())
        except Exception as e:
            print(f"AI解析JSON失败: {e}")
            print(f"AI返回内容: {result}")
    
    return itinerary


@router.post("/parse")
def parse_xiaohongshu(
    request: XiaohongshuParseRequest,
    db: Session = Depends(get_db)
):
    """解析小红书链接，提取行程信息"""
    
    url = request.url
    
    # 步骤1: 尝试获取小红书内容
    fetch_result = fetch_xiaohongshu_content(url)
    
    # 步骤2: 如果前端提供了内容（用户手动粘贴），优先使用
    if request.content and len(request.content) > 10:
        # 用户手动提供了内容
        note_content = request.content
        note_title = "用户提供的笔记内容"
        source_type = "manual"
    elif fetch_result.get("success"):
        # 自动获取成功
        note_content = fetch_result.get("content", "")
        note_title = fetch_result.get("title", "")
        source_type = "auto"
    else:
        # 无法获取内容，返回错误提示
        return {
            "success": False,
            "need_manual_input": True,
            "url": url,
            "error": "由于小红书反爬保护，无法自动获取笔记内容",
            "message": "请手动复制笔记的标题和正文内容，粘贴到输入框中",
            "itinerary": None
        }
    
    # 步骤3: 使用AI分析内容
    itinerary = analyze_content_with_ai(note_title, note_content, url)
    
    # 如果AI分析失败，使用默认结构
    if not itinerary:
        # 尝试从URL或内容中猜测目的地
        destination = "北京"  # 默认
        cities = ['北京', '上海', '广州', '深圳', '杭州', '西安', '成都', '重庆', '南京', '苏州',
                  '武汉', '长沙', '厦门', '青岛', '大连', '昆明', '丽江', '大理', '桂林', '三亚',
                  '黄山', '张家界', '西藏', '拉萨', '新疆', '哈尔滨', '长春', '沈阳']
        
        for city in cities:
            if city in note_content or city in note_title:
                destination = city
                break
        
        itinerary = {
            "title": note_title if note_title else "小红书行程导入",
            "destination": destination,
            "days": 3,
            "spots": [],
            "food": [],
            "summary": "请手动完善行程信息",
            "preferences": ["必玩景点"]
        }
    
    return {
        "success": True,
        "url": url,
        "source_type": source_type,
        "itinerary": itinerary,
        "raw_content": {
            "title": note_title,
            "content": note_content[:500] if len(note_content) > 500 else note_content  # 只返回部分内容
        }
    }


@router.post("/parse-with-content")
def parse_xiaohongshu_with_content(
    request: XiaohongshuParseRequest,
    db: Session = Depends(get_db)
):
    """
    解析小红书内容（用户手动粘贴的版本）
    前端应该提供：url（可选）和 content（笔记正文内容）
    """
    content = request.content or ""
    url = request.url or ""
    
    if not content or len(content.strip()) < 10:
        return {
            "success": False,
            "error": "内容太短，请提供完整的笔记内容",
            "itinerary": None
        }
    
    # 尝试从内容中提取标题（第一行或前50字）
    lines = content.strip().split('\n')
    title = lines[0][:50] if lines else "小红书行程"
    
    # 使用AI分析内容
    itinerary = analyze_content_with_ai(title, content, url)
    
    if not itinerary:
        return {
            "success": False,
            "error": "AI分析失败，请检查内容格式",
            "itinerary": None
        }
    
    return {
        "success": True,
        "url": url,
        "source_type": "manual_content",
        "itinerary": itinerary
    }


def extract_itinerary_with_ai(content: str) -> dict:
    """
    使用AI从内容中提取行程信息
    直接参考前端 extractItineraryWithAI 的实现
    """
    # 构建提取提示词 - 完全复制前端的提示词
    extract_prompt = f"""请从以下旅行笔记内容中提取行程信息，并按照固定格式返回。

笔记内容：
{content}

请提取以下信息并以JSON格式返回，**重点是将景点按照内容中提到的天数进行分配**：
{{
  "has_route": true/false,  // 是否有具体行程路线
  "destination": "城市名",  // 目的地城市
  "days": 数字,  // 行程天数
  "daySpots": {{  // 按天数分配的景点，这是最重要的字段
    "1": ["第1天景点1", "第1天景点2", ...],
    "2": ["第2天景点1", "第2天景点2", ...],
    ...
  }},
  "spots": ["景点1", "景点2", ...],  // 所有景点列表（可选，用于展示）
  "food": ["美食1", "美食2", ...],  // 美食推荐，最多4个
  "title": "行程标题"  // 如"北京3日游"
}}

**重要说明**：
- 请仔细阅读内容，根据"Day 1"、"第一天"、"第1天"等标识，将景点分配到对应的天数
- 例如：如果内容"Day 1: 天安门、故宫"，则 daySpots["1"] = ["天安门", "故宫"]
- 如果内容"第二天：长城、颐和园"，则 daySpots["2"] = ["长城", "颐和园"]

如果内容中没有具体行程路线（只是闲聊、问候、或没有提到具体景点），请返回：
{{
  "has_route": false
}}

注意：
- 只返回JSON格式，不要返回其他文字
- 景点名称要简洁，不要包含时间、价格等额外信息
- 天数根据内容中的"Day X"、"第X天"、"第X日"等信息判断
- 目的地根据内容中的城市名判断
- **重要：如果景点名称中包含"/"、"\"或"、"（如"鸟巢/水立方"），请将其拆分为多个独立景点（如["鸟巢", "水立方"]）**"""

    # 调用MiniMax API - 使用travel-chat相同的配置
    result = call_minimax(extract_prompt, temperature=0.3)
    
    if not result:
        return {"has_route": False, "error": "AI返回为空"}
    
    # 从AI回复中解析JSON
    try:
        json_match = re.search(r'\{[\s\S]*\}', result)
        if json_match:
            extracted = json.loads(json_match.group())
            return extracted
    except Exception as e:
        print(f"解析AI返回失败: {e}")
        print(f"AI返回内容: {result}")
    
    return {"has_route": False, "error": "解析失败"}


@router.post("/extract-itinerary")
def extract_itinerary_from_content(
    request: ExtractItineraryRequest,
    db: Session = Depends(get_db)
):
    """
    从用户粘贴的笔记内容中提取行程信息
    """
    content = request.content.strip()
    
    if not content or len(content) < 10:
        return {
            "success": False,
            "error": "内容太短，请提供完整的笔记内容（至少10个字符）",
            "itinerary": None
        }
    
    # 使用AI提取行程 - 完全参考前端逻辑
    extracted = extract_itinerary_with_ai(content)
    
    # 判断是否有行程
    if extracted.get("has_route") is True:
        # 有路线，创建行程（使用AI分配的daySpots）
        days = extracted.get("days") or len(extracted.get("daySpots", {})) or 3
        
        # 如果没有daySpots，但有spots，则平均分配
        day_spots = extracted.get("daySpots", {})
        spots = extracted.get("spots", [])
        
        if not day_spots and spots:
            spots_per_day = max(1, len(spots) // days)
            for i in range(1, days + 1):
                start_idx = (i - 1) * spots_per_day
                end_idx = min(start_idx + spots_per_day, len(spots))
                if start_idx < len(spots):
                    day_spots[str(i)] = spots[start_idx:end_idx]
        
        # 收集所有景点
        all_spots = []
        if day_spots:
            all_spots = [spot for day_spots_list in day_spots.values() for spot in day_spots_list]
        if not all_spots and spots:
            all_spots = spots
        
        itinerary = {
            "title": extracted.get("title", "行程"),
            "destination": extracted.get("destination", "未知目的地"),
            "days": days,
            "spots": all_spots,
            "daySpots": day_spots,
            "food": extracted.get("food", []),
            "preferences": ["必玩景点"]
        }
        
        return {
            "success": True,
            "itinerary": itinerary
        }
    else:
        # 没有行程
        return {
            "success": False,
            "error": "无法从内容中识别行程信息",
            "itinerary": None
        }


def find_existing_spot(db, spot_name: str, city: str) -> ScenicSpot:
    """
    智能查找已存在的景点
    处理各种匹配情况：
    1. 直接包含匹配
    2. 去除/分隔符后匹配
    3. 常见别名映射
    """
    # 常见别名映射
    alias_map = {
        "国家博物院": "国家博物馆",
        "博物院": "博物馆",
        "鸟巢/水立方": "鸟巢",
        "水立方/鸟巢": "鸟巢",
        "王府井小吃街": "王府井",
        "故宫博物院": "故宫",
    }
    
    # 1. 先尝试直接匹配
    spot = db.query(ScenicSpot).filter(
        ScenicSpot.name.like(f"%{spot_name}%"),
        ScenicSpot.city == city
    ).first()
    
    if spot:
        return spot
    
    # 2. 尝试别名映射
    if spot_name in alias_map:
        alias_name = alias_map[spot_name]
        spot = db.query(ScenicSpot).filter(
            ScenicSpot.name.like(f"%{alias_name}%"),
            ScenicSpot.city == city
        ).first()
        if spot:
            return spot
    
    # 3. 处理/分隔的情况（如"鸟巢/水立方"）
    if "/" in spot_name or "\\" in spot_name or "、" in spot_name:
        parts = re.split(r'[/\\、]', spot_name)
        for part in parts:
            part = part.strip()
            if len(part) >= 2:
                spot = db.query(ScenicSpot).filter(
                    ScenicSpot.name.like(f"%{part}%"),
                    ScenicSpot.city == city
                ).first()
                if spot:
                    return spot
    
    # 4. 尝试反向包含（数据库景点名包含在输入中）
    all_spots = db.query(ScenicSpot).filter(ScenicSpot.city == city).all()
    for existing_spot in all_spots:
        if existing_spot.name in spot_name:
            return existing_spot
    
    return None


@router.post("/generate")
def generate_from_xiaohongshu(
    request: XiaohongshuParseRequest,
    db: Session = Depends(get_db)
):
    """根据小红书内容生成完整行程"""
    
    # 首先解析
    parse_result = parse_xiaohongshu(request, db)
    
    if not parse_result.get("success"):
        return parse_result
    
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
}}"""
    
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
    
    # 获取目的地城市
    destination_city = itinerary.get("destination", "北京")
    
    if day_spots and len(day_spots) > 0:
        # 使用前端分配的景点（按天）
        order_index = 0
        for day_num, day_spot_list in day_spots.items():
            print(f"Processing day {day_num}: {day_spot_list}")
            for spot_name in day_spot_list:
                # 使用智能查找函数查找景点
                spot = find_existing_spot(db, spot_name, destination_city)
                
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
                    # 找不到景点，跳过（不再创建虚拟景点）
                    print(f"Spot not found, skipping: {spot_name}")
        
        db.commit()
        print(f"Added {order_index} schedules to trip {trip.id}")
    elif spots:
        # 使用默认分配（每3个景点一天）
        print(f"Using default distribution for {len(spots)} spots")
        added_count = 0
        for i, spot_name in enumerate(spots):
            # 使用智能查找函数查找景点
            spot = find_existing_spot(db, spot_name, destination_city)
            
            if spot:
                print(f"Found spot in DB: {spot.name}")
                schedule = TripDailySchedule(
                    trip_id=trip.id,
                    day_number=(i // 3) + 1,
                    spot_id=spot.id,
                    order_index=i
                )
                db.add(schedule)
                added_count += 1
            else:
                # 找不到景点，跳过（不再创建虚拟景点）
                print(f"Spot not found, skipping: {spot_name}")
        
        db.commit()
        print(f"Added {added_count} schedules to trip {trip.id}")
    
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
