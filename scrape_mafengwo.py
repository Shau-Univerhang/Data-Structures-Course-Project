#!/usr/bin/env python3
"""
使用 Selenium 爬取马蜂窝景点图片
"""

import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

# --- 配置 ---
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
        ("兵马俑", "bingmayong"), ("华清宫", "huaqinggong"), 
        ("回民街", "huiminjie"), ("大唐芙蓉园", "datang_furongyuan"), 
        ("大雁塔", "dayanta"), ("小雁塔", "xiaoyanta"), 
        ("永兴坊", "yongxingfang"), ("碑林博物馆", "beilin_bowuguan"), 
        ("西安城墙", "xian_chengqiang"), ("陕西历史博物馆", "shanxi_lishi_bowuguan")
    ],
    "chengdu": [
        ("宽窄巷子", "kuanzhai_xiangzi"), ("春熙路", "chunxilu"), 
        ("杜甫草堂", "dufu_caotang"), ("武侯祠", "wuhouci"), 
        ("熊猫基地", "xiongmao_jidi"), ("都江堰", "dujiangyan"), 
        ("金沙遗址博物馆", "jinsha_yizhi_bowuguan"), ("锦里古街", "jinli_gujie"), 
        ("青城山", "qingchengshan"), ("龙泉山", "longquanshan")
    ],
    "hangzhou": [
        ("宋城", "songcheng"), ("岳王庙", "yuewangmiao"), 
        ("断桥残雪", "duanqiao_canxue"), ("河坊街", "hefangjie"), 
        ("灵隐寺", "lingyinsi"), ("苏堤", "sudi"), 
        ("西湖", "xihu"), ("西溪湿地", "xixi_shidi"), 
        ("雷峰塔", "leifengta"), ("龙井村", "longjingcun")
    ],
    "chongqing": [
        ("武隆天生三桥", "wulong_tiansheng_sanqiao"), ("洪崖洞", "hongyadong"), 
        ("磁器口", "ciqikou"), ("解放碑", "jiefangbei"), ("长江索道", "changjiang_suodao")
    ],
    "qingdao": [
        ("五四广场", "wusi_guangchang"), ("八大关", "badaguan"), 
        ("崂山", "laoshan"), ("栈桥", "zhanqiao"), ("金沙滩", "jinshatan")
    ],
    "guangzhou": [
        ("北京路", "beijinglu"), ("广州塔", "guangzhouta"), 
        ("珠江夜游", "zhujiang_yeyou"), ("白云山", "baiyunshan"), ("陈家祠", "chenjiaci")
    ],
    "suzhou": [("周庄", "zhouzhuang"), ("拙政园", "zhuozhengyuan")],
    "xiamen": [("厦门大学", "xiamen_daxue"), ("鼓浪屿", "gulangyu")],
    "lijiang": [("丽江古城", "lijiang_gucheng"), ("玉龙雪山", "yulong_xueshan")],
    "sanya": [
        ("三亚湾", "sanyawan"), ("亚特兰蒂斯", "yatlandis"), ("亚龙湾", "yalongwan"),
        ("大东海", "dadonghai"), ("大小洞天", "daxiaodongtian"), ("天涯海角", "tianyahaijiao"),
        ("海棠湾", "haitangwan"), ("蜈支洲岛", "wuzhizhoudao"), ("鹿回头", "luhuitou"),
        ("南山文化旅游区", "nanshan_wenhua")
    ],
    "guilin": [
        ("漓江", "lijiang"), ("象鼻山", "xiangbishan"), ("阳朔西街", "yangshuo_xijie"),
        ("遇龙河", "yulonghe"), ("龙脊梯田", "longji_titian"), ("两江四湖", "liangjiang_sihu")
    ],
    "zhangjiajie": [
        ("天门山", "tianmenshan"), ("武陵源", "wulingyuan"), ("黄石寨", "huangshizhai"),
        ("金鞭溪", "jinbianxi"), ("袁家界", "yuanjiajie"), ("十里画廊", "shili_hualang")
    ],
    "huangshan": [
        ("光明顶", "guangmingding"), ("迎客松", "yingkesong"), ("飞来石", "feilaishi"),
        ("西海大峡谷", "xihai_daxiagu"), ("天都峰", "tiandufeng")
    ],
    "jiuzhaigou": [
        ("五彩池", "wucaichi"), ("诺日朗瀑布", "nuorilang_pubu"), ("五花海", "wuhuahai"),
        ("珍珠滩", "zhenzhutan"), ("树正群海", "shuzheng_qunhai")
    ],
    "dali": [
        ("洱海", "erhai"), ("大理古城", "dali_gucheng"), ("苍山", "cangshan"),
        ("崇圣寺三塔", "chongshengsi_santa"), ("双廊", "shuanglang"), ("喜洲", "xizhou")
    ],
    "fenghuang": [
        ("沱江", "tuojiang"), ("虹桥", "hongqiao"), ("沈从文故居", "shencongwen_guju"),
        ("南方长城", "nanfang_changcheng"), ("苗寨", "miaozhai")
    ]
}

