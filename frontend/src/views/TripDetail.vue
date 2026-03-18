<template>
  <div class="trip-detail-page">
    <!-- 顶部导航 -->
    <header class="page-header">
      <button class="back-btn" @click="goBack">
        <span class="back-icon">←</span>
      </button>
      <h1 class="page-title">{{ tripTitle }}</h1>
      <button class="action-btn" @click="saveTrip">保存</button>
    </header>

    <main class="main-content">
      <!-- 左侧：天数选择和景点列表 -->
      <aside class="left-panel">
        <!-- 天数选择标签 -->
        <div class="day-tabs">
          <div
            v-for="day in days"
            :key="day"
            class="day-tab"
            :class="{ active: selectedDay === day }"
            @click="selectDay(day)"
          >
            <span class="day-label">第{{ day }}天</span>
            <span class="day-count">{{ getDaySpots(day).length }}个景点</span>
          </div>
        </div>

        <!-- 当前天的景点列表（可拖拽） -->
        <div class="spots-container">
          <div class="spots-header">
            <h3>第{{ selectedDay }}天行程</h3>
            <button class="add-spot-btn" @click="showAddSpotModal">
              <span>+</span> 添加景点
            </button>
          </div>

          <draggable
            v-model="currentDaySpots"
            item-key="id"
            class="spots-list"
            ghost-class="spot-ghost"
            drag-class="spot-dragging"
            :animation="200"
            :delay="0"
            :delay-on-touch-only="true"
            @end="onDragEnd"
          >
            <template #item="{ element: spot, index }">
              <div class="spot-card" title="按住拖动可调整顺序">
                <div class="drag-handle">
                  <span class="drag-icon">⋮⋮</span>
                </div>
                <div class="spot-order">{{ index + 1 }}</div>
                <div class="spot-image">
                  <img :src="spot.image" :alt="spot.name" />
                </div>
                <div class="spot-info">
                  <h4 class="spot-name">{{ spot.name }}</h4>
                  <div class="spot-meta">
                    <span class="spot-rating">⭐ {{ spot.rating?.toFixed(1) || '4.5' }}</span>
                    <span class="spot-duration">⏱️ {{ spot.duration || '2小时' }}</span>
                  </div>
                  <div class="spot-tags" v-if="spot.tags?.length">
                    <span v-for="tag in spot.tags.slice(0, 2)" :key="tag" class="tag">{{ tag }}</span>
                  </div>
                </div>
                <button class="delete-btn" @click="removeSpot(index)">
                  <span>×</span>
                </button>
              </div>
            </template>
          </draggable>

          <!-- 空状态 -->
          <div v-if="currentDaySpots.length === 0" class="empty-state">
            <div class="empty-icon">🗺️</div>
            <p>暂无景点，点击上方按钮添加</p>
          </div>
        </div>

        <!-- 行程统计 -->
        <div class="trip-stats">
          <div class="stat-item">
            <span class="stat-value">{{ totalSpots }}</span>
            <span class="stat-label">总景点</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ days }}</span>
            <span class="stat-label">天数</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ city }}</span>
            <span class="stat-label">目的地</span>
          </div>
        </div>
      </aside>

      <!-- 右侧：高德地图 -->
      <section class="right-panel">
        <div id="amap-container" class="map-container"></div>
        
        <!-- 地图控制按钮 -->
        <div class="map-controls">
          <button class="map-btn" @click="fitView">
            <span>🎯</span> 适应视图
          </button>
          <button class="map-btn" @click="toggleTraffic">
            <span>🚦</span> {{ showTraffic ? '隐藏' : '显示' }}路况
          </button>
        </div>

        <!-- 路线信息 -->
        <div class="route-info" v-if="routeInfo">
          <div class="route-stat">
            <span class="route-icon">📏</span>
            <span>总距离: {{ routeInfo.distance }}公里</span>
          </div>
          <div class="route-stat">
            <span class="route-icon">⏱️</span>
            <span>预计时间: {{ routeInfo.duration }}分钟</span>
          </div>
        </div>
      </section>
    </main>

    <!-- 添加景点弹窗 -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>添加景点到第{{ selectedDay }}天</h3>
          <button class="close-btn" @click="closeModal">×</button>
        </div>
        <div class="modal-body">
          <div class="search-box">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="搜索景点..."
              class="search-input"
            />
          </div>
          <div class="available-spots">
            <div
              v-for="spot in filteredAvailableSpots"
              :key="spot.id"
              class="available-spot-item"
              @click="addSpot(spot)"
            >
              <img :src="spot.image" :alt="spot.name" class="spot-thumb" />
              <div class="spot-brief">
                <h4>{{ spot.name }}</h4>
                <span class="spot-rating-small">⭐ {{ spot.rating?.toFixed(1) || '4.5' }}</span>
              </div>
              <span class="add-icon">+</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import draggable from 'vuedraggable'

