"""
测试智能日记生成功能
"""
import requests
import json
import base64

BASE_URL = "http://localhost:8000"

def test_generate_diary():
    print("=" * 60)
    print("测试智能日记生成")
    print("=" * 60)
    
    # 测试用例 1: 美食日记
    print("\n1. 测试美食日记生成...")
    response = requests.post(
        f"{BASE_URL}/api/diary-generator/generate",
        json={
            "inspiration": "今天在上海吃到了一家超赞的本帮菜，红烧肉肥而不腻，入口即化",
            "style": "healing"
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ 生成成功")
        print(f"  标题：{result['title']}")
        print(f"  类型：{result['diary_type']}")
        print(f"  标签：{', '.join(result['tags'])}")
        print(f"\n  内容预览：{result['content'][:200]}...")
    else:
        print(f"✗ 生成失败：{response.text}")
    
    # 测试用例 2: 旅行日记
    print("\n2. 测试旅行日记生成（幽默风格）...")
    response = requests.post(
        f"{BASE_URL}/api/diary-generator/generate",
        json={
            "inspiration": "北京故宫人山人海，但是建筑真的很壮观，拍了很多照片",
            "style": "humorous"
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ 生成成功")
        print(f"  标题：{result['title']}")
        print(f"  类型：{result['diary_type']}")
        print(f"\n  内容预览：{result['content'][:200]}...")
    else:
        print(f"✗ 生成失败：{response.text}")
    
    # 测试用例 3: 纪实风格
    print("\n3. 测试纪实风格...")
    response = requests.post(
        f"{BASE_URL}/api/diary-generator/generate",
        json={
            "inspiration": "杭州西湖散步，苏堤春晓，断桥残雪，雷峰塔夕照",
            "style": "documentary"
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ 生成成功")
        print(f"  标题：{result['title']}")
        print(f"  类型：{result['diary_type']}")
        print(f"\n  内容预览：{result['content'][:200]}...")
    else:
        print(f"✗ 生成失败：{response.text}")
    
    # 测试用例 4: 获取风格列表
    print("\n4. 获取写作风格列表...")
    response = requests.get(f"{BASE_URL}/api/diary-generator/styles")
    
    if response.status_code == 200:
        styles = response.json()
        print(f"✓ 获取成功")
        for style in styles['styles']:
            print(f"  - {style['key']}: {style['name']}")
    else:
        print(f"✗ 获取失败：{response.text}")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_generate_diary()
    except Exception as e:
        print(f"\n✗ 测试过程中发生错误：{e}")
        import traceback
        traceback.print_exc()
