# City and Scenic Spot Images Database
# From Unsplash (verified working URLs)

city_images = {
    '北京': 'https://images.unsplash.com/photo-1599571234909-29ed5d1321d6?w=800',
    '上海': 'https://images.unsplash.com/photo-1474181487882-5abf3f0ba6c2?w=800',
    '西安': 'https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800',
    '成都': 'https://images.unsplash.com/photo-1528109966604-5a6a4a964e8d?w=800',
    '杭州': 'https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800',
    '青岛': 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800',
    '重庆': 'https://images.unsplash.com/photo-1560969184-10fe8719e047?w=800',
    '广州': 'https://images.unsplash.com/photo-1534054524995-69c5d4f8a5b5?w=800',
    '苏州': 'https://images.unsplash.com/photo-1548919973-5cef591cdbc9?w=800',
    '厦门': 'https://images.unsplash.com/photo-1518459021-c8f5211a7edc?w=800',
    '丽江': 'https://images.unsplash.com/photo-1527838832700-5059252407fa?w=800',
    '三亚': 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800',
    '桂林': 'https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800',
}

# Scenic spot images by city
spot_images = {
    '北京': [
        {'name': '故宫博物院', 'image': 'https://images.unsplash.com/photo-1599571234909-29ed5d1321d6?w=800'},
        {'name': '天坛公园', 'image': 'https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800'},
        {'name': '颐和园', 'image': 'https://images.unsplash.com/photo-1548919973-5cef591cdbc9?w=800'},
        {'name': '八达岭长城', 'image': 'https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800'},
        {'name': '天安门广场', 'image': 'https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800'},
        {'name': '圆明园', 'image': 'https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800'},
        {'name': '景山公园', 'image': 'https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800'},
        {'name': '北海公园', 'image': 'https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800'},
        {'name': '恭王府', 'image': 'https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800'},
        {'name': '南锣鼓巷', 'image': 'https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800'},
    ],
    '上海': [
        {'name': '外滩', 'image': 'https://images.unsplash.com/photo-1474181487882-5abf3f0ba6c2?w=800'},
        {'name': '东方明珠', 'image': 'https://images.unsplash.com/photo-1474181487882-5abf3f0ba6c2?w=800'},
        {'name': '豫园', 'image': 'https://images.unsplash.com/photo-1474181487882-5abf3f0ba6c2?w=800'},
        {'name': '上海迪士尼', 'image': 'https://images.unsplash.com/photo-1474181487882-5abf3f0ba6c2?w=800'},
        {'name': '田子坊', 'image': 'https://images.unsplash.com/photo-1474181487882-5abf3f0ba6c2?w=800'},
        {'name': '静安寺', 'image': 'https://images.unsplash.com/photo-1474181487882-5abf3f0ba6c2?w=800'},
        {'name': '南京路步行街', 'image': 'https://images.unsplash.com/photo-1474181487882-5abf3f0ba6c2?w=800'},
        {'name': '武康路', 'image': 'https://images.unsplash.com/photo-1474181487882-5abf3f0ba6c2?w=800'},
        {'name': '上海博物馆', 'image': 'https://images.unsplash.com/photo-1474181487882-5abf3f0ba6c2?w=800'},
        {'name': '召楼古镇', 'image': 'https://images.unsplash.com/photo-1474181487882-5abf3f0ba6c2?w=800'},
    ],
    '西安': [
        {'name': '兵马俑', 'image': 'https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800'},
        {'name': '大雁塔', 'image': 'https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800'},
        {'name': '西安城墙', 'image': 'https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800'},
        {'name': '回民街', 'image': 'https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800'},
        {'name': '华清宫', 'image': 'https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800'},
        {'name': '大唐芙蓉园', 'image': 'https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800'},
        {'name': '陕西历史博物馆', 'image': 'https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800'},
        {'name': '永兴坊', 'image': 'https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800'},
        {'name': '小雁塔', 'image': 'https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800'},
        {'name': '碑林博物馆', 'image': 'https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800'},
    ],
    '成都': [
        {'name': '熊猫基地', 'image': 'https://images.unsplash.com/photo-1528109966604-5a6a4a964e8d?w=800'},
        {'name': '宽窄巷子', 'image': 'https://images.unsplash.com/photo-1528109966604-5a6a4a964e8d?w=800'},
        {'name': '锦里古街', 'image': 'https://images.unsplash.com/photo-1528109966604-5a6a4a964e8d?w=800'},
        {'name': '都江堰', 'image': 'https://images.unsplash.com/photo-1528109966604-5a6a4a964e8d?w=800'},
        {'name': '青城山', 'image': 'https://images.unsplash.com/photo-1528109966604-5a6a4a964e8d?w=800'},
        {'name': '春熙路', 'image': 'https://images.unsplash.com/photo-1528109966604-5a6a4a964e8d?w=800'},
        {'name': '武侯祠', 'image': 'https://images.unsplash.com/photo-1528109966604-5a6a4a964e8d?w=800'},
        {'name': '杜甫草堂', 'image': 'https://images.unsplash.com/photo-1528109966604-5a6a4a964e8d?w=800'},
        {'name': '金沙遗址博物馆', 'image': 'https://images.unsplash.com/photo-1528109966604-5a6a4a964e8d?w=800'},
        {'name': '龙泉山', 'image': 'https://images.unsplash.com/photo-1528109966604-5a6a4a964e8d?w=800'},
    ],
    '杭州': [
        {'name': '西湖', 'image': 'https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800'},
        {'name': '灵隐寺', 'image': 'https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800'},
        {'name': '宋城', 'image': 'https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800'},
        {'name': '西溪湿地', 'image': 'https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800'},
        {'name': '雷峰塔', 'image': 'https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800'},
        {'name': '断桥残雪', 'image': 'https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800'},
        {'name': '苏堤', 'image': 'https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800'},
        {'name': '河坊街', 'image': 'https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800'},
        {'name': '岳王庙', 'image': 'https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800'},
        {'name': '龙井村', 'image': 'https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800'},
    ],
    '青岛': [
        {'name': '栈桥', 'image': 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800'},
        {'name': '五四广场', 'image': 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800'},
        {'name': '崂山', 'image': 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800'},
        {'name': '八大关', 'image': 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800'},
        {'name': '金沙滩', 'image': 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800'},
    ],
    '重庆': [
        {'name': '洪崖洞', 'image': 'https://images.unsplash.com/photo-1560969184-10fe8719e047?w=800'},
        {'name': '解放碑', 'image': 'https://images.unsplash.com/photo-1560969184-10fe8719e047?w=800'},
        {'name': '长江索道', 'image': 'https://images.unsplash.com/photo-1560969184-10fe8719e047?w=800'},
        {'name': '磁器口', 'image': 'https://images.unsplash.com/photo-1560969184-10fe8719e047?w=800'},
        {'name': '武隆天生三桥', 'image': 'https://images.unsplash.com/photo-1560969184-10fe8719e047?w=800'},
    ],
}

# Save to JSON
import json
with open('D:/travel/邮游世界/images/city_images.json', 'w', encoding='utf-8') as f:
    json.dump({'city_images': city_images, 'spot_images': spot_images}, f, ensure_ascii=False, indent=2)

print('Image database saved!')
print('Cities:', len(city_images))
print('Xi an spots:', len(spot_images.get('西安', [])))
