"""
验证数据库中的景点名称是否能被City.vue的映射匹配
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import SessionLocal, ScenicSpot

# City.vue中的映射关键词
CITY_VUE_MAPPINGS = {
    # 北京
    '故宫': '/images/spots/beijing/beijing_gugong_bowuyuan.jpg',
    '天坛': '/images/spots/beijing/beijing_tiantan_gongyuan.jpg',
    '长城': '/images/spots/beijing/beijing_badaling_changcheng.jpg',
    '八达岭': '/images/spots/beijing/beijing_badaling_changcheng.jpg',
    '颐和园': '/images/spots/beijing/beijing_yiheyuan.jpg',
    '圆明园': '/images/spots/beijing/beijing_yuanmingyuan.jpg',
    '北海': '/images/spots/beijing/beijing_beihai_gongyuan.jpg',
    '恭王府': '/images/spots/beijing/beijing_gongwangfu.jpg',
    '景山': '/images/spots/beijing/beijing_jingshan_gongyuan.jpg',
    '南锣鼓巷': '/images/spots/beijing/beijing_nanluoguxiang.jpg',
    '天安门': '/images/spots/beijing/beijing_tiananmen_guangchang.jpg',
    '鸟巢': '/images/spots/beijing/beijing_niaochao.jpg',
    '水立方': '/images/spots/beijing/beijing_shuilifang.jpg',
    '什刹海': '/images/spots/beijing/beijing_shichahai.jpg',
    '北京大学': '/images/spots/beijing/beijing_beijing_daxue.jpg',
    '清华大学': '/images/spots/beijing/beijing_qinghua_daxue.jpg',
    # 上海
    '外滩': '/images/spots/shanghai/shanghai_waitan.jpg',
    '东方明珠': '/images/spots/shanghai/shanghai_dongfang_mingzhu.jpg',
    '豫园': '/images/spots/shanghai/shanghai_yuyuan.jpg',
    '田子坊': '/images/spots/shanghai/shanghai_tianzifang.jpg',
    '武康路': '/images/spots/shanghai/shanghai_wukanglu.jpg',
    '南京路': '/images/spots/shanghai/shanghai_nanjinglu_buxingjie.jpg',
    '静安寺': '/images/spots/shanghai/shanghai_jingansi.jpg',
    '召楼': '/images/spots/shanghai/shanghai_zhaolou_guzhen.jpg',
    '迪士尼': '/images/spots/shanghai/shanghai_shanghai_dishini.jpg',
    '博物馆': '/images/spots/shanghai/shanghai_shanghai_bowuguan.jpg',
    '城隍庙': '/images/spots/shanghai/shanghai_chenghuangmiao.jpg',
    '新天地': '/images/spots/shanghai/shanghai_xintiandi.jpg',
    '中心大厦': '/images/spots/shanghai/shanghai_shanghai_zhongxin.jpg',
    '1933': '/images/spots/shanghai/shanghai_1933_laochangfang.jpg',
    '复旦': '/images/spots/shanghai/shanghai_fudan_daxue.jpg',
    # 西安
    '兵马俑': '/images/spots/xian/xian_bingmayong.jpg',
    '大雁塔': '/images/spots/xian/xian_dayanta.jpg',
    '城墙': '/images/spots/xian/xian_xian_chengqiang.jpg',
    '华清': '/images/spots/xian/xian_huaqinggong.jpg',
    '大唐': '/images/spots/xian/xian_datang_furongyuan.jpg',
    '回民街': '/images/spots/xian/xian_huiminjie.jpg',
    '碑林': '/images/spots/xian/xian_beilin_bowuguan.jpg',
    '钟楼': '/images/spots/xian/xian_zhonglou.jpg',
    '鼓楼': '/images/spots/xian/xian_gulou.jpg',
    '小雁塔': '/images/spots/xian/xian_xiaoyanta.jpg',
    '历史博物馆': '/images/spots/xian/xian_shanxi_lishi_bowuguan.jpg',
    '不夜城': '/images/spots/xian/xian_datang_buyecheng.jpg',
    '交大': '/images/spots/xian/xian_xian_jiaotong_daxue.jpg',
    # 成都
    '宽窄巷子': '/images/spots/chengdu/chengdu_kuanzhai_xiangzi.jpg',
    '春熙路': '/images/spots/chengdu/chengdu_chunxilu.jpg',
    '熊猫': '/images/spots/chengdu/chengdu_xiongmao_jidi.jpg',
    '锦里': '/images/spots/chengdu/chengdu_jinli_gujie.jpg',
    '武侯祠': '/images/spots/chengdu/chengdu_wuhouci.jpg',
    '杜甫草堂': '/images/spots/chengdu/chengdu_dufu_caotang.jpg',
    '青城山': '/images/spots/chengdu/chengdu_qingchengshan.jpg',
    '都江堰': '/images/spots/chengdu/chengdu_dujiangyan.jpg',
    '文殊院': '/images/spots/chengdu/chengdu_wenshuyuan.jpg',
    '人民公园': '/images/spots/chengdu/chengdu_renmin_gongyuan.jpg',
    '九眼桥': '/images/spots/chengdu/chengdu_jiuyanqiao.jpg',
    '川大': '/images/spots/chengdu/chengdu_sichuan_daxue.jpg',
    '太古里': '/images/spots/chengdu/chengdu_taikuli.jpg',
    # 杭州
    '西湖': '/images/spots/hangzhou/hangzhou_xihu.jpg',
    '灵隐寺': '/images/spots/hangzhou/hangzhou_lingyinsi.jpg',
    '雷峰塔': '/images/spots/hangzhou/hangzhou_leifengta.jpg',
    '千岛湖': '/images/spots/hangzhou/hangzhou_qiandaohu.jpg',
    '宋城': '/images/spots/hangzhou/hangzhou_songcheng.jpg',
    '西溪': '/images/spots/hangzhou/hangzhou_xixi_shidi.jpg',
    '河坊街': '/images/spots/hangzhou/hangzhou_hefangjie.jpg',
    '断桥': '/images/spots/hangzhou/hangzhou_duanqiao_canxue.jpg',
    '苏堤': '/images/spots/hangzhou/hangzhou_sudi_chunxiao.jpg',
    '三潭印月': '/images/spots/hangzhou/hangzhou_santanyinyue.jpg',
    '浙大': '/images/spots/hangzhou/hangzhou_zhejiang_daxue.jpg',
    '龙井': '/images/spots/hangzhou/hangzhou_longjingcun.jpg',
    '钱塘江': '/images/spots/hangzhou/hangzhou_qiantangjiang.jpg',
    # 武汉
    '黄鹤楼': '/images/spots/wuhan/wuhan_huanghelou.jpg',
    '东湖': '/images/spots/wuhan/wuhan_donghu.jpg',
    '户部巷': '/images/spots/wuhan/wuhan_hubuxiang.jpg',
    '武汉大学': '/images/spots/wuhan/wuhan_wuhan_daxue.jpg',
    '湖北省博物馆': '/images/spots/wuhan/wuhan_hubei_bowuguan.jpg',
    '江汉路': '/images/spots/wuhan/wuhan_jianghanlu_buxingjie.jpg',
    '古琴台': '/images/spots/wuhan/wuhan_guqintai.jpg',
    '晴川阁': '/images/spots/wuhan/wuhan_qingchuange.jpg',
    '昙华林': '/images/spots/wuhan/wuhan_tanhualin.jpg',
    '汉口江滩': '/images/spots/wuhan/wuhan_hankou_jiangtan.jpg',
    '长江大桥': '/images/spots/wuhan/wuhan_wuhan_changjiang_daqiao.jpg',
    '归元寺': '/images/spots/wuhan/wuhan_guiyuansi.jpg',
    '光谷': '/images/spots/wuhan/wuhan_guanggu_buxingjie.jpg',
}

def get_spot_image(spot_name, city):
    """模拟City.vue的getSpotImage函数"""
    if not spot_name:
        return None
    
    # 1. 完全匹配
    if spot_name in CITY_VUE_MAPPINGS:
        return CITY_VUE_MAPPINGS[spot_name]
    
    # 2. 包含匹配
    for keyword, image_path in CITY_VUE_MAPPINGS.items():
        if keyword in spot_name or spot_name in keyword:
            return image_path
    
    return None

def verify_mappings():
    db = SessionLocal()
    
    # 获取所有城市
    cities = db.query(ScenicSpot.city).distinct().all()
    cities = [c[0] for c in cities if c[0]]
    
    print("验证景点名称映射:\n")
    
    for city in sorted(cities):
        spots = db.query(ScenicSpot).filter(ScenicSpot.city == city).all()
        print(f"\n{city} ({len(spots)}个景点):")
        
        unmatched = []
        for spot in spots:
            image = get_spot_image(spot.name, city)
            if image:
                print(f"  [OK] {spot.name} -> {image.split('/')[-1]}")
            else:
                print(f"  [MISSING] {spot.name}")
                unmatched.append(spot.name)
        
        if unmatched:
            print(f"  未匹配: {unmatched}")
    
    db.close()

if __name__ == "__main__":
    verify_mappings()
