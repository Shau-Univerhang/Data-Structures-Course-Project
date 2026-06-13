/**
 * 多城市美食数据生成器 (Multi-City Food Data Generator)
 * ————————————————————————————————————————————————————————
 * 支持全部 21 个城市，自动生成贴合当地菜系的仿真美食数据。
 *
 * 生成策略：
 *   · 西安 — 保留原有 307 条模板的丰富数据（xianFoodGenerator.js）
 *   · 北京/成都/上海/广州/杭州 — 半手工模板 + 程序化扩展（每城 80-100 条）
 *   · 其余 15 城 — 全程序化生成（每城 60-80 条），基于城市菜系配置
 *
 * 数据格式与 xianFoodGenerator 完全对齐，确保管道无缝适配。
 */

import { getCityCuisineTags } from './cityCuisineConfig.js'
import { getFoodsBySpotName as _xianGetFoodsBySpotName } from './xianFoodGenerator.js'

// ═══════════════════════════════════════════════════════════
// 21 城市中心坐标
// ═══════════════════════════════════════════════════════════

const CITY_CENTERS = {
  北京: [116.397477, 39.903738],
  上海: [121.473667, 31.230525],
  广州: [113.264434, 23.129163],
  深圳: [114.057868, 22.543099],
  杭州: [120.15507, 30.274085],
  成都: [104.066541, 30.572269],
  西安: [108.93977, 34.341574],
  南京: [118.796877, 32.060255],
  武汉: [114.305539, 30.593099],
  长沙: [112.938823, 28.228208],
  重庆: [106.551557, 29.563009],
  厦门: [118.089425, 24.479833],
  青岛: [120.382642, 36.067082],
  苏州: [120.585316, 31.298886],
  桂林: [110.299621, 25.274215],
  丽江: [100.228975, 26.855571],
  大理: [100.267638, 25.60689],
  黄山: [118.315582, 29.71477],
  九寨沟: [104.246246, 33.111847],
  张家界: [110.479648, 29.117238],
  三亚: [109.511909, 18.252847],
}

// ═══════════════════════════════════════════════════════════
// 工具函数（与 xianFoodGenerator 对齐）
// ═══════════════════════════════════════════════════════════

function mulberry32(a) {
  return function () {
    a |= 0
    a = (a + 0x6d2b79f5) | 0
    let t = Math.imul(a ^ (a >>> 15), 1 | a)
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}

function haversineM(lng1, lat1, lng2, lat2) {
  const R = 6371000
  const toRad = (d) => (d * Math.PI) / 180
  const dLat = toRad(lat2 - lat1)
  const dLng = toRad(lng2 - lng1)
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLng / 2) ** 2
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
}

function hashStr(str) {
  let hash = 0
  for (let i = 0; i < str.length; i++) {
    const c = str.charCodeAt(i)
    hash = (hash << 5) - hash + c
    hash |= 0
  }
  return Math.abs(hash)
}

// ═══════════════════════════════════════════════════════════
// 餐厅名称模板库（按菜系大类）
// — 每个菜系有多组 {prefix, brand, specialty} 用于程序化拼接
// — 内置真实连锁品牌名提升仿真度
// ═══════════════════════════════════════════════════════════

