"""
检查所有文件是否包含完整的景点数据
"""
import os
import re

# 从爬虫脚本获取的完整景点数据
POI_DATA = {
    "beijing": [
        ("八达岭长城", "badaling_changcheng"), ("北海公园", "beihai_gongyuan"),
        ("南锣鼓巷", "nanluoguxiang"), ("圆明园", "yuanmingyuan"),
        ("天坛公园", "tiantan_gongyuan"), ("天安门广场", "tiananmen_guangchang"),
        ("恭王府", "gongwangfu"), ("故宫博物院", "gugong_bowuyuan"),
        ("景山公园", "jingshan_gongyuan"), ("颐和园", "yiheyuan"),
        ("北京大学", "beijing_daxue"), ("清华大学", "qinghua_daxue"),
        ("鸟巢", "niaochao"), ("水立方", "shuilifang"), ("什刹海", "shichahai")
    ],
    "shanghai": [
        ("上海博物馆", "shanghai_bowuguan"), ("上海迪士尼", "shanghai_dishini"),
        ("东方明珠", "dongfang_mingzhu"), ("南京路步行街", "nanjinglu_buxingjie"),
        ("召楼古镇", "zhaolou_guzhen"), ("外滩", "waitan"),
        ("武康路", "wukanglu"), ("田子坊", "tianzifang"),
        ("豫园", "yuyuan"), ("静安寺", "jingansi"),
        ("城隍庙", "chenghuangmiao"), ("新天地", "xintiandi"),
        ("上海中心大厦", "shanghai_zhongxin"), ("1933老场坊", "1933_laochangfang"),
        ("复旦大学", "fudan_daxue")
    ],
    "xian": [
        ("兵马俑", "bingmayong"), ("华清宫", "huaqinggong"), ("回民街", "huiminjie"),
        ("大唐芙蓉园", "datang_furongyuan"), ("大雁塔", "dayanta"), ("西安城墙", "xian_chengqiang"),
        ("大唐不夜城", "datang_buyecheng"), ("钟楼", "zhonglou"), ("鼓楼", "gulou"),
        ("陕西历史博物馆", "shanxi_lishi_bowuguan"), ("小雁塔", "xiaoyanta"),
        ("碑林博物馆", "beilin_bowuguan"), ("西安交通大学", "xian_jiaotong_daxue")
    ],
    "chengdu": [
        ("宽窄巷子", "kuanzhai_xiangzi"), ("春熙路", "chunxilu"), ("熊猫基地", "xiongmao_jidi"),
        ("锦里古街", "jinli_gujie"), ("武侯祠", "wuhouci"), ("杜甫草堂", "dufu_caotang"),
        ("青城山", "qingchengshan"), ("都江堰", "dujiangyan"), ("文殊院", "wenshuyuan"),
        ("人民公园", "renmin_gongyuan"), ("九眼桥", "jiuyanqiao"),
        ("四川大学", "sichuan_daxue"), ("太古里", "taikuli")
    ],
    "hangzhou": [
        ("西湖", "xihu"), ("灵隐寺", "lingyinsi"), ("雷峰塔", "leifengta"),
        ("千岛湖", "qiandaohu"), ("宋城", "songcheng"), ("西溪湿地", "xixi_shidi"),
        ("河坊街", "hefangjie"), ("断桥残雪", "duanqiao_canxue"), ("苏堤春晓", "sudi_chunxiao"),
        ("三潭印月", "santanyinyue"), ("浙江大学", "zhejiang_daxue"),
        ("龙井村", "longjingcun"), ("钱塘江", "qiantangjiang")
    ],
    "chongqing": [
        ("洪崖洞", "hongyadong"), ("磁器口", "ciqikou"), ("解放碑", "jiefangbei"),
        ("长江索道", "changjiang_suodao"), ("武隆天坑", "wulong_tiankeng"), ("朝天门", "chaotianmen"),
        ("李子坝轻轨", "liziba_qinggui"), ("鹅岭二厂", "eling_erchang"), ("南山一棵树", "nanshan_yikeshu"),
        ("三峡博物馆", "sanxia_bowuguan"), ("白公馆", "baigongguan"),
        ("渣滓洞", "zazidong"), ("重庆大学", "chongqing_daxue")
    ],
    "qingdao": [
        ("栈桥", "zhanqiao"), ("八大关", "badaguan"), ("崂山", "laoshan"),
        ("五四广场", "wusi_guangchang"), ("青岛啤酒博物馆", "qingdao_pijiu_bowuguan"), ("金沙滩", "jinshatan"),
        ("小鱼山", "xiaoyushan"), ("信号山公园", "xinhaoshan_gongyuan"), ("天主教堂", "tianzhu_jiaotang"),
        ("奥帆中心", "aofan_zhongxin"), ("德国总督府", "deguo_zongdufu"),
        ("中国海洋大学", "zhongguo_haiyang_daxue"), ("劈柴院", "pichaiyuan")
    ],
    "guangzhou": [
        ("广州塔", "guangzhouta"), ("沙面", "shamian"), ("陈家祠", "chenjiaci"),
        ("珠江夜游", "zhujiang_yeyou"), ("白云山", "baiyunshan"), ("越秀公园", "yuexiu_gongyuan"),
        ("北京路步行街", "beijinglu_buxingjie"), ("上下九步行街", "shangxiajiu_buxingjie"), ("长隆欢乐世界", "changlong_huanle_shijie"),
        ("中山纪念堂", "zhongshan_jiniantang"), ("石室圣心大教堂", "shishi_shengxin_dajiaotang"),
        ("中山大学", "zhongshan_daxue"), ("华南理工大学", "huanan_ligong_daxue")
    ],
    "suzhou": [
        ("拙政园", "zhuozhengyuan"), ("虎丘", "huqiu"), ("留园", "liuyuan"),
        ("狮子林", "shizilin"), ("苏州博物馆", "suzhou_bowuguan"), ("平江路", "pingjianglu"),
        ("周庄古镇", "zhouzhuang_guzhen"), ("同里古镇", "tongli_guzhen"), ("金鸡湖", "jinjihu"),
        ("寒山寺", "hanshansi"), ("山塘街", "shantangjie"),
        ("苏州大学", "suzhou_daxue"), ("观前街", "guanqianjie")
    ],
    "xiamen": [
        ("鼓浪屿", "gulangyu"), ("厦门大学", "xiamen_daxue"), ("南普陀寺", "nanputuosi"),
        ("曾厝垵", "zengcuoan"), ("环岛路", "huandaolu"), ("中山路步行街", "zhongshanlu_buxingjie"),
        ("胡里山炮台", "hulishan_paotai"), ("集美学村", "jimei_xuecun"), ("园林植物园", "yuanlin_zhiwuyuan"),
        ("白城沙滩", "baicheng_shatan"), ("沙坡尾", "shapowei"),
        ("厦门科技馆", "xiamen_kejiguan"), ("五缘湾", "wuyuanwan")
    ],
    "nanjing": [
        ("中山陵", "zhongshanling"), ("夫子庙", "fuzimiao"), ("秦淮河", "qinhuaihe"),
        ("明孝陵", "mingxiaoling"), ("总统府", "zongtongfu"), ("南京博物院", "nanjing_bowuyuan"),
        ("玄武湖", "xuanwuhu"), ("鸡鸣寺", "jimingsi"), ("侵华日军南京大屠杀遇难同胞纪念馆", "nanjing_datusha_jinianguan"),
        ("老门东", "laomendong"), ("新街口", "xinjiekou"),
        ("南京大学", "nanjing_daxue"), ("东南大学", "dongnan_daxue")
    ],
    "wuhan": [
        ("黄鹤楼", "huanghelou"), ("东湖", "donghu"), ("户部巷", "hubuxiang"),
        ("武汉大学", "wuhan_daxue"), ("湖北省博物馆", "hubei_bowuguan"), ("江汉路步行街", "jianghanlu_buxingjie"),
        ("古琴台", "guqintai"), ("晴川阁", "qingchuange"), ("昙华林", "tanhualin"),
        ("汉口江滩", "hankou_jiangtan"), ("武汉长江大桥", "wuhan_changjiang_daqiao"),
        ("归元寺", "guiyuansi"), ("光谷步行街", "guanggu_buxingjie")
    ],
    "changsha": [
        ("岳麓山", "yuelushan"), ("橘子洲", "juzizhou"), ("湖南省博物馆", "hunan_bowuguan"),
        ("太平街", "taipingjie"), ("天心阁", "tianxinge"), ("世界之窗", "shijie_zhichuang"),
        ("烈士公园", "lieshi_gongyuan"), ("黄兴路步行街", "huangxinglu_buxingjie"), ("坡子街", "pozijie"),
        ("爱晚亭", "aiwanting"), ("湖南大学", "hunan_daxue"),
        ("中南大学", "zhongnan_daxue"), ("超级文和友", "wenheyou")
    ],
    "shenzhen": [
        ("世界之窗", "shijie_zhichuang"), ("欢乐谷", "hualegu"), ("东部华侨城", "dongbu_huaqiaocheng"),
        ("大梅沙", "dameisha"), ("小梅沙", "xiaomeisha"), ("深圳湾公园", "shenzhenwan_gongyuan"),
        ("莲花山公园", "lianhuashan_gongyuan"), ("梧桐山", "wutongshan"), ("中英街", "zhongyingjie"),
        ("大鹏所城", "dapeng_suocheng"), ("较场尾", "jiaochangwei"),
        ("深圳大学", "shenzhen_daxue"), ("华强北", "huaqiangbei")
    ],
    "lijiang": [
        ("丽江古城", "lijiang_gucheng"), ("玉龙雪山", "yulong_xueshan"), ("束河古镇", "shuhe_guzhen"),
        ("拉市海", "lashihai"), ("虎跳峡", "hutiaoxia"), ("木府", "mufu"),
        ("黑龙潭公园", "heilongtan_gongyuan"), ("狮子山", "shizishan"), ("白沙古镇", "baisha_guzhen"),
        ("泸沽湖", "luguhu"), ("蓝月谷", "lanyuegu"),
        ("玉水寨", "yushuizhai"), ("东巴谷", "dongbagu")
    ],
    "sanya": [
        ("亚龙湾", "yalongwan"), ("天涯海角", "tianyahaijiao"), ("南山寺", "nanshansi"),
        ("蜈支洲岛", "wuzhizhou_dao"), ("大东海", "dadonghai"), ("鹿回头", "luhuitou"),
        ("三亚湾", "sanyawan"), ("呀诺达雨林", "yanuoda_yulin"), ("槟榔谷", "binglanggu"),
        ("大小洞天", "daxiao_dongtian"), ("西岛", "xidao"),
        ("亚特兰蒂斯水世界", "yatelandisi_shuishijie"), ("千古情", "qianguging")
    ],
    "guilin": [
        ("漓江", "lijiang"), ("象鼻山", "xiangbishan"), ("阳朔西街", "yangshuo_xijie"),
        ("龙脊梯田", "longji_titian"), ("两江四湖", "liangjiang_sihu"), ("银子岩", "yinziyan"),
        ("世外桃源", "shiwai_taoyuan"), ("十里画廊", "shili_hualang"), ("遇龙河", "yulonghe"),
        ("兴坪古镇", "xingping_guzhen"), ("芦笛岩", "ludiyan"),
        ("桂林理工大学", "guilin_ligong_daxue"), ("东西巷", "dongxixiang")
    ],
    "zhangjiajie": [
        ("张家界国家森林公园", "zhangjiajie_forest"), ("天门山", "tianmenshan"), ("黄龙洞", "huanglongdong"),
        ("宝峰湖", "baofenghu"), ("大峡谷玻璃桥", "daxiagu_boliqiao"), ("袁家界", "yuanjiajie"),
        ("杨家界", "yangjiajie"), ("天子山", "tianzishan"), ("十里画廊", "shili_hualang"),
        ("金鞭溪", "jinbianxi"), ("黄石寨", "huangshizhai"),
        ("百龙天梯", "bailong_tianti"), ("老屋场", "laowuchang")
    ],
    "huangshan": [
        ("黄山风景区", "huangshan_scenery"), ("宏村", "hongcun"), ("西递", "xidi"),
        ("屯溪老街", "tunxi_laojie"), ("翡翠谷", "feicuigu"), ("呈坎", "chenkan"),
        ("唐模", "tangmo"), ("潜口民宅", "qiankou_minzhai"), ("棠樾牌坊群", "tangyue_paifangqun"),
        ("徽州古城", "huizhou_gucheng"), ("齐云山", "qiyunshan"),
        ("新安江山水画廊", "xinanjiang_shanshui_hualang"), ("黄山温泉", "huangshan_wenquan")
    ],
    "jiuzhaigou": [
        ("九寨沟", "jiuzhaigou_valley"), ("五花海", "wuhuahai"), ("诺日朗瀑布", "nuorilang_pubu"),
        ("长海", "changhai"), ("熊猫海", "xiongmaohai"), ("镜海", "jinghai"),
        ("树正群海", "shuzheng_qunhai"), ("珍珠滩瀑布", "zhenzhutan_pubu"), ("芦苇海", "luweihai"),
        ("火花海", "huohuahai"), ("箭竹海", "jianzhuhai"),
        ("原始森林", "yuanshi_senlin"), ("则查洼沟", "zechawagou")
    ],
    "dali": [
        ("大理古城", "dali_ancient_city"), ("洱海", "erhai"), ("苍山", "cangshan"),
        ("崇圣寺三塔", "chongshengsi_santa"), ("双廊古镇", "shuanglang_guzhen"), ("喜洲古镇", "xizhou_guzhen"),
        ("蝴蝶泉", "hudiequan"), ("天龙八部影视城", "tianlongbabu_yingshicheng"), ("南诏风情岛", "nanzhao_fengqing_dao"),
        ("小普陀", "xiaoputuo"), ("挖色镇", "wasezhen"),
        ("大理大学", "dali_daxue"), ("才村码头", "caicun_matou")
    ]
}

