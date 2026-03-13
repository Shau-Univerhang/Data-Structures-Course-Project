"""
继续添加更多景点数据 - 最终版
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import SessionLocal, ScenicSpot

def add_final_spots():
    """继续添加更多小众景点"""
    db = SessionLocal()
    
    current_count = db.query(ScenicSpot).count()
    print(f"Current spots: {current_count}")
    
    # 更多城市和景点
    more_spots = [
        # 武汉
        {"name": "湖北省博物馆", "city": "武汉", "rating": 4.8, "heat_score": 8200, "lat": 30.5456, "lng": 114.3656, "category": "博物展览"},
        {"name": "东湖风景区", "city": "武汉", "rating": 4.7, "heat_score": 8000, "lat": 30.5656, "lng": 114.4156, "category": "风景名胜"},
        
        # 长沙
        {"name": "湖南省博物馆", "city": "长沙", "rating": 4.8, "heat_score": 8100, "lat": 28.2136, "lng": 112.9968, "category": "博物展览"},
        {"name": "太平街", "city": "长沙", "rating": 4.5, "heat_score": 7400, "lat": 28.2056, "lng": 112.9368, "category": "地标建筑"},
        
        # 厦门
        {"name": "曾厝垵", "city": "厦门", "rating": 4.5, "heat_score": 7800, "lat": 24.4356, "lng": 118.1268, "category": "地标建筑"},
        
        # 哈尔滨
        {"name": "索菲亚教堂", "city": "哈尔滨", "rating": 4.7, "heat_score": 8500, "lat": 45.7636, "lng": 126.6185, "category": "地标建筑"},
        
        # 拉萨
        {"name": "纳木措", "city": "拉萨", "rating": 4.9, "heat_score": 9200, "lat": 30.4176, "lng": 90.8816, "category": "风景名胜"},
        {"name": "羊卓雍措", "city": "拉萨", "rating": 4.9, "heat_score": 9100, "lat": 29.1176, "lng": 90.6516, "category": "风景名胜"},
        
        # 昆明
        {"name": "石林", "city": "昆明", "rating": 4.8, "heat_score": 8800, "lat": 24.8716, "lng": 103.2816, "category": "风景名胜"},
        {"name": "滇池", "city": "昆明", "rating": 4.6, "heat_score": 8000, "lat": 24.8516, "lng": 102.6516, "category": "风景名胜"},
        
        # 济南
        {"name": "趵突泉", "city": "济南", "rating": 4.7, "heat_score": 8200, "lat": 36.6516, "lng": 117.0116, "category": "风景名胜"},
        {"name": "大明湖", "city": "济南", "rating": 4.6, "heat_score": 7900, "lat": 36.6816, "lng": 117.0316, "category": "风景名胜"},
        
        # 洛阳
        {"name": "龙门石窟", "city": "洛阳", "rating": 4.9, "heat_score": 9200, "lat": 34.5516, "lng": 112.5316, "category": "历史古迹"},
        {"name": "白马寺", "city": "洛阳", "rating": 4.7, "heat_score": 8400, "lat": 34.7316, "lng": 112.5816, "category": "历史文化"},
        
        # 敦煌
        {"name": "莫高窟", "city": "敦煌", "rating": 4.9, "heat_score": 9500, "lat": 40.1416, "lng": 94.6616, "category": "历史古迹"},
        {"name": "鸣沙山月牙泉", "city": "敦煌", "rating": 4.8, "heat_score": 9100, "lat": 40.0816, "lng": 94.6116, "category": "风景名胜"},
        
        # 乌鲁木齐
        {"name": "天山天池", "city": "乌鲁木齐", "rating": 4.8, "heat_score": 8800, "lat": 43.8916, "lng": 88.1316, "category": "风景名胜"},
        
        # 丽江
        {"name": "丽江古城", "city": "丽江", "rating": 4.8, "heat_score": 9300, "lat": 26.8756, "lng": 100.2316, "category": "风景名胜"},
        {"name": "玉龙雪山", "city": "丽江", "rating": 4.9, "heat_score": 9400, "lat": 27.1156, "lng": 100.1516, "category": "风景名胜"},
        {"name": "泸沽湖", "city": "丽江", "rating": 4.8, "heat_score": 8700, "lat": 27.6916, "lng": 100.7516, "category": "风景名胜"},
        
        # 大理
        {"name": "大理古城", "city": "大理", "rating": 4.7, "heat_score": 8800, "lat": 25.5916, "lng": 100.2716, "category": "风景名胜"},
        {"name": "洱海", "city": "大理", "rating": 4.8, "heat_score": 9000, "lat": 25.6516, "lng": 100.2516, "category": "风景名胜"},
        
        # 西宁
        {"name": "青海湖", "city": "西宁", "rating": 4.9, "heat_score": 9300, "lat": 36.9516, "lng": 100.6316, "category": "风景名胜"},
        {"name": "塔尔寺", "city": "西宁", "rating": 4.8, "heat_score": 8900, "lat": 36.4916, "lng": 101.5816, "category": "历史文化"},
        
        # 沈阳
        {"name": "沈阳故宫", "city": "沈阳", "rating": 4.7, "heat_score": 8400, "lat": 41.7956, "lng": 123.4316, "category": "历史古迹"},
        
        # 大连
        {"name": "金石滩", "city": "大连", "rating": 4.6, "heat_score": 8000, "lat": 39.0716, "lng": 121.9316, "category": "风景名胜"},
        
        # 无锡
        {"name": "太湖鼋头渚", "city": "无锡", "rating": 4.7, "heat_score": 8300, "lat": 31.3216, "lng": 120.2216, "category": "风景名胜"},
        {"name": "灵山大佛", "city": "无锡", "rating": 4.8, "heat_score": 8600, "lat": 31.4216, "lng": 120.3516, "category": "历史文化"},
        
        # 扬州
        {"name": "瘦西湖", "city": "扬州", "rating": 4.7, "heat_score": 8200, "lat": 32.3916, "lng": 119.4216, "category": "风景名胜"},
        
        # 绍兴
        {"name": "鲁迅故里", "city": "绍兴", "rating": 4.6, "heat_score": 8000, "lat": 30.0016, "lng": 120.5816, "category": "历史文化"},
        
        # 嘉兴
        {"name": "乌镇", "city": "嘉兴", "rating": 4.7, "heat_score": 8700, "lat": 30.7416, "lng": 120.4916, "category": "风景名胜"},
        {"name": "西塘", "city": "嘉兴", "rating": 4.6, "heat_score": 8400, "lat": 30.9316, "lng": 120.8916, "category": "风景名胜"},
        
        # 九江
        {"name": "庐山", "city": "九江", "rating": 4.7, "heat_score": 8500, "lat": 29.4516, "lng": 115.9516, "category": "风景名胜"},
        
        # 珠海
        {"name": "长隆海洋王国", "city": "珠海", "rating": 4.7, "heat_score": 8700, "lat": 22.1216, "lng": 113.5516, "category": "休闲娱乐"},
        
        # 北海
        {"name": "涠洲岛", "city": "北海", "rating": 4.6, "heat_score": 8000, "lat": 21.0316, "lng": 109.1216, "category": "风景名胜"},
        
        # 柳州
        {"name": "程阳八寨", "city": "柳州", "rating": 4.5, "heat_score": 7200, "lat": 25.9316, "lng": 109.2516, "category": "风景名胜"},
        
        # 海口
        {"name": "假日海滩", "city": "海口", "rating": 4.4, "heat_score": 7100, "lat": 19.9516, "lng": 110.2816, "category": "风景名胜"},
        
        # 苏州
        {"name": "苏州博物馆", "city": "苏州", "rating": 4.7, "heat_score": 8200, "lat": 31.3216, "lng": 120.5816, "category": "博物展览"},
        
        # 佛山
        {"name": "祖庙", "city": "佛山", "rating": 4.6, "heat_score": 7800, "lat": 23.0216, "lng": 113.1216, "category": "历史文化"},
        
        # 宁波
        {"name": "天一阁", "city": "宁波", "rating": 4.6, "heat_score": 7600, "lat": 29.8616, "lng": 121.5516, "category": "历史文化"},
        
        # 温州
        {"name": "雁荡山", "city": "温州", "rating": 4.7, "heat_score": 8100, "lat": 28.3616, "lng": 121.0816, "category": "风景名胜"},
        
        # 泉州
        {"name": "开元寺", "city": "泉州", "rating": 4.6, "heat_score": 7700, "lat": 24.9116, "lng": 118.6716, "category": "历史文化"},
        
        # 芜湖
        {"name": "方特欢乐世界", "city": "芜湖", "rating": 4.5, "heat_score": 7800, "lat": 31.2216, "lng": 118.4316, "category": "休闲娱乐"},
        
        # 徐州
        {"name": "云龙湖", "city": "徐州", "rating": 4.5, "heat_score": 7200, "lat": 34.2116, "lng": 117.1216, "category": "风景名胜"},
        
        # 赣州
        {"name": "赣州古城墙", "city": "赣州", "rating": 4.5, "heat_score": 7400, "lat": 25.8516, "lng": 114.9316, "category": "历史古迹"},
        
        # 汕头
        {"name": "南澳岛", "city": "汕头", "rating": 4.5, "heat_score": 7300, "lat": 23.4116, "lng": 117.0316, "category": "风景名胜"},
        
        # 湖州
        {"name": "南浔古镇", "city": "湖州", "rating": 4.6, "heat_score": 7900, "lat": 30.8916, "lng": 120.4316, "category": "风景名胜"},
        
        # 镇江
        {"name": "金山寺", "city": "镇江", "rating": 4.6, "heat_score": 7700, "lat": 32.2016, "lng": 119.4516, "category": "历史文化"},
        
        # 泰州
        {"name": "溱湖湿地", "city": "泰州", "rating": 4.5, "heat_score": 7100, "lat": 32.5216, "lng": 120.1516, "category": "风景名胜"},
        
        # 常州
        {"name": "中华恐龙园", "city": "常州", "rating": 4.5, "heat_score": 8000, "lat": 31.8116, "lng": 119.9716, "category": "休闲娱乐"},
        
        # 潍坊
        {"name": "风筝博物馆", "city": "潍坊", "rating": 4.4, "heat_score": 6500, "lat": 36.7016, "lng": 119.1616, "category": "博物展览"},
        
        # 烟台
        {"name": "蓬莱阁", "city": "烟台", "rating": 4.6, "heat_score": 7800, "lat": 37.8016, "lng": 120.7516, "category": "风景名胜"},
        
        # 威海
        {"name": "刘公岛", "city": "威海", "rating": 4.5, "heat_score": 7400, "lat": 37.5016, "lng": 122.1816, "category": "风景名胜"},
        
        # 洛阳
        {"name": "关林", "city": "洛阳", "rating": 4.5, "heat_score": 7500, "lat": 34.4716, "lng": 112.4616, "category": "历史文化"},
        
        # 开封
        {"name": "龙亭公园", "city": "开封", "rating": 4.5, "heat_score": 7500, "lat": 34.7976, "lng": 114.3516, "category": "风景名胜"},
        
        # 西安
        {"name": "碑林", "city": "西安", "rating": 4.7, "heat_score": 8200, "lat": 34.2216, "lng": 108.9416, "category": "博物展览"},
        
        # 宝鸡
        {"name": "法门寺", "city": "宝鸡", "rating": 4.7, "heat_score": 8300, "lat": 34.5616, "lng": 107.9516, "category": "历史文化"},
        
        # 汉中
        {"name": "武侯祠", "city": "汉中", "rating": 4.5, "heat_score": 7200, "lat": 32.9816, "lng": 106.9516, "category": "历史文化"},
        
        # 延安
        {"name": "延安革命纪念馆", "city": "延安", "rating": 4.6, "heat_score": 7600, "lat": 36.5816, "lng": 109.4816, "category": "博物展览"},
        
        # 太原
        {"name": "晋祠", "city": "太原", "rating": 4.6, "heat_score": 7900, "lat": 37.7016, "lng": 112.4516, "category": "风景名胜"},
        
        # 平遥
        {"name": "平遥古城", "city": "平遥", "rating": 4.7, "heat_score": 8500, "lat": 37.2016, "lng": 112.1516, "category": "风景名胜"},
        
        # 大同
        {"name": "云冈石窟", "city": "大同", "rating": 4.8, "heat_score": 9000, "lat": 40.0516, "lng": 113.1316, "category": "历史古迹"},
        
        # 忻州
        {"name": "五台山", "city": "忻州", "rating": 4.7, "heat_score": 8600, "lat": 38.9816, "lng": 113.5816, "category": "风景名胜"},
        
        # 呼伦贝尔
        {"name": "呼伦贝尔大草原", "city": "呼伦贝尔", "rating": 4.8, "heat_score": 8900, "lat": 47.9816, "lng": 119.7516, "category": "风景名胜"},
        
        # 锡林郭勒
        {"name": "锡林郭勒草原", "city": "锡林郭勒", "rating": 4.7, "heat_score": 8400, "lat": 43.9316, "lng": 116.0516, "category": "风景名胜"},
        
        # 阿拉善
        {"name": "额济纳旗胡杨林", "city": "阿拉善", "rating": 4.8, "heat_score": 8700, "lat": 41.9516, "lng": 101.0516, "category": "风景名胜"},
    ]
    
    for spot_info in more_spots:
        exists = db.query(ScenicSpot).filter(
            ScenicSpot.name == spot_info['name']
        ).first()
        
        if not exists:
            spot = ScenicSpot(
                name=spot_info['name'],
                city=spot_info['city'],
                category=spot_info.get('category', '风景名胜'),
                rating=spot_info.get('rating', 4.5),
                heat_score=spot_info.get('heat_score', 5000),
                location_lat=spot_info.get('lat'),
                location_lng=spot_info.get('lng'),
                description=f"{spot_info['city']}的著名景点",
                tags=[],
                open_time="全天",
                ticket_price="参考实际"
            )
            db.add(spot)
    
    db.commit()
    new_count = db.query(ScenicSpot).count()
    print(f"Total spots now: {new_count}")
    db.close()


if __name__ == "__main__":
    add_final_spots()
