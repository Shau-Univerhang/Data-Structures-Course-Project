#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
根据爬虫脚本更新探索页面的美食数据
"""

import re

# 读取爬虫脚本中的美食数据
scrapers_content = open('D:\\travel\\Data-Structures-Course-Project\\scripts\\scrapers\\foods_scrape_xiachufang.py', 'r', encoding='utf-8').read()

# 提取FOOD_DATA字典
import ast
# 找到FOOD_DATA = { ... }
start = scrapers_content.find('FOOD_DATA = {')
if start == -1:
    print("未找到FOOD_DATA")
    exit(1)

# 找到匹配的结束括号
brace_count = 0
end = start
for i, char in enumerate(scrapers_content[start:]):
    if char == '{':
        brace_count += 1
    elif char == '}':
        brace_count -= 1
        if brace_count == 0:
            end = start + i + 1
            break

food_data_str = scrapers_content[start:end]

# 执行获取FOOD_DATA
local_vars = {}
exec(food_data_str, {}, local_vars)
FOOD_DATA = local_vars['FOOD_DATA']

print(f"从爬虫脚本中提取了 {len(FOOD_DATA)} 个美食")

# 城市映射
CITY_MAP = {
    'beijing': '北京',
    'shanghai': '上海',
    'xian': '西安',
    'chengdu': '成都',
    'hangzhou': '杭州',
    'chongqing': '重庆',
    'guangzhou': '广州',
    'suzhou': '苏州',
    'xiamen': '厦门',
    'sanya': '三亚',
    'qingdao': '青岛',
    'nanjing': '南京',
    'wuhan': '武汉',
    'changsha': '长沙',
    'shenzhen': '深圳',
    'guilin': '桂林',
    'zhangjiajie': '张家界',
    'huangshan': '黄山',
    'jiuzhaigou': '九寨沟',
    'dali': '大理',
    'lijiang': '丽江',
}

# 美食类型映射
CUISINE_MAP = {
    'beijing': '京菜',
    'shanghai': '本帮菜',
    'xian': '西北菜',
    'chengdu': '川菜',
    'hangzhou': '浙菜',
    'chongqing': '川菜',
    'guangzhou': '粤菜',
    'suzhou': '苏菜',
    'xiamen': '闽南菜',
    'sanya': '海南菜',
    'qingdao': '鲁菜',
    'nanjing': '苏菜',
    'wuhan': '鄂菜',
    'changsha': '湘菜',
    'shenzhen': '粤菜',
    'guilin': '桂菜',
    'zhangjiajie': '湘菜',
    'huangshan': '徽菜',
    'jiuzhaigou': '藏菜',
    'dali': '云南菜',
    'lijiang': '云南菜',
}

# 生成美食数据代码
def generate_foods_data():
    lines = []
    lines.append("// 生成美食数据")
    lines.append("const generateFoodsData = () => {")
    lines.append("  const foods = []")
    lines.append("  let id = 1")
    lines.append("")
    
    # 按城市分组
    city_foods = {}
    for key, name in FOOD_DATA.items():
        city_code = key.split('_')[0]
        if city_code not in city_foods:
            city_foods[city_code] = []
        city_foods[city_code].append((key, name))
    
    # 生成每个城市的美食数据
    for city_code, foods_list in sorted(city_foods.items()):
        city_name = CITY_MAP.get(city_code, city_code)
        cuisine_type = CUISINE_MAP.get(city_code, '地方菜')
        
        lines.append(f"  // {city_name}美食 ({len(foods_list)}个)")
        lines.append(f"  addCityFoods('{city_name}', [")
        
        for i, (key, name) in enumerate(foods_list):
            # 生成评分和价格（使用默认值）
            rating = round(4.0 + (hash(name) % 10) / 10, 1)
            price_min = 10 + (hash(name) % 20)
            price_max = price_min + 20 + (hash(name) % 30)
            price_range = f"¥{price_min}-{price_max}"
            
            # 前2个设为推荐
            is_featured = "true" if i < 2 else "false"
            tags = "['必吃', '特色']" if i < 2 else "['特色']"
            
            lines.append(f"    {{ name: '{name}', cuisine_type: '{cuisine_type}', rating: {rating}, price_range: '{price_range}', is_featured: {is_featured}, tags: {tags}, description: '{city_name}特色美食' }},")
        
        lines.append("  ])")
        lines.append("")
    
    lines.append("  return foods")
    lines.append("}")
    
    return "\n".join(lines)

# 生成代码
new_code = generate_foods_data()
print("\n生成的美食数据代码：")
print(new_code[:1000] + "...")

# 保存到文件
with open('D:\\travel\\Data-Structures-Course-Project\\scripts\\generated_foods_data.js', 'w', encoding='utf-8') as f:
    f.write(new_code)

print("\n✅ 美食数据代码已保存到 scripts/generated_foods_data.js")
print(f"总计 {len(FOOD_DATA)} 个美食")
