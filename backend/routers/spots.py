"""
景点相关API
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import sys
import json
sys.path.append("..")

from models.database import get_db, ScenicSpot, Restaurant
from algorithms.core import top_k_spots, top_k_restaurants, fuzzy_search_spots


def parse_tags(tags_value):
    """解析tags字段，支持JSON字符串或列表"""
    if not tags_value:
        return []
    if isinstance(tags_value, list):
        return tags_value
    if isinstance(tags_value, str):
        try:
            return json.loads(tags_value)
        except json.JSONDecodeError:
            return []
    return []

router = APIRouter()

# 推荐算法权重配置
PREFERENCE_WEIGHT = 1000  # 偏好权重：每个匹配的偏好加1000分
FAVORITES_WEIGHT = 0.1  # 收藏权重：每个收藏加0.1分
RATING_WEIGHT = 10  # 评分权重：每分加10分

# 景点图片映射 - 包含所有277个景点
SPOT_IMAGES = {
    # ========== 北京 (15个) ==========
    '故宫博物院': ['/images/spots/beijing/beijing_gugong_bowuyuan.jpg'],
    '故宫': ['/images/spots/beijing/beijing_gugong_bowuyuan.jpg'],
    '天坛公园': ['/images/spots/beijing/beijing_tiantan_gongyuan.jpg'],
    '天坛': ['/images/spots/beijing/beijing_tiantan_gongyuan.jpg'],
    '长城-八达岭': ['/images/spots/beijing/beijing_badaling_changcheng.jpg'],
    '八达岭长城': ['/images/spots/beijing/beijing_badaling_changcheng.jpg'],
    '颐和园': ['/images/spots/beijing/beijing_yiheyuan.jpg'],
    '圆明园': ['/images/spots/beijing/beijing_yuanmingyuan.jpg'],
    '天安门广场': ['/images/spots/beijing/beijing_tiananmen_guangchang.jpg'],
    '天安门': ['/images/spots/beijing/beijing_tiananmen_guangchang.jpg'],
    '北海公园': ['/images/spots/beijing/beijing_beihai_gongyuan.jpg'],
    '恭王府': ['/images/spots/beijing/beijing_gongwangfu.jpg'],
    '景山公园': ['/images/spots/beijing/beijing_jingshan_gongyuan.jpg'],
    '南锣鼓巷': ['/images/spots/beijing/beijing_nanluoguxiang.jpg'],
    '北京大学': ['/images/spots/beijing/beijing_beijing_daxue.jpg'],
    '清华大学': ['/images/spots/beijing/beijing_qinghua_daxue.jpg'],
    '鸟巢': ['/images/spots/beijing/beijing_niaochao.jpg'],
    '水立方': ['/images/spots/beijing/beijing_shuilifang.jpg'],
    '什刹海': ['/images/spots/beijing/beijing_shichahai.jpg'],
    '王府井': ['/images/spots/beijing/beijing_wangfujin.jpg'],
    '奥林匹克公园': ['/images/spots/beijing/beijing_aolinpikegongyuan.jpg'],
    '雍和宫': ['/images/spots/beijing/beijing_yonghegong.jpg'],
    '明十三陵': ['/images/spots/beijing/beijing_mingshisanling.jpg'],
    '798艺术区': ['/images/spots/beijing/beijing_798yishuqu.jpg'],
    '三里屯': ['/images/spots/beijing/beijing_sanlitun.jpg'],
    '国贸': ['/images/spots/beijing/beijing_guomao.jpg'],
    '前门大街': ['/images/spots/beijing/beijing_qianmendajie.jpg'],
    '环球影城': ['/images/spots/beijing/beijing_huanqiuyingcheng.jpg'],
    '军事博物馆': ['/images/spots/beijing/beijing_junshibowuguan.jpg'],
    '国家博物馆': ['/images/spots/beijing/beijing_guojiabowuguan.jpg'],
    '人民大会堂': ['/images/spots/beijing/beijing_renmindahuitang.jpg'],
    '地坛公园': ['/images/spots/beijing/beijing_ditangongyuan.jpg'],
    '北京鼓楼': ['/images/spots/beijing/beijing_gulou.jpg'],
    '北京动物园': ['/images/spots/beijing/beijing_beijingdongwuyuan.jpg'],

    # ========== 上海 (15个) ==========
    '外滩': ['/images/spots/shanghai/shanghai_waitan.jpg'],
    '东方明珠': ['/images/spots/shanghai/shanghai_dongfang_mingzhu.jpg'],
    '豫园': ['/images/spots/shanghai/shanghai_yuyuan.jpg'],
    '田子坊': ['/images/spots/shanghai/shanghai_tianzifang.jpg'],
    '武康路': ['/images/spots/shanghai/shanghai_wukanglu.jpg'],
    '南京路': ['/images/spots/shanghai/shanghai_nanjinglu_buxingjie.jpg'],
    '南京路步行街': ['/images/spots/shanghai/shanghai_nanjinglu_buxingjie.jpg'],
    '上海博物馆': ['/images/spots/shanghai/shanghai_shanghai_bowuguan.jpg'],
    '静安寺': ['/images/spots/shanghai/shanghai_jingansi.jpg'],
    '召楼古镇': ['/images/spots/shanghai/shanghai_zhaolou_guzhen.jpg'],
    '上海迪士尼': ['/images/spots/shanghai/shanghai_shanghai_dishini.jpg'],
    '迪士尼乐园': ['/images/spots/shanghai/shanghai_shanghai_dishini.jpg'],
    '城隍庙': ['/images/spots/shanghai/shanghai_chenghuangmiao.jpg'],
    '新天地': ['/images/spots/shanghai/shanghai_xintiandi.jpg'],
    '上海中心大厦': ['/images/spots/shanghai/shanghai_shanghai_zhongxin.jpg'],
    '1933老场坊': ['/images/spots/shanghai/shanghai_1933_laochangfang.jpg'],
    '复旦大学': ['/images/spots/shanghai/shanghai_fudan_daxue.jpg'],
    
    # ========== 西安 (13个) ==========
    '秦始皇兵马俑': ['/images/spots/xian/xian_bingmayong.jpg'],
    '兵马俑': ['/images/spots/xian/xian_bingmayong.jpg'],
    '大雁塔': ['/images/spots/xian/xian_dayanta.jpg'],
    '古城墙': ['/images/spots/xian/xian_xian_chengqiang.jpg'],
    '西安城墙': ['/images/spots/xian/xian_xian_chengqiang.jpg'],
    '华清宫': ['/images/spots/xian/xian_huaqinggong.jpg'],
    '大唐芙蓉园': ['/images/spots/xian/xian_datang_furongyuan.jpg'],
    '回民街': ['/images/spots/xian/xian_huiminjie.jpg'],
    '大唐不夜城': ['/images/spots/xian/xian_datang_buyecheng.jpg'],
    '钟楼': ['/images/spots/xian/xian_zhonglou.jpg'],
    '鼓楼': ['/images/spots/xian/xian_gulou.jpg'],
    '陕西历史博物馆': ['/images/spots/xian/xian_shanxi_lishi_bowuguan.jpg'],
    '小雁塔': ['/images/spots/xian/xian_xiaoyanta.jpg'],
    '碑林博物馆': ['/images/spots/xian/xian_beilin_bowuguan.jpg'],
    '西安交通大学': ['/images/spots/xian/xian_xian_jiaotong_daxue.jpg'],
    
    # ========== 成都 (13个) ==========
    '大熊猫繁育研究基地': ['/images/spots/chengdu/chengdu_xiongmao_jidi.jpg'],
    '熊猫基地': ['/images/spots/chengdu/chengdu_xiongmao_jidi.jpg'],
    '宽窄巷子': ['/images/spots/chengdu/chengdu_kuanzhai_xiangzi.jpg'],
    '锦里': ['/images/spots/chengdu/chengdu_chunxilu.jpg'],
    '锦里古街': ['/images/spots/chengdu/chengdu_jinli_gujie.jpg'],
    '武侯祠': ['/images/spots/chengdu/chengdu_wuhouci.jpg'],
    '杜甫草堂': ['/images/spots/chengdu/chengdu_dufu_caotang.jpg'],
    '青城山': ['/images/spots/chengdu/chengdu_qingchengshan.jpg'],
    '都江堰': ['/images/spots/chengdu/chengdu_dujiangyan.jpg'],
    '春熙路': ['/images/spots/chengdu/chengdu_chunxilu.jpg'],
    '文殊院': ['/images/spots/chengdu/chengdu_wenshuyuan.jpg'],
    '人民公园': ['/images/spots/chengdu/chengdu_renmin_gongyuan.jpg'],
    '九眼桥': ['/images/spots/chengdu/chengdu_jiuyanqiao.jpg'],
    '四川大学': ['/images/spots/chengdu/chengdu_sichuan_daxue.jpg'],
    '太古里': ['/images/spots/chengdu/chengdu_taikuli.jpg'],
    
    # ========== 杭州 (13个) ==========
    '西湖': ['/images/spots/hangzhou/hangzhou_xihu.jpg'],
    '灵隐寺': ['/images/spots/hangzhou/hangzhou_lingyinsi.jpg'],
    '雷峰塔': ['/images/spots/hangzhou/hangzhou_leifengta.jpg'],
    '千岛湖': ['/images/spots/hangzhou/hangzhou_qiandaohu.jpg'],
    '宋城': ['/images/spots/hangzhou/hangzhou_songcheng.jpg'],
    '西溪湿地': ['/images/spots/hangzhou/hangzhou_xixi_shidi.jpg'],
    '河坊街': ['/images/spots/hangzhou/hangzhou_hefangjie.jpg'],
    '断桥残雪': ['/images/spots/hangzhou/hangzhou_duanqiao_canxue.jpg'],
    '苏堤春晓': ['/images/spots/hangzhou/hangzhou_sudi_chunxiao.jpg'],
    '三潭印月': ['/images/spots/hangzhou/hangzhou_santanyinyue.jpg'],
    '浙江大学': ['/images/spots/hangzhou/hangzhou_zhejiang_daxue.jpg'],
    '龙井村': ['/images/spots/hangzhou/hangzhou_longjingcun.jpg'],
    '钱塘江': ['/images/spots/hangzhou/hangzhou_qiantangjiang.jpg'],
    
    # ========== 重庆 (13个) ==========
    '洪崖洞': ['/images/spots/chongqing/chongqing_hongyadong.jpg'],
    '解放碑': ['/images/spots/chongqing/chongqing_jiefangbei.jpg'],
    '磁器口': ['/images/spots/chongqing/chongqing_ciqikou.jpg'],
    '磁器口古镇': ['/images/spots/chongqing/chongqing_ciqikou.jpg'],
    '长江索道': ['/images/spots/chongqing/chongqing_changjiang_suodao.jpg'],
    '武隆天坑': ['/images/spots/chongqing/chongqing_wulong_tiankeng.jpg'],
    '朝天门': ['/images/spots/chongqing/chongqing_chaotianmen.jpg'],
    '李子坝轻轨': ['/images/spots/chongqing/chongqing_liziba_qinggui.jpg'],
    '鹅岭二厂': ['/images/spots/chongqing/chongqing_eling_erchang.jpg'],
    '南山一棵树': ['/images/spots/chongqing/chongqing_nanshan_yikeshu.jpg'],
    '三峡博物馆': ['/images/spots/chongqing/chongqing_sanxia_bowuguan.jpg'],
    '白公馆': ['/images/spots/chongqing/chongqing_baigongguan.jpg'],
    '渣滓洞': ['/images/spots/chongqing/chongqing_zazidong.jpg'],
    '重庆大学': ['/images/spots/chongqing/chongqing_chongqing_daxue.jpg'],
    
    # ========== 青岛 (13个) ==========
    '栈桥': ['/images/spots/qingdao/qingdao_zhanqiao.jpg'],
    '八大关': ['/images/spots/qingdao/qingdao_badaguan.jpg'],
    '崂山': ['/images/spots/qingdao/qingdao_laoshan.jpg'],
    '五四广场': ['/images/spots/qingdao/qingdao_wusi_guangchang.jpg'],
    '青岛啤酒博物馆': ['/images/spots/qingdao/qingdao_qingdao_pijiu_bowuguan.jpg'],
    '金沙滩': ['/images/spots/qingdao/qingdao_jinshatan.jpg'],
    '小鱼山': ['/images/spots/qingdao/qingdao_xiaoyushan.jpg'],
    '信号山公园': ['/images/spots/qingdao/qingdao_xinhaoshan_gongyuan.jpg'],
    '天主教堂': ['/images/spots/qingdao/qingdao_tianzhu_jiaotang.jpg'],
    '奥帆中心': ['/images/spots/qingdao/qingdao_aofan_zhongxin.jpg'],
    '德国总督府': ['/images/spots/qingdao/qingdao_deguo_zongdufu.jpg'],
    '中国海洋大学': ['/images/spots/qingdao/qingdao_zhongguo_haiyang_daxue.jpg'],
    '劈柴院': ['/images/spots/qingdao/qingdao_pichaiyuan.jpg'],
    
    # ========== 广州 (13个) ==========
    '广州塔': ['/images/spots/guangzhou/guangzhou_guangzhouta.jpg'],
    '沙面': ['/images/spots/guangzhou/guangzhou_shamian.jpg'],
    '陈家祠': ['/images/spots/guangzhou/guangzhou_chenjiaci.jpg'],
    '珠江夜游': ['/images/spots/guangzhou/guangzhou_zhujiang_yeyou.jpg'],
    '白云山': ['/images/spots/guangzhou/guangzhou_baiyunshan.jpg'],
    '越秀公园': ['/images/spots/guangzhou/guangzhou_yuexiu_gongyuan.jpg'],
    '北京路步行街': ['/images/spots/guangzhou/guangzhou_beijinglu_buxingjie.jpg'],
    '上下九步行街': ['/images/spots/guangzhou/guangzhou_shangxiajiu_buxingjie.jpg'],
    '长隆欢乐世界': ['/images/spots/guangzhou/guangzhou_changlong_huanle_shijie.jpg'],
    '中山纪念堂': ['/images/spots/guangzhou/guangzhou_zhongshan_jiniantang.jpg'],
    '石室圣心大教堂': ['/images/spots/guangzhou/guangzhou_shishi_shengxin_dajiaotang.jpg'],
    '中山大学': ['/images/spots/guangzhou/guangzhou_zhongshan_daxue.jpg'],
    '华南理工大学': ['/images/spots/guangzhou/guangzhou_huanan_ligong_daxue.jpg'],
    
    # ========== 苏州 (13个) ==========
    '拙政园': ['/images/spots/suzhou/suzhou_zhuozhengyuan.jpg'],
    '虎丘': ['/images/spots/suzhou/suzhou_huqiu.jpg'],
    '留园': ['/images/spots/suzhou/suzhou_liuyuan.jpg'],
    '狮子林': ['/images/spots/suzhou/suzhou_shizilin.jpg'],
    '苏州博物馆': ['/images/spots/suzhou/suzhou_suzhou_bowuguan.jpg'],
    '平江路': ['/images/spots/suzhou/suzhou_pingjianglu.jpg'],
    '周庄古镇': ['/images/spots/suzhou/suzhou_zhouzhuang_guzhen.jpg'],
    '同里古镇': ['/images/spots/suzhou/suzhou_tongli_guzhen.jpg'],
    '金鸡湖': ['/images/spots/suzhou/suzhou_jinjihu.jpg'],
    '寒山寺': ['/images/spots/suzhou/suzhou_hanshansi.jpg'],
    '山塘街': ['/images/spots/suzhou/suzhou_shantangjie.jpg'],
    '苏州大学': ['/images/spots/suzhou/suzhou_suzhou_daxue.jpg'],
    '观前街': ['/images/spots/suzhou/suzhou_guanqianjie.jpg'],
    
    # ========== 厦门 (13个) ==========
    '鼓浪屿': ['/images/spots/xiamen/xiamen_gulangyu.jpg'],
    '厦门大学': ['/images/spots/xiamen/xiamen_xiamen_daxue.jpg'],
    '南普陀寺': ['/images/spots/xiamen/xiamen_nanputuosi.jpg'],
    '曾厝垵': ['/images/spots/xiamen/xiamen_zengcuoan.jpg'],
    '环岛路': ['/images/spots/xiamen/xiamen_huandaolu.jpg'],
    '中山路步行街': ['/images/spots/xiamen/xiamen_zhongshanlu_buxingjie.jpg'],
    '胡里山炮台': ['/images/spots/xiamen/xiamen_hulishan_paotai.jpg'],
    '集美学村': ['/images/spots/xiamen/xiamen_jimei_xuecun.jpg'],
    '园林植物园': ['/images/spots/xiamen/xiamen_yuanlin_zhiwuyuan.jpg'],
    '白城沙滩': ['/images/spots/xiamen/xiamen_baicheng_shatan.jpg'],
    '沙坡尾': ['/images/spots/xiamen/xiamen_shapowei.jpg'],
    '厦门科技馆': ['/images/spots/xiamen/xiamen_xiamen_kejiguan.jpg'],
    '五缘湾': ['/images/spots/xiamen/xiamen_wuyuanwan.jpg'],
    
    # ========== 南京 (13个) ==========
    '中山陵': ['/images/spots/nanjing/nanjing_zhongshanling.jpg'],
    '夫子庙': ['/images/spots/nanjing/nanjing_fuzimiao.jpg'],
    '秦淮河': ['/images/spots/nanjing/nanjing_qinhuaihe.jpg'],
    '明孝陵': ['/images/spots/nanjing/nanjing_mingxiaoling.jpg'],
    '总统府': ['/images/spots/nanjing/nanjing_zongtongfu.jpg'],
    '南京博物院': ['/images/spots/nanjing/nanjing_nanjing_bowuyuan.jpg'],
    '玄武湖': ['/images/spots/nanjing/nanjing_xuanwuhu.jpg'],
    '鸡鸣寺': ['/images/spots/nanjing/nanjing_jimingsi.jpg'],
    '侵华日军南京大屠杀遇难同胞纪念馆': ['/images/spots/nanjing/nanjing_nanjing_datusha_jinianguan.jpg'],
    '老门东': ['/images/spots/nanjing/nanjing_laomendong.jpg'],
    '新街口': ['/images/spots/nanjing/nanjing_xinjiekou.jpg'],
    '南京大学': ['/images/spots/nanjing/nanjing_nanjing_daxue.jpg'],
    '东南大学': ['/images/spots/nanjing/nanjing_dongnan_daxue.jpg'],
    
    # ========== 武汉 (13个) ==========
    '黄鹤楼': ['/images/spots/wuhan/wuhan_huanghelou.jpg'],
    '东湖': ['/images/spots/wuhan/wuhan_donghu.jpg'],
    '户部巷': ['/images/spots/wuhan/wuhan_hubuxiang.jpg'],
    '武汉大学': ['/images/spots/wuhan/wuhan_wuhan_daxue.jpg'],
    '湖北省博物馆': ['/images/spots/wuhan/wuhan_hubei_bowuguan.jpg'],
    '江汉路步行街': ['/images/spots/wuhan/wuhan_jianghanlu_buxingjie.jpg'],
    '古琴台': ['/images/spots/wuhan/wuhan_guqintai.jpg'],
    '晴川阁': ['/images/spots/wuhan/wuhan_qingchuange.jpg'],
    '昙华林': ['/images/spots/wuhan/wuhan_tanhualin.jpg'],
    '汉口江滩': ['/images/spots/wuhan/wuhan_hankou_jiangtan.jpg'],
    '武汉长江大桥': ['/images/spots/wuhan/wuhan_wuhan_changjiang_daqiao.jpg'],
    '归元寺': ['/images/spots/wuhan/wuhan_guiyuansi.jpg'],
    '光谷步行街': ['/images/spots/wuhan/wuhan_guanggu_buxingjie.jpg'],
    
    # ========== 长沙 (13个) ==========
    '岳麓山': ['/images/spots/changsha/changsha_yuelushan.jpg'],
    '橘子洲': ['/images/spots/changsha/changsha_juzizhou.jpg'],
    '湖南省博物馆': ['/images/spots/changsha/changsha_hunan_bowuguan.jpg'],
    '太平街': ['/images/spots/changsha/changsha_taipingjie.jpg'],
    '天心阁': ['/images/spots/changsha/changsha_tianxinge.jpg'],
    '世界之窗': ['/images/spots/changsha/changsha_shijie_zhichuang.jpg'],
    '烈士公园': ['/images/spots/changsha/changsha_lieshi_gongyuan.jpg'],
    '黄兴路步行街': ['/images/spots/changsha/changsha_huangxinglu_buxingjie.jpg'],
    '坡子街': ['/images/spots/changsha/changsha_pozijie.jpg'],
    '爱晚亭': ['/images/spots/changsha/changsha_aiwanting.jpg'],
    '湖南大学': ['/images/spots/changsha/changsha_hunan_daxue.jpg'],
    '中南大学': ['/images/spots/changsha/changsha_zhongnan_daxue.jpg'],
    '超级文和友': ['/images/spots/changsha/changsha_wenheyou.jpg'],
    
    # ========== 深圳 (13个) ==========
    '世界之窗': ['/images/spots/shenzhen/shenzhen_shijie_zhichuang.jpg'],
    '欢乐谷': ['/images/spots/shenzhen/shenzhen_hualegu.jpg'],
    '东部华侨城': ['/images/spots/shenzhen/shenzhen_dongbu_huaqiaocheng.jpg'],
    '大梅沙': ['/images/spots/shenzhen/shenzhen_dameisha.jpg'],
    '小梅沙': ['/images/spots/shenzhen/shenzhen_xiaomeisha.jpg'],
    '深圳湾公园': ['/images/spots/shenzhen/shenzhen_shenzhenwan_gongyuan.jpg'],
    '莲花山公园': ['/images/spots/shenzhen/shenzhen_lianhuashan_gongyuan.jpg'],
    '梧桐山': ['/images/spots/shenzhen/shenzhen_wutongshan.jpg'],
    '中英街': ['/images/spots/shenzhen/shenzhen_zhongyingjie.jpg'],
    '大鹏所城': ['/images/spots/shenzhen/shenzhen_dapeng_suocheng.jpg'],
    '较场尾': ['/images/spots/shenzhen/shenzhen_jiaochangwei.jpg'],
    '深圳大学': ['/images/spots/shenzhen/shenzhen_shenzhen_daxue.jpg'],
    '华强北': ['/images/spots/shenzhen/shenzhen_huaqiangbei.jpg'],
    
    # ========== 三亚 (13个) ==========
    '亚龙湾': ['/images/spots/sanya/sanya_yalongwan.jpg'],
    '天涯海角': ['/images/spots/sanya/sanya_tianyahaijiao.jpg'],
    '南山寺': ['/images/spots/sanya/sanya_nanshansi.jpg'],
    '蜈支洲岛': ['/images/spots/sanya/sanya_wuzhizhou_dao.jpg'],
    '大东海': ['/images/spots/sanya/sanya_dadonghai.jpg'],
    '鹿回头': ['/images/spots/sanya/sanya_luhuitou.jpg'],
    '三亚湾': ['/images/spots/sanya/sanya_sanyawan.jpg'],
    '呀诺达雨林': ['/images/spots/sanya/sanya_yanuoda_yulin.jpg'],
    '槟榔谷': ['/images/spots/sanya/sanya_binglanggu.jpg'],
    '大小洞天': ['/images/spots/sanya/sanya_daxiao_dongtian.jpg'],
    '西岛': ['/images/spots/sanya/sanya_xidao.jpg'],
    '亚特兰蒂斯水世界': ['/images/spots/sanya/sanya_yatelandisi_shuishijie.jpg'],
    '千古情': ['/images/spots/sanya/sanya_qianguging.jpg'],
    
    # ========== 桂林 (13个) ==========
    '漓江': ['/images/spots/guilin/guilin_lijiang.jpg'],
    '象鼻山': ['/images/spots/guilin/guilin_xiangbishan.jpg'],
    '阳朔西街': ['/images/spots/guilin/guilin_yangshuo_xijie.jpg'],
    '龙脊梯田': ['/images/spots/guilin/guilin_longji_titian.jpg'],
    '两江四湖': ['/images/spots/guilin/guilin_liangjiang_sihu.jpg'],
    '银子岩': ['/images/spots/guilin/guilin_yinziyan.jpg'],
    '世外桃源': ['/images/spots/guilin/guilin_shiwai_taoyuan.jpg'],
    '十里画廊': ['/images/spots/guilin/guilin_shili_hualang.jpg'],
    '遇龙河': ['/images/spots/guilin/guilin_yulonghe.jpg'],
    '兴坪古镇': ['/images/spots/guilin/guilin_xingping_guzhen.jpg'],
    '芦笛岩': ['/images/spots/guilin/guilin_ludiyan.jpg'],
    '桂林理工大学': ['/images/spots/guilin/guilin_guilin_ligong_daxue.jpg'],
    '东西巷': ['/images/spots/guilin/guilin_dongxixiang.jpg'],
    
    # ========== 丽江 (13个) ==========
    '丽江古城': ['/images/spots/lijiang/lijiang_lijiang_gucheng.jpg'],
    '玉龙雪山': ['/images/spots/lijiang/lijiang_yulong_xueshan.jpg'],
    '束河古镇': ['/images/spots/lijiang/lijiang_shuhe_guzhen.jpg'],
    '拉市海': ['/images/spots/lijiang/lijiang_lashihai.jpg'],
    '虎跳峡': ['/images/spots/lijiang/lijiang_hutiaoxia.jpg'],
    '木府': ['/images/spots/lijiang/lijiang_mufu.jpg'],
    '黑龙潭公园': ['/images/spots/lijiang/lijiang_heilongtan_gongyuan.jpg'],
    '狮子山': ['/images/spots/lijiang/lijiang_shizishan.jpg'],
    '白沙古镇': ['/images/spots/lijiang/lijiang_baisha_guzhen.jpg'],
    '泸沽湖': ['/images/spots/lijiang/lijiang_luguhu.jpg'],
    '蓝月谷': ['/images/spots/lijiang/lijiang_lanyuegu.jpg'],
    '玉水寨': ['/images/spots/lijiang/lijiang_yushuizhai.jpg'],
    '东巴谷': ['/images/spots/lijiang/lijiang_dongbagu.jpg'],
    
    # ========== 张家界 (13个) ==========
    '张家界国家森林公园': ['/images/spots/zhangjiajie/zhangjiajie_zhangjiajie_forest.jpg'],
    '天门山': ['/images/spots/zhangjiajie/zhangjiajie_tianmenshan.jpg'],
    '黄龙洞': ['/images/spots/zhangjiajie/zhangjiajie_huanglongdong.jpg'],
    '宝峰湖': ['/images/spots/zhangjiajie/zhangjiajie_baofenghu.jpg'],
    '大峡谷玻璃桥': ['/images/spots/zhangjiajie/zhangjiajie_daxiagu_boliqiao.jpg'],
    '袁家界': ['/images/spots/zhangjiajie/zhangjiajie_yuanjiajie.jpg'],
    '杨家界': ['/images/spots/zhangjiajie/zhangjiajie_yangjiajie.jpg'],
    '天子山': ['/images/spots/zhangjiajie/zhangjiajie_tianzishan.jpg'],
    '十里画廊': ['/images/spots/zhangjiajie/zhangjiajie_shili_hualang.jpg'],
    '金鞭溪': ['/images/spots/zhangjiajie/zhangjiajie_jinbianxi.jpg'],
    '黄石寨': ['/images/spots/zhangjiajie/zhangjiajie_huangshizhai.jpg'],
    '百龙天梯': ['/images/spots/zhangjiajie/zhangjiajie_bailong_tianti.jpg'],
    '老屋场': ['/images/spots/zhangjiajie/zhangjiajie_laowuchang.jpg'],
    
    # ========== 黄山 (13个) ==========
    '黄山风景区': ['/images/spots/huangshan/huangshan_huangshan_scenery.jpg'],
    '黄山': ['/images/spots/huangshan/huangshan_huangshan_scenery.jpg'],
    '宏村': ['/images/spots/huangshan/huangshan_hongcun.jpg'],
    '西递': ['/images/spots/huangshan/huangshan_xidi.jpg'],
    '屯溪老街': ['/images/spots/huangshan/huangshan_tunxi_laojie.jpg'],
    '翡翠谷': ['/images/spots/huangshan/huangshan_feicuigu.jpg'],
    '呈坎': ['/images/spots/huangshan/huangshan_chenkan.jpg'],
    '唐模': ['/images/spots/huangshan/huangshan_tangmo.jpg'],
    '潜口民宅': ['/images/spots/huangshan/huangshan_qiankou_minzhai.jpg'],
    '棠樾牌坊群': ['/images/spots/huangshan/huangshan_tangyue_paifangqun.jpg'],
    '徽州古城': ['/images/spots/huangshan/huangshan_huizhou_gucheng.jpg'],
    '齐云山': ['/images/spots/huangshan/huangshan_qiyunshan.jpg'],
    '新安江山水画廊': ['/images/spots/huangshan/huangshan_xinanjiang_shanshui_hualang.jpg'],
    '黄山温泉': ['/images/spots/huangshan/huangshan_huangshan_wenquan.jpg'],
    
    # ========== 九寨沟 (13个) ==========
    '九寨沟': ['/images/spots/jiuzhaigou/jiuzhaigou_jiuzhaigou_valley.jpg'],
    '五花海': ['/images/spots/jiuzhaigou/jiuzhaigou_wuhuahai.jpg'],
    '诺日朗瀑布': ['/images/spots/jiuzhaigou/jiuzhaigou_nuorilang_pubu.jpg'],
    '长海': ['/images/spots/jiuzhaigou/jiuzhaigou_changhai.jpg'],
    '熊猫海': ['/images/spots/jiuzhaigou/jiuzhaigou_xiongmaohai.jpg'],
    '镜海': ['/images/spots/jiuzhaigou/jiuzhaigou_jinghai.jpg'],
    '树正群海': ['/images/spots/jiuzhaigou/jiuzhaigou_shuzheng_qunhai.jpg'],
    '珍珠滩瀑布': ['/images/spots/jiuzhaigou/jiuzhaigou_zhenzhutan_pubu.jpg'],
    '芦苇海': ['/images/spots/jiuzhaigou/jiuzhaigou_luweihai.jpg'],
    '火花海': ['/images/spots/jiuzhaigou/jiuzhaigou_huohuahai.jpg'],
    '箭竹海': ['/images/spots/jiuzhaigou/jiuzhaigou_jianzhuhai.jpg'],
    '原始森林': ['/images/spots/jiuzhaigou/jiuzhaigou_yuanshi_senlin.jpg'],
    '则查洼沟': ['/images/spots/jiuzhaigou/jiuzhaigou_zechawagou.jpg'],
    
    # ========== 大理 (13个) ==========
    '大理古城': ['/images/spots/dali/dali_dali_ancient_city.jpg'],
    '洱海': ['/images/spots/dali/dali_erhai.jpg'],
    '苍山': ['/images/spots/dali/dali_cangshan.jpg'],
    '崇圣寺三塔': ['/images/spots/dali/dali_chongshengsi_santa.jpg'],
    '双廊古镇': ['/images/spots/dali/dali_shuanglang_guzhen.jpg'],
    '喜洲古镇': ['/images/spots/dali/dali_xizhou_guzhen.jpg'],
    '蝴蝶泉': ['/images/spots/dali/dali_hudiequan.jpg'],
    '天龙八部影视城': ['/images/spots/dali/dali_tianlongbabu_yingshicheng.jpg'],
    '南诏风情岛': ['/images/spots/dali/dali_nanzhao_fengqing_dao.jpg'],
    '小普陀': ['/images/spots/dali/dali_xiaoputuo.jpg'],
    '挖色镇': ['/images/spots/dali/dali_wasezhen.jpg'],
    '大理大学': ['/images/spots/dali/dali_dali_daxue.jpg'],
    '才村码头': ['/images/spots/dali/dali_caicun_matou.jpg'],
}

# 城市默认图片
CITY_IMAGES = {
    '北京': '/images/cities/beijing.jpg',
    '上海': '/images/cities/shanghai.jpg',
    '西安': '/images/cities/xian.jpg',
    '成都': '/images/cities/chengdu.jpg',
    '杭州': '/images/cities/hangzhou.jpg',
    '重庆': '/images/cities/chongqing.jpg',
    '青岛': '/images/cities/qingdao.jpg',
    '广州': '/images/cities/guangzhou.jpg',
    '苏州': '/images/cities/suzhou.jpg',
    '厦门': '/images/cities/xiamen.jpg',
    '南京': '/images/cities/nanjing.jpg',
    '武汉': '/images/cities/wuhan.jpg',
    '长沙': '/images/cities/changsha.jpg',
    '深圳': '/images/cities/shenzhen.jpg',
    '三亚': '/images/cities/sanya.jpg',
    '桂林': '/images/cities/guilin.jpg',
    '张家界': '/images/cities/zhangjiajie.jpg',
    '黄山': '/images/cities/huangshan.jpg',
    '九寨沟': '/images/cities/jiuzhaigou.jpg',
    '大理': '/images/cities/dali.jpg',
    '丽江': '/images/cities/lijiang.jpg',
}

def get_spot_image(spot_name: str, city: str) -> list:
    """获取景点图片"""
    if spot_name in SPOT_IMAGES:
        return SPOT_IMAGES[spot_name]
    # 尝试部分匹配
    for name, images in SPOT_IMAGES.items():
        if name in spot_name or spot_name in name:
            return images
    # 返回城市默认图片
    city_img = CITY_IMAGES.get(city, '/images/cities/beijing.jpg')
    return [city_img]


# Pydantic模型
class SpotResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    address: Optional[str] = None
    city: Optional[str] = None
    category: Optional[str] = None
    rating: Optional[float] = 0
    heat_score: Optional[int] = 0
    review_count: Optional[int] = 0
    favorites_count: Optional[int] = 0
    open_time: Optional[str] = None
    ticket_price: Optional[str] = None
    need_booking: Optional[bool] = False
    images: Optional[list] = []
    tags: Optional[list] = []
    match_count: Optional[int] = 0
    score: Optional[float] = 0

    class Config:
        from_attributes = True


class SpotListResponse(BaseModel):
    total: int
    spots: List[SpotResponse]


class RestaurantResponse(BaseModel):
    id: int
    name: str
    cuisine_type: Optional[str] = None
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    rating: Optional[float] = 0
    heat_score: Optional[int] = 0
    price_range: Optional[str] = None
    open_time: Optional[str] = None
    images: Optional[list] = []
    tags: Optional[list] = []

    class Config:
        from_attributes = True


# 路由实现

@router.get("/", response_model=SpotListResponse)
def list_spots(
    city: Optional[str] = Query(None, description="城市筛选"),
    category: Optional[str] = Query(None, description="类别筛选"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """获取景点列表"""
    query = db.query(ScenicSpot)
    
    if city:
        query = query.filter(ScenicSpot.city == city)
    
    if category:
        query = query.filter(ScenicSpot.category == category)
    
    total = query.count()
    offset = (page - 1) * page_size
    spots = query.offset(offset).limit(page_size).all()
    
    return {"total": total, "spots": spots}


@router.get("/search", response_model=SpotListResponse)
def search_spots(
    q: Optional[str] = Query(None, description="搜索关键词"),
    city: Optional[str] = Query(None, description="城市筛选"),
    category: Optional[str] = Query(None, description="类别筛选"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """搜索景点"""
    query = db.query(ScenicSpot)
    
    if q:
        # 模糊搜索
        spots = db.query(ScenicSpot).all()
        spots_data = [s.__dict__ for s in spots]
        filtered = fuzzy_search_spots(spots_data, q)
        spot_ids = [s['id'] for s in filtered]
        if spot_ids:
            query = query.filter(ScenicSpot.id.in_(spot_ids))
    
    if city:
        query = query.filter(ScenicSpot.city == city)
    
    if category:
        query = query.filter(ScenicSpot.category == category)
    
    total = query.count()
    offset = (page - 1) * page_size
    spots = query.offset(offset).limit(page_size).all()
    
    return {"total": total, "spots": spots}


@router.get("/recommend", response_model=SpotListResponse)
def recommend_spots(
    city: str = Query(..., description="城市"),
    preferences: str = Query("", description="偏好标签，逗号分隔"),
    k: int = Query(50, ge=1, le=100, description="返回数量"),
    db: Session = Depends(get_db)
):
    """推荐景点（使用Top K部分排序算法）"""
    query = db.query(ScenicSpot).filter(ScenicSpot.city == city)
    spots = query.all()
    
    # 转换为字典列表
    spots_data = []
    for s in spots:
        # 获取景点图片 - 优先使用映射中的图片
        spot_images = get_spot_image(s.name, s.city)
        # 从数据库tags字段解析tags
        spot_tags = parse_tags(s.tags)
        
        spots_data.append({
            'id': s.id,
            'name': s.name,
            'description': s.description,
            'location_lat': s.location_lat,
            'location_lng': s.location_lng,
            'address': s.address,
            'city': s.city,
            'category': s.category,
            'rating': s.rating or 0,
            'heat_score': s.heat_score or 0,
            'review_count': s.review_count or 0,
            'favorites_count': s.favorites_count or 0,
            'open_time': s.open_time,
            'ticket_price': s.ticket_price,
            'need_booking': s.need_booking,
            'images': spot_images if spot_images else [],
            'tags': spot_tags
        })
    
    # 推荐排序算法
    # score = 偏好权重 * 匹配到的偏好个数 + 收藏权重 * 收藏人数 + 评分权重 * 平均评分
    pref_list = [p.strip() for p in preferences.split(',')] if preferences else []
    
    for spot in spots_data:
        spot_pref_tags = spot.get('tags', [])
        
        # 计算匹配到的偏好个数
        match_count = 0
        matched_prefs = []
        for pref in pref_list:
            if pref in spot_pref_tags:
                match_count += 1
                matched_prefs.append(pref)
        
        # 计算各项分数
        pref_score = match_count * PREFERENCE_WEIGHT
        favorites_score = (spot.get('favorites_count', 0) or 0) * FAVORITES_WEIGHT
        rating_score = (spot.get('rating', 0) or 0) * RATING_WEIGHT
        
        # 总分
        spot['score'] = pref_score + favorites_score + rating_score
        spot['match_count'] = match_count
        spot['matched_prefs'] = matched_prefs
    
    # 按分数排序（降序）
    spots_data.sort(key=lambda x: x['score'], reverse=True)
    
    # 返回前k个结果
    result = spots_data[:k]
    
    return {"total": len(result), "spots": result}


@router.get("/{spot_id}")
def get_spot(spot_id: int, db: Session = Depends(get_db)):
    """获取景点详情"""
    spot = db.query(ScenicSpot).filter(ScenicSpot.id == spot_id).first()
    if not spot:
        return {"error": "景点不存在"}
    
    # 转换为字典并添加图片
    spot_dict = {
        'id': spot.id,
        'name': spot.name,
        'description': spot.description,
        'location_lat': spot.location_lat,
        'location_lng': spot.location_lng,
        'address': spot.address,
        'city': spot.city,
        'category': spot.category,
        'type': spot.type,
        'rating': spot.rating or 0,
        'heat_score': spot.heat_score or 0,
        'review_count': spot.review_count or 0,
        'favorites_count': spot.favorites_count or 0,
        'open_time': spot.open_time,
        'ticket_price': spot.ticket_price,
        'need_booking': spot.need_booking,
        'images': get_spot_image(spot.name, spot.city),
        'tags': parse_tags(spot.tags)
    }
    print(f"[DEBUG] get_spot 返回数据: {spot_dict}")
    return spot_dict


@router.get("/city/list")
def get_city_list(db: Session = Depends(get_db)):
    """获取所有城市列表"""
    cities = db.query(ScenicSpot.city).distinct().all()
    return {"cities": [c[0] for c in cities if c[0]]}


@router.get("/restaurants/recommend", response_model=List[RestaurantResponse])
def recommend_restaurants(
    spot_id: int = Query(..., description="景点ID"),
    k: int = Query(10, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """推荐美食（使用Top K部分排序算法）"""
    restaurants = db.query(Restaurant).filter(Restaurant.spot_id == spot_id).all()
    
    # 转换为字典列表
    restaurants_data = []
    for r in restaurants:
        restaurants_data.append({
            'id': r.id,
            'name': r.name,
            'cuisine_type': r.cuisine_type,
            'location_lat': r.location_lat,
            'location_lng': r.location_lng,
            'rating': r.rating,
            'heat_score': r.heat_score,
            'price_range': r.price_range,
            'open_time': r.open_time,
            'images': r.images or [],
            'tags': r.tags or []
        })
    
    # 使用部分排序
    result = top_k_restaurants(restaurants_data, k=k)
    
    return result


@router.get("/restaurants/by-city", response_model=List[RestaurantResponse])
def get_restaurants_by_city(
    city: str = Query(..., description="城市名"),
    k: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """获取城市美食推荐"""
    # 先找到该城市的景点ID范围
    city_spots = db.query(ScenicSpot).filter(ScenicSpot.city == city).all()
    if not city_spots:
        return []
    
    spot_ids = [s.id for s in city_spots]
    
    # 查询这些景点的餐厅
    restaurants = db.query(Restaurant).filter(Restaurant.spot_id.in_(spot_ids)).all()
    
    # 转换为响应格式
    result = []
    for r in restaurants:
        result.append({
            'id': r.id,
            'name': r.name,
            'cuisine_type': r.cuisine_type,
            'location_lat': r.location_lat,
            'location_lng': r.location_lng,
            'rating': r.rating,
            'heat_score': r.heat_score,
            'price_range': r.price_range,
            'open_time': r.open_time,
            'images': r.images or [],
            'tags': r.tags or []
        })
    
    # 按评分和热度排序
    result.sort(key=lambda x: (x['rating'], x['heat_score']), reverse=True)
    return result[:k]
