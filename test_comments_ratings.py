"""
测试评论和评分功能
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_diary_api():
    print("=" * 60)
    print("测试日记评论和评分系统")
    print("=" * 60)
    
    # 1. 创建测试日记
    print("\n1. 创建测试日记...")
    response = requests.post(
        f"{BASE_URL}/api/diaries",
        json={
            "title": "测试日记 - 评论和评分功能",
            "content": "这是一篇用于测试评论和评分功能的日记。\n\n今天天气很好，我去参观了故宫，感受到了中国古代建筑的宏伟壮观。",
            "user_id": 4,
            "is_public": True
        }
    )
    
    if response.status_code == 200:
        diary = response.json()
        diary_id = diary['id']
        print(f"✓ 日记创建成功，ID: {diary_id}")
    else:
        print(f"✗ 日记创建失败：{response.text}")
        return
    
    # 2. 获取日记详情
    print("\n2. 获取日记详情...")
    response = requests.get(f"{BASE_URL}/api/diaries/{diary_id}")
    if response.status_code == 200:
        diary_detail = response.json()
        print(f"✓ 日记详情获取成功")
        print(f"  标题：{diary_detail['title']}")
        print(f"  作者：{diary_detail['username']}")
        print(f"  浏览量：{diary_detail['view_count']}")
    else:
        print(f"✗ 获取日记详情失败：{response.text}")
    
    # 3. 测试评分
    print("\n3. 测试评分功能...")
    response = requests.post(
        f"{BASE_URL}/api/diaries/{diary_id}/rating?user_id=4",
        json={"rating": 5}
    )
    if response.status_code == 200:
        rating_data = response.json()
        print(f"✓ 评分成功")
        print(f"  平均评分：{rating_data['avg_rating']}")
        print(f"  评分人数：{rating_data['rating_count']}")
    else:
        print(f"✗ 评分失败：{response.text}")
    
    # 4. 再次评分（更新）
    print("\n4. 更新评分...")
    response = requests.post(
        f"{BASE_URL}/api/diaries/{diary_id}/rating?user_id=4",
        json={"rating": 4}
    )
    if response.status_code == 200:
        rating_data = response.json()
        print(f"✓ 评分更新成功")
        print(f"  平均评分：{rating_data['avg_rating']}")
    else:
        print(f"✗ 评分更新失败：{response.text}")
    
    # 5. 创建评论
    print("\n5. 创建评论...")
    response = requests.post(
        f"{BASE_URL}/api/diaries/{diary_id}/comments?user_id=4",
        json={"content": "这是一篇很棒的日记！风景描述得很生动。"}
    )
    if response.status_code == 200:
        comment = response.json()
        comment_id = comment['id']
        print(f"✓ 评论创建成功，ID: {comment_id}")
        print(f"  内容：{comment['content']}")
    else:
        print(f"✗ 评论创建失败：{response.text}")
        comment_id = None
    
    # 6. 创建回复
    if comment_id:
        print("\n6. 创建回复...")
        response = requests.post(
            f"{BASE_URL}/api/diaries/{diary_id}/comments?user_id=4",
            json={
                "content": "谢谢你的夸奖！",
                "parent_id": comment_id
            }
        )
        if response.status_code == 200:
            reply = response.json()
            print(f"✓ 回复创建成功")
            print(f"  内容：{reply['content']}")
        else:
            print(f"✗ 回复创建失败：{response.text}")
    
    # 7. 获取评论列表
    print("\n7. 获取评论列表...")
    response = requests.get(f"{BASE_URL}/api/diaries/{diary_id}/comments")
    if response.status_code == 200:
        comments = response.json()
        print(f"✓ 获取评论成功，共 {len(comments)} 条")
        for comment in comments:
            print(f"\n  评论 ID: {comment['id']}")
            print(f"  用户：{comment['username']}")
            print(f"  内容：{comment['content']}")
            print(f"  点赞数：{comment['like_count']}")
            if comment.get('replies'):
                print(f"  回复数：{len(comment['replies'])}")
                for reply in comment['replies']:
                    print(f"    - 回复：{reply['content']}")
    else:
        print(f"✗ 获取评论失败：{response.text}")
    
    # 8. 点赞评论
    if comment_id:
        print("\n8. 点赞评论...")
        response = requests.post(f"{BASE_URL}/api/comments/{comment_id}/like")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ 点赞成功，当前点赞数：{data['like_count']}")
        else:
            print(f"✗ 点赞失败：{response.text}")
    
    # 9. 删除评论（软删除）
    if comment_id:
        print("\n9. 删除评论...")
        response = requests.delete(f"{BASE_URL}/api/comments/{comment_id}?user_id=4")
        if response.status_code == 200:
            print(f"✓ 评论删除成功")
        else:
            print(f"✗ 评论删除失败：{response.text}")
    
    # 10. 删除评分
    print("\n10. 删除评分...")
    response = requests.delete(f"{BASE_URL}/api/diaries/{diary_id}/rating?user_id=4")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ 评分删除成功")
        print(f"  新的平均评分：{data.get('avg_rating', 0)}")
    else:
        print(f"✗ 评分删除失败：{response.text}")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_diary_api()
    except Exception as e:
        print(f"\n✗ 测试过程中发生错误：{e}")
        import traceback
        traceback.print_exc()
