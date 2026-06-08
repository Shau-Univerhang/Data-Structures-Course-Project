"""
AIGC 动画生成服务测试
=====================
测试智谱 CogVideo 图生视频 API 调用流程
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.aigc_animation import (
    image_to_video, _encode_image, get_zhipu_token,
    TRAVEL_ANIMATION_PROMPTS
)

print("=" * 60)
print("测试 1: 智谱 API Token 配置")
print("=" * 60)

try:
    token = get_zhipu_token()
    masked_token = token[:10] + "..." + token[-5:]
    print(f"OK API Key 已配置: {masked_token}")
except ValueError as e:
    print(f"ERROR: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("测试 2: 固定提示词模板")
print("=" * 60)

for i, prompt in enumerate(TRAVEL_ANIMATION_PROMPTS, 1):
    print(f"  模板 {i}: {prompt[:80]}...")
print(f"OK 共 {len(TRAVEL_ANIMATION_PROMPTS)} 个提示词模板")

print("\n" + "=" * 60)
print("测试 3: 图片编码")
print("=" * 60)

# 测试本地图片编码
test_image_path = os.path.join(os.path.dirname(__file__), "..", "..", "uploads")
if os.path.exists(test_image_path):
    files = os.listdir(test_image_path)
    images = [f for f in files if f.endswith(('.jpg', '.png', '.jpeg'))]
    if images:
        first_image = os.path.join(test_image_path, images[0])
        print(f"  测试图片: {images[0]}")
        base64_data = _encode_image(first_image)
        if base64_data:
            print(f"  OK 编码成功，base64 长度: {len(base64_data)}")
        else:
            print("  ERROR 编码失败")
    else:
        print("  SKIP uploads 目录中无图片文件，跳过测试")
else:
    print("  SKIP uploads 目录不存在，跳过测试")

print("\n" + "=" * 60)
print("测试 4: URL 图片编码")
print("=" * 60)

test_url = "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400&q=80"
print(f"  测试 URL: {test_url[:60]}...")
base64_data = _encode_image(test_url)
if base64_data:
    print(f"  OK URL 编码成功，base64 长度: {len(base64_data)}")
else:
    print("  ERROR URL 编码失败（可能是网络问题）")

print("\n" + "=" * 60)
print("测试 5: 图生视频 API 调用（完整流程）")
print("=" * 60)
print("  注意: 此测试会实际调用智谱 API，耗时约 1-2 分钟")
print("  费用: 0.5 元/次")
print()

# 使用在线图片测试完整流程
test_image = "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400&q=80"
print(f"  输入图片: {test_image}")
print(f"  提示词: {TRAVEL_ANIMATION_PROMPTS[0][:60]}...")
print()

result = image_to_video(test_image, prompt=TRAVEL_ANIMATION_PROMPTS[0])

if result["status"] == "success":
    print(f"\nOK 视频生成成功")
    print(f"  任务 ID: {result['task_id']}")
    print(f"  视频 URL: {result['video_url']}")
else:
    print(f"\nERROR 视频生成失败")
    print(f"  错误信息: {result['message']}")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
