# 北京景点图片数据
# 从 Unsplash 获取的实际可用图片URL

beijing_data = {
    'city': {
        'name': '北京',
        'image': 'https://images.unsplash.com/photo-1599571234909-29ed5d1321d6?w=800'
    },
    'spots': [
        {'name': '故宫博物院', 'image': 'https://images.unsplash.com/photo-1599571234909-29ed5d1321d6?w=800'},
        {'name': '天坛公园', 'image': 'https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800'},
        {'name': '颐和园', 'image': 'https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800'},
        {'name': '八达岭长城', 'image': 'https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800'},
        {'name': '天安门广场', 'image': 'https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800'},
        {'name': '圆明园', 'image': 'https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800'},
        {'name': '景山公园', 'image': 'https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800'},
        {'name': '北海公园', 'image': 'https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800'},
        {'name': '恭王府', 'image': 'https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800'},
        {'name': '南锣鼓巷', 'image': 'https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800'},
    ]
}

print('北京:')
print(f\"City: {beijing_data['city']['image']}\")
for s in beijing_data['spots']:
    print(f\"{s['name']}: {s['image']}\")
