<template>
  <div class="trip-detail-page">
    <!-- 顶部导航 -->
    <header class="page-header">
      <button class="back-btn" @click="goBack">
        <span class="back-icon">←</span>
      </button>
      <h1 class="page-title">行程详情</h1>
      <button class="action-btn" @click="saveTrip">保存</button>
    </header>

    <main class="page-content">
      <!-- 行程信息 -->
      <section class="trip-info">
        <h2 class="trip-title">{{ tripTitle }}</h2>
        <div class="trip-meta">
          <span class="meta-item">
            <span class="meta-icon">📍</span>
            {{ city }}
          </span>
          <span class="meta-item">
            <span class="meta-icon">📅</span>
            {{ days }} 天
          </span>
          <span class="meta-item">
            <span class="meta-icon">🏷️</span>
            {{ preferencesText }}
          </span>
        </div>
      </section>

      <!-- AI 生成的攻略 -->
      <section class="guide-section" v-if="guideData">
        <h3 class="section-title">
          <span>✨</span> AI 智能攻略
        </h3>
        
        <div class="day-cards">
          <div 
            v-for="day in guideData.days" 
            :key="day.day" 
            class="day-card tech-card"
          >
            <div class="day-header">
              <span class="day-number">Day {{ day.day }}</span>
              <span class="day-theme">{{ day.theme }}</span>
            </div>
            
            <div class="spots-list">
              <div v-for="(spot, idx) in day.spots" :key="idx" class="spot-item">
                <div class="spot-time">{{ spot.time }}</div>
                <div class="spot-info">
                  <h4>{{ spot.name }}</h4>
                  <p>{{ spot.tips }}</p>
                </div>
              </div>
            </div>
            
            <div class="day-food" v-if="day.food">
              <span class="food-icon">🍜</span>
              <span>{{ day.food }}</span>
            </div>
          </div>
        </div>

        <!-- 实用贴士 -->
        <div class="tips-section" v-if="guideData.tips?.length">
          <h3 class="section-title">
            <span>💡</span> 实用贴士
          </h3>
          <ul class="tips-list">
            <li v-for="(tip, idx) in guideData.tips" :key="idx">{{ tip }}</li>
          </ul>
        </div>
      </section>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-container">
        <div class="loading-spinner"></div>
        <p>AI 正在生成专属攻略...</p>
      </div>
    </main>

    <!-- 底部操作 -->
    <footer class="page-footer">
      <button class="tech-button secondary" @click="regenerate">
        <span>🔄</span> 重新生成
      </button>
      <button class="tech-button" @click="viewRoute">
        <span>🗺️</span> 查看路线
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
const selectedSpots = ref([])
const guideData = ref(null)
const loading = ref(false)
const tripTitle = ref('')

// 偏好映射
const prefMap = {
  'must_visit': '必玩景点',
  'history': '历史文化',
  'landmark': '地标建筑',
  'heritage': '非遗体验',
  'scenery': '风景名胜',
  'food': '逛吃逛喝',
  'museum': '博物展览',
  'citywalk': 'citywalk',
  'photo': '拍照出片',
  'local_life': '市井烟火',
  'leisure': '休闲娱乐'
}

const preferencesText = computed(() => {
  return preferences.value.map(p => prefMap[p] || p).slice(0, 2).join('、')
})

// 加载数据
onMounted(async () => {
  city.value = route.query.city || localStorage.getItem('tripCity') || '北京'
  days.value = parseInt(route.query.days) || parseInt(localStorage.getItem('tripDays')) || 3
  
  const prefStr = route.query.preferences || localStorage.getItem('tripPreferences') || ''
  preferences.value = prefStr.split(',').filter(p => p)
  
  const spotsStr = route.query.spots || localStorage.getItem('selectedSpots') || '[]'
  selectedSpots.value = JSON.parse(spotsStr)
  
  tripTitle.value = `${city.value}${days.value}日${preferencesText.value || '游'}`
  
  // 生成攻略
  await generateGuide()
})