const router = useRouter()
const route = useRoute()

// 数据
const city = ref('')
const days = ref(3)
const preferences = ref([])
const selectedSpots = ref([])
const allSpots = ref([])
const selectedDay = ref(1)
const showModal = ref(false)
const searchQuery = ref('')
const routeInfo = ref(null)
const showTraffic = ref(false)

// 每天的景点分配
const daySpotsMap = ref({})

// 高德地图相关
let map = null
let markers = []
let polylines = []
let trafficLayer = null

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

const tripTitle = computed(() => {
  return `${city.value}${days.value}日${preferencesText.value || '游'}`
})

// 当前选中的天的景点列表
const currentDaySpots = computed({
  get() {
    return daySpotsMap.value[selectedDay.value] || []
  },
  set(value) {
    // 使用 Vue 的响应式方式更新数组
    const dayKey = selectedDay.value
    daySpotsMap.value[dayKey] = [...value]
  }
})

// 获取某天的景点
const getDaySpots = (day) => {
  return daySpotsMap.value[day] || []
}

// 总景点数
const totalSpots = computed(() => {
  return Object.values(daySpotsMap.value).flat().length
})

// 可添加的景点（未在当前天使用的）
const availableSpots = computed(() => {
  const usedIds = new Set(currentDaySpots.value.map(s => s.id))
  return allSpots.value.filter(spot => !usedIds.has(spot.id))
})

// 过滤后的可添加景点
const filteredAvailableSpots = computed(() => {
  if (!searchQuery.value) return availableSpots.value
  const query = searchQuery.value.toLowerCase()
  return availableSpots.value.filter(spot => 
    spot.name.toLowerCase().includes(query)
  )
})

// 加载数据
onMounted(async () => {
  // 优先从 currentTrip 读取（从行程列表点击进入）
  const currentTripStr = localStorage.getItem('currentTrip')
  
  if (currentTripStr && route.query.id) {
    // 从行程列表进入，读取保存的行程数据
    const currentTrip = JSON.parse(currentTripStr)
    city.value = currentTrip.city
    days.value = currentTrip.days
    preferences.value = currentTrip.preferences || []
    
    // 恢复每天的景点分配
    if (currentTrip.daySpots) {
      daySpotsMap.value = currentTrip.daySpots
      allSpots.value = Object.values(currentTrip.daySpots).flat()
    }
  } else {
    // 从创建流程进入
    city.value = route.query.city || localStorage.getItem('tripCity') || '北京'
    days.value = parseInt(route.query.days) || parseInt(localStorage.getItem('tripDays')) || 3
    
    const prefStr = route.query.preferences || localStorage.getItem('tripPreferences') || ''
    preferences.value = prefStr.split(',').filter(p => p)
    
    // 从 localStorage 读取已选择的景点（现在是完整的对象数组）
    const spotsStr = localStorage.getItem('selectedSpots') || '[]'
    selectedSpots.value = JSON.parse(spotsStr)
    
    // 如果有已选择的景点，直接使用它们
    if (selectedSpots.value.length > 0) {
      allSpots.value = selectedSpots.value
      // 平均分配景点到各天
      distributeSpotsToDays()
    } else {
      // 加载所有景点数据
      await loadAllSpots()
      // 平均分配景点到各天
      distributeSpotsToDays()
    }
  }
  
  // 初始化地图
  nextTick(() => {
    initMap()
  })
})

// 加载所有景点
const loadAllSpots = async () => {
  try {
    const response = await fetch(`/api/spots?city=${encodeURIComponent(city.value)}`)
    const data = await response.json()
    if (data && data.length > 0) {
      allSpots.value = data
    } else {
      // 使用模拟数据
      allSpots.value = getMockSpots()
    }
  } catch (error) {
    console.error('加载景点失败:', error)
    allSpots.value = getMockSpots()
  }
}

