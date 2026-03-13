<template>
  <div class="create-trip-page">
    <!-- 顶部导航 -->
    <header class="page-header">
      <button class="back-btn" @click="goBack">
        <span class="back-icon">←</span>
      </button>
      <h1 class="page-title">创建新行程</h1>
      <div class="header-placeholder"></div>
    </header>

    <main class="page-content">
      <!-- 地点选择 -->
      <section class="section">
        <h2 class="section-title">
          <span class="title-icon">📍</span>
          目的地
        </h2>
        <div class="destination-input">
          <div class="selected-tags" v-if="form.destinations.length > 0">
            <span 
              v-for="dest in form.destinations" 
              :key="dest" 
              class="selected-tag"
            >
              {{ dest }}
              <button class="remove-btn" @click="removeDestination(dest)">×</button>
            </span>
          </div>
          <input 
            type="text" 
            class="tech-input dest-input" 
            placeholder="输入目的地城市..." 
            v-model="cityInput"
            @keyup.enter="addDestinationFromInput"
          />
        </div>
        
        <!-- 热门城市 -->
        <div class="hot-cities">
          <span 
            v-for="city in hotCities" 
            :key="city" 
            class="hot-city"
            :class="{ active: form.destinations.includes(city) }"
            @click="toggleCity(city)"
          >
            {{ city }}
          </span>
        </div>
      </section>

      <!-- 天数选择 -->
      <section class="section">
        <h2 class="section-title">
          <span class="title-icon">📅</span>
          旅行天数
        </h2>
        <div class="day-slider-container">
          <div class="slider-wrapper">
            <input 
              type="range" 
              class="day-slider" 
              v-model.number="form.days" 
              min="1" 
              max="15"
            />
            <div class="slider-track" :style="{ width: ((form.days - 1) / 14) * 100 + '%' }"></div>
          </div>
          <div class="day-display">
            <span class="day-number">{{ form.days }}</span>
            <span class="day-unit">天</span>
          </div>
        </div>
        <div class="day-labels">
          <span>1天</span>
          <span>7天</span>
          <span>15天</span>
        </div>
      </section>

      <!-- 偏好标签 -->
      <section class="section">
        <h2 class="section-title">
          <span class="title-icon">🏷️</span>
          旅行偏好
        </h2>
        <div class="preference-grid">
          <button 
            v-for="tag in preferenceTags" 
            :key="tag.id"
            class="pref-tag"
            :class="{ active: form.preferences.includes(tag.id) }"
            @click="togglePreference(tag.id)"
          >
            <span class="tag-icon">{{ tag.icon }}</span>
            <span class="tag-name">{{ tag.name }}</span>
          </button>
        </div>
      </section>

      <!-- AI 助手提示 -->
      <div class="ai-tip">
        <div class="tip-icon">💡</div>
        <p>选择完成后，AI将根据你的偏好智能推荐景点</p>
      </div>
    </main>

    <!-- 底部按钮 -->
    <footer class="page-footer">
      <button 
        class="tech-button submit-btn" 
        :disabled="!canSubmit"
        @click="submitTrip"
      >
        <span>🤖</span> 帮我规划
      </button>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()

// 表单数据
const form = ref({
  destinations: [],
  days: 3,
  preferences: []
})

const cityInput = ref('')

// 热门城市
const hotCities = [
  '北京', '上海', '西安', '成都', '杭州', '青岛', '广州', '深圳', 
  '重庆', '南京', '武汉', '长沙', '厦门', '苏州', '桂林', '三亚',
  '东京', '巴黎', '纽约', '香港'
]

// 偏好标签
const preferenceTags = [
  { id: 'must_visit', name: '必玩景点', icon: '⭐' },
  { id: 'history', name: '历史文化', icon: '🏛️' },
  { id: 'landmark', name: '地标建筑', icon: '🏗️' },
  { id: 'heritage', name: '非遗体验', icon: '🎭' },
  { id: 'scenery', name: '风景名胜', icon: '🏞️' },
  { id: 'food', name: '逛吃逛喝', icon: '🍜' },
  { id: 'museum', name: '博物展览', icon: '🎨' },
  { id: 'citywalk', name: 'citywalk', icon: '🚶' },
  { id: 'photo', name: '拍照出片', icon: '📸' },
  { id: 'local_life', name: '市井烟火', icon: '🏘️' },
  { id: 'leisure', name: '休闲娱乐', icon: '☕' },
]

// 计算是否可以提交
const canSubmit = computed(() => {
  return form.value.destinations.length > 0
})

// 从输入框添加目的地
const addDestinationFromInput = () => {
  const city = cityInput.value.trim()
  if (city && !form.value.destinations.includes(city)) {
    form.value.destinations.push(city)
    cityInput.value = ''
  }
}

