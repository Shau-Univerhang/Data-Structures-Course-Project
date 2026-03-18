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
            <div class="spot-badges">
              <div class="badge rating-badge" v-if="spot.rating">
                <span class="star">★</span>
                <span>{{ spot.rating.toFixed(1) }}</span>
              </div>
              <div class="badge fav-badge" v-if="spot.collection_count">
                <span class="heart">♥</span>
                <span>{{ formatNumber(spot.collection_count) }}</span>
              </div>
            </div>
          </div>
          <div class="spot-content">
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
import { ref, computed, onMounted } from 'vue'
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

const loadSpots = async () => {
  try {
    const response = await fetch(`http://localhost:8000/api/spots/recommend?city=${encodeURIComponent(cityName.value)}`)
    const data = await response.json()
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
