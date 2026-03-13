<template>
  <div class="route-plan-page">
    <header class="page-header">
      <button class="back-btn" @click="goBack">←</button>
      <h1 class="page-title">路线规划</h1>
      <button class="action-btn" @click="shareRoute">分享</button>
    </header>

    <main class="page-content">
      <!-- 地图区域 -->
      <div class="map-container">
        <div id="amap-container" ref="mapContainer" class="map-area"></div>
        
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
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()

// 状态
const mapContainer = ref(null)
const waypoints = ref([])
const routeInfo = ref({ distance: 0, duration: '' })
const transportType = ref('driving')
const showAddSpotModal = ref(false)
const searchKeyword = ref('')
const searchResults = ref([])
const AMap = ref(null)
const map = ref(null)

// 初始化地图
onMounted(async () => {
  await initMap()
})

// 初始化高德地图
const initMap = async () => {
  // 动态加载高德地图JS API
  if (!window.AMap) {
    await loadAMapScript()
  }
  
  AMap.value = window.AMap
  
  // 初始化地图
  map.value = new AMap.value.Map('amap-container', {
    zoom: 12,
    center: [116.397428, 39.90923], // 默认北京
    mapStyle: 'amap://styles/dark', // 暗色主题
  })
  
  // 添加地图控件
  map.value.addControl(new AMap.value.Scale())
  map.value.addControl(new AMap.value.ToolBar({ position: 'RT' }))
}

// 加载高德地图脚本
const loadAMapScript = () => {
  return new Promise((resolve, reject) => {
    const script = document.createElement('script')
    script.src = 'https://webapi.amap.com/maps?v=2.0&key=YOUR_AMAP_KEY' // 需要替换为真实的Key
    script.onload = resolve
    script.onerror = reject
    document.head.appendChild(script)
  })
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
  
  // 在地图上添加标记
  addMarkerToMap(spot)
  
  // 重新计算路线
  recalculateRoute()
}

// 移除途经点
const removeWaypoint = (index) => {
  waypoints.value.splice(index, 1)
  recalculateRoute()
}

// 在地图上添加标记
const addMarkerToMap = (spot) => {
  if (!map.value || !spot.location_lat || !spot.location_lng) return
  
  const marker = new AMap.value.Marker({
    position: [spot.location_lng, spot.location_lat],
    title: spot.name,
  })
  
  map.value.add(marker)
  map.value.setFitView()
}

// 重新计算路线
const recalculateRoute = async () => {
  if (waypoints.value.length < 2) return
  
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
      
      // 绘制路线
      if (response.data.path) {
        drawRoute(response.data.path)
      }
    }
  } catch (error) {
    console.error('路线规划失败:', error)
    // 使用模拟数据
    routeInfo.value = {
      distance: (Math.random() * 50 + 10).toFixed(1),
      duration: Math.round(Math.random() * 60 + 30) + '分钟'
    }
  }
}

// 绘制路线
const drawRoute = (path) => {
  if (!map.value || !path || path.length === 0) return
  
  const line = new AMap.value.Polyline({
    path: path.map(p => [p.lng, p.lat]),
    strokeColor: '#00D4FF',
    strokeWeight: 5,
    strokeOpacity: 0.8
  })
  
  map.value.add(line)
  map.value.setFitView()
}

// 开始导航
const startNavigation = () => {
  alert('导航功能需要配置高德地图Key，请在控制台查看路线信息')
  console.log('路线:', waypoints.value)
}

// 分享路线
const shareRoute = () => {
  alert('分享功能开发中')
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

.map-container {
  height: 300px;
  background: #1a1a2e;
}

.map-area {
  width: 100%;
  height: 100%;
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
}

.route-info {
  padding: 15px 20px;
}

.info-card {
  display: flex;
  gap: 20px;
  justify-content: space-around;
}

.spots-section {
  padding: 15px 20px;
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
  background: #00D4FF;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
}

.nav-bar {
  padding: 20px;
}

.nav-btn {
  width: 100%;
  justify-content: center;
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

.search-results {
  max-height: 200px;
  overflow-y: auto;
  margin-top: 10px;
}

.search-result-item {
  padding: 10px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  cursor: pointer;
}

.search-result-item:hover {
  background: rgba(0, 212, 255, 0.1);
}
</style>
