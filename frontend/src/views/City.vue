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

// 使用本地图片
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
}

const cityImage = computed(() => {
  return cityImages[cityName.value] || '/images/cities/beijing.jpg'
})

// City-specific images for scenic spots
const citySpotImages = {
  '北京': 'https://images.unsplash.com/photo-1599571234909-29ed5d1321d6?w=800',
  '上海': 'https://images.unsplash.com/photo-1474181487882-5abf3f0ba6c2?w=800',
  '西安': 'https://images.unsplash.com/photo-1724458589661-a2f42eb58aca?w=800',
  '成都': 'https://images.unsplash.com/photo-1622613744987-0e3527fae518?w=800',
  '杭州': 'https://images.unsplash.com/photo-1697730047280-01082430a28a?w=800',
  '重庆': 'https://images.unsplash.com/photo-1567014688543-cc4abffb061a?w=800',
  '青岛': 'https://images.unsplash.com/photo-1718085875432-98c61c603b54?w=800',
  '广州': 'https://images.unsplash.com/photo-1559035871-4b9dcf31885c?w=800',
  '苏州': 'https://images.unsplash.com/photo-1521022741625-63f57c752f95?w=800',
  '厦门': 'https://images.unsplash.com/photo-1660531141240-d5fb7a955822?w=800',
  '南京': 'https://images.unsplash.com/photo-1569517282132-25d22f4573e6?w=800',
  '武汉': 'https://images.unsplash.com/photo-1596496050827-8299e0220de1?w=800',
  '长沙': 'https://images.unsplash.com/photo-1585351363283-95e3d5041053?w=800',
  '深圳': 'https://images.unsplash.com/photo-1558539320-1c71c5c5d8e8?w=800',
  '三亚': 'https://images.unsplash.com/photo-1580821810645-11a8fd7c9f37?w=800',
  '桂林': 'https://images.unsplash.com/photo-1548919973-5cef591cdbc9?w=800',
  '张家界': 'https://images.unsplash.com/photo-1565060169194-19fabf63012f?w=800',
  '黄山': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800',
  '九寨沟': 'https://images.unsplash.com/photo-1574169208507-84376144848b?w=800',
  '大理': 'https://images.unsplash.com/photo-1580870069867-74c57ee1bb07?w=800',
  '丽江': 'https://images.unsplash.com/photo-1529143694754-56f8e0156f33?w=800',
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
        // Use city-specific image if API doesn't provide unique image
        image: (s.images && s.images.length > 0) ? s.images[0] : (citySpotImages[cityName.value] || defaultImage)
      }))
    } else if (Array.isArray(data)) {
      spots.value = data.map(s => ({
        ...s,
        image: (s.images && s.images.length > 0) ? s.images[0] : (citySpotImages[cityName.value] || defaultImage)
      }))
    }
  } catch (error) {
    console.error('加载失败:', error)
    // 模拟数据
    spots.value = [
      { id: 1, name: '故宫博物院', rating: 4.9, category: '历史古迹', description: '世界上现存规模最大的木质结构古建筑', tags: ['必玩景点', '历史文化'] },
      { id: 2, name: '天坛公园', rating: 4.9, category: '历史古迹', description: '明清两代帝王祭祀场所', tags: ['古建绝美'] },
      { id: 3, name: '颐和园', rating: 4.9, category: '风景名胜', description: '清代皇家园林', tags: ['皇家园林'] },
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
