"""
AI接口 - 使用DeepSeek API (deepseek-v4-pro)
"""
from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import requests
import json
import sys
import re
import uuid
import base64
import time
import subprocess
import threading
from datetime import datetime
sys.path.append("..")

from models.database import get_db, ScenicSpot, Trip, TripDailySchedule, Restaurant, TourGuide, TripPhoto, VlogTask
from routers.spots import parse_tags

router = APIRouter()

import os

# LLM配置 (deepseek-v4-pro)
TOUR_GUIDE_LLM_KEY = os.getenv("TOUR_GUIDE_LLM_KEY", "")
TOUR_GUIDE_LLM_BASE = os.getenv("TOUR_GUIDE_LLM_BASE", "https://api.deepseek.com")
TOUR_GUIDE_LLM_MODEL = os.getenv("TOUR_GUIDE_LLM_MODEL", "deepseek-v4-pro")

# AI导游 TTS配置 (火山引擎语音合成)
TTS_API_KEY = os.getenv("TTS_API_KEY", "")
TTS_RESOURCE_ID = os.getenv("TTS_RESOURCE_ID", "seed-tts-2.0")
TTS_ENDPOINT = "https://openspeech.bytedance.com/api/v3/tts/unidirectional"

TTS_STYLE_SPEAKERS = {
    "rational": "zh_female_xiaohe_uranus_bigtts",
    "emotional": "zh_female_jiaochuannv_uranus_bigtts",
    "foodie": "zh_male_zhubajie_uranus_bigtts",
}

# VLOG视频生成配置 (Seedance)
SEEDANCE_API_KEY = os.getenv("SEEDANCE_API_KEY", "")
SEEDANCE_MODEL = os.getenv("SEEDANCE_MODEL", "doubao-seedance-1-0-pro-fast-251015")
SEEDANCE_BASE = "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks"


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


class TourGuideRequest(BaseModel):
    spot_id: int
    style: str = "rational"  # rational, emotional, foodie


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


# ==================== 旅行VLOG视频生成 ====================

class VlogGenerateRequest(BaseModel):
    trip_id: int
    user_id: int = 1
    style: str = "cartoon"  # cartoon, cinematic, realistic

class VlogStatusResponse(BaseModel):
    status: str  # processing, completed, failed
    vlog_url: Optional[str] = None
    progress: str = ""
    shots_total: int = 0
    shots_completed: int = 0


def call_seedance_i2v(image_path: str, prompt: str) -> Optional[str]:
    if image_path.startswith("http://localhost") or image_path.startswith("/"):
        local_path = image_path.replace("http://localhost:8000", "")
        root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        full_path = os.path.join(root, local_path.lstrip("/"))
        if not os.path.exists(full_path):
            return None
        ext = os.path.splitext(full_path)[1].lower().lstrip('.')
        mime = "jpeg" if ext in ("jpg", "jpeg") else ext
        with open(full_path, "rb") as f:
            image_b64 = base64.b64encode(f.read()).decode('utf-8')
        image_url = f"data:image/{mime};base64,{image_b64}"
    else:
        image_url = image_path

    headers = {
        "Authorization": f"Bearer {SEEDANCE_API_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "model": SEEDANCE_MODEL,
        "content": [
            {"type": "text", "text": f"{prompt} --resolution 720p --duration 5 --camerafixed false"},
            {"type": "image_url", "image_url": {"url": image_url}}
        ]
    }
    try:
        resp = requests.post(SEEDANCE_BASE, headers=headers, json=body, timeout=30)
        if resp.status_code not in (200, 201):
            return None
        data = resp.json()
        task_id = data.get("id") or data.get("task_id") or data.get("data", {}).get("id")
        if not task_id:
            return None

        for _ in range(60):
            time.sleep(5)
            poll_resp = requests.get(f"{SEEDANCE_BASE}/{task_id}", headers=headers, timeout=15)
            if poll_resp.status_code != 200:
                continue
            poll_data = poll_resp.json()
            status = poll_data.get("status") or poll_data.get("data", {}).get("status", "")
            if status in ("completed", "succeeded", "done"):
                video_url = poll_data.get("video_url") or \
                            poll_data.get("content", {}).get("video_url") or \
                            poll_data.get("data", {}).get("video_url") or \
                            poll_data.get("output") or \
                            poll_data.get("data", {}).get("output")
                return video_url
            if status in ("failed", "error", "cancelled"):
                return None
        return None
    except Exception:
        return None


