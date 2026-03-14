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
            <img :src="spot.image || defaultImage" :alt="spot.name" />
            <div class="spot-rating">
              <span class="heart">♥</span>
              <span>{{ spot.rating }}</span>
            </div>
          </div>
          <div class="spot-info">
            <h3>{{ spot.name }}</h3>
            <p class="spot-desc">{{ spot.description?.slice(0, 30) }}...</p>
            <div class="spot-tags">
              <span v-for="tag in (spot.tags || []).slice(0, 2)" :key="tag" class="tag">{{ tag }}</span>
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

// 使用本地图片 - 城市对应
const cityImages = {
  '北京': '/images/cities/beijing.jpg',
  '上海': '/images/cities/shanghai.jpg',
  '西安': '/images/cities/xian.jpg',
  '成都': '/images/cities/chengdu.jpg',
  '杭州': '/images/cities/suzhou.jpg',
  '重庆': '/images/cities/chongqing.jpg',
  '青岛': '/images/cities/qingdao.jpg',
  '广州': '/images/cities/guangzhou.jpg',
  '苏州': '/images/cities/suzhou.jpg',
  '厦门': '/images/cities/xiamen.jpg',
  '南京': '/images/cities/wuhan.jpg',
  '武汉': '/images/cities/wuhan.jpg',
  '长沙': '/images/cities/chongqing.jpg',
  '深圳': '/images/cities/shanghai.jpg',
  '三亚': '/images/cities/guilin.jpg',
  '桂林': '/images/cities/guilin.jpg',
  '张家界': '/images/cities/jiuzhaigou.jpg',
  '黄山': '/images/cities/huangshan.jpg',
  '九寨沟': '/images/cities/jiuzhaigou.jpg',
  '大理': '/images/cities/dali.jpg',
  '丽江': '/images/cities/dali.jpg',
}

const cityImage = computed(() => {
  return cityImages[cityName.value] || '/images/cities/beijing.jpg'
})

// 北京景点图片映射 - 使用本地真实图片
const beijingSpotImages = {
  '故宫': '/images/spots/beijing-gugong.jpg',
  '故宫博物院': '/images/spots/beijing-gugong.jpg',
  '长城': '/images/spots/beijing-changcheng.jpg',
  '八达岭长城': '/images/spots/beijing-changcheng.jpg',
  '天坛': '/images/spots/beijing-tiantan.jpg',
  '天坛公园': '/images/spots/beijing-tiantan.jpg',
  '天安门': '/images/spots/beijing-tiananmen.jpg',
  '天安门广场': '/images/spots/beijing-tiananmen.jpg',
  '颐和园': '/images/spots/beijing-yiheyuan.jpg',
  '鸟巢': '/images/spots/beijing-niaokong.jpg',
  '国家体育场': '/images/spots/beijing-niaokong.jpg',
}

// 上海景点图片映射
const shanghaiSpotImages = {
  '东方明珠': '/images/spots/shanghai-dongfangmingzhu.jpg',
  '外滩': '/images/spots/shanghai-waitan.jpg',
}

// 西安景点图片映射
const xianSpotImages = {
  '兵马俑': '/images/spots/xian-bingmayong.jpg',
  '大雁塔': '/images/spots/xian-dayanta.jpg',
}

// 成都景点图片映射
const chengduSpotImages = {
  '锦里': '/images/spots/chengdu-jinli.jpg',
  '宽窄巷子': '/images/spots/chengdu-kuanzhai.jpg',
}

