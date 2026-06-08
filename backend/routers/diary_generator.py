"""
智能日记生成 API - 使用智谱 GLM-4
"""
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import requests
import json
import os
import base64
import uuid
import subprocess
from datetime import datetime

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.database import get_db

router = APIRouter()

# 智谱 GLM-4 API 配置
ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY", "")
ZHIPU_API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

# 写作风格配置
WRITING_STYLES = {
    "healing": "治愈系温暖风格",
    "humorous": "幽默风趣风格",
    "documentary": "纪实文学风格",
    "poetic": "诗意浪漫风格",
    "concise": "简洁明快风格"
}


class GenerateDiaryRequest(BaseModel):
    """AI 生成日记请求"""
    inspiration: str  # 用户输入的灵感
    style: str = "healing"  # 写作风格
    images: List[str] = []  # 图片 URL 或 base64


class GenerateDiaryResponse(BaseModel):
    """AI 生成日记响应"""
    title: str
    content: str
    diary_type: str
    tags: List[str]
    suggested_images: List[str]


def call_zhipu_api(messages: list, model: str = "glm-4-flash", temperature: float = 0.7) -> str:
    """调用智谱 GLM-4 API 生成文本"""
    headers = {
        "Authorization": f"Bearer {ZHIPU_API_KEY}",
        "Content-Type": "application/json"
    }

    print(f"[DEBUG] 调用智谱API: model={model}, API_KEY存在={'*' if ZHIPU_API_KEY else '无'}")

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "top_p": 0.9,
        "max_tokens": 2048
    }

    try:
        response = requests.post(ZHIPU_API_URL, headers=headers, json=payload, timeout=60)
        print(f"[DEBUG] 智谱API响应状态码: {response.status_code}")
        response.raise_for_status()
        result = response.json()
        print(f"[DEBUG] 智谱API返回结果: {str(result)[:200]}")

        # 智谱响应格式
        if result.get("choices") and len(result["choices"]) > 0:
            content = result["choices"][0]["message"]["content"]
            return content
        else:
            print(f"智谱API无有效响应: {result}")
            return ""
    except requests.exceptions.RequestException as e:
        print(f"智谱API网络请求失败: {e}")
        return ""
    except Exception as e:
        print(f"智谱API调用失败: {e}")
        return ""


def extract_video_frames_ffmpeg(video_path: str, num_frames: int = 4) -> list:
    """使用 FFmpeg 从视频中提取关键帧，返回 base64 编码的图片列表"""
    frames_base64 = []

    print(f"[DEBUG] extract_video_frames_ffmpeg: {video_path}")
    if not os.path.exists(video_path):
        print(f"视频文件不存在: {video_path}")
        return frames_base64

    # 创建临时目录存放提取的帧
    temp_dir = os.path.dirname(video_path)
    frame_prefix = f"frame_{uuid.uuid4().hex}"

    try:
        # 使用 ffprobe 获取视频时长
        probe_cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "csv=p=0",
            video_path
        ]
        print(f"[DEBUG] 运行 ffprobe...")
        probe_result = subprocess.run(probe_cmd, capture_output=True, text=True, timeout=10)
        if probe_result.returncode != 0:
            print(f"[DEBUG] ffprobe 失败: {probe_result.stderr}")
            return frames_base64

        duration = float(probe_result.stdout.strip())
        print(f"[DEBUG] 视频时长: {duration}s")
        if duration <= 0:
            return frames_base64

        # 计算采样时间点（均匀分布）
        timestamps = [duration * i / num_frames for i in range(num_frames)]

        # 逐帧提取
        for i, ts in enumerate(timestamps):
            frame_path = os.path.join(temp_dir, f"{frame_prefix}_{i}.jpg")

            cmd = [
                "ffmpeg", "-y",
                "-ss", str(ts),
                "-i", video_path,
                "-frames:v", "1",
                "-vf", "scale=768:-1",
                "-q:v", "2",
                frame_path
            ]
            print(f"[DEBUG] 提取第 {i} 帧 at {ts}s...")
            result = subprocess.run(cmd, capture_output=True, timeout=30)
            if result.returncode == 0 and os.path.exists(frame_path):
                with open(frame_path, 'rb') as f:
                    frame_data = f.read()
                    frames_base64.append(base64.b64encode(frame_data).decode('utf-8'))
                os.remove(frame_path)  # 清理临时文件
            else:
                print(f"[DEBUG] ffmpeg 提取第 {i} 帧失败: {result.stderr}")

    except FileNotFoundError:
        print("FFmpeg 未安装，请安装 FFmpeg 或使用其他视频处理方法")
        return frames_base64
    except Exception as e:
        print(f"视频帧提取失败: {e}")
    finally:
        # 清理可能残留的临时文件
        for i in range(num_frames):
            path = os.path.join(temp_dir, f"{frame_prefix}_{i}.jpg")
            if os.path.exists(path):
                try:
                    os.remove(path)
                except:
                    pass

    return frames_base64


