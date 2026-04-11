"""
简单测试 AI 生成
"""
import requests
import json

BASE_URL = "http://localhost:8000"

# 测试生成
response = requests.post(
    f"{BASE_URL}/api/diary-generator/generate",
    json={
        "inspiration": "今天在上海吃到了一家超赞的本帮菜，红烧肉肥而不腻，入口即化，心情大好",
        "style": "healing"
    },
    timeout=60
)

print(f"状态码：{response.status_code}")
print(f"响应头：{response.headers}")
print(f"\n完整响应:\n{json.dumps(response.json(), indent=2, ensure_ascii=False)}")