def call_seedance_t2v(prompt: str) -> Optional[str]:
    headers = {
        "Authorization": f"Bearer {SEEDANCE_API_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "model": SEEDANCE_MODEL,
        "content": [
            {"type": "text", "text": f"{prompt} --resolution 720p --duration 5 --camerafixed false"}
        ]
    }
    try:
        resp = requests.post(SEEDANCE_BASE, headers=headers, json=body, timeout=30)
        if resp.status_code not in (200, 201):
            return None
        data = resp.json()
        task_id = data.get("id") or data.get("task_id") or data.get("data", {}).get("id")
        if not task_id:
            return None
        for _ in range(60):
            time.sleep(5)
            poll_resp = requests.get(f"{SEEDANCE_BASE}/{task_id}", headers=headers, timeout=15)
            if poll_resp.status_code != 200:
                continue
            poll_data = poll_resp.json()
            status = poll_data.get("status") or poll_data.get("data", {}).get("status", "")
            if status in ("completed", "succeeded", "done"):
                video_url = poll_data.get("video_url") or \
                            poll_data.get("content", {}).get("video_url") or \
                            poll_data.get("data", {}).get("video_url") or \
                            poll_data.get("output") or \
                            poll_data.get("data", {}).get("output")
                return video_url
            if status in ("failed", "error", "cancelled"):
                return None
        return None
    except Exception:
        return None


def generate_vlog_script(trip_info: dict) -> dict:
    trip_title = trip_info.get('title', '')
    destination = trip_info.get('destination', '')
    schedule = trip_info.get('schedule_text', '')

    prompt = f"""你是旅行VLOG导演。请为以下行程的每个景点写一段Seedance视频生成英文prompt。

行程：{trip_title}
目的地：{destination}

行程安排：
{schedule}

任务：行程中有几个景点就生成几段，每段为该景点写一个英文prompt。
格式："cartoon animation style, <景点名称>, <场景描述>, Ghibli inspired, warm lighting --dur 5"

只返回JSON：
{{
    "title": "VLOG标题",
    "spots": [
        {{"scene": "景点名", "prompt": "cartoon animation style, ..."}}
    ]
}}"""
    try:
        result = call_llm(prompt, temperature=0.7)
        json_match = re.search(r'\{[\s\S]*\}', result)
        if json_match:
            return json.loads(json_match.group())
    except Exception:
        pass

    spots = []
    for line in schedule.split("\n"):
        if not line.strip():
            continue
        for spot in line.split("→"):
            spot = spot.strip()
            if spot:
                spots.append({
                    "scene": spot,
                    "prompt": f"cartoon animation style, {spot}, {destination} travel, Ghibli inspired, warm lighting --dur 5"
                })
    return {"title": trip_title, "spots": spots}


_vlog_tasks = {}


def _download_video(video_url: str, trip_id: int) -> str:
    videos_root = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "videos")
    os.makedirs(videos_root, exist_ok=True)
    filename = f"vlog_{trip_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.mp4"
    filepath = os.path.join(videos_root, filename)
    try:
        r = requests.get(video_url, timeout=120, stream=True)
        if r.status_code == 200:
            with open(filepath, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            return filepath
    except Exception:
        pass
    return video_url


def _concat_videos(filepaths: list, trip_id: int) -> str:
    if len(filepaths) == 0:
        return None
    if len(filepaths) == 1:
        return filepaths[0]
    videos_root = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "videos")
    merged_name = f"vlog_{trip_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}_merged.mp4"
    merged_path = os.path.join(videos_root, merged_name)
    list_path = os.path.join(videos_root, f"_concat_{trip_id}.txt")
    try:
        with open(list_path, 'w', encoding='utf-8') as f:
            for fp in filepaths:
                safe_path = fp.replace('\\', '/')
                f.write(f"file '{safe_path}'\n")
        result = subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_path, "-c", "copy", merged_path],
            capture_output=True, timeout=120
        )
        os.remove(list_path)
        if result.returncode == 0 and os.path.exists(merged_path):
            for fp in filepaths:
                if fp != merged_path:
                    try:
                        os.remove(fp)
                    except Exception:
                        pass
            return merged_path
    except Exception:
        pass
    if os.path.exists(list_path):
        os.remove(list_path)
    return filepaths[0]