def extract_video_frames_pillow(video_path: str, num_frames: int = 4) -> list:
    """使用 Pillow 和 imageio-ffmpeg 从视频中提取关键帧"""
    frames_base64 = []

    print(f"[DEBUG] extract_video_frames_pillow: {video_path}")
    if not os.path.exists(video_path):
        print(f"视频文件不存在: {video_path}")
        return frames_base64

    try:
        from PIL import Image
        import imageio
        import io

        # 使用 imageio 的 ffmpeg 插件读取视频
        print(f"[DEBUG] 使用 imageio-ffmpeg 读取视频...")
        reader = imageio.get_reader(video_path, 'ffmpeg')
        
        # 将视频所有帧读取到列表
        all_frames = []
        for frame in reader:
            all_frames.append(frame)
        
        total_frames = len(all_frames)
        reader.close()
        print(f"[DEBUG] imageio-ffmpeg 读取到 {total_frames} 帧")
        
        if total_frames == 0:
            return frames_base64
            
        # 计算采样帧索引
        frame_indices = [int(total_frames * i / num_frames) for i in range(num_frames)]
        print(f"[DEBUG] 采样帧索引: {frame_indices}")
        
        for idx in frame_indices:
            try:
                frame = all_frames[idx]
                img = Image.fromarray(frame)
                
                # 缩放
                max_size = 768
                w, h = img.size
                if max(w, h) > max_size:
                    scale = max_size / max(w, h)
                    img = img.resize((int(w * scale), int(h * scale)))
                
                # 转换为 JPEG base64
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=80)
                base64_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
                frames_base64.append(base64_str)
                print(f"[DEBUG] 成功提取第 {idx} 帧")
            except Exception as e:
                print(f"[DEBUG] 提取第 {idx} 帧失败: {e}")
                continue
                    
    except ImportError as e:
        print(f"[DEBUG] imageio 模块缺失: {e}")
    except Exception as e:
        print(f"[DEBUG] Pillow 视频帧提取失败: {e}")
        import traceback
        traceback.print_exc()

    return frames_base64


def extract_video_frames(video_path: str, num_frames: int = 4) -> list:
    """从视频中提取关键帧，返回 base64 编码的图片列表"""
    print(f"[DEBUG] extract_video_frames 开始: {video_path}")
    # 优先尝试 FFmpeg（最可靠）
    frames = extract_video_frames_ffmpeg(video_path, num_frames)
    if frames:
        print(f"[DEBUG] FFmpeg 成功提取 {len(frames)} 帧")
        return frames

    # 备选方案：Pillow
    frames = extract_video_frames_pillow(video_path, num_frames)
    if frames:
        print(f"[DEBUG] Pillow 成功提取 {len(frames)} 帧")
        return frames

    print(f"所有视频帧提取方法都失败: {video_path}")
    return []


