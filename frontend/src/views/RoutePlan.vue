<template>
  <div class="route-plan-page">
    <Navbar />

    <header class="page-header">
      <button class="back-btn" @click="goBack">←</button>
      <h1 class="page-title">路线规划</h1>
      <span v-if="isTourMode" class="mode-badge tour">🔄 巡游模式</span>
      <span v-else-if="destinations.length === 1" class="mode-badge direct">📍 直达模式</span>
    </header>

    <main class="page-content">
      <!-- 景区/校园选择 -->
      <section class="spot-select-section">
        <label class="section-label">选择景区 / 校园</label>
        <div class="spot-select-row">
          <select v-model="selectedSpotId" class="tech-select" @change="onSpotChange">
            <option :value="null" disabled>-- 请选择 --</option>
            <option v-for="s in availableSpots" :key="s.id" :value="s.id">
              {{ s.name }}
            </option>
          </select>
          <span v-if="spotLoading" class="loading-hint">加载中...</span>
        </div>
      </section>

      <!-- 地图区域 -->
      <div class="map-wrapper">
        <AmapContainer ref="amapRef" />
      </div>

      <!-- 模式提示横幅 -->
      <div v-if="isTourMode && destinations.length >= 2" class="tour-banner">
        <span class="tour-icon">🗺️</span>
        <div class="tour-text">
          <strong>巡游模式已激活</strong>
          <p>系统将自动规划最优巡游路线，遍历全部 {{ destinations.length }} 个目的地后返回起点</p>
        </div>
      </div>

      <!-- 起点 -->
      <section class="point-section start-section">
        <div class="point-header">
          <span class="point-marker start">起</span>
          <span class="point-label">起点</span>
        </div>
        <div v-if="startNode" class="point-card selected">
          <div class="point-info">
            <h4>{{ startNode.name }}</h4>
            <p>{{ startNode.type === 'entrance' ? '入口' : startNode.type === 'building' ? '建筑' : '设施' }}</p>
          </div>
        </div>
        <button v-else class="add-point-btn" :disabled="!selectedSpotId" @click="openSearchModal('start')">
          + 选择起点
        </button>
      </section>

      <!-- 目的地列表 -->
      <section class="point-section">
        <div class="point-header">
          <span class="point-marker end">终</span>
          <span class="point-label">
            目的地
            <span v-if="destinations.length > 0" class="count-badge">{{ destinations.length }}</span>
          </span>
        </div>

        <div class="destinations-list">
          <div
            v-for="(dest, index) in destinations"
            :key="dest.id"
            class="dest-card"
          >
            <div class="dest-number">{{ index + 1 }}</div>
            <div class="dest-info">
              <h4>{{ dest.name }}</h4>
              <p>{{ dest.type === 'entrance' ? '入口' : dest.type === 'building' ? '建筑' : '设施' }}</p>
            </div>
            <button class="dest-remove" @click="removeDestination(index)" title="移除此目的地">×</button>
          </div>

          <div v-if="destinations.length === 0 && !selectedSpotId" class="empty-hint">
            请先在上方选择景区/校园
          </div>
          <div v-else-if="destinations.length === 0" class="empty-hint">
            添加至少 1 个目的地以规划路线
          </div>
        </div>

        <button
          class="add-dest-btn"
          :disabled="!selectedSpotId"
          @click="openSearchModal('destination')"
        >
          + 添加目的地
        </button>
      </section>

      <!-- 交通方式 -->
      <section class="transport-section">
        <span class="section-label">交通方式</span>
        <div class="transport-options">
          <button
            v-for="opt in transportOptions"
            :key="opt.value"
            class="transport-chip"
            :class="{ active: transportMode === opt.value }"
            @click="transportMode = opt.value"
          >
            {{ opt.icon }} {{ opt.label }}
          </button>
        </div>
      </section>

      <!-- 路线信息 -->
      <section class="route-result" v-if="routeResult">
        <div class="result-header">
          <h3>路线规划结果</h3>
          <span class="algo-badge">{{ routeResult.algorithm }}</span>
        </div>

        <div class="info-card">
          <div class="info-item">
            <span class="info-icon">📏</span>
            <div class="info-content">
              <span class="info-label">总距离</span>
              <span class="info-value">{{ (routeResult.distance / 1000).toFixed(2) }} km</span>
            </div>
          </div>
          <div class="info-item">
            <span class="info-icon">⏱️</span>
            <div class="info-content">
              <span class="info-label">预计时间</span>
              <span class="info-value">{{ formatDuration(routeResult.duration) }}</span>
            </div>
          </div>
          <div class="info-item">
            <span class="info-icon">📊</span>
            <div class="info-content">
              <span class="info-label">算法</span>
              <span class="info-value">{{ routeResult.algorithm === 'tsp_exact_dp' ? '精确DP' : routeResult.algorithm === 'tsp_greedy_2opt' ? '启发式TSP' : 'Dijkstra' }}</span>
            </div>
          </div>
        </div>

        <!-- TSP 最优顺序展示 -->
        <div v-if="routeResult.ordered_stop_names?.length" class="ordered-stops">
          <span class="stops-label">最优访问顺序：</span>
          <div class="stops-flow">
            <span
              v-for="(name, idx) in routeResult.ordered_stop_names"
              :key="idx"
              class="stop-chip"
              :class="{
                'is-start': idx === 0,
                'is-dest': idx > 0 && idx < routeResult.ordered_stop_names.length - 1,
                'is-return': idx === routeResult.ordered_stop_names.length - 1 && routeResult.return_to_start,
              }"
            >
              {{ name }}
              <span v-if="idx < routeResult.ordered_stop_names.length - 1" class="arrow">→</span>
            </span>
          </div>
        </div>
      </section>

      <!-- 规划按钮 -->
      <div class="action-bar">
        <button
          class="plan-btn"
          :disabled="!canPlan"
          :class="{ ready: canPlan }"
          @click="planRoute"
        >
          <span v-if="isTourMode">🗺️ 开始巡游规划</span>
          <span v-else>🧭 开始规划路线</span>
        </button>
        <p v-if="!canPlan && selectedSpotId" class="action-hint">
          请设置起点并添加至少 1 个目的地
        </p>
      </div>
    </main>

    <!-- 节点搜索弹窗 -->
    <div v-if="showSearchModal" class="modal-overlay" @click.self="closeSearchModal">
      <div class="modal-content">
        <h3>{{ searchMode === 'start' ? '选择起点' : '添加目的地' }}</h3>
        <input
          type="text"
          class="tech-input"
          :placeholder="searchMode === 'start' ? '搜索入口、建筑或设施...' : '搜索目的地...'"
          v-model="searchKeyword"
          @input="searchNodes"
        />
        <div class="search-results">
          <div
            v-for="node in searchResults"
            :key="node.id"
            class="search-result-item"
            :class="{ disabled: isNodeAlreadySelected(node.id) }"
            @click="!isNodeAlreadySelected(node.id) && selectNode(node)"
          >
            <div class="result-main">
              <span class="result-name">{{ node.name }}</span>
              <span class="result-type">{{ node.type === 'entrance' ? '入口' : node.type === 'building' ? '建筑' : '设施' }}</span>
            </div>
            <span v-if="isNodeAlreadySelected(node.id)" class="already-tag">已选</span>
          </div>
          <div v-if="searchResults.length === 0 && searchKeyword.length >= 1" class="no-results">
            未找到匹配节点
          </div>
        </div>
        <button class="close-modal" @click="closeSearchModal">关闭</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import AmapContainer from '../components/AmapContainer.vue'
