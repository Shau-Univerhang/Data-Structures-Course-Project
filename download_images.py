import requests
import os
from urllib.parse import urlparse

# 图片URL列表 - 真实的Unsplash图片
IMAGES = {
    # 城市头部图
    'cities/beijing.jpg': 'https://images.unsplash.com/photo-1599571234909-29ed5d1321d6?w=1200',
    'cities/shanghai.jpg': 'https://images.unsplash.com/photo-1474181487882-5abf3f0ba6c2?w=1200',
    'cities/xian.jpg': 'https://images.unsplash.com/photo-1724458589661-a2f42eb58aca?w=1200',
    'cities/chengdu.jpg': 'https://images.unsplash.com/photo-1622613744987-0e3527fae518?w=1200',
    'cities/hangzhou.jpg': 'https://images.unsplash.com/photo-1697730047280-01082430a28a?w=1200',
    'cities/chongqing.jpg': 'https://images.unsplash.com/photo-1567014688543-cc4abffb061a?w=1200',
    'cities/qingdao.jpg': 'https://images.unsplash.com/photo-1718085875432-98c61c603b54?w=1200',
    'cities/guangzhou.jpg': 'https://images.unsplash.com/photo-1559035871-4b9dcf31885c?w=1200',
    'cities/suzhou.jpg': 'https://images.unsplash.com/photo-1521022741625-63f57c752f95?w=1200',
    'cities/xiamen.jpg': 'https://images.unsplash.com/photo-1660531141240-d5fb7a955822?w=1200',
    'cities/nanjing.jpg': 'https://images.unsplash.com/photo-1569517282132-25d22f4573e6?w=1200',
    'cities/wuhan.jpg': 'https://images.unsplash.com/photo-1596496050827-8299e0220de1?w=1200',
    'cities/changsha.jpg': 'https://images.unsplash.com/photo-1585351363283-95e3d5041053?w=1200',
    'cities/shenzhen.jpg': 'https://images.unsplash.com/photo-1558539320-1c71c5c5d8e8?w=1200',
    'cities/sanya.jpg': 'https://images.unsplash.com/photo-1580821810645-11a8fd7c9f37?w=1200',
    'cities/guilin.jpg': 'https://images.unsplash.com/photo-1548919973-5cef591cdbc9?w=1200',
    'cities/zhangjiajie.jpg': 'https://images.unsplash.com/photo-1565060169194-19fabf63012f?w=1200',
    'cities/huangshan.jpg': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1200',
    'cities/jiuzhaigou.jpg': 'https://images.unsplash.com/photo-1574169208507-84376144848b?w=1200',
    'cities/dali.jpg': 'https://images.unsplash.com/photo-1580870069867-74c57ee1bb07?w=1200',
    'cities/lijiang.jpg': 'https://images.unsplash.com/photo-1529143694754-56f8e0156f33?w=1200',
    
    # 北京景点
    'spots/beijing-gugong.jpg': 'https://images.unsplash.com/photo-1599571234909-29ed5d1321d6?w=800',
    'spots/beijing-tiantan.jpg': 'https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800',
    'spots/beijing-changcheng.jpg': 'https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800',
    'spots/beijing-yiheyuan.jpg': 'https://images.unsplash.com/photo-1548919973-5cef591cdbc9?w=800',
    'spots/beijing-tiananmen.jpg': 'https://images.unsplash.com/photo-1599571234909-29ed5d1321d6?w=800',
    'spots/beijing-niaokong.jpg': 'https://images.unsplash.com/photo-1548013146-72479768bada?w=800',
    
    # 上海景点
    'spots/shanghai-waitan.jpg': 'https://images.unsplash.com/photo-1474181487882-5abf3f0ba6c2?w=800',
    'spots/shanghai-dongfangmingzhu.jpg': 'https://images.unsplash.com/photo-1474181487882-5abf3f0ba6c2?w=800',
    
    # 西安景点
    'spots/xian-bingmayong.jpg': 'https://images.unsplash.com/photo-1724458589661-a2f42eb58aca?w=800',
    'spots/xian-dayanta.jpg': 'https://images.unsplash.com/photo-1724458589661-a2f42eb58aca?w=800',
    
    # 成都景点
    'spots/chengdu-kuanzhai.jpg': 'https://images.unsplash.com/photo-1622613744987-0e3527fae518?w=800',
    'spots/chengdu-jinli.jpg': 'https://images.unsplash.com/photo-1622613744987-0e3527fae518?w=800',
    
    # 杭州景点
    'spots/hangzhou-xihu.jpg': 'https://images.unsplash.com/photo-1697730047280-01082430a28a?w=800',
    'spots/hangzhou-leifengta.jpg': 'https://images.unsplash.com/photo-1697730047280-01082430a28a?w=800',
    
    # 重庆景点
    'spots/chongqing-hongyadong.jpg': 'https://images.unsplash.com/photo-1567014688543-cc4abffb061a?w=800',
    
    # 青岛景点
    'spots/qingdao-zhanqiao.jpg': 'https://images.unsplash.com/photo-1718085875432-98c61c603b54?w=800',
    
    # 广州景点
    'spots/guangzhou-canton-tower.jpg': 'https://images.unsplash.com/photo-1559035871-4b9dcf31885c?w=800',
    
    # 苏州景点
    'spots/suzhou-zhuozhengyuan.jpg': 'https://images.unsplash.com/photo-1521022741625-63f57c752f95?w=800',
    
    # 厦门景点
    'spots/xiamen-gulangyu.jpg': 'https://images.unsplash.com/photo-1660531141240-d5fb7a955822?w=800',
    
    # 南京景点
    'spots/nanjing-zhongshanling.jpg': 'https://images.unsplash.com/photo-1569517282132-25d22f4573e6?w=800',
    
    # 武汉景点
    'spots/wuhan-huanghelou.jpg': 'https://images.unsplash.com/photo-1596496050827-8299e0220de1?w=800',
    
    # 张家界景点
    'spots/zhangjiajie-tianmenshan.jpg': 'https://images.unsplash.com/photo-1565060169194-19fabf63012f?w=800',
    
    # 黄山景点
    'spots/huangshan-guangmingding.jpg': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800',
    
    # 九寨沟景点
    'spots/jiuzhaigou-wucaichi.jpg': 'https://images.unsplash.com/photo-1574169208507-84376144848b?w=800',
    
    # 大理景点
    'spots/dali-erhai.jpg': 'https://images.unsplash.com/photo-1580870069867-74c57ee1bb07?w=800',
    
    # 丽江景点
    'spots/lijiang-old-town.jpg': 'https://images.unsplash.com/photo-1529143694754-56f8e0156f33?w=800',
    
    # 美食
    'foods/peking-duck.jpg': 'https://images.unsplash.com/photo-1563245372-f21724e3856f?w=400',
    'foods/hotpot.jpg': 'https://images.unsplash.com/photo-1587895929328-6226a77f5c0f?w=400',
    'foods/xiaolongbao.jpg': 'https://images.unsplash.com/photo-1563245372-f21724e3856f?w=400',
    'foods/bbq.jpg': 'https://images.unsplash.com/photo-1529006557810-274b9b2fc783?w=400',
    'foods/sushi.jpg': 'https://images.unsplash.com/photo-1579871494447-9811cf80d66c?w=400',
    'foods/steak.jpg': 'https://images.unsplash.com/photo-1544025162-d76694265947?w=400',
    'foods/cha.jpg': 'https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=400',
}

# 下载目录
BASE_DIR = 'E:/YOYO/images'

def download_image(url, filepath):
    """下载图片"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            with open(filepath, 'wb') as f:
                f.write(response.content)
            print(f'OK: {filepath}')
            return True
        else:
            print(f'FAIL: {filepath} ({response.status_code})')
            return False
    except Exception as e:
        print(f'ERROR: {filepath} - {e}')
        return False

# 下载所有图片
success = 0
failed = 0

for path, url in IMAGES.items():
    filepath = os.path.join(BASE_DIR, path)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    if download_image(url, filepath):
        success += 1
    else:
        failed += 1

print(f'\n=== Download Complete ===')
print(f'Success: {success}')
print(f'Failed: {failed}')