const RESTAURANT_NAME_POOL = {
  // —— 京菜 / 北京 ——
  '京菜正餐': [
    { brand: '全聚德', suffix: ['烤鸭店', '和平门店', '前门店', '王府井店'] },
    { brand: '便宜坊', suffix: ['烤鸭店', '鲜鱼口店', '哈德门店'] },
    { brand: '大董', suffix: ['烤鸭店', '工体店', '南新仓店'] },
    { brand: '局气', suffix: ['北京菜', '五道口店', '西单店'] },
    { brand: '北平食府', suffix: ['', '国贸店', '三里屯店'] },
    { brand: '那家小馆', suffix: ['', '798店', '香山店'] },
    { brand: '四世同堂', suffix: ['北京菜', '西便门店'] },
    { brand: '大鸭梨', suffix: ['烤鸭店', '家常菜'] },
    { brand: '四季民福', suffix: ['烤鸭店', '故宫店', '前门店'] },
    { brand: '花家怡园', suffix: ['', '簋街店', '四合院店'] },
    { brand: '老北京炸酱面大王', suffix: ['', '崇文门店'] },
    { brand: '京味斋', suffix: ['', '牡丹园店', '望京店'] },
    { brand: '仿膳饭庄', suffix: ['', '北海公园店'] },
    { brand: '东来顺', suffix: ['涮羊肉', '王府井店', '前门店'] },
    { brand: '聚宝源', suffix: ['涮肉', '牛街总店'] },
  ],
  '烤鸭爆肚': [
    { brand: '全聚德', suffix: ['烤鸭', '精品烤鸭'] },
    { brand: '便宜坊', suffix: ['焖炉烤鸭'] },
    { brand: '金生隆', suffix: ['爆肚冯', '爆肚专卖'] },
    { brand: '爆肚张', suffix: ['', '后海店'] },
    { brand: '爆肚满', suffix: ['', '牛街店'] },
    { brand: '四季民福', suffix: ['烤鸭', '故宫观景'] },
  ],
  '京味小吃': [
    { brand: '护国寺小吃', suffix: ['', '总店', '地安门店'] },
    { brand: '姚记炒肝', suffix: ['', '鼓楼店'] },
    { brand: '海碗居', suffix: ['炸酱面', '甘家口店'] },
    { brand: '门框胡同', suffix: ['卤煮', '百年卤煮'] },
    { brand: '小肠陈', suffix: ['卤煮火烧', '南横街店'] },
    { brand: '庆丰包子铺', suffix: ['', '月坛店'] },
    { brand: '炒肝赵', suffix: ['', '沙子口店'] },
    { brand: '天兴居', suffix: ['炒肝', '鲜鱼口店'] },
    { brand: '锦芳小吃', suffix: ['', '磁器口店'] },
    { brand: '白魁老号', suffix: ['烧羊肉', '交道口店'] },
  ],
  '茶饮宫廷糕点': [
    { brand: '吴裕泰', suffix: ['茶庄', '前门店'] },
    { brand: '张一元', suffix: ['茶庄', '大栅栏店'] },
    { brand: '稻香村', suffix: ['糕点', '前门店', '灯市口店'] },
    { brand: '富华斋', suffix: ['饽饽铺', '宫廷糕点'] },
    { brand: '御食园', suffix: ['宫廷小吃', '特产'] },
    { brand: '文宇奶酪', suffix: ['', '南锣鼓巷店'] },
  ],
  '铜锅涮肉': [
    { brand: '东来顺', suffix: ['涮羊肉', '王府井店'] },
    { brand: '聚宝源', suffix: ['涮肉', '牛街总店'] },
    { brand: '南门涮肉', suffix: ['', '天坛店'] },
    { brand: '满恒记', suffix: ['涮羊肉', '平安里店'] },
    { brand: '天桥老金', suffix: ['涮肉', '留学路店'] },
    { brand: '日坛涮肉', suffix: ['', '日坛店'] },
    { brand: '宏源涮肉', suffix: ['', '南门店'] },
  ],
  '川湘鲁菜': [
    { brand: '峨嵋酒家', suffix: ['', '车公庄店'] },
    { brand: '川办餐厅', suffix: ['', '贡院头条店'] },
    { brand: '张妈妈', suffix: ['川菜馆', '交道口店'] },
    { brand: '眉州东坡', suffix: ['', '国贸店'] },
    { brand: '湘爱', suffix: ['', '三里屯店'] },
    { brand: '翠清酒家', suffix: ['湘菜', '翠微路店'] },
    { brand: '丰泽园', suffix: ['鲁菜', '珠市口店'] },
    { brand: '同和居', suffix: ['鲁菜', '三里河店'] },
  ],
  '私房菜官府菜': [
    { brand: '谭家菜', suffix: ['官府菜', '北京饭店'] },
    { brand: '厉家菜', suffix: ['宫廷菜', '德胜门店'] },
    { brand: '程府宴', suffix: ['国宴菜', '南长街店'] },
    { brand: '和木私厨', suffix: ['', '鼓楼店'] },
  ],

  // —— 川菜 / 成都 ——
  '川菜正餐': [
    { brand: '眉州东坡', suffix: ['酒楼', '宽窄巷子店'] },
    { brand: '陈麻婆', suffix: ['豆腐', '骡马市店', '春熙路店'] },
    { brand: '盘飧市', suffix: ['', '华兴街店'] },
    { brand: '银杏', suffix: ['川菜馆', '神仙树店'] },
    { brand: '红杏酒家', suffix: ['', '羊西线店'] },
    { brand: '大蓉和', suffix: ['川菜', '一品天下店'] },
    { brand: '老房子', suffix: ['川菜', '玉林店'] },
    { brand: '带江草堂', suffix: ['', '青羊宫店'] },
    { brand: '努力餐', suffix: ['川菜', '宽窄巷子店'] },
    { brand: '巴蜀风', suffix: ['川菜馆', '春熙路店'] },
  ],
  '串串钵钵鸡': [
    { brand: '冒椒火辣', suffix: ['串串', '奎星楼店'] },
    { brand: '马路边边', suffix: ['麻辣烫', '玉林店', '建设路店'] },
    { brand: '叶婆婆', suffix: ['钵钵鸡', '太古里店'] },
    { brand: '钢管厂五区', suffix: ['小郡肝串串', '总店'] },
    { brand: '康二姐', suffix: ['串串香', '中道街店'] },
    { brand: '袁记', suffix: ['串串香', '双林路店'] },
  ],
  '经典川味小吃': [
    { brand: '钟水饺', suffix: ['', '人民公园店'] },
    { brand: '龙抄手', suffix: ['', '春熙路总店'] },
    { brand: '赖汤圆', suffix: ['', '总府路店'] },
    { brand: '夫妻肺片', suffix: ['', '总府路店'] },
    { brand: '韩包子', suffix: ['', '建设路店'] },
    { brand: '张老二', suffix: ['凉粉', '文殊院店'] },
    { brand: '洞子口张', suffix: ['凉粉', '东城根店'] },
    { brand: '糖油果子', suffix: ['', '奎星楼街店'] },
  ],
  '川味火锅': [
    { brand: '小龙坎', suffix: ['老火锅', '春熙路店', '太古里店'] },
    { brand: '大龙燚', suffix: ['火锅', '玉林店'] },
    { brand: '蜀九香', suffix: ['火锅', '彩虹桥店'] },
    { brand: '巴奴', suffix: ['毛肚火锅', 'IFS店'] },
    { brand: '谭鸭血', suffix: ['老火锅', '太古里店'] },
    { brand: '月满大江', suffix: ['火锅', '宽窄巷子店'] },
    { brand: '川西坝子', suffix: ['火锅', '杜甫草堂店'] },
    { brand: '电台巷', suffix: ['火锅', '科华路店'] },
    { brand: '皇城老妈', suffix: ['火锅', '琴台路店'] },
  ],
  '乐山烧烤': [
    { brand: '乐山刘记', suffix: ['烧烤', '玉林店'] },
    { brand: '醉西昌', suffix: ['火盆烧烤', '簇桥店'] },
    { brand: '江哥', suffix: ['烧烤', '贝森路店'] },
    { brand: '烤匠', suffix: ['烤鱼', 'IFS店', '群光店'] },
    { brand: '何师', suffix: ['烧烤', '科华路店'] },
    { brand: '王大爷', suffix: ['烧烤', '玉林店'] },
  ],

  // —— 上海 ——
  '本帮江浙菜': [
    { brand: '老正兴', suffix: ['菜馆', '福州路店'] },
    { brand: '上海老饭店', suffix: ['', '豫园店'] },
    { brand: '绿波廊', suffix: ['', '豫园店'] },
    { brand: '德兴馆', suffix: ['', '广东路店'] },
    { brand: '人和馆', suffix: ['本帮菜', '肇嘉浜路店'] },
    { brand: '兰亭', suffix: ['餐厅', '新天地店'] },
    { brand: '南麓浙里', suffix: ['杭帮菜', '巨鹿路店'] },
    { brand: '新荣记', suffix: ['台州菜', '外滩店'] },
    { brand: '雍颐庭', suffix: ['江南菜', '陆家嘴店'] },
  ],
  '海派西餐': [
    { brand: '红房子', suffix: ['西菜馆', '淮海路店'] },
    { brand: '德大', suffix: ['西餐社', '南京东路店'] },
    { brand: '凯司令', suffix: ['西餐', '南京西路店'] },
    { brand: 'Jean Georges', suffix: ['法餐', '外滩三号'] },
  ],
  '生煎汤包小吃': [
    { brand: '小杨生煎', suffix: ['', '南京东路店', '吴江路店'] },
    { brand: '大壶春', suffix: ['生煎', '云南南路店'] },
    { brand: '南翔馒头店', suffix: ['小笼包', '豫园店'] },
    { brand: '佳家汤包', suffix: ['', '黄河路店'] },
    { brand: '富春小笼', suffix: ['', '愚园路店'] },
    { brand: '万寿斋', suffix: ['', '山阴路店'] },
    { brand: '阿大葱油饼', suffix: ['', '瑞金二路店'] },
  ],
  '咖啡下午茶': [
    { brand: '%Arabica', suffix: ['咖啡', '武康路店'] },
    { brand: 'M Stand', suffix: ['咖啡', '新天地店'] },
    { brand: 'Seesaw', suffix: ['咖啡', '愚园路店'] },
    { brand: 'Manner', suffix: ['咖啡', '南阳路店'] },
    { brand: '星巴克臻选', suffix: ['烘焙工坊', '太古汇店'] },
  ],

  // —— 广州 ——
  '粤菜正餐': [
    { brand: '广州酒家', suffix: ['', '文昌路总店', '体育东店'] },
    { brand: '陶陶居', suffix: ['酒家', '第十甫路总店', '正佳广场店'] },
    { brand: '莲香楼', suffix: ['', '第十甫路店'] },
    { brand: '炳胜', suffix: ['品味', '珠江新城店', '海印总店'] },
    { brand: '惠食佳', suffix: ['啫啫煲', '滨江路店'] },
    { brand: '北园酒家', suffix: ['', '小北路店'] },
    { brand: '南园酒家', suffix: ['', '前进路店'] },
    { brand: '泮溪酒家', suffix: ['', '荔湾湖公园店'] },
  ],
  '早茶点心': [
    { brand: '点都德', suffix: ['茶楼', '花城汇店', '北京路店'] },
    { brand: '泮溪酒家', suffix: ['早茶', '荔湾湖公园店'] },
    { brand: '陶陶居', suffix: ['早茶', '第十甫路店'] },
    { brand: '禄运茶居', suffix: ['', '体育西店'] },
    { brand: '虾饺妹', suffix: ['', '天河店'] },
  ],
  '甜品糖水': [
    { brand: '南信', suffix: ['双皮奶', '第十甫路店'] },
    { brand: '百花', suffix: ['甜品', '文明路店'] },
    { brand: '玫瑰', suffix: ['甜品', '文明路店'] },
    { brand: '顺记', suffix: ['冰室', '宝华路店'] },
    { brand: '芬芳', suffix: ['甜品', '同福路店'] },
  ],

  // —— 杭州 ——
  '杭帮菜正餐': [
    { brand: '楼外楼', suffix: ['', '孤山路店'] },
    { brand: '山外山', suffix: ['菜馆', '玉泉路店'] },
    { brand: '天外天', suffix: ['菜馆', '灵隐路店'] },
    { brand: '外婆家', suffix: ['', '湖滨店', '西溪店'] },
    { brand: '绿茶', suffix: ['餐厅', '龙井路店', '湖滨店'] },
    { brand: '新白鹿', suffix: ['餐厅', '武林路店'] },
    { brand: '杭州酒家', suffix: ['', '延安路店'] },
    { brand: '奎元馆', suffix: ['', '解放路店'] },
    { brand: '张生记', suffix: ['', '双菱路店'] },
    { brand: '知味观', suffix: ['味庄', '杨公堤店', '湖滨总店'] },
  ],
  '龙井茶甜品': [
    { brand: '湖畔居', suffix: ['茶楼', '西湖天地店'] },
    { brand: '青藤', suffix: ['茶馆', '南山路店'] },
    { brand: '茶人村', suffix: ['', '龙井路店'] },
    { brand: '满陇桂雨', suffix: ['茶楼', '满觉陇路店'] },
  ],
  '金牌小吃': [
    { brand: '知味观', suffix: ['小吃', '湖滨总店'] },
    { brand: '新丰小吃', suffix: ['', '解放路店'] },
    { brand: '定胜糕', suffix: ['', '河坊街店'] },
    { brand: '葱包烩', suffix: ['', '河坊街店'] },
    { brand: '吴山烤禽', suffix: ['', '吴山广场店'] },
  ],
}