import Navbar from '../components/Navbar.vue'

const router = useRouter()
const API_BASE = 'http://localhost:8000'

// ─── 地图引用 ───
const amapRef = ref(null)

// ─── 景区/校园 ───
const availableSpots = ref([])
const selectedSpotId = ref(null)
const spotLoading = ref(false)
const spotNodes = ref([])

// ─── 路由参数 ───
const startNode = ref(null)
const destinations = ref([])
const transportMode = ref('walk')
const transportOptions = [
  { value: 'walk', label: '步行', icon: '🚶' },
  { value: 'bike', label: '骑行', icon: '🚲' },
  { value: 'shuttle', label: '电瓶车', icon: '🚌' },
  { value: 'smart', label: '智能混合', icon: '⚡' },
]

// ─── 搜索结果 ───
const showSearchModal = ref(false)
const searchMode = ref('destination') // 'start' | 'destination'
const searchKeyword = ref('')
const searchResults = ref([])

// ─── 路线结果 ───
const routeResult = ref(null)

// ─── 计算属性 ───
const isTourMode = computed(() => destinations.value.length >= 2)

const canPlan = computed(() =>
  selectedSpotId.value && startNode.value && destinations.value.length >= 1
)

// ─── 生命周期 ───
onMounted(async () => {
  await fetchAvailableSpots()
})

