"""
修复景点标签问题
根据 SPOT_PREFERENCE_TAGS 为每个景点设置正确的标签
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import SessionLocal, ScenicSpot

# 景点偏好标签映射（从 spots.py 复制）
SPOT_PREFERENCE_TAGS = {
    # 北京
    '故宫博物院': ['must_visit', 'history', 'museum', 'photo'],
    '天坛公园': ['must_visit', 'history', 'scenery', 'photo'],
    '颐和园': ['must_visit', 'history', 'scenery', 'photo'],
    '八达岭长城': ['must_visit', 'history', 'scenery', 'photo'],
    '天安门广场': ['must_visit', 'landmark', 'history'],
    '圆明园': ['history', 'scenery', 'photo'],
    '景山公园': ['scenery', 'photo', 'citywalk'],
    '北海公园': ['scenery', 'leisure', 'citywalk'],
    '恭王府': ['history', 'heritage', 'photo'],
    '南锣鼓巷': ['food', 'citywalk', 'local_life'],
    '什刹海': ['scenery', 'food', 'citywalk', 'local_life'],
    '鸟巢': ['landmark', 'photo', 'must_visit'],
    '水立方': ['landmark', 'photo'],
    '北京大学': ['history', 'scenery', 'photo'],
    '清华大学': ['history', 'scenery', 'photo'],
    
    # 上海
    '外滩': ['must_visit', 'landmark', 'photo', 'citywalk'],
    '东方明珠': ['must_visit', 'landmark', 'photo'],
    '豫园': ['history', 'heritage', 'scenery', 'photo'],
    '上海迪士尼': ['must_visit', 'leisure', 'photo'],
    '田子坊': ['citywalk', 'photo', 'local_life'],
    '静安寺': ['history', 'heritage', 'photo'],
    '南京路步行街': ['landmark', 'food', 'citywalk'],
    '武康路': ['history', 'citywalk', 'photo'],
    '上海博物馆': ['museum', 'history', 'heritage'],
    '召楼古镇': ['history', 'heritage', 'citywalk'],
    '城隍庙': ['history', 'food', 'local_life'],
    '新天地': ['landmark', 'food', 'citywalk', 'leisure'],
    '上海中心大厦': ['landmark', 'photo'],
    '1933老场坊': ['photo', 'citywalk'],
    '复旦大学': ['history', 'scenery'],
    
    # 西安
    '兵马俑': ['must_visit', 'history', 'museum', 'heritage'],
    '华清宫': ['history', 'scenery', 'heritage'],
    '回民街': ['food', 'local_life', 'citywalk'],
    '大唐芙蓉园': ['history', 'scenery', 'photo', 'heritage'],
    '大雁塔': ['must_visit', 'history', 'landmark', 'photo'],
    '西安城墙': ['must_visit', 'history', 'landmark', 'citywalk'],
    '大唐不夜城': ['history', 'photo', 'citywalk', 'leisure'],
    '钟楼': ['must_visit', 'history', 'landmark', 'photo'],
    '鼓楼': ['history', 'landmark', 'photo'],
    '陕西历史博物馆': ['museum', 'history', 'heritage'],
    '小雁塔': ['history', 'heritage', 'photo'],
    '碑林博物馆': ['museum', 'history', 'heritage'],
    '西安交通大学': ['history', 'scenery'],
    
    # 成都
    '宽窄巷子': ['history', 'food', 'citywalk', 'local_life'],
    '春熙路': ['landmark', 'food', 'citywalk'],
    '熊猫基地': ['must_visit', 'leisure', 'photo'],
    '锦里古街': ['history', 'food', 'citywalk', 'local_life'],
    '武侯祠': ['history', 'heritage', 'museum'],
    '杜甫草堂': ['history', 'heritage', 'scenery'],
    '青城山': ['scenery', 'heritage', 'photo'],
    '都江堰': ['history', 'scenery', 'heritage'],
    '文殊院': ['history', 'heritage', 'scenery'],
    '人民公园': ['leisure', 'local_life', 'citywalk'],
    '九眼桥': ['photo', 'citywalk', 'leisure'],
    '四川大学': ['history', 'scenery'],
    '太古里': ['landmark', 'food', 'citywalk', 'leisure'],
    
    # 杭州
    '西湖': ['must_visit', 'scenery', 'photo', 'citywalk'],
    '灵隐寺': ['history', 'heritage', 'scenery'],
    '雷峰塔': ['history', 'landmark', 'photo'],
    '千岛湖': ['scenery', 'leisure', 'photo'],
    '宋城': ['history', 'heritage', 'leisure'],
    '西溪湿地': ['scenery', 'leisure', 'citywalk'],
    '河坊街': ['history', 'food', 'citywalk'],
    '断桥残雪': ['scenery', 'photo', 'must_visit'],
    '苏堤春晓': ['scenery', 'photo', 'citywalk'],
    '三潭印月': ['scenery', 'photo', 'must_visit'],
    '浙江大学': ['history', 'scenery'],
    '龙井村': ['scenery', 'food', 'local_life'],
    '钱塘江': ['scenery', 'landmark'],
    
    # 重庆
    '洪崖洞': ['must_visit', 'landmark', 'photo', 'night_view'],
    '磁器口': ['history', 'food', 'citywalk', 'local_life'],
    '解放碑': ['must_visit', 'landmark', 'citywalk'],
    '长江索道': ['landmark', 'photo', 'experience'],
    '武隆天坑': ['must_visit', 'scenery', 'photo'],
    '朝天门': ['landmark', 'scenery', 'photo'],
    '李子坝轻轨': ['landmark', 'photo', 'experience'],
    '鹅岭二厂': ['photo', 'citywalk', 'art'],
    '南山一棵树': ['scenery', 'photo', 'night_view'],
    '三峡博物馆': ['museum', 'history', 'heritage'],
    '白公馆': ['history', 'heritage'],
    '渣滓洞': ['history', 'heritage'],
    '重庆大学': ['history', 'scenery'],
    
    # 青岛
    '栈桥': ['must_visit', 'landmark', 'scenery', 'photo'],
    '八大关': ['history', 'scenery', 'photo', 'citywalk'],
    '崂山': ['must_visit', 'scenery', 'heritage', 'photo'],
    '五四广场': ['landmark', 'scenery', 'photo'],
    '青岛啤酒博物馆': ['museum', 'history', 'experience'],
    '金沙滩': ['scenery', 'leisure', 'photo'],
    '小鱼山': ['scenery', 'photo'],
    '信号山公园': ['scenery', 'photo'],
    '天主教堂': ['history', 'landmark', 'photo'],
    '奥帆中心': ['landmark', 'scenery', 'photo'],
    '德国总督府': ['history', 'heritage', 'museum'],
    '中国海洋大学': ['history', 'scenery'],
    '劈柴院': ['food', 'local_life', 'history'],
    
    # 广州
    '广州塔': ['must_visit', 'landmark', 'photo', 'night_view'],
    '沙面': ['history', 'heritage', 'photo', 'citywalk'],
    '陈家祠': ['history', 'heritage', 'museum'],
    '珠江夜游': ['scenery', 'night_view', 'experience'],
    '白云山': ['scenery', 'leisure', 'photo'],
    '越秀公园': ['scenery', 'leisure', 'history'],
    '北京路步行街': ['food', 'citywalk', 'shopping'],
    '上下九步行街': ['food', 'citywalk', 'local_life'],
    '长隆欢乐世界': ['leisure', 'must_visit', 'experience'],
    '中山纪念堂': ['history', 'landmark', 'heritage'],
    '石室圣心大教堂': ['history', 'landmark', 'photo'],
    '中山大学': ['history', 'scenery'],
    '华南理工大学': ['history', 'scenery'],
    
    # 苏州
    '拙政园': ['must_visit', 'history', 'scenery', 'heritage', 'photo'],
    '虎丘': ['history', 'scenery', 'heritage', 'photo'],
    '留园': ['history', 'scenery', 'heritage', 'photo'],
    '狮子林': ['history', 'scenery', 'heritage'],
    '苏州博物馆': ['museum', 'history', 'heritage', 'photo'],
    '平江路': ['history', 'citywalk', 'local_life'],
    '周庄古镇': ['history', 'scenery', 'heritage', 'citywalk'],
    '同里古镇': ['history', 'scenery', 'heritage', 'citywalk'],
    '金鸡湖': ['scenery', 'leisure', 'photo', 'night_view'],
    '寒山寺': ['history', 'heritage', 'scenery'],
    '山塘街': ['history', 'food', 'citywalk', 'night_view'],
    '苏州大学': ['history', 'scenery'],
    '观前街': ['food', 'citywalk', 'shopping'],
    
    # 厦门
    '鼓浪屿': ['must_visit', 'history', 'scenery', 'heritage', 'photo'],
    '厦门大学': ['history', 'scenery', 'photo'],
    '南普陀寺': ['history', 'heritage', 'scenery'],
    '曾厝垵': ['food', 'citywalk', 'local_life', 'photo'],
    '环岛路': ['scenery', 'photo', 'citywalk', 'cycling'],
    '中山路步行街': ['food', 'citywalk', 'shopping', 'history'],
    '胡里山炮台': ['history', 'heritage', 'museum'],
    '集美学村': ['history', 'scenery', 'heritage'],
    '园林植物园': ['scenery', 'leisure', 'photo'],
    '白城沙滩': ['scenery', 'leisure', 'photo'],
    '沙坡尾': ['art', 'photo', 'citywalk', 'local_life'],
    '厦门科技馆': ['museum', 'leisure', 'experience'],
    '五缘湾': ['scenery', 'leisure', 'photo'],
    
    # 南京
    '中山陵': ['must_visit', 'history', 'scenery', 'heritage'],
    '夫子庙': ['history', 'food', 'citywalk', 'night_view'],
    '秦淮河': ['history', 'scenery', 'night_view'],
    '明孝陵': ['history', 'heritage', 'scenery'],
    '总统府': ['history', 'heritage', 'museum'],
    '南京博物院': ['museum', 'history', 'heritage'],
    '玄武湖': ['scenery', 'leisure', 'citywalk'],
    '鸡鸣寺': ['history', 'heritage', 'scenery'],
    '侵华日军南京大屠杀遇难同胞纪念馆': ['museum', 'history', 'memorial'],
    '老门东': ['history', 'food', 'citywalk', 'local_life'],
    '新街口': ['landmark', 'shopping', 'citywalk'],
    '南京大学': ['history', 'scenery'],
    '东南大学': ['history', 'scenery'],
    
    # 武汉
    '黄鹤楼': ['must_visit', 'history', 'landmark', 'scenery', 'photo'],
    '东湖': ['scenery', 'leisure', 'citywalk', 'cycling'],
    '户部巷': ['food', 'local_life', 'citywalk'],
    '武汉大学': ['history', 'scenery', 'photo'],
    '湖北省博物馆': ['museum', 'history', 'heritage'],
    '江汉路步行街': ['food', 'citywalk', 'shopping', 'history'],
    '古琴台': ['history', 'heritage', 'scenery'],
    '晴川阁': ['history', 'heritage', 'scenery', 'photo'],
    '昙华林': ['art', 'citywalk', 'photo', 'local_life'],
    '汉口江滩': ['scenery', 'leisure', 'citywalk'],
    '武汉长江大桥': ['landmark', 'scenery', 'photo'],
    '归元寺': ['history', 'heritage', 'scenery'],
    '光谷步行街': ['shopping', 'citywalk', 'food'],
    
    # 长沙
    '岳麓山': ['scenery', 'history', 'heritage', 'photo'],
    '橘子洲': ['scenery', 'history', 'photo', 'citywalk'],
    '湖南省博物馆': ['museum', 'history', 'heritage'],
    '太平街': ['history', 'food', 'citywalk', 'local_life'],
    '天心阁': ['history', 'heritage', 'scenery'],
    '世界之窗': ['leisure', 'experience', 'photo'],
    '烈士公园': ['scenery', 'leisure', 'memorial'],
    '黄兴路步行街': ['food', 'shopping', 'citywalk'],
    '坡子街': ['food', 'local_life', 'citywalk'],
    '爱晚亭': ['scenery', 'history', 'heritage', 'photo'],
    '湖南大学': ['history', 'scenery'],
    '中南大学': ['history', 'scenery'],
    '超级文和友': ['food', 'photo', 'local_life', 'experience'],
    
    # 深圳
    '世界之窗': ['leisure', 'experience', 'photo', 'landmark'],
    '欢乐谷': ['leisure', 'experience', 'must_visit'],
    '东部华侨城': ['scenery', 'leisure', 'experience'],
    '大梅沙': ['scenery', 'leisure', 'photo'],
    '小梅沙': ['scenery', 'leisure', 'photo'],
    '深圳湾公园': ['scenery', 'leisure', 'citywalk', 'photo'],
    '莲花山公园': ['scenery', 'leisure', 'citywalk'],
    '梧桐山': ['scenery', 'leisure', 'photo', 'hiking'],
    '中英街': ['history', 'local_life', 'shopping'],
    '大鹏所城': ['history', 'heritage', 'scenery'],
    '较场尾': ['scenery', 'leisure', 'photo'],
    '深圳大学': ['history', 'scenery'],
    '华强北': ['shopping', 'technology', 'citywalk'],
    
    # 丽江
    '丽江古城': ['must_visit', 'history', 'heritage', 'citywalk', 'night_view'],
    '玉龙雪山': ['must_visit', 'scenery', 'photo', 'experience'],
    '束河古镇': ['history', 'heritage', 'citywalk', 'local_life'],
    '拉市海': ['scenery', 'leisure', 'experience'],
    '虎跳峡': ['scenery', 'photo', 'hiking', 'experience'],
    '木府': ['history', 'heritage', 'museum'],
    '黑龙潭公园': ['scenery', 'photo'],
    '狮子山': ['scenery', 'photo', 'citywalk'],
    '白沙古镇': ['history', 'heritage', 'art', 'local_life'],
    '泸沽湖': ['must_visit', 'scenery', 'photo', 'experience'],
    '蓝月谷': ['scenery', 'photo', 'must_visit'],
    '玉水寨': ['history', 'heritage', 'scenery'],
    '东巴谷': ['history', 'heritage', 'experience'],
    
    # 三亚
    '亚龙湾': ['must_visit', 'scenery', 'leisure', 'photo'],
    '天涯海角': ['must_visit', 'scenery', 'photo', 'landmark'],
    '南山寺': ['history', 'heritage', 'scenery'],
    '蜈支洲岛': ['scenery', 'leisure', 'photo', 'experience'],
    '大东海': ['scenery', 'leisure', 'photo'],
    '鹿回头': ['scenery', 'photo', 'night_view'],
    '三亚湾': ['scenery', 'leisure', 'photo', 'night_view'],
    '呀诺达雨林': ['scenery', 'experience', 'adventure'],
    '槟榔谷': ['history', 'heritage', 'experience'],
    '大小洞天': ['scenery', 'history', 'heritage'],
    '西岛': ['scenery', 'leisure', 'photo', 'experience'],
    '亚特兰蒂斯水世界': ['leisure', 'experience', 'must_visit'],
    '千古情': ['leisure', 'experience', 'show'],
    
    # 桂林
    '漓江': ['must_visit', 'scenery', 'photo', 'experience'],
    '象鼻山': ['must_visit', 'scenery', 'photo', 'landmark'],
    '阳朔西街': ['food', 'citywalk', 'night_view', 'local_life'],
    '龙脊梯田': ['must_visit', 'scenery', 'photo', 'experience'],
    '两江四湖': ['scenery', 'night_view', 'citywalk'],
    '银子岩': ['scenery', 'experience', 'photo'],
    '世外桃源': ['scenery', 'photo', 'experience'],
    '十里画廊': ['scenery', 'photo', 'cycling'],
    '遇龙河': ['scenery', 'photo', 'experience'],
    '兴坪古镇': ['history', 'heritage', 'citywalk'],
    '芦笛岩': ['scenery', 'experience', 'photo'],
    '桂林理工大学': ['history', 'scenery'],
    '东西巷': ['history', 'food', 'citywalk'],
    
    # 张家界
    '张家界国家森林公园': ['must_visit', 'scenery', 'photo', 'experience'],
    '天门山': ['must_visit', 'scenery', 'photo', 'experience'],
    '黄龙洞': ['scenery', 'experience', 'photo'],
    '宝峰湖': ['scenery', 'photo'],
    '大峡谷玻璃桥': ['experience', 'adventure', 'photo'],
    '袁家界': ['scenery', 'photo', 'must_visit'],
    '杨家界': ['scenery', 'photo'],
    '天子山': ['scenery', 'photo'],
    '十里画廊': ['scenery', 'photo', 'cycling'],
    '金鞭溪': ['scenery', 'photo', 'hiking'],
    '黄石寨': ['scenery', 'photo'],
    '百龙天梯': ['experience', 'photo', 'landmark'],
    '老屋场': ['scenery', 'photo'],
    
    # 黄山
    '黄山风景区': ['must_visit', 'scenery', 'photo', 'hiking'],
    '宏村': ['history', 'heritage', 'scenery', 'photo'],
    '西递': ['history', 'heritage', 'scenery'],
    '屯溪老街': ['history', 'food', 'citywalk', 'local_life'],
    '翡翠谷': ['scenery', 'photo'],
    '呈坎': ['history', 'heritage', 'scenery'],
    '唐模': ['history', 'heritage', 'scenery'],
    '潜口民宅': ['history', 'heritage', 'museum'],
    '棠樾牌坊群': ['history', 'heritage', 'photo'],
    '徽州古城': ['history', 'heritage', 'citywalk'],
    '齐云山': ['scenery', 'heritage', 'hiking'],
    '新安江山水画廊': ['scenery', 'photo', 'experience'],
    '黄山温泉': ['leisure', 'experience'],
    
    # 九寨沟
    '九寨沟': ['must_visit', 'scenery', 'photo', 'experience'],
    '五花海': ['scenery', 'photo', 'must_visit'],
    '诺日朗瀑布': ['scenery', 'photo'],
    '长海': ['scenery', 'photo'],
    '熊猫海': ['scenery', 'photo'],
    '镜海': ['scenery', 'photo'],
    '树正群海': ['scenery', 'photo'],
    '珍珠滩瀑布': ['scenery', 'photo'],
    '芦苇海': ['scenery', 'photo'],
    '火花海': ['scenery', 'photo'],
    '箭竹海': ['scenery', 'photo'],
    '原始森林': ['scenery', 'experience', 'hiking'],
    '则查洼沟': ['scenery', 'photo'],
    
    # 大理
    '大理古城': ['must_visit', 'history', 'heritage', 'citywalk'],
    '洱海': ['must_visit', 'scenery', 'photo', 'experience'],
    '苍山': ['scenery', 'photo', 'hiking'],
    '崇圣寺三塔': ['history', 'heritage', 'scenery', 'photo'],
    '双廊古镇': ['history', 'scenery', 'citywalk'],
    '喜洲古镇': ['history', 'heritage', 'citywalk'],
    '蝴蝶泉': ['scenery', 'history', 'photo'],
    '天龙八部影视城': ['history', 'experience', 'photo'],
    '南诏风情岛': ['scenery', 'history', 'experience'],
    '小普陀': ['scenery', 'history', 'photo'],
    '挖色镇': ['scenery', 'local_life'],
    '大理大学': ['history', 'scenery', 'photo'],
    '才村码头': ['scenery', 'photo'],
}

# 英文标签到中文标签的映射
TAG_NAME_MAP = {
    'must_visit': '必玩景点',
    'history': '历史文化',
    'landmark': '地标建筑',
    'heritage': '非遗体验',
    'scenery': '风景名胜',
    'food': '逛吃逛喝',
    'museum': '博物展览',
    'citywalk': 'citywalk',
    'photo': '拍照出片',
    'local_life': '市井烟火',
    'leisure': '休闲娱乐',
    'night_view': '夜景',
    'shopping': '购物',
    'experience': '体验',
    'adventure': '探险',
    'hiking': '徒步',
    'cycling': '骑行',
    'art': '艺术',
    'memorial': '纪念',
    'technology': '科技',
    'show': '演出',
}

# 根据景点名称智能推断标签
def infer_tags(spot_name):
    """根据景点名称推断标签"""
    tags = []
    
    # 关键词匹配
    if any(kw in spot_name for kw in ['大学', '学院']):
        tags.extend(['历史文化', '拍照出片'])
    if any(kw in spot_name for kw in ['博物馆', '纪念馆', '故居']):
        tags.extend(['博物展览', '历史文化'])
    if any(kw in spot_name for kw in ['古镇', '古城', '古街']):
        tags.extend(['历史古迹', 'citywalk'])
    if any(kw in spot_name for kw in ['公园', '湖', '山', '海', '江', '河']):
        tags.extend(['风景名胜', '拍照出片'])
    if any(kw in spot_name for kw in ['寺', '庙', '塔', '陵', '祠']):
        tags.extend(['历史文化', '非遗体验'])
    if any(kw in spot_name for kw in ['步行街', '街', '巷']):
        tags.extend(['逛吃逛喝', 'citywalk', '市井烟火'])
    if any(kw in spot_name for kw in ['欢乐世界', '乐园', '谷', '水世界']):
        tags.extend(['休闲娱乐', '体验'])
    if any(kw in spot_name for kw in ['长城', '故宫', '兵马俑', '西湖', '外滩', '洪崖洞', '黄山', '九寨沟', '张家界']):
        tags.append('必玩景点')
    
    return list(set(tags)) if tags else ['风景名胜']

def fix_spot_tags():
    """修复所有景点的标签"""
    db = SessionLocal()
    
    spots = db.query(ScenicSpot).all()
    total = len(spots)
    updated = 0
    
    print(f"Found {total} spots to fix")
    print("="*60)
    
    for spot in spots:
        # 获取英文标签
        en_tags = SPOT_PREFERENCE_TAGS.get(spot.name, [])
        
        if en_tags:
            # 转换为中文标签
            cn_tags = [TAG_NAME_MAP.get(tag, tag) for tag in en_tags[:3]]
        else:
            # 智能推断
            cn_tags = infer_tags(spot.name)[:3]
        
        # 更新标签
        spot.tags = cn_tags
        updated += 1
        
        if updated % 50 == 0:
            print(f"Progress: {updated}/{total}")
    
    db.commit()
    db.close()
    
    print("="*60)
    print(f"Updated {updated} spots successfully!")

def verify_tags():
    """验证标签更新结果"""
    db = SessionLocal()
    
    spots = db.query(ScenicSpot).all()
    
    print("\nVerification - Sample spots:")
    print("="*60)
    
    # 按城市分组显示
    cities = {}
    for spot in spots:
        if spot.city not in cities:
            cities[spot.city] = []
        cities[spot.city].append(spot)
    
    for city in sorted(cities.keys())[:5]:  # 只显示前5个城市
        print(f"\n{city}:")
        for spot in cities[city][:3]:  # 每个城市显示3个景点
            print(f"  - {spot.name}: {spot.tags}")
    
    # 统计标签分布
    all_tags = []
    for spot in spots:
        all_tags.extend(spot.tags or [])
    
    from collections import Counter
    tag_counts = Counter(all_tags)
    
    print("\n\nTag Distribution:")
    print("="*60)
    for tag, count in tag_counts.most_common(15):
        print(f"  {tag}: {count}")
    
    db.close()

if __name__ == "__main__":
    print("Fixing spot tags...")
    print("="*60)
    fix_spot_tags()
    verify_tags()