IMAGES_PER_SPOT = 1
BASE_DIR = "/Users/fangyuan/.openclaw/workspace/Data-Structures-Course-Project/frontend/public/images/spots"

# --- 浏览器初始化 ---
chrome_options = Options()
#chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

print("正在初始化浏览器...")
try:
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
except Exception as e:
    print(f"浏览器初始化失败: {e}")
    print("尝试使用无头模式...")
    chrome_options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

def download_image(url, folder, filename):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            with open(os.path.join(folder, filename), 'wb') as f:
                f.write(response.content)
            return True
    except Exception as e:
        print(f"   下载失败: {e}")
    return False

def scrape_mafengwo():
    if not os.path.exists(BASE_DIR):
        os.makedirs(BASE_DIR)

    total_spots = sum(len(spots) for spots in POI_DATA.values())
    current = 0
    
    for city_py, spots in POI_DATA.items():
        for spot_zh, spot_py in spots:
            current += 1
            print(f"[{current}/{total_spots}] 正在处理: {city_py} - {spot_zh}")
            
            # 检查是否已存在
            filename = f"{city_py}_{spot_py}.jpg"
            filepath = os.path.join(BASE_DIR, filename)
            if os.path.exists(filepath):
                print(f"   已存在，跳过")
                continue
            
            try:
                # 访问马蜂窝搜索页
                search_url = f"https://www.mafengwo.cn/search/q.php?q={spot_zh}&t=info"
                driver.get(search_url)
                time.sleep(3)
                
                # 点击第一个搜索结果
                try:
                    first_result = driver.find_element(By.CSS_SELECTOR, ".s-list ._j_search_link")
                    first_result.click()
                    time.sleep(3)
                except:
                    # 尝试其他选择器
                    try:
                        links = driver.find_elements(By.CSS_SELECTOR, "a[href*='mafengwo.cn']")
                        if links:
                            links[0].click()
                            time.sleep(3)
                    except:
                        print(f"   无法找到搜索结果")
                        continue
                
                # 查找图片
                img_elements = driver.find_elements(By.TAG_NAME, "img")
                downloaded = 0
                
                for img in img_elements:
                    if downloaded >= IMAGES_PER_SPOT:
                        break
                    
                    src = img.get_attribute("src")
                    if src and ("images" in src or "is" in src):
                        # 转换为大图
                        large_src = src.split('?')[0]
                        if download_image(large_src, BASE_DIR, filename):
                            print(f"   ✅ 已保存: {filename}")
                            downloaded += 1
                            break
                
                if downloaded == 0:
                    print(f"   ⚠️ 未找到图片")
                
                # 回到搜索页
                if len(driver.window_handles) > 1:
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    
            except Exception as e:
                print(f"   ❌ 错误: {e}")
                try:
                    if len(driver.window_handles) > 1:
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                except:
                    pass

    driver.quit()
    print("\n✨ 完成!")

if __name__ == "__main__":
    scrape_mafengwo()