// 模拟景点数据
const getMockSpots = () => {
  const baseSpots = [
    { id: 1, name: '故宫博物院', rating: 4.9, favorites: 12580, tags: ['history', 'landmark', 'must_visit'], duration: '4小时', image: '/images/spots/beijing/beijing_gugong_bowuyuan.jpg', location: [116.397477, 39.903738] },
    { id: 2, name: '天安门广场', rating: 4.8, favorites: 9876, tags: ['landmark', 'must_visit', 'photo'], duration: '1小时', image: '/images/spots/beijing/beijing_tiananmen_guangchang.jpg', location: [116.397477, 39.905489] },
    { id: 3, name: '颐和园', rating: 4.8, favorites: 8654, tags: ['scenery', 'history', 'must_visit'], duration: '4小时', image: '/images/spots/beijing/beijing_yiheyuan.jpg', location: [116.275467, 39.994867] },
    { id: 4, name: '八达岭长城', rating: 4.9, favorites: 11234, tags: ['scenery', 'history', 'must_visit'], duration: '5小时', image: '/images/spots/beijing/beijing_badaling_changcheng.jpg', location: [116.016953, 40.353469] },
    { id: 5, name: '天坛公园', rating: 4.7, favorites: 6543, tags: ['history', 'scenery'], duration: '2小时', image: '/images/spots/beijing/beijing_tiantan_gongyuan.jpg', location: [116.406588, 39.883365] },
    { id: 6, name: '南锣鼓巷', rating: 4.5, favorites: 7890, tags: ['food', 'local_life', 'citywalk'], duration: '2小时', image: '/images/spots/beijing/beijing_nanluoguxiang.jpg', location: [116.403147, 39.937243] },
    { id: 7, name: '798艺术区', rating: 4.6, favorites: 5432, tags: ['photo', 'leisure', 'art'], duration: '3小时', image: '/images/spots/beijing/beijing_798_art.jpg', location: [116.500876, 39.985432] },
    { id: 8, name: '什刹海', rating: 4.6, favorites: 6789, tags: ['scenery', 'food', 'local_life'], duration: '2小时', image: '/images/spots/beijing/beijing_shichahai.jpg', location: [116.387654, 39.943210] },
    { id: 9, name: '圆明园', rating: 4.5, favorites: 4567, tags: ['history', 'scenery'], duration: '3小时', image: '/images/spots/beijing/beijing_yuanmingyuan.jpg', location: [116.298765, 40.009876] },
  ]
  
  // 根据已选择的景点ID过滤，如果没有则使用全部
  if (selectedSpots.value.length > 0) {
    const selectedIds = selectedSpots.value.map(s => s.id || s)
    return baseSpots.filter(s => selectedIds.includes(s.id))
  }
  return baseSpots
}

// 平均分配景点到各天
const distributeSpotsToDays = () => {
  const spots = [...allSpots.value]
  const spotsPerDay = Math.ceil(spots.length / days.value)
  
  for (let day = 1; day <= days.value; day++) {
    const startIndex = (day - 1) * spotsPerDay
    const endIndex = Math.min(startIndex + spotsPerDay, spots.length)
    daySpotsMap.value[day] = spots.slice(startIndex, endIndex)
  }
}

// 初始化高德地图
const initMap = () => {
  if (typeof AMap === 'undefined') {
    console.error('高德地图API未加载')
    return
  }
  
  map = new AMap.Map('amap-container', {
    zoom: 12,
    center: getCityCenter(),
    viewMode: '2D'
  })
  
  // 添加地图控件
  AMap.plugin(['AMap.ToolBar', 'AMap.Scale'], () => {
    map.addControl(new AMap.ToolBar())
    map.addControl(new AMap.Scale())
  })
  
  // 显示当前天的路线
  updateMapRoute()
}

// 获取城市中心坐标
const getCityCenter = () => {
  const cityCenters = {
    '北京': [116.397477, 39.903738],
    '上海': [121.473667, 31.230525],
    '广州': [113.264434, 23.129163],
    '深圳': [114.057868, 22.543099],
    '杭州': [120.155070, 30.274085],
    '成都': [104.066541, 30.572269],
    '西安': [108.939770, 34.341574],
    '南京': [118.796877, 32.060255]
  }
  return cityCenters[city.value] || [116.397477, 39.903738]
}

