<template>
  <div class="internal-nav-page">
    <!-- 顶部 -->
    <header class="nav-header">
      <button class="back-btn" @click="router.back()">←</button>
      <div class="header-center">
        <h1 class="header-title">{{ mapData.spot?.name || '校园导航' }}</h1>
        <span class="header-sub">内部路网导航</span>
      </div>
      <div style="width:40px" />
    </header>

    <div class="page-body">
      <!-- 左侧控制面板 -->
      <aside class="control-panel">
        <!-- 起点 -->
        <div class="panel-section">
          <div class="section-label">选择起点</div>
          <input
            v-model="startSearchKeyword"
            class="search-input"
            placeholder="搜索入口、建筑或设施..."
          />
          <div class="candidate-list start-list">
            <div
              v-for="node in filteredStartNodes"
              :key="`start-${node.id}`"
              :class="['candidate-item', 'start-item', { selected: startNodeId === node.id }]"
              @click="selectStartNode(node.id)"
            >
              <span :class="['node-dot', node.type]"></span>
              <span class="candidate-name">{{ node.name }}</span>
              <span class="candidate-type-badge">{{ typeLabel(node.type) }}</span>
              <span v-if="startNodeId === node.id" class="check">✓</span>
            </div>
          </div>
        </div>

        <!-- 模式切换 -->
        <div class="panel-section">
          <div class="section-label">规划模式</div>
          <div class="mode-tabs">
            <button :class="['mode-tab', { active: routeMode === 'single' }]" @click="routeMode = 'single'">
              单目标
            </button>
            <button :class="['mode-tab', { active: routeMode === 'multi' }]" @click="routeMode = 'multi'">
              多目标游览
            </button>
          </div>
        </div>

        <!-- 交通方式 -->
        <div class="panel-section">
          <div class="section-label">交通方式</div>
          <div class="transport-tabs">
            <button
              v-for="m in availableModes"
              :key="m.value"
              :class="['transport-tab', { active: transportMode === m.value }]"
              @click="transportMode = m.value"
            >{{ m.label }}</button>
          </div>
        </div>

        <!-- 策略 -->
        <div class="panel-section">
          <div class="section-label">优化目标</div>
          <div class="transport-tabs">
            <button :class="['transport-tab', { active: strategy === 'shortest_time' }]" @click="strategy = 'shortest_time'">最短时间</button>
            <button :class="['transport-tab', { active: strategy === 'shortest_distance' }]" @click="strategy = 'shortest_distance'">最短距离</button>
          </div>
        </div>

        <!-- 目标搜索 -->
        <div class="panel-section">
          <div class="section-label">
            {{ routeMode === 'single' ? '选择目标' : '选择途经点（可多选）' }}
          </div>
          <input
            v-model="searchKeyword"
            class="search-input"
            placeholder="搜索建筑或设施..."
            @input="onSearch"
          />
          <div class="candidate-list">
            <div
              v-for="node in filteredNodes"
              :key="node.id"
              :class="['candidate-item', { selected: isSelected(node.id) }]"
              @click="toggleSelect(node)"
            >
              <span :class="['node-dot', node.type]"></span>
              <span class="candidate-name">{{ node.name }}</span>
              <span class="candidate-type-badge">{{ typeLabel(node.type) }}</span>
              <span v-if="isSelected(node.id)" class="check">✓</span>
            </div>
          </div>
        </div>

        <!-- 已选目标 -->
        <div class="panel-section" v-if="selectedTargets.length">
          <div class="section-label">已选目标（{{ selectedTargets.length }}）</div>
          <div class="selected-list">
            <div v-for="(t, idx) in selectedTargets" :key="t.id" class="selected-item">
              <span class="selected-idx">{{ idx + 1 }}</span>
              <span class="selected-name">{{ t.name }}</span>
              <button class="remove-btn" @click="removeTarget(t.id)">×</button>
            </div>
          </div>
        </div>

        <!-- 规划按钮 -->
        <button
          class="plan-btn"
          :disabled="selectedTargets.length === 0 || planning"
          @click="planRoute"
        >
          <span v-if="planning">规划中...</span>
          <span v-else>{{ routeMode === 'single' ? '开始导航' : '规划最优游览路线' }}</span>
        </button>

        <div v-if="loadError" class="status-card error-card">{{ loadError }}</div>
        <div v-else-if="routeError" class="status-card error-card">{{ routeError }}</div>
        <div v-else-if="emptyStateText" class="status-card empty-card">{{ emptyStateText }}</div>

        <!-- 结果信息 -->
        <div class="result-card" v-if="routeResult && !routeResult.error">
          <div class="result-row">
            <span class="result-icon">📏</span>
            <span>总距离 {{ (routeResult.distance / 1000).toFixed(2) }} km</span>
          </div>
          <div class="result-row">
            <span class="result-icon">⏱️</span>
            <span>预计 {{ formatDuration(routeResult.duration) }}</span>
          </div>
          <div class="result-row">
            <span class="result-icon">🔬</span>
            <span>{{ routeResult.algorithm }}  {{ routeResult.time_complexity }}</span>
          </div>
          <div v-if="routeMode === 'multi' && orderedNames.length" class="result-order">
            <div class="result-order-label">最优游览顺序：</div>
            <div class="order-chain">
              <span class="order-node start">{{ startNodeName }}</span>
              <span v-for="(name, i) in orderedNames" :key="i">
                <span class="order-arrow">›</span>
                <span class="order-node">{{ name }}</span>
              </span>
              <template v-if="routeResult.return_to_start">
                <span class="order-arrow">›</span>
                <span class="order-node start">{{ startNodeName }}</span>
              </template>
            </div>
          </div>
        </div>
      </aside>

      <!-- 右侧地图 -->
      <div class="map-area">
        <div id="internal-nav-map" class="amap-container"></div>
        <div v-if="loading" class="map-loading">
          <div class="loading-spinner"></div>
          <span>加载地图数据中...</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const AMAP_KEY = import.meta.env.VITE_AMAP_KEY || '3350803110b3a0e1d1f84585f7976cf4'