// ═══════════════════════════════════════════════════════════
// 通用菜系 → 名称模板后备映射
// 当某城市的菜系标签在 RESTAURANT_NAME_POOL 中没有匹配时使用
// ═══════════════════════════════════════════════════════════

const FALLBACK_NAME_PATTERNS = {
  _default: [
    { prefix: '老', suffix: '菜馆' },
    { prefix: '', suffix: '食府' },
    { prefix: '', suffix: '风味餐厅' },
    { prefix: '', suffix: '美食轩' },
  ],
}

// ═══════════════════════════════════════════════════════════
// 地址模板（按城市）
// ═══════════════════════════════════════════════════════════

const CITY_ADDRESS_PREFIX = {
  北京: '北京市',
  上海: '上海市',
  广州: '广州市',
  深圳: '深圳市',
  杭州: '杭州市',
  成都: '成都市',
  南京: '南京市',
  武汉: '武汉市',
  长沙: '长沙市',
  重庆: '重庆市',
  厦门: '厦门市',
  青岛: '青岛市',
  苏州: '苏州市',
  桂林: '桂林市',
  丽江: '丽江市',
  大理: '大理市',
  黄山: '黄山市',
  九寨沟: '九寨沟县',
  张家界: '张家界市',
  三亚: '三亚市',
}