def _db_task_update(task_id: str, **kwargs):
    try:
        from models.database import SessionLocal
        db2 = SessionLocal()
        task = db2.query(VlogTask).filter(VlogTask.task_id == task_id).first()
        if task:
            for k, v in kwargs.items():
                setattr(task, k, v)
            task.updated_at = datetime.now().isoformat()
            db2.commit()
        db2.close()
    except Exception:
        pass


def _make_photo_path(url: str) -> str:
    local = url.replace("http://localhost:8000", "")
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(root, local.lstrip("/"))


@router.post("/vlog/generate")
def start_vlog_generation(request: VlogGenerateRequest, db: Session = Depends(get_db)):
    trip = db.query(Trip).filter(Trip.id == request.trip_id, Trip.user_id == request.user_id).first()
    if not trip:
        return {"error": "行程不存在"}

    schedules = db.query(TripDailySchedule).filter(TripDailySchedule.trip_id == request.trip_id)\
        .order_by(TripDailySchedule.day_number, TripDailySchedule.order_index).all()
    if not schedules:
        return {"error": "该行程没有安排景点"}

    day_spot_map = {}
    for s in schedules:
        spot_name = s.spot.name if s.spot else f"景点{s.spot_id}"
        day_spot_map.setdefault(s.day_number, []).append(spot_name)
    schedule_text = "\n".join([f"Day{day}: " + " → ".join(spots) for day, spots in sorted(day_spot_map.items())])

    trip_info = {
        "title": trip.title,
        "destination": trip.destination or "",
        "total_days": trip.total_days or len(day_spot_map),
        "schedule_text": schedule_text
    }

    task_id = str(uuid.uuid4())
    now = datetime.now().isoformat()

    if trip.vlog_url and trip.vlog_url.startswith("/videos/"):
        old_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            trip.vlog_url.lstrip("/")
        )
        if os.path.exists(old_path):
            os.remove(old_path)
        trip.vlog_url = None
        db.commit()

    trip_photos = db.query(TripPhoto).filter(TripPhoto.trip_id == request.trip_id).all()
    photos = []
    for p in trip_photos:
        local_path = _make_photo_path(p.photo_url)
        if os.path.exists(local_path):
            with open(local_path, "rb") as f:
                img_b64 = base64.b64encode(f.read()).decode('utf-8')
            ext = os.path.splitext(local_path)[1].lower().lstrip('.')
            mime = "jpeg" if ext in ("jpg", "jpeg") else ext
            photos.append({
                "url": f"data:image/{mime};base64,{img_b64}",
                "description": p.description or "旅行照片"
            })

    spot_count = sum(len(v) for v in day_spot_map.values())
    total_shots = spot_count + len(photos)
    vtask = VlogTask(
        task_id=task_id, trip_id=request.trip_id, user_id=request.user_id,
        status="scripting", progress_text="正在编写分镜脚本...", shots_total=total_shots,
        created_at=now, updated_at=now
    )
    db.add(vtask)
    db.commit()

    def run_vlog():
        try:
            _db_task_update(task_id, progress_text="AI正在为景点编写脚本...", status="scripting")

            script = generate_vlog_script(trip_info)
            spots = script.get("spots", [])
            segments = []
            for s in spots:
                segments.append({"type": "spot", "scene": s.get("scene", ""), "prompt": s.get("prompt", "")})
            for i, p in enumerate(photos):
                segments.append({"type": "photo", "scene": p["description"], "prompt": f"cartoon animation style, {p['description']}, travel memory, warm lighting --dur 5", "photo_url": p["url"]})

            _db_task_update(task_id, status="generating", progress_text="开始生成视频片段...", shots_total=len(segments), shots_completed=0)

            video_urls = []
            for i, seg in enumerate(segments):
                label = seg.get("scene", f"片段{i+1}")
                _db_task_update(task_id, progress_text=f"正在生成第{i+1}/{len(segments)}个: {label}...", shots_completed=i)

                if seg["type"] == "photo":
                    vurl = call_seedance_i2v(seg["photo_url"], seg["prompt"])
                else:
                    vurl = call_seedance_t2v(seg["prompt"])

                if vurl:
                    video_urls.append(vurl)
                _db_task_update(task_id, shots_completed=i + 1)

            if video_urls:
                local_paths = []
                for vurl in video_urls:
                    lp = _download_video(vurl, request.trip_id)
                    if os.path.exists(lp):
                        local_paths.append(lp)
                merged = _concat_videos(local_paths, request.trip_id)
                vlog_path = "/videos/" + os.path.basename(merged) if merged else ""
                _db_task_update(task_id, status="completed", progress_text="VLOG生成完成!", video_url=vlog_path)
                try:
                    from models.database import SessionLocal
                    db3 = SessionLocal()
                    t = db3.query(Trip).filter(Trip.id == request.trip_id).first()
                    if t:
                        t.vlog_url = vlog_path
                        db3.commit()
                    db3.close()
                except Exception:
                    pass
            else:
                _db_task_update(task_id, status="failed", error="视频生成失败", progress_text="视频生成失败")
        except Exception as e:
            _db_task_update(task_id, status="failed", error=str(e), progress_text="生成出错")

    threading.Thread(target=run_vlog, daemon=True).start()
    return {"task_id": task_id, "status": "scripting", "shots_total": total_shots}


