<template>
  <div class="city-page">
    <!-- 顶部导航 -->
    <header class="page-header">
      <button class="back-btn" @click="goBack">←</button>
      <h1 class="page-title">{{ cityName }}</h1>
      <button class="action-btn" @click="startPlan">创建行程</button>
    </header>

    <!-- 城市介绍 -->
    <section class="city-intro">
      <div class="intro-bg" :style="{backgroundImage: `url(${cityImage})`}"></div>
      <div class="intro-overlay">
        <h2>{{ cityName }}</h2>
        <p>{{ spotCount }}个热门景点</p>
      </div>
    </section>

    <!-- 景点筛选 -->
    <section class="filter-bar">
      <button 
        v-for="cat in categories" 
        :key="cat"
        class="filter-tag"
        :class="{ active: selectedCategory === cat }"
        @click="selectedCategory = cat"
      >
        {{ cat }}
      </button>
    </section>

    <!-- 景点列表 -->
    <section class="spots-section">
      <div class="spots-grid">
        <div 
          v-for="spot in filteredSpots" 
          :key="spot.id"
          class="spot-card"
          @click="goToSpot(spot)"
        >
          <div class="spot-image">
            <img :src="spot.image || defaultImage" :alt="spot.name" loading="lazy" />
            <div class="image-overlay"></div>
          </div>
          <div class="spot-content">
            <div class="spot-badges-below">
              <div class="badge rating-badge">
                <span class="star">★</span>
                <span>{{ (spot.rating || 0).toFixed(1) }}</span>
              </div>
              <div class="badge fav-badge">
                <span class="heart">♥</span>
                <span>{{ formatNumber(spot.favorites_count || 0) }}</span>
              </div>
            </div>
            <div class="spot-header">
              <h3 class="spot-title">{{ spot.name }}</h3>
              <span class="spot-category" v-if="spot.category">{{ spot.category }}</span>
            </div>
            <p class="spot-desc">{{ spot.description?.slice(0, 40) }}{{ spot.description?.length > 40 ? '...' : '' }}</p>
            <div class="spot-footer">
              <div class="spot-tags">
                <span v-for="tag in (spot.tags || []).slice(0, 2)" :key="tag" class="tag">{{ tag }}</span>
              </div>
              <div class="spot-arrow">→</div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 空状态 -->
    <div v-if="filteredSpots.length === 0" class="empty-state">
      <p>暂无景点数据</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onActivated } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const cityName = ref('')
const spots = ref([])
const selectedCategory = ref('全部')
const defaultImage = '/images/cities/beijing.jpg'

const categories = ['全部', '历史古迹', '风景名胜', '地标建筑', '博物展览', '休闲娱乐', '美食']

// 城市默认图片
const cityImages = {
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
  '凤凰': '/images/cities/fenghuang.jpg',
}

const cityImage = computed(() => {
  return cityImages[cityName.value] || '/images/cities/beijing.jpg'
})

// ==================== 景点图片智能映射（基于images/spots目录）====================

