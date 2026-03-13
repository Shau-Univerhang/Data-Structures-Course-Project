import sqlite3
import json

# 本地图片路径
LOCAL_IMAGE_BASE = '/images'

# 城市图片映射 - 使用本地图片
CITY_IMAGES = {
    '北京': f'{LOCAL_IMAGE_BASE}/cities/beijing.jpg',
    '上海': f'{LOCAL_IMAGE_BASE}/cities/shanghai.jpg',
    '西安': f'{LOCAL_IMAGE_BASE}/cities/xian.jpg',
    '成都': f'{LOCAL_IMAGE_BASE}/cities/chengdu.jpg',
    '杭州': f'{LOCAL_IMAGE_BASE}/cities/hangzhou.jpg',
    '重庆': f'{LOCAL_IMAGE_BASE}/cities/chongqing.jpg',
    '青岛': f'{LOCAL_IMAGE_BASE}/cities/qingdao.jpg',
    '广州': f'{LOCAL_IMAGE_BASE}/cities/guangzhou.jpg',
    '苏州': f'{LOCAL_IMAGE_BASE}/cities/suzhou.jpg',
    '厦门': f'{LOCAL_IMAGE_BASE}/cities/xiamen.jpg',
    '南京': f'{LOCAL_IMAGE_BASE}/cities/nanjing.jpg',
    '武汉': f'{LOCAL_IMAGE_BASE}/cities/wuhan.jpg',
    '长沙': f'{LOCAL_IMAGE_BASE}/cities/changsha.jpg',
    '深圳': f'{LOCAL_IMAGE_BASE}/cities/shenzhen.jpg',
    '三亚': f'{LOCAL_IMAGE_BASE}/cities/sanya.jpg',
    '桂林': f'{LOCAL_IMAGE_BASE}/cities/guilin.jpg',
    '张家界': f'{LOCAL_IMAGE_BASE}/cities/zhangjiajie.jpg',
    '黄山': f'{LOCAL_IMAGE_BASE}/cities/huangshan.jpg',
    '九寨沟': f'{LOCAL_IMAGE_BASE}/cities/jiuzhaigou.jpg',
    '大理': f'{LOCAL_IMAGE_BASE}/cities/dali.jpg',
    '丽江': f'{LOCAL_IMAGE_BASE}/cities/lijiang.jpg',
}

# 景点图片映射 - 使用本地图片
SPOT_IMAGES = {
    # 北京
    '故宫': f'{LOCAL_IMAGE_BASE}/spots/beijing-gugong.jpg',
    '天坛': f'{LOCAL_IMAGE_BASE}/spots/beijing-tiantan.jpg',
    '长城': f'{LOCAL_IMAGE_BASE}/spots/beijing-changcheng.jpg',
    '颐和园': f'{LOCAL_IMAGE_BASE}/spots/beijing-yiheyuan.jpg',
    '天安门': f'{LOCAL_IMAGE_BASE}/spots/beijing-tiananmen.jpg',
    '鸟巢': f'{LOCAL_IMAGE_BASE}/spots/beijing-niaokong.jpg',
    # 上海
    '外滩': f'{LOCAL_IMAGE_BASE}/spots/shanghai-waitan.jpg',
    '东方明珠': f'{LOCAL_IMAGE_BASE}/spots/shanghai-dongfangmingzhu.jpg',
    # 西安
    '兵马俑': f'{LOCAL_IMAGE_BASE}/spots/xian-bingmayong.jpg',
    '大雁塔': f'{LOCAL_IMAGE_BASE}/spots/xian-dayanta.jpg',
    # 成都
    '宽窄巷子': f'{LOCAL_IMAGE_BASE}/spots/chengdu-kuanzhai.jpg',
    '锦里': f'{LOCAL_IMAGE_BASE}/spots/chengdu-jinli.jpg',
    # 重庆
    '洪崖洞': f'{LOCAL_IMAGE_BASE}/spots/chongqing-hongyadong.jpg',
    # 青岛
    '栈桥': f'{LOCAL_IMAGE_BASE}/spots/qingdao-zhanqiao.jpg',
    # 广州
    '广州塔': f'{LOCAL_IMAGE_BASE}/spots/guangzhou-canton-tower.jpg',
    # 苏州
    '拙政园': f'{LOCAL_IMAGE_BASE}/spots/suzhou-zhuozhengyuan.jpg',
    # 厦门
    '鼓浪屿': f'{LOCAL_IMAGE_BASE}/spots/xiamen-gulangyu.jpg',
    # 南京
    '中山陵': f'{LOCAL_IMAGE_BASE}/spots/nanjing-zhongshanling.jpg',
    # 武汉
    '黄鹤楼': f'{LOCAL_IMAGE_BASE}/spots/wuhan-huanghelou.jpg',
    # 黄山
    '光明顶': f'{LOCAL_IMAGE_BASE}/spots/huangshan-guangmingding.jpg',
    # 九寨沟
    '五彩池': f'{LOCAL_IMAGE_BASE}/spots/jiuzhaigou-wucaichi.jpg',
    # 大理
    '洱海': f'{LOCAL_IMAGE_BASE}/spots/dali-erhai.jpg',
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
    return CITY_IMAGES.get(city, f'{LOCAL_IMAGE_BASE}/cities/beijing.jpg')

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

print(f'Updated {updated} spot images')
print(f'City count: {city_count}')

# 验证
print('\n=== Beijing spots ===')
c.execute("SELECT name, images FROM scenic_spots WHERE city='北京' LIMIT 5")
for row in c.fetchall():
    imgs = json.loads(row[1])
    print(f'  {row[0]}: {imgs[0]}')

conn.close()
print('\nDone!')