// 更新地图路线
const updateMapRoute = () => {
  if (!map) return
  
  // 清除旧的标记和路线
  clearMapOverlays()
  
  const spots = currentDaySpots.value
  if (spots.length === 0) return
  
  // 添加标记
  const path = []
  spots.forEach((spot, index) => {
    const position = spot.location || getMockLocation(spot.name)
    path.push(position)
    
    const marker = new AMap.Marker({
      position: position,
      content: `<div class="custom-marker">${index + 1}</div>`,
      offset: new AMap.Pixel(-15, -30)
    })
    
    marker.setMap(map)
    markers.push(marker)
    
    // 添加信息窗体
    const infoWindow = new AMap.InfoWindow({
      content: `<div style="padding: 10px;"><h4>${spot.name}</h4><p>⭐ ${spot.rating?.toFixed(1) || '4.5'}</p></div>`,
      offset: new AMap.Pixel(0, -30)
    })
    
    marker.on('click', () => {
      infoWindow.open(map, marker.getPosition())
    })
  })
  
  // 绘制路线
  if (path.length > 1) {
    const polyline = new AMap.Polyline({
      path: path,
      strokeColor: '#00d4ff',
      strokeWeight: 4,
      strokeOpacity: 0.8,
      showDir: true
    })
    polyline.setMap(map)
    polylines.push(polyline)
    
    // 计算路线信息
    calculateRouteInfo(path)
  }
  
  // 适应视图
  fitView()
}

// 获取模拟位置（实际应该从数据中获取）
const getMockLocation = (spotName) => {
  const mockLocations = {
    '故宫博物院': [116.397477, 39.903738],
    '天安门广场': [116.397477, 39.905489],
    '颐和园': [116.275467, 39.994867],
    '八达岭长城': [116.016953, 40.353469],
    '天坛公园': [116.406588, 39.883365],
    '南锣鼓巷': [116.403147, 39.937243],
    '798艺术区': [116.500876, 39.985432],
    '什刹海': [116.387654, 39.943210],
    '圆明园': [116.298765, 40.009876]
  }
  return mockLocations[spotName] || [116.397477 + Math.random() * 0.1, 39.903738 + Math.random() * 0.1]
}

// 清除地图覆盖物
const clearMapOverlays = () => {
  markers.forEach(marker => marker.setMap(null))
  markers = []
  polylines.forEach(line => line.setMap(null))
  polylines = []
}

// 计算路线信息
const calculateRouteInfo = (path) => {
  let totalDistance = 0
  for (let i = 0; i < path.length - 1; i++) {
    totalDistance += AMap.GeometryUtil.distance(path[i], path[i + 1])
  }
  
  routeInfo.value = {
    distance: (totalDistance / 1000).toFixed(1),
    duration: Math.ceil(totalDistance / 1000 / 30 * 60) // 假设平均速度30km/h
  }
}

// 适应视图
const fitView = () => {
  if (!map || markers.length === 0) return
  map.setFitView(markers)
}

// 切换路况
const toggleTraffic = () => {
  if (!map) return
  
  if (showTraffic.value) {
    if (trafficLayer) {
      trafficLayer.hide()
    }
    showTraffic.value = false
  } else {
    if (!trafficLayer) {
      trafficLayer = new AMap.TileLayer.Traffic({
        zIndex: 10
      })
      trafficLayer.setMap(map)
    } else {
      trafficLayer.show()
    }
    showTraffic.value = true
  }
}

// 选择天数
const selectDay = (day) => {
  selectedDay.value = day
  nextTick(() => {
    updateMapRoute()
  })
}

// 拖拽结束
const onDragEnd = (evt) => {
  console.log('拖拽结束', evt)
  // 强制更新视图
  nextTick(() => {
    updateMapRoute()
    ElMessage.success('顺序已更新')
  })
}

// 显示添加景点弹窗
const showAddSpotModal = () => {
  showModal.value = true
  searchQuery.value = ''
}

// 关闭弹窗
const closeModal = () => {
  showModal.value = false
}

// 添加景点
const addSpot = (spot) => {
  currentDaySpots.value.push(spot)
  closeModal()
  nextTick(() => {
    updateMapRoute()
  })
  ElMessage.success(`已添加 ${spot.name}`)
}

// 删除景点
const removeSpot = (index) => {
  const spot = currentDaySpots.value[index]
  currentDaySpots.value.splice(index, 1)
  nextTick(() => {
    updateMapRoute()
  })
  ElMessage.success(`已删除 ${spot.name}`)
}