// 所有景点图片映射表 - 关键词 -> 图片路径
const spotImageMap = {
  // 北京
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
  
  // 上海
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
  
  // 西安
  '兵马俑': '/images/spots/xian/xian_bingmayong.jpg',
  '秦始皇': '/images/spots/xian/xian_bingmayong.jpg',
  '大雁塔': '/images/spots/xian/xian_dayanta.jpg',
  '城墙': '/images/spots/xian/xian_xian_chengqiang.jpg',
  '华清': '/images/spots/xian/xian_huaqinggong.jpg',
  '大唐': '/images/spots/xian/xian_datang_furongyuan.jpg',
  '回民街': '/images/spots/xian/xian_huiminjie.jpg',
  '碑林': '/images/spots/xian/xian_xian_chengqiang.jpg',
  '钟楼': '/images/spots/xian/xian_xian_chengqiang.jpg',
  '鼓楼': '/images/spots/xian/xian_xian_chengqiang.jpg',
  '小雁塔': '/images/spots/xian/xian_dayanta.jpg',
  '历史博物馆': '/images/spots/xian/xian_datang_furongyuan.jpg',
  '陕博': '/images/spots/xian/xian_datang_furongyuan.jpg',
  '不夜城': '/images/spots/xian/xian_dayanta.jpg',
  '永兴坊': '/images/spots/xian/xian_huiminjie.jpg',
  '法门寺': '/images/spots/xian/xian_huaqinggong.jpg',
  '终南山': '/images/spots/xian/xian_huaqinggong.jpg',
  '翠华山': '/images/spots/xian/xian_huaqinggong.jpg',
  '白鹿原': '/images/spots/xian/xian_huaqinggong.jpg',
  '乾陵': '/images/spots/xian/xian_bingmayong.jpg',
  
  // 成都
  '宽窄巷子': '/images/spots/chengdu/chengdu_kuanzhai_xiangzi.jpg',
  '锦里': '/images/spots/chengdu/chengdu_chunxilu.jpg',
  '熊猫': '/images/spots/chengdu/chengdu_xiongmao_jidi.jpg',
  '春熙路': '/images/spots/chengdu/chengdu_kuanzhai_xiangzi.jpg',
  '太古里': '/images/spots/chengdu/chengdu_kuanzhai_xiangzi.jpg',
  'IFS': '/images/spots/chengdu/chengdu_kuanzhai_xiangzi.jpg',
  '天府广场': '/images/spots/chengdu/chengdu_kuanzhai_xiangzi.jpg',
  '人民公园': '/images/spots/chengdu/chengdu_kuanzhai_xiangzi.jpg',
  '武侯祠': '/images/spots/chengdu/chengdu_chunxilu.jpg',
  '杜甫草堂': '/images/spots/chengdu/chengdu_kuanzhai_xiangzi.jpg',
  '青羊宫': '/images/spots/chengdu/chengdu_kuanzhai_xiangzi.jpg',
  '文殊院': '/images/spots/chengdu/chengdu_kuanzhai_xiangzi.jpg',
  
  // 重庆
  '洪崖洞': '/images/spots/chongqing/chongqing_hongyadong.jpg',
  '解放碑': '/images/spots/chongqing/chongqing_jiefangbei.jpg',
  '磁器口': '/images/spots/chongqing/chongqing_ciqikou.jpg',
  '长江': '/images/spots/chongqing/chongqing_hongyadong.jpg',
  '索道': '/images/spots/chongqing/chongqing_hongyadong.jpg',
  '朝天门': '/images/spots/chongqing/chongqing_hongyadong.jpg',
  '南山': '/images/spots/chongqing/chongqing_hongyadong.jpg',
  '武隆': '/images/spots/chongqing/chongqing_hongyadong.jpg',
  '大足': '/images/spots/chongqing/chongqing_ciqikou.jpg',
  '李子坝': '/images/spots/chongqing/chongqing_hongyadong.jpg',
  '鹅岭': '/images/spots/chongqing/chongqing_hongyadong.jpg',
  '十八梯': '/images/spots/chongqing/chongqing_hongyadong.jpg',
  
  // 大理
  '洱海': '/images/spots/dali/dali_erhai.jpg',
  '大理古城': '/images/spots/dali/dali_dali_ancient_city.jpg',
  '双廊': '/images/spots/dali/dali_erhai.jpg',
  '喜洲': '/images/spots/dali/dali_dali_ancient_city.jpg',
  '苍山': '/images/spots/dali/dali_erhai.jpg',
  '崇圣寺': '/images/spots/dali/dali_dali_ancient_city.jpg',
  '三塔': '/images/spots/dali/dali_dali_ancient_city.jpg',
  
  // 桂林
  '漓江': '/images/spots/guilin/guilin_lijiang.jpg',
  '象鼻山': '/images/spots/guilin/guilin_xiangbishan.jpg',
  '阳朔': '/images/spots/guilin/guilin_lijiang.jpg',
  '遇龙河': '/images/spots/guilin/guilin_lijiang.jpg',
  '十里画廊': '/images/spots/guilin/guilin_lijiang.jpg',
  '兴坪': '/images/spots/guilin/guilin_lijiang.jpg',
  '七星岩': '/images/spots/guilin/guilin_xiangbishan.jpg',
  '芦笛岩': '/images/spots/guilin/guilin_xiangbishan.jpg',
  
  // 杭州
  '西湖': '/images/spots/hangzhou/hangzhou_xihu.jpg',
  '灵隐寺': '/images/spots/hangzhou/hangzhou_lingyinsi.jpg',
  '雷峰塔': '/images/spots/hangzhou/hangzhou_leifengta.jpg',
  '断桥': '/images/spots/hangzhou/hangzhou_xihu.jpg',
  '苏堤': '/images/spots/hangzhou/hangzhou_xihu.jpg',
  '三潭': '/images/spots/hangzhou/hangzhou_xihu.jpg',
  '宋城': '/images/spots/hangzhou/hangzhou_xihu.jpg',
  '西溪': '/images/spots/hangzhou/hangzhou_xihu.jpg',
  '河坊街': '/images/spots/hangzhou/hangzhou_lingyinsi.jpg',
  '龙井': '/images/spots/hangzhou/hangzhou_lingyinsi.jpg',
  '千岛湖': '/images/spots/hangzhou/hangzhou_xihu.jpg',
  '湘湖': '/images/spots/hangzhou/hangzhou_xihu.jpg',
  '六和塔': '/images/spots/hangzhou/hangzhou_leifengta.jpg',
  
  // 黄山
  '黄山': '/images/spots/huangshan/huangshan_huangshan_scenery.jpg',
  '光明顶': '/images/spots/huangshan/huangshan_huangshan_scenery.jpg',
  '迎客松': '/images/spots/huangshan/huangshan_huangshan_scenery.jpg',
  
  // 九寨沟
  '九寨沟': '/images/spots/jiuzhaigou/jiuzhaigou_jiuzhaigou_valley.jpg',
  '五彩池': '/images/spots/jiuzhaigou/jiuzhaigou_jiuzhaigou_valley.jpg',
  '珍珠滩': '/images/spots/jiuzhaigou/jiuzhaigou_jiuzhaigou_valley.jpg',
  '诺日朗': '/images/spots/jiuzhaigou/jiuzhaigou_jiuzhaigou_valley.jpg',
  '树正': '/images/spots/jiuzhaigou/jiuzhaigou_jiuzhaigou_valley.jpg',
  
  // 丽江
  '丽江古城': '/images/spots/lijiang/lijiang_lijiang_gucheng.jpg',
  '玉龙雪山': '/images/spots/lijiang/lijiang_yulong_xueshan.jpg',
  '泸沽湖': '/images/spots/lijiang/lijiang_lijiang_gucheng.jpg',
  '束河': '/images/spots/lijiang/lijiang_lijiang_gucheng.jpg',
  '拉市海': '/images/spots/lijiang/lijiang_lijiang_gucheng.jpg',
  
  // 凤凰
  '凤凰古城': '/images/spots/fenghuang/fenghuang_fenghuang_town.jpg',
  '凤凰': '/images/spots/fenghuang/fenghuang_fenghuang_town.jpg',
  
  // 广州
  '广州塔': '/images/spots/guangzhou/guangzhou_guangzhouta.jpg',
  '小蛮腰': '/images/spots/guangzhou/guangzhou_guangzhouta.jpg',
  '沙面': '/images/spots/guangzhou/guangzhou_shamian.jpg',
  '陈家祠': '/images/spots/guangzhou/guangzhou_chenjiaci.jpg',
  '珠江': '/images/spots/guangzhou/guangzhou_guangzhouta.jpg',
  '白云山': '/images/spots/guangzhou/guangzhou_guangzhouta.jpg',
  '北京路': '/images/spots/guangzhou/guangzhou_guangzhouta.jpg',
  '上下九': '/images/spots/guangzhou/guangzhou_shamian.jpg',
  
  // 苏州
  '拙政园': '/images/spots/suzhou/suzhou_zhuozhengyuan.jpg',
  '虎丘': '/images/spots/suzhou/suzhou_huqiu.jpg',
  '留园': '/images/spots/suzhou/suzhou_zhuozhengyuan.jpg',
  '狮子林': '/images/spots/suzhou/suzhou_zhuozhengyuan.jpg',
  '网师园': '/images/spots/suzhou/suzhou_zhuozhengyuan.jpg',
  '平江路': '/images/spots/suzhou/suzhou_zhuozhengyuan.jpg',
  '山塘街': '/images/spots/suzhou/suzhou_zhuozhengyuan.jpg',
  '周庄': '/images/spots/suzhou/suzhou_zhuozhengyuan.jpg',
  '同里': '/images/spots/suzhou/suzhou_zhuozhengyuan.jpg',
  '甪直': '/images/spots/suzhou/suzhou_zhuozhengyuan.jpg',
  '金鸡湖': '/images/spots/suzhou/suzhou_zhuozhengyuan.jpg',
  '太湖': '/images/spots/suzhou/suzhou_zhuozhengyuan.jpg',
  '阳澄湖': '/images/spots/suzhou/suzhou_zhuozhengyuan.jpg',
  
  // 厦门
  '鼓浪屿': '/images/spots/xiamen/xiamen_gulangyu.jpg',
  '厦门大学': '/images/spots/xiamen/xiamen_xiamen_daxue.jpg',
  '南普陀': '/images/spots/xiamen/xiamen_xiamen_daxue.jpg',
  '环岛路': '/images/spots/xiamen/xiamen_gulangyu.jpg',
  '曾厝垵': '/images/spots/xiamen/xiamen_gulangyu.jpg',
  '沙坡尾': '/images/spots/xiamen/xiamen_gulangyu.jpg',
  '中山路': '/images/spots/xiamen/xiamen_gulangyu.jpg',
  '五缘湾': '/images/spots/xiamen/xiamen_gulangyu.jpg',
  
  // 三亚
  '天涯海角': '/images/spots/sanya/sanya_tianyahaijiao.jpg',
  '亚龙湾': '/images/spots/sanya/sanya_yalongwan.jpg',
  '三亚湾': '/images/spots/sanya/sanya_tianyahaijiao.jpg',
  '大东海': '/images/spots/sanya/sanya_yalongwan.jpg',
  '海棠湾': '/images/spots/sanya/sanya_yalongwan.jpg',
  '蜈支洲岛': '/images/spots/sanya/sanya_yalongwan.jpg',
  '南山': '/images/spots/sanya/sanya_tianyahaijiao.jpg',
  '鹿回头': '/images/spots/sanya/sanya_yalongwan.jpg',
  '天涯镇': '/images/spots/sanya/sanya_tianyahaijiao.jpg',
  '后海': '/images/spots/sanya/sanya_yalongwan.jpg',
  '免税店': '/images/spots/sanya/sanya_yalongwan.jpg',
  
  // 张家界
  '张家界': '/images/spots/zhangjiajie/zhangjiajie_zhangjiajie_forest.jpg',
  '武陵源': '/images/spots/zhangjiajie/zhangjiajie_zhangjiajie_forest.jpg',
  '天门山': '/images/spots/zhangjiajie/zhangjiajie_zhangjiajie_forest.jpg',
  '玻璃桥': '/images/spots/zhangjiajie/zhangjiajie_zhangjiajie_forest.jpg',
  '黄龙洞': '/images/spots/zhangjiajie/zhangjiajie_zhangjiajie_forest.jpg',
  '宝峰湖': '/images/spots/zhangjiajie/zhangjiajie_zhangjiajie_forest.jpg',
  
  // 新增城市 - 南京
  '中山陵': '/images/spots/nanjing/nanjing_zhongshanling.jpg',
  '夫子庙': '/images/spots/nanjing/nanjing_fuzimiao.jpg',
  '秦淮河': '/images/spots/nanjing/nanjing_qinhuaihe.jpg',
  '明孝陵': '/images/spots/nanjing/nanjing_mingxiaoling.jpg',
  '总统府': '/images/spots/nanjing/nanjing_zongtongfu.jpg',
  '南京博物院': '/images/spots/nanjing/nanjing_nanjing_bowuyuan.jpg',
  '玄武湖': '/images/spots/nanjing/nanjing_xuanwuhu.jpg',
  '鸡鸣寺': '/images/spots/nanjing/nanjing_jimingsi.jpg',
  '侵华日军南京大屠杀遇难同胞纪念馆': '/images/spots/nanjing/nanjing_nanjing_datusha_jinianguan.jpg',
  '老门东': '/images/spots/nanjing/nanjing_laomendong.jpg',
  '新街口': '/images/spots/nanjing/nanjing_xinjiekou.jpg',
  '南京大学': '/images/spots/nanjing/nanjing_nanjing_daxue.jpg',
  '东南大学': '/images/spots/nanjing/nanjing_dongnan_daxue.jpg',
  
  // 新增城市 - 武汉
  '黄鹤楼': '/images/spots/wuhan/wuhan_huanghelou.jpg',
  '东湖': '/images/spots/wuhan/wuhan_donghu.jpg',
  '户部巷': '/images/spots/wuhan/wuhan_hubuxiang.jpg',
  '武汉大学': '/images/spots/wuhan/wuhan_wuhan_daxue.jpg',
  '湖北省博物馆': '/images/spots/wuhan/wuhan_hubei_bowuguan.jpg',
  '江汉路步行街': '/images/spots/wuhan/wuhan_jianghanlu_buxingjie.jpg',
  '古琴台': '/images/spots/wuhan/wuhan_guqintai.jpg',
  '晴川阁': '/images/spots/wuhan/wuhan_qingchuange.jpg',
  '昙华林': '/images/spots/wuhan/wuhan_tanhualin.jpg',
  '汉口江滩': '/images/spots/wuhan/wuhan_hankou_jiangtan.jpg',
  '武汉长江大桥': '/images/spots/wuhan/wuhan_wuhan_changjiang_daqiao.jpg',
  '归元寺': '/images/spots/wuhan/wuhan_guiyuansi.jpg',
  '光谷步行街': '/images/spots/wuhan/wuhan_guanggu_buxingjie.jpg',
  
  // 新增城市 - 长沙
  '岳麓山': '/images/spots/changsha/changsha_yuelushan.jpg',
  '橘子洲': '/images/spots/changsha/changsha_juzizhou.jpg',
  '湖南省博物馆': '/images/spots/changsha/changsha_hunan_bowuguan.jpg',
  '太平街': '/images/spots/changsha/changsha_taipingjie.jpg',
  '天心阁': '/images/spots/changsha/changsha_tianxinge.jpg',
  '世界之窗': '/images/spots/changsha/changsha_shijie_zhichuang.jpg',
  '烈士公园': '/images/spots/changsha/changsha_lieshi_gongyuan.jpg',
  '黄兴路步行街': '/images/spots/changsha/changsha_huangxinglu_buxingjie.jpg',
  '坡子街': '/images/spots/changsha/changsha_pozijie.jpg',
  '爱晚亭': '/images/spots/changsha/changsha_aiwanting.jpg',
  '湖南大学': '/images/spots/changsha/changsha_hunan_daxue.jpg',
  '中南大学': '/images/spots/changsha/changsha_zhongnan_daxue.jpg',
  '超级文和友': '/images/spots/changsha/changsha_wenheyou.jpg',
  
  // 新增城市 - 深圳
  '欢乐谷': '/images/spots/shenzhen/shenzhen_hualegu.jpg',
  '东部华侨城': '/images/spots/shenzhen/shenzhen_dongbu_huaqiaocheng.jpg',
  '大梅沙': '/images/spots/shenzhen/shenzhen_dameisha.jpg',
  '小梅沙': '/images/spots/shenzhen/shenzhen_xiaomeisha.jpg',
  '深圳湾公园': '/images/spots/shenzhen/shenzhen_shenzhenwan_gongyuan.jpg',
  '莲花山公园': '/images/spots/shenzhen/shenzhen_lianhuashan_gongyuan.jpg',
  '梧桐山': '/images/spots/shenzhen/shenzhen_wutongshan.jpg',
  '中英街': '/images/spots/shenzhen/shenzhen_zhongyingjie.jpg',
  '大鹏所城': '/images/spots/shenzhen/shenzhen_dapeng_suocheng.jpg',
  '较场尾': '/images/spots/shenzhen/shenzhen_jiaochangwei.jpg',
  '深圳大学': '/images/spots/shenzhen/shenzhen_shenzhen_daxue.jpg',
  '华强北': '/images/spots/shenzhen/shenzhen_huaqiangbei.jpg',
  
  // 新增城市 - 青岛
  '栈桥': '/images/spots/qingdao/qingdao_zhanqiao.jpg',
  '八大关': '/images/spots/qingdao/qingdao_badaguan.jpg',
  '崂山': '/images/spots/qingdao/qingdao_laoshan.jpg',
  '五四广场': '/images/spots/qingdao/qingdao_wusi_guangchang.jpg',
  '青岛啤酒博物馆': '/images/spots/qingdao/qingdao_qingdao_pijiu_bowuguan.jpg',
  '金沙滩': '/images/spots/qingdao/qingdao_jinshatan.jpg',
  '小鱼山': '/images/spots/qingdao/qingdao_xiaoyushan.jpg',
  '信号山公园': '/images/spots/qingdao/qingdao_xinhaoshan_gongyuan.jpg',
  '天主教堂': '/images/spots/qingdao/qingdao_tianzhu_jiaotang.jpg',
  '奥帆中心': '/images/spots/qingdao/qingdao_aofan_zhongxin.jpg',
  '德国总督府': '/images/spots/qingdao/qingdao_deguo_zongdufu.jpg',
  '中国海洋大学': '/images/spots/qingdao/qingdao_zhongguo_haiyang_daxue.jpg',
  '劈柴院': '/images/spots/qingdao/qingdao_pichaiyuan.jpg',
  
  // 新增景点 - 北京补充
  '北京大学': '/images/spots/beijing/beijing_beijing_daxue.jpg',
  '清华大学': '/images/spots/beijing/beijing_qinghua_daxue.jpg',
  '鸟巢': '/images/spots/beijing/beijing_niaochao.jpg',
  '水立方': '/images/spots/beijing/beijing_shuilifang.jpg',
  '什刹海': '/images/spots/beijing/beijing_shichahai.jpg',
  
  // 新增景点 - 上海补充
  '城隍庙': '/images/spots/shanghai/shanghai_chenghuangmiao.jpg',
  '新天地': '/images/spots/shanghai/shanghai_xintiandi.jpg',
  '上海中心大厦': '/images/spots/shanghai/shanghai_shanghai_zhongxin.jpg',
  '1933老场坊': '/images/spots/shanghai/shanghai_1933_laochangfang.jpg',
  '复旦大学': '/images/spots/shanghai/shanghai_fudan_daxue.jpg',
  
  // 新增景点 - 西安补充
  '大唐不夜城': '/images/spots/xian/xian_datang_buyecheng.jpg',
  '钟楼': '/images/spots/xian/xian_zhonglou.jpg',
  '鼓楼': '/images/spots/xian/xian_gulou.jpg',
  '陕西历史博物馆': '/images/spots/xian/xian_shanxi_lishi_bowuguan.jpg',
  '小雁塔': '/images/spots/xian/xian_xiaoyanta.jpg',
  '碑林博物馆': '/images/spots/xian/xian_beilin_bowuguan.jpg',
  '西安交通大学': '/images/spots/xian/xian_xian_jiaotong_daxue.jpg',
  
  // 新增景点 - 成都补充
  '锦里古街': '/images/spots/chengdu/chengdu_jinli_gujie.jpg',
  '武侯祠': '/images/spots/chengdu/chengdu_wuhouci.jpg',
  '杜甫草堂': '/images/spots/chengdu/chengdu_dufu_caotang.jpg',
  '青城山': '/images/spots/chengdu/chengdu_qingchengshan.jpg',
  '都江堰': '/images/spots/chengdu/chengdu_dujiangyan.jpg',
  '文殊院': '/images/spots/chengdu/chengdu_wenshuyuan.jpg',
  '人民公园': '/images/spots/chengdu/chengdu_renmin_gongyuan.jpg',
  '九眼桥': '/images/spots/chengdu/chengdu_jiuyanqiao.jpg',
  '四川大学': '/images/spots/chengdu/chengdu_sichuan_daxue.jpg',
  '太古里': '/images/spots/chengdu/chengdu_taikuli.jpg',
  
  // 新增景点 - 杭州补充
  '千岛湖': '/images/spots/hangzhou/hangzhou_qiandaohu.jpg',
  '宋城': '/images/spots/hangzhou/hangzhou_songcheng.jpg',
  '西溪湿地': '/images/spots/hangzhou/hangzhou_xixi_shidi.jpg',
  '河坊街': '/images/spots/hangzhou/hangzhou_hefangjie.jpg',
  '断桥残雪': '/images/spots/hangzhou/hangzhou_duanqiao_canxue.jpg',
  '苏堤春晓': '/images/spots/hangzhou/hangzhou_sudi_chunxiao.jpg',
  '三潭印月': '/images/spots/hangzhou/hangzhou_santanyinyue.jpg',
  '浙江大学': '/images/spots/hangzhou/hangzhou_zhejiang_daxue.jpg',
  '龙井村': '/images/spots/hangzhou/hangzhou_longjingcun.jpg',
  '钱塘江': '/images/spots/hangzhou/hangzhou_qiantangjiang.jpg',
  
  // 新增景点 - 重庆补充
  '长江索道': '/images/spots/chongqing/chongqing_changjiang_suodao.jpg',
  '武隆天坑': '/images/spots/chongqing/chongqing_wulong_tiankeng.jpg',
  '朝天门': '/images/spots/chongqing/chongqing_chaotianmen.jpg',
  '李子坝轻轨': '/images/spots/chongqing/chongqing_liziba_qinggui.jpg',
  '鹅岭二厂': '/images/spots/chongqing/chongqing_eling_erchang.jpg',
  '南山一棵树': '/images/spots/chongqing/chongqing_nanshan_yikeshu.jpg',
  '三峡博物馆': '/images/spots/chongqing/chongqing_sanxia_bowuguan.jpg',
  '白公馆': '/images/spots/chongqing/chongqing_baigongguan.jpg',
  '渣滓洞': '/images/spots/chongqing/chongqing_zazidong.jpg',
  '重庆大学': '/images/spots/chongqing/chongqing_chongqing_daxue.jpg',
  
  // 新增景点 - 苏州补充
  '留园': '/images/spots/suzhou/suzhou_liuyuan.jpg',
  '狮子林': '/images/spots/suzhou/suzhou_shizilin.jpg',
  '苏州博物馆': '/images/spots/suzhou/suzhou_suzhou_bowuguan.jpg',
  '平江路': '/images/spots/suzhou/suzhou_pingjianglu.jpg',
  '周庄古镇': '/images/spots/suzhou/suzhou_zhouzhuang_guzhen.jpg',
  '同里古镇': '/images/spots/suzhou/suzhou_tongli_guzhen.jpg',
  '金鸡湖': '/images/spots/suzhou/suzhou_jinjihu.jpg',
  '寒山寺': '/images/spots/suzhou/suzhou_hanshansi.jpg',
  '山塘街': '/images/spots/suzhou/suzhou_shantangjie.jpg',
  '苏州大学': '/images/spots/suzhou/suzhou_suzhou_daxue.jpg',
  '观前街': '/images/spots/suzhou/suzhou_guanqianjie.jpg',
  
  // 新增景点 - 厦门补充
  '南普陀寺': '/images/spots/xiamen/xiamen_nanputuosi.jpg',
  '曾厝垵': '/images/spots/xiamen/xiamen_zengcuoan.jpg',
  '环岛路': '/images/spots/xiamen/xiamen_huandaolu.jpg',
  '中山路步行街': '/images/spots/xiamen/xiamen_zhongshanlu_buxingjie.jpg',
  '胡里山炮台': '/images/spots/xiamen/xiamen_hulishan_paotai.jpg',
  '集美学村': '/images/spots/xiamen/xiamen_jimei_xuecun.jpg',
  '园林植物园': '/images/spots/xiamen/xiamen_yuanlin_zhiwuyuan.jpg',
  '白城沙滩': '/images/spots/xiamen/xiamen_baicheng_shatan.jpg',
  '沙坡尾': '/images/spots/xiamen/xiamen_shapowei.jpg',
  '厦门科技馆': '/images/spots/xiamen/xiamen_xiamen_kejiguan.jpg',
  '五缘湾': '/images/spots/xiamen/xiamen_wuyuanwan.jpg',
  
  // 新增景点 - 广州补充
  '珠江夜游': '/images/spots/guangzhou/guangzhou_zhujiang_yeyou.jpg',
  '白云山': '/images/spots/guangzhou/guangzhou_baiyunshan.jpg',
  '越秀公园': '/images/spots/guangzhou/guangzhou_yuexiu_gongyuan.jpg',
  '北京路步行街': '/images/spots/guangzhou/guangzhou_beijinglu_buxingjie.jpg',
  '上下九步行街': '/images/spots/guangzhou/guangzhou_shangxiajiu_buxingjie.jpg',
  '长隆欢乐世界': '/images/spots/guangzhou/guangzhou_changlong_huanle_shijie.jpg',
  '中山纪念堂': '/images/spots/guangzhou/guangzhou_zhongshan_jiniantang.jpg',
  '石室圣心大教堂': '/images/spots/guangzhou/guangzhou_shishi_shengxin_dajiaotang.jpg',
  '中山大学': '/images/spots/guangzhou/guangzhou_zhongshan_daxue.jpg',
  '华南理工大学': '/images/spots/guangzhou/guangzhou_huanan_ligong_daxue.jpg',
  
  // 新增景点 - 丽江补充
  '束河古镇': '/images/spots/lijiang/lijiang_shuhe_guzhen.jpg',
  '拉市海': '/images/spots/lijiang/lijiang_lashihai.jpg',
  '虎跳峡': '/images/spots/lijiang/lijiang_hutiaoxia.jpg',
  '木府': '/images/spots/lijiang/lijiang_mufu.jpg',
  '黑龙潭公园': '/images/spots/lijiang/lijiang_heilongtan_gongyuan.jpg',
  '狮子山': '/images/spots/lijiang/lijiang_shizishan.jpg',
  '白沙古镇': '/images/spots/lijiang/lijiang_baisha_guzhen.jpg',
  '泸沽湖': '/images/spots/lijiang/lijiang_luguhu.jpg',
  '蓝月谷': '/images/spots/lijiang/lijiang_lanyuegu.jpg',
  '玉水寨': '/images/spots/lijiang/lijiang_yushuizhai.jpg',
  '东巴谷': '/images/spots/lijiang/lijiang_dongbagu.jpg',
  
  // 新增景点 - 三亚补充
  '南山寺': '/images/spots/sanya/sanya_nanshansi.jpg',
  '蜈支洲岛': '/images/spots/sanya/sanya_wuzhizhou_dao.jpg',
  '三亚湾': '/images/spots/sanya/sanya_sanyawan.jpg',
  '海棠湾': '/images/spots/sanya/sanya_haitangwan.jpg',
  '鹿回头': '/images/spots/sanya/sanya_luhuitou.jpg',
  '天涯镇': '/images/spots/sanya/sanya_tianyazhen.jpg',
  '后海': '/images/spots/sanya/sanya_houhai.jpg',
  '免税店': '/images/spots/sanya/sanya_mianshuidian.jpg',
  '亚特兰蒂斯水世界': '/images/spots/sanya/sanya_yatelandisi_shuishijie.jpg',
  '千古情': '/images/spots/sanya/sanya_qianguging.jpg',
  
  // 新增景点 - 桂林补充
  '阳朔西街': '/images/spots/guilin/guilin_yangshuo_xijie.jpg',
  '龙脊梯田': '/images/spots/guilin/guilin_longji_titian.jpg',
  '两江四湖': '/images/spots/guilin/guilin_liangjiang_sihu.jpg',
  '银子岩': '/images/spots/guilin/guilin_yinziyan.jpg',
  '世外桃源': '/images/spots/guilin/guilin_shiwai_taoyuan.jpg',
  '十里画廊': '/images/spots/guilin/guilin_shili_hualang.jpg',
  '遇龙河': '/images/spots/guilin/guilin_yulonghe.jpg',
  '兴坪古镇': '/images/spots/guilin/guilin_xingping_guzhen.jpg',
  '芦笛岩': '/images/spots/guilin/guilin_ludiyan.jpg',
  '桂林理工大学': '/images/spots/guilin/guilin_guilin_ligong_daxue.jpg',
  '东西巷': '/images/spots/guilin/guilin_dongxixiang.jpg',
  
  // 新增景点 - 大理补充
  '苍山': '/images/spots/dali/dali_cangshan.jpg',
  '崇圣寺三塔': '/images/spots/dali/dali_chongshengsi_santa.jpg',
  '双廊古镇': '/images/spots/dali/dali_shuanglang_guzhen.jpg',
  '喜洲古镇': '/images/spots/dali/dali_xizhou_guzhen.jpg',
  '蝴蝶泉': '/images/spots/dali/dali_hudiequan.jpg',
  '天龙八部影视城': '/images/spots/dali/dali_tianlongbabu_yingshicheng.jpg',
  '南诏风情岛': '/images/spots/dali/dali_nanzhao_fengqing_dao.jpg',
  '小普陀': '/images/spots/dali/dali_xiaoputuo.jpg',
  '挖色镇': '/images/spots/dali/dali_wasezhen.jpg',
  '大理大学': '/images/spots/dali/dali_dali_daxue.jpg',
  '才村码头': '/images/spots/dali/dali_caicun_matou.jpg',
  
  // 新增景点 - 张家界补充
  '袁家界': '/images/spots/zhangjiajie/zhangjiajie_yuanjiajie.jpg',
  '杨家界': '/images/spots/zhangjiajie/zhangjiajie_yangjiajie.jpg',
  '天子山': '/images/spots/zhangjiajie/zhangjiajie_tianzishan.jpg',
  '十里画廊': '/images/spots/zhangjiajie/zhangjiajie_shili_hualang.jpg',
  '金鞭溪': '/images/spots/zhangjiajie/zhangjiajie_jinbianxi.jpg',
  '黄石寨': '/images/spots/zhangjiajie/zhangjiajie_huangshizhai.jpg',
  '百龙天梯': '/images/spots/zhangjiajie/zhangjiajie_bailong_tianti.jpg',
  '老屋场': '/images/spots/zhangjiajie/zhangjiajie_laowuchang.jpg',
  
  // 新增景点 - 黄山补充
  '宏村': '/images/spots/huangshan/huangshan_hongcun.jpg',
  '西递': '/images/spots/huangshan/huangshan_xidi.jpg',
  '屯溪老街': '/images/spots/huangshan/huangshan_tunxi_laojie.jpg',
  '翡翠谷': '/images/spots/huangshan/huangshan_feicuigu.jpg',
  '呈坎': '/images/spots/huangshan/huangshan_chenkan.jpg',
  '唐模': '/images/spots/huangshan/huangshan_tangmo.jpg',
  '潜口民宅': '/images/spots/huangshan/huangshan_qiankou_minzhai.jpg',
  '棠樾牌坊群': '/images/spots/huangshan/huangshan_tangyue_paifangqun.jpg',
  '徽州古城': '/images/spots/huangshan/huangshan_huizhou_gucheng.jpg',
  '齐云山': '/images/spots/huangshan/huangshan_qiyunshan.jpg',
  '新安江山水画廊': '/images/spots/huangshan/huangshan_xinanjiang_shanshui_hualang.jpg',
  '黄山温泉': '/images/spots/huangshan/huangshan_huangshan_wenquan.jpg',
  
  // 新增景点 - 九寨沟补充
  '五花海': '/images/spots/jiuzhaigou/jiuzhaigou_wuhuahai.jpg',
  '诺日朗瀑布': '/images/spots/jiuzhaigou/jiuzhaigou_nuorilang_pubu.jpg',
  '长海': '/images/spots/jiuzhaigou/jiuzhaigou_changhai.jpg',
  '熊猫海': '/images/spots/jiuzhaigou/jiuzhaigou_xiongmaohai.jpg',
  '镜海': '/images/spots/jiuzhaigou/jiuzhaigou_jinghai.jpg',
  '树正群海': '/images/spots/jiuzhaigou/jiuzhaigou_shuzheng_qunhai.jpg',
  '珍珠滩瀑布': '/images/spots/jiuzhaigou/jiuzhaigou_zhenzhutan_pubu.jpg',
  '芦苇海': '/images/spots/jiuzhaigou/jiuzhaigou_luweihai.jpg',
  '火花海': '/images/spots/jiuzhaigou/jiuzhaigou_huohuahai.jpg',
  '箭竹海': '/images/spots/jiuzhaigou/jiuzhaigou_jianzhuhai.jpg',
  '原始森林': '/images/spots/jiuzhaigou/jiuzhaigou_yuanshi_senlin.jpg',
  '则查洼沟': '/images/spots/jiuzhaigou/jiuzhaigou_zechawagou.jpg',
}