const AMAP_SECURITY_KEY = import.meta.env.VITE_AMAP_SECURITY_KEY || 'a7e5b0c229ff2ac54dd6fc4fc9fc489d'
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const spotId = computed(() => Number(route.query.id))

const mapData = ref({ spot: null, nodes: [], edges: [], buildings: [], facilities: [], entrance_node_id: null, available_modes: [] })
const loading = ref(true)
const planning = ref(false)
const loadError = ref('')
const routeError = ref('')
const routeMode = ref('single')
const transportMode = ref('walk')
const strategy = ref('shortest_time')
const startSearchKeyword = ref('')
const searchKeyword = ref('')
const startNodeId = ref(null)
const selectedTargets = ref([])   // [{id, name, node_id}]
const routeResult = ref(null)
const orderedNames = ref([])

// 地图相关
let map = null
let roadPolylines = []
let routePolyline = null
let markers = []
let routeMarkers = []

// 可导航节点（建筑+设施锚点，node_type 为 building/facility/entrance）
const anchorNodes = computed(() =>
  (mapData.value.nodes || []).filter(n => ['building', 'facility', 'entrance'].includes(n.type))
)

const startNodeName = computed(() => {
  const n = (mapData.value.nodes || []).find(n => n.id === startNodeId.value)
  return n?.name || '校园入口'
})

const TRANSPORT_MODES = [
  { value: 'walk', label: '步行' },
  { value: 'bike', label: '骑行' },
  { value: 'shuttle', label: '电瓶车' },
]
const availableModes = computed(() => {
  const avail = new Set(mapData.value.available_modes || ['walk'])
  const modes = TRANSPORT_MODES.filter(m => avail.has(m.value))
  return modes.length ? modes : [{ value: 'walk', label: '步行' }]
})

const filteredStartNodes = computed(() => {
  const kw = startSearchKeyword.value.trim().toLowerCase()
  const list = anchorNodes.value.filter(n => n.name)
  if (!kw) return list
  return list.filter(n => n.name.toLowerCase().includes(kw))
})

