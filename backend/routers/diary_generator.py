"""
智能日记生成 API - 使用 MiniMax AI
"""
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import requests
import json
import os
import base64
from datetime import datetime

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.database import get_db

router = APIRouter()

# MiniMax API 配置
MINIMAX_API_KEY = "sk-cp-eENF_3JXbnNR0MFbfGZJqpW6Yxq-W6Qt_9YjNoI5EFCL63wekVwj0y3z1OJdugX17zIGqN51KDheUiJCp3MnrC_LJlAuOpgah92L-r4YEED2Y7h31-tTtPc"
MINIMAX_API_URL = "https://api.minimax.chat/v1/text/chatcompletion_v2"

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


def call_minimax_api(messages: list, temperature: float = 0.7) -> str:
    """调用 MiniMax API 生成文本"""
    headers = {
        "Authorization": f"Bearer {MINIMAX_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # MiniMax API 格式
    payload = {
        "model": "abab6.5s-chat",
        "messages": messages,
        "stream": False,
        "temperature": temperature,
        "top_p": 0.9,
        "max_tokens": 2048
    }
    
    try:
        response = requests.post(MINIMAX_API_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        
        print(f"MiniMax 响应状态：{result.get('usage', {})}")
        
        # MiniMax 响应格式检查
        if result.get("choices") and len(result["choices"]) > 0:
            content = result["choices"][0]["message"]["content"]
            print(f"✓ AI 生成成功，长度：{len(content)}")
            return content
        elif result.get("result"):
            # 备用字段
            print(f"✓ 使用 result 字段")
            return result["result"]
        else:
            print(f"✗ 无有效响应：{result}")
            return ""
    except requests.exceptions.RequestException as e:
        print(f"✗ 网络请求失败：{e}")
        return ""
    except Exception as e:
        print(f"✗ API 调用失败：{e}")
        return ""


def analyze_image_content(image_base64: str) -> dict:
    """使用 MiniMax 多模态能力分析图片"""
    # MiniMax 多模态 API
    multimodal_url = "https://api.minimaxi.chat/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {MINIMAX_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # 构建多模态消息
    messages = [{
        "role": "user",
        "content": [
            {
                "type": "image",
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
    
    payload = {
        "model": "abab6.5s-chat",
        "messages": messages,
        "max_tokens": 512
    }
    
    try:
        response = requests.post(multimodal_url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        if result.get("choices") and len(result["choices"]) > 0:
            description = result["choices"][0]["message"]["content"]
            return {
                "description": description,
                "success": True
            }
        return {"description": "", "success": False}
    except Exception as e:
        print(f"图片分析失败：{e}")
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
        # 调用 AI 生成
        ai_response = call_minimax_api(messages, temperature=0.8)
        
        # 如果 AI 返回空，使用模拟响应（用于演示）
        if not ai_response or not ai_response.strip():
            print("AI 返回空，使用模拟响应")
            ai_response = generate_mock_response(request.inspiration, style_name)
        
        # 解析 JSON 响应
        try:
            # 尝试提取 JSON
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
            # 如果解析失败，使用默认结构
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
    # 根据关键词判断类型
    if any(k in inspiration for k in ['吃', '菜', '美食', '餐厅', '饭', '面', '肉']):
        diary_type = "food"
        title = "美食探店记"
        tags = ["美食", "探店", "味道"]
        content = f"""🍜 **{title}**

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
        content = f"""📝 **{title}**

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
    使用 AI 识别图片中的关键信息（菜名、景点名等）
    """
    try:
        # 读取图片
        contents = await image.read()
        
        # 转换为 base64
        image_base64 = base64.b64encode(contents).decode('utf-8')
        
        # 调用 AI 分析
        result = analyze_image_content(image_base64)
        
        if result.get("success"):
            return {
                "success": True,
                "description": result["description"],
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


@router.post("/enhance-content")
async def enhance_content(
    content: str = Form(...),
    style: str = Form("healing")
):
    """
    对已有内容进行润色和增强
    """
    style_name = WRITING_STYLES.get(style, "治愈系温暖风格")
    
    system_prompt = f"""你是一个专业的文字编辑。你的任务是润色用户提供的日记内容，使其更加优美、生动。

润色要求：
1. 保持原意不变
2. 风格：{style_name}
3. 优化语句流畅度
4. 增加细节描写
5. 适当使用修辞手法
6. 保持真诚的情感"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"请润色以下内容：\n\n{content}"}
    ]
    
    try:
        enhanced = call_minimax_api(messages, temperature=0.6)
        return {
            "success": True,
            "enhanced_content": enhanced
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