// 获取景点图片
const getSpotImage = (spotName, city) => {
  if (!spotName) return cityImages[city] || defaultImage
  
  // 1. 完全匹配
  if (spotImageMap[spotName]) {
    return spotImageMap[spotName]
  }
  
  // 2. 包含匹配 - 检查景点名称是否包含映射表中的关键词
  for (const [keyword, imagePath] of Object.entries(spotImageMap)) {
    if (spotName.includes(keyword) || keyword.includes(spotName)) {
      return imagePath
    }
  }
  
  // 3. 如果都不匹配，使用城市默认图片
  return cityImages[city] || defaultImage
}

const spotCount = computed(() => spots.value.length)

const filteredSpots = computed(() => {
  if (selectedCategory.value === '全部') return spots.value
  return spots.value.filter(s => s.category === selectedCategory.value)
})

onMounted(async () => {
  cityName.value = route.query.name || '北京'
  await loadSpots()
})

// 当页面重新激活时刷新数据（从其他页面返回时）
onActivated(async () => {
  await loadSpots()
})

const loadSpots = async () => {
  try {
    const response = await fetch(`http://localhost:8000/api/spots/recommend?city=${encodeURIComponent(cityName.value)}`)
    const data = await response.json()
    console.log('API返回数据:', data)
    console.log('景点数量:', data.spots?.length || data.length)
    if (data.spots) {
      spots.value = data.spots.map(s => {
        // 使用智能映射获取图片
        const image = getSpotImage(s.name, cityName.value)
        return {
          ...s,
          image: image
        }
      })
    } else if (Array.isArray(data)) {
      spots.value = data.map(s => {
        const image = getSpotImage(s.name, cityName.value)
        return {
          ...s,
          image: image
        }
      })
    }
    console.log('处理后的景点数量:', spots.value.length)
  } catch (error) {
    console.error('加载失败:', error)
  }
}