const filteredNodes = computed(() => {
  const kw = searchKeyword.value.trim().toLowerCase()
  const list = anchorNodes.value.filter(n => n.id !== startNodeId.value && n.name)
  if (!kw) return list
  return list.filter(n => n.name.toLowerCase().includes(kw))
})

const emptyStateText = computed(() => {
  if (loading.value) return ''
  if (!mapData.value.nodes.length) return '当前景点暂无内部路网数据。'
  if (!filteredNodes.value.length) return searchKeyword.value.trim() ? '没有匹配的建筑或设施。' : '暂无可导航目标。'
  return ''
})

const isSelected = (nodeId) => selectedTargets.value.some(t => t.id === nodeId)

const typeLabel = (type) => ({ building: '建筑', facility: '设施', entrance: '入口', crossing: '路口' }[type] || type)

function selectStartNode(nodeId) {
  if (startNodeId.value === nodeId) return
  startNodeId.value = nodeId
  selectedTargets.value = selectedTargets.value.filter(t => t.id !== nodeId)
}

function onSearch() { /* 响应式 computed 自动过滤 */ }

function toggleSelect(node) {
  if (routeMode.value === 'single') {
    selectedTargets.value = isSelected(node.id) ? [] : [{ id: node.id, name: node.name }]
  } else {
    if (isSelected(node.id)) {
      selectedTargets.value = selectedTargets.value.filter(t => t.id !== node.id)
    } else {
      selectedTargets.value.push({ id: node.id, name: node.name })
    }
  }
}

function removeTarget(nodeId) {
  selectedTargets.value = selectedTargets.value.filter(t => t.id !== nodeId)
  if (!selectedTargets.value.length) {
    routeResult.value = null
    routeError.value = ''
    orderedNames.value = []
    clearRouteLayer()
  }
}

watch(routeMode, () => {
  selectedTargets.value = []
  routeResult.value = null
  routeError.value = ''
  orderedNames.value = []
  clearRouteLayer()
})
watch([startNodeId, transportMode, strategy], async () => {
  routeResult.value = null
  routeError.value = ''
  orderedNames.value = []
  clearRouteLayer()
  if (selectedTargets.value.length) {
    await planRoute()
  }
})

function formatDuration(seconds) {
  if (seconds < 60) return `${seconds}秒`
  const m = Math.floor(seconds / 60)
  const s = seconds % 60
  return s > 0 ? `${m}分${s}秒` : `${m}分钟`
}

// ======== 数据加载 ========
async function loadMapData() {
  loading.value = true
  loadError.value = ''
  try {
    const res = await fetch(`${API_BASE}/api/route/internal-map/${spotId.value}`)
    if (!res.ok) {
      throw new Error(`接口返回 ${res.status}`)
    }
    const data = await res.json()
    if (data?.error) {
      throw new Error(data.error)
    }
    mapData.value = {
      spot: data.spot || null,
      nodes: data.nodes || [],
      edges: data.edges || [],
      buildings: data.buildings || [],
      facilities: data.facilities || [],
      entrance_node_id: data.entrance_node_id || null,
      available_modes: data.available_modes || [],
    }
    if (mapData.value.available_modes.length) {
      transportMode.value = mapData.value.available_modes.includes('walk') ? 'walk' : mapData.value.available_modes[0]
    }
    startNodeId.value = data.entrance_node_id || data.nodes?.[0]?.id || null
  } catch (e) {
    console.error('加载地图数据失败', e)
    loadError.value = e.message || '地图数据加载失败'
    mapData.value = { spot: null, nodes: [], edges: [], buildings: [], facilities: [], entrance_node_id: null, available_modes: ['walk'] }
  } finally {
    loading.value = false
  }
}

