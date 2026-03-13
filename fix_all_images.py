import sqlite3
import json

# 完整的城市和景点正确图片映射
CITY_IMAGES = {
    '北京': 'https://images.unsplash.com/photo-1599571234909-29ed5d1321d6?w=1200',
    '上海': 'https://images.unsplash.com/photo-1474181487882-5abf3f0ba6c2?w=1200',
    '西安': 'https://images.unsplash.com/photo-1724458589661-a2f42eb58aca?w=1200',
    '成都': 'https://images.unsplash.com/photo-1622613744987-0e3527fae518?w=1200',
    '杭州': 'https://images.unsplash.com/photo-1697730047280-01082430a28a?w=1200',
    '重庆': 'https://images.unsplash.com/photo-1567014688543-cc4abffb061a?w=1200',
    '青岛': 'https://images.unsplash.com/photo-1718085875432-98c61c603b54?w=1200',
    '广州': 'https://images.unsplash.com/photo-1559035871-4b9dcf31885c?w=1200',
    '苏州': 'https://images.unsplash.com/photo-1521022741625-63f57c752f95?w=1200',
    '厦门': 'https://images.unsplash.com/photo-1660531141240-d5fb7a955822?w=1200',
    '南京': 'https://images.unsplash.com/photo-1569517282132-25d22f4573e6?w=1200',
    '武汉': 'https://images.unsplash.com/photo-1596496050827-8299e0220de1?w=1200',
    '长沙': 'https://images.unsplash.com/photo-1585351363283-95e3d5041053?w=1200',
    '深圳': 'https://images.unsplash.com/photo-1558539320-1c71c5c5d8e8?w=1200',
    '三亚': 'https://images.unsplash.com/photo-1580821810645-11a8fd7c9f37?w=1200',
    '桂林': 'https://images.unsplash.com/photo-1548919973-5cef591cdbc9?w=1200',
    '张家界': 'https://images.unsplash.com/photo-1565060169194-19fabf63012f?w=1200',
    '黄山': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1200',
    '九寨沟': 'https://images.unsplash.com/photo-1574169208507-84376144848b?w=1200',
    '大理': 'https://images.unsplash.com/photo-1580870069867-74c57ee1bb07?w=1200',
    '丽江': 'https://images.unsplash.com/photo-1529143694754-56f8e0156f33?w=1200',
    '哈尔滨': 'https://images.unsplash.com/photo-1517457373958-b7bdd458e5e4?w=1200',
    '天津': 'https://images.unsplash.com/photo-1548919973-5cef591cdbc9?w=1200',
    '昆明': 'https://images.unsplash.com/photo-1580821810645-11a8fd7c9f37?w=1200',
    '贵阳': 'https://images.unsplash.com/photo-1598297677542-7d0b1a30ace5?w=1200',
}

