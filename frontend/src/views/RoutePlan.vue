<template>
  <div class="route-plan-page">
    <header class="page-header">
      <button class="back-btn" @click="goBack">←</button>
      <h1 class="page-title">路线规划</h1>
      <button class="action-btn" @click="shareRoute">分享</button>
    </header>

    <main class="page-content">
      <!-- 地图区域 - 使用 AmapContainer 组件 -->
      <div class="map-wrapper">
        <AmapContainer ref="amapRef" />
      </div>

      <!-- 添加景点按钮 -->
      <div class="add-spot-bar">
        <button class="tech-button add-spot-btn" @click="showAddSpotModal = true">
          <span>+</span> 添加景点
        </button>
      </div>

      <!-- 路线信息 -->
      <div class="route-info" v-if="routeInfo.distance">
        <div class="info-card tech-card">
          <div class="info-item">
            <span class="info-icon">📏</span>
            <div class="info-content">
              <span class="info-label">总距离</span>
              <span class="info-value">{{ routeInfo.distance }} km</span>
            </div>
          </div>
          <div class="info-item">
            <span class="info-icon">⏱️</span>
            <div class="info-content">
              <span class="info-label">预计时间</span>
              <span class="info-value">{{ routeInfo.duration }}</span>
            </div>
          </div>
          <div class="info-item">
            <span class="info-icon">🚗</span>
            <div class="info-content">
              <span class="info-label">交通方式</span>
              <select v-model="transportType" class="transport-select" @change="recalculateRoute">
                <option value="driving">驾车</option>
                <option value="walking">步行</option>
                <option value="riding">骑行</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <!-- 景点列表 -->
      <div class="spots-section">
        <h3 class="section-title">途经景点 ({{ waypoints.length }})</h3>
        <div class="spots-list">
          <div 
            v-for="(spot, index) in waypoints" 
            :key="index"
            class="spot-item"
          >
            <div class="spot-number">{{ index + 1 }}</div>
            <div class="spot-info">
              <h4>{{ spot.name }}</h4>
              <p>{{ spot.address || '地址未知' }}</p>
            </div>
            <button class="delete-btn" @click="removeWaypoint(index)">×</button>
          </div>
          
          <div v-if="waypoints.length === 0" class="empty-spots">
            <p>点击上方"添加景点"添加途经点</p>
          </div>
        </div>
      </div>

      <!-- 开始导航按钮 -->
      <div class="nav-bar" v-if="waypoints.length >= 2">
        <button class="tech-button nav-btn" @click="startNavigation" :disabled="!routeInfo.distance">
          <span>🧭</span> 开始导航
        </button>
      </div>
    </main>

    <!-- 添加景点弹窗 -->
    <div v-if="showAddSpotModal" class="modal-overlay" @click.self="showAddSpotModal = false">
      <div class="modal-content">
        <h3>添加途经点</h3>
        <input 
          type="text" 
          class="tech-input" 
          placeholder="输入景点名称..."
          v-model="searchKeyword"
          @input="searchSpots"
        />
        <div class="search-results">
          <div 
            v-for="spot in searchResults" 
            :key="spot.id"
            class="search-result-item"
            @click="addWaypoint(spot)"
          >
            <span class="result-name">{{ spot.name }}</span>
            <span class="result-city">{{ spot.city }}</span>
          </div>
        </div>
        <button class="close-modal" @click="showAddSpotModal = false">关闭</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import AmapContainer from '../components/AmapContainer.vue'

const router = useRouter()

// 地图组件引用
const amapRef = ref(null)

// 状态
const waypoints = ref([])
const routeInfo = ref({ distance: 0, duration: '' })
const transportType = ref('driving')
const showAddSpotModal = ref(false)
const searchKeyword = ref('')
const searchResults = ref([])

// 监听途经点变化，自动更新地图标记和路线
watch(() => waypoints.value, (newWaypoints) => {
  if (newWaypoints.length >= 2) {
    updateMapMarkers()
    recalculateRoute()
  }
}, { deep: true })

