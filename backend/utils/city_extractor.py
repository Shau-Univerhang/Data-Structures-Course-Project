"""
城市标签提取工具
自动从日记标题、内容、行程中提取城市信息
"""

import re
from typing import List, Dict, Optional

# ============================================
# 中国城市核心词典（约300个主要城市）
# ============================================
CITY_KEYWORDS = {
    # 直辖市
    "北京": ["北京", "京城", "帝都", "北平", "京", "Beijing", "PEK"],
    "上海": ["上海", "魔都", "沪", "申", "Shanghai", "SHA"],
    "天津": ["天津", "津", "Tianjin", "TSN"],
    "重庆": ["重庆", "渝", "山城", "巴渝", "Chongqing", "CKG"],
    
    # 河北省
    "石家庄": ["石家庄", "石", "Shijiazhuang"],
    "保定": ["保定", "Baoding"],
    "承德": ["承德", "避暑山庄", "Chengde"],
    "秦皇岛": ["秦皇岛", "北戴河", "Qinhuangdao"],
    "张家口": ["张家口", "Zhangjiakou"],
    
    # 山西省
    "太原": ["太原", "并州", "Taiyuan"],
    "大同": ["大同", "云冈", "Datong"],
    "平遥": ["平遥", "古城", "Pingyao"],
    
    # 内蒙古自治区
    "呼和浩特": ["呼和浩特", "呼市", "Hohhot"],
    "包头": ["包头", "Baotou"],
    "呼伦贝尔": ["呼伦贝尔", "草原", "Hulunbuir"],
    
    # 辽宁省
    "沈阳": ["沈阳", "盛京", "Shenyang"],
    "大连": ["大连", "滨城", "Dalian"],
    "丹东": ["丹东", "Dandong"],
    
    # 吉林省
    "长春": ["长春", "春城", "Changchun"],
    "吉林": ["吉林", "江城", "Jilin"],
    "延吉": ["延吉", "延边", "Yanji"],
    
    # 黑龙江省
    "哈尔滨": ["哈尔滨", "冰城", "哈", "Harbin", "HRB"],
    "齐齐哈尔": ["齐齐哈尔", "鹤城", "Qiqihar"],
    "牡丹江": ["牡丹江", "Mudanjiang"],
    "雪乡": ["雪乡", "双峰", "Xuexiang"],
    
    # 江苏省
    "南京": ["南京", "金陵", "宁", "Nanjing", "NKG"],
    "苏州": ["苏州", "苏", "姑苏", "Suzhou"],
    "无锡": ["无锡", "Wuxi"],
    "常州": ["常州", "Changzhou"],
    "扬州": ["扬州", "扬", "Yangzhou"],
    "镇江": ["镇江", "Zhenjiang"],
    "泰州": ["泰州", "Taizhou"],
    "南通": ["南通", "Nantong"],
    "盐城": ["盐城", "Yancheng"],
    "连云港": ["连云港", "Lianyungang"],
    "徐州": ["徐州", "Xuzhou"],
    "淮安": ["淮安", "Huaian"],
    "宿迁": ["宿迁", "Suqian"],
    
    # 浙江省
    "杭州": ["杭州", "杭", "西湖", "Hangzhou", "HGH"],
    "宁波": ["宁波", "甬", "Ningbo"],
    "温州": ["温州", "温", "Wenzhou"],
    "绍兴": ["绍兴", "越", "Shaoxing"],
    "嘉兴": ["嘉兴", "禾", "Jiaxing"],
    "湖州": ["湖州", "湖", "Huzhou"],
    "金华": ["金华", "婺", "Jinhua"],
    "衢州": ["衢州", "Quzhou"],
    "舟山": ["舟山", "岛", "Zhoushan"],
    "台州": ["台州", "Taizhou"],
    "丽水": ["丽水", "Lishui"],
    "义乌": ["义乌", "Yiwu"],
    "西塘": ["西塘", "Xitang"],
    "乌镇": ["乌镇", "Wuzhen"],
    
    # 安徽省
    "合肥": ["合肥", "庐州", "Hefei"],
    "黄山": ["黄山", "徽州", "Huangshan"],
    "宏村": ["宏村", "Hongcun"],
    "九华山": ["九华山", "Jiuhua"],
    "芜湖": ["芜湖", "Wuhu"],
    
    # 福建省
    "福州": ["福州", "榕", "Fuzhou"],
    "厦门": ["厦门", "鹭岛", "厦", "Xiamen", "XMN"],
    "泉州": ["泉州", "鲤", "Quanzhou"],
    "莆田": ["莆田", "Putian"],
    "漳州": ["漳州", "Zhangzhou"],
    "龙岩": ["龙岩", "Longyan"],
    "武夷山": ["武夷山", "Wuyishan"],
    "鼓浪屿": ["鼓浪屿", "Gulangyu"],
    
    # 江西省
    "南昌": ["南昌", "洪城", "Nanchang"],
    "景德镇": ["景德镇", "瓷都", "Jingdezhen"],
    "庐山": ["庐山", "Lu"],
    "井冈山": ["井冈山", "Jinggang"],
    "婺源": ["婺源", "Wuyuan"],
    "赣州": ["赣州", "Ganzhou"],
    
    # 山东省
    "济南": ["济南", "泉城", "济", "Jinan"],
    "青岛": ["青岛", "青", "岛", "Qingdao", "TAO"],
    "烟台": ["烟台", "Yantai"],
    "威海": ["威海", "Weihai"],
    "泰安": ["泰安", "泰山", "Taian"],
    "曲阜": ["曲阜", "三孔", "Qufu"],
    "潍坊": ["潍坊", "Weifang"],
    "日照": ["日照", "Rizhao"],
    "临沂": ["临沂", "Linyi"],
    "淄博": ["淄博", "Zibo"],
    "枣庄": ["枣庄", "Zaozhuang"],
    "东营": ["东营", "Dongying"],
    "济宁": ["济宁", "Jining"],
    
    # 河南省
    "郑州": ["郑州", "郑", "Zhengzhou"],
    "洛阳": ["洛阳", "洛", "龙门", "Luoyang"],
    "开封": ["开封", "汴", "Kaifeng"],
    "安阳": ["安阳", "Anyang"],
    "焦作": ["焦作", "云台山", "Jiaozuo"],
    "登封": ["登封", "少林寺", "Dengfeng"],
    
    # 湖北省
    "武汉": ["武汉", "江城", "汉", "Wuhan", "WUH"],
    "宜昌": ["宜昌", "三峡", "Yichang"],
    "襄阳": ["襄阳", "Xiangyang"],
    "荆州": ["荆州", "Jingzhou"],
    "十堰": ["十堰", "武当山", "Shiyan"],
    "恩施": ["恩施", "Enshi"],
    
    # 湖南省
    "长沙": ["长沙", "星城", "Changsha", "CSX"],
    "张家界": ["张家界", "Zhangjiajie"],
    "凤凰": ["凤凰", "古城", "Fenghuang"],
    "岳阳": ["岳阳", "Yueyang"],
    "常德": ["常德", "桃花源", "Changde"],
    "衡阳": ["衡阳", "Hengyang"],
    "韶山": ["韶山", "Shaoshan"],
    
    # 广东省
    "广州": ["广州", "羊城", "穗", "Guangzhou", "CAN"],
    "深圳": ["深圳", "鹏城", "深", "Shenzhen", "SZX"],
    "珠海": ["珠海", "百岛", "Zhuhai"],
    "佛山": ["佛山", "禅", "Foshan"],
    "东莞": ["东莞", "莞", "Dongguan"],
    "中山": ["中山", "Zhongshan"],
    "惠州": ["惠州", "鹅城", "Huizhou"],
    "江门": ["江门", "Jiangmen"],
    "汕头": ["汕头", "鮀", "Shantou"],
    "潮州": ["潮州", "Chaozhou"],
    "韶关": ["韶关", "Shaoguan"],
    "肇庆": ["肇庆", "Zhaoqing"],
    "清远": ["清远", "Qingyuan"],
    "湛江": ["湛江", "Zhanjiang"],
    "阳江": ["阳江", "Yangjiang"],
    "河源": ["河源", "Heyuan"],
    "梅州": ["梅州", "Meizhou"],
    "揭阳": ["揭阳", "Jieyang"],
    "汕尾": ["汕尾", "Shanwei"],
    "云浮": ["云浮", "Yunfu"],
    
    # 广西壮族自治区
    "南宁": ["南宁", "邕", "Nanning", "NNG"],
    "桂林": ["桂林", "桂", "山水", "Guilin", "KWL"],
    "柳州": ["柳州", "柳", "Liuzhou"],
    "北海": ["北海", "Beihai"],
    "阳朔": ["阳朔", "Yangshuo"],
    "漓江": ["漓江", "Lijiang-River"],
    
    # 海南省
    "海口": ["海口", "椰城", "Haikou", "HAK"],
    "三亚": ["三亚", "鹿城", "Sanya", "SYX"],
    "三沙": ["三沙", "Sansha"],
    "儋州": ["儋州", "Danzhou"],
    "文昌": ["文昌", "Wenchang"],
    "万宁": ["万宁", "Wanning"],
    "陵水": ["陵水", "Lingshui"],
    
    # 四川省
    "成都": ["成都", "蓉", "锦城", "Chengdu", "CTU"],
    "绵阳": ["绵阳", "Mianyang"],
    "自贡": ["自贡", "Zigong"],
    "攀枝花": ["攀枝花", "Panzhihua"],
    "泸州": ["泸州", "Luzhou"],
    "德阳": ["德阳", "Deyang"],
    "广元": ["广元", "Guangyuan"],
    "遂宁": ["遂宁", "Suining"],
    "内江": ["内江", "Neijiang"],
    "乐山": ["乐山", "大佛", "Leshan"],
    "南充": ["南充", "Nanchong"],
    "眉山": ["眉山", "Meishan"],
    "宜宾": ["宜宾", "Yibin"],
    "广安": ["广安", "Guangan"],
    "达州": ["达州", "Dazhou"],
    "雅安": ["雅安", "Yaan"],
    "巴中": ["巴中", "Bazhong"],
    "资阳": ["资阳", "Ziyang"],
    "阿坝": ["阿坝", "九寨沟", "Aba"],
    "甘孜": ["甘孜", "稻城亚丁", "Ganzi"],
    "凉山": ["凉山", "西昌", "Liangshan"],
    
    # 贵州省
    "贵阳": ["贵阳", "筑", "Guiyang", "KWE"],
    "遵义": ["遵义", "Zunyi"],
    "安顺": ["安顺", "黄果树", "Anshun"],
    "铜仁": ["铜仁", "Tongren"],
    "毕节": ["毕节", "Bijie"],
    "六盘水": ["六盘水", "Liupanshui"],
    "黔西南": ["黔西南", "兴义", "Qianxinan"],
    "黔东南": ["黔东南", "凯里", "Qiandongnan"],
    "黔南": ["黔南", "都匀", "Qiannan"],
    "荔波": ["荔波", "Libo"],
    "镇远": ["镇远", "古镇", "Zhenyuan"],
    
    # 云南省
    "昆明": ["昆明", "春城", "Kunming", "KMG"],
    "曲靖": ["曲靖", "Qujing"],
    "玉溪": ["玉溪", "Yuxi"],
    "保山": ["保山", "Baoshan"],
    "昭通": ["昭通", "Zhaotong"],
    "丽江": ["丽江", "古城", "Lijiang", "LJG"],
    "普洱": ["普洱", "Puer"],
    "临沧": ["临沧", "Lincang"],
    "楚雄": ["楚雄", "Chuxiong"],
    "红河": ["红河", "哈尼", "Honghe"],
    "文山": ["文山", "Wenshan"],
    "西双版纳": ["西双版纳", "版纳", "景洪", "Xishuangbanna", "JHG"],
    "大理": ["大理", "风花雪月", "Dali", "DLU"],
    "德宏": ["德宏", "芒市", "Dehong"],
    "怒江": ["怒江", "Nujiang"],
    "迪庆": ["迪庆", "香格里拉", "Deqen", "DIG"],
    "腾冲": ["腾冲", "火山", "Tengchong"],
    
    # 西藏自治区
    "拉萨": ["拉萨", "日光城", "Lhasa", "LXA"],
    "日喀则": ["日喀则", "珠峰", "Shigatse"],
    "林芝": ["林芝", "Nyingchi"],
    "昌都": ["昌都", "Qamdo"],
    "山南": ["山南", "Shannan"],
    "那曲": ["那曲", "Nagqu"],
    "阿里": ["阿里", "Ngari"],
    
    # 陕西省
    "西安": ["西安", "长安", "镐", "古城", "Xian", "XIY"],
    "宝鸡": ["宝鸡", "Baoji"],
    "咸阳": ["咸阳", "Xianyang"],
    "铜川": ["铜川", "Tongchuan"],
    "渭南": ["渭南", "Weinan"],
    "延安": ["延安", "革命圣地", "Yanan"],
    "汉中": ["汉中", "Hanzhong"],
    "榆林": ["榆林", "Yulin"],
    "安康": ["安康", "Ankang"],
    "商洛": ["商洛", "Shangluo"],
    
    # 甘肃省
    "兰州": ["兰州", "金城", "Lanzhou", "LHW"],
    "嘉峪关": ["嘉峪关", "Jiayuguan"],
    "金昌": ["金昌", "Jinchang"],
    "白银": ["白银", "Baiyin"],
    "天水": ["天水", "Tianshui"],
    "武威": ["武威", "Wuwei"],
    "张掖": ["张掖", "丹霞", "Zhangye"],
    "平凉": ["平凉", "Pingliang"],
    "酒泉": ["酒泉", "Jiuquan"],
    "庆阳": ["庆阳", "Qingyang"],
    "定西": ["定西", "Dingxi"],
    "陇南": ["陇南", "Longnan"],
    "临夏": ["临夏", "Linxia"],
    "甘南": ["甘南", "夏河", "Gannan"],
    "敦煌": ["敦煌", "莫高窟", "Dunhuang"],
    
    # 青海省
    "西宁": ["西宁", "Xining", "XNN"],
    "海东": ["海东", "Haidong"],
    "海北": ["海北", "Haibei"],
    "黄南": ["黄南", "Huangnan"],
    "海南": ["海南", "Hainan"],
    "果洛": ["果洛", "Golog"],
    "玉树": ["玉树", "Yushu"],
    "海西": ["海西", "德令哈", "Haixi"],
    "青海湖": ["青海湖", "Qinghaihu"],
    
    # 宁夏回族自治区
    "银川": ["银川", "凤凰城", "Yinchuan", "INC"],
    "石嘴山": ["石嘴山", "Shizuishan"],
    "吴忠": ["吴忠", "Wuzhong"],
    "固原": ["固原", "Guyuan"],
    "中卫": ["中卫", "Zhongwei"],
    "沙坡头": ["沙坡头", "Shapotou"],
    
    # 新疆维吾尔自治区
    "乌鲁木齐": ["乌鲁木齐", "乌市", "Urumqi", "URC"],
    "克拉玛依": ["克拉玛依", "Karamay"],
    "吐鲁番": ["吐鲁番", "Turpan"],
    "哈密": ["哈密", "Kumul"],
    "昌吉": ["昌吉", "Changji"],
    "博尔塔拉": ["博尔塔拉", "博乐", "Bortala"],
    "巴音郭楞": ["巴音郭楞", "库尔勒", "Bayingolin"],
    "阿克苏": ["阿克苏", "Aksu"],
    "克孜勒苏": ["克孜勒苏", "阿图什", "Kizilsu"],
    "喀什": ["喀什", "噶尔", "Kashgar", "KHG"],
    "和田": ["和田", "Hotan"],
    "伊犁": ["伊犁", "伊宁", "Ili", "YIN"],
    "塔城": ["塔城", "Qoqek"],
    "阿勒泰": ["阿勒泰", "Altay"],
    "石河子": ["石河子", "Shihezi"],
    "阿拉尔": ["阿拉尔", "Aral"],
    "图木舒克": ["图木舒克", "Tumxuk"],
    "五家渠": ["五家渠", "Wujiaqu"],
    "北屯": ["北屯", "Beitun"],
    "铁门关": ["铁门关", "Tiemenguan"],
    "双河": ["双河", "Shuanghe"],
    "可克达拉": ["可克达拉", "Kokdala"],
    "昆玉": ["昆玉", "Kunyu"],
    "胡杨河": ["胡杨河", "Huyanghe"],
    "新星": ["新星", "Xinxing"],
    "喀什古城": ["喀什古城", "Kashgar-Old"],
    
    # 台湾省
    "台北": ["台北", "Taipei", "TPE"],
    "高雄": ["高雄", "Kaohsiung", "KHH"],
    "台中": ["台中", "Taichung", "RMQ"],
    "台南": ["台南", "Tainan", "TNN"],
    "花莲": ["花莲", "Hualien", "HUN"],
    "垦丁": ["垦丁", "Kenting"],
    "日月潭": ["日月潭", "Sun-Moon-Lake"],
    "阿里山": ["阿里山", "Alishan"],
    "九份": ["九份", "Jiufen"],
    
    # 香港特别行政区
    "香港": ["香港", "港", "Hong-Kong", "HK", "HKG"],
    
    # 澳门特别行政区
    "澳门": ["澳门", "澳", "妈港", "Macao", "Macau", "MFM"],
}