const CITY_STREETS = {
  北京: ['王府井大街', '前门大街', '簋街', '南锣鼓巷', '三里屯太古里', '国贸商城', '西单大悦城', '朝阳大悦城', '五道口', '望京SOHO', '崇文门', '东直门', '鼓楼东大街'],
  上海: ['南京东路', '淮海中路', '云南南路', '吴江路', '黄河路', '愚园路', '武康路', '新天地', '陆家嘴正大广场', '豫园商城', '外滩', '静安寺', '徐家汇'],
  广州: ['上下九步行街', '北京路', '体育西路', '珠江新城', '江南西路', '文明路', '宝华路', '第十甫路', '同福路', '天河路', '花城汇', '琶洲'],
  深圳: ['东门步行街', '华强北', '海岸城', '万象天地', '欢乐海岸', '福田COCO Park', '南山科技园', '蛇口海上世界', '龙岗万科广场', '宝安壹方城'],
  杭州: ['湖滨银泰', '武林路', '河坊街', '南宋御街', '南山路', '龙井路', '满觉陇路', '西溪天堂', '拱宸桥运河', '钱江新城万象城'],
  成都: ['春熙路', '太古里', '宽窄巷子', '锦里', '玉林路', '建设路', '奎星楼街', '九眼桥', '万象城', '大悦城', '银泰城', '铁像寺水街'],
  南京: ['夫子庙', '老门东', '新街口', '湖南路', '狮子桥', '科巷', '明瓦廊', '三山街', '南京南站商圈', '百家湖'],
  武汉: ['江汉路', '户部巷', '吉庆街', '楚河汉街', '光谷步行街', '万松园', '粮道街', '武商广场', '江汉关', '东湖'],
  长沙: ['坡子街', '太平街', '黄兴南路', '五一广场', '解放西路', '文和友', '万家丽', '步步高梅溪湖', '冬瓜山'],
  重庆: ['解放碑', '洪崖洞', '观音桥', '磁器口', '南滨路', '较场口', '九街', '长江索道南站', '来福士广场'],
  厦门: ['中山路', '曾厝垵', '沙坡尾', '鼓浪屿龙头路', 'SM城市广场', '万象城', '宝龙一城', '思明南路'],
  青岛: ['台东步行街', '中山路', '劈柴院', '登州路啤酒街', '万象城', '奥帆中心', '崂山沙子口', '麦岛路'],
  苏州: ['观前街', '平江路', '山塘街', '李公堤', '圆融时代广场', '苏州中心', '木渎古镇', '斜塘老街'],
  桂林: ['正阳步行街', '十字街', '东西巷', '阳朔西街', '滨江路', '临桂万达', '七星万达'],
  丽江: ['四方街', '五一街', '七一街', '束河古镇', '忠义市场', '花马街', '雪山艺术小镇'],
  大理: ['人民路', '复兴路', '洋人街', '古城南门', '双廊古镇', '喜洲古镇', '下关泰业城'],
  黄山: ['屯溪老街', '黎阳in巷', '汤口镇', '黄山风景区南门', '徽州古城', '西递宏村'],
  九寨沟: ['九寨沟景区入口', '漳扎镇', '九寨大道', '沟口', '九寨宋城', '天堂口'],
  张家界: ['武陵源', '张家界国家森林公园入口', '溪布街', '天门山索道站', '大庸路', '步步高广场'],
  三亚: ['第一市场', '大东海', '海棠湾', '亚龙湾', '三亚湾椰梦长廊', '解放路步行街', '海昌不夜城'],
}

