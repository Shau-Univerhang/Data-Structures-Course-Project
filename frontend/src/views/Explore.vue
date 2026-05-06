<template>
  <div class="explore-page">
    <!-- 顶部导航栏 -->
    <Navbar />

    <div class="explore-container">
      <!-- 左侧导航栏 -->
      <aside class="sidebar">
        <div class="sidebar-header">
          <h2>探索发现</h2>
          <p>发现城市的美好</p>
        </div>
        
        <nav class="sidebar-nav">
          <button 
            class="nav-item" 
            :class="{ active: currentTab === 'spots' }"
            @click="currentTab = 'spots'"
          >
            <span class="nav-icon">📍</span>
            <span class="nav-label">景点推荐</span>
          </button>
          <button 
            class="nav-item" 
            :class="{ active: currentTab === 'food' }"
            @click="currentTab = 'food'"
          >
            <span class="nav-icon">🍜</span>
            <span class="nav-label">美食推荐</span>
          </button>
        </nav>

        <!-- 城市筛选 -->
        <div class="city-filter">
          <h3>选择城市</h3>
          <div class="city-list">
            <button 
              v-for="city in cities" 
              :key="city"
              class="city-btn"
              :class="{ active: selectedCity === city }"
              @click="selectedCity = city"
            >
              {{ city }}
            </button>
          </div>
        </div>
      </aside>

      <!-- 右侧内容区 -->
      <main class="content-area">
        <!-- 景点推荐内容 -->
        <div v-if="currentTab === 'spots'" class="content-section">
          <div class="section-header">
            <h1>{{ selectedCity }}热门景点</h1>
            <p>探索{{ selectedCity }}的精彩景点，发现城市之美</p>
          </div>

          <!-- 加载状态 -->
          <div v-if="loadingSpots" class="loading-container">
            <div class="loading-spinner"></div>
            <p>正在加载景点...</p>
          </div>

          <!-- 景点网格 -->
          <div v-else class="cards-grid">
            <div 
              v-for="spot in filteredSpots" 
              :key="spot.id" 
              class="card"
              @click="showSpotDetail(spot)"
            >
              <div class="card-image">
                <img :src="getSpotImage(spot.name, spot.city) || spot.images?.[0] || `/images/cities/${getCityImageName(spot.city)}`" :alt="spot.name" />
              </div>
              <div class="card-info">
                <h3>{{ spot.name }}</h3>
                <div class="card-meta">
                  <span class="rating">⭐ {{ spot.rating?.toFixed(1) || '0.0' }}</span>
                  <span class="favorites">❤️ {{ formatNumber(spot.favorites_count || 0) }}</span>
                </div>
                <div class="card-tags">
                  <span v-for="tag in (spot.tags || []).slice(0, 2)" :key="tag" class="tag">
                    {{ tag }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- 空状态 -->
          <div v-if="!loadingSpots && filteredSpots.length === 0" class="empty-state">
            <span class="empty-icon">🔍</span>
            <p>暂无景点数据</p>
          </div>
        </div>

        <!-- 美食推荐内容 -->
        <div v-else class="content-section">
          <div class="section-header">
            <h1>{{ selectedCity }}特色美食</h1>
            <p>品味{{ selectedCity }}的地道美食，享受舌尖上的旅行</p>
          </div>

          <!-- 美食分类筛选 -->
          <div class="cuisine-filter">
            <button 
              v-for="cuisine in cuisines" 
              :key="cuisine"
              class="filter-btn"
              :class="{ active: selectedCuisine === cuisine }"
              @click="selectedCuisine = cuisine"
            >
              {{ cuisine }}
            </button>
          </div>

          <!-- 美食网格 -->
          <div class="cards-grid">
            <div 
              v-for="food in filteredFoods" 
              :key="food.id"
              class="card"
              @click="showFoodDetail(food)"
            >
              <div class="card-image">
                <img :src="getFoodImage(food.name) || `/images/cities/${getCityImageName(food.city)}`" :alt="food.name" />
                <div class="card-badge featured" v-if="food.is_featured">
                  <span>必吃</span>
                </div>
              </div>
              <div class="card-info">
                <h3>{{ food.name }}</h3>
                <div class="card-meta">
                  <span class="rating">★ {{ food.rating }}</span>
                  <span class="price">{{ food.price_range }}</span>
                </div>
                <div class="card-tags">
                  <span v-for="tag in food.tags.slice(0, 2)" :key="tag" class="tag">
                    {{ tag }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- 空状态 -->
          <div v-if="filteredFoods.length === 0" class="empty-state">
            <span class="empty-icon">🍽️</span>
            <p>暂无美食数据</p>
          </div>
        </div>
      </main>
    </div>

    <!-- 景点详情弹窗 -->
    <div v-if="showSpotModal" class="modal" @click.self="showSpotModal = false">
      <div class="modal-content">
        <button class="modal-close" @click="showSpotModal = false">×</button>
        <div class="modal-header">
          <img :src="getSpotImage(currentSpot.name, currentSpot.city) || currentSpot.images?.[0] || `/images/cities/${getCityImageName(currentSpot.city)}`" :alt="currentSpot.name" />
        </div>
        <div class="modal-body">
          <h2>{{ currentSpot.name }}</h2>
          <div class="modal-rating">
            <span class="star">★</span>
            <span>{{ currentSpot.rating }}</span>
          </div>
          <div class="modal-tags">
            <span v-for="tag in currentSpot.tags" :key="tag" class="tag">{{ tag }}</span>
          </div>
          <p class="modal-desc">{{ currentSpot.description || '暂无描述' }}</p>
          <button class="go-detail-btn" @click="goToSpotDetail(currentSpot)">
            查看详情 / 校园导航
          </button>
        </div>
      </div>
    </div>

    <!-- 美食详情弹窗 -->
    <div v-if="showFoodModal" class="modal" @click.self="showFoodModal = false">
      <div class="modal-content">
        <button class="modal-close" @click="showFoodModal = false">×</button>
        <div class="modal-header">
          <img :src="getFoodImage(currentFood.name) || `/images/cities/${getCityImageName(currentFood.city)}`" :alt="currentFood.name" />
        </div>
        <div class="modal-body">
          <h2>{{ currentFood.name }}</h2>
          <div class="modal-meta">
            <span class="rating">★ {{ currentFood.rating }}</span>
            <span class="price">{{ currentFood.price_range }}</span>
          </div>
          <div class="modal-tags">
            <span v-for="tag in currentFood.tags" :key="tag" class="tag">{{ tag }}</span>
          </div>
          <p class="modal-desc">{{ currentFood.description }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import Navbar from '../components/Navbar.vue'

const router = useRouter()

// 当前选中的标签
const currentTab = ref('spots')
const selectedCity = ref('北京')
const selectedCuisine = ref('全部')

// 弹窗状态
const showSpotModal = ref(false)
const showFoodModal = ref(false)
const currentSpot = ref({})
const currentFood = ref({})

// 城市列表 - 与主页轮播一致
const cities = ['北京', '上海', '西安', '成都', '杭州', '重庆', '青岛', '广州', '苏州', '厦门', '南京', '武汉', '长沙', '深圳', '三亚', '桂林', '张家界', '黄山', '九寨沟', '大理', '丽江']

// 美食分类
const cuisines = ['全部', '川菜', '火锅', '烧烤', '小吃', '粤菜', '湘菜', '西餐', '日料']

// 加载状态
const loadingSpots = ref(false)

// 景点数据
const spots = ref([])

// ========== 景点图片映射 - 和 City.vue 保持一致 ==========

// 上海景点图片映射
const shanghaiSpotImages = {
  '东方明珠': '/images/spots/shanghai/shanghai_dongfang_mingzhu.jpg',
  '外滩': '/images/spots/shanghai/shanghai_waitan.jpg',
  '豫园': '/images/spots/shanghai/shanghai_yuyuan.jpg',
  '田子坊': '/images/spots/shanghai/shanghai_tianzifang.jpg',
  '武康路': '/images/spots/shanghai/shanghai_wukanglu.jpg',
  '南京路': '/images/spots/shanghai/shanghai_nanjinglu_buxingjie.jpg',
  '南京路步行街': '/images/spots/shanghai/shanghai_nanjinglu_buxingjie.jpg',
  '上海博物馆': '/images/spots/shanghai/shanghai_shanghai_bowuguan.jpg',
  '静安寺': '/images/spots/shanghai/shanghai_jingansi.jpg',
  '召楼古镇': '/images/spots/shanghai/shanghai_zhaolou_guzhen.jpg',
  '迪士尼': '/images/spots/shanghai/shanghai_shanghai_dishini.jpg',
  '迪士尼乐园': '/images/spots/shanghai/shanghai_shanghai_dishini.jpg',
  '上海迪士尼': '/images/spots/shanghai/shanghai_shanghai_dishini.jpg',
  '上海迪士尼乐园': '/images/spots/shanghai/shanghai_shanghai_dishini.jpg',
}

// 北京景点图片映射
const beijingSpotImages = {
  '故宫': '/images/spots/beijing/beijing_gugong_bowuyuan.jpg',
  '故宫博物院': '/images/spots/beijing/beijing_gugong_bowuyuan.jpg',
  '长城': '/images/spots/beijing/beijing_badaling_changcheng.jpg',
  '八达岭': '/images/spots/beijing/beijing_badaling_changcheng.jpg',
  '天坛': '/images/spots/beijing/beijing_tiantan_gongyuan.jpg',
  '天坛公园': '/images/spots/beijing/beijing_tiantan_gongyuan.jpg',
  '天安门': '/images/spots/beijing/beijing_tiananmen_guangchang.jpg',
  '天安门广场': '/images/spots/beijing/beijing_tiananmen_guangchang.jpg',
  '颐和园': '/images/spots/beijing/beijing_yiheyuan.jpg',
  '圆明园': '/images/spots/beijing/beijing_yuanmingyuan.jpg',
  '北海公园': '/images/spots/beijing/beijing_beihai_gongyuan.jpg',
  '恭王府': '/images/spots/beijing/beijing_gongwangfu.jpg',
  '景山公园': '/images/spots/beijing/beijing_jingshan_gongyuan.jpg',
  '南锣鼓巷': '/images/spots/beijing/beijing_nanluoguxiang.jpg',
}

// 西安景点图片映射
const xianSpotImages = {
  '兵马俑': '/images/spots/xian/xian_bingmayong.jpg',
  '大雁塔': '/images/spots/xian/xian_dayanta.jpg',
  '古城墙': '/images/spots/xian/xian_xian_chengqiang.jpg',
  '城墙': '/images/spots/xian/xian_xian_chengqiang.jpg',
  '华清宫': '/images/spots/xian/xian_huaqinggong.jpg',
  '大唐芙蓉园': '/images/spots/xian/xian_datang_furongyuan.jpg',
  '回民街': '/images/spots/xian/xian_huiminjie.jpg',
  '大唐不夜城': '/images/spots/xian/xian_datang_buyecheng.jpg',
  '钟楼': '/images/spots/xian/xian_zhonglou.jpg',
  '鼓楼': '/images/spots/xian/xian_gulou.jpg',
  '陕西历史博物馆': '/images/spots/xian/xian_shanxi_lishi_bowuguan.jpg',
  '小雁塔': '/images/spots/xian/xian_xiaoyanta.jpg',
  '碑林博物馆': '/images/spots/xian/xian_beilin_bowuguan.jpg',
  '西安交通大学': '/images/spots/xian/xian_xian_jiaotong_daxue.jpg',
}

// 成都景点图片映射
const chengduSpotImages = {
  '宽窄巷子': '/images/spots/chengdu/chengdu_kuanzhai_xiangzi.jpg',
  '锦里': '/images/spots/chengdu/chengdu_jinli_gujie.jpg',
  '锦里古街': '/images/spots/chengdu/chengdu_jinli_gujie.jpg',
  '大熊猫繁育研究基地': '/images/spots/chengdu/chengdu_xiongmao_jidi.jpg',
  '熊猫基地': '/images/spots/chengdu/chengdu_xiongmao_jidi.jpg',
  '武侯祠': '/images/spots/chengdu/chengdu_wuhouci.jpg',
  '杜甫草堂': '/images/spots/chengdu/chengdu_dufu_caotang.jpg',
  '青城山': '/images/spots/chengdu/chengdu_qingchengshan.jpg',
  '都江堰': '/images/spots/chengdu/chengdu_dujiangyan.jpg',
  '春熙路': '/images/spots/chengdu/chengdu_chunxilu.jpg',
  '文殊院': '/images/spots/chengdu/chengdu_wenshuyuan.jpg',
  '人民公园': '/images/spots/chengdu/chengdu_renmin_gongyuan.jpg',
  '九眼桥': '/images/spots/chengdu/chengdu_jiuyanqiao.jpg',
  '四川大学': '/images/spots/chengdu/chengdu_sichuan_daxue.jpg',
  '太古里': '/images/spots/chengdu/chengdu_taikuli.jpg',
}

// 杭州景点图片映射
const hangzhouSpotImages = {
  '西湖': '/images/spots/hangzhou/hangzhou_xihu.jpg',
  '灵隐寺': '/images/spots/hangzhou/hangzhou_lingyinsi.jpg',
  '雷峰塔': '/images/spots/hangzhou/hangzhou_leifengta.jpg',
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
}

// 重庆景点图片映射
const chongqingSpotImages = {
  '洪崖洞': '/images/spots/chongqing/chongqing_hongyadong.jpg',
  '解放碑': '/images/spots/chongqing/chongqing_jiefangbei.jpg',
  '磁器口': '/images/spots/chongqing/chongqing_ciqikou.jpg',
  '磁器口古镇': '/images/spots/chongqing/chongqing_ciqikou.jpg',
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
}

// 青岛景点图片映射
const qingdaoSpotImages = {
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
}

// 广州景点图片映射
const guangzhouSpotImages = {
  '广州塔': '/images/spots/guangzhou/guangzhou_guangzhouta.jpg',
  '小蛮腰': '/images/spots/guangzhou/guangzhou_guangzhouta.jpg',
  '沙面': '/images/spots/guangzhou/guangzhou_shamian.jpg',
  '陈家祠': '/images/spots/guangzhou/guangzhou_chenjiaci.jpg',
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
}

// 苏州景点图片映射
const suzhouSpotImages = {
  '拙政园': '/images/spots/suzhou/suzhou_zhuozhengyuan.jpg',
  '虎丘': '/images/spots/suzhou/suzhou_huqiu.jpg',
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
}

// 厦门景点图片映射
const xiamenSpotImages = {
  '鼓浪屿': '/images/spots/xiamen/xiamen_gulangyu.jpg',
  '厦门大学': '/images/spots/xiamen/xiamen_xiamen_daxue.jpg',
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
}

// 南京景点图片映射
const nanjingSpotImages = {
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
}

// 武汉景点图片映射
const wuhanSpotImages = {
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
}

// 长沙景点图片映射
const changshaSpotImages = {
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
}

// 深圳景点图片映射
const shenzhenSpotImages = {
  '世界之窗': '/images/spots/shenzhen/shenzhen_shijie_zhichuang.jpg',
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
}

// 三亚景点图片映射
const sanyaSpotImages = {
  '亚龙湾': '/images/spots/sanya/sanya_yalongwan.jpg',
  '天涯海角': '/images/spots/sanya/sanya_tianyahaijiao.jpg',
  '南山寺': '/images/spots/sanya/sanya_nanshansi.jpg',
  '蜈支洲岛': '/images/spots/sanya/sanya_wuzhizhou_dao.jpg',
  '大东海': '/images/spots/sanya/sanya_dadonghai.jpg',
  '鹿回头': '/images/spots/sanya/sanya_luhuitou.jpg',
  '三亚湾': '/images/spots/sanya/sanya_sanyawan.jpg',
  '呀诺达雨林': '/images/spots/sanya/sanya_yanuoda_yulin.jpg',
  '槟榔谷': '/images/spots/sanya/sanya_binglanggu.jpg',
  '大小洞天': '/images/spots/sanya/sanya_daxiao_dongtian.jpg',
  '西岛': '/images/spots/sanya/sanya_xidao.jpg',
  '亚特兰蒂斯水世界': '/images/spots/sanya/sanya_yatelandisi_shuishijie.jpg',
  '千古情': '/images/spots/sanya/sanya_qianguging.jpg',
}

// 桂林景点图片映射
const guilinSpotImages = {
  '漓江': '/images/spots/guilin/guilin_lijiang.jpg',
  '象鼻山': '/images/spots/guilin/guilin_xiangbishan.jpg',
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
}

// 丽江景点图片映射
const lijiangSpotImages = {
  '丽江古城': '/images/spots/lijiang/lijiang_lijiang_gucheng.jpg',
  '玉龙雪山': '/images/spots/lijiang/lijiang_yulong_xueshan.jpg',
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
}

// 张家界景点图片映射
const zhangjiajieSpotImages = {
  '张家界国家森林公园': '/images/spots/zhangjiajie/zhangjiajie_zhangjiajie_forest.jpg',
  '天门山': '/images/spots/zhangjiajie/zhangjiajie_tianmenshan.jpg',
  '黄龙洞': '/images/spots/zhangjiajie/zhangjiajie_huanglongdong.jpg',
  '宝峰湖': '/images/spots/zhangjiajie/zhangjiajie_baofenghu.jpg',
  '大峡谷玻璃桥': '/images/spots/zhangjiajie/zhangjiajie_daxiagu_boliqiao.jpg',
  '袁家界': '/images/spots/zhangjiajie/zhangjiajie_yuanjiajie.jpg',
  '杨家界': '/images/spots/zhangjiajie/zhangjiajie_yangjiajie.jpg',
  '天子山': '/images/spots/zhangjiajie/zhangjiajie_tianzishan.jpg',
  '十里画廊': '/images/spots/zhangjiajie/zhangjiajie_shili_hualang.jpg',
  '金鞭溪': '/images/spots/zhangjiajie/zhangjiajie_jinbianxi.jpg',
  '黄石寨': '/images/spots/zhangjiajie/zhangjiajie_huangshizhai.jpg',
  '百龙天梯': '/images/spots/zhangjiajie/zhangjiajie_bailong_tianti.jpg',
  '老屋场': '/images/spots/zhangjiajie/zhangjiajie_laowuchang.jpg',
}

// 黄山景点图片映射
const huangshanSpotImages = {
  '黄山风景区': '/images/spots/huangshan/huangshan_huangshan_scenery.jpg',
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
}

// 九寨沟景点图片映射
const jiuzhaigouSpotImages = {
  '九寨沟': '/images/spots/jiuzhaigou/jiuzhaigou_jiuzhaigou_valley.jpg',
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

// 大理景点图片映射
const daliSpotImages = {
  '大理古城': '/images/spots/dali/dali_dali_ancient_city.jpg',
  '洱海': '/images/spots/dali/dali_erhai.jpg',
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
}

// 城市景点映射表
const citySpotImages = {
  '北京': beijingSpotImages,
  '上海': shanghaiSpotImages,
  '西安': xianSpotImages,
  '成都': chengduSpotImages,
  '杭州': hangzhouSpotImages,
  '重庆': chongqingSpotImages,
  '青岛': qingdaoSpotImages,
  '广州': guangzhouSpotImages,
  '苏州': suzhouSpotImages,
  '厦门': xiamenSpotImages,
  '南京': nanjingSpotImages,
  '武汉': wuhanSpotImages,
  '长沙': changshaSpotImages,
  '深圳': shenzhenSpotImages,
  '三亚': sanyaSpotImages,
  '桂林': guilinSpotImages,
  '丽江': lijiangSpotImages,
  '张家界': zhangjiajieSpotImages,
  '黄山': huangshanSpotImages,
  '九寨沟': jiuzhaigouSpotImages,
  '大理': daliSpotImages,
}

// 获取景点对应的图片
const getSpotImage = (spotName, city) => {
  const cityImagesMap = citySpotImages[city]
  if (cityImagesMap) {
    // 优先完全匹配
    if (cityImagesMap[spotName]) {
      return cityImagesMap[spotName]
    }
    // 其次包含匹配
    for (const [key, value] of Object.entries(cityImagesMap)) {
      if (spotName.includes(key) || key.includes(spotName)) {
        return value
      }
    }
  }
  return null
}

// 城市图片名称映射
const getCityImageName = (cityName) => {
  const cityMap = {
    '北京': 'beijing.jpg',
    '上海': 'shanghai.jpg',
    '西安': 'xian.jpg',
    '成都': 'chengdu.jpg',
    '重庆': 'chongqing.jpg',
    '杭州': 'hangzhou.jpg',
    '广州': 'guangzhou.jpg',
    '苏州': 'suzhou.jpg',
    '厦门': 'xiamen.jpg',
    '三亚': 'sanya.jpg',
    '青岛': 'qingdao.jpg',
    '南京': 'nanjing.jpg',
    '武汉': 'wuhan.jpg',
    '长沙': 'changsha.jpg',
    '深圳': 'shenzhen.jpg',
    '桂林': 'guilin.jpg',
    '张家界': 'zhangjiajie.jpg',
    '黄山': 'huangshan.jpg',
    '九寨沟': 'jiuzhaigou.jpg',
    '大理': 'dali.jpg',
    '丽江': 'lijiang.jpg',
  }
  return cityMap[cityName] || 'beijing.jpg'
}

// 美食图片映射 - 从后端加载
const getFoodImage = (foodName) => {
  // 将食物名称转换为图片文件名
  const imageMap = {
    // ===== 北京美食 (30+) =====
    '北京烤鸭': 'beijing_kaoya.jpg',
    '老北京炸酱面': 'beijing_zhajiangmian.jpg',
    '涮羊肉': 'beijing_shuanyangrou.jpg',
    '豆汁儿': 'beijing_douzhir.jpg',
    '卤煮火烧': 'beijing_luzhu.jpg',
    '爆肚': 'beijing_baodu.jpg',
    '门钉肉饼': 'beijing_menbing.jpg',
    '炙子烤肉': 'beijing_zhizi.jpg',
    '炒肝': 'beijing_chaogan.jpg',
    '豌豆黄': 'beijing_wandouhuang.jpg',
    '炸灌肠': 'beijing_zhaguan.jpg',
    '麻酱糖饼': 'beijing_majiangbing.jpg',
    '焦圈': 'beijing_jiaoquan.jpg',
    '艾窝窝': 'beijing_aiwowo.jpg',
    '玫瑰饼': 'beijing_meiguibing.jpg',
    '牛舌饼': 'beijing_niushebing.jpg',
    '糖葫芦': 'beijing_tanghulu.jpg',
    '茯苓饼': 'beijing_fulingbing.jpg',
    '正明斋糕点': 'beijing_zhengmingzhai.jpg',
    '京八件': 'beijing_jingbajian.jpg',
    '驴打滚': 'beijing_lvdagun.jpg',
    '奶油炸糕': 'beijing_naiyouzhagao.jpg',
    '面茶': 'beijing_miancha.jpg',
    '小吊梨汤': 'beijing_xiaodiaolitang.jpg',
    '葱烧海参': 'beijing_congshaohaishen.jpg',
    '京酱肉丝': 'beijing_jingjiangrousi.jpg',
    '九转大肠': 'beijing_jiuzhuandachang.jpg',
    '枣钱饼': 'beijing_zaoqianbing.jpg',
    '吹糖人': 'beijing_chuitangren.jpg',
    '柳泉居面点': 'beijing_liudaju.jpg',
    
    // ===== 上海美食 (30+) =====
    '小笼包': 'shanghai_xiaolongbao.jpg',
    '生煎包': 'shanghai_shengjian.jpg',
    '本帮红烧肉': 'shanghai_hongshaorou.jpg',
    '油爆虾': 'shanghai_youbaoxian.jpg',
    '脆牛肉': 'shanghai_cuiniurou.jpg',
    '糟钵头': 'shanghai_baoyu.jpg',
    '开洋葱油拌面': 'shanghai_kaiyangcong.jpg',
    '糖醋小排': 'shanghai_tangcu.jpg',
    '三黄鸡': 'shanghai_sanhuang.jpg',
    '粢饭糕': 'shanghai_cifan.jpg',
    '臭豆腐': 'shanghai_doufu.jpg',
    '咖喱牛肉汤': 'shanghai_niunan.jpg',
    '排骨年糕': 'shanghai_paigu.jpg',
    '四喜烤麸': 'shanghai_baiye.jpg',
    '上海香肠': 'shanghai_xiangchang.jpg',
    '大馄饨': 'shanghai_hundun.jpg',
    '上海青': 'shanghai_cai.jpg',
    '豆沙包': 'shanghai_dousha.jpg',
    '绿豆糕': 'shanghai_lvdou.jpg',
    '擂沙汤圆': 'shanghai_tangyuan.jpg',
    '蟹壳黄': 'shanghai_xiekehuang.jpg',
    '南翔小笼': 'shanghai_nanxiang.jpg',
    '鲜肉月饼': 'shanghai_xianrouyuebing.jpg',
    '梨膏糖': 'shanghai_ligaotang.jpg',
    '五香豆': 'shanghai_wuxiangdou.jpg',
    '高桥松饼': 'shanghai_gaogiaosongbing.jpg',
    '条头糕': 'shanghai_tiaotougao.jpg',
    '油豆腐线粉汤': 'shanghai_you Doufu xianfen.jpg',
    '沈大成糕点': 'shanghai_shengdabai.jpg',
    '国际饭店蝴蝶酥': 'shanghai_guojifandian.jpg',
    
    // ===== 西安美食 (30+) =====
    '羊肉泡馍': 'xian_paomo.jpg',
    '肉夹馍': 'xian_roujiamo.jpg',
    '凉皮': 'xian_liangpi.jpg',
    'Biangbiang面': 'xian_biangbiang.jpg',
    '牛肉泡馍': 'xian_yangroupaomo.jpg',
    '葫芦头': 'xian_hulutou.jpg',
    '粉蒸肉': 'xian_fenzheng.jpg',
    '臊子面': 'xian_shaozi.jpg',
    '油泼面': 'xian_youpo.jpg',
    '锅盔': 'xian_guokui.jpg',
    '胡辣汤': 'xian_hulao.jpg',
    '甑糕': 'xian_jinggao.jpg',
    '灌汤包': 'xian_baozi.jpg',
    '烧饼': 'xian_shaobing.jpg',
    '腊汁肉': 'xian_lazhi.jpg',
    '水盆羊肉': 'xian_yangrou.jpg',
    '黄桂柿子饼': 'xian_huanggui.jpg',
    '酸梅汤': 'xian_suanmei.jpg',
    '冰峰汽水': 'xian_bingfeng.jpg',
    '铜锣烧': 'xian_tongluo.jpg',
    '肉丸糊辣汤': 'xian_rouwan.jpg',
    '小炒泡馍': 'xian_xiaochaopaomo.jpg',
    '南瓜盖被': 'xian_nangai.jpg',
    '腊汁肉夹馍': 'xian_lazhirou.jpg',
    '金线油塔': 'xian_jinxianyouta.jpg',
    '石子馍': 'xian_shizimo.jpg',
    '荞面饸饹': 'xian_qiaomianhele.jpg',
    '柿子糊塌': 'xian_shizihuta.jpg',
    
    // ===== 成都美食 (30+) =====
    '麻辣香锅': 'chengdu_malaxiangguo.jpg',
    '麻婆豆腐': 'chengdu_mapo.jpg',
    '四川火锅': 'chengdu_huoguo.jpg',
    '宫保鸡丁': 'chengdu_gongbao.jpg',
    '水煮牛肉': 'chengdu_shuizhu.jpg',
    '回锅肉': 'chengdu_huiguorou.jpg',
    '夫妻肺片': 'chengdu_fuqifeipian.jpg',
    '担担面': 'chengdu_dandan.jpg',
    '串串香': 'chengdu_chuanchuan.jpg',
    '龙抄手': 'chengdu_longchaoshou.jpg',
    '钟水饺': 'chengdu_zhongshuijiao.jpg',
    '赖汤圆': 'chengdu_lai.jpg',
    '酸辣粉': 'chengdu_suanlafen.jpg',
    '冰粉': 'chengdu_bingfen.jpg',
    '三大炮': 'chengdu_tianpin.jpg',
    '兔头': 'chengdu_tu.jpg',
    '肥肠粉': 'chengdu_changwang.jpg',
    '叶儿粑': 'chengdu_ye.jpg',
    '艾窝窝': 'chengdu_ai.jpg',
    '樟茶鸭': 'chengdu_zhangcha.jpg',
    '钵钵鸡': 'chengdu_boboji.jpg',
    '蛋烘糕': 'chengdu_danhonggao.jpg',
    '糖油果子': 'chengdu_tangyouguozi.jpg',
    '甜水面': 'chengdu_tangmian.jpg',
    '红油水饺': 'chengdu_hongyou.jpg',
    '冒菜': 'chengdu_maonao.jpg',
    '冷锅串串': 'chengdu_lengguo.jpg',
    '成都烧烤': 'chengdu_shaokao.jpg',
    '三哥田螺': 'chengdu_tianluo.jpg',
    '肖家河家常面': 'chengdu_jiachangmian.jpg',
    
    // ===== 杭州美食 (30+) =====
    '西湖醋鱼': 'hangzhou_xihucuyu.jpg',
    '东坡肉': 'hangzhou_dongpo.jpg',
    '片儿川': 'hangzhou_pianer.jpg',
    '葱包桧儿': 'hangzhou_congbao.jpg',
    '宋嫂鱼羹': 'hangzhou_songsaoyugeng.jpg',
    '干炸响铃': 'hangzhou_ganzha.jpg',
    '荷叶粉蒸肉': 'hangzhou_henian.jpg',
    '小鸡酥': 'hangzhou_xiaoji.jpg',
    '南宋定胜糕': 'hangzhou_dingsheng.jpg',
    '知味小笼': 'hangzhou_zhixiao.jpg',
    '吴山酥油饼': 'hangzhou_wushan.jpg',
    '杭州猫耳朵': 'hangzhou_maoer.jpg',
    '麻球王': 'hangzhou_maqiu.jpg',
    '龙井虾仁': 'hangzhou_longjing.jpg',
    '叫花鸡': 'hangzhou_jiao.jpg',
    '白切鸡': 'hangzhou_bai.jpg',
    '糖桂花': 'hangzhou_tang.jpg',
    '绿豆糕': 'hangzhou_lvdou.jpg',
    '粢饭团': 'hangzhou_cifan.jpg',
    '油条': 'hangzhou_you.jpg',
    '西湖莼菜汤': 'hangzhou_chuncai.jpg',
    '虾爆鳝面': 'hangzhou_xiabao.jpg',
    '西湖藕粉': 'hangzhou_oufen.jpg',
    '荷花酥': 'hangzhou_hehua.jpg',
    '定胜糕': 'hangzhou_dingsheng2.jpg',
    '醋鱼': 'hangzhou_cuyu.jpg',
    '杭州小笼': 'hangzhou_xiaolong.jpg',
    '杭州油条': 'hangzhou_youtiao.jpg',
    '杭州粢饭': 'hangzhou_cifantuan.jpg',
    
    // ===== 重庆美食 (30+) =====
    '重庆火锅': 'chongqing_huoguo.jpg',
    '重庆小面': 'chongqing_xiaomian.jpg',
    '酸辣粉': 'chongqing_suanlafen.jpg',
    '麻辣香锅': 'chongqing_malaxiang.jpg',
    '毛血旺': 'chongqing_maoxuewang.jpg',
    '水煮鱼': 'chongqing_shuizhu.jpg',
    '辣子鸡': 'chongqing_laziji.jpg',
    '豆花饭': 'chongqing_douhua.jpg',
    '重庆粑粑': 'chongqing_baba.jpg',
    '糍粑': 'chongqing_ciba.jpg',
    '流水席': 'chongqing_liushui.jpg',
    '八宝饭': 'chongqing_babaofan.jpg',
    '酸萝卜面': 'chongqing_suanmian.jpg',
    '冰粉': 'chongqing_bingfen.jpg',
    '凉粉': 'chongqing_liangfen.jpg',
    '留香鸡': 'chongqing_liuxiang.jpg',
    '串串香': 'chongqing_chuan.jpg',
    '板凳面': 'chongqing_ban.jpg',
    '豌杂面': 'chongqing_wan.jpg',
    '烧麦': 'chongqing_shaomai.jpg',
    '鸡杂': 'chongqing_jizha.jpg',
    '烤鱼': 'chongqing_kaoyu.jpg',
    '黔江鸡杂': 'chongqing_qianjiang.jpg',
    '涪陵榨菜': 'chongqing_fuling.jpg',
    '合川桃片': 'chongqing_hechuan.jpg',
    '江津米花糖': 'chongqing_jiangjin.jpg',
    '陈麻花': 'chongqing_chenmahua.jpg',
    '山城小汤圆': 'chongqing_shancheng.jpg',
    '毛凉粉': 'chongqing_maoliangfen.jpg',
    '重庆回锅肉': 'chongqing_huiguorou.jpg',
    
    // ===== 广州美食 (30+) =====
    '虾饺': 'guangzhou_xiajiao.jpg',
    '叉烧包': 'guangzhou_chashaobao.jpg',
    '蛋挞': 'guangzhou_danta.jpg',
    '马拉糕': 'guangzhou_malagao.jpg',
    '干蒸烧卖': 'guangzhou_shaomai.jpg',
    '奶黄包': 'guangzhou_naicha.jpg',
    '陈醋凤爪': 'guangzhou_fengzhao.jpg',
    '沙爹金钱肚': 'guangzhou_jinqian.jpg',
    '红米肠': 'guangzhou_hongmi.jpg',
    '艇仔粥': 'guangzhou_tingzai.jpg',
    '肠粉': 'guangzhou_changfen.jpg',
    '白切鸡': 'guangzhou_baiqie.jpg',
    '烧鹅': 'guangzhou_shaoe.jpg',
    '腊肠': 'guangzhou_lachang.jpg',
    '卤肉饭': 'guangzhou_lurou.jpg',
    '双皮奶': 'guangzhou_shuangpinai.jpg',
    '姜撞奶': 'guangzhou_ginger.jpg',
    '云吞面': 'guangzhou_yun.jpg',
    '生滚粥': 'guangzhou_sheng.jpg',
    '凉茶': 'guangzhou_liang.jpg',
    '及第粥': 'guangzhou_jidi.jpg',
    '萝卜牛杂': 'guangzhou_luobu.jpg',
    '鸡仔饼': 'guangzhou_jizaibing.jpg',
    '老婆饼': 'guangzhou_laopobing.jpg',
    '广式月饼': 'guangzhou_yuebing.jpg',
    '马蹄糕': 'guangzhou_matigao.jpg',
    '伦教糕': 'guangzhou_lunjiao.jpg',
    '沙河粉': 'guangzhou_shahe.jpg',
    '煲仔饭': 'guangzhou_baozaifan.jpg',
    '豉油鸡': 'guangzhou_zhaji.jpg',
    
    // ===== 苏州美食 (30+) =====
    '松鼠桂鱼': 'suzhou_songshu.jpg',
    '响油鳝糊': 'suzhou_xiangyou.jpg',
    '清炒虾仁': 'suzhou_qingchao.jpg',
    '腌笃鲜': 'suzhou_yandu.jpg',
    '苏式红烧肉': 'suzhou_hongshaorou.jpg',
    '母油船鸭': 'suzhou_muyou.jpg',
    '西瓜鸡': 'suzhou_xigua.jpg',
    '酱方': 'suzhou_jiangfang.jpg',
    '碧螺虾仁': 'suzhou_biluo.jpg',
    '糖粥': 'suzhou_tang.jpg',
    '哑巴生煎': 'suzhou_guotie.jpg',
    '臭豆腐干': 'suzhou_doufu.jpg',
    '咸肉菜饭': 'suzhou_mifan.jpg',
    '汤圆': 'suzhou_yuan.jpg',
    '苏式月饼': 'suzhou_bing.jpg',
    '枣泥麻饼': 'suzhou_zaoni.jpg',
    '酥饼': 'suzhou_su.jpg',
    '海棠糕': 'suzhou_gao.jpg',
    '青团': 'suzhou_tuan.jpg',
    '茶糕': 'suzhou_cha.jpg',
    '蟹壳黄': 'suzhou_xiekehuang.jpg',
    '奥灶面': 'suzhou_aozao.jpg',
    '枫镇大肉面': 'suzhou_fengzhen.jpg',
    '藏书羊肉': 'suzhou_cangshu.jpg',
    '叫花鸡': 'suzhou_jiaohuaji.jpg',
    '三虾面': 'suzhou_sanxia.jpg',
    '梅花糕': 'suzhou_meihuagao.jpg',
    '苏州青团': 'suzhou_qingtuan.jpg',
    '苏州酥饼': 'suzhou_sushibing.jpg',
    
    // ===== 厦门美食 (30+) =====
    '沙茶面': 'xiamen_shachamian.jpg',
    '海蛎煎': 'xiamen_hailijian.jpg',
    '炸五香': 'xiamen_zhawuxiang.jpg',
    '花生汤': 'xiamen_tongsuan.jpg',
    '土笋冻': 'xiamen_tusundong.jpg',
    '满煎糕': 'xiamen_manjian.jpg',
    '四果汤': 'xiamen_siguo.jpg',
    '同安封肉': 'xiamen_fengwei.jpg',
    '大肠血': 'xiamen_dachang.jpg',
    '厦门薄饼': 'xiamen_bing.jpg',
    '烧肉粽': 'xiamen_shaomai.jpg',
    '姜母鸭': 'xiamen_jiangmu.jpg',
    '油墩子': 'xiamen_youdun.jpg',
    '面线糊': 'xiamen_mian.jpg',
    '五香条': 'xiamen_wuxiang.jpg',
    '碗仔粿': 'xiamen_gao.jpg',
    '烧仙草': 'xiamen_cao.jpg',
    '冬瓜茶': 'xiamen_cha.jpg',
    '凤梨酥': 'xiamen_binggan.jpg',
    '鱼丸汤': 'xiamen_yu.jpg',
    '芋包': 'xiamen_yubao.jpg',
    '虾面': 'xiamen_xiamian.jpg',
    '鸭肉粥': 'xiamen_yarouzhou.jpg',
    '韭菜盒': 'xiamen_jiucaige.jpg',
    '薄饼': 'xiamen_baobing.jpg',
    '马蹄酥': 'xiamen_matisu.jpg',
    '沙茶酱': 'xiamen_shacha.jpg',
    '厦门海鲜': 'xiamen_haixian.jpg',
    '鼓浪屿馅饼': 'xiamen_gulang.jpg',
    '黄则和花生汤': 'xiamen_huangzehe.jpg',
    
    // ===== 三亚美食 (30+) =====
    '文昌鸡': 'sanya_wenchang.jpg',
    '加积鸭': 'sanya_jiaji.jpg',
    '和乐蟹': 'sanya_helexie.jpg',
    '东山羊': 'sanya_dongshan.jpg',
    '抱罗粉': 'sanya_baoluo.jpg',
    '清补凉': 'sanya_qingbuliang.jpg',
    '海南粉': 'sanya_haimian.jpg',
    '椰子饭': 'sanya_yezi.jpg',
    '竹筒饭': 'sanya_zhubafan.jpg',
    '黑毛猪': 'sanya_heimei.jpg',
    '海胆蒸蛋': 'sanya_haidan.jpg',
    '龙虾': 'sanya_longxia.jpg',
    '扇贝': 'sanya_shanbei.jpg',
    '海蜇': 'sanya_haizhe.jpg',
    '鱼煲': 'sanya_yuba.jpg',
    '羊栏酸鱼汤': 'sanya_yang.jpg',
    '黎家竹筒饭': 'sanya_li.jpg',
    '海南腌面': 'sanya_mian.jpg',
    '鸡屎藤粑仔': 'sanya_ji.jpg',
    '红糖年糕': 'sanya_tang.jpg',
    '椰子冻': 'sanya_yezidong.jpg',
    '港门粉': 'sanya_gangmen.jpg',
    '藤桥排骨': 'sanya_tengqiao.jpg',
    '荔枝木烤鸭': 'sanya_lizhi.jpg',
    '海鲜火锅': 'sanya_haixianhuoguo.jpg',
    '椰奶清补凉': 'sanya_yenai.jpg',
    '黄流老鸭': 'sanya_huangliu.jpg',
    '海南大虾': 'sanya_haidaxia.jpg',
    '海南海胆': 'sanya_haidan.jpg',
    '椰子鸡': 'sanya_yeziji.jpg',
    
    // ===== 青岛美食 (30+) =====
    '辣炒蛤蜊': 'qingdao_lachao.jpg',
    '鲅鱼水饺': 'qingdao_baoyu.jpg',
    '流亭猪蹄': 'qingdao_liuting.jpg',
    '海肠捞饭': 'qingdao_haichang.jpg',
    '青岛脂渣': 'qingdao_lazha.jpg',
    '李村戳子肉': 'qingdao_chuozi.jpg',
    '海菜凉粉': 'qingdao_haicai.jpg',
    '排骨米饭': 'qingdao_paigu.jpg',
    '青岛锅贴': 'qingdao_guotie.jpg',
    '崂山菇炖鸡': 'qingdao_laoshan.jpg',
    '鲍鱼': 'qingdao_baoyu2.jpg',
    '海参': 'qingdao_haican.jpg',
    '大虾': 'qingdao_xia.jpg',
    '海带': 'qingdao_haidai.jpg',
    '黄花鱼': 'qingdao_yu.jpg',
    '青岛大包': 'qingdao_mian.jpg',
    '油条': 'qingdao_you.jpg',
    '豆腐脑': 'qingdao_doufu.jpg',
    '烧饼': 'qingdao_shaobing.jpg',
    '煎饼果子': 'qingdao_bing.jpg',
    '海鲜大咖': 'qingdao_haixiandaka.jpg',
    '烤鱿鱼': 'qingdao_kaoyouyu.jpg',
    '海鲜馄饨': 'qingdao_haixianhun.jpg',
    '酱猪蹄': 'qingdao_jiangzhuti.jpg',
    '葱油饼': 'qingdao_congyoubing.jpg',
    '海鲜疙瘩汤': 'qingdao_gedatang.jpg',
    '炸蛎黄': 'qingdao_zhalihuang.jpg',
    '原壳鲍鱼': 'qingdao_yuanke.jpg',
    '肉末海参': 'qingdao_roumoshen.jpg',
    
    // ===== 南京美食 (30+) =====
    '鸭血粉丝汤': 'nanjing_yaxue.jpg',
    '牛肉锅贴': 'nanjing_guotie.jpg',
    '盐水鸭': 'nanjing_yanshui.jpg',
    '南京烤鸭': 'nanjing_kaoya.jpg',
    '皮肚面': 'nanjing_pidu.jpg',
    '鸡鸣汤包': 'nanjing_tangbao.jpg',
    '秦淮八绝': 'nanjing_shao.jpg',
    '黄桥烧饼': 'nanjing_huangqiao.jpg',
    '开洋干丝': 'nanjing_gansi.jpg',
    '牛肉汤': 'nanjing_niurou.jpg',
    '臭豆腐': 'nanjing_doufu.jpg',
    '麻辣小龙虾': 'nanjing_mala.jpg',
    '糖芋苗': 'nanjing_tang.jpg',
    '赤豆元宵': 'nanjing_chi.jpg',
    '梅花糕': 'nanjing_mei.jpg',
    '酥烧饼': 'nanjing_su.jpg',
    '菜包': 'nanjing_cai.jpg',
    '肉包': 'nanjing_rou.jpg',
    '美龄粥': 'nanjing_zhou.jpg',
    '桂花糕': 'nanjing_guihua.jpg',
    '如意回卤干': 'nanjing_ruyi.jpg',
    '什锦豆腐涝': 'nanjing_shijin.jpg',
    '状元豆': 'nanjing_zhuangyuan.jpg',
    '旺鸡蛋': 'nanjing_wangjidan.jpg',
    '活珠子': 'nanjing_huozhuzi.jpg',
    '洪蓝玉带糕': 'nanjing_honglan.jpg',
    '东坝豆腐干': 'nanjing_dongba.jpg',
    '南京鸭血粉丝': 'nanjing_yaxue2.jpg',
    '鸭血粉丝': 'nanjing_yaxue3.jpg',
    
    // ===== 武汉美食 (30+) =====
    '热干面': 'wuhan_regan.jpg',
    '三鲜豆皮': 'wuhan_doupi.jpg',
    '鲜鱼糊汤粉': 'wuhan_hutang.jpg',
    '油焖小龙虾': 'wuhan_longxia.jpg',
    '清蒸武昌鱼': 'wuhan_wuchang.jpg',
    '排骨藕汤': 'wuhan_outang.jpg',
    '面窝': 'wuhan_mianwo.jpg',
    '煎饺': 'wuhan_jianjiao.jpg',
    '重油烧麦': 'wuhan_shaomai.jpg',
    '汤包': 'wuhan_tangbao.jpg',
    '鸡蛋灌饼': 'wuhan_jidan.jpg',
    '油条': 'wuhan_you.jpg',
    '包子': 'wuhan_baozi.jpg',
    '馒头': 'wuhan_mantou.jpg',
    '花饭': 'wuhan_huafan.jpg',
    '凉面': 'wuhan_liang.jpg',
    '米粉': 'wuhan_mifen.jpg',
    '粥': 'wuhan_zhou.jpg',
    '牛肉面': 'wuhan_niurou.jpg',
    '豆腐脑': 'wuhan_doufu.jpg',
    '欢喜坨': 'wuhan_huanxitu.jpg',
    '糯米鸡': 'wuhan_nuomiji.jpg',
    '鸡冠饺': 'wuhan_jiguanjiao.jpg',
    '糯米包油条': 'wuhan_nuomiyoutiao.jpg',
    '汽水包': 'wuhan_qishuibao.jpg',
    '鸭脖': 'wuhan_yabo.jpg',
    '周黑鸭': 'wuhan_zhouheiya.jpg',
    '精武鸭脖': 'wuhan_jingwuyabo.jpg',
    '四季美汤包': 'wuhan_sijimei.jpg',
    '蔡林记热干面': 'wuhan_cailinji.jpg',
    
    // ===== 长沙美食 (30+) =====
    '长沙臭豆腐': 'changsha_choudoufu.jpg',
    '糖油粑粑': 'changsha_tangyou.jpg',
    '口味虾': 'changsha_kouweixia.jpg',
    '湖南酱板鸭': 'changsha_jiangban.jpg',
    '长沙米粉': 'changsha_mifen.jpg',
    '德园包子': 'changsha_deyuan.jpg',
    '龙脂猪血': 'changsha_longzhi.jpg',
    '嗍螺': 'changsha_suoluo.jpg',
    '红烧猪脚': 'changsha_hongshao.jpg',
    '口味蟹': 'changsha_kouweixie.jpg',
    '辣椒炒肉': 'changsha_labi.jpg',
    '剁椒鱼头': 'changsha_dongcai.jpg',
    '蒸菜': 'changsha_zheng.jpg',
    '刮凉粉': 'changsha_liangfen.jpg',
    '油炸串串': 'changsha_youzha.jpg',
    '茶颜悦色': 'changsha_cha.jpg',
    '小龙虾': 'changsha_xiaolong.jpg',
    '甜酒冲蛋': 'changsha_tian.jpg',
    '毛氏红烧肉': 'changsha_mao.jpg',
    '冰粉': 'changsha_bing.jpg',
    '姊妹团子': 'changsha_zimei.jpg',
    '荷兰粉': 'changsha_helan.jpg',
    '口味蛇': 'changsha_kouweishe.jpg',
    '麻辣子鸡': 'changsha_malaziji.jpg',
    '三层套鸡': 'changsha_sanceng.jpg',
    '长沙糕点': 'changsha_gaodian.jpg',
    '浏阳蒸菜': 'changsha_liuyang.jpg',
    '宁乡口味蛇': 'changsha_ningxiang.jpg',
    '长沙盒饭': 'changsha_hefan.jpg',
    '湘西外婆菜': 'changsha_xiangxia.jpg',
    
    // ===== 深圳美食 (30+) =====
    '光明乳鸽': 'shenzhen_guangming.jpg',
    '公明烧鹅': 'shenzhen_gongming.jpg',
    '深井烧鹅': 'shenzhen_shen.jpg',
    '沙井蚝': 'shenzhen_shae.jpg',
    '南头荔枝': 'shenzhen_nantou.jpg',
    '福田云吞': 'shenzhen_futian.jpg',
    '罗湖肠粉': 'shenzhen_luohu.jpg',
    '龙岗鸡': 'shenzhen_longgang.jpg',
    '宝安腊鸭': 'shenzhen_baoan.jpg',
    '盐田海鲜': 'shenzhen_yantian.jpg',
    '大梅沙海鲜': 'shenzhen_dameisha.jpg',
    '小梅沙烧烤': 'shenzhen_xiaomeisha.jpg',
    '春满园早茶': 'shenzhen_chun.jpg',
    '点都德': 'shenzhen_dian.jpg',
    '陶陶居': 'shenzhen_taotaoju.jpg',
    '莲香楼': 'shenzhen_lianxiang.jpg',
    '广州酒家': 'shenzhen_guangzhou.jpg',
    '泮溪酒家': 'shenzhen_panxi.jpg',
    '北园酒家': 'shenzhen_beiyuan.jpg',
    '东江盐焗鸡': 'shenzhen_dongjiang.jpg',
    '猪肚鸡': 'shenzhen_zhuduji.jpg',
    '椰子鸡': 'shenzhen_yeziji.jpg',
    '潮汕牛肉火锅': 'shenzhen_chaoshan.jpg',
    '广式早茶': 'shenzhen_guangshi.jpg',
    '肠粉': 'shenzhen_changfen.jpg',
    '叉烧': 'shenzhen_chashao.jpg',
    '烧鹅饭': 'shenzhen_shaoe.jpg',
    '港式奶茶': 'shenzhen_naicha.jpg',
    '鸡蛋仔': 'shenzhen_jidan.jpg',
    '菠萝油': 'shenzhen_boluoyou.jpg',
    
    // ===== 桂林美食 (30+) =====
    '桂林米粉': 'guilin_mifen.jpg',
    '荔浦扣肉': 'guilin_lipu.jpg',
    '阳朔啤酒鱼': 'guilin_pijiu.jpg',
    '全州醋血鸭': 'guilin_quanzhou.jpg',
    '平乐十八酿': 'guilin_pingyue.jpg',
    '灵川狗肉': 'guilin_lingchuan.jpg',
    '桂林马肉米粉': 'guilin_marou.jpg',
    '全州禾花鱼': 'guilin_hehua.jpg',
    '阳朔田螺酿': 'guilin_yangshuo.jpg',
    '恭城油茶': 'guilin_gongcheng.jpg',
    '龙脊竹筒饭': 'guilin_longsheng.jpg',
    '兴安白果': 'guilin_xingan.jpg',
    '阳朔糍粑': 'guilin_yangshuo2.jpg',
    '灌阳红薯粉': 'guilin_guanyan.jpg',
    '资源竹笋': 'guilin_ziyuan.jpg',
    '永福罗汉果': 'guilin_yongfu.jpg',
    '平乐沙田柚': 'guilin_pingle.jpg',
    '恭城月柿': 'guilin_gongcheng2.jpg',
    '荔浦芋': 'guilin_li.jpg',
    '桂林三花酒': 'guilin_sanhuajiu.jpg',
    '桂林田螺': 'guilin_tianluo.jpg',
    '马蹄糕': 'guilin_matigao.jpg',
    '桂花糕': 'guilin_guihuagao.jpg',
    '尼姑素面': 'guilin_nigusu.jpg',
    '桂林松糕': 'guilin_songgao.jpg',
    '桂林水糍粑': 'guilin_shuiciba.jpg',
    '桂林腐乳': 'guilin_furu.jpg',
    '桂林辣椒酱': 'guilin_lajiao.jpg',
    '阳朔啤酒': 'guilin_pijiu2.jpg',
    '罗汉果': 'guilin_luohanguo.jpg',
    
    // ===== 张家界美食 (30+) =====
    '土家三下锅': 'zhangjiajie_sanxiaguo.jpg',
    '岩耳炖鸡': 'zhangjiajie_yaner.jpg',
    '土家腊肉': 'zhangjiajie_larou.jpg',
    '土家血豆腐': 'zhangjiajie_xuedoufu.jpg',
    '蒿子粑粑': 'zhangjiajie_haozi.jpg',
    '合渣': 'zhangjiajie_hezha.jpg',
    '草帽面': 'zhangjiajie_caomao.jpg',
    '糖油粑粑': 'zhangjiajie_tangyou.jpg',
    '土家粉蒸肉': 'zhangjiajie_tujia.jpg',
    '社饭': 'zhangjiajie_shefan.jpg',
    '糍粑': 'zhangjiajie_ciba.jpg',
    '腊猪蹄': 'zhangjiajie_la.jpg',
    '土家香肠': 'zhangjiajie_xiangchang.jpg',
    '玉米饭': 'zhangjiajie_yumi.jpg',
    '张家界米粉': 'zhangjiajie_mifen.jpg',
    '豆腐脑': 'zhangjiajie_doufu.jpg',
    '油条': 'zhangjiajie_you.jpg',
    '包子': 'zhangjiajie_baozi.jpg',
    '馒头': 'zhangjiajie_mantou.jpg',
    '粥': 'zhangjiajie_zhou.jpg',
    '葛根粉': 'zhangjiajie_gegen.jpg',
    '猕猴桃': 'zhangjiajie_mihoutao.jpg',
    '岩耳': 'zhangjiajie_yaner2.jpg',
    '杜仲茶': 'zhangjiajie_duzhong.jpg',
    '张家界酒': 'zhangjiajie_zhangjiajiejiu.jpg',
    '野味': 'zhangjiajie_yewei.jpg',
    '土家鸡': 'zhangjiajie_tuji.jpg',
    '土家蒸肉': 'zhangjiajie_tujiazhengrou.jpg',
    '土家腌菜': 'zhangjiajie_tujiayancai.jpg',
    '土家腊八': 'zhangjiajie_tujialaba.jpg',
    
    // ===== 黄山美食 (30+) =====
    '徽州臭鳜鱼': 'huangshan_chouguiyu.jpg',
    '徽州毛豆腐': 'huangshan_maodoufu.jpg',
    '黄山烧饼': 'huangshan_shaobing.jpg',
    '徽州刀板香': 'huangshan_daoban.jpg',
    '问政山笋': 'huangshan_wenzheng.jpg',
    '黄山双石': 'huangshan_shuangshi.jpg',
    '五城茶干': 'huangshan_wucheng.jpg',
    '黄山炖鸽': 'huangshan_dunge.jpg',
    '徽州圆子': 'huangshan_yuanzi.jpg',
    '黄山蕨菜': 'huangshan_juecai.jpg',
    '红烧臭鳜鱼': 'huangshan_hongshao.jpg',
    '问政山笋煲': 'huangshan_wenzheng2.jpg',
    '胡适一品锅': 'huangshan_hushi.jpg',
    '火腿炖甲鱼': 'huangshan_huotui.jpg',
    '沙地马蹄鳖': 'huangshan_shadi.jpg',
    '石耳炖石鸡': 'huangshan_shier.jpg',
    '挞粿': 'huangshan_ta.jpg',
    '毛豆腐': 'huangshan_mao.jpg',
    '油煎毛豆腐': 'huangshan_you.jpg',
    '徽州裹粽': 'huangshan_guozong.jpg',
    '徽州状元饭': 'huangshan_zhuangyuan.jpg',
    '虎皮毛豆腐': 'huangshan_humaodoufu.jpg',
    '徽州石鸡': 'huangshan_shiji.jpg',
    '徽州桃脂烧肉': 'huangshan_taozhi.jpg',
    '徽州蒸鸡': 'huangshan_zhengji.jpg',
    '黟县腊八豆腐': 'huangshan_yixian.jpg',
    '徽州臭豆腐': 'huangshan_chou.jpg',
    '黄山猕猴桃': 'huangshan_mihoutao.jpg',
    
    // ===== 九寨沟美食 (30+) =====
    '九寨柿饼': 'jiuzhaigou_zhaxibing.jpg',
    '酸菜面块': 'jiuzhaigou_suancai.jpg',
    '洋芋糍粑': 'jiuzhaigou_yangyu.jpg',
    '酥油茶': 'jiuzhaigou_suyou.jpg',
    '藏族血肠': 'jiuzhaigou_xuechang.jpg',
    '牦牛肉干': 'jiuzhaigou_maoniu.jpg',
    '奶渣包子': 'jiuzhaigou_naizha.jpg',
    '藏民奶制品': 'jiuzhaigou_niuzai.jpg',
    '荞麦面食': 'jiuzhaigou_qiaomai.jpg',
    '豌杂面': 'jiuzhaigou_wanza.jpg',
    '糌粑': 'jiuzhaigou_zanba.jpg',
    '牦牛肉': 'jiuzhaigou_maoniurou.jpg',
    '荞麦饼': 'jiuzhaigou_qiaomai2.jpg',
    '青稞酒': 'jiuzhaigou_qingke.jpg',
    '酸奶': 'jiuzhaigou_suannai.jpg',
    '奶茶': 'jiuzhaigou_nai.jpg',
    '羊肉汤': 'jiuzhaigou_yang.jpg',
    '牛肉汤': 'jiuzhaigou_niu.jpg',
    '面条': 'jiuzhaigou_mian.jpg',
    '米饭': 'jiuzhaigou_fan.jpg',
    '手抓肉': 'jiuzhaigou_shouzhua.jpg',
    '烤全羊': 'jiuzhaigou_kaoquanyang.jpg',
    '藏式火锅': 'jiuzhaigou_zanghuoguo.jpg',
    '人参果饭': 'jiuzhaigou_rencanguo.jpg',
    '虫草鸭': 'jiuzhaigou_chongcao.jpg',
    '九寨黄瓜': 'jiuzhaigou_huanggua.jpg',
    '羊肉泡馍': 'jiuzhaigou_yangroupaomo.jpg',
    '风干牛肉': 'jiuzhaigou_niurougan.jpg',
    '奶皮': 'jiuzhaigou_naijiao.jpg',
    '油炸酸奶': 'jiuzhaigou_youzha.jpg',
    
    // ===== 大理美食 (30+) =====
    '烤乳扇': 'dali_rushan.jpg',
    '大理生皮': 'dali_shengpi.jpg',
    '大理酸辣鱼': 'dali_suanla.jpg',
    '喜洲粑粑': 'dali_xizhou.jpg',
    '凉鸡米线': 'dali_liangji.jpg',
    '砂锅鱼': 'dali_shaguo.jpg',
    '巍山耙肉饵丝': 'dali_weishan.jpg',
    '雕梅扣肉': 'dali_diaomei.jpg',
    '永平黄焖鸡': 'dali_huangmen.jpg',
    '雕梅酒': 'dali_diaomei2.jpg',
    '白族土八碗': 'dali_bajian.jpg',
    '大理洱海砂锅鱼': 'dali_erhai.jpg',
    '剑川八大碗': 'dali_jianchuan.jpg',
    '云龙诺邓火腿': 'dali_nuodeng.jpg',
    '南涧锅巴油粉': 'dali_nanjian.jpg',
    '漾濞卷粉': 'dali_yangbi.jpg',
    '宾川韭菜腌菜': 'dali_binxuan.jpg',
    '烤饵块': 'dali_kaoer.jpg',
    '大理凉粉': 'dali_dali.jpg',
    '耙肉饵丝': 'dali_pa.jpg',
    '大理锅锅菜': 'dali_guoguo.jpg',
    '白族三道茶': 'dali_baixizhu.jpg',
    '大理梅子': 'dali_meizi.jpg',
    '双乳扇': 'dali_shuangrufan.jpg',
    '大理黑桂鱼': 'dali_heguiyu.jpg',
    '苍山雪鱼': 'dali_cangshan.jpg',
    '大理雪茶': 'dali_xuecha.jpg',
    '西瓜酱': 'dali_xiguajiao.jpg',
    '大理鱼粥': 'dali_yuzhou.jpg',
    '羊奶乳扇': 'dali_yangnai.jpg',
    
    // ===== 丽江美食 (30+) =====
    '腊排骨火锅': 'lijiang_larou.jpg',
    '水性杨花': 'lijiang_shuixing.jpg',
    '丽江粑粑': 'lijiang_baba.jpg',
    '纳西烤肉': 'lijiang_naxi.jpg',
    '鸡豆凉粉': 'lijiang_jidou.jpg',
    '包浆豆腐': 'lijiang_baojiang.jpg',
    '黑山羊火锅': 'lijiang_hei.jpg',
    '松茸': 'lijiang_songrong.jpg',
    '纳西烤鱼': 'lijiang_naxi2.jpg',
    '洋芋鸡': 'lijiang_yang.jpg',
    '汽锅鸡': 'lijiang_qi.jpg',
    '过桥米线': 'lijiang_guo.jpg',
    '酸汤鱼': 'lijiang_suan.jpg',
    '凉粉': 'lijiang_liang.jpg',
    '米线': 'lijiang_mifen.jpg',
    '饵丝': 'lijiang_er.jpg',
    '小白菜': 'lijiang_xiaobaicai.jpg',
    '青菜': 'lijiang_qingcai.jpg',
    '土豆': 'lijiang_tudou.jpg',
    '红薯': 'lijiang_hongshu.jpg',
    '米灌肠': 'lijiang_miguanchang.jpg',
    '酥油茶': 'lijiang_suyoucha.jpg',
    '雪茶': 'lijiang_xuecha.jpg',
    '螺旋藻': 'lijiang_luoxuanzao.jpg',
    '东巴烤鱼': 'lijiang_dongba.jpg',
    '三文鱼': 'lijiang_sanwenyu.jpg',
    '野生菌': 'lijiang_yeshengjun.jpg',
    '鲜花饼': 'lijiang_xianhuabing.jpg',
    '丽江腌菜': 'lijiang_lijiangyan.jpg',
    '丽江酒': 'lijiang_lijiangjiu.jpg',
  }
  const imageName = imageMap[foodName]
  if (imageName) {
    // 添加时间戳参数防止缓存，确保图片更新后能立即显示
    const timestamp = new Date().getTime()
    return `/images/foods/${imageName}?v=${timestamp}`
  }
  // 如果没有对应图片，返回 null 使用城市图片
  return null
}

// 生成美食数据的辅助函数
const generateFoodsData = () => {
  const foods = []
  let id = 1
  
  // 北京美食 (30个)
  const beijingFoods = [
    { name: '北京烤鸭', cuisine_type: '京菜', rating: 4.9, price_range: '¥80-150', is_featured: true, tags: ['必吃', '招牌'], description: '北京最著名的传统名菜，皮脆肉嫩' },
    { name: '老北京炸酱面', cuisine_type: '小吃', rating: 4.7, price_range: '¥20-40', is_featured: false, tags: ['特色'], description: '老北京特色面食' },
    { name: '涮羊肉', cuisine_type: '火锅', rating: 4.7, price_range: '¥60-100', is_featured: false, tags: ['特色'], description: '老北京传统铜锅涮肉' },
    { name: '豆汁儿', cuisine_type: '小吃', rating: 4.2, price_range: '¥5-10', is_featured: false, tags: ['特色'], description: '老北京传统饮品' },
    { name: '卤煮火烧', cuisine_type: '小吃', rating: 4.5, price_range: '¥25-40', is_featured: false, tags: ['特色'], description: '北京传统小吃' },
    { name: '爆肚', cuisine_type: '小吃', rating: 4.6, price_range: '¥30-50', is_featured: false, tags: ['特色'], description: '北京传统小吃' },
    { name: '门钉肉饼', cuisine_type: '小吃', rating: 4.5, price_range: '¥10-20', is_featured: false, tags: ['特色'], description: '北京传统小吃' },
    { name: '炙子烤肉', cuisine_type: '烧烤', rating: 4.6, price_range: '¥60-100', is_featured: false, tags: ['特色'], description: '北京特色烤肉' },
    { name: '炒肝', cuisine_type: '小吃', rating: 4.4, price_range: '¥15-25', is_featured: false, tags: ['特色'], description: '北京传统小吃' },
    { name: '豌豆黄', cuisine_type: '甜品', rating: 4.5, price_range: '¥10-20', is_featured: false, tags: ['特色'], description: '北京传统甜品' },
    { name: '炸灌肠', cuisine_type: '小吃', rating: 4.3, price_range: '¥10-20', is_featured: false, tags: ['特色'], description: '北京传统小吃' },
    { name: '麻酱糖饼', cuisine_type: '小吃', rating: 4.5, price_range: '¥10-20', is_featured: false, tags: ['特色'], description: '北京传统小吃' },
    { name: '焦圈', cuisine_type: '小吃', rating: 4.4, price_range: '¥5-10', is_featured: false, tags: ['特色'], description: '北京传统早餐' },
    { name: '艾窝窝', cuisine_type: '甜品', rating: 4.5, price_range: '¥10-20', is_featured: false, tags: ['特色'], description: '北京传统甜品' },
    { name: '玫瑰饼', cuisine_type: '甜品', rating: 4.4, price_range: '¥15-25', is_featured: false, tags: ['特色'], description: '北京传统糕点' },
    { name: '牛舌饼', cuisine_type: '甜品', rating: 4.3, price_range: '¥10-20', is_featured: false, tags: ['特色'], description: '北京传统糕点' },
    { name: '糖葫芦', cuisine_type: '甜品', rating: 4.6, price_range: '¥10-20', is_featured: false, tags: ['特色'], description: '北京传统小吃' },
    { name: '茯苓饼', cuisine_type: '甜品', rating: 4.4, price_range: '¥15-25', is_featured: false, tags: ['特色'], description: '北京传统糕点' },
    { name: '正明斋糕点', cuisine_type: '甜品', rating: 4.5, price_range: '¥30-60', is_featured: false, tags: ['特色'], description: '北京老字号糕点' },
    { name: '京八件', cuisine_type: '甜品', rating: 4.6, price_range: '¥50-100', is_featured: false, tags: ['特色'], description: '北京传统糕点礼盒' },
    { name: '驴打滚', cuisine_type: '甜品', rating: 4.5, price_range: '¥10-20', is_featured: false, tags: ['特色'], description: '北京传统糕点' },
    { name: '奶油炸糕', cuisine_type: '甜品', rating: 4.4, price_range: '¥15-25', is_featured: false, tags: ['特色'], description: '北京传统甜品' },
    { name: '面茶', cuisine_type: '小吃', rating: 4.3, price_range: '¥8-15', is_featured: false, tags: ['特色'], description: '北京传统早餐' },
    { name: '小吊梨汤', cuisine_type: '饮品', rating: 4.4, price_range: '¥15-25', is_featured: false, tags: ['特色'], description: '北京传统饮品' },
    { name: '葱烧海参', cuisine_type: '京菜', rating: 4.6, price_range: '¥120-200', is_featured: false, tags: ['特色'], description: '北京高档名菜' },
    { name: '京酱肉丝', cuisine_type: '京菜', rating: 4.5, price_range: '¥40-70', is_featured: false, tags: ['特色'], description: '北京传统菜' },
    { name: '九转大肠', cuisine_type: '鲁菜', rating: 4.4, price_range: '¥50-90', is_featured: false, tags: ['特色'], description: '北京传统名菜' },
    { name: '枣钱饼', cuisine_type: '甜品', rating: 4.3, price_range: '¥12-22', is_featured: false, tags: ['特色'], description: '北京传统糕点' },
    { name: '吹糖人', cuisine_type: '甜品', rating: 4.2, price_range: '¥15-30', is_featured: false, tags: ['特色'], description: '北京传统手艺' },
    { name: '柳泉居面点', cuisine_type: '小吃', rating: 4.4, price_range: '¥20-40', is_featured: false, tags: ['特色'], description: '北京老字号' },
  ]
  beijingFoods.forEach(food => foods.push({ id: id++, city: '北京', ...food }))
  
  // 上海美食 (30个)
  const shanghaiFoods = [
    { name: '小笼包', cuisine_type: '小吃', rating: 4.9, price_range: '¥15-30', is_featured: true, tags: ['必吃', '特色'], description: '上海传统小吃，汤汁鲜美' },
    { name: '生煎包', cuisine_type: '小吃', rating: 4.6, price_range: '¥10-25', is_featured: false, tags: ['特色'], description: '上海特色早餐' },
    { name: '本帮红烧肉', cuisine_type: '本帮菜', rating: 4.8, price_range: '¥50-80', is_featured: true, tags: ['必吃'], description: '上海经典本帮菜，肥而不腻' },
    { name: '油爆虾', cuisine_type: '本帮菜', rating: 4.6, price_range: '¥60-100', is_featured: false, tags: ['特色'], description: '上海特色菜' },
    { name: '脆牛肉', cuisine_type: '本帮菜', rating: 4.5, price_range: '¥50-90', is_featured: false, tags: ['特色'], description: '上海特色菜' },
    { name: '糟钵头', cuisine_type: '本帮菜', rating: 4.4, price_range: '¥40-70', is_featured: false, tags: ['特色'], description: '上海传统菜' },
    { name: '开洋葱油拌面', cuisine_type: '小吃', rating: 4.5, price_range: '¥15-30', is_featured: false, tags: ['特色'], description: '上海特色面食' },
    { name: '糖醋小排', cuisine_type: '本帮菜', rating: 4.6, price_range: '¥40-70', is_featured: false, tags: ['特色'], description: '上海经典菜' },
    { name: '三黄鸡', cuisine_type: '本帮菜', rating: 4.5, price_range: '¥40-70', is_featured: false, tags: ['特色'], description: '上海特色菜' },
    { name: '粢饭糕', cuisine_type: '小吃', rating: 4.4, price_range: '¥5-10', is_featured: false, tags: ['特色'], description: '上海传统早餐' },
    { name: '臭豆腐', cuisine_type: '小吃', rating: 4.3, price_range: '¥8-15', is_featured: false, tags: ['特色'], description: '上海特色小吃' },
    { name: '咖喱牛肉汤', cuisine_type: '小吃', rating: 4.4, price_range: '¥15-25', is_featured: false, tags: ['特色'], description: '上海传统汤品' },
    { name: '排骨年糕', cuisine_type: '小吃', rating: 4.5, price_range: '¥20-35', is_featured: false, tags: ['特色'], description: '上海特色小吃' },
    { name: '四喜烤麸', cuisine_type: '本帮菜', rating: 4.4, price_range: '¥25-40', is_featured: false, tags: ['特色'], description: '上海传统菜' },
    { name: '上海香肠', cuisine_type: '小吃', rating: 4.3, price_range: '¥20-40', is_featured: false, tags: ['特色'], description: '上海传统小吃' },
    { name: '大馄饨', cuisine_type: '小吃', rating: 4.5, price_range: '¥15-25', is_featured: false, tags: ['特色'], description: '上海传统小吃' },
    { name: '豆沙包', cuisine_type: '甜品', rating: 4.3, price_range: '¥5-10', is_featured: false, tags: ['特色'], description: '上海传统点心' },
    { name: '绿豆糕', cuisine_type: '甜品', rating: 4.4, price_range: '¥15-25', is_featured: false, tags: ['特色'], description: '上海传统糕点' },
    { name: '擂沙汤圆', cuisine_type: '甜品', rating: 4.5, price_range: '¥15-25', is_featured: false, tags: ['特色'], description: '上海传统甜品' },
    { name: '蟹壳黄', cuisine_type: '小吃', rating: 4.4, price_range: '¥10-20', is_featured: false, tags: ['特色'], description: '上海传统烧饼' },
    { name: '南翔小笼', cuisine_type: '小吃', rating: 4.8, price_range: '¥20-40', is_featured: false, tags: ['特色'], description: '上海著名小笼包' },
    { name: '鲜肉月饼', cuisine_type: '甜品', rating: 4.5, price_range: '¥8-15', is_featured: false, tags: ['特色'], description: '上海中秋特色' },
    { name: '梨膏糖', cuisine_type: '甜品', rating: 4.3, price_range: '¥20-40', is_featured: false, tags: ['特色'], description: '上海传统糖果' },
    { name: '五香豆', cuisine_type: '小吃', rating: 4.2, price_range: '¥10-20', is_featured: false, tags: ['特色'], description: '上海传统小吃' },
    { name: '高桥松饼', cuisine_type: '甜品', rating: 4.4, price_range: '¥15-30', is_featured: false, tags: ['特色'], description: '上海传统糕点' },
    { name: '条头糕', cuisine_type: '甜品', rating: 4.3, price_range: '¥5-10', is_featured: false, tags: ['特色'], description: '上海传统糕点' },
    { name: '油豆腐线粉汤', cuisine_type: '小吃', rating: 4.2, price_range: '¥12-22', is_featured: false, tags: ['特色'], description: '上海传统汤品' },
    { name: '沈大成糕点', cuisine_type: '甜品', rating: 4.5, price_range: '¥20-40', is_featured: false, tags: ['特色'], description: '上海老字号' },
    { name: '国际饭店蝴蝶酥', cuisine_type: '甜品', rating: 4.6, price_range: '¥25-45', is_featured: false, tags: ['特色'], description: '上海网红糕点' },
    { name: '上海青', cuisine_type: '本帮菜', rating: 4.2, price_range: '¥15-30', is_featured: false, tags: ['特色'], description: '上海特色蔬菜' },
  ]
  shanghaiFoods.forEach(food => foods.push({ id: id++, city: '上海', ...food }))
  
  // 其他城市的美食数据生成函数
  const addCityFoods = (city, cityFoods) => {
    cityFoods.forEach(food => foods.push({ id: id++, city, ...food }))
  }
  
  // 西安美食 (30个)
  addCityFoods('西安', [
    { name: '羊肉泡馍', cuisine_type: '西北菜', rating: 4.8, price_range: '¥30-50', is_featured: true, tags: ['必吃', '特色'], description: '西安传统美食' },
    { name: '肉夹馍', cuisine_type: '小吃', rating: 4.8, price_range: '¥10-20', is_featured: true, tags: ['必吃', '特色'], description: '西安经典小吃' },
    { name: '凉皮', cuisine_type: '小吃', rating: 4.6, price_range: '¥8-15', is_featured: false, tags: ['特色'], description: '西安夏日美食' },
    { name: 'Biangbiang面', cuisine_type: '小吃', rating: 4.7, price_range: '¥15-25', is_featured: false, tags: ['特色'], description: '西安特色面食' },
    { name: '牛肉泡馍', cuisine_type: '西北菜', rating: 4.7, price_range: '¥32-52', is_featured: false, tags: ['特色'], description: '西安传统美食' },
    { name: '葫芦头', cuisine_type: '小吃', rating: 4.5, price_range: '¥25-40', is_featured: false, tags: ['特色'], description: '西安传统小吃' },
    { name: '粉蒸肉', cuisine_type: '小吃', rating: 4.4, price_range: '¥20-35', is_featured: false, tags: ['特色'], description: '西安传统菜' },
    { name: '臊子面', cuisine_type: '小吃', rating: 4.5, price_range: '¥15-25', is_featured: false, tags: ['特色'], description: '西安特色面食' },
    { name: '油泼面', cuisine_type: '小吃', rating: 4.6, price_range: '¥15-25', is_featured: false, tags: ['特色'], description: '西安特色面食' },
    { name: '锅盔', cuisine_type: '小吃', rating: 4.3, price_range: '¥10-20', is_featured: false, tags: ['特色'], description: '西安传统面食' },
    { name: '胡辣汤', cuisine_type: '小吃', rating: 4.5, price_range: '¥8-15', is_featured: false, tags: ['特色'], description: '西安早餐首选' },
    { name: '甑糕', cuisine_type: '甜品', rating: 4.4, price_range: '¥10-20', is_featured: false, tags: ['特色'], description: '西安传统甜品' },
    { name: '灌汤包', cuisine_type: '小吃', rating: 4.5, price_range: '¥15-30', is_featured: false, tags: ['特色'], description: '西安特色小吃' },
    { name: '烧饼', cuisine_type: '小吃', rating: 4.2, price_range: '¥5-10', is_featured: false, tags: ['特色'], description: '西安传统面食' },
    { name: '腊汁肉', cuisine_type: '小吃', rating: 4.5, price_range: '¥20-35', is_featured: false, tags: ['特色'], description: '西安传统菜' },
    { name: '水盆羊肉', cuisine_type: '西北菜', rating: 4.6, price_range: '¥35-55', is_featured: false, tags: ['特色'], description: '西安传统美食' },
    { name: '黄桂柿子饼', cuisine_type: '甜品', rating: 4.3, price_range: '¥10-20', is_featured: false, tags: ['特色'], description: '西安传统糕点' },
    { name: '酸梅汤', cuisine_type: '饮品', rating: 4.4, price_range: '¥8-15', is_featured: false, tags: ['特色'], description: '西安传统饮品' },
    { name: '冰峰汽水', cuisine_type: '饮品', rating: 4.3, price_range: '¥5-8', is_featured: false, tags: ['特色'], description: '西安特色饮料' },
    { name: '铜锣烧', cuisine_type: '甜品', rating: 4.1, price_range: '¥8-15', is_featured: false, tags: ['特色'], description: '西安传统糕点' },
    { name: '肉丸糊辣汤', cuisine_type: '小吃', rating: 4.4, price_range: '¥10-18', is_featured: false, tags: ['特色'], description: '西安特色早餐' },
    { name: '小炒泡馍', cuisine_type: '西北菜', rating: 4.5, price_range: '¥28-48', is_featured: false, tags: ['特色'], description: '西安特色菜' },
    { name: '南瓜盖被', cuisine_type: '小吃', rating: 4.2, price_range: '¥12-22', is_featured: false, tags: ['特色'], description: '西安传统小吃' },
    { name: '腊汁肉夹馍', cuisine_type: '小吃', rating: 4.6, price_range: '¥12-22', is_featured: false, tags: ['特色'], description: '西安经典小吃' },
    { name: '金线油塔', cuisine_type: '小吃', rating: 4.2, price_range: '¥15-25', is_featured: false, tags: ['特色'], description: '西安传统小吃' },
    { name: '石子馍', cuisine_type: '小吃', rating: 4.3, price_range: '¥10-20', is_featured: false, tags: ['特色'], description: '西安传统面食' },
    { name: '荞面饸饹', cuisine_type: '小吃', rating: 4.4, price_range: '¥12-20', is_featured: false, tags: ['特色'], description: '西安特色面食' },
    { name: '柿子糊塌', cuisine_type: '甜品', rating: 4.2, price_range: '¥8-15', is_featured: false, tags: ['特色'], description: '西安传统小吃' },
  ])
  
  // 成都美食 (30个)
  addCityFoods('成都', [
    { name: '麻辣香锅', cuisine_type: '川菜', rating: 4.8, price_range: '¥50-90', is_featured: true, tags: ['必吃', '辣'], description: '成都特色麻辣香锅' },
    { name: '麻婆豆腐', cuisine_type: '川菜', rating: 4.7, price_range: '¥25-45', is_featured: false, tags: ['经典'], description: '川菜经典代表' },
    { name: '四川火锅', cuisine_type: '火锅', rating: 4.9, price_range: '¥70-120', is_featured: true, tags: ['必吃', '辣'], description: '成都特色麻辣火锅' },
    { name: '宫保鸡丁', cuisine_type: '川菜', rating: 4.6, price_range: '¥30-50', is_featured: false, tags: ['经典'], description: '川菜经典代表' },
    { name: '水煮牛肉', cuisine_type: '川菜', rating: 4.7, price_range: '¥45-75', is_featured: false, tags: ['特色'], description: '成都特色菜' },
    { name: '回锅肉', cuisine_type: '川菜', rating: 4.6, price_range: '¥35-55', is_featured: false, tags: ['经典'], description: '川菜经典代表' },
    { name: '夫妻肺片', cuisine_type: '川菜', rating: 4.5, price_range: '¥30-50', is_featured: false, tags: ['特色'], description: '成都传统凉菜' },
    { name: '担担面', cuisine_type: '小吃', rating: 4.6, price_range: '¥12-20', is_featured: false, tags: ['特色'], description: '成都特色面食' },
    { name: '串串香', cuisine_type: '火锅', rating: 4.7, price_range: '¥40-70', is_featured: false, tags: ['特色'], description: '成都街头美食' },
    { name: '龙抄手', cuisine_type: '小吃', rating: 4.5, price_range: '¥15-30', is_featured: false, tags: ['特色'], description: '成都传统小吃' },
    { name: '钟水饺', cuisine_type: '小吃', rating: 4.5, price_range: '¥15-25', is_featured: false, tags: ['特色'], description: '成都传统小吃' },
    { name: '赖汤圆', cuisine_type: '甜品', rating: 4.4, price_range: '¥10-20', is_featured: false, tags: ['特色'], description: '成都传统甜品' },
    { name: '酸辣粉', cuisine_type: '小吃', rating: 4.5, price_range: '¥10-18', is_featured: false, tags: ['特色'], description: '成都街头美食' },
    { name: '冰粉', cuisine_type: '甜品', rating: 4.6, price_range: '¥8-15', is_featured: false, tags: ['特色'], description: '成都夏日甜品' },
    { name: '三大炮', cuisine_type: '甜品', rating: 4.3, price_range: '¥10-20', is_featured: false, tags: ['特色'], description: '成都传统小吃' },
    { name: '兔头', cuisine_type: '小吃', rating: 4.4, price_range: '¥12-20', is_featured: false, tags: ['特色'], description: '成都特色小吃' },
    { name: '肥肠粉', cuisine_type: '小吃', rating: 4.5, price_range: '¥15-25', is_featured: false, tags: ['特色'], description: '成都特色面食' },
    { name: '叶儿粑', cuisine_type: '小吃', rating: 4.3, price_range: '¥8-15', is_featured: false, tags: ['特色'], description: '成都传统小吃' },
    { name: '艾窝窝', cuisine_type: '甜品', rating: 4.2, price_range: '¥8-15', is_featured: false, tags: ['特色'], description: '成都传统甜品' },
    { name: '樟茶鸭', cuisine_type: '川菜', rating: 4.5, price_range: '¥50-80', is_featured: false, tags: ['特色'], description: '成都传统名菜' },
    { name: '钵钵鸡', cuisine_type: '小吃', rating: 4.6, price_range: '¥25-45', is_featured: false, tags: ['特色'], description: '成都街头美食' },
    { name: '蛋烘糕', cuisine_type: '甜品', rating: 4.4, price_range: '¥5-12', is_featured: false, tags: ['特色'], description: '成都传统小吃' },
    { name: '糖油果子', cuisine_type: '甜品', rating: 4.3, price_range: '¥5-10', is_featured: false, tags: ['特色'], description: '成都传统小吃' },
    { name: '甜水面', cuisine_type: '小吃', rating: 4.4, price_range: '¥10-18', is_featured: false, tags: ['特色'], description: '成都特色面食' },
    { name: '红油水饺', cuisine_type: '小吃', rating: 4.5, price_range: '¥12-22', is_featured: false, tags: ['特色'], description: '成都特色小吃' },
    { name: '冒菜', cuisine_type: '川菜', rating: 4.6, price_range: '¥30-55', is_featured: false, tags: ['特色'], description: '成都街头美食' },
    { name: '冷锅串串', cuisine_type: '火锅', rating: 4.5, price_range: '¥35-60', is_featured: false, tags: ['特色'], description: '成都特色火锅' },
    { name: '成都烧烤', cuisine_type: '烧烤', rating: 4.4, price_range: '¥40-80', is_featured: false, tags: ['特色'], description: '成都夜宵美食' },
    { name: '三哥田螺', cuisine_type: '小吃', rating: 4.3, price_range: '¥30-55', is_featured: false, tags: ['特色'], description: '成都特色小吃' },
    { name: '肖家河家常面', cuisine_type: '小吃', rating: 4.4, price_range: '¥12-22', is_featured: false, tags: ['特色'], description: '成都特色面食' },
  ])
  
  // 继续添加其他城市的美食...
  // 杭州美食 (30个)
  addCityFoods('杭州', [
    { name: '西湖醋鱼', cuisine_type: '浙菜', rating: 4.7, price_range: '¥60-100', is_featured: true, tags: ['必吃'], description: '杭州名菜' },
    { name: '东坡肉', cuisine_type: '浙菜', rating: 4.8, price_range: '¥40-70', is_featured: true, tags: ['经典'], description: '杭州传统名菜' },
    { name: '片儿川', cuisine_type: '小吃', rating: 4.5, price_range: '¥15-25', is_featured: false, tags: ['特色'], description: '杭州特色面食' },
    { name: '葱包桧儿', cuisine_type: '小吃', rating: 4.4, price_range: '¥8-15', is_featured: false, tags: ['特色'], description: '杭州传统小吃' },
    { name: '宋嫂鱼羹', cuisine_type: '浙菜', rating: 4.5, price_range: '¥40-65', is_featured: false, tags: ['特色'], description: '杭州传统名菜' },
    { name: '干炸响铃', cuisine_type: '浙菜', rating: 4.4, price_range: '¥25-40', is_featured: false, tags: ['特色'], description: '杭州传统菜' },
    { name: '荷叶粉蒸肉', cuisine_type: '浙菜', rating: 4.5, price_range: '¥35-55', is_featured: false, tags: ['特色'], description: '杭州特色菜' },
    { name: '小鸡酥', cuisine_type: '甜品', rating: 4.3, price_range: '¥15-25', is_featured: false, tags: ['特色'], description: '杭州传统糕点' },
    { name: '南宋定胜糕', cuisine_type: '甜品', rating: 4.4, price_range: '¥10-20', is_featured: false, tags: ['特色'], description: '杭州传统糕点' },
    { name: '知味小笼', cuisine_type: '小吃', rating: 4.6, price_range: '¥20-35', is_featured: false, tags: ['特色'], description: '杭州特色小笼包' },
    { name: '吴山酥油饼', cuisine_type: '小吃', rating: 4.4, price_range: '¥10-20', is_featured: false, tags: ['特色'], description: '杭州传统小吃' },
    { name: '杭州猫耳朵', cuisine_type: '小吃', rating: 4.3, price_range: '¥15-25', is_featured: false, tags: ['特色'], description: '杭州特色面食' },
    { name: '麻球王', cuisine_type: '甜品', rating: 4.2, price_range: '¥8-15', is_featured: false, tags: ['特色'], description: '杭州传统小吃' },
    { name: '龙井虾仁', cuisine_type: '浙菜', rating: 4.6, price_range: '¥50-80', is_featured: false, tags: ['特色'], description: '杭州特色菜' },
    { name: '叫花鸡', cuisine_type: '浙菜', rating: 4.5, price_range: '¥80-150', is_featured: false, tags: ['特色'], description: '杭州传统名菜' },
    { name: '白切鸡', cuisine_type: '浙菜', rating: 4.4, price_range: '¥35-60', is_featured: false, tags: ['特色'], description: '杭州特色菜' },
    { name: '糖桂花', cuisine_type: '甜品', rating: 4.3, price_range: '¥15-25', is_featured: false, tags: ['特色'], description: '杭州传统甜品' },
    { name: '绿豆糕', cuisine_type: '甜品', rating: 4.2, price_range: '¥10-20', is_featured: false, tags: ['特色'], description: '杭州传统糕点' },
    { name: '粢饭团', cuisine_type: '小吃', rating: 4.1, price_range: '¥8-15', is_featured: false, tags: ['特色'], description: '杭州传统早餐' },
    { name: '油条', cuisine_type: '小吃', rating: 4.0, price_range: '¥3-6', is_featured: false, tags: ['特色'], description: '杭州传统早餐' },
    { name: '西湖莼菜汤', cuisine_type: '浙菜', rating: 4.4, price_range: '¥30-50', is_featured: false, tags: ['特色'], description: '杭州特色汤品' },
    { name: '虾爆鳝面', cuisine_type: '小吃', rating: 4.5, price_range: '¥30-50', is_featured: false, tags: ['特色'], description: '杭州特色面食' },
    { name: '西湖藕粉', cuisine_type: '甜品', rating: 4.3, price_range: '¥15-25', is_featured: false, tags: ['特色'], description: '杭州传统甜品' },
    { name: '荷花酥', cuisine_type: '甜品', rating: 4.4, price_range: '¥20-35', is_featured: false, tags: ['特色'], description: '杭州传统糕点' },
    { name: '定胜糕', cuisine_type: '甜品', rating: 4.3, price_range: '¥8-15', is_featured: false, tags: ['特色'], description: '杭州传统糕点' },
    { name: '醋鱼', cuisine_type: '浙菜', rating: 4.2, price_range: '¥55-95', is_featured: false, tags: ['特色'], description: '杭州特色菜' },
    { name: '杭州小笼', cuisine_type: '小吃', rating: 4.5, price_range: '¥18-32', is_featured: false, tags: ['特色'], description: '杭州特色小笼包' },
    { name: '杭州油条', cuisine_type: '小吃', rating: 4.1, price_range: '¥3-6', is_featured: false, tags: ['特色'], description: '杭州传统早餐' },
    { name: '杭州粢饭', cuisine_type: '小吃', rating: 4.0, price_range: '¥8-15', is_featured: false, tags: ['特色'], description: '杭州传统早餐' },
  ])
  
  // 重庆美食 (30个)
  addCityFoods('重庆', [
    { name: '重庆火锅', cuisine_type: '火锅', rating: 4.9, price_range: '¥60-100', is_featured: true, tags: ['必吃', '辣'], description: '正宗重庆麻辣火锅' },
    { name: '重庆小面', cuisine_type: '小吃', rating: 4.7, price_range: '¥10-20', is_featured: true, tags: ['必吃', '特色'], description: '重庆特色小面' },
    { name: '酸辣粉', cuisine_type: '小吃', rating: 4.6, price_range: '¥10-18', is_featured: false, tags: ['特色'], description: '重庆街头美食' },
    { name: '麻辣香锅', cuisine_type: '川菜', rating: 4.5, price_range: '¥45-75', is_featured: false, tags: ['特色'], description: '重庆特色菜' },
    { name: '毛血旺', cuisine_type: '川菜', rating: 4.6, price_range: '¥40-70', is_featured: false, tags: ['特色'], description: '重庆特色菜' },
    { name: '水煮鱼', cuisine_type: '川菜', rating: 4.7, price_range: '¥50-85', is_featured: false, tags: ['特色'], description: '重庆特色菜' },
    { name: '辣子鸡', cuisine_type: '川菜', rating: 4.5, price_range: '¥45-75', is_featured: false, tags: ['特色'], description: '重庆特色菜' },
    { name: '豆花饭', cuisine_type: '小吃', rating: 4.4, price_range: '¥12-20', is_featured: false, tags: ['特色'], description: '重庆传统美食' },
    { name: '重庆粑粑', cuisine_type: '甜品', rating: 4.3, price_range: '¥8-15', is_featured: false, tags: ['特色'], description: '重庆传统小吃' },
    { name: '糍粑', cuisine_type: '甜品', rating: 4.3, price_range: '¥8-15', is_featured: false, tags: ['特色'], description: '重庆传统小吃' },
    { name: '流水席', cuisine_type: '川菜', rating: 4.2, price_range: '¥80-150', is_featured: false, tags: ['特色'], description: '重庆传统宴席' },
    { name: '八宝饭', cuisine_type: '甜品', rating: 4.1, price_range: '¥15-30', is_featured: false, tags: ['特色'], description: '重庆传统甜品' },
    { name: '酸萝卜面', cuisine_type: '小吃', rating: 4.4, price_range: '¥12-22', is_featured: false, tags: ['特色'], description: '重庆特色面食' },
    { name: '冰粉', cuisine_type: '甜品', rating: 4.5, price_range: '¥8-15', is_featured: false, tags: ['特色'], description: '重庆夏日甜品' },
    { name: '凉粉', cuisine_type: '小吃', rating: 4.4, price_range: '¥8-15', is_featured: false, tags: ['特色'], description: '重庆传统小吃' },
    { name: '留香鸡', cuisine_type: '川菜', rating: 4.3, price_range: '¥40-70', is_featured: false, tags: ['特色'], description: '重庆特色菜' },
    { name: '串串香', cuisine_type: '火锅', rating: 4.6, price_range: '¥35-60', is_featured: false, tags: ['特色'], description: '重庆街头美食' },
    { name: '板凳面', cuisine_type: '小吃', rating: 4.4, price_range: '¥10-18', is_featured: false, tags: ['特色'], description: '重庆特色面食' },
    { name: '豌杂面', cuisine_type: '小吃', rating: 4.5, price_range: '¥12-22', is_featured: false, tags: ['特色'], description: '重庆特色面食' },
    { name: '烧麦', cuisine_type: '小吃', rating: 4.2, price_range: '¥8-15', is_featured: false, tags: ['特色'], description: '重庆传统小吃' },
    { name: '鸡杂', cuisine_type: '川菜', rating: 4.4, price_range: '¥35-55', is_featured: false, tags: ['特色'], description: '重庆特色菜' },
    { name: '烤鱼', cuisine_type: '川菜', rating: 4.6, price_range: '¥60-100', is_featured: false, tags: ['特色'], description: '重庆特色美食' },
    { name: '黔江鸡杂', cuisine_type: '川菜', rating: 4.5, price_range: '¥40-65', is_featured: false, tags: ['特色'], description: '重庆特色菜' },
    { name: '涪陵榨菜', cuisine_type: '小吃', rating: 4.2, price_range: '¥5-15', is_featured: false, tags: ['特色'], description: '重庆特产' },
    { name: '合川桃片', cuisine_type: '甜品', rating: 4.3, price_range: '¥15-30', is_featured: false, tags: ['特色'], description: '重庆传统糕点' },
    { name: '江津米花糖', cuisine_type: '甜品', rating: 4.2, price_range: '¥10-20', is_featured: false, tags: ['特色'], description: '重庆传统小吃' },
    { name: '陈麻花', cuisine_type: '小吃', rating: 4.4, price_range: '¥15-30', is_featured: false, tags: ['特色'], description: '重庆磁器口特产' },
    { name: '山城小汤圆', cuisine_type: '甜品', rating: 4.3, price_range: '¥8-15', is_featured: false, tags: ['特色'], description: '重庆传统甜品' },
    { name: '毛凉粉', cuisine_type: '小吃', rating: 4.4, price_range: '¥10-18', is_featured: false, tags: ['特色'], description: '重庆传统小吃' },
    { name: '重庆回锅肉', cuisine_type: '川菜', rating: 4.5, price_range: '¥35-60', is_featured: false, tags: ['特色'], description: '重庆经典菜' },
  ])
  
  // 广州美食 (30个)
  addCityFoods('广州', [
    { name: '虾饺', cuisine_type: '粤菜', rating: 4.9, price_range: '¥25-45', is_featured: true, tags: ['必吃', '特色'], description: '广式早茶经典' },
    { name: '叉烧包', cuisine_type: '粤菜', rating: 4.7, price_range: '¥15-30', is_featured: false, tags: ['特色'], description: '广式早茶经典' },
    { name: '蛋挞', cuisine_type: '粤菜', rating: 4.6, price_range: '¥8-15', is_featured: false, tags: ['特色'], description: '广式早茶经典' },
    { name: '马拉糕', cuisine_type: '粤菜', rating: 4.5, price_range: '¥8-15', is_featured: false, tags: ['特色'], description: '广式早茶经典' },
    { name: '干蒸烧卖', cuisine_type: '粤菜', rating: 4.6, price_range: '¥20-35', is_featured: false, tags: ['特色'], description: '广式早茶经典' },
    { name: '奶黄包', cuisine_type: '粤菜', rating: 4.5, price_range: '¥12-22', is_featured: false, tags: ['特色'], description: '广式早茶经典' },
    { name: '陈醋凤爪', cuisine_type: '粤菜', rating: 4.4, price_range: '¥15-28', is_featured: false, tags: ['特色'], description: '广式早茶经典' },
    { name: '沙爹金钱肚', cuisine_type: '粤菜', rating: 4.5, price_range: '¥25-45', is_featured: false, tags: ['特色'], description: '广式早茶经典' },
    { name: '红米肠', cuisine_type: '粤菜', rating: 4.4, price_range: '¥20-38', is_featured: false, tags: ['特色'], description: '广式早茶经典' },
    { name: '艇仔粥', cuisine_type: '粤菜', rating: 4.5, price_range: '¥20-35', is_featured: false, tags: ['特色'], description: '广州传统粥品' },
    { name: '肠粉', cuisine_type: '粤菜', rating: 4.6, price_range: '¥10-20', is_featured: false, tags: ['特色'], description: '广州传统早餐' },
    { name: '白切鸡', cuisine_type: '粤菜', rating: 4.7, price_range: '¥40-70', is_featured: false, tags: ['特色'], description: '广州传统名菜' },
    { name: '烧鹅', cuisine_type: '粤菜', rating: 4.8, price_range: '¥50-90', is_featured: true, tags: ['必吃'], description: '广州经典烧腊' },
    { name: '腊肠', cuisine_type: '粤菜', rating: 4.4, price_range: '¥25-50', is_featured: false, tags: ['特色'], description: '广州传统腊味' },
    { name: '卤肉饭', cuisine_type: '粤菜', rating: 4.3, price_range: '¥20-35', is_featured: false, tags: ['特色'], description: '广州传统快餐' },
    { name: '双皮奶', cuisine_type: '甜品', rating: 4.5, price_range: '¥12-22', is_featured: false, tags: ['特色'], description: '广州传统甜品' },
    { name: '姜撞奶', cuisine_type: '甜品', rating: 4.4, price_range: '¥12-20', is_featured: false, tags: ['特色'], description: '广州传统甜品' },
    { name: '云吞面', cuisine_type: '粤菜', rating: 4.5, price_range: '¥20-35', is_featured: false, tags: ['特色'], description: '广州传统面食' },
    { name: '生滚粥', cuisine_type: '粤菜', rating: 4.4, price_range: '¥18-32', is_featured: false, tags: ['特色'], description: '广州传统粥品' },
    { name: '凉茶', cuisine_type: '饮品', rating: 4.3, price_range: '¥8-15', is_featured: false, tags: ['特色'], description: '广州传统饮品' },
    { name: '及第粥', cuisine_type: '粤菜', rating: 4.4, price_range: '¥25-40', is_featured: false, tags: ['特色'], description: '广州传统粥品' },
    { name: '萝卜牛杂', cuisine_type: '小吃', rating: 4.5, price_range: '¥15-30', is_featured: false, tags: ['特色'], description: '广州街头美食' },
    { name: '鸡仔饼', cuisine_type: '甜品', rating: 4.3, price_range: '¥15-30', is_featured: false, tags: ['特色'], description: '广州传统糕点' },
    { name: '老婆饼', cuisine_type: '甜品', rating: 4.4, price_range: '¥12-25', is_featured: false, tags: ['特色'], description: '广州传统糕点' },
    { name: '广式月饼', cuisine_type: '甜品', rating: 4.5, price_range: '¥25-80', is_featured: false, tags: ['特色'], description: '广州中秋特色' },
    { name: '马蹄糕', cuisine_type: '甜品', rating: 4.3, price_range: '¥10-20', is_featured: false, tags: ['特色'], description: '广州传统糕点' },
    { name: '伦教糕', cuisine_type: '甜品', rating: 4.2, price_range: '¥12-22', is_featured: false, tags: ['特色'], description: '广州传统糕点' },
    { name: '沙河粉', cuisine_type: '粤菜', rating: 4.4, price_range: '¥20-35', is_featured: false, tags: ['特色'], description: '广州传统小吃' },
    { name: '煲仔饭', cuisine_type: '粤菜', rating: 4.5, price_range: '¥25-50', is_featured: false, tags: ['特色'], description: '广州传统主食' },
    { name: '豉油鸡', cuisine_type: '粤菜', rating: 4.4, price_range: '¥35-65', is_featured: false, tags: ['特色'], description: '广州传统名菜' },
  ])
  
  // 苏州美食 (30个)
  addCityFoods('苏州', [
    { name: '松鼠桂鱼', cuisine_type: '苏菜', rating: 4.8, price_range: '¥80-150', is_featured: true, tags: ['必吃'], description: '苏州名菜' },
    { name: '响油鳝糊', cuisine_type: '苏菜', rating: 4.6, price_range: '¥60-100', is_featured: false, tags: ['特色'], description: '苏州传统菜' },
    { name: '清炒虾仁', cuisine_type: '苏菜', rating: 4.5, price_range: '¥50-80', is_featured: false, tags: ['特色'], description: '苏州特色菜' },
    { name: '腌笃鲜', cuisine_type: '苏菜', rating: 4.6, price_range: '¥40-70', is_featured: false, tags: ['特色'], description: '苏州传统汤菜' },
    { name: '苏式红烧肉', cuisine_type: '苏菜', rating: 4.5, price_range: '¥45-75', is_featured: false, tags: ['特色'], description: '苏州传统菜' },
    { name: '母油船鸭', cuisine_type: '苏菜', rating: 4.4, price_range: '¥80-150', is_featured: false, tags: ['特色'], description: '苏州传统名菜' },
    { name: '西瓜鸡', cuisine_type: '苏菜', rating: 4.3, price_range: '¥70-130', is_featured: false, tags: ['特色'], description: '苏州特色菜' },
    { name: '酱方', cuisine_type: '苏菜', rating: 4.4, price_range: '¥50-90', is_featured: false, tags: ['特色'], description: '苏州传统名菜' },
    { name: '碧螺虾仁', cuisine_type: '苏菜', rating: 4.5, price_range: '¥55-90', is_featured: false, tags: ['特色'], description: '苏州特色菜' },
    { name: '糖粥', cuisine_type: '甜品', rating: 4.3, price_range: '¥8-15', is_featured: false, tags: ['特色'], description: '苏州传统甜品' },
    { name: '哑巴生煎', cuisine_type: '小吃', rating: 4.5, price_range: '¥15-25', is_featured: false, tags: ['特色'], description: '苏州特色小吃' },
    { name: '臭豆腐干', cuisine_type: '小吃', rating: 4.2, price_range: '¥8-15', is_featured: false, tags: ['特色'], description: '苏州传统小吃' },
    { name: '咸肉菜饭', cuisine_type: '苏菜', rating: 4.3, price_range: '¥20-35', is_featured: false, tags: ['特色'], description: '苏州传统主食' },
    { name: '汤圆', cuisine_type: '甜品', rating: 4.2, price_range: '¥10-20', is_featured: false, tags: ['特色'], description: '苏州传统甜品' },
    { name: '苏式月饼', cuisine_type: '甜品', rating: 4.4, price_range: '¥15-40', is_featured: false, tags: ['特色'], description: '苏州中秋特色' },
    { name: '枣泥麻饼', cuisine_type: '甜品', rating: 4.3, price_range: '¥12-25', is_featured: false, tags: ['特色'], description: '苏州传统糕点' },
    { name: '酥饼', cuisine_type: '甜品', rating: 4.2, price_range: '¥8-15', is_featured: false, tags: ['特色'], description: '苏州传统糕点' },
    { name: '海棠糕', cuisine_type: '甜品', rating: 4.3, price_range: '¥8-15', is_featured: false, tags: ['特色'], description: '苏州传统糕点' },
    { name: '青团', cuisine_type: '甜品', rating: 4.5, price_range: '¥8-15', is_featured: false, tags: ['特色'], description: '苏州清明特色' },
    { name: '茶糕', cuisine_type: '甜品', rating: 4.2, price_range: '¥8-15', is_featured: false, tags: ['特色'], description: '苏州传统糕点' },
    { name: '蟹壳黄', cuisine_type: '小吃', rating: 4.2, price_range: '¥8-15', is_featured: false, tags: ['特色'], description: '苏州传统烧饼' },
    { name: '奥灶面', cuisine_type: '小吃', rating: 4.4, price_range: '¥15-30', is_featured: false, tags: ['特色'], description: '昆山特色面食' },
    { name: '枫镇大肉面', cuisine_type: '小吃', rating: 4.5, price_range: '¥20-35', is_featured: false, tags: ['特色'], description: '苏州特色面食' },
    { name: '藏书羊肉', cuisine_type: '苏菜', rating: 4.4, price_range: '¥40-70', is_featured: false, tags: ['特色'], description: '苏州传统美食' },
    { name: '叫花鸡', cuisine_type: '苏菜', rating: 4.5, price_range: '¥80-150', is_featured: false, tags: ['特色'], description: '苏州传统名菜' },
    { name: '三虾面', cuisine_type: '小吃', rating: 4.6, price_range: '¥60-100', is_featured: false, tags: ['特色'], description: '苏州特色面食' },
    { name: '梅花糕', cuisine_type: '甜品', rating: 4.2, price_range: '¥8-15', is_featured: false, tags: ['特色'], description: '苏州传统糕点' },
    { name: '苏州青团', cuisine_type: '甜品', rating: 4.4, price_range: '¥10-18', is_featured: false, tags: ['特色'], description: '苏州清明特色' },
    { name: '苏州酥饼', cuisine_type: '甜品', rating: 4.3, price_range: '¥10-20', is_featured: false, tags: ['特色'], description: '苏州传统糕点' },
    { name: '海棠糕', cuisine_type: '甜品', rating: 4.3, price_range: '¥8-15', is_featured: false, tags: ['特色'], description: '苏州传统糕点' },
  ])
  
  // 厦门美食 (30个)
  addCityFoods('厦门', [
    { name: '沙茶面', cuisine_type: '闽南菜', rating: 4.7, price_range: '¥20-40', is_featured: true, tags: ['必吃', '特色'], description: '厦门特色小吃' },
    { name: '海蛎煎', cuisine_type: '闽南菜', rating: 4.6, price_range: '¥25-45', is_featured: false, tags: ['特色'], description: '厦门传统小吃' },
    { name: '炸五香', cuisine_type: '闽南菜', rating: 4.4, price_range: '¥15-30', is_featured: false, tags: ['特色'], description: '厦门传统小吃' },
    { name: '花生汤', cuisine_type: '甜品', rating: 4.3, price_range: '¥8-15', is_featured: false, tags: ['特色'], description: '厦门传统甜品' },
    { name: '土笋冻', cuisine_type: '闽南菜', rating: 4.4, price_range: '¥15-30', is_featured: false, tags: ['特色'], description: '厦门特色凉菜' },
    { name: '满煎糕', cuisine_type: '甜品', rating: 4.2, price_range: '¥8-15', is_featured: false, tags: ['特色'], description: '厦门传统糕点' },
    { name: '四果汤', cuisine_type: '甜品', rating: 4.3, price_range: '¥10-20', is_featured: false, tags: ['特色'], description: '厦门夏日甜品' },
    { name: '同安封肉', cuisine_type: '闽南菜', rating: 4.5, price_range: '¥40-70', is_featured: false, tags: ['特色'], description: '厦门传统名菜' },
    { name: '大肠血', cuisine_type: '闽南菜', rating: 4.3, price_range: '¥20-35', is_featured: false, tags: ['特色'], description: '厦门传统小吃' },
    { name: '厦门薄饼', cuisine_type: '闽南菜', rating: 4.2, price_range: '¥12-25', is_featured: false, tags: ['特色'], description: '厦门传统小吃' },
    { name: '烧肉粽', cuisine_type: '闽南菜', rating: 4.5, price_range: '¥15-30', is_featured: false, tags: ['特色'], description: '厦门传统小吃' },
    { name: '姜母鸭', cuisine_type: '闽南菜', rating: 4.6, price_range: '¥60-100', is_featured: false, tags: ['特色'], description: '厦门特色菜' },
    { name: '油墩子', cuisine_type: '闽南菜', rating: 4.1, price_range: '¥8-15', is_featured: false, tags: ['特色'], description: '厦门传统小吃' },
    { name: '面线糊', cuisine_type: '闽南菜', rating: 4.4, price_range: '¥15-25', is_featured: false, tags: ['特色'], description: '厦门传统早餐' },
    { name: '五香条', cuisine_type: '闽南菜', rating: 4.3, price_range: '¥12-22', is_featured: false, tags: ['特色'], description: '厦门传统小吃' },
    { name: '碗仔粿', cuisine_type: '闽南菜', rating: 4.2, price_range: '¥10-18', is_featured: false, tags: ['特色'], description: '厦门传统小吃' },
    { name: '烧仙草', cuisine_type: '甜品', rating: 4.3, price_range: '¥8-15', is_featured: false, tags: ['特色'], description: '厦门夏日甜品' },
    { name: '冬瓜茶', cuisine_type: '饮品', rating: 4.2, price_range: '¥8-15', is_featured: false, tags: ['特色'], description: '厦门传统饮品' },
    { name: '凤梨酥', cuisine_type: '甜品', rating: 4.5, price_range: '¥25-50', is_featured: false, tags: ['特色'], description: '厦门特产' },
    { name: '鱼丸汤', cuisine_type: '闽南菜', rating: 4.4, price_range: '¥20-35', is_featured: false, tags: ['特色'], description: '厦门传统汤品' },
    { name: '芋包', cuisine_type: '闽南菜', rating: 4.3, price_range: '¥15-30', is_featured: false, tags: ['特色'], description: '厦门传统小吃' },
    { name: '虾面', cuisine_type: '闽南菜', rating: 4.4, price_range: '¥20-35', is_featured: false, tags: ['特色'], description: '厦门特色面食' },
    { name: '鸭肉粥', cuisine_type: '闽南菜', rating: 4.3, price_range: '¥15-30', is_featured: false, tags: ['特色'], description: '厦门传统粥品' },
    { name: '韭菜盒', cuisine_type: '闽南菜', rating: 4.2, price_range: '¥10-20', is_featured: false, tags: ['特色'], description: '厦门传统小吃' },
    { name: '薄饼', cuisine_type: '闽南菜', rating: 4.3, price_range: '¥12-25', is_featured: false, tags: ['特色'], description: '厦门传统小吃' },
    { name: '马蹄酥', cuisine_type: '甜品', rating: 4.2, price_range: '¥10-20', is_featured: false, tags: ['特色'], description: '厦门传统糕点' },
    { name: '沙茶酱', cuisine_type: '闽南菜', rating: 4.1, price_range: '¥15-30', is_featured: false, tags: ['特色'], description: '厦门特产调料' },
    { name: '厦门海鲜', cuisine_type: '海鲜', rating: 4.5, price_range: '¥80-200', is_featured: false, tags: ['特色'], description: '厦门新鲜海鲜' },
    { name: '鼓浪屿馅饼', cuisine_type: '甜品', rating: 4.4, price_range: '¥20-40', is_featured: false, tags: ['特色'], description: '鼓浪屿特产' },
    { name: '黄则和花生汤', cuisine_type: '甜品', rating: 4.3, price_range: '¥10-20', is_featured: false, tags: ['特色'], description: '厦门老字号' },
  ])
  
  // 三亚美食 (30个)
  addCityFoods('三亚', [
    { name: '文昌鸡', cuisine_type: '海南菜', rating: 4.8, price_range: '¥60-100', is_featured: true, tags: ['必吃', '特色'], description: '海南四大名菜之首' },
    { name: '加积鸭', cuisine_type: '海南菜', rating: 4.6, price_range: '¥50-90', is_featured: false, tags: ['特色'], description: '海南四大名菜' },
    { name: '和乐蟹', cuisine_type: '海鲜', rating: 4.7, price_range: '¥100-200', is_featured: false, tags: ['特色'], description: '海南四大名菜' },
    { name: '东山羊', cuisine_type: '海南菜', rating: 4.5, price_range: '¥70-120', is_featured: false, tags: ['特色'], description: '海南四大名菜' },
    { name: '抱罗粉', cuisine_type: '小吃', rating: 4.4, price_range: '¥15-30', is_featured: false, tags: ['特色'], description: '海南传统小吃' },
    { name: '清补凉', cuisine_type: '甜品', rating: 4.5, price_range: '¥12-25', is_featured: false, tags: ['特色'], description: '海南夏日甜品' },
    { name: '海南粉', cuisine_type: '小吃', rating: 4.4, price_range: '¥15-30', is_featured: false, tags: ['特色'], description: '海南传统小吃' },
    { name: '椰子饭', cuisine_type: '海南菜', rating: 4.3, price_range: '¥25-45', is_featured: false, tags: ['特色'], description: '海南特色主食' },
    { name: '竹筒饭', cuisine_type: '海南菜', rating: 4.2, price_range: '¥20-40', is_featured: false, tags: ['特色'], description: '黎族传统美食' },
    { name: '黑毛猪', cuisine_type: '海南菜', rating: 4.3, price_range: '¥50-90', is_featured: false, tags: ['特色'], description: '海南特色菜' },
    { name: '海胆蒸蛋', cuisine_type: '海鲜', rating: 4.4, price_range: '¥80-150', is_featured: false, tags: ['特色'], description: '三亚特色海鲜' },
    { name: '龙虾', cuisine_type: '海鲜', rating: 4.7, price_range: '¥150-300', is_featured: false, tags: ['特色'], description: '三亚新鲜海鲜' },
    { name: '扇贝', cuisine_type: '海鲜', rating: 4.3, price_range: '¥60-120', is_featured: false, tags: ['特色'], description: '三亚新鲜海鲜' },
    { name: '海蜇', cuisine_type: '海鲜', rating: 4.2, price_range: '¥40-80', is_featured: false, tags: ['特色'], description: '三亚特色海鲜' },
    { name: '鱼煲', cuisine_type: '海鲜', rating: 4.3, price_range: '¥70-130', is_featured: false, tags: ['特色'], description: '三亚特色菜' },
    { name: '羊栏酸鱼汤', cuisine_type: '海南菜', rating: 4.2, price_range: '¥50-90', is_featured: false, tags: ['特色'], description: '三亚特色汤品' },
    { name: '黎家竹筒饭', cuisine_type: '海南菜', rating: 4.3, price_range: '¥25-45', is_featured: false, tags: ['特色'], description: '黎族传统美食' },
    { name: '海南腌面', cuisine_type: '小吃', rating: 4.3, price_range: '¥12-25', is_featured: false, tags: ['特色'], description: '海南传统面食' },
    { name: '鸡屎藤粑仔', cuisine_type: '甜品', rating: 4.2, price_range: '¥10-20', is_featured: false, tags: ['特色'], description: '海南传统甜品' },
    { name: '红糖年糕', cuisine_type: '甜品', rating: 4.1, price_range: '¥15-30', is_featured: false, tags: ['特色'], description: '海南传统糕点' },
    { name: '椰子冻', cuisine_type: '甜品', rating: 4.4, price_range: '¥20-40', is_featured: false, tags: ['特色'], description: '海南特色甜品' },
    { name: '港门粉', cuisine_type: '小吃', rating: 4.3, price_range: '¥15-30', is_featured: false, tags: ['特色'], description: '三亚特色小吃' },
    { name: '藤桥排骨', cuisine_type: '海南菜', rating: 4.4, price_range: '¥40-70', is_featured: false, tags: ['特色'], description: '三亚特色菜' },
    { name: '荔枝木烤鸭', cuisine_type: '海南菜', rating: 4.3, price_range: '¥50-90', is_featured: false, tags: ['特色'], description: '三亚特色菜' },
    { name: '海鲜火锅', cuisine_type: '火锅', rating: 4.5, price_range: '¥100-200', is_featured: false, tags: ['特色'], description: '三亚特色火锅' },
    { name: '椰奶清补凉', cuisine_type: '甜品', rating: 4.4, price_range: '¥15-30', is_featured: false, tags: ['特色'], description: '海南特色甜品' },
    { name: '黄流老鸭', cuisine_type: '海南菜', rating: 4.3, price_range: '¥60-100', is_featured: false, tags: ['特色'], description: '海南传统名菜' },
    { name: '海南大虾', cuisine_type: '海鲜', rating: 4.4, price_range: '¥80-160', is_featured: false, tags: ['特色'], description: '三亚新鲜海鲜' },
    { name: '海南海胆', cuisine_type: '海鲜', rating: 4.3, price_range: '¥70-140', is_featured: false, tags: ['特色'], description: '三亚特色海鲜' },
    { name: '椰子鸡', cuisine_type: '海南菜', rating: 4.5, price_range: '¥70-120', is_featured: false, tags: ['特色'], description: '海南特色菜' },
  ])
  
  // 青岛美食 (30个)
  addCityFoods('青岛', [
    { name: '辣炒蛤蜊', cuisine_type: '海鲜', rating: 4.7, price_range: '¥30-60', is_featured: true, tags: ['必吃', '特色'], description: '青岛特色海鲜' },
    { name: '鲅鱼水饺', cuisine_type: '小吃', rating: 4.6, price_range: '¥25-45', is_featured: false, tags: ['特色'], description: '青岛特色水饺' },
    { name: '流亭猪蹄', cuisine_type: '鲁菜', rating: 4.5, price_range: '¥40-70', is_featured: false, tags: ['特色'], description: '青岛传统名菜' },
    { name: '海肠捞饭', cuisine_type: '海鲜', rating: 4.6, price_range: '¥50-90', is_featured: false, tags: ['特色'], description: '青岛特色菜' },
    { name: '青岛脂渣', cuisine_type: '小吃', rating: 4.4, price_range: '¥20-40', is_featured: false, tags: ['特色'], description: '青岛传统小吃' },
    { name: '李村戳子肉', cuisine_type: '烧烤', rating: 4.5, price_range: '¥40-70', is_featured: false, tags: ['特色'], description: '青岛特色烧烤' },
    { name: '海菜凉粉', cuisine_type: '小吃', rating: 4.3, price_range: '¥10-20', is_featured: false, tags: ['特色'], description: '青岛传统小吃' },
    { name: '排骨米饭', cuisine_type: '小吃', rating: 4.4, price_range: '¥20-35', is_featured: false, tags: ['特色'], description: '青岛特色快餐' },
    { name: '青岛锅贴', cuisine_type: '小吃', rating: 4.3, price_range: '¥15-30', is_featured: false, tags: ['特色'], description: '青岛传统小吃' },
    { name: '崂山菇炖鸡', cuisine_type: '鲁菜', rating: 4.5, price_range: '¥60-100', is_featured: false, tags: ['特色'], description: '青岛特色菜' },
    { name: '鲍鱼', cuisine_type: '海鲜', rating: 4.6, price_range: '¥100-200', is_featured: false, tags: ['特色'], description: '青岛高档海鲜' },
    { name: '海参', cuisine_type: '海鲜', rating: 4.5, price_range: '¥120-250', is_featured: false, tags: ['特色'], description: '青岛高档海鲜' },
    { name: '大虾', cuisine_type: '海鲜', rating: 4.4, price_range: '¥80-160', is_featured: false, tags: ['特色'], description: '青岛新鲜海鲜' },
    { name: '海带', cuisine_type: '海鲜', rating: 4.2, price_range: '¥15-30', is_featured: false, tags: ['特色'], description: '青岛特产' },
    { name: '黄花鱼', cuisine_type: '海鲜', rating: 4.3, price_range: '¥60-120', is_featured: false, tags: ['特色'], description: '青岛特色海鲜' },
    { name: '青岛大包', cuisine_type: '小吃', rating: 4.2, price_range: '¥8-15', is_featured: false, tags: ['特色'], description: '青岛传统包子' },
    { name: '油条', cuisine_type: '小吃', rating: 4.1, price_range: '¥3-6', is_featured: false, tags: ['特色'], description: '青岛传统早餐' },
    { name: '豆腐脑', cuisine_type: '小吃', rating: 4.2, price_range: '¥5-10', is_featured: false, tags: ['特色'], description: '青岛传统早餐' },
    { name: '烧饼', cuisine_type: '小吃', rating: 4.0, price_range: '¥5-10', is_featured: false, tags: ['特色'], description: '青岛传统面食' },
    { name: '煎饼果子', cuisine_type: '小吃', rating: 4.1, price_range: '¥8-15', is_featured: false, tags: ['特色'], description: '青岛传统早餐' },
    { name: '海鲜大咖', cuisine_type: '海鲜', rating: 4.6, price_range: '¥150-300', is_featured: false, tags: ['特色'], description: '青岛海鲜盛宴' },
    { name: '烤鱿鱼', cuisine_type: '烧烤', rating: 4.4, price_range: '¥15-30', is_featured: false, tags: ['特色'], description: '青岛街头美食' },
    { name: '海鲜馄饨', cuisine_type: '小吃', rating: 4.3, price_range: '¥20-35', is_featured: false, tags: ['特色'], description: '青岛特色馄饨' },
    { name: '酱猪蹄', cuisine_type: '鲁菜', rating: 4.4, price_range: '¥35-60', is_featured: false, tags: ['特色'], description: '青岛传统菜' },
    { name: '葱油饼', cuisine_type: '小吃', rating: 4.2, price_range: '¥8-15', is_featured: false, tags: ['特色'], description: '青岛传统面食' },
    { name: '海鲜疙瘩汤', cuisine_type: '鲁菜', rating: 4.3, price_range: '¥25-45', is_featured: false, tags: ['特色'], description: '青岛特色汤品' },
    { name: '炸蛎黄', cuisine_type: '海鲜', rating: 4.4, price_range: '¥30-55', is_featured: false, tags: ['特色'], description: '青岛特色海鲜' },
    { name: '原壳鲍鱼', cuisine_type: '海鲜', rating: 4.5, price_range: '¥80-150', is_featured: false, tags: ['特色'], description: '青岛高档海鲜' },
    { name: '肉末海参', cuisine_type: '海鲜', rating: 4.4, price_range: '¥100-200', is_featured: false, tags: ['特色'], description: '青岛特色菜' },
    { name: '青岛大包', cuisine_type: '小吃', rating: 4.2, price_range: '¥8-15', is_featured: false, tags: ['特色'], description: '青岛传统包子' },
  ])
  
  // 南京美食 (30个)
  addCityFoods('南京', [
    { name: '鸭血粉丝汤', cuisine_type: '小吃', rating: 4.8, price_range: '¥15-30', is_featured: true, tags: ['必吃', '特色'], description: '南京特色小吃' },
    { name: '牛肉锅贴', cuisine_type: '小吃', rating: 4.6, price_range: '¥15-25', is_featured: false, tags: ['特色'], description: '南京传统小吃' },
    { name: '盐水鸭', cuisine_type: '苏菜', rating: 4.8, price_range: '¥40-80', is_featured: true, tags: ['必吃', '特色'], description: '南京传统名菜' },
    { name: '南京烤鸭', cuisine_type: '苏菜', rating: 4.6, price_range: '¥50-90', is_featured: false, tags: ['特色'], description: '南京特色菜' },
    { name: '皮肚面', cuisine_type: '小吃', rating: 4.5, price_range: '¥20-35', is_featured: false, tags: ['特色'], description: '南京特色面食' },
    { name: '鸡鸣汤包', cuisine_type: '小吃', rating: 4.5, price_range: '¥20-35', is_featured: false, tags: ['特色'], description: '南京特色汤包' },
    { name: '秦淮八绝', cuisine_type: '小吃', rating: 4.6, price_range: '¥60-120', is_featured: false, tags: ['特色'], description: '秦淮风味小吃' },
    { name: '黄桥烧饼', cuisine_type: '小吃', rating: 4.3, price_range: '¥8-15', is_featured: false, tags: ['特色'], description: '南京传统烧饼' },
    { name: '开洋干丝', cuisine_type: '小吃', rating: 4.4, price_range: '¥15-30', is_featured: false, tags: ['特色'], description: '南京传统小吃' },
    { name: '牛肉汤', cuisine_type: '小吃', rating: 4.3, price_range: '¥18-32', is_featured: false, tags: ['特色'], description: '南京传统汤品' },
    { name: '臭豆腐', cuisine_type: '小吃', rating: 4.2, price_range: '¥8-15', is_featured: false, tags: ['特色'], description: '南京传统小吃' },
    { name: '麻辣小龙虾', cuisine_type: '小吃', rating: 4.4, price_range: '¥60-120', is_featured: false, tags: ['特色'], description: '南京夜宵美食' },
    { name: '糖芋苗', cuisine_type: '甜品', rating: 4.3, price_range: '¥10-20', is_featured: false, tags: ['特色'], description: '南京传统甜品' },
    { name: '赤豆元宵', cuisine_type: '甜品', rating: 4.4, price_range: '¥10-20', is_featured: false, tags: ['特色'], description: '南京传统甜品' },
    { name: '梅花糕', cuisine_type: '甜品', rating: 4.2, price_range: '¥8-15', is_featured: false, tags: ['特色'], description: '南京传统糕点' },
    { name: '酥烧饼', cuisine_type: '小吃', rating: 4.1, price_range: '¥6-12', is_featured: false, tags: ['特色'], description: '南京传统烧饼' },
    { name: '菜包', cuisine_type: '小吃', rating: 4.0, price_range: '¥3-6', is_featured: false, tags: ['特色'], description: '南京传统早餐' },
    { name: '肉包', cuisine_type: '小吃', rating: 4.1, price_range: '¥4-8', is_featured: false, tags: ['特色'], description: '南京传统早餐' },
    { name: '美龄粥', cuisine_type: '甜品', rating: 4.3, price_range: '¥15-28', is_featured: false, tags: ['特色'], description: '南京传统甜品' },
    { name: '桂花糕', cuisine_type: '甜品', rating: 4.2, price_range: '¥10-20', is_featured: false, tags: ['特色'], description: '南京传统糕点' },
    { name: '如意回卤干', cuisine_type: '小吃', rating: 4.2, price_range: '¥10-20', is_featured: false, tags: ['特色'], description: '南京传统小吃' },
    { name: '什锦豆腐涝', cuisine_type: '小吃', rating: 4.1, price_range: '¥8-15', is_featured: false, tags: ['特色'], description: '南京传统早餐' },
    { name: '状元豆', cuisine_type: '小吃', rating: 4.2, price_range: '¥10-20', is_featured: false, tags: ['特色'], description: '南京传统小吃' },
    { name: '旺鸡蛋', cuisine_type: '小吃', rating: 4.0, price_range: '¥5-10', is_featured: false, tags: ['特色'], description: '南京街头美食' },
    { name: '活珠子', cuisine_type: '小吃', rating: 4.1, price_range: '¥5-10', is_featured: false, tags: ['特色'], description: '南京特色小吃' },
    { name: '洪蓝玉带糕', cuisine_type: '甜品', rating: 4.2, price_range: '¥15-30', is_featured: false, tags: ['特色'], description: '溧水特产' },
    { name: '东坝豆腐干', cuisine_type: '小吃', rating: 4.1, price_range: '¥10-20', is_featured: false, tags: ['特色'], description: '高淳特产' },
    { name: '南京鸭血粉丝', cuisine_type: '小吃', rating: 4.7, price_range: '¥18-35', is_featured: false, tags: ['特色'], description: '南京特色小吃' },
    { name: '鸭血粉丝', cuisine_type: '小吃', rating: 4.6, price_range: '¥16-32', is_featured: false, tags: ['特色'], description: '南京特色小吃' },
  ])
  
  // 武汉美食 (30个)
  addCityFoods('武汉', [
    { name: '热干面', cuisine_type: '小吃', rating: 4.8, price_range: '¥8-15', is_featured: true, tags: ['必吃', '特色'], description: '武汉经典早餐' },
    { name: '三鲜豆皮', cuisine_type: '小吃', rating: 4.6, price_range: '¥12-25', is_featured: false, tags: ['特色'], description: '武汉传统小吃' },
    { name: '鲜鱼糊汤粉', cuisine_type: '小吃', rating: 4.5, price_range: '¥10-20', is_featured: false, tags: ['特色'], description: '武汉特色早餐' },
    { name: '油焖小龙虾', cuisine_type: '鄂菜', rating: 4.7, price_range: '¥80-150', is_featured: false, tags: ['特色'], description: '武汉夜宵首选' },
    { name: '清蒸武昌鱼', cuisine_type: '鄂菜', rating: 4.6, price_range: '¥50-100', is_featured: false, tags: ['特色'], description: '武汉传统名菜' },
    { name: '排骨藕汤', cuisine_type: '鄂菜', rating: 4.5, price_range: '¥35-60', is_featured: false, tags: ['特色'], description: '武汉传统汤品' },
    { name: '面窝', cuisine_type: '小吃', rating: 4.4, price_range: '¥3-8', is_featured: false, tags: ['特色'], description: '武汉传统早餐' },
    { name: '煎饺', cuisine_type: '小吃', rating: 4.3, price_range: '¥10-18', is_featured: false, tags: ['特色'], description: '武汉传统小吃' },
    { name: '重油烧麦', cuisine_type: '小吃', rating: 4.5, price_range: '¥12-25', is_featured: false, tags: ['特色'], description: '武汉特色烧麦' },
    { name: '汤包', cuisine_type: '小吃', rating: 4.4, price_range: '¥15-30', is_featured: false, tags: ['特色'], description: '武汉传统小吃' },
    { name: '鸡蛋灌饼', cuisine_type: '小吃', rating: 4.2, price_range: '¥6-12', is_featured: false, tags: ['特色'], description: '武汉传统早餐' },
    { name: '油条', cuisine_type: '小吃', rating: 4.1, price_range: '¥2-5', is_featured: false, tags: ['特色'], description: '武汉传统早餐' },
    { name: '包子', cuisine_type: '小吃', rating: 4.0, price_range: '¥2-5', is_featured: false, tags: ['特色'], description: '武汉传统早餐' },
    { name: '馒头', cuisine_type: '小吃', rating: 3.9, price_range: '¥1-3', is_featured: false, tags: ['特色'], description: '武汉传统主食' },
    { name: '花饭', cuisine_type: '小吃', rating: 4.0, price_range: '¥10-20', is_featured: false, tags: ['特色'], description: '武汉特色炒饭' },
    { name: '凉面', cuisine_type: '小吃', rating: 4.2, price_range: '¥8-15', is_featured: false, tags: ['特色'], description: '武汉夏日美食' },
    { name: '米粉', cuisine_type: '小吃', rating: 4.1, price_range: '¥10-18', is_featured: false, tags: ['特色'], description: '武汉特色面食' },
    { name: '粥', cuisine_type: '小吃', rating: 4.0, price_range: '¥5-12', is_featured: false, tags: ['特色'], description: '武汉传统早餐' },
    { name: '牛肉面', cuisine_type: '小吃', rating: 4.3, price_range: '¥15-28', is_featured: false, tags: ['特色'], description: '武汉特色面食' },
    { name: '豆腐脑', cuisine_type: '小吃', rating: 4.1, price_range: '¥5-10', is_featured: false, tags: ['特色'], description: '武汉传统早餐' },
    { name: '欢喜坨', cuisine_type: '甜品', rating: 4.2, price_range: '¥5-10', is_featured: false, tags: ['特色'], description: '武汉传统甜品' },
    { name: '糯米鸡', cuisine_type: '小吃', rating: 4.3, price_range: '¥8-15', is_featured: false, tags: ['特色'], description: '武汉传统早餐' },
    { name: '鸡冠饺', cuisine_type: '小吃', rating: 4.2, price_range: '¥3-8', is_featured: false, tags: ['特色'], description: '武汉传统早餐' },
    { name: '糯米包油条', cuisine_type: '小吃', rating: 4.3, price_range: '¥6-12', is_featured: false, tags: ['特色'], description: '武汉特色早餐' },
    { name: '汽水包', cuisine_type: '小吃', rating: 4.1, price_range: '¥3-8', is_featured: false, tags: ['特色'], description: '武汉传统小吃' },
    { name: '鸭脖', cuisine_type: '小吃', rating: 4.4, price_range: '¥15-30', is_featured: false, tags: ['特色'], description: '武汉特色小吃' },
    { name: '周黑鸭', cuisine_type: '小吃', rating: 4.5, price_range: '¥25-50', is_featured: false, tags: ['特色'], description: '武汉特产' },
    { name: '精武鸭脖', cuisine_type: '小吃', rating: 4.4, price_range: '¥20-40', is_featured: false, tags: ['特色'], description: '武汉特产' },
    { name: '四季美汤包', cuisine_type: '小吃', rating: 4.5, price_range: '¥20-40', is_featured: false, tags: ['特色'], description: '武汉老字号' },
    { name: '蔡林记热干面', cuisine_type: '小吃', rating: 4.7, price_range: '¥10-20', is_featured: false, tags: ['特色'], description: '武汉老字号' },
  ])
  
  // 长沙美食 (30个)
  addCityFoods('长沙', [
    { name: '长沙臭豆腐', cuisine_type: '小吃', rating: 4.7, price_range: '¥10-20', is_featured: true, tags: ['必吃', '特色'], description: '长沙著名小吃' },
    { name: '糖油粑粑', cuisine_type: '甜品', rating: 4.4, price_range: '¥8-15', is_featured: false, tags: ['特色'], description: '长沙传统甜品' },
    { name: '口味虾', cuisine_type: '湘菜', rating: 4.6, price_range: '¥60-120', is_featured: false, tags: ['特色'], description: '长沙夜宵首选' },
    { name: '湖南酱板鸭', cuisine_type: '湘菜', rating: 4.5, price_range: '¥40-80', is_featured: false, tags: ['特色'], description: '长沙特产' },
    { name: '长沙米粉', cuisine_type: '小吃', rating: 4.5, price_range: '¥12-25', is_featured: false, tags: ['特色'], description: '长沙传统早餐' },
    { name: '德园包子', cuisine_type: '小吃', rating: 4.3, price_range: '¥3-8', is_featured: false, tags: ['特色'], description: '长沙老字号' },
    { name: '龙脂猪血', cuisine_type: '小吃', rating: 4.2, price_range: '¥8-15', is_featured: false, tags: ['特色'], description: '长沙传统小吃' },
    { name: '嗍螺', cuisine_type: '小吃', rating: 4.3, price_range: '¥15-30', is_featured: false, tags: ['特色'], description: '长沙夜宵美食' },
    { name: '红烧猪脚', cuisine_type: '湘菜', rating: 4.4, price_range: '¥35-60', is_featured: false, tags: ['特色'], description: '长沙传统菜' },
    { name: '口味蟹', cuisine_type: '湘菜', rating: 4.5, price_range: '¥80-150', is_featured: false, tags: ['特色'], description: '长沙特色菜' },
    { name: '辣椒炒肉', cuisine_type: '湘菜', rating: 4.4, price_range: '¥30-50', is_featured: false, tags: ['特色'], description: '长沙家常菜' },
    { name: '剁椒鱼头', cuisine_type: '湘菜', rating: 4.6, price_range: '¥60-100', is_featured: false, tags: ['特色'], description: '长沙特色菜' },
    { name: '蒸菜', cuisine_type: '湘菜', rating: 4.3, price_range: '¥25-45', is_featured: false, tags: ['特色'], description: '长沙传统菜' },
    { name: '刮凉粉', cuisine_type: '小吃', rating: 4.2, price_range: '¥8-15', is_featured: false, tags: ['特色'], description: '长沙夏日美食' },
    { name: '油炸串串', cuisine_type: '小吃', rating: 4.1, price_range: '¥15-30', is_featured: false, tags: ['特色'], description: '长沙街头美食' },
    { name: '茶颜悦色', cuisine_type: '饮品', rating: 4.5, price_range: '¥15-30', is_featured: false, tags: ['特色'], description: '长沙网红奶茶' },
    { name: '小龙虾', cuisine_type: '湘菜', rating: 4.4, price_range: '¥70-140', is_featured: false, tags: ['特色'], description: '长沙夜宵美食' },
    { name: '甜酒冲蛋', cuisine_type: '甜品', rating: 4.2, price_range: '¥8-15', is_featured: false, tags: ['特色'], description: '长沙传统甜品' },
    { name: '毛氏红烧肉', cuisine_type: '湘菜', rating: 4.3, price_range: '¥45-80', is_featured: false, tags: ['特色'], description: '长沙传统名菜' },
    { name: '冰粉', cuisine_type: '甜品', rating: 4.1, price_range: '¥8-15', is_featured: false, tags: ['特色'], description: '长沙夏日甜品' },
    { name: '姊妹团子', cuisine_type: '甜品', rating: 4.2, price_range: '¥8-15', is_featured: false, tags: ['特色'], description: '长沙传统糕点' },
    { name: '荷兰粉', cuisine_type: '小吃', rating: 4.1, price_range: '¥8-15', is_featured: false, tags: ['特色'], description: '长沙传统小吃' },
    { name: '麻辣子鸡', cuisine_type: '湘菜', rating: 4.4, price_range: '¥40-70', is_featured: false, tags: ['特色'], description: '长沙传统菜' },
    { name: '三层套鸡', cuisine_type: '湘菜', rating: 4.2, price_range: '¥80-150', is_featured: false, tags: ['特色'], description: '长沙传统名菜' },
    { name: '长沙糕点', cuisine_type: '甜品', rating: 4.1, price_range: '¥15-35', is_featured: false, tags: ['特色'], description: '长沙传统糕点' },
    { name: '浏阳蒸菜', cuisine_type: '湘菜', rating: 4.3, price_range: '¥25-50', is_featured: false, tags: ['特色'], description: '浏阳特色美食' },
    { name: '长沙盒饭', cuisine_type: '小吃', rating: 4.0, price_range: '¥15-30', is_featured: false, tags: ['特色'], description: '长沙快餐' },
    { name: '湘西外婆菜', cuisine_type: '湘菜', rating: 4.2, price_range: '¥25-45', is_featured: false, tags: ['特色'], description: '湘西特色菜' },
  ])
  
  // 深圳美食 (30个)
  addCityFoods('深圳', [
    { name: '光明乳鸽', cuisine_type: '粤菜', rating: 4.8, price_range: '¥50-90', is_featured: true, tags: ['必吃', '特色'], description: '深圳特产美食' },
    { name: '公明烧鹅', cuisine_type: '粤菜', rating: 4.6, price_range: '¥45-80', is_featured: false, tags: ['特色'], description: '深圳传统美食' },
    { name: '深井烧鹅', cuisine_type: '粤菜', rating: 4.5, price_range: '¥50-90', is_featured: false, tags: ['特色'], description: '广式烧腊' },
    { name: '沙井蚝', cuisine_type: '海鲜', rating: 4.7, price_range: '¥80-150', is_featured: false, tags: ['特色'], description: '深圳特产海鲜' },
    { name: '南头荔枝', cuisine_type: '甜品', rating: 4.4, price_range: '¥20-40', is_featured: false, tags: ['特色'], description: '深圳特产' },
    { name: '福田云吞', cuisine_type: '粤菜', rating: 4.3, price_range: '¥18-35', is_featured: false, tags: ['特色'], description: '深圳传统美食' },
    { name: '罗湖肠粉', cuisine_type: '粤菜', rating: 4.4, price_range: '¥12-25', is_featured: false, tags: ['特色'], description: '深圳传统早餐' },
    { name: '龙岗鸡', cuisine_type: '粤菜', rating: 4.4, price_range: '¥40-70', is_featured: false, tags: ['特色'], description: '深圳传统美食' },
    { name: '宝安腊鸭', cuisine_type: '粤菜', rating: 4.3, price_range: '¥35-65', is_featured: false, tags: ['特色'], description: '深圳传统美食' },
    { name: '盐田海鲜', cuisine_type: '海鲜', rating: 4.5, price_range: '¥100-200', is_featured: false, tags: ['特色'], description: '盐田特色海鲜' },
    { name: '大梅沙海鲜', cuisine_type: '海鲜', rating: 4.4, price_range: '¥90-180', is_featured: false, tags: ['特色'], description: '大梅沙特色海鲜' },
    { name: '小梅沙烧烤', cuisine_type: '烧烤', rating: 4.3, price_range: '¥50-100', is_featured: false, tags: ['特色'], description: '小梅沙特色烧烤' },
    { name: '春满园早茶', cuisine_type: '粤菜', rating: 4.5, price_range: '¥60-120', is_featured: false, tags: ['特色'], description: '深圳早茶' },
    { name: '点都德', cuisine_type: '粤菜', rating: 4.6, price_range: '¥70-140', is_featured: false, tags: ['特色'], description: '深圳早茶名店' },
    { name: '陶陶居', cuisine_type: '粤菜', rating: 4.5, price_range: '¥65-130', is_featured: false, tags: ['特色'], description: '深圳早茶名店' },
    { name: '莲香楼', cuisine_type: '粤菜', rating: 4.4, price_range: '¥60-120', is_featured: false, tags: ['特色'], description: '深圳早茶名店' },
    { name: '广州酒家', cuisine_type: '粤菜', rating: 4.5, price_range: '¥70-140', is_featured: false, tags: ['特色'], description: '深圳粤菜名店' },
    { name: '泮溪酒家', cuisine_type: '粤菜', rating: 4.4, price_range: '¥65-130', is_featured: false, tags: ['特色'], description: '深圳粤菜名店' },
    { name: '北园酒家', cuisine_type: '粤菜', rating: 4.3, price_range: '¥60-120', is_featured: false, tags: ['特色'], description: '深圳粤菜名店' },
    { name: '东江盐焗鸡', cuisine_type: '粤菜', rating: 4.4, price_range: '¥40-75', is_featured: false, tags: ['特色'], description: '客家传统菜' },
    { name: '猪肚鸡', cuisine_type: '粤菜', rating: 4.5, price_range: '¥60-100', is_featured: false, tags: ['特色'], description: '广式火锅' },
    { name: '椰子鸡', cuisine_type: '粤菜', rating: 4.6, price_range: '¥70-120', is_featured: false, tags: ['特色'], description: '深圳特色火锅' },
    { name: '潮汕牛肉火锅', cuisine_type: '火锅', rating: 4.7, price_range: '¥80-150', is_featured: false, tags: ['特色'], description: '潮汕特色美食' },
    { name: '广式早茶', cuisine_type: '粤菜', rating: 4.6, price_range: '¥50-100', is_featured: false, tags: ['特色'], description: '广式早茶文化' },
    { name: '肠粉', cuisine_type: '粤菜', rating: 4.4, price_range: '¥10-25', is_featured: false, tags: ['特色'], description: '广式传统早餐' },
    { name: '叉烧', cuisine_type: '粤菜', rating: 4.5, price_range: '¥30-60', is_featured: false, tags: ['特色'], description: '广式烧腊' },
    { name: '烧鹅饭', cuisine_type: '粤菜', rating: 4.4, price_range: '¥25-50', is_featured: false, tags: ['特色'], description: '广式快餐' },
    { name: '港式奶茶', cuisine_type: '饮品', rating: 4.3, price_range: '¥12-25', is_featured: false, tags: ['特色'], description: '港式饮品' },
    { name: '鸡蛋仔', cuisine_type: '甜品', rating: 4.2, price_range: '¥10-20', is_featured: false, tags: ['特色'], description: '港式小吃' },
    { name: '菠萝油', cuisine_type: '粤菜', rating: 4.3, price_range: '¥12-25', is_featured: false, tags: ['特色'], description: '港式茶点' },
  ])
  
  // 桂林美食 (30个)
  addCityFoods('桂林', [
    { name: '桂林米粉', cuisine_type: '小吃', rating: 4.8, price_range: '¥10-20', is_featured: true, tags: ['必吃', '特色'], description: '桂林传统美食' },
    { name: '荔浦扣肉', cuisine_type: '桂菜', rating: 4.5, price_range: '¥40-70', is_featured: false, tags: ['特色'], description: '桂林传统名菜' },
    { name: '阳朔啤酒鱼', cuisine_type: '桂菜', rating: 4.6, price_range: '¥60-100', is_featured: false, tags: ['特色'], description: '阳朔特色菜' },
    { name: '全州醋血鸭', cuisine_type: '桂菜', rating: 4.4, price_range: '¥45-80', is_featured: false, tags: ['特色'], description: '全州传统名菜' },
    { name: '平乐十八酿', cuisine_type: '桂菜', rating: 4.3, price_range: '¥35-65', is_featured: false, tags: ['特色'], description: '平乐特色菜' },
    { name: '桂林马肉米粉', cuisine_type: '小吃', rating: 4.3, price_range: '¥15-30', is_featured: false, tags: ['特色'], description: '桂林特色米粉' },
    { name: '全州禾花鱼', cuisine_type: '桂菜', rating: 4.4, price_range: '¥40-75', is_featured: false, tags: ['特色'], description: '全州特色菜' },
    { name: '阳朔田螺酿', cuisine_type: '桂菜', rating: 4.3, price_range: '¥35-65', is_featured: false, tags: ['特色'], description: '阳朔特色菜' },
    { name: '恭城油茶', cuisine_type: '小吃', rating: 4.2, price_range: '¥8-15', is_featured: false, tags: ['特色'], description: '恭城传统饮品' },
    { name: '龙脊竹筒饭', cuisine_type: '桂菜', rating: 4.3, price_range: '¥20-40', is_featured: false, tags: ['特色'], description: '龙胜特色美食' },
    { name: '兴安白果', cuisine_type: '桂菜', rating: 4.1, price_range: '¥15-30', is_featured: false, tags: ['特色'], description: '兴安特产' },
    { name: '阳朔糍粑', cuisine_type: '甜品', rating: 4.0, price_range: '¥8-15', is_featured: false, tags: ['特色'], description: '阳朔传统小吃' },
    { name: '灌阳红薯粉', cuisine_type: '小吃', rating: 4.2, price_range: '¥12-25', is_featured: false, tags: ['特色'], description: '灌阳特产' },
    { name: '资源竹笋', cuisine_type: '桂菜', rating: 4.1, price_range: '¥20-40', is_featured: false, tags: ['特色'], description: '资源特产' },
    { name: '永福罗汉果', cuisine_type: '饮品', rating: 4.3, price_range: '¥15-35', is_featured: false, tags: ['特色'], description: '永福特产' },
    { name: '平乐沙田柚', cuisine_type: '甜品', rating: 4.2, price_range: '¥15-35', is_featured: false, tags: ['特色'], description: '平乐特产' },
    { name: '恭城月柿', cuisine_type: '甜品', rating: 4.1, price_range: '¥12-28', is_featured: false, tags: ['特色'], description: '恭城特产' },
    { name: '荔浦芋', cuisine_type: '桂菜', rating: 4.4, price_range: '¥25-45', is_featured: false, tags: ['特色'], description: '荔浦特产' },
    { name: '桂林三花酒', cuisine_type: '饮品', rating: 4.4, price_range: '¥30-80', is_featured: false, tags: ['特色'], description: '桂林特产酒' },
    { name: '桂林田螺', cuisine_type: '小吃', rating: 4.2, price_range: '¥15-30', is_featured: false, tags: ['特色'], description: '桂林夜宵美食' },
    { name: '马蹄糕', cuisine_type: '甜品', rating: 4.1, price_range: '¥10-20', is_featured: false, tags: ['特色'], description: '桂林传统糕点' },
    { name: '桂花糕', cuisine_type: '甜品', rating: 4.3, price_range: '¥12-25', is_featured: false, tags: ['特色'], description: '桂林传统糕点' },
    { name: '尼姑素面', cuisine_type: '小吃', rating: 4.2, price_range: '¥15-30', is_featured: false, tags: ['特色'], description: '桂林特色面食' },
    { name: '桂林松糕', cuisine_type: '甜品', rating: 4.1, price_range: '¥10-20', is_featured: false, tags: ['特色'], description: '桂林传统糕点' },
    { name: '桂林水糍粑', cuisine_type: '甜品', rating: 4.0, price_range: '¥8-15', is_featured: false, tags: ['特色'], description: '桂林传统小吃' },
    { name: '桂林腐乳', cuisine_type: '小吃', rating: 4.2, price_range: '¥15-30', is_featured: false, tags: ['特色'], description: '桂林特产' },
    { name: '桂林辣椒酱', cuisine_type: '小吃', rating: 4.3, price_range: '¥10-25', is_featured: false, tags: ['特色'], description: '桂林特产' },
    { name: '阳朔啤酒', cuisine_type: '饮品', rating: 4.2, price_range: '¥15-30', is_featured: false, tags: ['特色'], description: '阳朔特产' },
    { name: '罗汉果', cuisine_type: '饮品', rating: 4.1, price_range: '¥10-25', is_featured: false, tags: ['特色'], description: '桂林特产' },
  ])
  
  // 张家界美食 (30个)
  addCityFoods('张家界', [
    { name: '土家三下锅', cuisine_type: '湘菜', rating: 4.7, price_range: '¥40-70', is_featured: true, tags: ['必吃', '特色'], description: '张家界传统名菜' },
    { name: '岩耳炖鸡', cuisine_type: '湘菜', rating: 4.5, price_range: '¥60-100', is_featured: false, tags: ['特色'], description: '张家界特色菜' },
    { name: '土家腊肉', cuisine_type: '湘菜', rating: 4.6, price_range: '¥50-90', is_featured: false, tags: ['特色'], description: '张家界特色美食' },
    { name: '土家血豆腐', cuisine_type: '湘菜', rating: 4.3, price_range: '¥25-45', is_featured: false, tags: ['特色'], description: '张家界传统菜' },
    { name: '蒿子粑粑', cuisine_type: '小吃', rating: 4.2, price_range: '¥8-15', is_featured: false, tags: ['特色'], description: '张家界传统小吃' },
    { name: '合渣', cuisine_type: '湘菜', rating: 4.1, price_range: '¥15-30', is_featured: false, tags: ['特色'], description: '张家界传统菜' },
    { name: '草帽面', cuisine_type: '小吃', rating: 4.3, price_range: '¥12-25', is_featured: false, tags: ['特色'], description: '张家界特色面食' },
    { name: '糖油粑粑', cuisine_type: '甜品', rating: 4.2, price_range: '¥8-15', is_featured: false, tags: ['特色'], description: '张家界传统甜品' },
    { name: '土家粉蒸肉', cuisine_type: '湘菜', rating: 4.4, price_range: '¥35-60', is_featured: false, tags: ['特色'], description: '张家界传统菜' },
    { name: '社饭', cuisine_type: '湘菜', rating: 4.1, price_range: '¥15-30', is_featured: false, tags: ['特色'], description: '张家界传统美食' },
    { name: '糍粑', cuisine_type: '甜品', rating: 4.0, price_range: '¥8-15', is_featured: false, tags: ['特色'], description: '张家界传统小吃' },
    { name: '腊猪蹄', cuisine_type: '湘菜', rating: 4.3, price_range: '¥50-90', is_featured: false, tags: ['特色'], description: '张家界特色菜' },
    { name: '土家香肠', cuisine_type: '湘菜', rating: 4.2, price_range: '¥35-65', is_featured: false, tags: ['特色'], description: '张家界特产' },
    { name: '玉米饭', cuisine_type: '湘菜', rating: 4.1, price_range: '¥10-20', is_featured: false, tags: ['特色'], description: '张家界传统主食' },
    { name: '张家界米粉', cuisine_type: '小吃', rating: 4.3, price_range: '¥10-20', is_featured: false, tags: ['特色'], description: '张家界特色早餐' },
    { name: '豆腐脑', cuisine_type: '小吃', rating: 4.0, price_range: '¥5-10', is_featured: false, tags: ['特色'], description: '张家界传统早餐' },
    { name: '油条', cuisine_type: '小吃', rating: 3.9, price_range: '¥2-5', is_featured: false, tags: ['特色'], description: '张家界传统早餐' },
    { name: '包子', cuisine_type: '小吃', rating: 4.0, price_range: '¥2-5', is_featured: false, tags: ['特色'], description: '张家界传统早餐' },
    { name: '馒头', cuisine_type: '小吃', rating: 3.9, price_range: '¥1-3', is_featured: false, tags: ['特色'], description: '张家界传统主食' },
    { name: '粥', cuisine_type: '小吃', rating: 4.0, price_range: '¥5-10', is_featured: false, tags: ['特色'], description: '张家界传统早餐' },
    { name: '葛根粉', cuisine_type: '甜品', rating: 4.1, price_range: '¥15-30', is_featured: false, tags: ['特色'], description: '张家界特产' },
    { name: '猕猴桃', cuisine_type: '甜品', rating: 4.2, price_range: '¥10-25', is_featured: false, tags: ['特色'], description: '张家界特产' },
    { name: '岩耳', cuisine_type: '湘菜', rating: 4.0, price_range: '¥40-80', is_featured: false, tags: ['特色'], description: '张家界特产' },
    { name: '杜仲茶', cuisine_type: '饮品', rating: 4.1, price_range: '¥15-35', is_featured: false, tags: ['特色'], description: '张家界特产' },
    { name: '张家界酒', cuisine_type: '饮品', rating: 4.0, price_range: '¥30-80', is_featured: false, tags: ['特色'], description: '张家界特产' },
    { name: '土家鸡', cuisine_type: '湘菜', rating: 4.3, price_range: '¥45-80', is_featured: false, tags: ['特色'], description: '张家界特色菜' },
    { name: '土家蒸肉', cuisine_type: '湘菜', rating: 4.2, price_range: '¥35-65', is_featured: false, tags: ['特色'], description: '张家界传统菜' },
    { name: '土家腌菜', cuisine_type: '湘菜', rating: 4.1, price_range: '¥10-20', is_featured: false, tags: ['特色'], description: '张家界传统菜' },
    { name: '土家腊八', cuisine_type: '湘菜', rating: 4.0, price_range: '¥15-30', is_featured: false, tags: ['特色'], description: '张家界传统美食' },
  ])
  
  // 黄山美食 (30个)
  addCityFoods('黄山', [
    { name: '徽州臭鳜鱼', cuisine_type: '徽菜', rating: 4.6, price_range: '¥60-100', is_featured: true, tags: ['必吃', '特色'], description: '黄山传统名菜' },
    { name: '徽州毛豆腐', cuisine_type: '徽菜', rating: 4.5, price_range: '¥15-30', is_featured: false, tags: ['特色'], description: '黄山特色小吃' },
    { name: '黄山烧饼', cuisine_type: '小吃', rating: 4.4, price_range: '¥10-20', is_featured: false, tags: ['特色'], description: '黄山传统小吃' },
    { name: '徽州刀板香', cuisine_type: '徽菜', rating: 4.3, price_range: '¥45-80', is_featured: false, tags: ['特色'], description: '黄山传统名菜' },
    { name: '问政山笋', cuisine_type: '徽菜', rating: 4.2, price_range: '¥30-55', is_featured: false, tags: ['特色'], description: '黄山特色菜' },
    { name: '黄山双石', cuisine_type: '徽菜', rating: 4.1, price_range: '¥80-150', is_featured: false, tags: ['特色'], description: '黄山特色菜' },
    { name: '五城茶干', cuisine_type: '小吃', rating: 4.0, price_range: '¥10-25', is_featured: false, tags: ['特色'], description: '黄山特产' },
    { name: '黄山炖鸽', cuisine_type: '徽菜', rating: 4.0, price_range: '¥60-110', is_featured: false, tags: ['特色'], description: '黄山特色菜' },
    { name: '徽州圆子', cuisine_type: '徽菜', rating: 4.2, price_range: '¥25-50', is_featured: false, tags: ['特色'], description: '黄山传统菜' },
    { name: '黄山蕨菜', cuisine_type: '徽菜', rating: 4.1, price_range: '¥20-40', is_featured: false, tags: ['特色'], description: '黄山特色菜' },
    { name: '红烧臭鳜鱼', cuisine_type: '徽菜', rating: 4.3, price_range: '¥65-110', is_featured: false, tags: ['特色'], description: '黄山传统名菜' },
    { name: '问政山笋煲', cuisine_type: '徽菜', rating: 4.2, price_range: '¥35-65', is_featured: false, tags: ['特色'], description: '黄山特色菜' },
    { name: '胡适一品锅', cuisine_type: '徽菜', rating: 4.4, price_range: '¥70-120', is_featured: false, tags: ['特色'], description: '黄山传统名菜' },
    { name: '火腿炖甲鱼', cuisine_type: '徽菜', rating: 4.3, price_range: '¥100-200', is_featured: false, tags: ['特色'], description: '黄山高档菜' },
    { name: '沙地马蹄鳖', cuisine_type: '徽菜', rating: 4.2, price_range: '¥90-180', is_featured: false, tags: ['特色'], description: '黄山特色菜' },
    { name: '石耳炖石鸡', cuisine_type: '徽菜', rating: 4.2, price_range: '¥85-170', is_featured: false, tags: ['特色'], description: '黄山特色菜' },
    { name: '挞粿', cuisine_type: '小吃', rating: 4.0, price_range: '¥8-18', is_featured: false, tags: ['特色'], description: '黄山传统小吃' },
    { name: '毛豆腐', cuisine_type: '徽菜', rating: 4.3, price_range: '¥15-30', is_featured: false, tags: ['特色'], description: '黄山特色小吃' },
    { name: '油煎毛豆腐', cuisine_type: '徽菜', rating: 4.2, price_range: '¥18-35', is_featured: false, tags: ['特色'], description: '黄山特色小吃' },
    { name: '徽州裹粽', cuisine_type: '小吃', rating: 4.1, price_range: '¥8-18', is_featured: false, tags: ['特色'], description: '黄山传统小吃' },
    { name: '徽州状元饭', cuisine_type: '徽菜', rating: 4.2, price_range: '¥25-50', is_featured: false, tags: ['特色'], description: '黄山传统美食' },
    { name: '虎皮毛豆腐', cuisine_type: '徽菜', rating: 4.3, price_range: '¥20-40', is_featured: false, tags: ['特色'], description: '黄山特色菜' },
    { name: '徽州石鸡', cuisine_type: '徽菜', rating: 4.2, price_range: '¥80-150', is_featured: false, tags: ['特色'], description: '黄山特色菜' },
    { name: '徽州桃脂烧肉', cuisine_type: '徽菜', rating: 4.1, price_range: '¥40-75', is_featured: false, tags: ['特色'], description: '黄山传统菜' },
    { name: '徽州蒸鸡', cuisine_type: '徽菜', rating: 4.1, price_range: '¥50-90', is_featured: false, tags: ['特色'], description: '黄山传统菜' },
    { name: '黟县腊八豆腐', cuisine_type: '小吃', rating: 4.0, price_range: '¥12-25', is_featured: false, tags: ['特色'], description: '黟县特产' },
    { name: '徽州臭豆腐', cuisine_type: '小吃', rating: 4.2, price_range: '¥10-20', is_featured: false, tags: ['特色'], description: '黄山特色小吃' },
    { name: '黄山猕猴桃', cuisine_type: '甜品', rating: 4.1, price_range: '¥15-35', is_featured: false, tags: ['特色'], description: '黄山特产' },
  ])
  
  // 九寨沟美食 (30个)
  addCityFoods('九寨沟', [
    { name: '牦牛肉', cuisine_type: '藏菜', rating: 4.7, price_range: '¥60-120', is_featured: true, tags: ['必吃', '特色'], description: '九寨沟特色美食' },
    { name: '酥油茶', cuisine_type: '藏菜', rating: 4.5, price_range: '¥10-20', is_featured: false, tags: ['特色'], description: '藏族传统饮品' },
    { name: '糌粑', cuisine_type: '藏菜', rating: 4.3, price_range: '¥8-15', is_featured: false, tags: ['特色'], description: '藏族传统主食' },
    { name: '青稞酒', cuisine_type: '饮品', rating: 4.4, price_range: '¥20-50', is_featured: false, tags: ['特色'], description: '藏族传统酒' },
    { name: '洋芋糍粑', cuisine_type: '藏菜', rating: 4.2, price_range: '¥15-30', is_featured: false, tags: ['特色'], description: '九寨沟特色小吃' },
    { name: '九寨柿饼', cuisine_type: '甜品', rating: 4.1, price_range: '¥12-25', is_featured: false, tags: ['特色'], description: '九寨沟特产' },
    { name: '酸菜面块', cuisine_type: '藏菜', rating: 4.0, price_range: '¥15-30', is_featured: false, tags: ['特色'], description: '九寨沟特色面食' },
    { name: '藏族血肠', cuisine_type: '藏菜', rating: 4.2, price_range: '¥25-50', is_featured: false, tags: ['特色'], description: '藏族传统菜' },
    { name: '牦牛肉干', cuisine_type: '小吃', rating: 4.3, price_range: '¥40-80', is_featured: false, tags: ['特色'], description: '九寨沟特产' },
    { name: '奶渣包子', cuisine_type: '藏菜', rating: 4.1, price_range: '¥10-20', is_featured: false, tags: ['特色'], description: '藏族传统小吃' },
    { name: '藏民奶制品', cuisine_type: '甜品', rating: 4.0, price_range: '¥15-30', is_featured: false, tags: ['特色'], description: '藏族特产' },
    { name: '荞麦面食', cuisine_type: '藏菜', rating: 4.1, price_range: '¥10-20', is_featured: false, tags: ['特色'], description: '藏族传统主食' },
    { name: '豌杂面', cuisine_type: '小吃', rating: 4.0, price_range: '¥12-25', is_featured: false, tags: ['特色'], description: '九寨沟特色面食' },
    { name: '酸奶', cuisine_type: '甜品', rating: 4.2, price_range: '¥10-20', is_featured: false, tags: ['特色'], description: '藏族传统甜品' },
    { name: '奶茶', cuisine_type: '饮品', rating: 4.0, price_range: '¥8-15', is_featured: false, tags: ['特色'], description: '藏族传统饮品' },
    { name: '荞麦饼', cuisine_type: '藏菜', rating: 4.1, price_range: '¥8-15', is_featured: false, tags: ['特色'], description: '藏族传统主食' },
    { name: '羊肉汤', cuisine_type: '藏菜', rating: 4.2, price_range: '¥30-60', is_featured: false, tags: ['特色'], description: '藏族传统汤品' },
    { name: '牛肉汤', cuisine_type: '藏菜', rating: 4.1, price_range: '¥35-65', is_featured: false, tags: ['特色'], description: '藏族传统汤品' },
    { name: '面条', cuisine_type: '藏菜', rating: 4.0, price_range: '¥10-20', is_featured: false, tags: ['特色'], description: '藏族传统面食' },
    { name: '米饭', cuisine_type: '藏菜', rating: 3.9, price_range: '¥5-10', is_featured: false, tags: ['特色'], description: '藏族传统主食' },
    { name: '手抓肉', cuisine_type: '藏菜', rating: 4.3, price_range: '¥50-100', is_featured: false, tags: ['特色'], description: '藏族传统菜' },
    { name: '烤全羊', cuisine_type: '藏菜', rating: 4.4, price_range: '¥200-500', is_featured: false, tags: ['特色'], description: '藏族盛宴' },
    { name: '藏式火锅', cuisine_type: '火锅', rating: 4.2, price_range: '¥60-120', is_featured: false, tags: ['特色'], description: '藏族特色火锅' },
    { name: '人参果饭', cuisine_type: '藏菜', rating: 4.0, price_range: '¥20-40', is_featured: false, tags: ['特色'], description: '藏族传统主食' },
    { name: '虫草鸭', cuisine_type: '藏菜', rating: 4.1, price_range: '¥100-200', is_featured: false, tags: ['特色'], description: '藏族高档菜' },
    { name: '九寨黄瓜', cuisine_type: '藏菜', rating: 4.0, price_range: '¥10-20', is_featured: false, tags: ['特色'], description: '九寨沟特产' },
    { name: '羊肉泡馍', cuisine_type: '藏菜', rating: 4.1, price_range: '¥25-50', is_featured: false, tags: ['特色'], description: '藏族传统美食' },
    { name: '风干牛肉', cuisine_type: '小吃', rating: 4.2, price_range: '¥35-70', is_featured: false, tags: ['特色'], description: '藏族特产' },
    { name: '奶皮', cuisine_type: '甜品', rating: 4.0, price_range: '¥12-25', is_featured: false, tags: ['特色'], description: '藏族传统甜品' },
    { name: '油炸酸奶', cuisine_type: '甜品', rating: 4.1, price_range: '¥15-30', is_featured: false, tags: ['特色'], description: '藏族特色甜品' },
  ])
  
  // 大理美食 (30个)
  addCityFoods('大理', [
    { name: '烤乳扇', cuisine_type: '云南菜', rating: 4.5, price_range: '¥10-20', is_featured: true, tags: ['必吃', '特色'], description: '大理特色小吃' },
    { name: '大理生皮', cuisine_type: '云南菜', rating: 4.3, price_range: '¥40-80', is_featured: false, tags: ['特色'], description: '白族传统菜' },
    { name: '大理酸辣鱼', cuisine_type: '云南菜', rating: 4.4, price_range: '¥45-85', is_featured: false, tags: ['特色'], description: '大理特色菜' },
    { name: '喜洲粑粑', cuisine_type: '云南菜', rating: 4.3, price_range: '¥8-15', is_featured: false, tags: ['特色'], description: '喜洲传统小吃' },
    { name: '凉鸡米线', cuisine_type: '云南菜', rating: 4.4, price_range: '¥15-30', is_featured: false, tags: ['特色'], description: '大理特色面食' },
    { name: '砂锅鱼', cuisine_type: '云南菜', rating: 4.5, price_range: '¥50-100', is_featured: false, tags: ['特色'], description: '大理特色菜' },
    { name: '巍山耙肉饵丝', cuisine_type: '云南菜', rating: 4.3, price_range: '¥15-30', is_featured: false, tags: ['特色'], description: '巍山特色小吃' },
    { name: '雕梅扣肉', cuisine_type: '云南菜', rating: 4.2, price_range: '¥40-75', is_featured: false, tags: ['特色'], description: '大理传统菜' },
    { name: '永平黄焖鸡', cuisine_type: '云南菜', rating: 4.4, price_range: '¥45-85', is_featured: false, tags: ['特色'], description: '永平特色菜' },
    { name: '雕梅酒', cuisine_type: '饮品', rating: 4.1, price_range: '¥25-50', is_featured: false, tags: ['特色'], description: '大理特产酒' },
    { name: '白族土八碗', cuisine_type: '云南菜', rating: 4.3, price_range: '¥80-150', is_featured: false, tags: ['特色'], description: '白族传统宴席' },
    { name: '大理洱海砂锅鱼', cuisine_type: '云南菜', rating: 4.4, price_range: '¥60-110', is_featured: false, tags: ['特色'], description: '大理特色菜' },
    { name: '剑川八大碗', cuisine_type: '云南菜', rating: 4.2, price_range: '¥70-130', is_featured: false, tags: ['特色'], description: '剑川传统宴席' },
    { name: '云龙诺邓火腿', cuisine_type: '云南菜', rating: 4.5, price_range: '¥60-120', is_featured: false, tags: ['特色'], description: '诺邓特产' },
    { name: '南涧锅巴油粉', cuisine_type: '云南菜', rating: 4.1, price_range: '¥10-20', is_featured: false, tags: ['特色'], description: '南涧特色小吃' },
    { name: '漾濞卷粉', cuisine_type: '云南菜', rating: 4.2, price_range: '¥8-18', is_featured: false, tags: ['特色'], description: '漾濞特色小吃' },
    { name: '宾川韭菜腌菜', cuisine_type: '云南菜', rating: 4.0, price_range: '¥8-15', is_featured: false, tags: ['特色'], description: '宾川特产' },
    { name: '烤饵块', cuisine_type: '云南菜', rating: 4.1, price_range: '¥5-12', is_featured: false, tags: ['特色'], description: '大理传统小吃' },
    { name: '大理凉粉', cuisine_type: '云南菜', rating: 4.0, price_range: '¥8-15', is_featured: false, tags: ['特色'], description: '大理传统小吃' },
    { name: '耙肉饵丝', cuisine_type: '云南菜', rating: 4.2, price_range: '¥12-25', is_featured: false, tags: ['特色'], description: '大理特色面食' },
    { name: '大理锅锅菜', cuisine_type: '云南菜', rating: 4.1, price_range: '¥35-70', is_featured: false, tags: ['特色'], description: '大理传统菜' },
    { name: '白族三道茶', cuisine_type: '饮品', rating: 4.0, price_range: '¥15-35', is_featured: false, tags: ['特色'], description: '白族传统饮品' },
    { name: '大理梅子', cuisine_type: '甜品', rating: 4.1, price_range: '¥10-25', is_featured: false, tags: ['特色'], description: '大理特产' },
    { name: '双乳扇', cuisine_type: '云南菜', rating: 4.2, price_range: '¥12-25', is_featured: false, tags: ['特色'], description: '大理特色小吃' },
    { name: '大理黑桂鱼', cuisine_type: '云南菜', rating: 4.3, price_range: '¥55-110', is_featured: false, tags: ['特色'], description: '大理特色菜' },
    { name: '苍山雪鱼', cuisine_type: '云南菜', rating: 4.2, price_range: '¥60-120', is_featured: false, tags: ['特色'], description: '大理特色菜' },
    { name: '大理雪茶', cuisine_type: '饮品', rating: 4.1, price_range: '¥20-45', is_featured: false, tags: ['特色'], description: '大理特产' },
    { name: '西瓜酱', cuisine_type: '云南菜', rating: 4.0, price_range: '¥8-18', is_featured: false, tags: ['特色'], description: '大理传统小吃' },
    { name: '大理鱼粥', cuisine_type: '云南菜', rating: 4.1, price_range: '¥25-50', is_featured: false, tags: ['特色'], description: '大理传统粥品' },
    { name: '羊奶乳扇', cuisine_type: '云南菜', rating: 4.2, price_range: '¥15-30', is_featured: false, tags: ['特色'], description: '大理特色小吃' },
  ])
  
  // 丽江美食 (30个)
  addCityFoods('丽江', [
    { name: '腊排骨火锅', cuisine_type: '云南菜', rating: 4.7, price_range: '¥60-100', is_featured: true, tags: ['必吃', '特色'], description: '丽江特色美食' },
    { name: '水性杨花', cuisine_type: '云南菜', rating: 4.4, price_range: '¥25-45', is_featured: false, tags: ['特色'], description: '丽江特色菜' },
    { name: '丽江粑粑', cuisine_type: '云南菜', rating: 4.3, price_range: '¥8-15', is_featured: false, tags: ['特色'], description: '纳西族传统小吃' },
    { name: '纳西烤肉', cuisine_type: '云南菜', rating: 4.5, price_range: '¥40-75', is_featured: false, tags: ['特色'], description: '纳西族传统菜' },
    { name: '鸡豆凉粉', cuisine_type: '云南菜', rating: 4.4, price_range: '¥10-20', is_featured: false, tags: ['特色'], description: '丽江传统小吃' },
    { name: '包浆豆腐', cuisine_type: '云南菜', rating: 4.3, price_range: '¥15-30', is_featured: false, tags: ['特色'], description: '丽江特色小吃' },
    { name: '黑山羊火锅', cuisine_type: '云南菜', rating: 4.5, price_range: '¥70-120', is_featured: false, tags: ['特色'], description: '丽江特色火锅' },
    { name: '松茸', cuisine_type: '云南菜', rating: 4.6, price_range: '¥100-300', is_featured: false, tags: ['特色'], description: '丽江珍贵食材' },
    { name: '纳西烤鱼', cuisine_type: '云南菜', rating: 4.4, price_range: '¥45-85', is_featured: false, tags: ['特色'], description: '纳西族传统菜' },
    { name: '洋芋鸡', cuisine_type: '云南菜', rating: 4.3, price_range: '¥50-95', is_featured: false, tags: ['特色'], description: '丽江特色菜' },
    { name: '汽锅鸡', cuisine_type: '云南菜', rating: 4.5, price_range: '¥60-110', is_featured: false, tags: ['特色'], description: '云南传统名菜' },
    { name: '过桥米线', cuisine_type: '云南菜', rating: 4.6, price_range: '¥25-50', is_featured: false, tags: ['特色'], description: '云南经典美食' },
    { name: '酸汤鱼', cuisine_type: '云南菜', rating: 4.3, price_range: '¥50-95', is_featured: false, tags: ['特色'], description: '丽江特色菜' },
    { name: '凉粉', cuisine_type: '云南菜', rating: 4.2, price_range: '¥8-15', is_featured: false, tags: ['特色'], description: '丽江传统小吃' },
    { name: '米线', cuisine_type: '云南菜', rating: 4.1, price_range: '¥12-25', is_featured: false, tags: ['特色'], description: '丽江特色面食' },
    { name: '饵丝', cuisine_type: '云南菜', rating: 4.0, price_range: '¥10-20', is_featured: false, tags: ['特色'], description: '丽江特色面食' },
    { name: '小白菜', cuisine_type: '云南菜', rating: 4.0, price_range: '¥8-15', is_featured: false, tags: ['特色'], description: '丽江特色蔬菜' },
    { name: '青菜', cuisine_type: '云南菜', rating: 3.9, price_range: '¥6-12', is_featured: false, tags: ['特色'], description: '丽江特色蔬菜' },
    { name: '土豆', cuisine_type: '云南菜', rating: 4.0, price_range: '¥8-15', is_featured: false, tags: ['特色'], description: '丽江特色蔬菜' },
    { name: '红薯', cuisine_type: '云南菜', rating: 3.9, price_range: '¥6-12', is_featured: false, tags: ['特色'], description: '丽江特色蔬菜' },
    { name: '米灌肠', cuisine_type: '云南菜', rating: 4.2, price_range: '¥15-30', is_featured: false, tags: ['特色'], description: '纳西族传统小吃' },
    { name: '酥油茶', cuisine_type: '云南菜', rating: 4.1, price_range: '¥10-20', is_featured: false, tags: ['特色'], description: '纳西族传统饮品' },
    { name: '雪茶', cuisine_type: '饮品', rating: 4.2, price_range: '¥15-35', is_featured: false, tags: ['特色'], description: '丽江特产' },
    { name: '螺旋藻', cuisine_type: '饮品', rating: 4.0, price_range: '¥20-50', is_featured: false, tags: ['特色'], description: '丽江特产' },
    { name: '东巴烤鱼', cuisine_type: '云南菜', rating: 4.3, price_range: '¥50-90', is_featured: false, tags: ['特色'], description: '纳西族传统菜' },
    { name: '三文鱼', cuisine_type: '云南菜', rating: 4.4, price_range: '¥80-150', is_featured: false, tags: ['特色'], description: '丽江特色菜' },
    { name: '野生菌', cuisine_type: '云南菜', rating: 4.5, price_range: '¥60-120', is_featured: false, tags: ['特色'], description: '丽江特色菜' },
    { name: '鲜花饼', cuisine_type: '甜品', rating: 4.3, price_range: '¥15-35', is_featured: false, tags: ['特色'], description: '云南特产' },
    { name: '丽江腌菜', cuisine_type: '云南菜', rating: 4.1, price_range: '¥8-18', is_featured: false, tags: ['特色'], description: '纳西族传统菜' },
    { name: '丽江酒', cuisine_type: '饮品', rating: 4.2, price_range: '¥25-55', is_featured: false, tags: ['特色'], description: '丽江特产' },
  ])
  
  return foods
}

// 美食数据
const foods = ref(generateFoodsData())

// 筛选后的景点
const filteredSpots = computed(() => {
  return spots.value.filter(spot => spot.city === selectedCity.value)
})

// 筛选后的美食
const filteredFoods = computed(() => {
  let result = foods.value.filter(food => food.city === selectedCity.value)
  
  if (selectedCuisine.value !== '全部') {
    result = result.filter(food => food.cuisine_type.includes(selectedCuisine.value))
  }
  
  return result.sort((a, b) => b.rating - a.rating)
})

// 加载景点数据
const loadSpots = async () => {
  loadingSpots.value = true
  try {
    const response = await fetch(`http://localhost:8000/api/spots/recommend?city=${encodeURIComponent(selectedCity.value)}&limit=20`)
    const data = await response.json()
    
    if (data.spots) {
      spots.value = data.spots
    } else if (Array.isArray(data)) {
      spots.value = data
    }
  } catch (error) {
    console.error('加载景点失败:', error)
    // 使用模拟数据
    spots.value = getMockSpots()
  } finally {
    loadingSpots.value = false
  }
}

// 模拟景点数据
const getMockSpots = () => {
  const mockData = {
    '北京': [
      { id: 1, name: '故宫博物院', rating: 4.9, tags: ['建筑宏伟', '历史厚重'], images: ['/images/spots/beijing/beijing_gugong_bowuyuan.jpg'], description: '中国明清两代的皇家宫殿，是世界上现存规模最大、保存最为完整的木质结构古建筑之一。' },
      { id: 2, name: '天坛公园', rating: 4.9, tags: ['古建绝美', '声学奇迹'], images: ['/images/spots/beijing/beijing_tiantan_gongyuan.jpg'], description: '明清两代皇帝祭天的场所，是中国现存最大的古代祭祀建筑群。' },
      { id: 3, name: '颐和园', rating: 4.9, tags: ['皇家园林', '湖光山色'], images: ['/images/spots/beijing/beijing_yiheyuan.jpg'], description: '中国清朝时期皇家园林，被誉为"皇家园林博物馆"。' },
      { id: 4, name: '长城-八达岭', rating: 4.8, tags: ['必玩景点', '地标建筑'], images: ['/images/spots/beijing/beijing_badaling_changcheng.jpg'], description: '万里长城的重要组成部分，是明长城的一个隘口。' },
      { id: 5, name: '天安门广场', rating: 4.8, tags: ['升旗仪式', '庄严神圣'], images: ['/images/spots/beijing/beijing_tiananmen_guangchang.jpg'], description: '世界上最大的城市广场之一，是中国的象征。' },
      { id: 6, name: '圆明园', rating: 4.7, tags: ['历史遗址', '园林景观'], images: ['/images/spots/beijing/beijing_yuanmingyuan.jpg'], description: '清代大型皇家园林，有"万园之园"之称。' },
      { id: 287, name: '北京邮电大学（本部）', rating: 4.8, tags: ['学府', '导航测试'], images: ['/images/spots/beijing/beijing_beijing_daxue.jpg'], description: '可直接进入详情页并体验北邮本部内部导航测试。' },
    ],
    '上海': [
      { id: 11, name: '外滩', rating: 4.9, tags: ['地标建筑', '夜景绝美'], images: ['/images/spots/shanghai/shanghai_waitan.jpg'], description: '上海的标志性景观，拥有万国建筑博览群。' },
      { id: 12, name: '东方明珠', rating: 4.7, tags: ['地标建筑', '登高望远'], images: ['/images/spots/shanghai/shanghai_dongfang_mingzhu.jpg'], description: '上海标志性文化景观之一，是亚洲第一、世界第三的高塔。' },
      { id: 13, name: '豫园', rating: 4.8, tags: ['江南园林', '历史文化'], images: ['/images/spots/shanghai/shanghai_yuyuan.jpg'], description: '明代私人园林，充分体现了中国古典园林的设计与建造水平。' },
    ],
    '西安': [
      { id: 21, name: '兵马俑', rating: 4.9, tags: ['世界遗产', '历史厚重'], images: ['/images/spots/xian/xian_bingmayong.jpg'], description: '世界第八大奇迹，秦始皇陵的陪葬坑。' },
      { id: 22, name: '大雁塔', rating: 4.8, tags: ['古建绝美', '佛教文化'], images: ['/images/spots/xian/xian_dayanta.jpg'], description: '唐代佛教建筑艺术杰作，是古城西安的独特标志。' },
      { id: 23, name: '古城墙', rating: 4.7, tags: ['历史遗迹', '骑行游览'], images: ['/images/spots/xian/xian_xian_chengqiang.jpg'], description: '中国现存规模最大、保存最完整的古代城垣。' },
    ],
  }
  return mockData[selectedCity.value] || []
}

// 显示景点详情
const showSpotDetail = (spot) => {
  currentSpot.value = spot
  showSpotModal.value = true
}

const goToSpotDetail = (spot) => {
  showSpotModal.value = false
  router.push({ path: '/spot', query: { id: spot.id, city: spot.city } })
}

// 显示美食详情
const showFoodDetail = (food) => {
  currentFood.value = food
  showFoodModal.value = true
}

// 格式化数字
const formatNumber = (num) => {
  if (num >= 10000) {
    return (num / 10000).toFixed(1) + 'w'
  } else if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'k'
  }
  return num.toString()
}

// 监听城市变化，重新加载景点
watch(selectedCity, () => {
  loadSpots()
}, { immediate: true })
</script>

<style scoped>
.explore-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #0a0a1a 0%, #1a1a2e 50%, #16213e 100%);
  color: #fff;
}

/* 主容器 */
.explore-container {
  display: flex;
  padding-top: 70px;
  min-height: 100vh;
}

/* 左侧边栏 */
.sidebar {
  width: 280px;
  background: rgba(20, 20, 40, 0.6);
  backdrop-filter: blur(20px);
  border-right: 1px solid rgba(0, 212, 255, 0.1);
  padding: 30px 20px;
  position: fixed;
  left: 0;
  top: 70px;
  bottom: 0;
  overflow-y: auto;
}

.sidebar-header {
  margin-bottom: 30px;
}

.sidebar-header h2 {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 8px;
  background: linear-gradient(135deg, #00d4ff, #fff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.sidebar-header p {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.5);
}

/* 侧边栏导航 */
.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 30px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 18px;
  border-radius: 12px;
  border: 1px solid transparent;
  background: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.7);
  font-size: 15px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(0, 212, 255, 0.3);
}

.nav-item.active {
  background: rgba(0, 212, 255, 0.15);
  border-color: rgba(0, 212, 255, 0.5);
  color: #00d4ff;
}

.nav-icon {
  font-size: 20px;
}

/* 城市筛选 */
.city-filter h3 {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 15px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.city-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.city-btn {
  padding: 8px 14px;
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  background: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.7);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.city-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.3);
}