def analyze_video_content(video_url: str) -> dict:
    """使用智谱 GLM-4V-Plus 多模态能力分析视频"""
    print(f"[DEBUG] analyze_video_content 输入 URL: {video_url}")
    # 将URL转换为本地路径
    local_path = video_url
    if video_url.startswith("/videos/"):
        local_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "videos",
            os.path.basename(video_url)
        )

    print(f"[DEBUG] 本地路径: {local_path}")

    # 提取关键帧
    frames = extract_video_frames(local_path)
    print(f"[DEBUG] 提取了 {len(frames)} 帧")
    if not frames:
        return {"description": "无法提取视频内容", "success": False}

    # 构建多模态消息
    content_parts = []
    for frame_b64 in frames:
        content_parts.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{frame_b64}"
            }
        })

    content_parts.append({
        "type": "text",
        "text": "请根据这些视频截图描述视频内容。如果是旅行视频，请描述: 1.主要场景和地点 2.活动或体验 3.整体氛围和感受 4.可能的旅行类型。请用简洁的中文描述。"
    })

    messages = [{
        "role": "user",
        "content": content_parts
    }]

    try:
        print(f"[DEBUG] 调用智谱视觉模型分析...")
        response_text = call_zhipu_api(messages, model="glm-4v-plus", temperature=0.5)
        if response_text:
            return {"description": response_text, "success": True}
        return {"description": "", "success": False}
    except Exception as e:
        print(f"视频分析失败: {e}")
        return {"description": "", "success": False, "error": str(e)}