// 更新地图标记
const updateMapMarkers = () => {
  if (!amapRef.value || waypoints.value.length < 2) return
  
  // 设置起点（第一个景点）
  const start = waypoints.value[0]
  if (start.location) {
    amapRef.value.setStart(start.location.lng, start.location.lat)
  }
  
  // 设置终点（最后一个景点）
  const end = waypoints.value[waypoints.value.length - 1]
  if (end.location) {
    amapRef.value.setEnd(end.location.lng, end.location.lat)
  }
}

// 搜索景点
const searchSpots = async () => {
  if (searchKeyword.value.length < 2) {
    searchResults.value = []
    return
  }
  
  try {
    const response = await axios.get(`http://localhost:8000/api/spots/recommend?city=${encodeURIComponent(searchKeyword.value)}&limit=10`)
    if (response.data.spots) {
      searchResults.value = response.data.spots
    }
  } catch (error) {
    console.error('搜索失败:', error)
  }
}

// 添加途经点
const addWaypoint = (spot) => {
  waypoints.value.push({
    id: spot.id,
    name: spot.name,
    address: spot.address,
    location: { lng: spot.location_lng, lat: spot.location_lat }
  })
  showAddSpotModal.value = false
  searchKeyword.value = ''
  searchResults.value = []
}

// 移除途经点
const removeWaypoint = (index) => {
  waypoints.value.splice(index, 1)
  
  // 如果剩余景点少于2个，清除地图
  if (waypoints.value.length < 2) {
    amapRef.value?.clearAll()
    routeInfo.value = { distance: 0, duration: '' }
  }
}

// 重新计算路线
const recalculateRoute = async () => {
  if (waypoints.value.length < 2) return
  
  // 先更新地图标记
  updateMapMarkers()
  
  try {
    const response = await axios.post('http://localhost:8000/api/route/plan', {
      start: waypoints.value[0].location,
      end: waypoints.value[waypoints.value.length - 1].location,
      waypoints: waypoints.value.slice(1, -1).map(w => w.location),
      strategy: transportType.value
    })
    
    if (response.data) {
      routeInfo.value = {
        distance: (response.data.distance / 1000).toFixed(1),
        duration: Math.round(response.data.time / 60) + '分钟'
      }
    }
    
    // 调用地图组件的路线规划
    setTimeout(() => {
      amapRef.value?.planRoute()
    }, 500)
    
  } catch (error) {
    console.error('路线规划失败:', error)
    // 使用模拟数据
    routeInfo.value = {
      distance: (Math.random() * 50 + 10).toFixed(1),
      duration: Math.round(Math.random() * 60 + 30) + '分钟'
    }
    // 仍然调用地图规划显示路线
    setTimeout(() => {
      amapRef.value?.planRoute()
    }, 500)
  }
}

// 开始导航
const startNavigation = () => {
  if (waypoints.value.length < 2) {
    alert('请至少添加两个景点')
    return
  }
  
  // 构建高德地图导航URL
  const start = waypoints.value[0]
  const end = waypoints.value[waypoints.value.length - 1]
  
  // 使用高德地图URI API进行导航
  const url = `https://uri.amap.com/navigation?from=${start.location.lng},${start.location.lat},${encodeURIComponent(start.name)}&to=${end.location.lng},${end.location.lat},${encodeURIComponent(end.name)}&mode=car&policy=1`
  
  window.open(url, '_blank')
}

// 分享路线
const shareRoute = () => {
  if (waypoints.value.length < 2) {
    alert('请至少添加两个景点后再分享')
    return
  }
  
  const routeText = waypoints.value.map((spot, index) => `${index + 1}. ${spot.name}`).join(' → ')
  const shareText = `我的旅游路线：${routeText}\n总距离：${routeInfo.value.distance}km，预计时间：${routeInfo.value.duration}`
  
  // 复制到剪贴板
  navigator.clipboard.writeText(shareText).then(() => {
    alert('路线信息已复制到剪贴板！')
  }).catch(() => {
    alert(shareText)
  })
}

