<template>
  <div class="spot-recommend-page">
    <!-- 顶部导航 -->
    <header class="page-header">
      <button class="back-btn" @click="goBack">
        <span class="back-icon">←</span>
      </button>
      <div class="header-center">
        <span class="selected-count">{{ selectedSpots.length }} 个地点</span>
      </div>
      <button class="confirm-btn" :disabled="selectedSpots.length === 0" @click="generateGuide">
        ✓
      </button>
    </header>

    <main class="page-content">
      <!-- 筛选条件 -->
      <div class="filter-bar">
        <div class="filter-tags">
          <span class="filter-tag">{{ city }}</span>
          <span class="filter-tag">玩 {{ days }} 天</span>
        </div>
        <button class="change-btn" @click="changePreferences">更换偏好</button>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-container">
        <div class="loading-spinner"></div>
        <p>AI 正在为你智能推荐景点...</p>
      </div>

      <!-- 景点网格 -->
      <div v-else class="spot-grid">
        <div 
          v-for="spot in spots" 
          :key="spot.id" 
          class="spot-card"
          :class="{ selected: isSelected(spot.id) }"
          @click="toggleSpot(spot)"
        >
          <div class="card-image">
            <img :src="spot.images?.[0] || '/images/default.jpg'" :alt="spot.name" />
            <div class="rating-badge">
              <span class="heart">♥</span>
              <span class="rating-value">{{ spot.rating }}</span>
            </div>
            <button class="add-btn" :class="{ added: isSelected(spot.id) }">
              {{ isSelected(spot.id) ? '✓' : '+' }}
            </button>
          </div>
          <div class="card-info">
            <h3 class="spot-name">{{ spot.name }}</h3>
            <div class="spot-tags">
              <span v-for="tag in (spot.tags || []).slice(0, 3)" :key="tag" class="spot-tag">
                {{ tag }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="!loading && spots.length === 0" class="empty-state">
        <span class="empty-icon">🔍</span>
        <p>暂无推荐景点，请尝试其他偏好</p>
      </div>
    </main>

    <!-- 底部按钮 -->
    <footer class="page-footer" v-if="selectedSpots.length > 0">
      <button class="tech-button submit-btn" @click="generateGuide">
        <span>✨</span> 生成攻略
      </button>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const router = useRouter()
const route = useRoute()

// 数据
const city = ref('')
const days = ref(3)
const preferences = ref([])
const spots = ref([])
const selectedSpots = ref([])
const loading = ref(true)

// 热门城市图片映射
const cityImages = {
  '北京': ['https://images.unsplash.com/photo-1599571234909-29ed5d1321d6?w=400', 'https://images.unsplash.com/photo-1599571234909-29ed5d1321d6?w=400'],
  '上海': ['https://images.unsplash.com/photo-1474181487882-5abf3f0ba6c2?w=400'],
  '西安': ['https://images.unsplash/photo-1599571234909-29ed5d1321d6?w=400'],
  '成都': ['https://images.unsplash.com/photo-1599571234909-29ed5d1321d6?w=400'],
  '杭州': ['https://images.unsplash.com/photo-1599571234909-29ed5d1321d6?w=400'],
  '青岛': ['https://images.unsplash.com/photo-1599571234909-29ed5d1321d6?w=400'],
}

// 加载数据
onMounted(async () => {
  city.value = route.query.city || '北京'
  days.value = parseInt(route.query.days) || 3
  preferences.value = (route.query.preferences || '').split(',').filter(p => p)
  
  await loadRecommendedSpots()
})

// 加载推荐景点
const loadRecommendedSpots = async () => {
  loading.value = true
  
  try {
    // 调用API获取景点（按城市筛选）
    const response = await fetch(`http://localhost:8000/api/spots/recommend?city=${encodeURIComponent(city.value)}&limit=20`)
    const data = await response.json()
    
    if (data.spots) {
      // 添加默认图片
      spots.value = data.spots.map(spot => ({
        ...spot,
        images: spot.images || getDefaultImages(spot.name)
      }))
    } else if (Array.isArray(data)) {
      spots.value = data.map(spot => ({
        ...spot,
        images: spot.images || getDefaultImages(spot.name)
      }))
    }
  } catch (error) {
    console.error('加载推荐失败:', error)
    // 使用本地模拟数据
    spots.value = getMockSpots()
  } finally {
    loading.value = false
  }
}

// 获取默认图片
const getDefaultImages = (name) => {
  return cityImages[city.value] || ['https://images.unsplash.com/photo-1713173642147-30cbbdb176d5?q=80&w=400']
}

// 模拟数据
const getMockSpots = () => {
  const mockData = {
    '北京': [
      { id: 1, name: '故宫博物院', rating: 4.9, tags: ['建筑宏伟', '历史厚重', '必玩景点'], images: ['https://images.unsplash.com/photo-1599571234909-29ed5d1321d6?w=400'] },
      { id: 2, name: '天坛公园', rating: 4.9, tags: ['古建绝美', '声学奇迹'], images: ['https://images.unsplash.com/photo-1599571234909-29ed5d1321d6?w=400'] },
      { id: 3, name: '颐和园', rating: 4.9, tags: ['皇家园林', '湖光山色'], images: ['https://images.unsplash.com/photo-1599571234909-29ed5d1321d6?w=400'] },
      { id: 4, name: '长城-八达岭', rating: 4.8, tags: ['必玩景点', '地标建筑'], images: ['https://images.unsplash.com/photo-1599571234909-29ed5d1321d6?w=400'] },
      { id: 5, name: '天安门广场', rating: 4.8, tags: ['升旗仪式', '庄严神圣'], images: ['https://images.unsplash.com/photo-1599571234909-29ed5d1321d6?w=400'] },
      { id: 6, name: '圆明园', rating: 4.7, tags: ['历史遗址', '园林景观'], images: ['https://images.unsplash.com/photo-1599571234909-29ed5d1321d6?w=400'] },
    ],
    '上海': [
      { id: 11, name: '外滩', rating: 4.9, tags: ['地标建筑', '夜景绝美'], images: ['https://images.unsplash.com/photo-1599571234909-29ed5d1321d6?w=400'] },
      { id: 12, name: '东方明珠', rating: 4.7, tags: ['地标建筑', '登高望远'], images: ['https://images.unsplash.com/photo-1599571234909-29ed5d1321d6?w=400'] },
      { id: 13, name: '豫园', rating: 4.8, tags: ['江南园林', '历史文化'], images: ['https://images.unsplash.com/photo-1599571234909-29ed5d1321d6?w=400'] },
    ]
  }
  return mockData[city.value] || mockData['北京']
}

// 判断是否已选
const isSelected = (spotId) => {
  return selectedSpots.value.includes(spotId)
}

// 切换选择
const toggleSpot = (spot) => {
  const index = selectedSpots.value.indexOf(spot.id)
  if (index > -1) {
    selectedSpots.value.splice(index, 1)
  } else {
    selectedSpots.value.push(spot.id)
  }
}

// 返回
const goBack = () => {
  router.push('/create-trip')
}

// 更换偏好
const changePreferences = () => {
  router.push('/create-trip')
}

// 生成攻略
const generateGuide = async () => {
  if (selectedSpots.value.length === 0) {
    ElMessage.warning('请至少选择一个景点')
    return
  }
  
  // 保存选择到本地存储
  localStorage.setItem('selectedSpots', JSON.stringify(selectedSpots.value))
  localStorage.setItem('tripCity', city.value)
  localStorage.setItem('tripDays', days.value)
  
  ElMessage.success('已选择 ' + selectedSpots.value.length + ' 个景点，正在生成攻略...')
  
  // 跳转到行程详情页
  router.push({
    path: '/trip/new',
    query: {
      city: city.value,
      days: days.value,
      spots: selectedSpots.value.join(',')
    }
  })
}
</script>

<style scoped>
.spot-recommend-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #0a0a1a 0%, #1a1a2e 100%);
  padding-bottom: 100px;
}