// ═══════════════════════════════════════════════════════════
// 价格区间池
// ═══════════════════════════════════════════════════════════

const PRICE_RANGES = ['¥', '¥¥', '¥¥¥', '¥¥¥¥', '¥¥¥¥¥']

// ═══════════════════════════════════════════════════════════
// 标签池（按菜系类型映射通用标签）
// ═══════════════════════════════════════════════════════════

const CUISINE_TAG_POOL = {
  _hotpot: ['火锅', '麻辣', '聚餐', '涮菜'],
  _bbq: ['烧烤', '宵夜', '大串', '烤串'],
  _dessert: ['甜品', '茶饮', '网红', '打卡'],
  _snack: ['小吃', '老字号', '地道', '性价比'],
  _private: ['私房', '需预约', '雅致', '小众'],
  _seafood: ['海鲜', '现捞', '生猛', '鲜活'],
  _noodles: ['面食', '手工', '筋道', '碳水'],
}

function pickTagsForCuisine(cuisine, seed) {
  const rng = mulberry32(seed)
  const allKeys = Object.keys(CUISINE_TAG_POOL)
  const lower = cuisine.toLowerCase()

  // 根据菜系名匹配关键词
  const matched = []
  if (lower.includes('火锅') || lower.includes('涮')) matched.push('_hotpot')
  if (lower.includes('烧烤') || lower.includes('烤')) matched.push('_bbq')
  if (lower.includes('甜品') || lower.includes('茶饮') || lower.includes('咖啡') || lower.includes('糕点') || lower.includes('糖水')) matched.push('_dessert')
  if (lower.includes('小吃') || lower.includes('面') || lower.includes('粉') || lower.includes('包')) matched.push('_snack')
  if (lower.includes('私房') || lower.includes('官府')) matched.push('_private')
  if (lower.includes('海鲜') || lower.includes('河鲜') || lower.includes('排挡')) matched.push('_seafood')

  // 从匹配的池中抽取标签
  const tags = []
  const used = new Set()
  for (const key of matched) {
    const pool = CUISINE_TAG_POOL[key]
    if (pool) {
      const idx = Math.floor(rng() * pool.length)
      if (!used.has(pool[idx])) {
        tags.push(pool[idx])
        used.add(pool[idx])
      }
    }
  }

  // 如果匹配不足，从通用池补充
  if (tags.length < 3) {
    const generic = ['人气', '口碑', '正宗', '特色', '必吃', '推荐', '地标美食']
    while (tags.length < 3) {
      const idx = Math.floor(rng() * generic.length)
      if (!used.has(generic[idx])) {
        tags.push(generic[idx])
        used.add(generic[idx])
      }
    }
  }

  return tags.slice(0, 4)
}