@router.post("/generate", response_model=GenerateDiaryResponse)
async def generate_diary(request: GenerateDiaryRequest):
    """
    智能日记生成

    根据用户输入的一句话灵感，自动生成完整的日记内容
    """
    style_name = WRITING_STYLES.get(request.style, "治愈系温暖风格")

    # 构建图片信息
    image_info = ""
    if request.images and len(request.images) > 0:
        image_info = f"\n\n用户上传了 {len(request.images)} 张图片，请根据图片内容补充描述。"

    # 构建提示词
    system_prompt = f"""你是一个专业的旅行日记写作助手。你的任务是根据用户输入的简短灵感，生成一篇优美、有氛围感的旅行日记。

写作要求：
1. 风格：{style_name}
2. 内容要生动具体，有细节描写
3. 情感真挚，能引起读者共鸣
4. 适当使用 emoji 表情增加趣味性
5. 结构清晰，分段合理

请从以下内容中提取信息并创作：
- 用户的灵感输入
- 可能的时间、地点、人物
- 用户的感受和心情
{image_info}

输出格式（JSON）：
{{
    "title": "日记标题（吸引人且贴合内容）",
    "content": "完整的日记内容（分段，使用 emoji）",
    "diary_type": "日记类型（travel/food/photo/notes）",
    "tags": ["标签 1", "标签 2", "标签 3"]
}}"""

    user_message = f"我的灵感：{request.inspiration}"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]

    try:
        # 使用 GLM-4-Flash (免费) 生成文本
        ai_response = call_zhipu_api(messages, model="glm-4-flash", temperature=0.8)

        # 如果 AI 返回空，使用模拟响应
        if not ai_response or not ai_response.strip():
            print("AI 返回空，使用模拟响应")
            ai_response = generate_mock_response(request.inspiration, style_name)

        # 解析 JSON 响应
        try:
            start_idx = ai_response.find('{')
            end_idx = ai_response.rfind('}') + 1
            if start_idx >= 0 and end_idx > start_idx:
                json_str = ai_response[start_idx:end_idx]
                result = json.loads(json_str)
            else:
                result = {
                    "title": "旅行日记",
                    "content": ai_response,
                    "diary_type": "notes",
                    "tags": ["旅行"]
                }
        except:
            result = {
                "title": "旅行日记",
                "content": ai_response,
                "diary_type": "notes",
                "tags": ["旅行", "随笔"]
            }

        return GenerateDiaryResponse(
            title=result.get("title", "旅行日记"),
            content=result.get("content", ""),
            diary_type=result.get("diary_type", "notes"),
            tags=result.get("tags", []),
            suggested_images=[]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成失败：{str(e)}")


def generate_mock_response(inspiration: str, style: str) -> str:
    """生成模拟响应（当 API 不可用时）"""
    if any(k in inspiration for k in ['吃', '菜', '美食', '餐厅', '饭', '面', '肉']):
        diary_type = "food"
        title = "美食探店记"
        tags = ["美食", "探店", "味道"]
        content = f""" **{title}**

{inspiration}

今天真是幸运的一天！偶然间发现了这家小店，没想到会有这么惊艳的味道。

📍 **餐厅信息**
- 地点：根据位置自动识别
- 人均：待补充
- 推荐菜：招牌菜

😋 **口味评价**
味道真的很棒，每一口都让人回味无穷。食材新鲜，烹饪技艺精湛，是一道不容错过的美味！

💫 **总体感受**
这次的美食发现之旅真是太棒了！已经迫不及待想要下次再来了～"""
    elif any(k in inspiration for k in ['玩', '旅游', '景点', '风景', '拍照', '旅行']):
        diary_type = "travel"
        title = "旅行日记"
        tags = ["旅行", "风景", "心情"]
        content = f"""✈️ **{title}**

{inspiration}

旅行的意义，就在于发现美好。今天的行程充满了惊喜和感动。

📍 **行程记录**
- 地点：美丽景点
- 天气：晴朗
- 心情：超级棒！

📸 **美好瞬间**
用镜头记录下这些珍贵的画面，每一张照片都是一个故事。

💭 **旅行感悟**
生活不止眼前的苟且，还有诗和远方。继续保持热爱，奔赴下一场山海！"""
    else:
        diary_type = "notes"
        title = "心情随笔"
        tags = ["随笔", "心情", "生活"]
        content = f""" **{title}**

{inspiration}

生活中总有一些值得记录的美好瞬间，今天就是这样一个特别的日子。

✨ **今日小确幸**
- 发现美好
- 感受温暖
- 记录感动

💝 **心情分享**
保持一颗感恩的心，去发现生活中的小美好。每一天都是独一无二的礼物。

🌈 **期待明天**
带着今天的快乐，继续前行。明天会更好！"""

    return json.dumps({
        "title": title,
        "content": content,
        "diary_type": diary_type,
        "tags": tags
    }, ensure_ascii=False)


@router.post("/analyze-image")
async def analyze_image(image: UploadFile = File(...)):
    """
    分析上传图片内容
    使用智谱 GLM-4V-Plus 识别图片中的关键信息
    """
    try:
        contents = await image.read()
        image_base64 = base64.b64encode(contents).decode('utf-8')

        messages = [{
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_base64}"
                    }
                },
                {
                    "type": "text",
                    "text": "请详细描述这张图片的内容，包括：1.图片中的主要物体或场景 2.如果是食物，请描述菜名、外观、可能的口味 3.如果是景点，请描述建筑特色、可能的地点 4.图片的整体氛围和给人的感觉。请用简洁的中文描述。"
                }
            ]
        }]

        description = call_zhipu_api(messages, model="glm-4v-plus", temperature=0.5)

        if description:
            return {
                "success": True,
                "description": description,
                "filename": image.filename
            }
        else:
            return {
                "success": False,
                "description": "无法识别图片内容",
                "filename": image.filename
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "filename": image.filename
        }