// 格式化数字
const formatNumber = (num) => {
  if (!num) return '0'
  if (num >= 10000) {
    return (num / 10000).toFixed(1) + 'w'
  } else if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'k'
  }
  return num.toString()
}

const goBack = () => router.back()

const startPlan = () => {
  router.push({ path: '/create-trip', query: { city: cityName.value } })
}

const goToSpot = (spot) => {
  router.push({ path: '/spot', query: { id: spot.id, city: cityName.value } })
}
</script>

<style scoped>
.city-page {
  min-height: 100vh;
  background: #0a0a1a;
  color: #fff;
  padding-bottom: 80px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 15px 20px;
  background: rgba(10, 10, 26, 0.9);
  backdrop-filter: blur(10px);
  position: sticky;
  top: 0;
  z-index: 100;
}

.back-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 1px solid rgba(0, 212, 255, 0.3);
  background: transparent;
  color: #fff;
  font-size: 20px;
  cursor: pointer;
}

.page-title {
  font-size: 18px;
}

.action-btn {
  padding: 8px 20px;
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  border: none;
  border-radius: 20px;
  color: #fff;
  font-size: 14px;
  cursor: pointer;
}

.city-intro {
  position: relative;
  height: 200px;
  overflow: hidden;
}

.intro-bg {
  position: absolute;
  inset: 0;
  background-size: cover;
  background-position: center;
  filter: blur(5px);
}