// ═══════════════════════════════════════════════════════════
// 核心生成：为指定城市生成美食数据
// ═══════════════════════════════════════════════════════════

let _multiCityCache = {}

/**
 * 为指定城市生成美食数据
 *
 * @param {string} cityName - 城市名称
 * @param {number} perCuisineMin - 每种菜系最少生成数量（默认 10）
 * @returns {Array} 美食列表
 */
export function generateCityFoodData(cityName, perCuisineMin = 10) {
  const cityKey = cityName?.trim() || ''
  if (!cityKey) return []

  // 命中缓存
  if (_multiCityCache[cityKey]) return _multiCityCache[cityKey]

  const center = CITY_CENTERS[cityKey]
  if (!center) return []

  const cuisineTags = getCityCuisineTags(cityKey).filter((t) => t !== '全部')
  const streets = CITY_STREETS[cityKey] || ['市中心', '商业街', '美食街']
  const addrPrefix = CITY_ADDRESS_PREFIX[cityKey] || `${cityKey}市`

  const allFoods = []
  let globalId = 0

  for (const cuisine of cuisineTags) {
    // 查找该菜系对应的名称模板
    const templates = RESTAURANT_NAME_POOL[cuisine] || _buildFallbackTemplates(cuisine, cityKey)

    // 每个模板生成 1 条（含接近和远离景点的坐标变化）
    const count = Math.max(perCuisineMin, templates.length)
    const expandFactor = Math.ceil(count / Math.max(1, templates.length))

    for (let ti = 0; ti < templates.length; ti++) {
      const tpl = templates[ti]
      const brand = tpl.brand || tpl.prefix || ''
      const suffixList = tpl.suffix || ['']

      for (let si = 0; si < Math.min(suffixList.length, expandFactor + 1); si++) {
        const seedBase = hashStr(`${cityKey}_${cuisine}_${ti}_${si}_${brand}`)

        // 名称：品牌 + 后缀
        const suffix = suffixList[si] || suffixList[0] || ''
        const name = suffix ? `${brand}${suffix}` : brand

        // 坐标：在城市中心周围随机偏移
        const rng = mulberry32(seedBase + 100)
        const angle = rng() * 2 * Math.PI
        const radius = 100 + rng() * 4000 // 100m - 4000m
        const latPerM = 1 / 111320
        const lngPerM = 1 / (111320 * Math.cos((center[1] * Math.PI) / 180))
        const lng = center[0] + radius * Math.cos(angle) * lngPerM
        const lat = center[1] + radius * Math.sin(angle) * latPerM

        // 距离（距城市中心）
        const distance = Math.round(radius)

        // 评分：3.5 - 5.0
        const ratingRng = mulberry32(seedBase + 200)
        const rating = Math.round((3.5 + ratingRng() * 1.5) * 10) / 10

        // 热度：200 - 9500
        const popRng = mulberry32(seedBase + 300)
        const popularity = Math.round(200 + popRng() * 9300)

        // 价格
        const priceRng = mulberry32(seedBase + 400)
        const priceRange = PRICE_RANGES[Math.floor(priceRng() * PRICE_RANGES.length)]

        // 标签
        const tags = pickTagsForCuisine(cuisine, seedBase + 500)

        // 地址
        const streetRng = mulberry32(seedBase + 600)
        const street = streets[Math.floor(streetRng() * streets.length)]
        const addrNum = Math.floor(rng() * 300) + 1
        const address = `${addrPrefix}${street}${addrNum}号`

        globalId++
        const id = `mcf_${hashStr(cityKey).toString(36)}_${String(globalId).padStart(4, '0')}`

        allFoods.push({
          id,
          name,
          type: cuisine,
          rating,
          popularity,
          distance,
          lnglat: [Math.round(lng * 1000000) / 1000000, Math.round(lat * 1000000) / 1000000],
          location_lng: Math.round(lng * 1000000) / 1000000,
          location_lat: Math.round(lat * 1000000) / 1000000,
          tags,
          price_range: priceRange,
          address,
          _city: cityKey,
          _cuisine: cuisine,
          cuisine_type: cuisine,
          distance_m: distance,
          heat_score: popularity,
        })

        // 控制每种菜系数量
        if (allFoods.filter((f) => f.type === cuisine).length >= perCuisineMin + 2) break
      }
      if (allFoods.filter((f) => f.type === cuisine).length >= perCuisineMin + 2) break
    }
  }

  _multiCityCache[cityKey] = allFoods
  return allFoods
}