# 城市中文名映射
CITY_NAMES = {
    "beijing": "北京", "shanghai": "上海", "xian": "西安", "chengdu": "成都",
    "hangzhou": "杭州", "chongqing": "重庆", "qingdao": "青岛", "guangzhou": "广州",
    "suzhou": "苏州", "xiamen": "厦门", "nanjing": "南京", "wuhan": "武汉",
    "changsha": "长沙", "shenzhen": "深圳", "lijiang": "丽江", "sanya": "三亚",
    "guilin": "桂林", "zhangjiajie": "张家界", "huangshan": "黄山", "jiuzhaigou": "九寨沟",
    "dali": "大理"
}

def check_city_vue():
    """检查 City.vue 中的景点映射"""
    print("\n=== 检查 City.vue ===")
    with open("frontend/src/views/City.vue", "r", encoding="utf-8") as f:
        content = f.read()
    
    missing = []
    for city_py, spots in POI_DATA.items():
        city_cn = CITY_NAMES[city_py]
        for spot_name, spot_py in spots:
            # 检查是否包含这个景点的映射
            pattern = f"'{spot_name}':"
            if pattern not in content:
                missing.append((city_cn, spot_name))
    
    if missing:
        print(f"  缺失 {len(missing)} 个景点映射:")
        for city, spot in missing[:20]:  # 只显示前20个
            print(f"    - {city}: {spot}")
        if len(missing) > 20:
            print(f"    ... 还有 {len(missing)-20} 个")
    else:
        print("  ✓ 所有景点映射都完整")
    
    return missing