.intro-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(transparent, #0a0a1a);
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  padding: 30px;
}

.intro-overlay h2 {
  font-size: 32px;
  margin-bottom: 8px;
}

.intro-overlay p {
  color: rgba(255, 255, 255, 0.6);
}

.filter-bar {
  display: flex;
  gap: 10px;
  padding: 15px 20px;
  overflow-x: auto;
  scrollbar-width: none;
}

.filter-tag {
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(0, 212, 255, 0.2);
  border-radius: 20px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
  white-space: nowrap;
  cursor: pointer;
}

.filter-tag.active {
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  border-color: transparent;
  color: #fff;
}

.spots-section {
  padding: 20px;
}

.spots-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 20px;
}

@media (max-width: 768px) {
  .spots-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 15px;
  }
}

@media (max-width: 480px) {
  .spots-grid {
    grid-template-columns: 1fr;
    gap: 15px;
  }
}

.spot-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
}

.spot-card:hover {
  transform: translateY(-5px);
  border-color: rgba(0, 212, 255, 0.3);
  box-shadow: 0 10px 30px rgba(0, 212, 255, 0.15);
}

.spot-image {
  position: relative;
  height: 160px;
  overflow: hidden;
}

.spot-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.spot-card:hover .spot-image img {
  transform: scale(1.05);
}