// 切换城市
const toggleCity = (city) => {
  const index = form.value.destinations.indexOf(city)
  if (index > -1) {
    form.value.destinations.splice(index, 1)
  } else {
    form.value.destinations.push(city)
  }
}

// 移除目的地
const removeDestination = (dest) => {
  const index = form.value.destinations.indexOf(dest)
  if (index > -1) {
    form.value.destinations.splice(index, 1)
  }
}

// 切换偏好
const togglePreference = (prefId) => {
  const index = form.value.preferences.indexOf(prefId)
  if (index > -1) {
    form.value.preferences.splice(index, 1)
  } else {
    form.value.preferences.push(prefId)
  }
}

// 返回
const goBack = () => {
  router.push('/')
}

// 提交
const submitTrip = async () => {
  if (!canSubmit.value) {
    ElMessage.warning('请至少选择一个目的地')
    return
  }

  // 保存到本地存储（后续会调用API）
  localStorage.setItem('createTripForm', JSON.stringify(form.value))
  
  // 跳转到推荐页面
  router.push({
    path: '/spot-recommend',
    query: {
      city: form.value.destinations[0],
      days: form.value.days,
      preferences: form.value.preferences.join(',')
    }
  })
}

// 检查URL参数
const checkQueryParams = () => {
  if (route.query.city) {
    form.value.destinations = [route.query.city]
  }
  if (route.query.days) {
    form.value.days = parseInt(route.query.days)
  }
  if (route.query.preferences) {
    form.value.preferences = route.query.preferences.split(',')
  }
}

checkQueryParams()
</script>

<style scoped>
.create-trip-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #0a0a1a 0%, #1a1a2e 100%);
  padding-bottom: 100px;
}

/* 顶部导航 */
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px;
  background: rgba(10, 10, 26, 0.9);
  backdrop-filter: blur(10px);
  position: sticky;
  top: 0;
  z-index: 100;
  border-bottom: 1px solid var(--border-color);
}

.back-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 1px solid var(--border-color);
  background: transparent;
  color: var(--text-primary);
  font-size: 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.back-btn:hover {
  background: var(--primary-color);
  border-color: var(--primary-color);
}

.page-title {
  font-size: 20px;
  font-weight: 600;
}

.header-placeholder {
  width: 40px;
}

/* 内容区域 */
.page-content {
  padding: 30px 20px;
  max-width: 800px;
  margin: 0 auto;
}

.section {
  margin-bottom: 40px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.title-icon {
  font-size: 20px;
}

/* 目的地 */
.destination-input {
  margin-bottom: 15px;
}

.selected-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 15px;
}

.selected-tag {
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  border-radius: 20px;
  padding: 8px 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.remove-btn {
  background: none;
  border: none;
  color: white;
  font-size: 18px;
  cursor: pointer;
  opacity: 0.8;
}

.remove-btn:hover {
  opacity: 1;
}

.dest-input {
  width: 100%;
}

.hot-cities {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.hot-city {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-color);
  border-radius: 20px;
  padding: 8px 16px;
  font-size: 14px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s ease;
}

.hot-city:hover {
  border-color: var(--primary-color);
  color: var(--primary-color);
}

.hot-city.active {
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  border-color: transparent;
  color: white;
}

/* 天数选择 */
.day-slider-container {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 10px;
}

.slider-wrapper {
  flex: 1;
  position: relative;
}

.day-slider {
  width: 100%;
  height: 8px;
  -webkit-appearance: none;
  appearance: none;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  outline: none;
}

.day-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  cursor: pointer;
  box-shadow: 0 0 15px var(--glow-color);
}

.slider-track {
  position: absolute;
  top: 0;
  left: 0;
  height: 8px;
  background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
  border-radius: 4px;
  pointer-events: none;
}

.day-display {
  display: flex;
  align-items: baseline;
  gap: 5px;
}

.day-number {
  font-size: 48px;
  font-weight: 700;
  background: linear-gradient(135deg, var(--primary-color), #ffffff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.day-unit {
  font-size: 18px;
  color: var(--text-secondary);
}

.day-labels {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: var(--text-secondary);
  padding: 0 5px;
}

/* 偏好标签 */
.preference-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.pref-tag {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.pref-tag:hover {
  border-color: var(--primary-color);
  transform: translateY(-2px);
}

.pref-tag.active {
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.2), rgba(123, 44, 191, 0.2));
  border-color: var(--primary-color);
  box-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
}

.tag-icon {
  font-size: 24px;
}

.tag-name {
  font-size: 14px;
  color: var(--text-primary);
}

/* AI提示 */
.ai-tip {
  display: flex;
  align-items: center;
  gap: 15px;
  background: rgba(0, 212, 255, 0.1);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 16px 20px;
  margin-top: 30px;
}

.tip-icon {
  font-size: 24px;
}

.ai-tip p {
  font-size: 14px;
  color: var(--text-secondary);
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
  font-size: 18px;
}

.submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