# 景点详细图片
SPOT_IMAGES = {
    # 北京
    '故宫': 'https://images.unsplash.com/photo-1599571234909-29ed5d1321d6?w=800',
    '天坛': 'https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800',
    '长城': 'https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800',
    '颐和园': 'https://images.unsplash.com/photo-1548919973-5cef591cdbc9?w=800',
    '圆明园': 'https://images.unsplash.com/photo-1548919973-5cef591cdbc9?w=800',
    '鸟巢': 'https://images.unsplash.com/photo-1548013146-72479768bada?w=800',
    '水立方': 'https://images.unsplash.com/photo-1548013146-72479768bada?w=800',
    # 上海
    '外滩': 'https://images.unsplash.com/photo-1474181487882-5abf3f0ba6c2?w=800',
    '东方明珠': 'https://images.unsplash.com/photo-1474181487882-5abf3f0ba6c2?w=800',
    # 西安
    '兵马俑': 'https://images.unsplash.com/photo-1724458589661-a2f42eb58aca?w=800',
    '大雁塔': 'https://images.unsplash.com/photo-1724458589661-a2f42eb58aca?w=800',
    # 成都
    '宽窄巷子': 'https://images.unsplash.com/photo-1622613744987-0e3527fae518?w=800',
    '锦里': 'https://images.unsplash.com/photo-1622613744987-0e3527fae518?w=800',
    # 杭州
    '西湖': 'https://images.unsplash.com/photo-1697730047280-01082430a28a?w=800',
    '灵隐寺': 'https://images.unsplash.com/photo-1697730047280-01082430a28a?w=800',
    # 重庆
    '洪崖洞': 'https://images.unsplash.com/photo-1567014688543-cc4abffb061a?w=800',
    # 青岛
    '栈桥': 'https://images.unsplash.com/photo-1718085875432-98c61c603b54?w=800',
    # 广州
    '广州塔': 'https://images.unsplash.com/photo-1559035871-4b9dcf31885c?w=800',
    # 苏州
    '拙政园': 'https://images.unsplash.com/photo-1521022741625-63f57c752f95?w=800',
    # 厦门
    '鼓浪屿': 'https://images.unsplash.com/photo-1660531141240-d5fb7a955822?w=800',
    # 南京
    '中山陵': 'https://images.unsplash.com/photo-1569517282132-25d22f4573e6?w=800',
    # 武汉
    '黄鹤楼': 'https://images.unsplash.com/photo-1596496050827-8299e0220de1?w=800',
    # 长沙
    '岳麓山': 'https://images.unsplash.com/photo-1585351363283-95e3d5041053?w=800',
    # 深圳
    '世界之窗': 'https://images.unsplash.com/photo-1558539320-1c71c5c5d8e8?w=800',
    # 三亚
    '亚龙湾': 'https://images.unsplash.com/photo-1580821810645-11a8fd7c9f37?w=800',
    # 桂林
    '漓江': 'https://images.unsplash.com/photo-1548919973-5cef591cdbc9?w=800',
    '象鼻山': 'https://images.unsplash.com/photo-1548919973-5cef591cdbc9?w=800',
    # 张家界
    '天门山': 'https://images.unsplash.com/photo-1565060169194-19fabf63012f?w=800',
    '武陵源': 'https://images.unsplash.com/photo-1565060169194-19fabf63012f?w=800',
    # 黄山
    '光明顶': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800',
    '迎客松': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800',
    # 九寨沟
    '五彩池': 'https://images.unsplash.com/photo-1574169208507-84376144848b?w=800',
    # 大理
    '洱海': 'https://images.unsplash.com/photo-1580870069867-74c57ee1bb07?w=800',
    '大理古城': 'https://images.unsplash.com/photo-1580870069867-74c57ee1bb07?w=800',
    # 丽江
    '丽江古城': 'https://images.unsplash.com/photo-1529143694754-56f8e0156f33?w=800',
    '玉龙雪山': 'https://images.unsplash.com/photo-1529143694754-56f8e0156f33?w=800',
}

def get_spot_image(spot_name, city):
    """获取景点图片"""
    # 精确匹配
    if spot_name in SPOT_IMAGES:
        return SPOT_IMAGES[spot_name]
    
    # 模糊匹配
    for key, url in SPOT_IMAGES.items():
        if key in spot_name or spot_name in key:
            return url
    
    # 使用城市默认图
    return CITY_IMAGES.get(city, 'https://images.unsplash.com/photo-1599571234909-29ed5d1321d6?w=800')

# 连接数据库
conn = sqlite3.connect('E:/YOYO/backend/data/travel.db')
c = conn.cursor()

# 获取所有景点
c.execute('SELECT id, name, city FROM scenic_spots')
spots = c.fetchall()

# 更新每个景点的图片
updated = 0
for spot_id, name, city in spots:
    image = get_spot_image(name, city)
    images_json = json.dumps([image])
    c.execute('UPDATE scenic_spots SET images = ? WHERE id = ?', (images_json, spot_id))
    updated += 1

conn.commit()

# 统计
c.execute('SELECT COUNT(DISTINCT city) FROM scenic_spots')
city_count = c.fetchone()[0]

c.execute('SELECT COUNT(*) FROM scenic_spots')
spot_count = c.fetchone()[0]

print(f'Updated {updated} spot images')
print(f'City count: {city_count}')
print(f'Spot count: {spot_count}')

# 验证
print('\n=== Beijing spots:')
c.execute("SELECT name, images FROM scenic_spots WHERE city='北京' LIMIT 5")
for row in c.fetchall():
    imgs = json.loads(row[1])
    print(f"  {row[0]}: {imgs[0][-50:]}")

print('\n=== Shanghai spots:')
c.execute("SELECT name, images FROM scenic_spots WHERE city='上海' LIMIT 3")
for row in c.fetchall():
    imgs = json.loads(row[1])
    print(f"  {row[0]}: {imgs[0][-50:]}")

conn.close()
print('\nDone!')
