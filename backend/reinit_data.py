# -*- coding: utf-8 -*-
"""
重新插入正确的景点数据 - 解决编码问题
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import SessionLocal, ScenicSpot

# 确保输出UTF-8
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def add_spots():
    db = SessionLocal()
    
    # 清空旧数据
    db.query(ScenicSpot).delete()
    db.commit()
    
    # 景点数据 - 每个城市10个
    spots_data = [
        # 北京 (10个)
        {"name": "故宫博物院", "city": "北京", "rating": 4.9, "heat_score": 9850, "location_lat": 39.9163, "location_lng": 116.3972, "category": "历史古迹", "tags": ["必玩景点", "世界遗产"], "description": "世界上现存规模最大、保存最为完整的木质结构古建筑之一", "open_time": "08:30-17:00", "ticket_price": "60元", "images": ["https://images.unsplash.com/photo-1599571234909-29ed5d1321d6?w=800"]},
        {"name": "天坛公园", "city": "北京", "rating": 4.9, "heat_score": 9200, "location_lat": 39.9022, "location_lng": 116.4106, "category": "历史古迹", "tags": ["古建绝美", "历史文化"], "description": "明清两代帝王祭祀皇天、祈五谷丰登的场所", "open_time": "06:00-21:00", "ticket_price": "15元", "images": ["https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800"]},
        {"name": "颐和园", "city": "北京", "rating": 4.9, "heat_score": 9100, "location_lat": 39.9998, "location_lng": 116.6172, "category": "风景名胜", "tags": ["皇家园林", "湖光山色"], "description": "清代皇家园林，以昆明湖、万寿山为基址", "open_time": "06:30-18:00", "ticket_price": "30元", "images": ["https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800"]},
        {"name": "八达岭长城", "city": "北京", "rating": 4.8, "heat_score": 9800, "location_lat": 40.4319, "location_lng": 116.5704, "category": "历史古迹", "tags": ["必玩景点", "登高望远"], "description": "中国古代伟大的防御工程", "open_time": "06:30-19:00", "ticket_price": "40元", "images": ["https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800"]},
        {"name": "天安门广场", "city": "北京", "rating": 4.8, "heat_score": 9500, "location_lat": 39.9054, "location_lng": 116.3976, "category": "地标建筑", "tags": ["升旗仪式", "地标建筑"], "description": "世界上最大的城市广场之一", "open_time": "全天", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800"]},
        {"name": "圆明园", "city": "北京", "rating": 4.7, "heat_score": 8500, "location_lat": 40.0094, "location_lng": 116.3063, "category": "历史古迹", "tags": ["历史遗址", "园林景观"], "description": "清代著名皇家园林", "open_time": "07:00-21:00", "ticket_price": "10元", "images": ["https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800"]},
        {"name": "景山公园", "city": "北京", "rating": 4.8, "heat_score": 7800, "location_lat": 39.9213, "location_lng": 116.3970, "category": "风景名胜", "tags": ["登高望远", "citywalk"], "description": "可以俯瞰故宫全景", "open_time": "06:00-21:00", "ticket_price": "2元", "images": ["https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800"]},
        {"name": "北海公园", "city": "北京", "rating": 4.8, "heat_score": 8200, "location_lat": 39.9280, "location_lng": 116.3856, "category": "风景名胜", "tags": ["皇家园林", "湖光山色"], "description": "中国现存最古老的皇家园林之一", "open_time": "06:30-21:00", "ticket_price": "10元", "images": ["https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800"]},
        {"name": "恭王府", "city": "北京", "rating": 4.8, "heat_score": 8800, "location_lat": 39.9158, "location_lng": 116.3809, "category": "历史古迹", "tags": ["历史文化", "建筑宏伟"], "description": "清代规模最大的一座王府建筑群", "open_time": "08:00-17:00", "ticket_price": "40元", "images": ["https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800"]},
        {"name": "南锣鼓巷", "city": "北京", "rating": 4.6, "heat_score": 8600, "location_lat": 39.9326, "location_lng": 116.4098, "category": "地标建筑", "tags": ["市井烟火", "citywalk"], "description": "北京最古老的街区之一", "open_time": "全天", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800"]},
        
        # 上海 (10个)
        {"name": "外滩", "city": "上海", "rating": 4.9, "heat_score": 9700, "location_lat": 31.2456, "location_lng": 121.4901, "category": "地标建筑", "tags": ["夜景绝美", "citywalk"], "description": "上海最具代表性的景观", "open_time": "全天", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1474181487882-5abf3f0ba6c2?w=800"]},
        {"name": "东方明珠", "city": "上海", "rating": 4.7, "heat_score": 9300, "location_lat": 31.2401, "location_lng": 121.5019, "category": "地标建筑", "tags": ["登高望远", "夜景绝美"], "description": "上海标志性建筑之一", "open_time": "08:00-21:30", "ticket_price": "199元", "images": ["https://images.unsplash.com/photo-1474181487882-5abf3f0ba6c2?w=800"]},
        {"name": "豫园", "city": "上海", "rating": 4.8, "heat_score": 8600, "location_lat": 31.2256, "location_lng": 121.4806, "category": "风景名胜", "tags": ["江南园林", "古建绝美"], "description": "始建于明代的古典园林", "open_time": "08:30-17:00", "ticket_price": "40元", "images": ["https://images.unsplash.com/photo-1474181487882-5abf3f0ba6c2?w=800"]},
        {"name": "上海迪士尼乐园", "city": "上海", "rating": 4.8, "heat_score": 9500, "location_lat": 31.1430, "location_lng": 121.6600, "category": "休闲娱乐", "tags": ["亲子乐园", "必玩景点"], "description": "中国大陆第一个迪士尼主题乐园", "open_time": "08:30-20:30", "ticket_price": "475元", "images": ["https://images.unsplash.com/photo-1474181487882-5abf3f0ba6c2?w=800"]},
        {"name": "田子坊", "city": "上海", "rating": 4.6, "heat_score": 8100, "location_lat": 31.2056, "location_lng": 121.4606, "category": "地标建筑", "tags": ["文艺小资", "市井烟火"], "description": "最具代表性的石库门里弄文化", "open_time": "全天", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1474181487882-5abf3f0ba6c2?w=800"]},
        {"name": "静安寺", "city": "上海", "rating": 4.7, "heat_score": 7800, "location_lat": 31.2301, "location_lng": 121.4456, "category": "历史文化", "tags": ["宗教信仰", "古建"], "description": "上海最古老的佛寺", "open_time": "07:30-17:00", "ticket_price": "50元", "images": ["https://images.unsplash.com/photo-1474181487882-5abf3f0ba6c2?w=800"]},
        {"name": "南京路步行街", "city": "上海", "rating": 4.7, "heat_score": 8900, "location_lat": 31.2356, "location_lng": 121.4756, "category": "地标建筑", "tags": ["购物天堂", "citywalk"], "description": "中国最繁华的商业街之一", "open_time": "全天", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1474181487882-5abf3f0ba6c2?w=800"]},
        {"name": "武康路", "city": "上海", "rating": 4.7, "heat_score": 8200, "location_lat": 31.2086, "location_lng": 121.4356, "category": "地标建筑", "tags": ["历史文化", "拍照出片"], "description": "被誉为浓缩了上海近代百年历史的名人路", "open_time": "全天", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1474181487882-5abf3f0ba6c2?w=800"]},
        {"name": "上海博物馆", "city": "上海", "rating": 4.8, "heat_score": 7500, "location_lat": 31.2086, "location_lng": 121.4756, "category": "博物展览", "tags": ["历史文化", "艺术展览"], "description": "中国四大博物馆之一", "open_time": "09:00-17:00", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1474181487882-5abf3f0ba6c2?w=800"]},
        {"name": "召楼古镇", "city": "上海", "rating": 4.5, "heat_score": 6800, "location_lat": 31.0286, "location_lng": 121.5256, "category": "风景名胜", "tags": ["水乡古镇", "古镇风貌"], "description": "上海四大历史文化名镇之一", "open_time": "全天", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1474181487882-5abf3f0ba6c2?w=800"]},
        
        # 西安 (10个)
        {"name": "秦始皇兵马俑", "city": "西安", "rating": 4.9, "heat_score": 9900, "location_lat": 34.3843, "location_lng": 109.2785, "category": "历史古迹", "tags": ["必玩景点", "世界遗产"], "description": "世界第八大奇迹", "open_time": "08:30-18:00", "ticket_price": "120元", "images": ["https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800"]},
        {"name": "大雁塔", "city": "西安", "rating": 4.8, "heat_score": 9000, "location_lat": 34.2194, "location_lng": 108.9597, "category": "历史古迹", "tags": ["古建绝美", "地标建筑"], "description": "唐代著名的佛教建筑", "open_time": "08:00-18:30", "ticket_price": "50元", "images": ["https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800"]},
        {"name": "西安城墙", "city": "西安", "rating": 4.8, "heat_score": 8800, "location_lat": 34.2580, "location_lng": 108.9456, "category": "历史古迹", "tags": ["登高望远", "citywalk"], "description": "中国现存规模最大的古代城垣", "open_time": "08:00-22:00", "ticket_price": "54元", "images": ["https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800"]},
        {"name": "回民街", "city": "西安", "rating": 4.6, "heat_score": 8500, "location_lat": 34.2597, "location_lng": 108.9433, "category": "地标建筑", "tags": ["美食天堂", "市井烟火"], "description": "西安著名的美食文化街区", "open_time": "全天", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800"]},
        {"name": "华清宫", "city": "西安", "rating": 4.7, "heat_score": 8600, "location_lat": 34.4317, "location_lng": 109.2111, "category": "历史古迹", "tags": ["历史文化", "温泉体验"], "description": "唐代皇家温泉行宫", "open_time": "07:00-19:00", "ticket_price": "120元", "images": ["https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800"]},
        {"name": "大唐芙蓉园", "city": "西安", "rating": 4.6, "heat_score": 8100, "location_lat": 34.2156, "location_lng": 108.9656, "category": "风景名胜", "tags": ["主题公园", "夜景绝美"], "description": "以唐代文化为主题的大型主题公园", "open_time": "09:00-22:00", "ticket_price": "120元", "images": ["https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800"]},
        {"name": "陕西历史博物馆", "city": "西安", "rating": 4.8, "heat_score": 8400, "location_lat": 34.2194, "location_lng": 108.9597, "category": "博物展览", "tags": ["历史文化", "必玩景点"], "description": "中国第一座大型现代化国家级博物馆", "open_time": "08:30-18:00", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800"]},
        {"name": "永兴坊", "city": "西安", "rating": 4.5, "heat_score": 7900, "location_lat": 34.2597, "location_lng": 108.9533, "category": "地标建筑", "tags": ["美食天堂", "市井烟火"], "description": "西安新兴的网红美食街区", "open_time": "全天", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800"]},
        {"name": "小雁塔", "city": "西安", "rating": 4.7, "heat_score": 7600, "location_lat": 34.2194, "location_lng": 108.9297, "category": "历史古迹", "tags": ["古建", "历史文化"], "description": "唐代著名的佛教建筑", "open_time": "09:00-17:00", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800"]},
        {"name": "碑林博物馆", "city": "西安", "rating": 4.7, "heat_score": 7800, "location_lat": 34.2194, "location_lng": 108.9397, "category": "博物展览", "tags": ["历史文化", "书法艺术"], "description": "中国最大的碑刻艺术博物馆", "open_time": "08:00-17:30", "ticket_price": "65元", "images": ["https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800"]},
        
        # 成都 (10个)
        {"name": "大熊猫繁育研究基地", "city": "成都", "rating": 4.9, "heat_score": 9400, "location_lat": 30.7416, "location_lng": 104.1277, "category": "休闲娱乐", "tags": ["必玩景点", "亲子乐园"], "description": "全球最大的大熊猫繁育研究机构", "open_time": "07:30-18:00", "ticket_price": "55元", "images": ["https://images.unsplash.com/photo-1528109966604-5a6a4a964e8d?w=800"]},
        {"name": "宽窄巷子", "city": "成都", "rating": 4.7, "heat_score": 8700, "location_lat": 30.6686, "location_lng": 104.0556, "category": "地标建筑", "tags": ["市井烟火", "citywalk"], "description": "成都三大历史文化保护区之一", "open_time": "全天", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1528109966604-5a6a4a964e8d?w=800"]},
        {"name": "锦里古街", "city": "成都", "rating": 4.6, "heat_score": 8300, "location_lat": 30.6606, "location_lng": 104.0506, "category": "地标建筑", "tags": ["市井烟火", "逛吃逛喝"], "description": "成都知名的步行商业街", "open_time": "全天", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1528109966604-5a6a4a964e8d?w=800"]},
        {"name": "都江堰", "city": "成都", "rating": 4.9, "heat_score": 9100, "location_lat": 30.9919, "location_lng": 103.5773, "category": "历史古迹", "tags": ["世界遗产", "必玩景点"], "description": "世界文化遗产古代水利工程的奇迹", "open_time": "08:00-18:00", "ticket_price": "80元", "images": ["https://images.unsplash.com/photo-1528109966604-5a6a4a964e8d?w=800"]},
        {"name": "青城山", "city": "成都", "rating": 4.8, "heat_score": 8800, "location_lat": 30.8912, "location_lng": 103.5313, "category": "风景名胜", "tags": ["道教文化", "自然风光"], "description": "中国道教发源地之一", "open_time": "08:00-18:00", "ticket_price": "80元", "images": ["https://images.unsplash.com/photo-1528109966604-5a6a4a964e8d?w=800"]},
        {"name": "春熙路", "city": "成都", "rating": 4.6, "heat_score": 8500, "location_lat": 30.6656, "location_lng": 104.0656, "category": "地标建筑", "tags": ["购物天堂", "citywalk"], "description": "成都最繁华的商业街", "open_time": "全天", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1528109966604-5a6a4a964e8d?w=800"]},
        {"name": "武侯祠", "city": "成都", "rating": 4.7, "heat_score": 8200, "location_lat": 30.6516, "location_lng": 104.0456, "category": "历史文化", "tags": ["三国文化", "古建"], "description": "纪念诸葛亮为主的祠堂", "open_time": "08:00-20:00", "ticket_price": "50元", "images": ["https://images.unsplash.com/photo-1528109966604-5a6a4a964e8d?w=800"]},
        {"name": "杜甫草堂", "city": "成都", "rating": 4.7, "heat_score": 7800, "location_lat": 30.7516, "location_lng": 104.0056, "category": "历史文化", "tags": ["诗词文化", "园林"], "description": "杜甫流寓成都时的故居", "open_time": "08:00-18:00", "ticket_price": "50元", "images": ["https://images.unsplash.com/photo-1528109966604-5a6a4a964e8d?w=800"]},
        {"name": "金沙遗址博物馆", "city": "成都", "rating": 4.7, "heat_score": 7500, "location_lat": 30.7316, "location_lng": 104.0056, "category": "博物展览", "tags": ["历史文化", "古蜀文化"], "description": "展示古蜀文明的重要遗址", "open_time": "08:00-18:00", "ticket_price": "70元", "images": ["https://images.unsplash.com/photo-1528109966604-5a6a4a964e8d?w=800"]},
        {"name": "龙泉山城市森林公园", "city": "成都", "rating": 4.5, "heat_score": 6800, "location_lat": 30.5516, "location_lng": 104.3056, "category": "风景名胜", "tags": ["自然风光", "森林公园"], "description": "全球最大的城市森林公园", "open_time": "全天", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1528109966604-5a6a4a964e8d?w=800"]},
        
        # 杭州 (10个)
        {"name": "西湖", "city": "杭州", "rating": 4.9, "heat_score": 9900, "location_lat": 30.2467, "location_lng": 120.1481, "category": "风景名胜", "tags": ["必玩景点", "湖光山色"], "description": "中国著名的风景名胜区", "open_time": "全天", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800"]},
        {"name": "灵隐寺", "city": "杭州", "rating": 4.8, "heat_score": 9000, "location_lat": 30.2365, "location_lng": 120.0965, "category": "历史文化", "tags": ["佛教文化", "古建绝美"], "description": "江南著名古刹", "open_time": "07:00-18:00", "ticket_price": "75元", "images": ["https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800"]},
        {"name": "宋城", "city": "杭州", "rating": 4.6, "heat_score": 8200, "location_lat": 30.1836, "location_lng": 120.1656, "category": "休闲娱乐", "tags": ["主题公园", "演艺表演"], "description": "以宋代历史文化为主题的大型主题公园", "open_time": "09:00-21:00", "ticket_price": "300元", "images": ["https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800"]},
        {"name": "西溪湿地", "city": "杭州", "rating": 4.8, "heat_score": 8500, "location_lat": 30.0816, "location_lng": 120.0716, "category": "风景名胜", "tags": ["自然风光", "生态休闲"], "description": "国内第一个国家湿地公园", "open_time": "07:30-18:30", "ticket_price": "80元", "images": ["https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800"]},
        {"name": "雷峰塔", "city": "杭州", "rating": 4.6, "heat_score": 7800, "location_lat": 30.2366, "location_lng": 120.1481, "category": "地标建筑", "tags": ["地标建筑", "历史文化"], "description": "杭州的标志性建筑", "open_time": "08:00-17:30", "ticket_price": "40元", "images": ["https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800"]},
        {"name": "断桥残雪", "city": "杭州", "rating": 4.7, "heat_score": 8200, "location_lat": 30.2467, "location_lng": 120.1581, "category": "风景名胜", "tags": ["西湖十景", "浪漫爱情"], "description": "西湖最著名的景观之一", "open_time": "全天", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800"]},
        {"name": "苏堤春晓", "city": "杭州", "rating": 4.7, "heat_score": 8000, "location_lat": 30.2567, "location_lng": 120.1481, "category": "风景名胜", "tags": ["西湖十景", "园林"], "description": "西湖十景之首", "open_time": "全天", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800"]},
        {"name": "河坊街", "city": "杭州", "rating": 4.5, "heat_score": 7800, "location_lat": 30.2467, "location_lng": 120.1381, "category": "地标建筑", "tags": ["市井烟火", "美食天堂"], "description": "杭州历史文化街区", "open_time": "全天", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800"]},
        {"name": "岳王庙", "city": "杭州", "rating": 4.7, "heat_score": 7500, "location_lat": 30.2367, "location_lng": 120.1481, "category": "历史文化", "tags": ["民族英雄", "古建"], "description": "纪念岳飞的祠庙", "open_time": "07:30-17:00", "ticket_price": "25元", "images": ["https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800"]},
        {"name": "龙井村", "city": "杭州", "rating": 4.6, "heat_score": 7200, "location_lat": 30.2365, "location_lng": 120.0565, "category": "风景名胜", "tags": ["茶文化", "乡村游"], "description": "龙井茶的发源地", "open_time": "全天", "ticket_price": "免费", "images": ["https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800"]},
    ]
    
    # 添加数据
    for spot_data in spots_data:
        spot = ScenicSpot(**spot_data)
        db.add(spot)
    
    db.commit()
    
    # 验证
    count = db.query(ScenicSpot).count()
    print(f"Total spots: {count}")
    
    # 检查城市
    cities = db.query(ScenicSpot.city).distinct().all()
    for c in cities:
        city_name = c[0]
        city_count = db.query(ScenicSpot).filter(ScenicSpot.city == city_name).count()
        print(f"  {city_name}: {city_count}")
    
    db.close()

if __name__ == "__main__":
    add_spots()