// ─── API 调用 ───
const fetchAvailableSpots = async () => {
  try {
    // 优先使用可导航场所接口（有道路网络数据的景区/校园）
    const res = await axios.get(`${API_BASE}/api/route/navigable-spots`)
    if (res.data?.spots?.length) {
      availableSpots.value = res.data.spots
      return
    }
  } catch (e) {
    console.warn('navigable-spots 接口不可用，降级到通用景点接口:', e.message)
  }
  // 降级：使用通用景点接口
  try {
    const res = await axios.get(`${API_BASE}/api/spots?limit=100`)
    if (res.data?.spots) {
      availableSpots.value = res.data.spots
    }
  } catch (e2) {
    console.error('获取景区列表失败:', e2)
  }
}

const fetchSpotNodes = async (spotId) => {
  spotLoading.value = true
  try {
    const res = await axios.get(`${API_BASE}/api/route/nodes/${spotId}`)
    spotNodes.value = res.data?.nodes || []
  } catch (e) {
    console.error('获取节点失败:', e)
    spotNodes.value = []
  } finally {
    spotLoading.value = false
  }
}

const onSpotChange = async () => {
  // 重置选择
  startNode.value = null
  destinations.value = []
  routeResult.value = null

  if (selectedSpotId.value) {
    await fetchSpotNodes(selectedSpotId.value)
  }
}

// ─── 节点搜索（本地过滤） ───
const searchNodes = () => {
  const kw = searchKeyword.value.trim().toLowerCase()
  if (kw.length < 1) {
    searchResults.value = []
    return
  }
  const allNodes = spotNodes.value
  // 过滤：名称或类型匹配，且排除纯坐标节点
  searchResults.value = allNodes
    .filter(n => {
      const name = (n.name || '').toLowerCase()
      const type = (n.type || '').toLowerCase()
      return name.includes(kw) || type.includes(kw)
    })
    .slice(0, 20)
}

const isNodeAlreadySelected = (nodeId) => {
  if (startNode.value?.id === nodeId) return true
  return destinations.value.some(d => d.id === nodeId)
}

const openSearchModal = (mode) => {
  searchMode.value = mode
  searchKeyword.value = ''
  searchResults.value = []
  showSearchModal.value = true
}

const closeSearchModal = () => {
  showSearchModal.value = false
  searchKeyword.value = ''
  searchResults.value = []
}

const selectNode = (node) => {
  if (searchMode.value === 'start') {
    startNode.value = { ...node }
  } else {
    destinations.value.push({ ...node })
  }
  closeSearchModal()
}

const removeDestination = (index) => {
  destinations.value.splice(index, 1)
  // 目的地变更后清除旧结果
  routeResult.value = null
}

// 监听关键参数变化，清除旧结果
watch([startNode, destinations, transportMode], () => {
  routeResult.value = null
})

