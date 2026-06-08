"""
验证压缩逻辑修改是否正确
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from algorithms.core import compress_diary, decompress_diary

# 测试合并压缩和解压
content = "今天去了故宫，参观了太和殿、中和殿和保和殿，感受到了浓厚的历史文化氛围。"
itinerary = [
    {
        "day": 1,
        "title": "第1天行程",
        "spots": [
            {
                "time": "9:00",
                "location": "故宫博物院",
                "description": "参观了太和殿",
                "duration": "2:00"
            },
            {
                "time": "11:00",
                "location": "故宫博物院",
                "description": "参观了中和殿",
                "duration": "1:30"
            }
        ]
    }
]

# 测试压缩
data_to_compress = {
    "content": content,
    "itinerary": itinerary
}

compressed = compress_diary(data_to_compress)
print(f"原始大小: {len(str(data_to_compress))} 字节")
print(f"压缩后大小: {len(compressed)} 字节")
print(f"压缩率: {len(compressed) / len(str(data_to_compress)) * 100:.1f}%")

# 测试解压
decompressed = decompress_diary(compressed)
print(f"\n解压后内容: {decompressed.get('content')}")
print(f"解压后时间轴: {decompressed.get('itinerary')}")

# 验证数据完整性
assert decompressed['content'] == content, "内容不一致！"
assert decompressed['itinerary'] == itinerary, "时间轴不一致！"

print("\n验证通过：压缩和解压逻辑正常工作！")