/**
 * 为没有显式模板的菜系构建后备模板
 */
function _buildFallbackTemplates(cuisine, cityName) {
  const templates = []
  const prefixes = ['老', '大', '小', '好', '香', '金', '福', '龙', '御', '一品', '聚', '满', '真']
  const suffixes = ['菜馆', '食府', '餐厅', '馆', '人家', '小馆', '饭店', '酒楼', '美食', '厨房']

  for (let i = 0; i < 15; i++) {
    const seed = hashStr(`${cityName}_${cuisine}_${i}`)
    const rng = mulberry32(seed)
    const prefix = prefixes[Math.floor(rng() * prefixes.length)]
    const suffix = suffixes[Math.floor(rng() * (seed % 97) / 97 * suffixes.length)]
    const brand = rng() > 0.3 ? `${prefix}${cityName.slice(0, 2)}${suffix}` : `${cuisine.slice(0, 2)}${suffix}`
    templates.push({ brand, suffix: [''] })
  }

  return templates
}

/**
 * ★ 核心 API：根据城市和景点获取附近美食 ★
 *
 * 数据优先策略：
 *   1. 西安 → 使用 xianFoodGenerator 的丰富真实数据
 *   2. 其他城市 → 使用本文件的程序化生成数据
 *
 * 流程：
 *   获取全城数据 → 计算距景点的距离 → 过滤排序 → 返回
 *
 * @param {string}         cityName     - 城市名称
 * @param {string}         spotName     - 景点名称
 * @param {[number,number]} spotLocation - 景点经纬度 [lng, lat]
 * @returns {Array} 按距离排序后的该城市美食列表（含景点距离）
 */
