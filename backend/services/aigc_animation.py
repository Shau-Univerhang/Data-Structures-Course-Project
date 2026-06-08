"""
AIGC 动画生成服务 - 基于智谱 CogVideo 图生视频
================================================
功能：根据日记图片生成 5-6 秒旅游动画视频
流程：上传图片 -> 智谱 CogVideo API -> 返回视频 URL

API 文档: https://docs.bigmodel.cn/cn/guide/models/video-generation/cogvideox-2
"""
import base64
import mimetypes
import os
import re
import time
from typing import Optional, Dict, Any
from urllib.parse import urlparse

import requests


# 智谱 CogVideo API 配置
ZHIPU_API_BASE = "https://open.bigmodel.cn/api/paas/v4"
ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY", "")

# 固定提示词模板（旅游场景 - 图生视频优化）
TRAVEL_ANIMATION_PROMPTS = [
    "Cinematic travel vlog style, slow pan across the scenic landscape, gentle camera movement, warm golden hour lighting, peaceful atmosphere, clouds moving slowly",
    "Dynamic travel photography, smooth zoom in with subtle parallax effect, vibrant colors, cinematic composition, gentle wind blowing",
    "Beautiful travel documentary style, gentle camera dolly movement, natural lighting transition, soft focus background, vivid colors and sharp details",
    "Cinematic travel animation, slow orbit around the landmark, dramatic sky with moving clouds, golden light rays, professional color grading"
]


def get_zhipu_token() -> str:
    """获取智谱 API Token"""
    if not ZHIPU_API_KEY:
        raise ValueError("ZHIPU_API_KEY 未配置")
    return ZHIPU_API_KEY


def image_to_video(
    image_url: str,
    prompt: str = "",
    duration: int = 5
) -> Dict[str, Any]:
    """
    使用智谱 CogVideo 将图片转为视频
    
    Args:
        image_url: 图片的完整 URL 或本地路径
        prompt: 动画描述提示词（可选，默认使用旅游模板）
        duration: 视频时长（秒），默认 5 秒
    
    Returns:
        {
            "task_id": "任务ID",
            "video_url": "视频URL",
            "status": "success/failed",
            "message": "状态消息"
        }
    """
    if not prompt:
        # 随机选择一个固定提示词
        import random
        prompt = random.choice(TRAVEL_ANIMATION_PROMPTS)
    
    # 读取图片并转为 base64，同时识别 MIME 类型
    encoded_image = _encode_image(image_url)
    if not encoded_image:
        return {
            "status": "failed",
            "message": "无法读取图片"
        }
    
    # Step 1: 创建异步任务
    task_id = _create_cogvideo_task(
        encoded_image["base64"],
        prompt,
        mime_type=encoded_image["mime_type"]
    )
    if not task_id:
        return {
            "status": "failed",
            "message": "创建视频任务失败"
        }
    
    # Step 2: 轮询等待任务完成（最多 120 秒，视频生成较慢）
    video_url = _poll_task_status(task_id, timeout=120)
    if not video_url:
        return {
            "status": "failed", 
            "message": "视频生成超时或失败"
        }
    
    return {
        "task_id": task_id,
        "video_url": video_url,
        "status": "success",
        "message": "动画生成成功"
    }


def _infer_mime_type(source: str, content_type: Optional[str] = None) -> str:
    """推断图片 MIME 类型，避免将 png/webp 强行标记为 jpeg。"""
    if content_type:
        mime_type = content_type.split(";")[0].strip().lower()
        if mime_type.startswith("image/"):
            return mime_type

    guessed_type, _ = mimetypes.guess_type(source)
    if guessed_type and guessed_type.startswith("image/"):
        return guessed_type

    return "image/jpeg"