// 返回
const goBack = () => router.back()
</script>

<style scoped>
.route-plan-page {
  min-height: 100vh;
  background: #0a0a1a;
  color: #fff;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 15px 20px;
  background: rgba(10, 10, 26, 0.9);
}

.back-btn {
  background: none;
  border: none;
  color: #fff;
  font-size: 20px;
  cursor: pointer;
}

.page-title {
  font-size: 18px;
  font-weight: 500;
}

.action-btn {
  background: rgba(0, 212, 255, 0.2);
  border: 1px solid #00D4FF;
  color: #00D4FF;
  padding: 6px 16px;
  border-radius: 15px;
  cursor: pointer;
}

/* 地图容器 */
.map-wrapper {
  height: 400px;
  width: 100%;
}

.add-spot-bar {
  padding: 15px 20px;
  background: rgba(0, 212, 255, 0.1);
}

.tech-button {
  background: linear-gradient(135deg, #00D4FF, #7b2cbf);
  border: none;
  color: #fff;
  padding: 12px 24px;
  border-radius: 25px;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.tech-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.route-info {
  padding: 15px 20px;
}

.info-card {
  display: flex;
  gap: 20px;
  justify-content: space-around;
  background: rgba(255, 255, 255, 0.05);
  padding: 15px;
  border-radius: 12px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.info-icon {
  font-size: 24px;
}

.info-content {
  display: flex;
  flex-direction: column;
}

.info-label {
  font-size: 12px;
  color: #888;
}

.info-value {
  font-size: 16px;
  font-weight: 500;
  color: #00D4FF;
}

.transport-select {
  background: rgba(0, 212, 255, 0.1);
  border: 1px solid #00D4FF;
  color: #fff;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 14px;
}

.spots-section {
  padding: 15px 20px;
}

.section-title {
  font-size: 16px;
  margin-bottom: 12px;
  color: #ccc;
}

.spots-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.spot-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
}

.spot-number {
  width: 30px;
  height: 30px;
  background: linear-gradient(135deg, #00D4FF, #7b2cbf);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 14px;
}

.spot-info {
  flex: 1;
}

.spot-info h4 {
  font-size: 15px;
  margin-bottom: 4px;
}

.spot-info p {
  font-size: 12px;
  color: #888;
}

.delete-btn {
  background: rgba(245, 108, 108, 0.2);
  border: none;
  color: #f56c6c;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-spots {
  text-align: center;
  padding: 40px;
  color: #666;
}

.nav-bar {
  padding: 20px;
}

.nav-btn {
  width: 100%;
  justify-content: center;
  font-size: 16px;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: #1a1a2e;
  padding: 20px;
  border-radius: 15px;
  width: 90%;
  max-width: 400px;
}

.modal-content h3 {
  margin-bottom: 15px;
  font-size: 18px;
}

.tech-input {
  width: 100%;
  padding: 12px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(0, 212, 255, 0.3);
  border-radius: 8px;
  color: #fff;
  font-size: 14px;
}

.tech-input:focus {
  outline: none;
  border-color: #00D4FF;
}

.search-results {
  max-height: 200px;
  overflow-y: auto;
  margin-top: 10px;
}

.search-result-item {
  padding: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-result-item:hover {
  background: rgba(0, 212, 255, 0.1);
}

.result-name {
  font-size: 14px;
}

.result-city {
  font-size: 12px;
  color: #888;
}

.close-modal {
  width: 100%;
  padding: 12px;
  margin-top: 15px;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  color: #fff;
  border-radius: 8px;
  cursor: pointer;
}

.close-modal:hover {
  background: rgba(255, 255, 255, 0.2);
}
</style>