// ======== 路线规划 ========
async function planRoute() {
  if (!selectedTargets.value.length || !startNodeId.value) return
  planning.value = true
  routeResult.value = null
  routeError.value = ''
  orderedNames.value = []
  clearRouteLayer()

  try {
    let result
    if (routeMode.value === 'single') {
      const res = await fetch(`${API_BASE}/api/route/plan`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          spot_id: spotId.value,
          start_node_id: startNodeId.value,
          end_node_id: selectedTargets.value[0].id,
          strategy: strategy.value,
          transport_mode: transportMode.value,
        })
      })
      result = await res.json()
    } else {
      const res = await fetch(`${API_BASE}/api/route/plan-multi`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          spot_id: spotId.value,
          start_node_id: startNodeId.value,
          waypoint_ids: selectedTargets.value.map(t => t.id),
          return_to_start: true,
          strategy: strategy.value,
          transport_mode: transportMode.value,
        })
      })
      result = await res.json()
    }

    routeResult.value = result
    orderedNames.value = result.ordered_waypoint_names || []

    if (result.error) {
      routeError.value = result.error
      clearRouteLayer()
      return
    }

    drawRoute(result.path || [])
  } catch (e) {
    console.error('路线规划失败', e)
    routeError.value = e.message || '路线规划失败'
  } finally {
    planning.value = false
  }
}

// ======== 地图渲染 ========
async function initMap() {
  if (window._AMapSecurityConfig === undefined) {
    window._AMapSecurityConfig = { securityJsCode: AMAP_SECURITY_KEY }
  }
  await loadAMapScript()
  const AMap = window.AMap
  map = new AMap.Map('internal-nav-map', {
    zoom: 16,
    center: [mapData.value.spot?.location_lng || 116.327, mapData.value.spot?.location_lat || 40.003],
  })
  drawRoadNetwork()
  drawAnchors()
}

function loadAMapScript() {
  return new Promise((resolve) => {
    if (window.AMap) { resolve(); return }
    const s = document.createElement('script')
    s.src = `https://webapi.amap.com/maps?v=2.0&key=${AMAP_KEY}`
    s.onload = () => resolve()
    document.head.appendChild(s)
  })
}

function drawRoadNetwork() {
  if (!map || !mapData.value.nodes.length) return
  const AMap = window.AMap
  const nodeMap = Object.fromEntries(mapData.value.nodes.map(n => [n.id, n]))
  const drawn = new Set()

  for (const edge of mapData.value.edges) {
    const from = nodeMap[edge.from_node_id]
    const to = nodeMap[edge.to_node_id]
    if (!from || !to) continue
    const key = [Math.min(edge.from_node_id, edge.to_node_id), Math.max(edge.from_node_id, edge.to_node_id)].join('-')
    if (drawn.has(key)) continue
    drawn.add(key)
    const poly = new AMap.Polyline({
      path: [[from.lng, from.lat], [to.lng, to.lat]],
      strokeColor: 'rgba(0,180,220,0.25)',
      strokeWeight: 1.5,
      strokeOpacity: 0.6,
    })
    poly.setMap(map)
    roadPolylines.push(poly)
  }
}

function drawAnchors() {
  if (!map) return
  const AMap = window.AMap
  for (const node of anchorNodes.value) {
    const color = node.type === 'entrance' ? '#ff9f43' : node.type === 'building' ? '#00d4ff' : '#a29bfe'
    const marker = new AMap.CircleMarker({
      center: [node.lng, node.lat],
      radius: node.type === 'entrance' ? 7 : 5,
      fillColor: color,
      fillOpacity: 0.9,
      strokeColor: '#fff',
      strokeWeight: 1,
    })
    marker.setMap(map)

    const label = new AMap.Text({
      text: node.name,
      position: [node.lng, node.lat],
      offset: new AMap.Pixel(8, -8),
      style: {
        'background-color': 'rgba(255,255,255,0.9)',
        border: '1px solid rgba(0,0,0,0.08)',
        'border-radius': '6px',
        color: node.type === 'entrance' ? '#ff9f43' : '#1f2937',
        'font-size': '11px',
        'white-space': 'nowrap',
        padding: '2px 6px',
      },
    })
    label.setMap(map)
    markers.push(marker, label)
  }
}

