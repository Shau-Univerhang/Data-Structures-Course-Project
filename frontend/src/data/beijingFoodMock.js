/**
 * 北京景点附近美食 Mock 数据集
 * 用于离线测试和前端开发调试
 *
 * 数据结构说明：
 * - 按景点名称分组，每个景点对应 10-15 条美食数据
 * - 美食字段：id, name, cuisine_type, rating, heat_score, distance_m, price_range, tags, location_lng, location_lat
 */

const BEIJING_FOOD_MOCK = {
  // ========== 天安门广场 ==========
  '天安门广场': [
    { id: 101, name: '全聚德烤鸭店(前门店)', cuisine_type: '北京菜', rating: 4.7, heat_score: 9850, distance_m: 450, price_range: '¥¥¥¥', tags: ['百年老字号', '挂炉烤鸭', '宫廷菜'], location_lng: 116.4001, location_lat: 39.8995 },
    { id: 102, name: '便宜坊烤鸭店(鲜鱼口街店)', cuisine_type: '北京菜', rating: 4.6, heat_score: 8720, distance_m: 380, price_range: '¥¥¥', tags: ['焖炉烤鸭', '非遗技艺', '老字号'], location_lng: 116.3995, location_lat: 39.8988 },
    { id: 103, name: '都一处烧麦馆(前门店)', cuisine_type: '北京小吃', rating: 4.5, heat_score: 7650, distance_m: 520, price_range: '¥¥', tags: ['烧麦', '乾隆赐名', '三百年历史'], location_lng: 116.4012, location_lat: 39.9001 },
    { id: 104, name: '庆丰包子铺(前门店)', cuisine_type: '北京小吃', rating: 4.3, heat_score: 9200, distance_m: 280, price_range: '¥', tags: ['包子', '炒肝', '亲民价'], location_lng: 116.3988, location_lat: 39.9005 },
    { id: 105, name: '护国寺小吃(前门店)', cuisine_type: '北京小吃', rating: 4.4, heat_score: 8100, distance_m: 620, price_range: '¥', tags: ['豌豆黄', '驴打滚', '艾窝窝'], location_lng: 116.4020, location_lat: 39.9010 },
    { id: 106, name: '四季民福烤鸭店(前门大栅栏店)', cuisine_type: '北京菜', rating: 4.8, heat_score: 11200, distance_m: 750, price_range: '¥¥¥¥', tags: ['酥香嫩烤鸭', '观景位', '网红店'], location_lng: 116.3975, location_lat: 39.8970 },
    { id: 107, name: '东来顺饭庄(大栅栏店)', cuisine_type: '涮羊肉', rating: 4.5, heat_score: 6800, distance_m: 890, price_range: '¥¥¥', tags: ['铜锅涮肉', '清真', '老字号'], location_lng: 116.3968, location_lat: 39.8965 },
    { id: 108, name: '爆肚冯(前门店)', cuisine_type: '北京小吃', rating: 4.4, heat_score: 5900, distance_m: 410, price_range: '¥¥', tags: ['爆肚', '肚仁', '芥末墩'], location_lng: 116.3998, location_lat: 39.8990 },
    { id: 109, name: '天兴居(鲜鱼口店)', cuisine_type: '北京小吃', rating: 4.3, heat_score: 5400, distance_m: 350, price_range: '¥', tags: ['炒肝', '包子', '百年老店'], location_lng: 116.4005, location_lat: 39.8992 },
    { id: 110, name: '锦芳小吃(磁器口店)', cuisine_type: '北京小吃', rating: 4.2, heat_score: 4800, distance_m: 1200, price_range: '¥', tags: ['元宵', '奶油炸糕', '豆汁'], location_lng: 116.4050, location_lat: 39.8920 },
    { id: 111, name: '大董烤鸭店(王府井店)', cuisine_type: '创意北京菜', rating: 4.7, heat_score: 8900, distance_m: 1500, price_range: '¥¥¥¥¥', tags: ['意境菜', '酥不腻烤鸭', '高端'], location_lng: 116.4105, location_lat: 39.9120 },
    { id: 112, name: '海碗居(增光路店)', cuisine_type: '北京菜', rating: 4.4, heat_score: 6200, distance_m: 1800, price_range: '¥¥', tags: ['炸酱面', '豆汁焦圈', '京味十足'], location_lng: 116.3380, location_lat: 39.9230 },
  ],

  // ========== 故宫博物院 ==========
  '故宫博物院': [
    { id: 201, name: '故宫冰窖餐厅', cuisine_type: '创意中餐', rating: 4.6, heat_score: 13200, distance_m: 80, price_range: '¥¥¥', tags: ['故宫文创', '宫廷风', '打卡必去'], location_lng: 116.3970, location_lat: 39.9165 },
    { id: 202, name: '角楼咖啡', cuisine_type: '咖啡甜品', rating: 4.5, heat_score: 15800, distance_m: 150, price_range: '¥¥', tags: ['故宫角楼', '网红咖啡', '拍照圣地'], location_lng: 116.3978, location_lat: 39.9170 },
    { id: 203, name: '四季民福烤鸭店(故宫店)', cuisine_type: '北京菜', rating: 4.8, heat_score: 14500, distance_m: 600, price_range: '¥¥¥¥', tags: ['观景烤鸭', '故宫景观', '排队王'], location_lng: 116.4010, location_lat: 39.9150 },
    { id: 204, name: '满恒记清真涮羊肉(平安里店)', cuisine_type: '涮羊肉', rating: 4.7, heat_score: 9800, distance_m: 1800, price_range: '¥¥¥', tags: ['手切羊肉', '糖饼', '清真'], location_lng: 116.3700, location_lat: 39.9320 },
    { id: 205, name: '聚宝源(牛街总店)', cuisine_type: '涮羊肉', rating: 4.8, heat_score: 11200, distance_m: 3500, price_range: '¥¥¥', tags: ['铜锅涮肉', '手切鲜羊肉', '牛街必吃'], location_lng: 116.3715, location_lat: 39.8835 },
    { id: 206, name: '姚记炒肝店(鼓楼店)', cuisine_type: '北京小吃', rating: 4.4, heat_score: 8900, distance_m: 2200, price_range: '¥', tags: ['炒肝', '包子', '卤煮'], location_lng: 116.3900, location_lat: 39.9400 },
    { id: 207, name: '宏源南门涮肉(天坛店)', cuisine_type: '涮羊肉', rating: 4.6, heat_score: 7600, distance_m: 2800, price_range: '¥¥¥', tags: ['天坛南门', '涮肉', '老北京风味'], location_lng: 116.4070, location_lat: 39.8750 },
    { id: 208, name: '北新桥卤煮老店', cuisine_type: '北京小吃', rating: 4.5, heat_score: 7200, distance_m: 2500, price_range: '¥', tags: ['卤煮火烧', '大肠', '老字号'], location_lng: 116.4150, location_lat: 39.9350 },
    { id: 209, name: '白魁老号饭庄(宽街店)', cuisine_type: '北京菜', rating: 4.3, heat_score: 5400, distance_m: 1900, price_range: '¥¥', tags: ['烧羊肉', '清真', '百年老店'], location_lng: 116.4050, location_lat: 39.9300 },
    { id: 210, name: '花家怡园(四合院总店)', cuisine_type: '创意北京菜', rating: 4.6, heat_score: 6800, distance_m: 1600, price_range: '¥¥¥¥', tags: ['四合院', '八爷烤鸭', '宫廷菜'], location_lng: 116.4000, location_lat: 39.9350 },
    { id: 211, name: '厉家菜(德胜门总店)', cuisine_type: '宫廷菜', rating: 4.5, heat_score: 6200, distance_m: 2800, price_range: '¥¥¥¥¥', tags: ['宫廷御膳', '私房菜', '预约制'], location_lng: 116.3800, location_lat: 39.9500 },
    { id: 212, name: '小肠陈卤煮(南横街老店)', cuisine_type: '北京小吃', rating: 4.4, heat_score: 5800, distance_m: 3200, price_range: '¥¥', tags: ['卤煮', '小肠', '百年传承'], location_lng: 116.3850, location_lat: 39.8850 },
  ],

  // ========== 景山公园 ==========
  '景山公园': [
    { id: 301, name: '皇家冰窖小院', cuisine_type: '私房菜', rating: 4.7, heat_score: 5600, distance_m: 350, price_range: '¥¥¥¥', tags: ['皇家冰窖', '四合院', '高端私房'], location_lng: 116.3950, location_lat: 39.9280 },
    { id: 302, name: '什刹海烤肉季(银锭桥店)', cuisine_type: '烤肉', rating: 4.6, heat_score: 7800, distance_m: 800, price_range: '¥¥¥', tags: ['烤羊肉', '银锭观山', '老字号'], location_lng: 116.3850, location_lat: 39.9380 },
    { id: 303, name: '同和居(什刹海店)', cuisine_type: '鲁菜', rating: 4.5, heat_score: 4500, distance_m: 900, price_range: '¥¥¥', tags: ['鲁菜老字号', '三不粘', '糟溜鱼片'], location_lng: 116.3860, location_lat: 39.9370 },
    { id: 304, name: '庆云楼饭庄', cuisine_type: '鲁菜', rating: 4.4, heat_score: 4200, distance_m: 750, price_range: '¥¥¥', tags: ['八大楼之一', '百年老店', '什刹海'], location_lng: 116.3870, location_lat: 39.9390 },
    { id: 305, name: '烤肉宛(南礼士路店)', cuisine_type: '烤肉', rating: 4.5, heat_score: 5100, distance_m: 3200, price_range: '¥¥¥', tags: ['烤牛肉', '清真', '康熙赐匾'], location_lng: 116.3500, location_lat: 39.9100 },
    { id: 306, name: '峨眉酒家(地安门店)', cuisine_type: '川菜', rating: 4.4, heat_score: 6800, distance_m: 1100, price_range: '¥¥', tags: ['宫保鸡丁', '川菜老字号', '地安门'], location_lng: 116.3900, location_lat: 39.9350 },
    { id: 307, name: '马凯餐厅(地安门店)', cuisine_type: '湘菜', rating: 4.3, heat_score: 5900, distance_m: 1000, price_range: '¥¥', tags: ['湘菜老字号', '左宗棠鸡', '地安门'], location_lng: 116.3910, location_lat: 39.9340 },
    { id: 308, name: '柳泉居饭庄', cuisine_type: '鲁菜', rating: 4.5, heat_score: 3800, distance_m: 1800, price_range: '¥¥¥', tags: ['豆包', '鲁菜', '明代老号'], location_lng: 116.3700, location_lat: 39.9200 },
    { id: 309, name: '砂锅居(西四店)', cuisine_type: '北京菜', rating: 4.4, heat_score: 4600, distance_m: 2000, price_range: '¥¥¥', tags: ['砂锅白肉', '百年老店', '满族风味'], location_lng: 116.3680, location_lat: 39.9220 },
    { id: 310, name: '曲园酒楼', cuisine_type: '湘菜', rating: 4.3, heat_score: 3200, distance_m: 2200, price_range: '¥¥', tags: ['湘菜老字号', '地安门', '剁椒鱼头'], location_lng: 116.3950, location_lat: 39.9400 },
  ],

  // ========== 南锣鼓巷 ==========
  '南锣鼓巷': [
    { id: 401, name: '文宇奶酪店', cuisine_type: '甜品', rating: 4.6, heat_score: 15200, distance_m: 120, price_range: '¥', tags: ['宫廷奶酪', '双皮奶', '红豆奶酪'], location_lng: 116.4030, location_lat: 39.9360 },
    { id: 402, name: '海小姐玫瑰饼', cuisine_type: '甜品', rating: 4.5, heat_score: 9800, distance_m: 80, price_range: '¥', tags: ['玫瑰饼', '现烤', '伴手礼'], location_lng: 116.4025, location_lat: 39.9355 },
    { id: 403, name: '中央戏剧学院实验剧场餐厅', cuisine_type: '融合菜', rating: 4.4, heat_score: 4200, distance_m: 200, price_range: '¥¥¥', tags: ['中戏', '艺术氛围', '创意菜'], location_lng: 116.4040, location_lat: 39.9370 },
    { id: 404, name: '菊儿人家', cuisine_type: '北京菜', rating: 4.3, heat_score: 7600, distance_m: 150, price_range: '¥¥', tags: ['卤肉饭', '胡同菜', '家常味'], location_lng: 116.4035, location_lat: 39.9365 },
    { id: 405, name: '咂摸', cuisine_type: '创意菜', rating: 4.5, heat_score: 6800, distance_m: 180, price_range: '¥¥', tags: ['宫保鸡丁披萨', '创意融合', '网红'], location_lng: 116.4020, location_lat: 39.9350 },
    { id: 406, name: '鬼味烤翅', cuisine_type: '烧烤', rating: 4.4, heat_score: 11200, distance_m: 250, price_range: '¥¥', tags: ['烤翅', 'BT辣', '深夜食堂'], location_lng: 116.4015, location_lat: 39.9345 },
    { id: 407, name: '双皮奶专家', cuisine_type: '甜品', rating: 4.3, heat_score: 5400, distance_m: 300, price_range: '¥', tags: ['双皮奶', '姜撞奶', '广式甜品'], location_lng: 116.4045, location_lat: 39.9375 },
    { id: 408, name: '过客', cuisine_type: '西餐', rating: 4.5, heat_score: 6200, distance_m: 350, price_range: '¥¥¥', tags: ['披萨', '意面', '胡同西餐'], location_lng: 116.4010, location_lat: 39.9340 },
    { id: 409, name: '锣鼓洞天烤鸭店', cuisine_type: '北京菜', rating: 4.2, heat_score: 3800, distance_m: 400, price_range: '¥¥¥', tags: ['烤鸭', '四合院', '胡同里'], location_lng: 116.4050, location_lat: 39.9380 },
    { id: 410, name: '烧虾师', cuisine_type: '小龙虾', rating: 4.4, heat_score: 8900, distance_m: 500, price_range: '¥¥¥', tags: ['小龙虾', '麻辣', '夜宵'], location_lng: 116.4000, location_lat: 39.9330 },
    { id: 411, name: '付小姐在成都', cuisine_type: '川菜', rating: 4.5, heat_score: 10200, distance_m: 600, price_range: '¥¥', tags: ['串串香', '冒菜', '成都味'], location_lng: 116.4060, location_lat: 39.9390 },
    { id: 412, name: '姚记炒肝(鼓楼店)', cuisine_type: '北京小吃', rating: 4.4, heat_score: 9500, distance_m: 700, price_range: '¥', tags: ['炒肝', '包子', '鼓楼'], location_lng: 116.3900, location_lat: 39.9400 },
  ],

  // ========== 颐和园 ==========
  '颐和园': [
    { id: 501, name: '听鹂馆饭庄', cuisine_type: '宫廷菜', rating: 4.6, heat_score: 6800, distance_m: 200, price_range: '¥¥¥¥¥', tags: ['颐和园', '宫廷御膳', '皇家园林'], location_lng: 116.2750, location_lat: 39.9950 },
    { id: 502, name: '西贝莜面村(苏州街店)', cuisine_type: '西北菜', rating: 4.5, heat_score: 8200, distance_m: 1500, price_range: '¥¥', tags: ['莜面', '羊肉串', '西北风味'], location_lng: 116.2800, location_lat: 39.9850 },
    { id: 503, name: '烤肉季(颐和园店)', cuisine_type: '烤肉', rating: 4.4, heat_score: 4500, distance_m: 800, price_range: '¥¥¥', tags: ['烤羊肉', '老字号', '颐和园'], location_lng: 116.2780, location_lat: 39.9920 },
    { id: 504, name: '功德林素菜饭庄(苏州街店)', cuisine_type: '素食', rating: 4.5, heat_score: 3800, distance_m: 1800, price_range: '¥¥¥', tags: ['素食', '仿荤菜', '百年老店'], location_lng: 116.2820, location_lat: 39.9830 },
    { id: 505, name: '大鸭梨烤鸭店(颐和园店)', cuisine_type: '北京菜', rating: 4.3, heat_score: 5600, distance_m: 1200, price_range: '¥¥', tags: ['烤鸭', '家常菜', '性价比高'], location_lng: 116.2720, location_lat: 39.9880 },
    { id: 506, name: '巴依老爷新疆美食(中关村店)', cuisine_type: '新疆菜', rating: 4.6, heat_score: 7200, distance_m: 2500, price_range: '¥¥', tags: ['大盘鸡', '烤包子', '拉条子'], location_lng: 116.3150, location_lat: 39.9850 },
    { id: 507, name: '云海肴云南菜(中关村店)', cuisine_type: '云南菜', rating: 4.4, heat_score: 6800, distance_m: 2800, price_range: '¥¥', tags: ['汽锅鸡', '过桥米线', '云南风味'], location_lng: 116.3180, location_lat: 39.9820 },
    { id: 508, name: '胡大饭馆(簋街店)', cuisine_type: '川菜', rating: 4.7, heat_score: 13500, distance_m: 8000, price_range: '¥¥¥', tags: ['麻辣小龙虾', '簋街排队王', '夜宵'], location_lng: 116.4170, location_lat: 39.9400 },
    { id: 509, name: '金鼎轩(团结湖店)', cuisine_type: '粤菜', rating: 4.4, heat_score: 5900, distance_m: 8500, price_range: '¥¥', tags: ['24小时', '粤式点心', '夜宵'], location_lng: 116.4600, location_lat: 39.9250 },
    { id: 510, name: '眉州东坡(中关村店)', cuisine_type: '川菜', rating: 4.5, heat_score: 6200, distance_m: 2600, price_range: '¥¥¥', tags: ['东坡肘子', '川菜', '商务宴请'], location_lng: 116.3120, location_lat: 39.9880 },
  ],

  // ========== 天坛公园 ==========
  '天坛公园': [
    { id: 601, name: '宏源南门涮肉(天坛店)', cuisine_type: '涮羊肉', rating: 4.7, heat_score: 8900, distance_m: 300, price_range: '¥¥¥', tags: ['天坛南门', '铜锅涮肉', '老北京'], location_lng: 116.4070, location_lat: 39.8750 },
    { id: 602, name: '老磁器口豆汁店', cuisine_type: '北京小吃', rating: 4.3, heat_score: 7200, distance_m: 800, price_range: '¥', tags: ['豆汁', '焦圈', '北京特色'], location_lng: 116.4050, location_lat: 39.8850 },
    { id: 603, name: '锦芳小吃(磁器口店)', cuisine_type: '北京小吃', rating: 4.4, heat_score: 6500, distance_m: 900, price_range: '¥', tags: ['元宵', '奶油炸糕', '清真'], location_lng: 116.4060, location_lat: 39.8860 },
    { id: 604, name: '便宜坊烤鸭店(玉蜓桥店)', cuisine_type: '北京菜', rating: 4.5, heat_score: 5600, distance_m: 1200, price_range: '¥¥¥', tags: ['焖炉烤鸭', '老字号', '天坛附近'], location_lng: 116.4100, location_lat: 39.8700 },
    { id: 605, name: '都一处烧麦馆(方庄店)', cuisine_type: '北京小吃', rating: 4.3, heat_score: 4200, distance_m: 2500, price_range: '¥¥', tags: ['烧麦', '乾隆赐名', '三百年'], location_lng: 116.4200, location_lat: 39.8600 },
    { id: 606, name: '小肠陈卤煮(南横街老店)', cuisine_type: '北京小吃', rating: 4.5, heat_score: 7800, distance_m: 1500, price_range: '¥¥', tags: ['卤煮', '小肠', '百年传承'], location_lng: 116.3850, location_lat: 39.8850 },
    { id: 607, name: '丰泽园饭庄(珠市口店)', cuisine_type: '鲁菜', rating: 4.6, heat_score: 5100, distance_m: 2000, price_range: '¥¥¥¥', tags: ['鲁菜泰斗', '葱烧海参', '商务宴请'], location_lng: 116.3950, location_lat: 39.8850 },
    { id: 608, name: '晋阳饭庄(虎坊桥店)', cuisine_type: '山西菜', rating: 4.4, heat_score: 3800, distance_m: 2200, price_range: '¥¥¥', tags: ['香酥鸭', '过油肉', '纪晓岚故居'], location_lng: 116.3900, location_lat: 39.8880 },
    { id: 609, name: '功德林素菜饭庄(前门东大街店)', cuisine_type: '素食', rating: 4.5, heat_score: 3400, distance_m: 2800, price_range: '¥¥¥', tags: ['素食', '仿荤', '百年老店'], location_lng: 116.4000, location_lat: 39.8950 },
    { id: 610, name: '泰丰楼(前门西大街店)', cuisine_type: '鲁菜', rating: 4.3, heat_score: 2900, distance_m: 3000, price_range: '¥¥¥', tags: ['鲁菜老字号', '八大楼之一', '三不粘'], location_lng: 116.3950, location_lat: 39.9000 },
  ],

  // ========== 什刹海 ==========
  '什刹海': [
    { id: 701, name: '烤肉季(什刹海总店)', cuisine_type: '烤肉', rating: 4.7, heat_score: 9200, distance_m: 150, price_range: '¥¥¥¥', tags: ['烤羊肉', '银锭观山', '中华老字号'], location_lng: 116.3850, location_lat: 39.9380 },
    { id: 702, name: '爆肚张', cuisine_type: '北京小吃', rating: 4.5, heat_score: 6800, distance_m: 200, price_range: '¥¥', tags: ['爆肚', '肚仁', '后海'], location_lng: 116.3860, location_lat: 39.9390 },
    { id: 703, name: '九门小吃', cuisine_type: '北京小吃', rating: 4.3, heat_score: 7200, distance_m: 300, price_range: '¥', tags: ['豆汁', '焦圈', '驴打滚'], location_lng: 116.3870, location_lat: 39.9400 },
    { id: 704, name: '宋庆龄故居茶室', cuisine_type: '茶室', rating: 4.4, heat_score: 3200, distance_m: 400, price_range: '¥¥', tags: ['宋庆龄故居', '茶点', '安静'], location_lng: 116.3880, location_lat: 39.9370 },
    { id: 705, name: '孔乙己酒店(什刹海店)', cuisine_type: '江浙菜', rating: 4.5, heat_score: 5600, distance_m: 500, price_range: '¥¥¥', tags: ['绍兴菜', '黄酒', '茴香豆'], location_lng: 116.3840, location_lat: 39.9410 },
    { id: 706, name: '望德楼清真餐厅', cuisine_type: '清真菜', rating: 4.4, heat_score: 4800, distance_m: 350, price_range: '¥¥', tags: ['清真', '涮肉', '后海'], location_lng: 116.3890, location_lat: 39.9385 },
    { id: 707, name: '荷花市场酒吧街', cuisine_type: '酒吧', rating: 4.2, heat_score: 8500, distance_m: 250, price_range: '¥¥¥', tags: ['酒吧', '夜景', '后海'], location_lng: 116.3830, location_lat: 39.9370 },
    { id: 708, name: '银锭桥小吃', cuisine_type: '北京小吃', rating: 4.3, heat_score: 6200, distance_m: 180, price_range: '¥', tags: ['灌肠', '炸糕', '银锭桥'], location_lng: 116.3855, location_lat: 39.9385 },
    { id: 709, name: '后海16号', cuisine_type: '创意菜', rating: 4.5, heat_score: 4500, distance_m: 600, price_range: '¥¥¥¥', tags: ['私房菜', '四合院', '商务'], location_lng: 116.3820, location_lat: 39.9400 },
    { id: 710, name: '鸦儿李记涮肉', cuisine_type: '涮羊肉', rating: 4.6, heat_score: 7800, distance_m: 450, price_range: '¥¥¥', tags: ['涮肉', '烧饼', '后海'], location_lng: 116.3865, location_lat: 39.9395 },
  ],

  // ========== 八达岭长城 ==========
  '八达岭长城': [
    { id: 801, name: '八达岭饭店', cuisine_type: '北京菜', rating: 4.2, heat_score: 3200, distance_m: 500, price_range: '¥¥¥', tags: ['长城脚下', '团餐', '家常菜'], location_lng: 116.0170, location_lat: 39.3540 },
    { id: 802, name: '岔道古城农家乐', cuisine_type: '农家菜', rating: 4.4, heat_score: 2800, distance_m: 1200, price_range: '¥¥', tags: ['农家菜', '岔道古城', '柴鸡'], location_lng: 116.0150, location_lat: 39.3600 },
    { id: 803, name: '长城脚下的公社餐厅', cuisine_type: '融合菜', rating: 4.5, heat_score: 2100, distance_m: 2000, price_range: '¥¥¥¥', tags: ['凯悦', '设计酒店', '景观餐厅'], location_lng: 116.0100, location_lat: 39.3650 },
    { id: 804, name: '石峡村石光长城民宿餐厅', cuisine_type: '农家菜', rating: 4.3, heat_score: 1800, distance_m: 3500, price_range: '¥¥', tags: ['石峡村', '豆腐宴', '民宿'], location_lng: 116.0050, location_lat: 39.3700 },
    { id: 805, name: '延庆火勺铺', cuisine_type: '北京小吃', rating: 4.4, heat_score: 2400, distance_m: 8000, price_range: '¥', tags: ['延庆火勺', '地方特色', '便宜'], location_lng: 115.9800, location_lat: 39.4500 },
    { id: 806, name: '柳沟豆腐宴', cuisine_type: '农家菜', rating: 4.5, heat_score: 3200, distance_m: 15000, price_range: '¥¥', tags: ['豆腐宴', '柳沟', '农家'], location_lng: 115.9500, location_lat: 39.5000 },
    { id: 807, name: '永宁古城火勺', cuisine_type: '北京小吃', rating: 4.3, heat_score: 2100, distance_m: 12000, price_range: '¥', tags: ['永宁古城', '火勺', '传统'], location_lng: 116.0500, location_lat: 39.5500 },
    { id: 808, name: '龙庆峡农家院', cuisine_type: '农家菜', rating: 4.2, heat_score: 1500, distance_m: 18000, price_range: '¥¥', tags: ['龙庆峡', '烤鱼', '农家'], location_lng: 115.9800, location_lat: 39.6000 },
    { id: 809, name: '八达岭野生动物园餐厅', cuisine_type: '快餐', rating: 3.9, heat_score: 1200, distance_m: 3000, price_range: '¥¥', tags: ['动物园', '快餐', '亲子'], location_lng: 116.0200, location_lat: 39.3400 },
    { id: 810, name: '世园公园美食街', cuisine_type: '小吃', rating: 4.1, heat_score: 1800, distance_m: 20000, price_range: '¥¥', tags: ['世园会', '美食街', '各国料理'], location_lng: 115.9500, location_lat: 39.4800 },
  ],

  // ========== 798艺术区 ==========
  '798艺术区': [
    { id: 901, name: '本宫的茶(798店)', cuisine_type: '茶饮', rating: 4.5, heat_score: 6200, distance_m: 200, price_range: '¥', tags: ['茶饮', '艺术区', '网红'], location_lng: 116.5010, location_lat: 39.9850 },
    { id: 902, name: 'AT CAFE', cuisine_type: '西餐', rating: 4.4, heat_score: 4800, distance_m: 300, price_range: '¥¥¥', tags: ['艺术咖啡', '西餐', '展览'], location_lng: 116.5020, location_lat: 39.9860 },
    { id: 903, name: '沈记菜馆', cuisine_type: '私房菜', rating: 4.6, heat_score: 3500, distance_m: 400, price_range: '¥¥¥¥', tags: ['私房菜', '艺术区', '预约'], location_lng: 116.5000, location_lat: 39.9840 },
    { id: 904, name: '小万食堂', cuisine_type: '川菜', rating: 4.5, heat_score: 5200, distance_m: 350, price_range: '¥¥', tags: ['川菜', '艺术区', '文艺'], location_lng: 116.5030, location_lat: 39.9870 },
    { id: 905, name: '佩斯北京餐厅', cuisine_type: '融合菜', rating: 4.3, heat_score: 2800, distance_m: 500, price_range: '¥¥¥¥', tags: ['佩斯画廊', '艺术餐厅', '高端'], location_lng: 116.4990, location_lat: 39.9830 },
    { id: 906, name: '尤伦斯当代艺术中心餐厅', cuisine_type: '西餐', rating: 4.4, heat_score: 3200, distance_m: 450, price_range: '¥¥¥', tags: ['UCCA', '艺术餐厅', 'brunch'], location_lng: 116.5040, location_lat: 39.9880 },
    { id: 907, name: '那家小馆(酒仙桥店)', cuisine_type: '北京菜', rating: 4.6, heat_score: 6800, distance_m: 1500, price_range: '¥¥¥', tags: ['宫廷菜', '那家', '酒仙桥'], location_lng: 116.5100, location_lat: 39.9800 },
    { id: 908, name: '将太无二(颐堤港店)', cuisine_type: '日料', rating: 4.5, heat_score: 7200, distance_m: 2000, price_range: '¥¥¥', tags: ['寿司', '刺身', '颐堤港'], location_lng: 116.5150, location_lat: 39.9750 },
    { id: 909, name: '蓝蛙(颐堤港店)', cuisine_type: '西餐', rating: 4.4, heat_score: 6500, distance_m: 2000, price_range: '¥¥¥', tags: ['汉堡', '西餐', '酒吧'], location_lng: 116.5160, location_lat: 39.9760 },
    { id: 910, name: '外婆家(颐堤港店)', cuisine_type: '江浙菜', rating: 4.3, heat_score: 7800, distance_m: 2000, price_range: '¥¥', tags: ['杭帮菜', '性价比高', '排队'], location_lng: 116.5170, location_lat: 39.9770 },
  ],

  // ========== 王府井 ==========
  '王府井': [
    { id: 1001, name: '东来顺饭庄(王府井店)', cuisine_type: '涮羊肉', rating: 4.5, heat_score: 8500, distance_m: 200, price_range: '¥¥¥', tags: ['铜锅涮肉', '清真', '老字号'], location_lng: 116.4100, location_lat: 39.9120 },
    { id: 1002, name: '狗不理包子(王府井店)', cuisine_type: '天津小吃', rating: 4.0, heat_score: 9200, distance_m: 150, price_range: '¥¥', tags: ['狗不理', '包子', '天津'], location_lng: 116.4110, location_lat: 39.9110 },
    { id: 1003, name: '王府井小吃街', cuisine_type: '小吃', rating: 4.1, heat_score: 12500, distance_m: 100, price_range: '¥', tags: ['小吃街', '烤串', '炸酱面'], location_lng: 116.4120, location_lat: 39.9100 },
    { id: 1004, name: '海碗居(王府井店)', cuisine_type: '北京菜', rating: 4.4, heat_score: 6800, distance_m: 300, price_range: '¥¥', tags: ['炸酱面', '豆汁', '京味'], location_lng: 116.4090, location_lat: 39.9130 },
    { id: 1005, name: '全聚德(王府井店)', cuisine_type: '北京菜', rating: 4.6, heat_score: 9800, distance_m: 400, price_range: '¥¥¥¥', tags: ['烤鸭', '老字号', '商务'], location_lng: 116.4080, location_lat: 39.9140 },
    { id: 1006, name: '吴裕泰茶庄(王府井店)', cuisine_type: '茶饮', rating: 4.5, heat_score: 7200, distance_m: 250, price_range: '¥', tags: ['花茶冰淇淋', '茶叶', '老字号'], location_lng: 116.4130, location_lat: 39.9090 },
    { id: 1007, name: '东方君悦大酒店悦庭', cuisine_type: '粤菜', rating: 4.7, heat_score: 4200, distance_m: 500, price_range: '¥¥¥¥¥', tags: ['五星酒店', '粤菜', '自助'], location_lng: 116.4140, location_lat: 39.9150 },
    { id: 1008, name: 'APM美食广场', cuisine_type: '美食广场', rating: 4.2, heat_score: 8500, distance_m: 350, price_range: '¥¥', tags: ['美食广场', '快餐', '年轻'], location_lng: 116.4150, location_lat: 39.9080 },
    { id: 1009, name: '局气(王府井店)', cuisine_type: '北京菜', rating: 4.5, heat_score: 7800, distance_m: 600, price_range: '¥¥¥', tags: ['创意北京菜', '兔爷', '网红'], location_lng: 116.4070, location_lat: 39.9160 },
    { id: 1010, name: '鼎泰丰(王府井店)', cuisine_type: '台湾菜', rating: 4.6, heat_score: 8200, distance_m: 450, price_range: '¥¥¥', tags: ['小笼包', '台湾', '精致'], location_lng: 116.4160, location_lat: 39.9070 },
  ],

  // ========== 三里屯 ==========
  '三里屯': [
    { id: 1101, name: '太古里南区美食街', cuisine_type: '美食广场', rating: 4.5, heat_score: 15200, distance_m: 100, price_range: '¥¥', tags: ['潮流', '网红', '各国料理'], location_lng: 116.4550, location_lat: 39.9350 },
    { id: 1102, name: 'Shake Shack(三里屯店)', cuisine_type: '汉堡', rating: 4.4, heat_score: 9800, distance_m: 150, price_range: '¥¥¥', tags: ['网红汉堡', '奶昔', '美式'], location_lng: 116.4560, location_lat: 39.9340 },
    { id: 1103, name: 'Page One 餐厅', cuisine_type: '西餐', rating: 4.5, heat_score: 6200, distance_m: 200, price_range: '¥¥¥', tags: ['书店餐厅', 'brunch', '文艺'], location_lng: 116.4540, location_lat: 39.9360 },
    { id: 1104, name: '那里花园意大利餐厅', cuisine_type: '意大利菜', rating: 4.6, heat_score: 4800, distance_m: 300, price_range: '¥¥¥¥', tags: ['意大利', '披萨', '那里花园'], location_lng: 116.4570, location_lat: 39.9330 },
    { id: 1105, name: '京A Taproom(三里屯店)', cuisine_type: '西餐', rating: 4.5, heat_score: 7200, distance_m: 250, price_range: '¥¥¥', tags: ['精酿啤酒', '汉堡', '露台'], location_lng: 116.4530, location_lat: 39.9370 },
    { id: 1106, name: '悠航鲜啤(三里屯店)', cuisine_type: '西餐', rating: 4.6, heat_score: 8500, distance_m: 350, price_range: '¥¥¥', tags: ['精酿', '汉堡', '薯条'], location_lng: 116.4580, location_lat: 39.9320 },
    { id: 1107, name: 'Migas(三里屯店)', cuisine_type: '西班牙菜', rating: 4.5, heat_score: 5600, distance_m: 400, price_range: '¥¥¥¥', tags: ['西班牙', '露台', '夜景'], location_lng: 116.4590, location_lat: 39.9310 },
    { id: 1108, name: ' Element Fresh(三里屯店)', cuisine_type: '轻食', rating: 4.3, heat_score: 4800, distance_m: 300, price_range: '¥¥¥', tags: ['轻食', '沙拉', '健康'], location_lng: 116.4520, location_lat: 39.9380 },
    { id: 1109, name: '海底捞(三里屯店)', cuisine_type: '火锅', rating: 4.7, heat_score: 11200, distance_m: 500, price_range: '¥¥¥', tags: ['服务', '火锅', '24小时'], location_lng: 116.4600, location_lat: 39.9300 },
    { id: 1110, name: '胡大饭馆(三里屯店)', cuisine_type: '川菜', rating: 4.6, heat_score: 9800, distance_m: 600, price_range: '¥¥¥', tags: ['小龙虾', '川菜', '夜宵'], location_lng: 116.4610, location_lat: 39.9290 },
  ],
}