// 返回
const goBack = () => {
  router.push('/trips')
}

// 保存行程
const saveTrip = () => {
  // 生成唯一ID
  const tripId = 'trip_' + Date.now()
  
  const tripData = {
    id: tripId,
    title: tripTitle.value,
    city: city.value,
    days: days.value,
    preferences: preferences.value,
    daySpots: daySpotsMap.value,
    totalSpots: totalSpots.value,
    createTime: new Date().toISOString(),
    updateTime: new Date().toISOString()
  }
  
  // 保存到本地存储
  const savedTrips = JSON.parse(localStorage.getItem('savedTrips') || '[]')
  
  // 检查是否已存在相同行程（根据城市、天数、创建时间判断）
  const existingIndex = savedTrips.findIndex(t => 
    t.city === tripData.city && 
    t.days === tripData.days && 
    t.createTime === tripData.createTime
  )
  
  if (existingIndex > -1) {
    // 更新已有行程
    savedTrips[existingIndex] = tripData
    ElMessage.success('行程已更新')
  } else {
    // 添加新行程
    savedTrips.push(tripData)
    ElMessage.success('行程已保存')
  }
  
  localStorage.setItem('savedTrips', JSON.stringify(savedTrips))
  
  // 同时保存为当前行程
  localStorage.setItem('currentTrip', JSON.stringify(tripData))
}

// 监听当前天变化，更新地图
watch(selectedDay, () => {
  nextTick(() => {
    updateMapRoute()
  })
})
</script>

<style scoped>
.trip-detail-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #0a0a1a 0%, #1a1a2e 100%);
  display: flex;
  flex-direction: column;
}

/* 顶部导航 */
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 15px 20px;
  background: rgba(10, 10, 26, 0.9);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--border-color);
  flex-shrink: 0;
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

.page-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.action-btn {
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  border: none;
  color: #000;
  font-size: 14px;
  font-weight: 600;
  padding: 8px 20px;
  border-radius: 20px;
  cursor: pointer;
}

/* 主内容区 - 左右分栏 */
.main-content {
  display: flex;
  flex: 1;
  overflow: hidden;
}

/* 左侧面板 */
.left-panel {
  width: 420px;
  display: flex;
  flex-direction: column;
  border-right: 1px solid var(--border-color);
  background: rgba(10, 10, 26, 0.5);
}

/* 天数标签 */
.day-tabs {
  display: flex;
  gap: 10px;
  padding: 15px;
  overflow-x: auto;
  border-bottom: 1px solid var(--border-color);
  flex-shrink: 0;
}

.day-tabs::-webkit-scrollbar {
  height: 4px;
}

.day-tabs::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 2px;
}

.day-tab {
  flex-shrink: 0;
  padding: 10px 20px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;
}

.day-tab:hover {
  background: rgba(0, 212, 255, 0.1);
  border-color: var(--primary-color);
}

.day-tab.active {
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  border-color: transparent;
  color: #000;
}

.day-label {
  display: block;
  font-size: 14px;
  font-weight: 600;
}

.day-count {
  display: block;
  font-size: 12px;
  opacity: 0.7;
  margin-top: 2px;
}

/* 景点容器 */
.spots-container {
  flex: 1;
  overflow-y: auto;
  padding: 15px;
}

.spots-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.spots-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.add-spot-btn {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 8px 15px;
  background: rgba(0, 212, 255, 0.1);
  border: 1px solid var(--primary-color);
  border-radius: 20px;
  color: var(--primary-color);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.add-spot-btn:hover {
  background: var(--primary-color);
  color: #000;
}

/* 景点列表 */
.spots-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.spot-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  transition: all 0.3s ease;
}

.spot-card:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(0, 212, 255, 0.3);
}

.drag-handle {
  cursor: grab;
  padding: 5px;
  color: var(--text-secondary);
}

.drag-handle:active {
  cursor: grabbing;
}

.drag-icon {
  font-size: 12px;
  letter-spacing: 2px;
}

.spot-order {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  border-radius: 50%;
  font-size: 12px;
  font-weight: 600;
  color: #000;
  flex-shrink: 0;
}

.spot-image {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
}

.spot-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.spot-info {
  flex: 1;
  min-width: 0;
}