/* 顶部导航 */
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
  border-bottom: 1px solid var(--border-color);
}

.back-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 1px solid var(--border-color);
  background: transparent;
  color: var(--text-primary);
  font-size: 18px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.back-btn:hover {
  background: var(--primary-color);
}

.header-center {
  font-size: 16px;
  font-weight: 500;
}

.confirm-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 1px solid var(--border-color);
  background: transparent;
  color: var(--text-primary);
  font-size: 18px;
  cursor: pointer;
}

.confirm-btn:not(:disabled):hover {
  background: var(--primary-color);
  border-color: var(--primary-color);
}

.confirm-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

/* 筛选栏 */
.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid var(--border-color);
}

.filter-tags {
  display: flex;
  gap: 10px;
}

.filter-tag {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  padding: 6px 14px;
  font-size: 13px;
  color: var(--primary-color);
}

.change-btn {
  background: transparent;
  border: 1px solid var(--primary-color);
  border-radius: 15px;
  padding: 6px 14px;
  font-size: 13px;
  color: var(--primary-color);
  cursor: pointer;
}

/* 加载状态 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  color: var(--text-secondary);
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 3px solid var(--border-color);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 景点网格 */
.spot-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
  padding: 20px;
}

.spot-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
}

.spot-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0, 212, 255, 0.2);
}

.spot-card.selected {
  border-color: var(--primary-color);
  box-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
}

.card-image {
  position: relative;
  height: 150px;
  overflow: hidden;
}

.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.rating-badge {
  position: absolute;
  top: 10px;
  left: 10px;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(5px);
  border-radius: 12px;
  padding: 4px 10px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.heart {
  color: #ff6b6b;
  font-size: 14px;
}

.rating-value {
  font-size: 13px;
  font-weight: 500;
}

.add-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: none;
  background: rgba(255, 255, 255, 0.9);
  color: var(--primary-color);
  font-size: 18px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.add-btn:hover {
  background: var(--primary-color);
  color: white;
}

.add-btn.added {
  background: var(--primary-color);
  color: white;
}

.card-info {
  padding: 12px;
}

.spot-name {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.spot-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.spot-tag {
  font-size: 11px;
  color: var(--text-secondary);
  background: rgba(255, 255, 255, 0.05);
  padding: 3px 8px;
  border-radius: 10px;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  color: var(--text-secondary);
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 15px;
}

/* 底部按钮 */
.page-footer {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 20px;
  background: rgba(10, 10, 26, 0.9);
  backdrop-filter: blur(10px);
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: center;
}

.submit-btn {
  width: 100%;
  max-width: 400px;
  padding: 16px;
  font-size: 16px;
}
</style>