def check_spot_recommend_vue():
    """检查 SpotRecommend.vue 中的景点数据"""
    print("\n=== 检查 SpotRecommend.vue ===")
    with open("frontend/src/views/SpotRecommend.vue", "r", encoding="utf-8") as f:
        content = f.read()
    
    missing = []
    for city_py, spots in POI_DATA.items():
        city_cn = CITY_NAMES[city_py]
        for spot_name, spot_py in spots:
            # 检查是否包含这个景点的数据
            if spot_name not in content:
                missing.append((city_cn, spot_name))
    
    if missing:
        print(f"  缺失 {len(missing)} 个景点数据:")
        for city, spot in missing[:20]:
            print(f"    - {city}: {spot}")
        if len(missing) > 20:
            print(f"    ... 还有 {len(missing)-20} 个")
    else:
        print("  ✓ 所有景点数据都完整")
    
    return missing

def check_explore_vue():
    """检查 Explore.vue 中的景点映射"""
    print("\n=== 检查 Explore.vue ===")
    with open("frontend/src/views/Explore.vue", "r", encoding="utf-8") as f:
        content = f.read()
    
    missing = []
    for city_py, spots in POI_DATA.items():
        city_cn = CITY_NAMES[city_py]
        for spot_name, spot_py in spots:
            # 检查是否包含这个景点的映射
            pattern = f"'{spot_name}':"
            if pattern not in content:
                missing.append((city_cn, spot_name))
    
    if missing:
        print(f"  缺失 {len(missing)} 个景点映射:")
        for city, spot in missing[:20]:
            print(f"    - {city}: {spot}")
        if len(missing) > 20:
            print(f"    ... 还有 {len(missing)-20} 个")
    else:
        print("  ✓ 所有景点映射都完整")
    
    return missing