// 其他城市景点映射
const citySpotImages = {
  '北京': beijingSpotImages,
  '上海': shanghaiSpotImages,
  '西安': xianSpotImages,
  '成都': chengduSpotImages,
  '重庆': { '洪崖洞': '/images/spots/chongqing-hongyadong.jpg' },
  '大理': { '洱海': '/images/spots/dali-erhai.jpg' },
  '广州': { '小蛮腰': '/images/spots/guangzhou-canton-tower.jpg', '广州塔': '/images/spots/guangzhou-canton-tower.jpg' },
  '黄山': { '光明顶': '/images/spots/huangshan-guangmingding.jpg' },
  '九寨沟': { '五彩池': '/images/spots/jiuzhaigou-wucaichi.jpg' },
  '青岛': { '栈桥': '/images/spots/qingdao-zhanqiao.jpg' },
  '苏州': { '拙政园': '/images/spots/suzhou-zhuozhengyuan.jpg' },
  '武汉': { '黄鹤楼': '/images/spots/wuhan-huanghelou.jpg' },
  '厦门': { '鼓浪屿': '/images/spots/xiamen-gulangyu.jpg' },
}

// 获取景点对应的图片
const getSpotImage = (spotName, city) => {
  const cityImagesMap = citySpotImages[city]
  if (cityImagesMap) {
    for (const [key, value] of Object.entries(cityImagesMap)) {
      if (spotName.includes(key)) {
        return value
      }
    }
  }
  // 如果没有特定映射，使用城市默认图片
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
      spots.value = data.spots.map(s => ({
        ...s,
        // 使用本地景点图片映射
        image: (s.images && s.images.length > 0) ? s.images[0] : getSpotImage(s.name, cityName.value)
      }))
    } else if (Array.isArray(data)) {
      spots.value = data.map(s => ({
        ...s,
        image: (s.images && s.images.length > 0) ? s.images[0] : getSpotImage(s.name, cityName.value)
      }))
    }
  } catch (error) {
    console.error('加载失败:', error)
    // 模拟数据 - 带真实本地图片
    spots.value = [
      { id: 1, name: '故宫博物院', rating: 4.9, category: '历史古迹', description: '世界上现存规模最大的木质结构古建筑', tags: ['必玩景点', '历史文化'], image: '/images/spots/beijing-gugong.jpg' },
      { id: 2, name: '天坛公园', rating: 4.9, category: '历史古迹', description: '明清两代帝王祭祀场所', tags: ['古建绝美'], image: '/images/spots/beijing-tiantan.jpg' },
      { id: 3, name: '颐和园', rating: 4.9, category: '风景名胜', description: '清代皇家园林', tags: ['皇家园林'], image: '/images/spots/beijing-yiheyuan.jpg' },
      { id: 4, name: '八达岭长城', rating: 4.8, category: '历史古迹', description: '万里长城的重要组成部分', tags: ['必玩景点'], image: '/images/spots/beijing-changcheng.jpg' },
      { id: 5, name: '天安门广场', rating: 4.7, category: '历史古迹', description: '世界上最大的城市广场', tags: ['标志性建筑'], image: '/images/spots/beijing-tiananmen.jpg' },
      { id: 6, name: '国家体育场', rating: 4.8, category: '地标建筑', description: '又称鸟巢', tags: ['现代建筑'], image: '/images/spots/beijing-niaokong.jpg' },
    ]
  }
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
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
}

.spot-card {
  background: rgba(20, 20, 40, 0.8);
  border: 1px solid rgba(0, 212, 255, 0.1);
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
}

.spot-card:hover {
  transform: translateY(-5px);
  border-color: #00d4ff;
}

.spot-image {
  position: relative;
  height: 120px;
}

.spot-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.spot-rating {
  position: absolute;
  top: 10px;
  left: 10px;
  background: rgba(0, 0, 0, 0.6);
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.heart {
  color: #ff6b6b;
}

.spot-info {
  padding: 12px;
}

.spot-info h3 {
  font-size: 15px;
  margin-bottom: 6px;
}

.spot-desc {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 8px;
}

.spot-tags {
  display: flex;
  gap: 6px;
}

.tag {
  font-size: 11px;
  padding: 2px 8px;
  background: rgba(0, 212, 255, 0.1);
  border-radius: 10px;
  color: #00d4ff;
}

.empty-state {
  text-align: center;
  padding: 60px;
  color: rgba(255, 255, 255, 0.5);
}
</style>