// 生成攻略
const generateGuide = async () => {
  loading.value = true
  
  try {
    // 调用 AI 接口
    const response = await fetch('http://localhost:8000/api/ai/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        destination: city.value,
        days: days.value,
        preferences: preferences.value,
        selected_spots: selectedSpots.value
      })
    })
    
    const data = await response.json()
    if (data) {
      guideData.value = data
    }
  } catch (error) {
    console.error('生成失败:', error)
    // 使用模拟数据
    guideData.value = getMockGuide()
  } finally {
    loading.value = false
  }
}

// 模拟攻略数据
const getMockGuide = () => {
  return {
    title: `${city.value}${days.value}日游`,
    days: [
      {
        day: 1,
        theme: '历史文化之旅',
        spots: [
          { time: '09:00', name: '抵达景点', tips: '建议早点出发，避开人流' },
          { time: '10:00', name: '主要景点游览', tips: '预留足够时间参观' },
          { time: '12:00', name: '午餐时间', tips: '品尝当地特色美食' },
        ],
        food: '推荐当地特色餐厅'
      },
      {
        day: 2,
        theme: '自然风光游览',
        spots: [
          { time: '08:30', name: '晨间游览', tips: '空气清新，适合拍照' },
          { time: '11:00', name: '深度体验', tips: '不要错过标志性景观' },
        ],
        food: '推荐景区周边美食'
      }
    ],
    tips: ['建议提前预约门票', '带好防晒用品', '注意保管好个人物品']
  }
}

// 返回
const goBack = () => {
  router.push('/spot-recommend')
}

// 保存
const saveTrip = () => {
  ElMessage.success('行程已保存')
}

// 重新生成
const regenerate = async () => {
  await generateGuide()
}

// 查看路线
const viewRoute = () => {
  router.push('/route/new')
}
</script>

<style scoped>
.trip-detail-page {
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
}

.action-btn {
  background: transparent;
  border: none;
  color: var(--primary-color);
  font-size: 16px;
  cursor: pointer;
}

/* 行程信息 */
.trip-info {
  padding: 30px 20px;
  border-bottom: 1px solid var(--border-color);
}

.trip-title {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 15px;
  background: linear-gradient(135deg, var(--primary-color), #ffffff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.trip-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: var(--text-secondary);
}

.meta-icon {
  font-size: 16px;
}

/* 攻略区域 */
.guide-section {
  padding: 20px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.day-cards {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.day-card {
  padding: 20px;
}

.day-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--border-color);
}

.day-number {
  font-size: 18px;
  font-weight: 700;
  color: var(--primary-color);
}

.day-theme {
  font-size: 14px;
  color: var(--text-secondary);
}

.spots-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-bottom: 15px;
}

.spot-item {
  display: flex;
  gap: 15px;
}

.spot-time {
  font-size: 13px;
  color: var(--primary-color);
  min-width: 50px;
}

.spot-info h4 {
  font-size: 15px;
  margin-bottom: 4px;
}

.spot-info p {
  font-size: 13px;
  color: var(--text-secondary);
}

.day-food {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: var(--text-secondary);
  background: rgba(255, 255, 255, 0.05);
  padding: 10px;
  border-radius: 8px;
}

/* 贴士 */
.tips-section {
  margin-top: 30px;
}

.tips-list {
  list-style: none;
  padding: 0;
}

.tips-list li {
  padding: 10px 0;
  border-bottom: 1px solid var(--border-color);
  font-size: 14px;
  color: var(--text-secondary);
}

.tips-list li::before {
  content: '•';
  color: var(--primary-color);
  margin-right: 10px;
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

/* 底部操作 */
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
  gap: 15px;
}

.page-footer .tech-button {
  flex: 1;
}

.tech-button.secondary {
  background: transparent;
  border: 1px solid var(--primary-color);
}
</style>