// ─── 智能路线规划 ───
const planRoute = async () => {
  if (!canPlan.value) return

  const destIds = destinations.value.map(d => d.id)
  // 巡游模式（≥2个目的地）自动开启 return_to_start
  const returnToStart = isTourMode.value

  try {
    const res = await axios.post(`${API_BASE}/api/route/plan-smart`, {
      spot_id: selectedSpotId.value,
      start_node_id: startNode.value.id,
      destination_ids: destIds,
      return_to_start: returnToStart,
      strategy: 'shortest_time',
      transport_mode: transportMode.value,
    })

    if (res.data?.error) {
      alert(`路线规划失败：${res.data.error}`)
      routeResult.value = null
      return
    }

    routeResult.value = res.data

    // 在地图上绘制路径
    if (amapRef.value && res.data.path?.length) {
      drawPathOnMap(res.data.path)
    }
  } catch (e) {
    console.error('路线规划失败:', e)
    alert('路线规划请求失败，请检查后端服务')
  }
}

const drawPathOnMap = (pathNodes) => {
  if (!amapRef.value || !pathNodes.length) return

  // 设置起点标记
  const first = pathNodes[0]
  const last = pathNodes[pathNodes.length - 1]
  if (first) amapRef.value.setStart(first.lng, first.lat)
  if (last) amapRef.value.setEnd(last.lng, last.lat)

  // 延迟执行路径绘制（等待地图就绪）
  setTimeout(() => {
    amapRef.value?.planRoute?.()
  }, 500)
}

// ─── 工具函数 ───
const formatDuration = (seconds) => {
  if (!seconds || seconds <= 0) return '--'
  if (seconds < 60) return `${seconds}秒`
  const mins = Math.floor(seconds / 60)
  if (mins < 60) return `${mins}分钟`
  const hours = Math.floor(mins / 60)
  const remainMins = mins % 60
  return remainMins > 0 ? `${hours}小时${remainMins}分钟` : `${hours}小时`
}

const goBack = () => router.back()
</script>

<style scoped>
/* ─── 基础布局 ─── */
.route-plan-page {
  min-height: 100vh;
  background: #0a0a1a;
  color: #fff;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 15px 20px;
  background: rgba(10, 10, 26, 0.95);
  backdrop-filter: blur(10px);
  position: sticky;
  top: 0;
  z-index: 100;
}

.back-btn {
  background: none;
  border: none;
  color: #fff;
  font-size: 20px;
  cursor: pointer;
  padding: 4px 8px;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
  flex: 1;
}

/* ─── 模式徽章 ─── */
.mode-badge {
  font-size: 12px;
  padding: 4px 12px;
  border-radius: 20px;
  font-weight: 600;
  white-space: nowrap;
}

.mode-badge.tour {
  background: linear-gradient(135deg, rgba(255, 159, 67, 0.2), rgba(255, 107, 107, 0.2));
  border: 1px solid rgba(255, 159, 67, 0.4);
  color: #ff9f43;
}

.mode-badge.direct {
  background: rgba(0, 212, 255, 0.15);
  border: 1px solid rgba(0, 212, 255, 0.3);
  color: #00d4ff;
}

.page-content {
  padding: 0 20px 40px;
}

/* ─── 景区选择 ─── */
.spot-select-section {
  padding: 16px 0;
}

.section-label {
  display: block;
  font-size: 13px;
  color: rgba(255,255,255,0.55);
  margin-bottom: 8px;
  font-weight: 500;
}

.spot-select-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.tech-select {
  flex: 1;
  padding: 10px 14px;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 10px;
  color: #fff;
  font-size: 14px;
  outline: none;
  cursor: pointer;
}

.tech-select:focus {
  border-color: rgba(0, 212, 255, 0.4);
}

.tech-select option {
  background: #1a1a2e;
  color: #fff;
}

.loading-hint {
  font-size: 12px;
  color: rgba(255,255,255,0.4);
}

/* ─── 地图 ─── */
.map-wrapper {
  height: 280px;
  width: 100%;
  border-radius: 14px;
  overflow: hidden;
  margin-bottom: 16px;
  border: 1px solid rgba(255,255,255,0.08);
}

/* ─── 巡游横幅 ─── */
.tour-banner {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px 16px;
  background: linear-gradient(135deg, rgba(255,159,67,0.08), rgba(255,107,107,0.06));
  border: 1px solid rgba(255,159,67,0.2);
  border-radius: 12px;
  margin-bottom: 16px;
}