.city-btn.active {
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  border-color: transparent;
  color: #fff;
}

/* 内容区域 */
.content-area {
  flex: 1;
  margin-left: 280px;
  padding: 30px 40px;
}

.section-header {
  margin-bottom: 30px;
}

.section-header h1 {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 10px;
}

.section-header p {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.5);
}

/* 美食分类筛选 */
.cuisine-filter {
  display: flex;
  gap: 10px;
  margin-bottom: 25px;
  flex-wrap: wrap;
}

.filter-btn {
  padding: 8px 16px;
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  background: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.7);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.filter-btn:hover {
  background: rgba(255, 255, 255, 0.1);
}

.filter-btn.active {
  background: rgba(0, 212, 255, 0.2);
  border-color: #00d4ff;
  color: #00d4ff;
}

/* 卡片网格 */
.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 20px;
}

.card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
}

.card:hover {
  transform: translateY(-5px);
  border-color: rgba(0, 212, 255, 0.3);
  box-shadow: 0 10px 30px rgba(0, 212, 255, 0.15);
}

.card-image {
  position: relative;
  height: 160px;
  overflow: hidden;
}

.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.card:hover .card-image img {
  transform: scale(1.05);
}

.card-badge {
  position: absolute;
  top: 10px;
  right: 10px;
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 10px;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(5px);
  border-radius: 20px;
  font-size: 13px;
}