/**
 * 根据景点名称获取 Mock 美食数据
 * @param {string} spotName - 景点名称
 * @param {string} sortBy - 排序方式: distance | rating | popularity
 * @param {string} keyword - 搜索关键词
 * @param {number} topK - 返回数量限制
 * @returns {Array} 美食列表
 */
export function getMockFoodsBySpot(spotName, sortBy = 'distance', keyword = '', topK = 10) {
  // 尝试直接匹配
  let foods = BEIJING_FOOD_MOCK[spotName] || []

  // 如果没有直接匹配，尝试部分匹配
  if (foods.length === 0) {
    const key = Object.keys(BEIJING_FOOD_MOCK).find(k => spotName.includes(k) || k.includes(spotName))
    if (key) {
      foods = BEIJING_FOOD_MOCK[key]
    }
  }

  // 深拷贝避免修改原数据
  let result = foods.map(f => ({ ...f }))

  // 关键词过滤
  if (keyword && keyword.trim()) {
    const kw = keyword.toLowerCase().trim()
    result = result.filter(f => {
      const fields = [
        f.name,
        f.cuisine_type,
        ...(f.tags || [])
      ].filter(Boolean).join(' ').toLowerCase()
      return fields.includes(kw)
    })
  }

  // 排序
  if (sortBy === 'distance') {
    result.sort((a, b) => (a.distance_m || Infinity) - (b.distance_m || Infinity))
  } else if (sortBy === 'rating') {
    result.sort((a, b) => (b.rating || 0) - (a.rating || 0))
  } else if (sortBy === 'popularity') {
    result.sort((a, b) => (b.heat_score || 0) - (a.heat_score || 0))
  }

  // 限制数量
  return result.slice(0, topK)
}

/**
 * 获取所有支持的景点名称列表
 */
export function getSupportedSpots() {
  return Object.keys(BEIJING_FOOD_MOCK)
}

export default BEIJING_FOOD_MOCK
