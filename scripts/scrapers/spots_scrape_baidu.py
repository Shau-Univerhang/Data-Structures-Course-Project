import os
import requests
import re
import time
from urllib.parse import quote

# --- 1. 路径与景点配置 (已补全所有景点) ---
current_dir = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.join(current_dir, "images", "spots")

POI_DATA = {
    "beijing": [
        ("八达岭长城", "badaling_changcheng"), ("北海公园", "beihai_gongyuan"), 
        ("南锣鼓巷", "nanluoguxiang"), ("圆明园", "yuanmingyuan"), 
        ("天坛公园", "tiantan_gongyuan"), ("天安门广场", "tiananmen_guangchang"), 
        ("恭王府", "gongwangfu"), ("故宫博物院", "gugong_bowuyuan"), 
        ("景山公园", "jingshan_gongyuan"), ("颐和园", "yiheyuan")
    ],
    "shanghai": [
        ("上海博物馆", "shanghai_bowuguan"), ("上海迪士尼", "shanghai_dishini"), 
        ("东方明珠", "dongfang_mingzhu"), ("南京路步行街", "nanjinglu_buxingjie"), 
        ("召楼古镇", "zhaolou_guzhen"), ("外滩", "waitan"), 
        ("武康路", "wukanglu"), ("田子坊", "tianzifang"), 
        ("豫园", "yuyuan"), ("静安寺", "jingansi")
    ],
    "xian": [
        ("兵马俑", "bingmayong"), ("华清宫", "huaqinggong"), ("回民街", "huiminjie"), 
        ("大唐芙蓉园", "datang_furongyuan"), ("大雁塔", "dayanta"), ("西安城墙", "xian_chengqiang")
    ],
    "chengdu": [
        ("宽窄巷子", "kuanzhai_xiangzi"), ("春熙路", "chunxilu"), ("熊猫基地", "xiongmao_jidi")
    ],
    "hangzhou": [("西湖", "xihu"), ("灵隐寺", "lingyinsi"), ("雷峰塔", "leifengta")],
    "chongqing": [("洪崖洞", "hongyadong"), ("磁器口", "ciqikou"), ("解放碑", "jiefangbei")],
    "guangzhou": [("广州塔", "guangzhouta"), ("沙面", "shamian"), ("陈家祠", "chenjiaci")],
    "suzhou": [("拙政园", "zhuozhengyuan"), ("虎丘", "huqiu")],
    "xiamen": [("鼓浪屿", "gulangyu"), ("厦门大学", "xiamen_daxue")],
    "lijiang": [("丽江古城", "lijiang_gucheng"), ("玉龙雪山", "yulong_xueshan")],
    "sanya": [("亚龙湾", "yalongwan"), ("天涯海角", "tianyahaijiao")],
    "guilin": [("漓江", "lijiang"), ("象鼻山", "xiangbishan")],
    "zhangjiajie": [("张家界国家森林公园", "zhangjiajie_forest")],
    "huangshan": [("黄山风景区", "huangshan_scenery")],
    "jiuzhaigou": [("九寨沟", "jiuzhaigou_valley")],
    "dali": [("大理古城", "dali_ancient_city"), ("洱海", "erhai")],
    "fenghuang": [("凤凰古城", "fenghuang_town")]
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def download_img(url, folder, filename):
    try:
        # 增加 Referer 绕过某些防盗链
        res = requests.get(url, headers=HEADERS, timeout=15)
        if res.status_code == 200:
            with open(os.path.join(folder, filename), 'wb') as f:
                f.write(res.content)
            return True
    except:
        pass
    return False

def scrape_baidu():
    print(f"🚀 开始抓取高清景点图...")
    
    if not os.path.exists(BASE_DIR):
        os.makedirs(BASE_DIR, exist_ok=True)

    for city_py, spots in POI_DATA.items():
        # 按城市创建子目录
        city_folder = os.path.join(BASE_DIR, city_py)
        os.makedirs(city_folder, exist_ok=True)
            
        for spot_zh, spot_py in spots:
            filename = f"{city_py}_{spot_py}.jpg"
            save_path = os.path.join(city_folder, filename)

            if os.path.exists(save_path):
                continue

            print(f"🔍 正在抓取: {city_py} - {spot_zh}...")
            
            # 搜索关键词加上“摄影”或“高清”可以显著提升图质
            search_query = f"{spot_zh} 摄影 高清"
            search_url = f"https://image.baidu.com/search/flip?tn=baiduimage&ie=utf-8&word={quote(search_query)}"
            
            try:
                response = requests.get(search_url, headers=HEADERS, timeout=10)
                # 百度图片的原始 URL 存储在 objURL 字段中
                img_urls = re.findall(r'"objURL":"(.*?)"', response.text)
                
                success = False
                # 尝试搜索结果中的前几张，直到成功下载一张
                for url in img_urls[:10]:
                    if download_img(url, city_folder, filename):
                        print(f"    ✅ 已保存: {filename}")
                        success = True
                        break
                
                if not success:
                    print(f"    ❌ 无法找到合适的图片: {spot_zh}")
                
                time.sleep(1.2) # 礼貌停顿
                
            except Exception as e:
                print(f"    💥 搜索发生错误: {e}")

    print("\n✨ 任务结束！所有图片已按城市存入 images/spots/ 文件夹。")

if __name__ == "__main__":
    scrape_baidu()