.card-badge.featured {
  background: linear-gradient(135deg, #ff6b6b, #ff8e53);
}

.card-info {
  padding: 16px;
}

.card-info h3 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 10px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.card-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
}

.rating {
  color: #ffd700;
  font-size: 14px;
}

.favorites {
  color: #ff6b6b;
  font-size: 14px;
}

.price {
  color: #00d4ff;
  font-size: 14px;
}

.card-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.tag {
  padding: 4px 10px;
  background: rgba(0, 212, 255, 0.1);
  border-radius: 10px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
}

/* 加载状态 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  color: rgba(255, 255, 255, 0.5);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(255, 255, 255, 0.1);
  border-top-color: #00d4ff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  color: rgba(255, 255, 255, 0.5);
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 15px;
}

/* 弹窗 */
.modal {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(10px);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.modal-content {
  background: rgba(20, 20, 40, 0.95);
  border: 1px solid rgba(0, 212, 255, 0.2);
  border-radius: 20px;
  overflow: hidden;
  max-width: 500px;
  width: 100%;
  position: relative;
}

.modal-close {
  position: absolute;
  top: 15px;
  right: 15px;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: none;
  background: rgba(0, 0, 0, 0.5);
  color: #fff;
  font-size: 20px;
  cursor: pointer;
  z-index: 10;
  transition: all 0.3s ease;
}

.modal-close:hover {
  background: rgba(255, 255, 255, 0.2);
}

.modal-header {
  height: 200px;
  overflow: hidden;
}

.modal-header img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.modal-body {
  padding: 25px;
}

.modal-body h2 {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 12px;
}

.modal-rating {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 15px;
  font-size: 16px;
}

.modal-rating .star {
  color: #ffd700;
}

.modal-meta {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 15px;
}

.modal-tags {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.modal-desc {
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.7;
  font-size: 15px;
  margin-bottom: 18px;
}

.go-detail-btn {
  width: 100%;
  padding: 12px 16px;
  border: none;
  border-radius: 14px;
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  color: #fff;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
}

.go-detail-btn:hover {
  opacity: 0.92;
}

/* 响应式 */
@media (max-width: 1024px) {
  .sidebar {
    width: 240px;
  }
  
  .content-area {
    margin-left: 240px;
    padding: 20px;
  }
  
  .cards-grid {
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  }
}

@media (max-width: 768px) {
  .navbar {
    padding: 12px 20px;
  }
  
  .nav-menu {
    display: none;
  }
  
  .sidebar {
    width: 100%;
    position: relative;
    top: 0;
    border-right: none;
    border-bottom: 1px solid rgba(0, 212, 255, 0.1);
  }
  
  .explore-container {
    flex-direction: column;
  }
  
  .content-area {
    margin-left: 0;
  }
  
  .cards-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 15px;
  }
}
</style>
