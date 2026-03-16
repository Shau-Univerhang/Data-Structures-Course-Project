import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# --- 配置 ---
BASE_DIR = "backend/images/foods"
FOOD_DATA = {
    "beijing_kaoya": "北京烤鸭", "shuan_yangrou": "涮羊肉", "zhajiangmian": "炸酱面",
    "benbang_hongshaorou": "本帮红烧肉", "xiaolongbao": "小笼包", "shengjianbao": "生煎包",
    "mala_huoguo": "麻辣火锅", "mapo_doufu": "麻婆豆腐", "longchaoshou": "龙抄手",
    "chongqing_huoguo": "重庆火锅", "chongqing_xiaomian": "重庆小面", "xihu_cuyu": "西湖醋鱼",
    "dongporou": "东坡肉", "roujiamo": "肉夹馍", "yangrou_paomo": "羊肉泡馍",
    "guangdong_zaocha": "广东早茶", "shaola": "烧腊", "songshu_guiyu": "松鼠桂鱼",
    "shachamian": "沙茶面", "tusundong": "土笋冻"
}

def init_driver():
    options = Options()
    #options.add_argument('--headless') # 建议先关掉 headless 看看能不能搜到，稳了再开
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

def start_scrape():
    if not os.path.exists(BASE_DIR):
        os.makedirs(BASE_DIR, exist_ok=True)

    driver = init_driver()
    print("🚀 浏览器已就绪，开始抓取美食图...")

    for py_name, cn_name in FOOD_DATA.items():
        filename = f"{py_name}.jpg"
        save_path = os.path.join(BASE_DIR, filename)

        if os.path.exists(save_path):
            continue

        print(f"🔍 正在找: {cn_name}...")
        try:
            # 访问下厨房搜索页
            driver.get(f"https://www.xiachufang.com/search/?keyword={cn_name}&cat=1001")
            time.sleep(2)

            # 定位搜索结果的第一张图
            # 下厨房的结构比较清晰，第一个菜谱通常在 .normal-recipe-list li
            first_img = driver.find_element(By.CSS_SELECTOR, ".normal-recipe-list li img")
            img_url = first_img.get_attribute("src")

            # 转换成高清大图（下厨房的缩略图 URL 替换后缀即可）
            # 示例：.../cover/xxx_280.jpg -> .../cover/xxx_660.jpg
            if "_280" in img_url:
                img_url = img_url.replace("_280", "_660")
            elif "?" in img_url:
                img_url = img_url.split("?")[0]

            # 下载图片
            r = requests.get(img_url, timeout=10)
            if r.status_code == 200:
                with open(save_path, 'wb') as f:
                    f.write(r.content)
                print(f"   ✅ {filename} 保存完成")
            
            time.sleep(1) # 歇口气

        except Exception as e:
            print(f"   ❌ {cn_name} 抓取失败: 找不到元素")

    driver.quit()
    print("\n✨ 任务全部结束！")

if __name__ == "__main__":
    start_scrape()