@router.get("/vlog/status/{task_id}")
def get_vlog_status(task_id: str, db: Session = Depends(get_db)):
    task = db.query(VlogTask).filter(VlogTask.task_id == task_id).first()
    if not task:
        return {"status": "not_found"}
    return {
        "status": task.status,
        "vlog_url": task.video_url,
        "progress": f"{task.shots_completed}/{task.shots_total}",
        "progress_text": task.progress_text or "",
        "shots_total": task.shots_total,
        "shots_completed": task.shots_completed,
        "error": task.error
    }


@router.get("/vlog/check/{trip_id}")
def check_vlog(trip_id: int, user_id: int = 1, db: Session = Depends(get_db)):
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == user_id).first()
    if not trip or not trip.vlog_url:
        return {"has_vlog": False}
    if trip.vlog_url.startswith("/videos/"):
        local_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            trip.vlog_url.lstrip("/")
        )
        if not os.path.exists(local_path):
            trip.vlog_url = None
            db.commit()
            return {"has_vlog": False}
    return {"has_vlog": True, "vlog_url": trip.vlog_url}

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
            '北京': ['天安门', '故宫', '长城', '颐和园', '天坛', '景山公园', '北海公园', '什刹海', '南锣鼓巷', '圆明园', '鸟巢', '水立方'],
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
        # 调用AI API生成行程规划
        
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
        
        # 调用AI API
        ai_reply = call_llm(prompt, temperature=0.8)
        
        # 检查是否API调用失败
        if ai_reply.startswith("LLM错误") or ai_reply.startswith("LLM调用失败"):
            # 使用预设数据作为备用
            default_itineraries = {
                "北京": {
                    "spots": ["故宫博物院", "天安门广场", "颐和园", "八达岭长城", "天坛公园", "景山公园", "北海公园", "什刹海", "南锣鼓巷", "圆明园"],
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
            
            extract_reply = call_llm(extract_prompt, temperature=0.3)
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
        # 普通对话 - 调用AI API
        
        # 构建提示词
        history_context_str = ""
        if history_context:
            history_context_str = f"\n\n之前的对话：\n{history_context}"
        
        prompt = f"""你是旅行助手邮邮，一个友好、专业的AI旅行助手。

用户问题：{message}{history_context_str}

请用友好、自然的语气回复用户。如果用户问的是旅行相关问题，请提供有用的建议；
如果用户问的是非旅行问题，请礼貌地回答并引导用户回到旅行话题。

请用Markdown格式回复，可以适当使用emoji让回复更生动。"""
        
        # 调用AI API
        ai_reply = call_llm(prompt, temperature=0.8)
        
        # 检查是否API调用失败
        if ai_reply.startswith("LLM错误") or ai_reply.startswith("LLM调用失败"):
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
    """生成旅游攻略（AI生成）"""
    
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
                'tags': parse_tags(spot.tags),
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
    
    result = call_llm(prompt)
    
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
    
    result = call_llm(prompt)
    
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


# ==================== AI语音导游 ====================

TOUR_GUIDE_PROMPTS = {
    "rational": """你是一位专业的历史文化导游，风格理性、严谨、数据驱动。
请为景点"{spot_name}"（位于{spot_city}）撰写一份约300字的语音导游词。

景点简介：{description}
景点标签：{tags}
开放时间：{open_time}
门票：{ticket_price}

要求：
- 语言精炼、信息密度高
- 重点介绍历史背景、建筑特色、文化价值
- 引用具体数据（年代、面积、规模等）
- 语气专业但不生硬，像一位博学的导游
- 结尾用一句话总结这个景点的核心价值""",

    "emotional": """你是一位擅长讲故事的文艺导游，风格感性、诗意、富有想象力。
请为景点"{spot_name}"（位于{spot_city}）撰写一份约300字的语音导游词。

景点简介：{description}
景点标签：{tags}
开放时间：{open_time}
门票：{ticket_price}

要求：
- 用优美的语言描绘景点的意境和氛围
- 加入有趣的传说、轶事或名人故事（可适度创作）
- 激发听众的想象力和情感共鸣
- 语气温暖亲切，像一位在讲故事的朋友
- 结尾用一句诗意的句子收尾""",

    "foodie": """你是一位热爱美食的旅行导游，风格活泼、接地气，对美食如数家珍。
请为景点"{spot_name}"（位于{spot_city}）撰写一份约300字的语音导游词。

景点简介：{description}
景点标签：{tags}
开放时间：{open_time}
门票：{ticket_price}
附近美食：{nearby_foods}

要求：
- 简要介绍景点亮点后，重点推荐周边美食
- 提及具体的老字号、特色小吃、推荐菜品
- 分享一些只有本地人知道的美食小秘密
- 语气活泼有趣，像一位热情的吃货朋友
- 结尾用一句"逛完记得犒劳自己"收尾"""
}


def call_llm(prompt: str, temperature: float = 0.8) -> str:
    url = f"{TOUR_GUIDE_LLM_BASE}/chat/completions"
    headers = {
        "Authorization": f"Bearer {TOUR_GUIDE_LLM_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": TOUR_GUIDE_LLM_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 800,
        "temperature": temperature
    }
    try:
        resp = requests.post(url, headers=headers, json=data, timeout=60)
        result = resp.json()
        if 'choices' in result and len(result['choices']) > 0:
            return result['choices'][0]['message']['content']
        return f"LLM错误: {result}"
    except Exception as e:
        return f"LLM调用失败: {str(e)}"


def call_tts(text: str, speaker: str = None) -> bytes:
    if speaker is None:
        speaker = TTS_STYLE_SPEAKERS["rational"]
    headers = {
        "x-api-key": TTS_API_KEY,
        "X-Api-Resource-Id": TTS_RESOURCE_ID,
        "Content-Type": "application/json"
    }
    additions = json.dumps({
        "disable_markdown_filter": True,
        "enable_language_detector": True,
        "disable_default_bit_rate": True,
        "max_length_to_filter_parenthesis": 0
    })
    body = {
        "req_params": {
            "text": text.strip(),
            "speaker": speaker,
            "additions": additions,
            "audio_params": {
                "format": "mp3",
                "sample_rate": 24000
            }
        }
    }
    try:
        resp = requests.post(TTS_ENDPOINT, headers=headers, json=body, timeout=120)
        if resp.status_code != 200:
            return None
        ct = resp.headers.get('Content-Type', '')
        if 'audio' in ct:
            return resp.content
        all_audio = bytearray()
        for line in resp.text.split('\n'):
            line = line.strip()
            if not line or not line.startswith('{'):
                continue
            idx = line.find('"data":"')
            if idx < 0:
                continue
            start = idx + len('"data":"')
            end = line.find('"', start)
            if end <= start:
                continue
            b64 = line[start:end]
            try:
                all_audio.extend(base64.b64decode(b64))
            except Exception:
                continue
        return bytes(all_audio) if len(all_audio) > 0 else None
    except Exception:
        return None


@router.post("/tour-guide")
def generate_tour_guide(request: TourGuideRequest, db: Session = Depends(get_db)):
    spot = db.query(ScenicSpot).filter(ScenicSpot.id == request.spot_id).first()
    if not spot:
        return {"error": "景点不存在"}

    nearby_foods_list = db.query(Restaurant).filter(
        Restaurant.spot_id == request.spot_id
    ).limit(5).all()
    nearby_foods = ", ".join([r.name for r in nearby_foods_list]) if nearby_foods_list else "暂无数据"

    prompt_template = TOUR_GUIDE_PROMPTS.get(request.style, TOUR_GUIDE_PROMPTS["rational"])
    prompt = prompt_template.format(
        spot_name=spot.name,
        spot_city=spot.city or "未知",
        description=spot.description or "暂无描述",
        tags=", ".join(parse_tags(spot.tags)) if spot.tags else "暂无",
        open_time=spot.open_time or "全天开放",
        ticket_price=spot.ticket_price or "免费",
        nearby_foods=nearby_foods
    )

    guide_text = call_llm(prompt, temperature=0.8)

    speaker = TTS_STYLE_SPEAKERS.get(request.style, TTS_STYLE_SPEAKERS["rational"])

    audio_base64 = None
    audio_bytes = None
    if guide_text and not guide_text.startswith("LLM"):
        audio_bytes = call_tts(guide_text, speaker)
        if audio_bytes:
            audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')

    existing = db.query(TourGuide).filter(
        TourGuide.spot_id == request.spot_id,
        TourGuide.style == request.style
    ).first()

    from datetime import datetime
    now = datetime.now().isoformat()

    if existing:
        existing.text = guide_text
        if audio_bytes:
            existing.audio_data = audio_bytes
        existing.updated_at = now
    else:
        new_guide = TourGuide(
            spot_id=request.spot_id,
            style=request.style,
            text=guide_text,
            audio_data=audio_bytes,
            created_at=now,
            updated_at=now
        )
        db.add(new_guide)
    db.commit()

    style_names = {"rational": "理性派", "emotional": "感性派", "foodie": "吃货派"}

    return {
        "text": guide_text,
        "audio_base64": audio_base64,
        "style": request.style,
        "style_name": style_names.get(request.style, "理性派"),
        "spot_name": spot.name
    }


@router.get("/tour-guide/{spot_id}")
def get_tour_guide(spot_id: int, db: Session = Depends(get_db)):
    guides = db.query(TourGuide).filter(TourGuide.spot_id == spot_id).all()
    result = {}
    style_names = {"rational": "理性派", "emotional": "感性派", "foodie": "吃货派"}
    for g in guides:
        result[g.style] = {
            "text": g.text,
            "audio_base64": base64.b64encode(g.audio_data).decode('utf-8') if g.audio_data else None,
            "style_name": style_names.get(g.style, g.style)
        }
    return result