def check_backend_spots():
    """检查后端 spots.py 中的景点映射"""
    print("\n=== 检查 backend/routers/spots.py ===")
    with open("backend/routers/spots.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    missing = []
    for city_py, spots in POI_DATA.items():
        city_cn = CITY_NAMES[city_py]
        for spot_name, spot_py in spots:
            # 检查是否包含这个景点的映射
            pattern = f"'{spot_name}':"
            if pattern not in content:
                missing.append((city_cn, spot_name))
    
    if missing:
        print(f"  缺失 {len(missing)} 个景点映射:")
        for city, spot in missing[:20]:
            print(f"    - {city}: {spot}")
        if len(missing) > 20:
            print(f"    ... 还有 {len(missing)-20} 个")
    else:
        print("  ✓ 所有景点映射都完整")
    
    return missing

def check_images():
    """检查图片是否存在"""
    print("\n=== 检查图片文件 ===")
    base_dir = "images/spots"
    missing = []
    
    for city_py, spots in POI_DATA.items():
        city_cn = CITY_NAMES[city_py]
        for spot_name, spot_py in spots:
            img_path = f"{base_dir}/{city_py}/{city_py}_{spot_py}.jpg"
            if not os.path.exists(img_path):
                missing.append((city_cn, spot_name, img_path))
    
    if missing:
        print(f"  缺失 {len(missing)} 个图片文件:")
        for city, spot, path in missing[:10]:
            print(f"    - {city}/{spot}: {path}")
        if len(missing) > 10:
            print(f"    ... 还有 {len(missing)-10} 个")
    else:
        print("  ✓ 所有图片文件都存在")
    
    return missing

if __name__ == "__main__":
    print("=" * 60)
    print("开始检查所有景点数据完整性")
    print("=" * 60)
    
    city_vue_missing = check_city_vue()
    spot_recommend_missing = check_spot_recommend_vue()
    explore_missing = check_explore_vue()
    backend_missing = check_backend_spots()
    images_missing = check_images()
    
    print("\n" + "=" * 60)
    print("检查完成!")
    print(f"  City.vue 缺失: {len(city_vue_missing)} 个")
    print(f"  SpotRecommend.vue 缺失: {len(spot_recommend_missing)} 个")
    print(f"  Explore.vue 缺失: {len(explore_missing)} 个")
    print(f"  backend/spots.py 缺失: {len(backend_missing)} 个")
    print(f"  图片文件缺失: {len(images_missing)} 个")
    print("=" * 60)