function drawRoute(path) {
  if (!map || !path.length) return
  const AMap = window.AMap
  clearRouteLayer()
  const coords = path.map(p => [p.lng, p.lat])
  routePolyline = new AMap.Polyline({
    path: coords,
    strokeColor: '#00ff88',
    strokeWeight: 4,
    strokeOpacity: 0.95,
    showDir: true,
  })
  routePolyline.setMap(map)

  const addFlag = (pt, label, color) => {
    const m = new AMap.Marker({
      position: [pt.lng, pt.lat],
      content: `<div style="background:${color};color:#000;padding:3px 8px;border-radius:10px;font-size:12px;font-weight:600;white-space:nowrap">${label}</div>`,
      offset: new AMap.Pixel(-20, -16),
    })
    m.setMap(map)
    routeMarkers.push(m)
  }

  addFlag(path[0], `出发 · ${startNodeName.value}`, '#ff9f43')
  if (routeResult.value?.return_to_start) {
    addFlag(path[path.length - 1], `返回 · ${startNodeName.value}`, '#00ff88')
  } else {
    addFlag(path[path.length - 1], '到达', '#00ff88')
  }

  map.setFitView([routePolyline])
}

function clearRouteLayer() {
  if (routePolyline) { routePolyline.setMap(null); routePolyline = null }
  routeMarkers.forEach(m => m.setMap(null))
  routeMarkers = []
}

// ======== 生命周期 ========
onMounted(async () => {
  await loadMapData()
  await nextTick()
  await initMap()
})

onBeforeUnmount(() => {
  roadPolylines.forEach(p => p.setMap(null))
  markers.forEach(m => m.setMap(null))
  if (routePolyline) routePolyline.setMap(null)
  if (map) map.destroy()
})
</script>

<style scoped>
.internal-nav-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f5f7fb;
  color: #111827;
  overflow: hidden;
}