export function getFoodsForCitySpot(cityName, spotName, spotLocation) {
  if (!cityName) return []

  // ★ 西安走原有生成器，保持数据最丰富 ★
  if (cityName.includes('西安') || cityName === '西安') {
    const foods = _xianGetFoodsBySpotName(spotName)
    if (foods && foods.length > 0) return foods
    // 兜底：也走程序化生成
  }

  // 获取全城数据
  const allCityFoods = generateCityFoodData(cityName)
  if (allCityFoods.length === 0) return []

  // 如果有景点坐标，重新计算距离并排序
  if (spotLocation && spotLocation.length === 2) {
    const [spotLng, spotLat] = spotLocation
    return allCityFoods
      .map((f) => {
        const [fLng, fLat] = f.lnglat || [f.location_lng, f.location_lat]
        const dist = haversineM(spotLng, spotLat, fLng, fLat)
        return {
          ...f,
          distance: Math.round(dist),
          distance_m: Math.round(dist),
        }
      })
      .sort((a, b) => a.distance - b.distance)
  }

  return allCityFoods
}

/**
 * 获取某城市的所有美食（无景点过滤）
 */
export function getAllFoodsForCity(cityName) {
  return generateCityFoodData(cityName)
}

/**
 * 获取某城市的所有菜系类型
 */
export function getCuisineTypesForCity(cityName) {
  return getCityCuisineTags(cityName).filter((t) => t !== '全部')
}

/**
 * 清除缓存（用于测试或数据重置）
 */
export function clearMultiCityCache() {
  _multiCityCache = {}
}

export default generateCityFoodData