.tour-icon {
  font-size: 24px;
  flex-shrink: 0;
  margin-top: 2px;
}

.tour-text strong {
  font-size: 14px;
  color: #ff9f43;
  display: block;
  margin-bottom: 4px;
}

.tour-text p {
  font-size: 12px;
  color: rgba(255,255,255,0.55);
  margin: 0;
  line-height: 1.5;
}

/* ─── 点位区域 ─── */
.point-section {
  margin-bottom: 20px;
}

.point-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.point-marker {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 700;
  color: #fff;
}

.point-marker.start {
  background: linear-gradient(135deg, #00d4ff, #0090ff);
}

.point-marker.end {
  background: linear-gradient(135deg, #ff6b6b, #ee5a24);
}

.point-label {
  font-size: 14px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.count-badge {
  font-size: 11px;
  background: rgba(255,255,255,0.1);
  padding: 2px 8px;
  border-radius: 10px;
  color: rgba(255,255,255,0.7);
}

/* ─── 点位卡片 ─── */
.point-card {
  padding: 14px;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 12px;
}

.point-card.selected {
  border-color: rgba(0,212,255,0.25);
  background: rgba(0,212,255,0.04);
}

.point-info h4 {
  font-size: 14px;
  font-weight: 600;
  margin: 0 0 4px;
}

.point-info p {
  font-size: 12px;
  color: rgba(255,255,255,0.45);
  margin: 0;
}

.add-point-btn {
  width: 100%;
  padding: 12px;
  background: rgba(255,255,255,0.04);
  border: 1px dashed rgba(255,255,255,0.15);
  border-radius: 10px;
  color: rgba(255,255,255,0.5);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.add-point-btn:hover:not(:disabled) {
  border-color: rgba(0,212,255,0.3);
  color: #00d4ff;
}

.add-point-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

/* ─── 目的地列表 ─── */
.destinations-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 10px;
}

.dest-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 10px;
  transition: all 0.2s;
}

.dest-card:hover {
  border-color: rgba(255,107,107,0.2);
  background: rgba(255,107,107,0.04);
}

.dest-number {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: linear-gradient(135deg, #ff6b6b, #ee5a24);
  color: #fff;
  font-size: 12px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.dest-info {
  flex: 1;
  min-width: 0;
}

.dest-info h4 {
  font-size: 13px;
  font-weight: 600;
  margin: 0 0 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.dest-info p {
  font-size: 11px;
  color: rgba(255,255,255,0.4);
  margin: 0;
}

.dest-remove {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: rgba(245,108,108,0.15);
  border: none;
  color: #f56c6c;
  font-size: 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.2s;
}

.dest-remove:hover {
  background: rgba(245,108,108,0.3);
}

.empty-hint {
  text-align: center;
  padding: 24px 12px;
  color: rgba(255,255,255,0.3);
  font-size: 13px;
}

.add-dest-btn {
  width: 100%;
  padding: 10px;
  background: transparent;
  border: 1px dashed rgba(255,107,107,0.25);
  border-radius: 10px;
  color: rgba(255,107,107,0.7);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.add-dest-btn:hover:not(:disabled) {
  border-color: rgba(255,107,107,0.5);
  background: rgba(255,107,107,0.05);
  color: #ff6b6b;
}

.add-dest-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

/* ─── 交通方式 ─── */
.transport-section {
  margin-bottom: 20px;
}

.transport-options {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.transport-chip {
  padding: 8px 14px;
  border-radius: 20px;
  border: 1px solid rgba(255,255,255,0.08);
  background: rgba(255,255,255,0.04);
  color: rgba(255,255,255,0.6);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.transport-chip:hover {
  background: rgba(255,255,255,0.08);
  border-color: rgba(255,255,255,0.15);
}

.transport-chip.active {
  background: linear-gradient(135deg, rgba(0,212,255,0.18), rgba(123,44,191,0.18));
  border-color: rgba(0,212,255,0.4);
  color: #00d4ff;
  font-weight: 600;
}

/* ─── 路线结果 ─── */
.route-result {
  margin-bottom: 20px;
}

.result-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.result-header h3 {
  font-size: 15px;
  font-weight: 600;
}

.algo-badge {
  font-size: 10px;
  padding: 3px 10px;
  border-radius: 10px;
  background: rgba(0,255,136,0.1);
  border: 1px solid rgba(0,255,136,0.2);
  color: #00ff88;
  font-family: monospace;
}

.info-card {
  display: flex;
  gap: 12px;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 12px;
  padding: 14px;
  margin-bottom: 14px;
}

.info-item {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.info-icon {
  font-size: 20px;
  flex-shrink: 0;
}

.info-content {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.info-label {
  font-size: 11px;
  color: rgba(255,255,255,0.45);
}

.info-value {
  font-size: 15px;
  font-weight: 600;
  color: #00d4ff;
  white-space: nowrap;
}

/* ─── 访问顺序 ─── */
.ordered-stops {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 10px;
  padding: 12px 14px;
}

.stops-label {
  font-size: 12px;
  color: rgba(255,255,255,0.5);
  display: block;
  margin-bottom: 8px;
}

.stops-flow {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 4px;
}

.stop-chip {
  font-size: 12px;
  padding: 4px 10px;
  border-radius: 14px;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.stop-chip.is-start {
  background: rgba(0,212,255,0.12);
  color: #00d4ff;
}

.stop-chip.is-dest {
  background: rgba(255,107,107,0.1);
  color: #ff6b6b;
}

.stop-chip.is-return {
  background: rgba(0,255,136,0.08);
  color: #00ff88;
}

.arrow {
  margin-left: 2px;
  opacity: 0.4;
}

/* ─── 规划按钮 ─── */
.action-bar {
  padding: 10px 0 30px;
  text-align: center;
}

.plan-btn {
  width: 100%;
  padding: 14px;
  border-radius: 25px;
  border: none;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  background: rgba(255,255,255,0.06);
  color: rgba(255,255,255,0.35);
}

.plan-btn.ready {
  background: linear-gradient(135deg, #00D4FF, #7b2cbf);
  color: #fff;
  box-shadow: 0 4px 20px rgba(0,212,255,0.25);
}

.plan-btn.ready:hover {
  box-shadow: 0 6px 28px rgba(0,212,255,0.4);
  transform: translateY(-1px);
}

.plan-btn:disabled {
  cursor: not-allowed;
}

.action-hint {
  font-size: 12px;
  color: rgba(255,255,255,0.3);
  margin-top: 8px;
}

/* ─── 搜索弹窗 ─── */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  background: #1a1a2e;
  padding: 24px;
  border-radius: 16px;
  width: 100%;
  max-width: 420px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
}

.modal-content h3 {
  margin: 0 0 16px;
  font-size: 17px;
}

.tech-input {
  width: 100%;
  padding: 12px 14px;
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 10px;
  color: #fff;
  font-size: 14px;
  outline: none;
  box-sizing: border-box;
}

.tech-input:focus {
  border-color: rgba(0,212,255,0.4);
}

.tech-input::placeholder {
  color: rgba(255,255,255,0.3);
}

.search-results {
  flex: 1;
  overflow-y: auto;
  margin-top: 12px;
  max-height: 300px;
}

.search-result-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 14px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.15s;
}

.search-result-item:hover:not(.disabled) {
  background: rgba(0,212,255,0.1);
}

.search-result-item.disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

.result-main {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.result-name {
  font-size: 14px;
  font-weight: 500;
}

.result-type {
  font-size: 11px;
  color: rgba(255,255,255,0.4);
}

.already-tag {
  font-size: 11px;
  padding: 2px 8px;
  background: rgba(255,255,255,0.1);
  border-radius: 8px;
  color: rgba(255,255,255,0.4);
}

.no-results {
  text-align: center;
  padding: 24px;
  color: rgba(255,255,255,0.3);
  font-size: 13px;
}

.close-modal {
  width: 100%;
  padding: 12px;
  margin-top: 14px;
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 10px;
  color: #fff;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;
}

.close-modal:hover {
  background: rgba(255,255,255,0.14);
}
</style>