.spot-badges {
  position: absolute;
  top: 10px;
  right: 10px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.spot-badges-below {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
}

.badge {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 10px;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(5px);
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.rating-badge {
  color: #ffc107;
}

.fav-badge {
  color: #ff6b6b;
}

.star {
  font-size: 11px;
}

.heart {
  font-size: 10px;
}

.spot-content {
  padding: 16px;
}

.spot-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
  margin-bottom: 8px;
}

.spot-title {
  font-size: 15px;
  font-weight: 600;
  color: #fff;
  line-height: 1.3;
  flex: 1;
}

.spot-category {
  font-size: 11px;
  padding: 3px 8px;
  background: rgba(0, 212, 255, 0.15);
  border-radius: 6px;
  color: #00d4ff;
  white-space: nowrap;
}

.spot-desc {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
  line-height: 1.5;
  margin-bottom: 12px;
}

.spot-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.spot-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.tag {
  font-size: 11px;
  padding: 3px 8px;
  background: rgba(0, 212, 255, 0.1);
  border-radius: 10px;
  color: #00d4ff;
}

.spot-arrow {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(255, 255, 255, 0.5);
  font-size: 14px;
}

.empty-state {
  text-align: center;
  padding: 60px;
  color: rgba(255, 255, 255, 0.5);
}
</style>
