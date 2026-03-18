<template>
  <div class="spot-recommend-page">
    <!-- 导航栏 -->
    <Navbar />

    <div class="page-content">
      <!-- 页面标题 -->
      <div class="page-header">
        <h1 class="page-title">为您推荐 {{ city }} 景点</h1>
        <p class="page-subtitle">根据您的偏好智能排序，点击景点加入行程</p>
      </div>

      <!-- 已选择景点数 -->
      <div class="selected-count" v-if="selectedSpots.length > 0">
        <span>已选择 {{ selectedSpots.length }} 个景点</span>
        <button class="clear-btn" @click="clearSelection">清空</button>
      </div>

      <!-- 景点列表 -->
      <div class="spots-grid">
        <div
          v-for="spot in sortedSpots"
          :key="spot.id"
          class="spot-card"
          :class="{ selected: isSelected(spot.id) }"
          @click="toggleSpot(spot)"
        >
          <div class="spot-image">
            <img :src="spot.images?.[0] || `/images/cities/${getCityImageName(spot.city)}`" :alt="spot.name" />
            <div class="spot-rank" v-if="spot.rank <= 3">
              <span>TOP {{ spot.rank }}</span>
            </div>
            <div class="select-indicator" v-if="isSelected(spot.id)">
              <span>✓</span>
            </div>
          </div>
          
          <div class="spot-info">
            <h3 class="spot-name">{{ spot.name }}</h3>
            
            <!-- 评分和收藏 -->
            <div class="spot-stats">
              <div class="stat-item">
                <span class="stat-icon">⭐</span>
                <span class="stat-value">{{ spot.rating?.toFixed(1) || '4.5' }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-icon">❤️</span>
                <span class="stat-value">{{ formatNumber(spot.favorites || 0) }}</span>
              </div>
            </div>

            <!-- 标签匹配度 -->
            <div class="tag-match" v-if="getMatchCount(spot) > 0">
              <span class="match-badge">匹配 {{ getMatchCount(spot) }} 个偏好</span>
            </div>

            <!-- 景点标签 -->
            <div class="spot-tags">
              <span v-for="tag in (spot.tags || []).slice(0, 3)" :key="tag" class="tag">
                {{ tag }}
              </span>
            </div>

            <!-- 推荐理由 -->
            <div class="recommend-reason" v-if="spot.recommendReason">
              <span>💡 {{ spot.recommendReason }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="sortedSpots.length === 0 && !loading" class="empty-state">
        <span class="empty-icon">🔍</span>
        <p>暂无景点数据</p>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-container">
        <div class="loading-spinner"></div>
        <p>正在为您推荐景点...</p>
      </div>
    </div>

    <!-- 底部操作栏 -->
    <div class="bottom-bar" v-if="selectedSpots.length > 0">
      <div class="bar-info">
        <span>已选 {{ selectedSpots.length }} 个景点</span>
        <span class="days-info">{{ days }} 天行程</span>
      </div>
      <button class="create-trip-btn" @click="createTrip">
        生成行程
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import Navbar from '../components/Navbar.vue'

const router = useRouter()
const route = useRoute()

// 页面数据
const city = ref('')
const days = ref(3)
const preferences = ref([])
const spots = ref([])
const selectedSpots = ref([])
const loading = ref(false)

// 偏好映射（标签ID到标签名称的映射）
const prefTagMap = {
  'must_visit': ['必玩景点', '地标', '热门'],
  'history': ['历史', '文化', '古迹', '博物馆'],
  'landmark': ['地标', '建筑', '地标建筑'],
  'heritage': ['非遗', '传统', '文化'],
  'scenery': ['风景', '名胜', '自然', '山水'],
  'food': ['美食', '小吃', '特色'],
  'museum': ['博物馆', '展览', '文化'],
  'citywalk': ['步行街', '街区', 'citywalk'],
  'photo': ['拍照', '打卡', '出片'],
  'local_life': ['市井', '生活', '烟火'],
  'leisure': ['休闲', '娱乐', '放松']
}

// 城市图片映射
const getCityImageName = (cityName) => {
  const cityMap = {
    '北京': 'beijing.jpg', '上海': 'shanghai.jpg', '西安': 'xian.jpg',
    '成都': 'chengdu.jpg', '重庆': 'chongqing.jpg', '杭州': 'hangzhou.jpg',
    '广州': 'guangzhou.jpg', '苏州': 'suzhou.jpg', '厦门': 'xiamen.jpg',
    '三亚': 'sanya.jpg', '青岛': 'qingdao.jpg', '南京': 'nanjing.jpg',
    '武汉': 'wuhan.jpg', '长沙': 'changsha.jpg', '深圳': 'shenzhen.jpg',
    '桂林': 'guilin.jpg', '张家界': 'zhangjiajie.jpg', '黄山': 'huangshan.jpg',
    '九寨沟': 'jiuzhaigou.jpg', '大理': 'dali.jpg', '丽江': 'lijiang.jpg',
  }
  return cityMap[cityName] || 'beijing.jpg'
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

// 计算标签匹配数量
const getMatchCount = (spot) => {
  if (!spot.tags || preferences.value.length === 0) return 0
  
  let count = 0
  const spotTags = spot.tags.map(t => t.toLowerCase())
  
  preferences.value.forEach(pref => {
    const relatedTags = prefTagMap[pref] || []
    if (relatedTags.some(tag => spotTags.some(st => st.includes(tag)))) {
      count++
    }
  })
  
  return count
}

// 推荐排序算法
const calculateScore = (spot) => {
  let score = 0
  
  // 1. 标签匹配加分（大量加分）
  const matchCount = getMatchCount(spot)
  score += matchCount * 100  // 每个匹配标签加100分
  
  // 2. 收藏人数加分（中量加分）
  const favorites = spot.favorites || 0
  score += Math.min(favorites / 100, 50)  // 最多加50分
  
  // 3. 评分加分（少量加分）
  const rating = spot.rating || 4.5
  score += (rating - 3) * 10  // 评分越高加分越多
  
  return score
}

// 排序后的景点列表
const sortedSpots = computed(() => {
  const scoredSpots = spots.value.map((spot, index) => ({
    ...spot,
    score: calculateScore(spot),
    rank: 0 // 稍后计算
  }))
  
  // 按分数降序排序
  scoredSpots.sort((a, b) => b.score - a.score)
  
  // 添加排名
  scoredSpots.forEach((spot, index) => {
    spot.rank = index + 1
    // 生成推荐理由
    if (spot.score >= 150) {
      spot.recommendReason = '高度匹配您的偏好'
    } else if (spot.favorites > 5000) {
      spot.recommendReason = '热门必玩景点'
    } else if (spot.rating >= 4.8) {
      spot.recommendReason = '评分超高好评'
    }
  })
  
  return scoredSpots
})

// 加载景点数据
const loadSpots = async () => {
  loading.value = true
  try {
    const response = await fetch(`http://localhost:8000/api/spots/recommend?city=${encodeURIComponent(city.value)}&limit=50`)
    const data = await response.json()
    
    if (data.spots) {
      spots.value = data.spots.map(spot => ({
        ...spot,
        // 如果没有收藏数，生成一个模拟的
        favorites: spot.favorites || Math.floor(Math.random() * 5000) + 500,
        // 如果没有评分，使用默认值
        rating: spot.rating || (4.0 + Math.random() * 1.0)
      }))
    } else {
      // 使用模拟数据
      spots.value = getMockSpots()
    }
  } catch (error) {
    console.error('加载景点失败:', error)
    spots.value = getMockSpots()
  } finally {
    loading.value = false
  }
}

// 模拟景点数据
const getMockSpots = () => {
  const mockSpots = [
    { id: 1, name: '故宫博物院', city: '北京', rating: 4.9, favorites: 15234, tags: ['历史', '文化', '建筑', '必玩景点'], images: ['/images/spots/beijing/beijing_gugong_bowuyuan.jpg'] },
    { id: 2, name: '天坛公园', city: '北京', rating: 4.8, favorites: 8932, tags: ['历史', '文化', '建筑'], images: ['/images/spots/beijing/beijing_tiantan_gongyuan.jpg'] },
    { id: 3, name: '颐和园', city: '北京', rating: 4.9, favorites: 12456, tags: ['风景', '名胜', '历史'], images: ['/images/spots/beijing/beijing_yiheyuan.jpg'] },
    { id: 4, name: '长城-八达岭', city: '北京', rating: 4.8, favorites: 18543, tags: ['必玩景点', '地标', '风景'], images: ['/images/spots/beijing/beijing_badaling_changcheng.jpg'] },
    { id: 5, name: '天安门广场', city: '北京', rating: 4.7, favorites: 22341, tags: ['地标', '必玩景点'], images: ['/images/spots/beijing/beijing_tiananmen_guangchang.jpg'] },
    { id: 6, name: '圆明园', city: '北京', rating: 4.6, favorites: 6789, tags: ['历史', '文化', '园林'], images: ['/images/spots/beijing/beijing_yuanmingyuan.jpg'] },
    { id: 7, name: '南锣鼓巷', city: '北京', rating: 4.4, favorites: 15678, tags: ['citywalk', '美食', '市井'], images: ['/images/spots/beijing/beijing_nanluoguxiang.jpg'] },
    { id: 8, name: '北海公园', city: '北京', rating: 4.5, favorites: 7890, tags: ['风景', '休闲', '园林'], images: ['/images/spots/beijing/beijing_beihai_gongyuan.jpg'] },
  ]
  
  return mockSpots.filter(s => s.city === city.value)
}

// 检查是否已选择
const isSelected = (spotId) => {
  return selectedSpots.value.some(s => s.id === spotId)
}

// 切换选择
const toggleSpot = (spot) => {
  const index = selectedSpots.value.findIndex(s => s.id === spot.id)
  if (index > -1) {
    selectedSpots.value.splice(index, 1)
  } else {
    // 保存完整的景点对象
    selectedSpots.value.push({
      id: spot.id,
      name: spot.name,
      rating: spot.rating,
      favorites: spot.favorites,
      tags: spot.tags,
      image: spot.images?.[0] || `/images/cities/${getCityImageName(spot.city)}`,
      duration: spot.duration || '2小时',
      location: spot.location
    })
  }
}

// 清空选择
const clearSelection = () => {
  selectedSpots.value = []
}

// 创建行程
const createTrip = () => {
  if (selectedSpots.value.length === 0) {
    ElMessage.warning('请至少选择一个景点')
    return
  }
  
  // 保存选择的数据（保存完整的景点对象数组）
  localStorage.setItem('selectedSpots', JSON.stringify(selectedSpots.value))
  localStorage.setItem('tripCity', city.value)
  localStorage.setItem('tripDays', days.value)
  localStorage.setItem('tripPreferences', preferences.value.join(','))
  
  // 跳转到行程详情页
  router.push({
    path: '/trip',
    query: {
      city: city.value,
      days: days.value,
      preferences: preferences.value.join(',')
    }
  })
}

// 初始化
onMounted(() => {
  city.value = route.query.city || '北京'
  days.value = parseInt(route.query.days) || 3
  const prefStr = route.query.preferences || ''
  preferences.value = prefStr.split(',').filter(p => p)
  
  loadSpots()
})
</script>

<style scoped>
.spot-recommend-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #0a0a1a 0%, #1a1a2e 50%, #16213e 100%);
  color: #fff;
  padding-bottom: 100px;
}

.page-content {
  padding: 90px 40px 40px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
}

.page-title {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 10px;
  background: linear-gradient(135deg, #00d4ff, #fff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.page-subtitle {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.6);
}

.selected-count {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background: rgba(0, 212, 255, 0.1);
  border-radius: 12px;
  margin-bottom: 20px;
  border: 1px solid rgba(0, 212, 255, 0.2);
}

.clear-btn {
  padding: 6px 12px;
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  background: transparent;
  color: #fff;
  font-size: 13px;
  cursor: pointer;
}

.spots-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.spot-card {
  background: rgba(255, 255, 255, 0.05);
  border: 2px solid transparent;
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
}

.spot-card:hover {
  transform: translateY(-5px);
  border-color: rgba(0, 212, 255, 0.3);
  box-shadow: 0 10px 30px rgba(0, 212, 255, 0.15);
}

.spot-card.selected {
  border-color: #00d4ff;
  box-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
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

.spot-rank {
  position: absolute;
  top: 10px;
  left: 10px;
  padding: 6px 12px;
  background: linear-gradient(135deg, #ffd700, #ff8c00);
  border-radius: 20px;
  font-size: 12px;
  font-weight: 700;
  color: #000;
}

.select-indicator {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #00d4ff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  color: #fff;
}

.spot-info {
  padding: 16px;
}

.spot-name {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 10px;
}

.spot-stats {
  display: flex;
  gap: 15px;
  margin-bottom: 10px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
}

.stat-icon {
  font-size: 14px;
}

.stat-value {
  font-weight: 600;
}

.tag-match {
  margin-bottom: 10px;
}

.match-badge {
  display: inline-block;
  padding: 4px 10px;
  background: rgba(0, 212, 255, 0.2);
  border-radius: 10px;
  font-size: 12px;
  color: #00d4ff;
}

.spot-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-bottom: 10px;
}

.tag {
  padding: 4px 10px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
}

.recommend-reason {
  padding: 8px 12px;
  background: rgba(123, 44, 191, 0.2);
  border-radius: 8px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.8);
}

.empty-state {
  text-align: center;
  padding: 80px 20px;
  color: rgba(255, 255, 255, 0.5);
}

.empty-icon {
  font-size: 60px;
  display: block;
  margin-bottom: 20px;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 3px solid rgba(255, 255, 255, 0.1);
  border-top-color: #00d4ff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.bottom-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 20px 40px;
  background: rgba(10, 10, 26, 0.95);
  backdrop-filter: blur(20px);
  border-top: 1px solid rgba(0, 212, 255, 0.2);
  display: flex;
  justify-content: space-between;
  align-items: center;
  z-index: 100;
}

.bar-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.bar-info span {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
}

.days-info {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

.create-trip-btn {
  padding: 12px 30px;
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  border: none;
  border-radius: 25px;
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.create-trip-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 20px rgba(0, 212, 255, 0.4);
}

@media (max-width: 768px) {
  .page-content {
    padding: 90px 20px 40px;
  }
  
  .spots-grid {
    grid-template-columns: 1fr;
  }
  
  .bottom-bar {
    padding: 15px 20px;
  }
}
</style>