# 别名映射（非正式称呼映射到标准名称）
CITY_ALIASES = {
    # 常见别名
    "帝都": "北京",
    "魔都": "上海",
    "妖都": "广州",
    "雌都": "深圳",
    "腐都": "成都",
    "雾都": "重庆",
    "霸都": "合肥",
    "神都": "洛阳",
    "冰城": "哈尔滨",
    "春城": "昆明",
    "泉城": "济南",
    "羊城": "广州",
    "鹏城": "深圳",
    "蓉城": "成都",
    "锦城": "成都",
    "江城": "武汉",
    "星城": "长沙",
    "椰城": "海口",
    "鹿城": "三亚",
    "日光城": "拉萨",
    "金城": "兰州",
    "凤凰城": "银川",
    
    # 景点映射到城市
    "西湖": "杭州",
    "故宫": "北京",
    "天安门": "北京",
    "长城": "北京",
    "外滩": "上海",
    "东方明珠": "上海",
    "兵马俑": "西安",
    "大雁塔": "西安",
    "洪崖洞": "重庆",
    "解放碑": "重庆",
    "宽窄巷子": "成都",
    "春熙路": "成都",
    "夫子庙": "南京",
    "中山陵": "南京",
    "鼓浪屿": "厦门",
    "曾厝垵": "厦门",
    "丽江古城": "丽江",
    "玉龙雪山": "丽江",
    "大理古城": "大理",
    "洱海": "大理",
    "香格里拉": "迪庆",
    "普达措": "迪庆",
    "布达拉宫": "拉萨",
    "纳木错": "拉萨",
    "九寨沟": "阿坝",
    "黄龙": "阿坝",
    "稻城亚丁": "甘孜",
    "色达": "甘孜",
    "峨眉山": "乐山",
    "乐山大佛": "乐山",
    "张家界": "张家界",
    "凤凰古城": "凤凰",
    "黄山": "黄山",
    "宏村": "黄山",
    "庐山": "九江",
    "井冈山": "吉安",
    "婺源": "上饶",
    "三清山": "上饶",
    "龙虎山": "鹰潭",
    "泰山": "泰安",
    "曲阜三孔": "济宁",
    "崂山": "青岛",
    "蓬莱": "烟台",
    "刘公岛": "威海",
    "云冈石窟": "大同",
    "平遥古城": "晋中",
    "五台山": "忻州",
    "壶口瀑布": "临汾",
    "悬空寺": "大同",
    "乔家大院": "晋中",
    "晋祠": "太原",
    "雁门关": "忻州",
    "恒山": "大同",
    "嵩山": "郑州",
    "少林寺": "郑州",
    "龙门石窟": "洛阳",
    "白马寺": "洛阳",
    "云台山": "焦作",
    "清明上河园": "开封",
    "殷墟": "安阳",
    "鸡公山": "信阳",
    "武当山": "十堰",
    "神农架": "神农架",
    "三峡大坝": "宜昌",
    "黄鹤楼": "武汉",
    "东湖": "武汉",
    "古琴台": "武汉",
    "赤壁": "咸宁",
    "恩施大峡谷": "恩施",
    "衡山": "衡阳",
    "岳阳楼": "岳阳",
    "桃花源": "常德",
    "张家界森林公园": "张家界",
    "天门山": "张家界",
    "凤凰": "湘西",
    "韶山": "湘潭",
    "东江湖": "郴州",
    "崀山": "邵阳",
    "黄果树瀑布": "安顺",
    "梵净山": "铜仁",
    "西江千户苗寨": "黔东南",
    "镇远古镇": "黔东南",
    "荔波小七孔": "黔南",
    "马岭河峡谷": "黔西南",
    "万峰林": "黔西南",
    "织金洞": "毕节",
    "百里杜鹃": "毕节",
    "龙宫": "安顺",
    "肇兴侗寨": "黔东南",
    "加榜梯田": "黔东南",
    "乌蒙大草原": "六盘水",
    "竹海": "遵义",
    "茅台酒镇": "遵义",
    "青岩古镇": "贵阳",
    "花溪公园": "贵阳",
    "甲秀楼": "贵阳",
    "黔灵山": "贵阳",
    "石林": "昆明",
    "滇池": "昆明",
    "翠湖": "昆明",
    "九乡": "昆明",
    "世博园": "昆明",
    "民族村": "昆明",
    "东川红土地": "昆明",
    "罗平油菜花": "曲靖",
    "元阳梯田": "红河",
    "建水古城": "红河",
    "普者黑": "文山",
    "坝美": "文山",
    "西双版纳": "西双版纳",
    "野象谷": "西双版纳",
    "曼听公园": "西双版纳",
    "中科院植物园": "西双版纳",
    "傣族园": "西双版纳",
    "望天树": "西双版纳",
    "原始森林公园": "西双版纳",
    "茶马古道": "普洱",
    "梅里雪山": "迪庆",
    "雨崩": "迪庆",
    "虎跳峡": "迪庆",
    "松赞林寺": "迪庆",
    "白水台": "迪庆",
    "独克宗": "迪庆",
    "泸沽湖": "丽江",
    "束河古镇": "丽江",
    "白沙古镇": "丽江",
    "拉市海": "丽江",
    "虎跳峡丽江": "丽江",
    "玉龙": "丽江",
    "蓝月谷": "丽江",
    "冰川公园": "丽江",
    "云杉坪": "丽江",
    "牦牛坪": "丽江",
    "崇圣寺": "大理",
    "苍山": "大理",
    "喜洲": "大理",
    "双廊": "大理",
    "蝴蝶泉": "大理",
    "鸡足山": "大理",
    "沙溪": "大理",
    "诺邓": "大理",
    "腾冲火山": "保山",
    "和顺古镇": "保山",
    "热海": "保山",
    "银杏村": "保山",
    "北海湿地": "保山",
    "瑞丽": "德宏",
    "芒市": "德宏",
    "畹町": "德宏",
    "独龙江": "怒江",
    "丙中洛": "怒江",
    "秋那桶": "怒江",
    "雾里村": "怒江",
    "老姆登": "怒江",
    "知子罗": "怒江",
    "青海湖": "海南",
    "茶卡盐湖": "海西",
    "塔尔寺": "西宁",
    "坎布拉": "黄南",
    "年保玉则": "果洛",
    "三江源": "玉树",
    "可可西里": "海西",
    "莫高窟": "敦煌",
    "鸣沙山": "敦煌",
    "月牙泉": "敦煌",
    "雅丹魔鬼城": "敦煌",
    "玉门关": "敦煌",
    "阳关": "敦煌",
    "嘉峪关关城": "嘉峪关",
    "悬壁长城": "嘉峪关",
    "七彩丹霞": "张掖",
    "马蹄寺": "张掖",
    "大佛寺": "张掖",
    "平山湖大峡谷": "张掖",
    "山丹军马场": "张掖",
    "麦积山": "天水",
    "伏羲庙": "天水",
    "崆峒山": "平凉",
    "拉卜楞寺": "甘南",
    "郎木寺": "甘南",
    "扎尕那": "甘南",
    "桑科草原": "甘南",
    "尕海": "甘南",
    "黄河第一湾": "甘南",
    "花湖": "甘南",
    "若尔盖": "四川阿坝",
    "九曲黄河": "阿坝",
    "月亮湾": "阿坝",
    "俄么塘": "阿坝",
    "达古冰川": "阿坝",
    "毕棚沟": "阿坝",
    "四姑娘山": "阿坝",
    "卧龙": "阿坝",
    "汶川": "阿坝",
    "理县": "阿坝",
    "茂县": "阿坝",
    "松潘": "阿坝",
    "川主寺": "阿坝",
    "黄龙九寨": "阿坝",
    "米亚罗": "阿坝",
    "桃坪羌寨": "阿坝",
    "甘堡藏寨": "阿坝",
    "毕棚": "阿坝",
    "古尔沟": "阿坝",
    "鹧鸪山": "阿坝",
    "雅克夏": "阿坝",
    "奶子沟": "阿坝",
    "卡龙沟": "阿坝",
    "达古": "阿坝",
    "三奥雪山": "阿坝",
    "莲宝叶则": "阿坝",
    "神座": "阿坝",
    "曼扎塘": "阿坝",
    "壤塘": "阿坝",
    "金川": "阿坝",
    "马尔康": "阿坝",
    "红原": "阿坝",
    "阿坝县": "阿坝",
    "若尔盖县": "阿坝",
    "九寨沟县": "阿坝",
    "小金": "阿坝",
    "金川": "阿坝",
    "汶川": "阿坝",
    "理县": "阿坝",
    "茂县": "阿坝",
    "松潘": "阿坝",
    "九寨沟": "阿坝",
    "金川": "阿坝",
    "小金": "阿坝",
    "阿坝": "阿坝",
    "若尔盖": "阿坝",
    "红原": "阿坝",
    "壤塘": "阿坝",
    "茂县": "阿坝",
    "汶川": "阿坝",
    "理县": "阿坝",
    "松潘": "阿坝",
    "九寨沟": "阿坝",
    "金川": "阿坝",
    "小金": "阿坝",
    "黑水": "阿坝",
    "马尔康": "阿坝",
}