.spot-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 5px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.spot-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 5px;
}

.spot-tags {
  display: flex;
  gap: 5px;
  flex-wrap: wrap;
}

.tag {
  padding: 2px 8px;
  background: rgba(0, 212, 255, 0.1);
  border-radius: 10px;
  font-size: 11px;
  color: var(--primary-color);
}

.delete-btn {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 71, 87, 0.1);
  border: 1px solid rgba(255, 71, 87, 0.3);
  border-radius: 50%;
  color: #ff4757;
  font-size: 18px;
  cursor: pointer;
  flex-shrink: 0;
  transition: all 0.3s ease;
}

.delete-btn:hover {
  background: rgba(255, 71, 87, 0.2);
}

/* 拖拽样式 */
.spot-ghost {
  opacity: 0.5;
  background: rgba(0, 212, 255, 0.1);
  border: 2px dashed var(--primary-color);
}

.spot-dragging {
  opacity: 0.8;
  transform: scale(1.02);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-secondary);
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 15px;
}

/* 行程统计 */
.trip-stats {
  display: flex;
  justify-content: space-around;
  padding: 15px;
  border-top: 1px solid var(--border-color);
  background: rgba(10, 10, 26, 0.8);
  flex-shrink: 0;
}

.stat-item {
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 18px;
  font-weight: 700;
  color: var(--primary-color);
}

.stat-label {
  display: block;
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 3px;
}

/* 右侧面板 - 地图 */
.right-panel {
  flex: 1;
  position: relative;
  background: #1a1a2e;
}

.map-container {
  width: 100%;
  height: 100%;
}

/* 地图控制按钮 */
.map-controls {
  position: absolute;
  top: 15px;
  right: 15px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  z-index: 100;
}

.map-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 15px;
  background: rgba(10, 10, 26, 0.9);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 13px;
  cursor: pointer;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.map-btn:hover {
  background: rgba(0, 212, 255, 0.1);
  border-color: var(--primary-color);
}

/* 路线信息 */
.route-info {
  position: absolute;
  bottom: 20px;
  left: 20px;
  right: 20px;
  display: flex;
  gap: 20px;
  padding: 15px 20px;
  background: rgba(10, 10, 26, 0.9);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  backdrop-filter: blur(10px);
  z-index: 100;
}

.route-stat {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: var(--text-primary);
}

.route-icon {
  font-size: 16px;
}

/* 弹窗 */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  width: 100%;
  max-width: 500px;
  max-height: 80vh;
  background: linear-gradient(180deg, #1a1a2e 0%, #0a0a1a 100%);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid var(--border-color);
}

.modal-header h3 {
  font-size: 16px;
  font-weight: 600;
}

.close-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 50%;
  color: var(--text-primary);
  font-size: 20px;
  cursor: pointer;
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.search-box {
  margin-bottom: 15px;
}

.search-input {
  width: 100%;
  padding: 12px 15px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  color: var(--text-primary);
  font-size: 14px;
}

.search-input::placeholder {
  color: var(--text-secondary);
}

.search-input:focus {
  outline: none;
  border-color: var(--primary-color);
}

.available-spots {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.available-spot-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.available-spot-item:hover {
  background: rgba(0, 212, 255, 0.1);
  border-color: var(--primary-color);
}

.spot-thumb {
  width: 50px;
  height: 50px;
  border-radius: 8px;
  object-fit: cover;
}

.spot-brief {
  flex: 1;
}

.spot-brief h4 {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 4px;
}

.spot-rating-small {
  font-size: 12px;
  color: var(--text-secondary);
}

.add-icon {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--primary-color);
  border-radius: 50%;
  color: #000;
  font-size: 18px;
  font-weight: 600;
}

/* 自定义地图标记样式 */
:global(.custom-marker) {
  width: 30px;
  height: 30px;
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  border-radius: 50% 50% 50% 0;
  transform: rotate(-45deg);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-weight: 600;
  font-size: 14px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

:global(.custom-marker::after) {
  content: attr(data-index);
  transform: rotate(45deg);
}

/* 响应式 */
@media (max-width: 900px) {
  .main-content {
    flex-direction: column;
  }
  
  .left-panel {
    width: 100%;
    height: 50vh;
    border-right: none;
    border-bottom: 1px solid var(--border-color);
  }
  
  .right-panel {
    height: 50vh;
  }
}
</style>