.nav-header {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  background: rgba(255,255,255,0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(15,23,42,0.08);
  gap: 12px;
  flex-shrink: 0;
}

.back-btn {
  width: 40px; height: 40px;
  border-radius: 50%;
  border: 1px solid rgba(15,23,42,0.12);
  background: #fff;
  color: #111827;
  font-size: 18px;
  cursor: pointer;
  flex-shrink: 0;
}

.header-center { flex: 1; text-align: center; }
.header-title { font-size: 17px; font-weight: 600; margin: 0; }
.header-sub { font-size: 11px; color: #2563eb; }

.page-body {
  display: flex;
  flex: 1;
  overflow: hidden;
}

/* 控制面板 */
.control-panel {
  width: 320px;
  flex-shrink: 0;
  overflow-y: auto;
  padding: 14px 14px 100px;
  border-right: 1px solid rgba(15,23,42,0.08);
  background: rgba(255,255,255,0.96);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.panel-section { display: flex; flex-direction: column; gap: 8px; }
.section-label { font-size: 11px; color: rgba(17,24,39,0.55); text-transform: uppercase; letter-spacing: 0.05em; }

.start-list {
  max-height: 160px;
}

.start-item.selected {
  background: rgba(255,159,67,0.12);
  border-color: rgba(255,159,67,0.45);
}

.start-node-card {
  display: flex; align-items: center; gap: 8px;
  padding: 10px 12px;
  background: rgba(255,159,67,0.08);
  border: 1px solid rgba(255,159,67,0.25);
  border-radius: 10px;
  font-size: 14px;
}

.node-dot {
  width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0;
}
.node-dot.entrance { background: #ff9f43; }
.node-dot.building { background: #00d4ff; }
.node-dot.facility { background: #a29bfe; }
.node-dot.crossing  { background: rgba(255,255,255,0.3); }

.mode-tabs, .transport-tabs {
  display: flex; gap: 6px;
}

.mode-tab, .transport-tab {
  flex: 1;
  padding: 8px 0;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 8px;
  color: rgba(255,255,255,0.6);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.mode-tab.active, .transport-tab.active {
  background: rgba(0,212,255,0.15);
  border-color: #00d4ff;
  color: #00d4ff;
}

.search-input {
  width: 100%;
  padding: 9px 12px;
  background: #fff;
  border: 1px solid rgba(37,99,235,0.18);
  border-radius: 8px;
  color: #111827;
  font-size: 13px;
  box-sizing: border-box;
}
.search-input::placeholder { color: rgba(17,24,39,0.35); }

.candidate-list {
  display: flex; flex-direction: column; gap: 4px;
  max-height: 220px; overflow-y: auto;
}

.candidate-item {
  display: flex; align-items: center; gap: 8px;
  padding: 8px 10px;
  background: #fff;
  border: 1px solid rgba(15,23,42,0.08);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.18s;
  font-size: 13px;
}
.candidate-item:hover { background: rgba(37,99,235,0.04); border-color: rgba(37,99,235,0.22); }
.candidate-item.selected { background: rgba(37,99,235,0.08); border-color: rgba(37,99,235,0.35); }

.candidate-name { flex: 1; }
.candidate-type-badge {
  font-size: 11px;
  color: rgba(17,24,39,0.45);
  background: rgba(15,23,42,0.04);
  padding: 1px 6px; border-radius: 6px;
}
.check { color: #2563eb; font-weight: 700; }

.selected-list { display: flex; flex-direction: column; gap: 4px; }
.selected-item {
  display: flex; align-items: center; gap: 8px;
  padding: 7px 10px;
  background: rgba(37,99,235,0.07);
  border-radius: 8px;
  font-size: 13px;
}
.selected-idx {
  width: 20px; height: 20px; border-radius: 50%;
  background: #2563eb; color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-size: 11px; font-weight: 700; flex-shrink: 0;
}
.selected-name { flex: 1; }
.remove-btn {
  background: none; border: none; color: rgba(17,24,39,0.4);
  font-size: 16px; cursor: pointer; padding: 0 2px;
}
.remove-btn:hover { color: #ff6b6b; }

.plan-btn {
  padding: 13px;
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  border: none; border-radius: 12px;
  color: #fff; font-size: 15px; font-weight: 600;
  cursor: pointer; transition: opacity 0.2s;
}
.plan-btn:disabled { opacity: 0.4; cursor: not-allowed; }

.result-card {
  padding: 14px;
  background: rgba(16,185,129,0.06);
  border: 1px solid rgba(16,185,129,0.18);
  border-radius: 12px;
  display: flex; flex-direction: column; gap: 8px;
}
.result-row { display: flex; align-items: center; gap: 8px; font-size: 14px; }
.result-icon { font-size: 16px; }

.result-order { margin-top: 6px; }
.result-order-label { font-size: 12px; color: rgba(17,24,39,0.5); margin-bottom: 6px; }
.order-chain { display: flex; flex-wrap: wrap; align-items: center; gap: 4px; }
.order-node {
  padding: 3px 8px; background: rgba(37,99,235,0.08);
  border-radius: 8px; font-size: 12px; color: #2563eb;
}
.order-node.start { background: rgba(255,159,67,0.14); color: #d97706; }
.order-arrow { color: rgba(17,24,39,0.3); font-size: 14px; }

/* 地图 */
.map-area {
  flex: 1; position: relative;
}
.amap-container { width: 100%; height: 100%; }
.map-loading {
  position: absolute; inset: 0;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 12px; background: rgba(255,255,255,0.88);
  font-size: 14px; color: rgba(17,24,39,0.7);
}
.loading-spinner {
  width: 36px; height: 36px;
  border: 3px solid rgba(0,212,255,0.2);
  border-top-color: #00d4ff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.status-card {
  padding: 12px 14px;
  border-radius: 12px;
  font-size: 13px;
  line-height: 1.5;
}

.error-card {
  background: rgba(255, 107, 107, 0.08);
  border: 1px solid rgba(255, 107, 107, 0.22);
  color: #ffb3b3;
}

.empty-card {
  background: rgba(15,23,42,0.03);
  border: 1px solid rgba(15,23,42,0.08);
  color: rgba(17,24,39,0.6);
}
</style>