class CityExtractor:
    """城市标签提取器"""
    
    def __init__(self):
        self.city_keywords = CITY_KEYWORDS
        self.aliases = CITY_ALIASES
        # 构建反向索引（关键词 -> 城市）
        self.keyword_to_city = {}
        for city, keywords in self.city_keywords.items():
            for keyword in keywords:
                self.keyword_to_city[keyword.lower()] = city
    
    def extract_cities(self, title: str, content: str = "", itinerary: dict = None) -> List[Dict]:
        """
        从日记中提取城市标签
        
        Args:
            title: 日记标题
            content: 日记内容（可选）
            itinerary: 行程数据（可选）
            
        Returns:
            [
                {"city": "杭州", "confidence": 0.95, "source": "title"},
                {"city": "苏州", "confidence": 0.80, "source": "content"}
            ]
        """
        results = []
        city_scores = {}
        
        # 1. 标题匹配（权重最高）
        title_cities = self._match_cities(title, weight=1.0)
        for city, score in title_cities.items():
            city_scores[city] = {"score": score, "source": "title"}
        
        # 2. 内容匹配
        if content:
            content_cities = self._match_cities(content, weight=0.6)
            for city, score in content_cities.items():
                if city in city_scores:
                    # 取最高分，不完全叠加避免过高
                    city_scores[city]["score"] = max(city_scores[city]["score"], score)
                else:
                    city_scores[city] = {"score": score * 0.6, "source": "content"}
        
        # 3. 行程数据匹配
        if itinerary:
            itinerary_cities = self._extract_from_itinerary(itinerary)
            for city in itinerary_cities:
                if city in city_scores:
                    city_scores[city]["score"] = min(city_scores[city]["score"] + 0.2, 1.0)
                else:
                    city_scores[city] = {"score": 0.7, "source": "itinerary"}
        
        # 4. 转换结果并过滤低置信度
        for city, data in city_scores.items():
            confidence = min(data["score"], 1.0)
            if confidence >= 0.5:  # 置信度阈值
                results.append({
                    "city": city,
                    "confidence": round(confidence, 2),
                    "source": data["source"]
                })
        
        # 按置信度排序
        results.sort(key=lambda x: x["confidence"], reverse=True)
        
        # 最多返回3个城市（避免过多标签）
        return results[:3]
    
    def _match_cities(self, text: str, weight: float = 1.0) -> Dict[str, float]:
        """匹配文本中的城市关键词"""
        cities_found = {}
        if not text:
            return cities_found
            
        text_lower = text.lower()
        
        for city, keywords in self.city_keywords.items():
            score = 0
            matched_keywords = set()
            
            for keyword in keywords:
                keyword_lower = keyword.lower()
                
                # 使用简单的字符串查找（避免正则对中文的边界问题）
                matches = []
                idx = text_lower.find(keyword_lower)
                while idx != -1:
                    # 检查是否是完整词
                    before_char = text_lower[idx-1:idx] if idx > 0 else ''
                    after_pos = idx + len(keyword_lower)
                    after_char = text_lower[after_pos:after_pos+1] if after_pos < len(text_lower) else ''
                    
                    # CJK Unicode 范围
                    CJK_START = '\u4e00'
                    CJK_END = '\u9fff'
                    
                    # 检查前后字符是否是 CJK 字符
                    before_is_cjk = before_char and CJK_START <= before_char <= CJK_END
                    after_is_cjk = after_char and CJK_START <= after_char <= CJK_END
                    
                    # 关键词本身是否是 CJK 字符
                    keyword_is_cjk = all(CJK_START <= c <= CJK_END for c in keyword_lower if c.strip())
                    
                    # 有效匹配逻辑：
                    # 1. 前面是开头或非 CJK 字符（避免部分匹配前面）
                    # 2. 对于纯 CJK 关键词：后面接 CJK 是正常的（如"大理古城"）
                    # 3. 对于非 CJK 关键词：后面应该是非字母数字或结尾
                    is_valid = (idx == 0 or not before_is_cjk)
                    
                    if is_valid:
                        matches.append(idx)
                    
                    idx = text_lower.find(keyword_lower, idx + 1)
                
                if matches:
                    # 避免同一关键词重复计分
                    if keyword_lower not in matched_keywords:
                        matched_keywords.add(keyword_lower)
                        
                        # 根据关键词类型给分
                        if keyword == city:  # 城市本名
                            score += 1.0 * weight
                        elif len(keyword) <= 2:  # 简称（沪、杭）
                            score += 0.8 * weight
                        else:  # 别名/英文名
                            score += 0.9 * weight
            
            if score > 0:
                cities_found[city] = min(score, 1.0)
        
        return cities_found
    
    def _extract_from_itinerary(self, itinerary: dict) -> List[str]:
        """从行程数据中提取城市"""
        cities = []
        if not isinstance(itinerary, (list, dict)):
            return cities
            
        # 处理列表格式
        if isinstance(itinerary, list):
            for day in itinerary:
                if isinstance(day, dict):
                    # 从地点描述中提取
                    spots = day.get("spots", [])
                    for spot in spots:
                        if isinstance(spot, dict):
                            location = spot.get("location", "")
                            description = spot.get("description", "")
                            
                            # 合并文本进行匹配
                            combined_text = f"{location} {description}"
                            matched = self._match_cities(combined_text, weight=0.5)
                            cities.extend(matched.keys())
        
        # 去重
        return list(set(cities))
    
    def resolve_alias(self, name: str) -> str:
        """解析别名到标准城市名"""
        return self.aliases.get(name, name)
    
    def get_all_cities(self) -> List[str]:
        """获取所有城市名称列表"""
        return list(self.city_keywords.keys())