@router.post("/analyze-video")
async def analyze_video(video_url: str = Form(...)):
    """
    分析视频内容并生成日记文案

    输入: 视频URL
    输出: 基于视频内容生成的日记标题、内容、标签
    """
    print(f"[DEBUG] /analyze-video 接收到请求: video_url={video_url}")
    try:
        # 分析视频内容
        analysis = analyze_video_content(video_url)
        print(f"[DEBUG] 视频分析结果: success={analysis.get('success')}, description={str(analysis.get('description', ''))[:100]}")

        if not analysis.get("success"):
            error_detail = analysis.get("error", "视频分析失败")
            print(f"[DEBUG] 视频分析失败: {error_detail}")
            raise HTTPException(status_code=500, detail=f"视频分析失败: {error_detail}")

        video_description = analysis["description"]
        print(f"[DEBUG] 视频描述: {video_description[:100]}...")

        # 根据分析结果生成日记文案
        system_prompt = """你是一个专业的旅行日记写作助手。请根据用户提供的视频内容描述，生成一篇优美的旅行日记。

输出格式（JSON）：
{
    "title": "日记标题（吸引人且贴合内容）",
    "content": "完整的日记内容（分段，使用 emoji）",
    "diary_type": "日记类型（travel/food/photo/notes）",
    "tags": ["标签 1", "标签 2", "标签 3"]
}"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"视频内容描述：\n{video_description}\n\n请根据这个视频内容生成一篇旅行日记。"}
        ]

        print(f"[DEBUG] 调用 GLM-4-Flash 生成文案...")
        ai_response = call_zhipu_api(messages, model="glm-4-flash", temperature=0.8)
        print(f"[DEBUG] AI 文案响应: {str(ai_response)[:100]}...")

        if not ai_response:
            raise HTTPException(status_code=500, detail="文案生成失败")

        # 解析 JSON 响应
        try:
            start_idx = ai_response.find('{')
            end_idx = ai_response.rfind('}') + 1
            if start_idx >= 0 and end_idx > start_idx:
                json_str = ai_response[start_idx:end_idx]
                result = json.loads(json_str)
            else:
                result = {"title": "旅行日记", "content": ai_response, "diary_type": "travel", "tags": ["旅行"]}
        except:
            result = {"title": "旅行日记", "content": ai_response, "diary_type": "travel", "tags": ["旅行"]}

        return {
            "success": True,
            "title": result.get("title", "旅行日记"),
            "content": result.get("content", ""),
            "diary_type": result.get("diary_type", "travel"),
            "tags": result.get("tags", []),
            "video_description": video_description
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"[DEBUG] 视频分析接口异常: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"视频分析失败：{str(e)}")


@router.post("/enhance-content")
async def enhance_content(
    content: str = Form(...),
    style: str = Form("healing")
):
    """
    对旅行笔记进行 AI 文案润色：优化文字表达、生成标题
    注意：时间轴提取由前端规则代码完成，不依赖 AI
    """
    style_name = WRITING_STYLES.get(style, "治愈系温暖风格")

    system_prompt = f"""你是一个专业的旅行日记写作助手。你的任务是将用户零散的旅行笔记润色为优美的游记文字。

## 写作要求
1. 风格：{style_name}
2. 保持用户原始内容的时间顺序和行程
3. 润色细节：优化文字表达，补充感官描写（视觉、听觉、嗅觉、味觉）、情感表达、文化背景
4. 使用 emoji 适当点缀
5. 语言自然流畅，像朋友分享旅行故事
6. 分段合理，阅读体验好

## 输出要求
请以 JSON 格式输出：

```json
{{
  "title": "日记标题（简洁有力，体现旅行主题）",
  "enhanced_content": "润色后的完整游记内容（分段、有emoji、细节丰富）"
}}
```

## 注意
- 不要改变用户描述的实际行程和地点
- enhanced_content 是可以直接作为游记发布的完整文章"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"请润色以下旅行笔记：\n\n{content}"}
    ]

    try:
        ai_response = call_zhipu_api(messages, model="glm-4-flash", temperature=0.7)
        
        if not ai_response:
            return {
                "success": False,
                "error": "AI返回内容为空"
            }

        # 解析 JSON 响应
        try:
            start_idx = ai_response.find('{')
            end_idx = ai_response.rfind('}') + 1
            if start_idx >= 0 and end_idx > start_idx:
                json_str = ai_response[start_idx:end_idx]
                result = json.loads(json_str)
            else:
                result = {
                    "title": "旅行日记",
                    "enhanced_content": ai_response
                }
        except (json.JSONDecodeError, IndexError):
            result = {
                "title": "旅行日记",
                "enhanced_content": ai_response
            }

        return {
            "success": True,
            "title": result.get("title", "旅行日记"),
            "enhanced_content": result.get("enhanced_content", ai_response)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/styles")
async def get_writing_styles():
    """获取所有写作风格"""
    return {
        "styles": [
            {"key": key, "name": name}
            for key, name in WRITING_STYLES.items()
        ]
    }