def _encode_image(image_path: str) -> Optional[Dict[str, str]]:
    """将图片转为 base64 编码并返回 MIME 类型。"""
    try:
        preview = image_path[:80] + "..." if len(image_path) > 80 else image_path
        print(f"[AIGC] _encode_image 输入: {preview}")
        mime_type = "image/jpeg"

        # 前端通常会直接传 data URL，这里直接解析，不再当作文件路径处理
        if image_path.startswith("data:image/"):
            header, _, encoded = image_path.partition(",")
            if not encoded:
                print("[AIGC] data URL 中缺少 base64 数据")
                return None
            mime_match = re.match(r"data:(image/[^;]+);base64$", header, re.IGNORECASE)
            mime_type = mime_match.group(1).lower() if mime_match else "image/jpeg"
            encoded = encoded.strip()
            # 校验 base64 合法性，避免把损坏数据直接送给模型
            base64.b64decode(encoded, validate=True)
            print(f"[AIGC] 检测到 data URL 图片: mime={mime_type}, base64_len={len(encoded)}")
            return {
                "base64": encoded,
                "mime_type": mime_type
            }

        # 兼容直接存储为纯 base64 的历史数据
        if len(image_path) > 256 and "," not in image_path and not image_path.startswith(("http://", "https://")):
            compact = image_path.strip()
            if re.fullmatch(r"[A-Za-z0-9+/=\s]+", compact):
                normalized = re.sub(r"\s+", "", compact)
                base64.b64decode(normalized, validate=True)
                print(f"[AIGC] 检测到纯 base64 图片数据: base64_len={len(normalized)}")
                return {
                    "base64": normalized,
                    "mime_type": "image/jpeg"
                }

        # 如果是远程 URL（非 localhost），先下载
        if image_path.startswith(("http://", "https://")) and "localhost" not in image_path:
            print(f"[AIGC] 检测到远程 URL，将下载: {image_path}")
            response = requests.get(image_path, timeout=10, proxies={"http": None, "https": None})
            response.raise_for_status()
            mime_type = _infer_mime_type(image_path, response.headers.get("Content-Type"))
            if not mime_type.startswith("image/"):
                print(f"[AIGC] 远程资源不是图片: {response.headers.get('Content-Type', 'unknown')}")
                return None
            image_bytes = response.content
        elif image_path.startswith(("http://", "https://")) and "localhost" in image_path:
            # localhost URL 转为本机文件路径直接读取，避免请求自身
            print(f"[AIGC] 检测到 localhost URL，转换为本地路径: {image_path}")
            # http://localhost:8000/images/xxx.jpg -> images/xxx.jpg
            parsed = urlparse(image_path)
            local_path = parsed.path.lstrip("/")  # images/xxx.jpg
            if not local_path:
                print(f"[AIGC] 无效的 localhost 图片路径: {image_path}")
                return None
            full_path = os.path.join(os.path.dirname(__file__), "..", "..", local_path)
            print(f"[AIGC] 解析后的本地路径: {full_path}")
            if not os.path.exists(full_path):
                print(f"[AIGC] 图片文件不存在: {full_path}")
                return None
            with open(full_path, "rb") as f:
                image_bytes = f.read()
            mime_type = _infer_mime_type(full_path)
        else:
            # 本地路径处理
            full_path = image_path.lstrip("/\\")
            if not os.path.isabs(full_path):
                full_path = os.path.join(os.path.dirname(__file__), "..", "..", full_path)
            
            if not os.path.exists(full_path):
                # 尝试 uploads 目录
                uploads_path = os.path.join(os.path.dirname(__file__), "..", "..", "uploads", image_path)
                if os.path.exists(uploads_path):
                    full_path = uploads_path
                else:
                    print(f"[AIGC] 图片不存在: {image_path}")
                    return None
            
            with open(full_path, "rb") as f:
                image_bytes = f.read()
            mime_type = _infer_mime_type(full_path)

        if len(image_bytes) == 0:
            print("[AIGC] 图片内容为空")
            return None

        encoded = base64.b64encode(image_bytes).decode("utf-8")
        print(f"[AIGC] 图片编码成功: mime={mime_type}, size={len(image_bytes)} bytes, base64_len={len(encoded)}")
        return {
            "base64": encoded,
            "mime_type": mime_type
        }
    except Exception as e:
        print(f"[AIGC] 图片编码失败: {e}")
        return None


def _create_cogvideo_task(base64_image: str, prompt: str, mime_type: str = "image/jpeg") -> Optional[str]:
    """
    创建 CogVideo 图生视频任务
    
    API: POST /videos/generations
    文档: https://open.bigmodel.cn/dev/api#image-to-video
    """
    url = f"{ZHIPU_API_BASE}/videos/generations"
    headers = {
        "Authorization": f"Bearer {get_zhipu_token()}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "cogvideox-2",
        "prompt": prompt,
        "image_url": f"data:{mime_type};base64,{base64_image}"
    }
    
    print(f"[AIGC] 正在创建 CogVideo 任务: {prompt[:50]}...")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        print(f"[AIGC] API 响应: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            task_id = result.get("id") or result.get("data", {}).get("id")
            print(f"[AIGC] 任务创建成功: {task_id}")
            return task_id
        else:
            print(f"[AIGC] 创建任务失败: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"[AIGC] 请求异常: {e}")
        return None


def _poll_task_status(task_id: str, timeout: int = 120) -> Optional[str]:
    """
    轮询任务状态，直到视频生成完成
    
    API: GET /async-result/{task_id}
    """
    url = f"{ZHIPU_API_BASE}/async-result/{task_id}"
    headers = {
        "Authorization": f"Bearer {get_zhipu_token()}"
    }
    
    start_time = time.time()
    poll_interval = 5  # 每 5 秒轮询一次
    
    print(f"[AIGC] 开始轮询任务状态: {task_id}")
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, headers=headers, timeout=30)
            if response.status_code == 200:
                result = response.json()
                result_data = result.get("data", {}) if isinstance(result.get("data"), dict) else {}
                status = result.get("task_status") or result_data.get("task_status") or result.get("status", "")
                
                if status == "SUCCESS":
                    # 返回视频 URL
                    video_results = result.get("video_result") or result_data.get("video_result") or []
                    if video_results:
                        video_url = video_results[0].get("url")
                        print(f"[AIGC] 视频生成成功: {video_url}")
                        return video_url
                    print(f"[AIGC] 任务成功但无视频结果: {result}")
                    return None
                elif status == "FAILED":
                    fail_message = (
                        result.get("message")
                        or result_data.get("message")
                        or result.get("task_msg")
                        or result_data.get("task_msg")
                        or "unknown"
                    )
                    print(f"[AIGC] 任务失败: {fail_message}")
                    return None
                elif status in ["PENDING", "PROCESSING"]:
                    elapsed = int(time.time() - start_time)
                    print(f"[AIGC] 任务处理中... ({elapsed}s) - 状态: {status}")
                    time.sleep(poll_interval)
                    continue
                else:
                    print(f"[AIGC] 未知状态: {status}")
                    time.sleep(poll_interval)
            else:
                print(f"[AIGC] 查询状态失败: {response.status_code} - {response.text}")
                time.sleep(poll_interval)
        except Exception as e:
            print(f"[AIGC] 轮询异常: {e}")
            time.sleep(poll_interval)
    
    print(f"[AIGC] 任务超时: {task_id} (超时时间: {timeout}s)")
    return None