# 单例模式，全局使用
_extractor = None

def get_extractor() -> CityExtractor:
    """获取城市提取器实例（单例）"""
    global _extractor
    if _extractor is None:
        _extractor = CityExtractor()
    return _extractor


def extract_cities(title: str, content: str = "", itinerary: dict = None) -> List[Dict]:
    """
    便捷函数：提取城市标签
    
    使用示例:
        >>> extract_cities("杭州西湖两日游", "游玩了断桥残雪、雷峰塔")
        [{'city': '杭州', 'confidence': 1.0, 'source': 'title'}]
    """
    extractor = get_extractor()
    return extractor.extract_cities(title, content, itinerary)


if __name__ == "__main__":
    # 测试
    test_cases = [
        ("杭州西湖两日游", "游玩了断桥残雪、雷峰塔"),
        ("成都美食之旅", "打卡了宽窄巷子、锦里"),
        ("西藏拉萨朝圣之路", "布达拉宫、大昭寺"),
        ("厦门鼓浪屿漫步", "最美转角、日光岩"),
        ("北京故宫一日游", ""),
        ("周末去上海玩", "外滩、东方明珠"),
        ("三亚海岛日记", "亚龙湾、天涯海角"),
        ("云南之旅", "丽江古城、大理洱海"),
    ]
    
    extractor = CityExtractor()
    print("=" * 60)
    print("城市提取测试")
    print("=" * 60)
    
    for title, content in test_cases:
        cities = extractor.extract_cities(title, content)
        cities_str = ", ".join([f"{c['city']}({c['confidence']})" for c in cities])
        print(f"标题: {title}")
        print(f"提取: {cities_str or '无'}")
        print("-" * 40)
