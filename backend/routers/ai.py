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

import os

# MiniMax API配置
MINIMAX_API_KEY = "sk-cp-eENF_3JXbnNR0MFbfGZJqpW6Yxq-W6Qt_9YjNoI5EFCL63wekVwj0y3z1OJdugX17zIGqN51KDheUiJCp3MnrC_LJlAuOpgah92L-r4YEED2Y7h31-tTtPc"
MINIMAX_API_BASE = "https://api.minimax.chat"


# Pydantic模型
class TravelChatRequest(BaseModel):
    message: str
    context: Optional[str] = None
    history: Optional[List[dict]] = None  # 对话历史


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
    url = f"{MINIMAX_API_BASE}/v1/text/chatcompletion_v2"
    
    headers = {
        "Authorization": f"Bearer {MINIMAX_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "MiniMax-M2.5",
        "messages": [{"role": "user", "content": prompt}],
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
        if result.get('choices') and len(result['choices']) > 0:
            content = result['choices'][0]['message'].get('content', '')
            if content:
                # 尝试修复编码
                try:
                    return content.encode('latin1').decode('utf-8')
                except:
                    return content
        
        return str(result)
    except Exception as e:
        return f"请求失败: {str(e)}"


def split_spots_with_slash(spots: list) -> list:
    """分割包含斜杠的景点，如['豫园/城隍庙'] -> ['豫园', '城隍庙']"""
    result = []
    seen = set()
    for spot in spots:
        if '/' in spot:
            # 按斜杠分割
            parts = [p.strip() for p in spot.split('/')]
            # 过滤掉空字符串和太短的，并去重
            for part in parts:
                if len(part) > 1 and part not in seen:
                    result.append(part)
                    seen.add(part)
        else:
            if spot not in seen:
                result.append(spot)
                seen.add(spot)
    return result

def extract_spots_from_reply(reply: str, destination: str) -> list:
    """从AI回复中提取景点列表"""
    spots = []
    
    print(f"Extracting spots from reply for destination: {destination}")
    
    # 1. 匹配时间格式：08:00 📍 景点名
    time_pattern = r'\d{2}:\d{2}\s*[📍\-–—]?\s*([^\n]+)'
    time_matches = re.findall(time_pattern, reply)
    print(f"Time pattern matches: {time_matches}")
    
    for match in time_matches:
        spot = match.strip()
        # 清理景点名称
        spot = re.sub(r'[（(].*?[）)]', '', spot)  # 移除括号内容
        spot = spot.split('：')[0].split(':')[0]  # 移除冒号后的内容
        spot = spot.split('-')[0].split('—')[0]  # 移除横线后的内容
        spot = spot.split('→')[0]  # 移除箭头后的内容
        spot = spot.strip()
        # 过滤掉太短的或太长的，以及包含特定关键词的
        if len(spot) > 2 and len(spot) < 20 and spot not in spots:
            # 过滤掉不是景点的内容（如"午餐"、"晚餐"等）
            if not any(keyword in spot for keyword in ['午餐', '晚餐', '早餐', '用餐', '吃饭', '附近', '建议', '推荐']):
                spots.append(spot)
    
    # 2. 匹配数字列表格式：1. 景点名 或 1、景点名
    if not spots:
        pattern = r'(?:^|\n)\s*\d+[\.、]\s*([^\n]+)'
        matches = re.findall(pattern, reply)
        print(f"Number pattern matches: {matches}")
        
        for match in matches:
            spot = match.strip()
            # 清理景点名称
            spot = re.sub(r'[（(].*?[）)]', '', spot)
            spot = spot.split('：')[0].split(':')[0]
            spot = spot.split('-')[0].split('—')[0]
            spot = spot.split('→')[0]
            spot = spot.strip()
            if len(spot) > 2 and len(spot) < 20 and spot not in spots:
                if not any(keyword in spot for keyword in ['午餐', '晚餐', '早餐', '用餐', '吃饭']):
                    spots.append(spot)
    
    # 3. 匹配箭头分隔的景点：景点A→景点B→景点C
    if not spots:
        arrow_pattern = r'([^\n→]+)→'
        arrow_matches = re.findall(arrow_pattern, reply)
        print(f"Arrow pattern matches: {arrow_matches}")
        for match in arrow_matches:
            spot = match.strip()
            if len(spot) > 2 and len(spot) < 20 and spot not in spots:
                spots.append(spot)
    
    # 4. 匹配常见景点关键词（目的地相关的）
    if len(spots) < 3:  # 如果提取到的景点太少，补充常见景点
        common_spots_map = {
            '北京': ['天安门', '故宫', '长城', '颐和园', '天坛', '王府井', '景山', '北海', '什刹海'],
            '上海': ['外滩', '东方明珠', '豫园', '南京路', '田子坊', '迪士尼', '陆家嘴'],
            '杭州': ['西湖', '灵隐寺', '雷峰塔', '宋城', '河坊街', '千岛湖'],
            '西安': ['兵马俑', '大雁塔', '古城墙', '回民街', '华清池', '大唐不夜城'],
            '成都': ['熊猫基地', '宽窄巷子', '锦里', '武侯祠', '都江堰', '青城山'],
            '重庆': ['洪崖洞', '解放碑', '磁器口', '长江索道', '武隆', '朝天门'],
            '厦门': ['鼓浪屿', '南普陀寺', '厦门大学', '曾厝垵', '环岛路', '中山路'],
            '桂林': ['漓江', '象鼻山', '阳朔', '龙脊梯田', '两江四湖', '银子岩'],
            '丽江': ['丽江古城', '玉龙雪山', '束河古镇', '拉市海', '虎跳峡'],
            '三亚': ['亚龙湾', '天涯海角', '南山寺', '蜈支洲岛', '大东海']
        }
        city_spots = common_spots_map.get(destination, [f"{destination}景点{i+1}" for i in range(6)])
        for spot in city_spots:
            if spot in reply and spot not in spots:
                spots.append(spot)
        # 如果还是没提取到，直接使用该城市的常见景点
        if not spots:
            spots = city_spots[:6]
    
    print(f"Final extracted spots: {spots}")
    
    return spots[:12]  # 最多返回12个景点


@router.post("/travel-chat")
def travel_chat_with_ai(request: TravelChatRequest, db: Session = Depends(get_db)):
    """与AI助手对话 - 支持智能行程推荐和上下文记忆"""
    message = request.message
    history = request.history or []
    
    # 从对话历史中尝试提取已知的行程信息
    history_context = ""
    if history:
        # 提取最近的几轮对话作为上下文
        recent_history = history[-6:]  # 最近3轮对话
        history_context = "\n".join([f"{'用户' if h.get('role') == 'user' else '助手'}: {h.get('content', '')[:100]}" 
                                     for h in recent_history])
    
    # 判断用户是否在询问行程规划
    is_planning_request = any(keyword in message for keyword in 
        ['行程', '规划', '攻略', '路线', '推荐', '怎么玩', '去哪', '旅游', '旅行', '几天', '天游'])
    
    # 尝试从当前消息提取目的地
    destination = None
    days = 3
    
    # 常见城市匹配
    cities = ['北京', '上海', '广州', '深圳', '杭州', '西安', '成都', '重庆', '南京', '苏州', 
              '武汉', '长沙', '厦门', '青岛', '大连', '昆明', '丽江', '大理', '桂林', '三亚',
              '黄山', '张家界', '西藏', '拉萨', '新疆', '哈尔滨', '长春', '沈阳']
    
    for city in cities:
        if city in message:
            destination = city
            break

    # 如果从当前消息没提取到目的地，尝试从历史对话中提取
    if not destination and history:
        for city in cities:
            for h in reversed(history):
                if city in h.get('content', ''):
                    destination = city
                    break
            if destination:
                break
    
    # 提取天数（支持 "3天"、"3日"、"三天"、"三日"、"2日游" 等格式）
    # 先尝试匹配阿拉伯数字
    day_match = re.search(r'(\d+)\s*[天日]', message)
    if day_match:
        days = int(day_match.group(1))
        days = max(1, min(days, 7))  # 限制1-7天
    else:
        # 尝试匹配中文数字
        chinese_numbers = {
            '一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
            '两': 2
        }
        for chinese, num in chinese_numbers.items():
            if f'{chinese}天' in message or f'{chinese}日' in message:
                days = num
                break
    
    if days == 3 and history:
        # 尝试从历史中提取天数（支持阿拉伯数字和中文数字）
        for h in reversed(history):
            content = h.get('content', '')
            # 先尝试匹配阿拉伯数字
            match = re.search(r'(\d+)\s*[天日]', content)
            if match:
                days = int(match.group(1))
                days = max(1, min(days, 7))
                break
            # 尝试匹配中文数字
            chinese_numbers = {
                '一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
                '两': 2
            }
            for chinese, num in chinese_numbers.items():
                if f'{chinese}天' in content or f'{chinese}日' in content:
                    days = num
                    break
            if days != 3:
                break
    
    if is_planning_request and destination:
        # 调用MiniMax API生成行程规划
        
        # 构建提示词
        prompt = f"""你是旅行助手邮邮，请为用户规划{destination}{days}日游行程。

用户问题：{message}

请提供详细的行程规划，包括：
1. 每天的景点安排（按天数分配）
2. 当地特色美食推荐
3. 实用旅行小贴士

请用友好的语气回复，使用Markdown格式。格式如下：

🎉 欢迎来到{destination}！我是邮邮~

太棒了！{destination}是一座充满魅力的城市，{days}天时间可以玩得很精彩！

📋 **推荐行程安排**

**Day 1**: 主题
1. 景点1
2. 景点2
...

**Day 2**: 主题
...

🍜 **美食推荐**: 美食1、美食2、美食3

💡 **小贴士**:
✓ 提示1
✓ 提示2

这个行程你觉得怎么样？可以直接点击下方卡片保存，或者告诉我你想调整哪些地方！"""
        
        # 调用MiniMax API
        ai_reply = call_minimax(prompt, temperature=0.8)
        
        # 检查是否API调用失败
        if ai_reply.startswith("API错误") or ai_reply.startswith("请求失败"):
            # 使用预设数据作为备用
            default_itineraries = {
                "北京": {
                    "spots": ["故宫博物院", "天安门广场", "颐和园", "八达岭长城", "天坛公园", "王府井大街"],
                    "food": ["北京烤鸭", "炸酱面", "豆汁儿", "卤煮火烧"]
                },
                "上海": {
                    "spots": ["外滩", "东方明珠", "南京路步行街", "豫园", "田子坊", "上海迪士尼"],
                    "food": ["小笼包", "生煎包", "蟹壳黄", "排骨年糕"]
                },
                "杭州": {
                    "spots": ["西湖", "灵隐寺", "雷峰塔", "宋城", "河坊街", "千岛湖"],
                    "food": ["西湖醋鱼", "东坡肉", "龙井虾仁", "叫花鸡"]
                }
            }
            city_data = default_itineraries.get(destination, {
                "spots": [f"{destination}著名景点1", f"{destination}著名景点2", f"{destination}著名景点3"],
                "food": ["当地特色美食1", "当地特色美食2"]
            })
            
            # 构建备用回复
            reply = f"""🎉 欢迎来到{destination}！我是邮邮~

太棒了！{destination}是一座充满魅力的城市，{days}天时间可以玩得很精彩！

📋 **推荐行程安排**

"""
            spots_per_day = max(2, len(city_data["spots"]) // days + 1)
            for day in range(1, days + 1):
                reply += f"**Day {day}**: 第{day}天行程\n"
                start_idx = (day - 1) * spots_per_day
                end_idx = min(start_idx + spots_per_day, len(city_data["spots"]))
                day_spots = city_data["spots"][start_idx:end_idx] if start_idx < len(city_data["spots"]) else [city_data["spots"][0]]
                for i, spot in enumerate(day_spots, 1):
                    reply += f"{i}. {spot}\n"
                reply += "\n"
            
            reply += f"""
🍜 **美食推荐**: {', '.join(city_data['food'][:3])}

💡 **小贴士**:
✓ 提前预订热门景点门票
✓ 带好身份证
✓ 穿舒适的鞋子

这个行程你觉得怎么样？可以直接点击下方卡片保存，或者告诉我你想调整哪些地方！"""
            
            selected_spots = city_data["spots"][:min(days * 3, len(city_data["spots"]))]
        else:
            # 使用AI生成的回复
            reply = ai_reply
            
            # 再次调用AI API，让AI提取景点并按天数分配
            extract_prompt = f"""请从以下行程规划内容中提取景点信息，并按天数分配。

行程内容：
{ai_reply}

用户要求：{destination} {days}天行程

请严格按照原文提取景点，不要添加原文中没有的景点，以JSON格式返回：
{{
    "spots": ["景点1", "景点2", "景点3", ...],
    "daySpots": {{
        "1": ["第1天景点1", "第1天景点2", ...],
        "2": ["第2天景点1", "第2天景点2", ...],
        ...
    }},
    "food": ["美食1", "美食2", ...]
}}

【极其重要的规则 - 必须严格遵守】：
1. 只返回JSON格式，不要返回其他文字
2. **严格按照原文提取景点，不要添加原文中没有的景点**
3. **严禁使用斜杠"/"连接多个景点**，必须将每个景点作为单独的条目
4. 如果原文中有"A/B"、"A/B/C"这种格式（如"豫园/城隍庙"、"武康路/愚园路"），必须拆分成独立的景点条目
5. 错误示例："豫园/城隍庙" ❌
   正确示例：["豫园", "城隍庙"] ✅
6. 错误示例："武康路/愚园路" ❌
   正确示例：["武康路", "愚园路"] ✅
7. 景点名称要简洁，不要包含时间、价格、说明等额外信息
8. daySpots的key是字符串格式的天数（"1", "2", ...）
9. 根据行程内容中的时间安排，将景点分配到对应的天数
10. 如果行程内容没有明确的天数分配，请平均分配到{days}天"""
            
            extract_reply = call_minimax(extract_prompt, temperature=0.3)
            print(f"AI extraction reply: {extract_reply}")
            
            # 解析AI提取的结果
            try:
                # 尝试提取JSON部分
                json_match = re.search(r'\{[\s\S]*\}', extract_reply)
                if json_match:
                    extracted_data = json.loads(json_match[0])
                    selected_spots = extracted_data.get("spots", [])
                    day_spots = extracted_data.get("daySpots", {})
                    food = extracted_data.get("food", ["当地特色美食"])
                    
                    # 强制分割包含斜杠的景点
                    selected_spots = split_spots_with_slash(selected_spots)
                    
                    # 同样处理daySpots中的景点
                    for day_key in day_spots:
                        day_spots[day_key] = split_spots_with_slash(day_spots[day_key])
                    
                    print(f"AI extracted spots after splitting: {selected_spots}")
                    print(f"AI extracted daySpots after splitting: {day_spots}")
                else:
                    selected_spots = extract_spots_from_reply(ai_reply, destination)
                    day_spots = {}
                    food = ["当地特色美食"]
            except Exception as e:
                print(f"Failed to parse AI extraction: {e}")
                selected_spots = extract_spots_from_reply(ai_reply, destination)
                day_spots = {}
                food = ["当地特色美食"]
        
        # 构建行程数据结构
        itinerary = {
            "title": f"{destination}{days}日游",
            "destination": destination,
            "days": days,
            "spots": selected_spots if selected_spots else [f"{destination}热门景点"],
            "daySpots": day_spots if day_spots else {},
            "food": food,
            "preferences": ["必玩景点", "美食体验"]
        }
        
        print(f"Returning itinerary: {itinerary}")
        
        return {
            "reply": reply,
            "message": message,
            "has_itinerary": True,
            "itinerary": itinerary
        }
    else:
        # 普通对话 - 调用MiniMax API
        
        # 构建提示词
        history_context_str = ""
        if history_context:
            history_context_str = f"\n\n之前的对话：\n{history_context}"
        
        prompt = f"""你是旅行助手邮邮，一个友好、专业的AI旅行助手。

用户问题：{message}{history_context_str}

请用友好、自然的语气回复用户。如果用户问的是旅行相关问题，请提供有用的建议；
如果用户问的是非旅行问题，请礼貌地回答并引导用户回到旅行话题。

请用Markdown格式回复，可以适当使用emoji让回复更生动。"""
        
        # 调用MiniMax API
        ai_reply = call_minimax(prompt, temperature=0.8)
        
        # 检查是否API调用失败
        if ai_reply.startswith("API错误") or ai_reply.startswith("请求失败"):
            # 使用备用回复
            message_lower = message.lower()
            if any(word in message_lower for word in ['你好', '嗨', 'hi', 'hello']):
                reply = "你好！我是邮邮 🎒 你的专属旅行助手，可以帮你规划行程、推荐景点和美食。你想去哪里旅行呢？"
            elif any(word in message_lower for word in ['谢谢', '感谢']):
                reply = "不客气！😊 有问题随时找我，祝你旅途愉快！"
            elif any(word in message_lower for word in ['再见', '拜拜', 'bye']):
                reply = "再见！� 期待帮你规划下一次旅行~"
            else:
                reply = "明白你的需求了！😊 我是邮邮，你的旅行助手。我可以帮你规划行程、推荐景点和美食。你想去哪里旅行呢？"
        else:
            reply = ai_reply
        
        return {
            "reply": reply,
            "message": message,
            "has_itinerary": False
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
