#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
根据图片文件检查并构建景点卡片
"""
import os
import re

# 图片文件夹路径
IMAGES_DIR = "images/spots"

# 城市英文名到中文名的映射
CITY_MAP = {
    "beijing": "北京",
    "shanghai": "上海",
    "xian": "西安",
    "chengdu": "成都",
    "hangzhou": "杭州",
    "chongqing": "重庆",
    "qingdao": "青岛",
    "guangzhou": "广州",
    "suzhou": "苏州",
    "xiamen": "厦门",
    "nanjing": "南京",
    "wuhan": "武汉",
    "changsha": "长沙",
    "shenzhen": "深圳",
    "lijiang": "丽江",
    "sanya": "三亚",
    "guilin": "桂林",
    "zhangjiajie": "张家界",
    "huangshan": "黄山",
    "jiuzhaigou": "九寨沟",
    "dali": "大理"
}

# 从爬虫脚本获取景点名称映射
SPOT_NAME_MAP = {
    # 北京
    "badaling_changcheng": "八达岭长城",
    "beihai_gongyuan": "北海公园",
    "beijing_daxue": "北京大学",
    "gongwangfu": "恭王府",
    "gugong_bowuyuan": "故宫博物院",
    "jingshan_gongyuan": "景山公园",
    "nanluoguxiang": "南锣鼓巷",
    "niaochao": "鸟巢",
    "qinghua_daxue": "清华大学",
    "shichahai": "什刹海",
    "shuilifang": "水立方",
    "tiananmen_guangchang": "天安门广场",
    "tiantan_gongyuan": "天坛公园",
    "yiheyuan": "颐和园",
    "yuanmingyuan": "圆明园",
    # 上海
    "1933_laochangfang": "1933老场坊",
    "chenghuangmiao": "城隍庙",
    "dongfang_mingzhu": "东方明珠",
    "fudan_daxue": "复旦大学",
    "jingansi": "静安寺",
    "nanjinglu_buxingjie": "南京路步行街",
    "shanghai_bowuguan": "上海博物馆",
    "shanghai_dishini": "上海迪士尼",
    "shanghai_zhongxin": "上海中心大厦",
    "tianzifang": "田子坊",
    "waitan": "外滩",
    "wukanglu": "武康路",
    "xintiandi": "新天地",
    "yuyuan": "豫园",
    "zhaolou_guzhen": "召楼古镇",
    # 西安
    "beilin_bowuguan": "碑林博物馆",
    "bingmayong": "兵马俑",
    "datang_buyecheng": "大唐不夜城",
    "datang_furongyuan": "大唐芙蓉园",
    "dayanta": "大雁塔",
    "gulou": "鼓楼",
    "huaqinggong": "华清宫",
    "huiminjie": "回民街",
    "shanxi_lishi_bowuguan": "陕西历史博物馆",
    "xian_chengqiang": "西安城墙",
    "xian_jiaotong_daxue": "西安交通大学",
    "xiaoyanta": "小雁塔",
    "zhonglou": "钟楼",
    # 成都
    "chunxilu": "春熙路",
    "dufu_caotang": "杜甫草堂",
    "dujiangyan": "都江堰",
    "jinli_gujie": "锦里古街",
    "jiuyanqiao": "九眼桥",
    "kuanzhai_xiangzi": "宽窄巷子",
    "qingchengshan": "青城山",
    "renmin_gongyuan": "人民公园",
    "sichuan_daxue": "四川大学",
    "taikuli": "太古里",
    "wenshuyuan": "文殊院",
    "wuhouci": "武侯祠",
    "xiongmao_jidi": "熊猫基地",
    # 杭州
    "duanqiao_canxue": "断桥残雪",
    "hefangjie": "河坊街",
    "leifengta": "雷峰塔",
    "lingyinsi": "灵隐寺",
    "longjingcun": "龙井村",
    "santanyinyue": "三潭印月",
    "songcheng": "宋城",
    "sudi_chunxiao": "苏堤春晓",
    "xihu": "西湖",
    "zhejiang_daxue": "浙江大学",
    # 重庆
    "baigongguan": "白公馆",
    "changjiang_suodao": "长江索道",
    "chaotianmen": "朝天门",
    "chongqing_daxue": "重庆大学",
    "ciqikou": "磁器口",
    "eling_erchang": "鹅岭二厂",
    "hongyadong": "洪崖洞",
    "jiefangbei": "解放碑",
    "liziba_qinggui": "李子坝轻轨",
    "nanshan_yikeshu": "南山一棵树",
    "sanxia_bowuguan": "三峡博物馆",
    "zazidong": "渣滓洞",
    # 青岛
    "aofan_zhongxin": "奥帆中心",
    "badaguan": "八大关",
    "deguo_zongdufu": "德国总督府",
    "jinshatan": "金沙滩",
    "laoshan": "崂山",
    "pichaiyuan": "劈柴院",
    "qingdao_pijiu_bowuguan": "青岛啤酒博物馆",
    "tianzhu_jiaotang": "天主教堂",
    "wusi_guangchang": "五四广场",
    "xiaoyushan": "小鱼山",
    "xinhaoshan_gongyuan": "信号山公园",
    "zhanqiao": "栈桥",
    "zhongguo_haiyang_daxue": "中国海洋大学",
    # 广州
    "baiyunshan": "白云山",
    "beijinglu_buxingjie": "北京路步行街",
    "changlong_huanle_shijie": "长隆欢乐世界",
    "chenjiaci": "陈家祠",
    "guangzhouta": "广州塔",
    "huanan_ligong_daxue": "华南理工大学",
    "shamian": "沙面",
    "shangxiajiu_buxingjie": "上下九步行街",
    "shishi_shengxin_dajiaotang": "石室圣心大教堂",
    "yuexiu_gongyuan": "越秀公园",
    "zhongshan_daxue": "中山大学",
    "zhongshan_jiniantang": "中山纪念堂",
    "zhujiang_yeyou": "珠江夜游",
    # 苏州
    "guanqianjie": "观前街",
    "hanshansi": "寒山寺",
    "huqiu": "虎丘",
    "jinjihu": "金鸡湖",
    "liuyuan": "留园",
    "pingjianglu": "平江路",
    "shantangjie": "山塘街",
    "shizilin": "狮子林",
    "suzhou_bowuguan": "苏州博物馆",
    "suzhou_daxue": "苏州大学",
    "tongli_guzhen": "同里古镇",
    "zhouzhuang_guzhen": "周庄古镇",
    "zhuozhengyuan": "拙政园",
    # 厦门
    "baicheng_shatan": "白城沙滩",
    "gulangyu": "鼓浪屿",
    "huandaolu": "环岛路",
    "hulishan_paotai": "胡里山炮台",
    "jimei_xuecun": "集美学村",
    "nanputuosi": "南普陀寺",
    "shapowei": "沙坡尾",
    "wuyuanwan": "五缘湾",
    "xiamen_daxue": "厦门大学",
    "xiamen_kejiguan": "厦门科技馆",
    "yuanlin_zhiwuyuan": "园林植物园",
    "zengcuoan": "曾厝垵",
    "zhongshanlu_buxingjie": "中山路步行街",
    # 南京
    "dongnan_daxue": "东南大学",
    "fuzimiao": "夫子庙",
    "jimingsi": "鸡鸣寺",
    "laomendong": "老门东",
    "mingxiaoling": "明孝陵",
    "nanjing_bowuyuan": "南京博物院",
    "nanjing_datusha_jinianguan": "侵华日军南京大屠杀遇难同胞纪念馆",
    "nanjing_daxue": "南京大学",
    "qinhuaihe": "秦淮河",
    "xinjiekou": "新街口",
    "xuanwuhu": "玄武湖",
    "zhongshanling": "中山陵",
    "zongtongfu": "总统府",
    # 武汉
    "donghu": "东湖",
    "guanggu_buxingjie": "光谷步行街",
    "guiyuansi": "归元寺",
    "guqintai": "古琴台",
    "hankou_jiangtan": "汉口江滩",
    "huanghelou": "黄鹤楼",
    "hubei_bowuguan": "湖北省博物馆",
    "hubuxiang": "户部巷",
    "jianghanlu_buxingjie": "江汉路步行街",
    "qingchuange": "晴川阁",
    "tanhualin": "昙华林",
    "wuhan_changjiang_daqiao": "武汉长江大桥",
    "wuhan_daxue": "武汉大学",
    # 长沙
    "aiwanting": "爱晚亭",
    "huangxinglu_buxingjie": "黄兴路步行街",
    "hunan_bowuguan": "湖南省博物馆",
    "hunan_daxue": "湖南大学",
    "juzizhou": "橘子洲",
    "lieshi_gongyuan": "烈士公园",
    "pozijie": "坡子街",
    "shijie_zhichuang": "世界之窗",
    "taipingjie": "太平街",
    "tianxinge": "天心阁",
    "wenheyou": "超级文和友",
    "yuelushan": "岳麓山",
    "zhongnan_daxue": "中南大学",
    # 深圳
    "dameisha": "大梅沙",
    "dapeng_suocheng": "大鹏所城",
    "dongbu_huaqiaocheng": "东部华侨城",
    "hualegu": "欢乐谷",
    "huaqiangbei": "华强北",
    "jiaochangwei": "较场尾",
    "lianhuashan_gongyuan": "莲花山公园",
    "shenzhen_daxue": "深圳大学",
    "shenzhenwan_gongyuan": "深圳湾公园",
    "shijie_zhichuang": "世界之窗",
    "wutongshan": "梧桐山",
    "xiaomeisha": "小梅沙",
    "zhongyingjie": "中英街",
    # 丽江
    "baisha_guzhen": "白沙古镇",
    "dongbagu": "东巴谷",
    "heilongtan_gongyuan": "黑龙潭公园",
    "hutiaoxia": "虎跳峡",
    "lanyuegu": "蓝月谷",
    "lashihai": "拉市海",
    "lijiang_gucheng": "丽江古城",
    "luguhu": "泸沽湖",
    "mufu": "木府",
    "shizishan": "狮子山",
    "shuhe_guzhen": "束河古镇",
    "yulong_xueshan": "玉龙雪山",
    "yushuizhai": "玉水寨",
    # 三亚
    "binglanggu": "槟榔谷",
    "dadonghai": "大东海",
    "daxiao_dongtian": "大小洞天",
    "luhuitou": "鹿回头",
    "nanshansi": "南山寺",
    "qianguging": "千古情",
    "sanyawan": "三亚湾",
    "tianyahaijiao": "天涯海角",
    "wuzhizhou_dao": "蜈支洲岛",
    "xidao": "西岛",
    "yalongwan": "亚龙湾",
    "yanuoda_yulin": "呀诺达雨林",
    "yatelandisi_shuishijie": "亚特兰蒂斯水世界",
    # 桂林
    "dongxixiang": "东西巷",
    "guilin_ligong_daxue": "桂林理工大学",
    "liangjiang_sihu": "两江四湖",
    "lijiang": "漓江",
    "longji_titian": "龙脊梯田",
    "ludiyan": "芦笛岩",
    "shili_hualang": "十里画廊",
    "shiwai_taoyuan": "世外桃源",
    "xiangbishan": "象鼻山",
    "xingping_guzhen": "兴坪古镇",
    "yangshuo_xijie": "阳朔西街",
    "yinziyan": "银子岩",
    "yulonghe": "遇龙河",
    # 张家界
    "bailong_tianti": "百龙天梯",
    "baofenghu": "宝峰湖",
    "daxiagu_boliqiao": "大峡谷玻璃桥",
    "huanglongdong": "黄龙洞",
    "huangshizhai": "黄石寨",
    "jinbianxi": "金鞭溪",
    "laowuchang": "老屋场",
    "shili_hualang": "十里画廊",
    "tianmenshan": "天门山",
    "tianzishan": "天子山",
    "yangjiajie": "杨家界",
    "yuanjiajie": "袁家界",
    "zhangjiajie_forest": "张家界国家森林公园",
    # 黄山
    "chenkan": "呈坎",
    "feicuigu": "翡翠谷",
    "hongcun": "宏村",
    "huangshan_scenery": "黄山风景区",
    "huangshan_wenquan": "黄山温泉",
    "huizhou_gucheng": "徽州古城",
    "qiankou_minzhai": "潜口民宅",
    "qiyunshan": "齐云山",
    "tangmo": "唐模",
    "tangyue_paifangqun": "棠樾牌坊群",
    "tunxi_laojie": "屯溪老街",
    "xidi": "西递",
    "xinanjiang_shanshui_hualang": "新安江山水画廊",
    # 九寨沟
    "changhai": "长海",
    "huohuahai": "火花海",
    "jianzhuhai": "箭竹海",
    "jinghai": "镜海",
    "jiuzhaigou_valley": "九寨沟",
    "luweihai": "芦苇海",
    "nuorilang_pubu": "诺日朗瀑布",
    "shuzheng_qunhai": "树正群海",
    "wuhuahai": "五花海",
    "xiongmaohai": "熊猫海",
    "yuanshi_senlin": "原始森林",
    "zechawagou": "则查洼沟",
    "zhenzhutan_pubu": "珍珠滩瀑布",
    # 大理
    "caicun_matou": "才村码头",
    "cangshan": "苍山",
    "chongshengsi_santa": "崇圣寺三塔",
    "dali_ancient_city": "大理古城",
    "dali_daxue": "大理大学",
    "erhai": "洱海",
    "hudiequan": "蝴蝶泉",
    "nanzhao_fengqing_dao": "南诏风情岛",
    "shuanglang_guzhen": "双廊古镇",
    "tianlongbabu_yingshicheng": "天龙八部影视城",
    "wasezhen": "挖色镇",
    "xiaoputuo": "小普陀",
    "xizhou_guzhen": "喜洲古镇"
}

def parse_image_filename(filename):
    """解析图片文件名，返回(城市英文名, 景点英文名)"""
    # 移除.jpg后缀
    name = filename.replace('.jpg', '')
    # 分割城市名和景点名
    parts = name.split('_', 1)
    if len(parts) == 2:
        return parts[0], parts[1]
    return None, None

def get_all_images():
    """获取所有图片文件"""
    images = {}
    for city_en in os.listdir(IMAGES_DIR):
        city_path = os.path.join(IMAGES_DIR, city_en)
        if os.path.isdir(city_path):
            images[city_en] = []
            for filename in os.listdir(city_path):
                if filename.endswith('.jpg'):
                    city, spot_en = parse_image_filename(filename)
                    if city and spot_en:
                        images[city_en].append({
                            'filename': filename,
                            'spot_en': spot_en,
                            'spot_cn': SPOT_NAME_MAP.get(spot_en, spot_en),
                            'path': f"/images/spots/{city_en}/{filename}"
                        })
    return images

def check_city_vue():
    """检查City.vue中的景点映射"""
    with open("frontend/src/views/City.vue", "r", encoding="utf-8") as f:
        content = f.read()
    
    images = get_all_images()
    missing = {}
    
    for city_en, spots in images.items():
        city_cn = CITY_MAP.get(city_en, city_en)
        missing[city_cn] = []
        for spot in spots:
            spot_cn = spot['spot_cn']
            # 检查是否包含这个景点的映射
            pattern = f"'{spot_cn}':"
            if pattern not in content:
                missing[city_cn].append(spot)
    
    return missing

def check_explore_vue():
    """检查Explore.vue中的景点映射"""
    with open("frontend/src/views/Explore.vue", "r", encoding="utf-8") as f:
        content = f.read()
    
    images = get_all_images()
    missing = {}
    
    for city_en, spots in images.items():
        city_cn = CITY_MAP.get(city_en, city_en)
        missing[city_cn] = []
        for spot in spots:
            spot_cn = spot['spot_cn']
            pattern = f"'{spot_cn}':"
            if pattern not in content:
                missing[city_cn].append(spot)
    
    return missing

def check_spot_recommend_vue():
    """检查SpotRecommend.vue中的景点数据"""
    with open("frontend/src/views/SpotRecommend.vue", "r", encoding="utf-8") as f:
        content = f.read()
    
    images = get_all_images()
    missing = {}
    
    for city_en, spots in images.items():
        city_cn = CITY_MAP.get(city_en, city_en)
        missing[city_cn] = []
        for spot in spots:
            spot_cn = spot['spot_cn']
            if spot_cn not in content:
                missing[city_cn].append(spot)
    
    return missing

def check_backend_spots():
    """检查后端spots.py中的景点映射"""
    with open("backend/routers/spots.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    images = get_all_images()
    missing = {}
    
    for city_en, spots in images.items():
        city_cn = CITY_MAP.get(city_en, city_en)
        missing[city_cn] = []
        for spot in spots:
            spot_cn = spot['spot_cn']
            pattern = f"'{spot_cn}':"
            if pattern not in content:
                missing[city_cn].append(spot)
    
    return missing

def generate_city_vue_mappings(missing):
    """生成City.vue的映射代码"""
    code = []
    for city_cn, spots in missing.items():
        if spots:
            code.append(f"\n  // {city_cn}")
            for spot in spots:
                code.append(f"  '{spot['spot_cn']}': '{spot['path']}',")
    return '\n'.join(code)

def generate_explore_vue_mappings(missing):
    """生成Explore.vue的映射代码"""
    code = []
    for city_cn, spots in missing.items():
        if spots:
            code.append(f"\n// {city_cn}景点图片映射")
            code.append(f"const {city_cn.lower()}SpotImages = {{")
            for spot in spots:
                code.append(f"  '{spot['spot_cn']}': '{spot['path']}',")
            code.append("}")
    return '\n'.join(code)

def generate_spot_recommend_data(missing):
    """生成SpotRecommend.vue的景点数据"""
    code = []
    spot_id = 1000
    for city_cn, spots in missing.items():
        if spots:
            code.append(f"\n    // {city_cn}")
            for spot in spots:
                code.append(f"    {{ id: {spot_id}, name: '{spot['spot_cn']}', city: '{city_cn}', rating: 4.5, favorites: 10000, tags: ['景点'], images: ['{spot['path']}'] }},")
                spot_id += 1
    return '\n'.join(code)

if __name__ == "__main__":
    print("=" * 80)
    print("检查所有景点卡片完整性")
    print("=" * 80)
    
    # 获取所有图片
    images = get_all_images()
    total_images = sum(len(spots) for spots in images.values())
    print(f"\n总共找到 {total_images} 张图片")
    
    for city_en, spots in sorted(images.items()):
        city_cn = CITY_MAP.get(city_en, city_en)
        print(f"  {city_cn}: {len(spots)}张")
    
    # 检查各个文件
    print("\n" + "=" * 80)
    print("检查缺失的景点映射...")
    print("=" * 80)
    
    city_vue_missing = check_city_vue()
    explore_missing = check_explore_vue()
    spot_recommend_missing = check_spot_recommend_vue()
    backend_missing = check_backend_spots()
    
    # 统计缺失数量
    city_vue_count = sum(len(spots) for spots in city_vue_missing.values())
    explore_count = sum(len(spots) for spots in explore_missing.values())
    spot_recommend_count = sum(len(spots) for spots in spot_recommend_missing.values())
    backend_count = sum(len(spots) for spots in backend_missing.values())
    
    print(f"\nCity.vue 缺失: {city_vue_count} 个景点")
    print(f"Explore.vue 缺失: {explore_count} 个景点")
    print(f"SpotRecommend.vue 缺失: {spot_recommend_count} 个景点")
    print(f"backend/spots.py 缺失: {backend_count} 个景点")
    
    # 显示详细缺失列表
    print("\n" + "=" * 80)
    print("详细缺失列表 (City.vue):")
    print("=" * 80)
    for city_cn, spots in city_vue_missing.items():
        if spots:
            print(f"\n{city_cn}:")
            for spot in spots:
                print(f"  - {spot['spot_cn']}")
    
    # 生成补充代码
    print("\n" + "=" * 80)
    print("生成的补充代码 (City.vue):")
    print("=" * 80)
    print(generate_city_vue_mappings(city_vue_missing))
