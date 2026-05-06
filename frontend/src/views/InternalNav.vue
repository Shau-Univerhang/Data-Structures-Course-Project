<template>
  <div class="internal-nav-page">
    <header class="nav-header">
      <button class="back-btn" @click="router.back()">←</button>
      <div class="header-center">
        <h1 class="header-title">{{ mapData.spot?.name || '内部导航' }}</h1>
        <span class="header-sub">路线规划 · 场所查询 · 室内导航</span>
      </div>
      <div class="header-badge">{{ mapData.spot?.type === 'campus' ? '校园' : '景区' }}</div>
    </header>

    <div class="page-body">
      <aside class="control-panel">
        <section class="panel-card search-card">
          <div class="section-heading">场所搜索</div>
          <input
            v-model="nodeSearchKeyword"
            class="search-input"
            placeholder="搜索入口、建筑或设施..."
          />
          <div class="candidate-list compact">
            <button
              v-for="node in filteredAnchorNodes"
              :key="node.id"
              class="candidate-item"
              :class="{ active: selectedMapNode?.id === node.id }"
              @click="focusNode(node)"
            >
              <span :class="['node-dot', node.type]"></span>
              <span class="candidate-name">{{ node.name }}</span>
              <span class="candidate-type-badge">{{ typeLabel(node.type) }}</span>
            </button>
          </div>
        </section>

        <section class="panel-card quick-card">
          <div class="section-heading">当前选择</div>
          <div v-if="selectedMapNode" class="selected-node-card">
            <div class="selected-node-title-row">
              <div>
                <div class="selected-node-title">{{ selectedMapNode.name }}</div>
                <div class="selected-node-meta">{{ typeLabel(selectedMapNode.type) }}</div>
              </div>
              <button class="mini-btn ghost" @click="selectedMapNode = null">关闭</button>
            </div>
            <div class="action-grid">
              <button class="mini-btn" @click="setAsStart(selectedMapNode)">设为起点</button>
              <button class="mini-btn" @click="setAsEnd(selectedMapNode)">设为终点</button>
              <button class="mini-btn" @click="addAsWaypoint(selectedMapNode)">加入途经点</button>
              <button class="mini-btn" @click="openNearbyForNode(selectedMapNode)">查看附近</button>
              <button
                class="mini-btn"
                :disabled="!canOpenIndoorFromNode(selectedMapNode)"
                @click="openIndoorForNode(selectedMapNode)"
              >
                室内导航
              </button>
            </div>
          </div>
          <div v-else class="hint-card">点击左侧搜索结果或地图节点，可以设为起点、加入路线或查看附近设施。</div>
        </section>

        <section class="panel-card tabs-card">
          <div class="top-tabs">
            <button :class="['top-tab', { active: activePanel === 'route' }]" @click="activePanel = 'route'">路线规划</button>
            <button :class="['top-tab', { active: activePanel === 'nearby' }]" @click="activePanel = 'nearby'">场所查询</button>
            <button :class="['top-tab', { active: activePanel === 'indoor' }]" @click="activePanel = 'indoor'">室内导航</button>
          </div>
        </section>

        <template v-if="activePanel === 'route'">
          <section class="panel-card">
            <div class="section-heading">路线设置</div>
            <div class="route-slot-card start">
              <div class="route-slot-label">起点</div>
              <div class="route-slot-name">{{ startNodeName }}</div>
              <div class="route-slot-hint">在左侧搜索结果或地图点位中选择地点后，点击“设为起点”。</div>
            </div>
            <div class="route-slot-card end top-gap">
              <div class="route-slot-label">终点</div>
              <div class="route-slot-name">{{ endNodeName }}</div>
              <div class="route-slot-hint">选择最终到达地点，路径会按起点 → 途经点 → 终点规划。</div>
            </div>
          </section>

          <section class="panel-card">
            <div class="section-heading">交通方式</div>
            <div class="transport-tabs transport-tabs-icons">
              <button
                v-for="mode in plannerModes"
                :key="mode.value"
                :class="['transport-tab', 'transport-tab-icon', { active: transportMode === mode.value }]"
                @click="transportMode = mode.value"
              >
                <span class="transport-icon">{{ transportIcon(mode.value) }}</span>
                <span>{{ mode.label }}</span>
              </button>
            </div>
            <div class="transport-tabs small-gap top-gap">
              <button :class="['transport-tab secondary', { active: strategy === 'shortest_time' }]" @click="strategy = 'shortest_time'">最短时间</button>
              <button :class="['transport-tab secondary', { active: strategy === 'shortest_distance' }]" @click="strategy = 'shortest_distance'">最短距离</button>
            </div>
          </section>

          <section class="panel-card">
            <div class="section-heading">途经点</div>
            <div v-if="waypointNodes.length" class="selected-list">
              <div v-for="(target, index) in waypointNodes" :key="target.id" class="selected-item">
                <span class="selected-idx">{{ index + 1 }}</span>
                <span class="selected-name">{{ target.name }}</span>
                <button class="remove-btn" @click="removeWaypoint(target.id)">×</button>
              </div>
            </div>
            <div v-else class="hint-card">可添加多个途经点，系统会自动规划经过它们后到达终点。</div>

            <div class="route-action-row">
              <button class="plan-btn" :disabled="!canPlanRoute" @click="planRoute">
                {{ planning ? '规划中...' : '开始规划路线' }}
              </button>
              <button class="mini-btn secondary-action" :disabled="!canSwapRoute" @click="swapRouteEndpoints">交换起终点</button>
              <button class="mini-btn secondary-action" :disabled="!hasRouteSelection" @click="clearRouteSelections">清空路线</button>
            </div>
          </section>

          <section v-if="routeResult && !routeResult.error" class="panel-card result-card">
            <div class="section-heading">路线结果</div>
            <div class="result-grid">
              <div class="metric-card">
                <span class="metric-label">总距离</span>
                <strong>{{ (routeResult.distance / 1000).toFixed(2) }} km</strong>
              </div>
              <div class="metric-card">
                <span class="metric-label">预计时间</span>
                <strong>{{ formatDuration(routeResult.duration) }}</strong>
              </div>
            </div>
            <div class="summary-row"><span>策略</span><strong>{{ transportModeLabel(transportMode) }} / {{ strategyLabel }}</strong></div>
            <div class="summary-row"><span>终点</span><strong>{{ endNodeName }}</strong></div>

            <div v-if="transportSegments.length" class="chips-wrap">
              <span class="chip-label">分段交通</span>
              <span v-for="segment in transportSegments" :key="segment.key" class="mode-chip">{{ segment.icon }} {{ segment.label }} × {{ segment.count }}</span>
            </div>

            <div v-if="orderedNames.length" class="order-box">
              <div class="order-title">推荐顺序</div>
              <div class="order-chain">
                <span class="order-node start">{{ startNodeName }}</span>
                <template v-for="(name, index) in orderedNames" :key="`${name}-${index}`">
                  <span class="order-arrow">→</span>
                  <span :class="['order-node', { end: index === orderedNames.length - 1 }]">{{ name }}</span>
                </template>
              </div>
            </div>
          </section>
        </template>

        <template v-else-if="activePanel === 'nearby'">
          <section class="panel-card">
            <div class="section-heading">查询中心</div>
            <div class="summary-row"><span>当前中心点</span><strong>{{ nearbyOriginName }}</strong></div>
            <div class="hint-card small">先选中某个地点，再点“查看附近”，或直接使用当前起点。</div>
            <div class="transport-tabs transport-tabs-icons">
              <button
                v-for="mode in plannerModes"
                :key="`nearby-${mode.value}`"
                :class="['transport-tab', 'transport-tab-icon', { active: transportMode === mode.value }]"
                @click="transportMode = mode.value"
              >
                <span class="transport-icon">{{ transportIcon(mode.value) }}</span>
                <span>{{ mode.label }}</span>
              </button>
            </div>
          </section>

          <section class="panel-card">
            <div class="section-heading">类别筛选</div>
            <div class="chips-wrap">
              <button :class="['filter-chip', { active: nearbyCategory === 'all' }]" @click="nearbyCategory = 'all'">全部</button>
              <button
                v-for="category in facilityCategories"
                :key="category"
                :class="['filter-chip', { active: nearbyCategory === category }]"
                @click="nearbyCategory = category"
              >
                {{ facilityLabel(category) }}
              </button>
            </div>
            <div class="transport-tabs small-gap top-gap">
              <button :class="['transport-tab secondary', { active: nearbyStrategy === 'shortest_time' }]" @click="nearbyStrategy = 'shortest_time'">按时间排序</button>
              <button :class="['transport-tab secondary', { active: nearbyStrategy === 'shortest_distance' }]" @click="nearbyStrategy = 'shortest_distance'">按距离排序</button>
            </div>
            <input
              v-model="nearbyKeyword"
              class="search-input"
              placeholder="输入类别或设施名称，如 卫生间 / 超市"
            />
            <button class="plan-btn secondary-btn" :disabled="nearbyLoading || !nearbyOriginNodeId" @click="fetchNearbyFacilities">
              {{ nearbyLoading ? '查询中...' : '查询附近设施' }}
            </button>
          </section>

          <section class="panel-card">
            <div class="section-heading">查询结果</div>
            <div v-if="nearbyResults.length" class="selected-list results-list">
              <div
                v-for="item in nearbyResults"
                :key="item.node_id"
                class="nearby-item"
                :class="{ active: activeNearbyNodeId === item.node_id }"
              >
                <button class="nearby-preview" @click="previewNearbyResult(item)">
                  <div class="nearby-main-row">
                    <strong>{{ item.name }}</strong>
                    <span class="candidate-type-badge">{{ facilityLabel(item.type) }}</span>
                  </div>
                  <div class="nearby-meta-row">
                    <span>{{ (item.distance / 1000).toFixed(2) }} km</span>
                    <span>{{ formatDuration(item.duration) }}</span>
                  </div>
                  <div class="nearby-path-row">
                    <span>{{ item.transport_label }}</span>
                    <span v-if="item.segment_transport_modes?.length">{{ item.segment_transport_modes.map(mode => transportIcon(mode)).join(' ') }}</span>
                  </div>
                  <div v-if="item.description" class="nearby-desc">{{ item.description }}</div>
                </button>
                <div class="nearby-actions-row">
                  <button class="mini-btn" @click="previewNearbyResult(item)">预览路径</button>
                  <button class="mini-btn" @click="addNearbyAsWaypoint(item)">加入途经点</button>
                  <button class="mini-btn primary-action" @click="navigateToNearby(item)">导航去这里</button>
                </div>
              </div>
            </div>
            <div v-else class="hint-card">查询后会按图距离排序展示超市、卫生间、食堂、医务室等设施。</div>
          </section>
        </template>

        <template v-else>
          <section class="panel-card">
            <div class="section-heading">室内导航样例</div>
            <div v-if="indoorNavigation">
              <div class="summary-row"><span>楼宇</span><strong>{{ indoorBuilding?.name || indoorNavigation.default_building_name }}</strong></div>
              <div class="chips-wrap">
                <button
                  v-for="scene in indoorScenes"
                  :key="scene.id"
                  :class="['filter-chip', { active: indoorSceneId === scene.id }]"
                  @click="indoorSceneId = scene.id"
                >
                  {{ scene.label }}
                </button>
              </div>
              <div class="chips-wrap floor-tabs">
                <button
                  v-for="floor in indoorFloors"
                  :key="floor.id"
                  :class="['filter-chip', { active: indoorFloorId === floor.id }]"
                  @click="indoorFloorId = floor.id"
                >
                  {{ floor.label }}
                </button>
              </div>
              <div v-if="activeIndoorScene" class="hint-card small">
                {{ activeIndoorScene.description }}
              </div>
              <div class="indoor-canvas">
                <svg viewBox="0 0 100 100" preserveAspectRatio="none">
                  <line
                    v-for="(edge, index) in indoorEdges"
                    :key="`edge-${index}`"
                    :x1="indoorNodeMap[edge[0]]?.x || 0"
                    :y1="indoorNodeMap[edge[0]]?.y || 0"
                    :x2="indoorNodeMap[edge[1]]?.x || 0"
                    :y2="indoorNodeMap[edge[1]]?.y || 0"
                    class="indoor-edge"
                  />
                  <line
                    v-for="(segment, index) in indoorHighlightedSegments"
                    :key="`highlight-${index}`"
                    :x1="segment.from.x"
                    :y1="segment.from.y"
                    :x2="segment.to.x"
                    :y2="segment.to.y"
                    class="indoor-edge active"
                  />
                  <g v-for="node in indoorFloorNodes" :key="node.id">
                    <circle :cx="node.x" :cy="node.y" :r="nodeRadius(node.kind)" :class="['indoor-node', node.kind, { active: indoorPathNodeIds.includes(node.id) }]" />
                    <text :x="node.x" :y="node.y - 6" class="indoor-label">{{ node.label }}</text>
                  </g>
                </svg>
              </div>
              <div v-if="indoorActiveStep" class="summary-row top-gap"><span>当前楼层路径</span><strong>{{ indoorPathSummary }}</strong></div>
            </div>
            <div v-else class="hint-card">当前景点暂无室内导航样例数据。</div>
          </section>
        </template>

        <section v-if="loadError || routeError || nearbyError || emptyStateText" class="status-stack">
          <div v-if="loadError" class="status-card error-card">{{ loadError }}</div>
          <div v-else-if="routeError" class="status-card error-card">{{ routeError }}</div>
          <div v-else-if="nearbyError" class="status-card error-card">{{ nearbyError }}</div>
          <div v-else-if="emptyStateText" class="status-card empty-card">{{ emptyStateText }}</div>
        </section>
      </aside>

      <div class="map-area">
        <div id="internal-nav-map" class="amap-container"></div>
        <div v-if="loading" class="map-loading">
          <div class="loading-spinner"></div>
          <span>加载地图数据中...</span>
        </div>

        <div v-if="selectedMapNode" class="map-floating-card">
          <div class="floating-title">{{ selectedMapNode.name }}</div>
          <div class="floating-sub">{{ typeLabel(selectedMapNode.type) }}</div>
          <div class="floating-actions">
            <button class="mini-btn" @click="setAsStart(selectedMapNode)">设为起点</button>
            <button class="mini-btn" @click="setAsEnd(selectedMapNode)">设为终点</button>
            <button class="mini-btn" @click="addAsWaypoint(selectedMapNode)">途经点</button>
            <button class="mini-btn" @click="openNearbyForNode(selectedMapNode)">附近设施</button>
            <button
              class="mini-btn"
              :disabled="!canOpenIndoorFromNode(selectedMapNode)"
              @click="openIndoorForNode(selectedMapNode)"
            >
              室内导航
            </button>
          </div>
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

const mapData = ref({
  spot: null,
  nodes: [],
  edges: [],
  buildings: [],
  facilities: [],
  entrance_node_id: null,
  available_modes: [],
  display_modes: [],
  facility_categories: [],
  indoor_navigation: null,
})

const loading = ref(true)
const planning = ref(false)
const loadError = ref('')
const routeError = ref('')
const nearbyError = ref('')

const activePanel = ref('route')
const transportMode = ref('walk')
const strategy = ref('shortest_time')

const nodeSearchKeyword = ref('')
const startNodeId = ref(null)
const endNodeId = ref(null)
const waypointIds = ref([])
const routeResult = ref(null)
const orderedNames = ref([])
const selectedMapNode = ref(null)

const nearbyCategory = ref('all')
const nearbyKeyword = ref('')
const nearbyStrategy = ref('shortest_time')
const nearbyResults = ref([])
const nearbyLoading = ref(false)
const nearbyOriginNodeId = ref(null)
const activeNearbyNodeId = ref(null)

const indoorSceneId = ref('')
const indoorFloorId = ref('')

let map = null
let roadPolylines = []
let anchorMarkers = []
let activePolyline = null
let activeMarkers = []

const anchorNodes = computed(() => (mapData.value.nodes || []).filter(node => ['building', 'facility', 'entrance'].includes(node.type)))
const nodeMap = computed(() => Object.fromEntries((mapData.value.nodes || []).map(node => [node.id, node])))
const filteredAnchorNodes = computed(() => {
  const keyword = nodeSearchKeyword.value.trim().toLowerCase()
  const list = anchorNodes.value.filter(node => node.name)
  if (!keyword) return list
  return list.filter(node => node.name.toLowerCase().includes(keyword))
})

const startNodeName = computed(() => nodeMap.value[startNodeId.value]?.name || '未选择')
const endNodeName = computed(() => nodeMap.value[endNodeId.value]?.name || '未选择')
const waypointNodes = computed(() => waypointIds.value.map(id => nodeMap.value[id]).filter(Boolean))
const plannerModes = computed(() => displayModes.value.filter(mode => ['walk', 'bike'].includes(mode.value)))
const displayModes = computed(() => {
  const modes = mapData.value.display_modes || []
  return modes.length ? modes : [{ value: 'walk', label: '步行' }]
})
const canPlanRoute = computed(() => Boolean(startNodeId.value && endNodeId.value))
const canSwapRoute = computed(() => Boolean(startNodeId.value && endNodeId.value))
const hasRouteSelection = computed(() => Boolean(startNodeId.value || endNodeId.value || waypointIds.value.length || routeResult.value))
const strategyLabel = computed(() => strategy.value === 'shortest_time' ? '最短时间' : '最短距离')
const facilityCategories = computed(() => mapData.value.facility_categories || [])
const emptyStateText = computed(() => {
  if (loading.value) return ''
  if (!mapData.value.nodes.length) return '当前景点暂无内部路网数据。'
  if (nodeSearchKeyword.value.trim() && !filteredAnchorNodes.value.length) return '没有匹配的建筑或设施。'
  return ''
})
const nearbyOriginName = computed(() => nodeMap.value[nearbyOriginNodeId.value]?.name || startNodeName.value)
const indoorNavigation = computed(() => mapData.value.indoor_navigation || null)
const indoorBuilding = computed(() => indoorNavigation.value?.buildings?.[0] || null)
const indoorScenes = computed(() => indoorBuilding.value?.scenes || [])
const indoorFloors = computed(() => indoorBuilding.value?.floors || [])
const activeIndoorScene = computed(() => indoorScenes.value.find(scene => scene.id === indoorSceneId.value) || indoorScenes.value[0] || null)
const activeIndoorFloor = computed(() => indoorFloors.value.find(floor => floor.id === indoorFloorId.value) || indoorFloors.value[0] || null)
const indoorNodeMap = computed(() => Object.fromEntries((activeIndoorFloor.value?.nodes || []).map(node => [node.id, node])))
const indoorFloorNodes = computed(() => activeIndoorFloor.value?.nodes || [])
const indoorEdges = computed(() => activeIndoorFloor.value?.edges || [])
const indoorActiveStep = computed(() => activeIndoorScene.value?.steps?.find(step => step.floor_id === indoorFloorId.value) || null)
const indoorPathNodeIds = computed(() => indoorActiveStep.value?.path || [])
const indoorHighlightedSegments = computed(() => {
  const ids = indoorPathNodeIds.value
  const nodes = indoorNodeMap.value
  return ids.slice(0, -1).map((id, index) => ({ from: nodes[id], to: nodes[ids[index + 1]] })).filter(segment => segment.from && segment.to)
})
const indoorPathSummary = computed(() => indoorPathNodeIds.value.map(id => indoorNodeMap.value[id]?.label).filter(Boolean).join(' → '))
const transportSegments = computed(() => {
  const modes = routeResult.value?.segment_transport_modes || []
  const summary = []
  const counts = new Map()
  modes.forEach(mode => counts.set(mode, (counts.get(mode) || 0) + 1))
  counts.forEach((count, mode) => summary.push({ key: mode, label: transportModeLabel(mode), icon: transportIcon(mode), count }))
  return summary
})

function typeLabel(type) {
  return ({ building: '建筑', facility: '设施', entrance: '入口', crossing: '路口' }[type] || type)
}

function mapPoint(lng, lat) {
  return [lng, lat]
}

function projectNode(node) {
  return [node.lng, node.lat]
}

function projectPath(path) {
  return path.map(point => [point.lng, point.lat])
}

function facilityLabel(type) {
  return ({ canteen: '食堂', supermarket: '超市', toilet: '卫生间', clinic: '医务室', cafe: '咖啡', parking: '停放点', shop: '商店', restaurant: '餐厅', express: '快递', print: '打印', bank: 'ATM', sports: '运动场' }[type] || type || '设施')
}

function transportModeLabel(mode) {
  return ({ walk: '步行', bike: '骑行', shuttle: '电瓶车', smart: '智能混合', smart_campus: '智能混合', smart_scenic: '智能混合' }[mode] || mode)
}

function transportIcon(mode) {
  return ({ walk: '🚶', bike: '🚴', shuttle: '🛺', smart: '🧭', smart_campus: '🧭', smart_scenic: '🧭' }[mode] || '📍')
}

function nodeRadius(kind) {
  return ({ entrance: 4, elevator: 4, stairs: 4, room: 3.5, corridor: 3, hall: 3, service: 3 }[kind] || 3)
}

function isSelected(nodeId) {
  return waypointIds.value.includes(nodeId) || endNodeId.value === nodeId
}

function focusNode(node) {
  selectedMapNode.value = node
  if (map) {
    map.setCenter(mapPoint(node.lng, node.lat))
    map.setZoom(17)
  }
}

function setAsStart(node) {
  if (!node) return
  startNodeId.value = node.id
  nearbyOriginNodeId.value = node.id
  routeError.value = ''
  nearbyError.value = ''
  routeResult.value = null
  orderedNames.value = []
  if (endNodeId.value === node.id) endNodeId.value = null
  waypointIds.value = waypointIds.value.filter(id => id !== node.id)
  selectedMapNode.value = node
}

function setAsEnd(node) {
  if (!node) return
  endNodeId.value = node.id
  activePanel.value = 'route'
  routeError.value = ''
  nearbyError.value = ''
  routeResult.value = null
  orderedNames.value = []
  if (startNodeId.value === node.id) startNodeId.value = null
  waypointIds.value = waypointIds.value.filter(id => id !== node.id)
  selectedMapNode.value = node
}

function addAsWaypoint(node) {
  if (!node) return
  if (node.id === startNodeId.value || node.id === endNodeId.value) return
  activePanel.value = 'route'
  routeError.value = ''
  nearbyError.value = ''
  routeResult.value = null
  orderedNames.value = []
  if (!waypointIds.value.includes(node.id)) {
    waypointIds.value.push(node.id)
  }
  selectedMapNode.value = node
}

function removeWaypoint(nodeId) {
  waypointIds.value = waypointIds.value.filter(id => id !== nodeId)
  routeResult.value = null
  routeError.value = ''
  orderedNames.value = []
  clearActivePath()
}

function resetRouteArtifacts() {
  routeResult.value = null
  routeError.value = ''
  orderedNames.value = []
  clearActivePath()
}

function clearRouteSelections() {
  endNodeId.value = null
  waypointIds.value = []
  activeNearbyNodeId.value = null
  nearbyResults.value = []
  selectedMapNode.value = startNodeId.value ? nodeMap.value[startNodeId.value] || null : null
  resetRouteArtifacts()
}

function swapRouteEndpoints() {
  if (!canSwapRoute.value) return
  const originalStart = startNodeId.value
  startNodeId.value = endNodeId.value
  endNodeId.value = originalStart
  nearbyOriginNodeId.value = startNodeId.value
  selectedMapNode.value = nodeMap.value[startNodeId.value] || null
  resetRouteArtifacts()
}

function canOpenIndoorFromNode(node) {
  return Boolean(indoorNavigation.value && node && node.type === 'building')
}

function openIndoorForNode(node) {
  if (!canOpenIndoorFromNode(node)) return
  selectedMapNode.value = node
  activePanel.value = 'indoor'
}

function openNearbyForNode(node) {
  if (!node) return
  nearbyOriginNodeId.value = node.id
  activeNearbyNodeId.value = null
  nearbyResults.value = []
  nearbyError.value = ''
  activePanel.value = 'nearby'
  fetchNearbyFacilities()
}

function navigateToNearby(item) {
  if (!item) return
  const targetNode = nodeMap.value[item.node_id]
  if (!targetNode) return
  activePanel.value = 'route'
  activeNearbyNodeId.value = item.node_id
  nearbyError.value = ''
  setAsEnd(targetNode)
}

function addNearbyAsWaypoint(item) {
  if (!item) return
  const targetNode = nodeMap.value[item.node_id]
  if (!targetNode) return
  activePanel.value = 'route'
  activeNearbyNodeId.value = item.node_id
  nearbyError.value = ''
  addAsWaypoint(targetNode)
}

function formatDuration(seconds) {
  if (!seconds) return '0秒'
  if (seconds < 60) return `${seconds}秒`
  const minutes = Math.floor(seconds / 60)
  const remain = seconds % 60
  return remain > 0 ? `${minutes}分${remain}秒` : `${minutes}分钟`
}

async function loadMapData() {
  loading.value = true
  loadError.value = ''
  try {
    const res = await fetch(`${API_BASE}/api/route/internal-map/${spotId.value}`)
    if (!res.ok) throw new Error(`接口返回 ${res.status}`)
    const data = await res.json()
    if (data?.error) throw new Error(data.error)

    mapData.value = {
      spot: data.spot || null,
      nodes: data.nodes || [],
      edges: data.edges || [],
      buildings: data.buildings || [],
      facilities: data.facilities || [],
      entrance_node_id: data.entrance_node_id || null,
      available_modes: data.available_modes || [],
      display_modes: data.display_modes || [],
      facility_categories: data.facility_categories || [],
      indoor_navigation: data.indoor_navigation || null,
    }

    transportMode.value = plannerModes.value.some(mode => mode.value === transportMode.value)
    ? transportMode.value
    : (plannerModes.value[0]?.value || 'walk')
    startNodeId.value = data.entrance_node_id || data.nodes?.[0]?.id || null
    endNodeId.value = null
    waypointIds.value = []
    nearbyOriginNodeId.value = startNodeId.value

    const defaultScene = data.indoor_navigation?.buildings?.[0]?.scenes?.[0]
    const defaultFloor = data.indoor_navigation?.buildings?.[0]?.default_floor_id || data.indoor_navigation?.buildings?.[0]?.floors?.[0]?.id
    indoorSceneId.value = defaultScene?.id || ''
    indoorFloorId.value = defaultFloor || ''
  } catch (error) {
    loadError.value = error.message || '地图数据加载失败'
    mapData.value = {
      spot: null,
      nodes: [],
      edges: [],
      buildings: [],
      facilities: [],
      entrance_node_id: null,
      available_modes: [],
      display_modes: [{ value: 'walk', label: '步行' }],
      facility_categories: [],
      indoor_navigation: null,
    }
  } finally {
    loading.value = false
  }
}

async function planRoute() {
  if (!canPlanRoute.value) return
  planning.value = true
  routeError.value = ''
  orderedNames.value = []

  try {
    const hasWaypoints = waypointIds.value.length > 0
    const url = hasWaypoints ? `${API_BASE}/api/route/plan-multi` : `${API_BASE}/api/route/plan`
    const payload = hasWaypoints
      ? {
          spot_id: spotId.value,
          start_node_id: startNodeId.value,
          waypoint_ids: [...waypointIds.value, endNodeId.value],
          return_to_start: false,
          strategy: strategy.value,
          transport_mode: transportMode.value,
        }
      : {
          spot_id: spotId.value,
          start_node_id: startNodeId.value,
          end_node_id: endNodeId.value,
          strategy: strategy.value,
          transport_mode: transportMode.value,
        }

    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    if (!res.ok) throw new Error(`接口返回 ${res.status}`)
    const result = await res.json()
    routeResult.value = result
    orderedNames.value = result.ordered_waypoint_names || []

    if (result.error) {
      routeError.value = result.error
      clearActivePath()
      return
    }

    drawPath(result.path || [], '#2563eb', endNodeName.value || '到达')
  } catch (error) {
    routeError.value = error.message || '路线规划失败'
  } finally {
    planning.value = false
  }
}

async function fetchNearbyFacilities() {
  if (!nearbyOriginNodeId.value) return
  nearbyLoading.value = true
  nearbyError.value = ''
  activeNearbyNodeId.value = null

  try {
    const params = new URLSearchParams({
      spot_id: String(spotId.value),
      origin_node_id: String(nearbyOriginNodeId.value),
      top_k: '12',
      transport_mode: transportMode.value,
    })
    if (nearbyCategory.value && nearbyCategory.value !== 'all') params.set('category', nearbyCategory.value)
    if (nearbyKeyword.value.trim()) params.set('keyword', nearbyKeyword.value.trim())
    params.set('strategy', nearbyStrategy.value)

    const res = await fetch(`${API_BASE}/api/route/nearby-facilities?${params.toString()}`)
    if (!res.ok) throw new Error(`接口返回 ${res.status}`)
    const data = await res.json()
    if (data.error) throw new Error(data.error)
    nearbyResults.value = data.results || []
    mapData.value.facility_categories = data.facility_categories || mapData.value.facility_categories

    if (nearbyResults.value.length) {
      previewNearbyResult(nearbyResults.value[0])
    } else {
      clearActivePath()
    }
  } catch (error) {
    nearbyError.value = error.message || '附近设施查询失败'
    nearbyResults.value = []
    clearActivePath()
  } finally {
    nearbyLoading.value = false
  }
}

function previewNearbyResult(item) {
  activeNearbyNodeId.value = item.node_id
  selectedMapNode.value = nodeMap.value[item.node_id] || null
  drawPath(item.path || [], '#10b981', item.name)
}

async function initMap() {
  if (window._AMapSecurityConfig === undefined) {
    window._AMapSecurityConfig = { securityJsCode: AMAP_SECURITY_KEY }
  }
  await loadAMapScript()
  const AMap = window.AMap
  map = new AMap.Map('internal-nav-map', {
    zoom: 16,
    center: mapPoint(mapData.value.spot?.location_lng || 116.35255, mapData.value.spot?.location_lat || 39.9612),
    resizeEnable: true,
    viewMode: '2D',
  })
  drawRoadNetwork()
  drawAnchors()
}

function loadAMapScript() {
  return new Promise((resolve) => {
    if (window.AMap) {
      resolve()
      return
    }
    const script = document.createElement('script')
    script.src = `https://webapi.amap.com/maps?v=2.0&key=${AMAP_KEY}`
    script.onload = () => resolve()
    document.head.appendChild(script)
  })
}

function drawRoadNetwork() {
  if (!map || !mapData.value.nodes.length) return
  const AMap = window.AMap
  const nodes = nodeMap.value
  const drawn = new Set()

  for (const edge of mapData.value.edges) {
    const from = nodes[edge.from_node_id]
    const to = nodes[edge.to_node_id]
    if (!from || !to) continue
    const key = [Math.min(edge.from_node_id, edge.to_node_id), Math.max(edge.from_node_id, edge.to_node_id), edge.road_type].join('-')
    if (drawn.has(key)) continue
    drawn.add(key)

    const polyline = new AMap.Polyline({
      path: [projectNode(from), projectNode(to)],
      strokeColor: edge.road_type === 'bike' ? 'rgba(245, 158, 11, 0.55)' : 'rgba(148, 163, 184, 0.55)',
      strokeWeight: edge.road_type === 'bike' ? 2.5 : 2,
      strokeOpacity: 0.95,
      strokeStyle: edge.road_type === 'bike' ? 'dashed' : 'solid',
      lineJoin: 'round',
      lineCap: 'round',
    })
    polyline.setMap(map)
    roadPolylines.push(polyline)
  }
}

function drawAnchors() {
  if (!map) return
  const AMap = window.AMap
  clearAnchorMarkers()

  for (const node of anchorNodes.value) {
    const color = node.type === 'entrance' ? '#f97316' : node.type === 'building' ? '#2563eb' : '#8b5cf6'
    const marker = new AMap.CircleMarker({
      center: projectNode(node),
      radius: node.type === 'entrance' ? 7 : 5,
      fillColor: color,
      fillOpacity: 0.92,
      strokeColor: '#ffffff',
      strokeWeight: 2,
      zIndex: 20,
    })
    marker.setMap(map)
    marker.on('click', () => focusNode(node))

    const label = new AMap.Text({
      text: node.name,
      position: projectNode(node),
      offset: new AMap.Pixel(10, -8),
      style: {
        'background-color': 'rgba(255,255,255,0.96)',
        border: '1px solid rgba(148,163,184,0.35)',
        'border-radius': '999px',
        color: '#0f172a',
        'font-size': '11px',
        'white-space': 'nowrap',
        padding: '3px 8px',
        'box-shadow': '0 4px 10px rgba(15,23,42,0.08)',
      },
    })
    label.setMap(map)

    anchorMarkers.push(marker, label)
  }
}

function drawPath(path, color, endLabel) {
  if (!map || !path.length) return
  const AMap = window.AMap
  clearActivePath()
  const coords = projectPath(path)
  activePolyline = new AMap.Polyline({
    path: coords,
    strokeColor: color,
    strokeWeight: 5,
    strokeOpacity: 0.95,
    showDir: true,
    lineJoin: 'round',
    lineCap: 'round',
    zIndex: 50,
  })
  activePolyline.setMap(map)

  addFlag(path[0], `出发 · ${startNodeName.value}`, '#f97316')
  addFlag(path[path.length - 1], endLabel || '到达', color)
  map.setFitView([activePolyline])
}

function addFlag(point, label, color) {
  const AMap = window.AMap
  const marker = new AMap.Marker({
    position: mapPoint(point.lng, point.lat),
    content: `<div style="background:${color};color:#fff;padding:4px 10px;border-radius:999px;font-size:12px;font-weight:600;white-space:nowrap;box-shadow:0 6px 16px rgba(15,23,42,0.16)">${label}</div>`,
    offset: new AMap.Pixel(-24, -18),
  })
  marker.setMap(map)
  activeMarkers.push(marker)
}

function clearAnchorMarkers() {
  anchorMarkers.forEach(marker => marker.setMap?.(null))
  anchorMarkers = []
}

function clearActivePath() {
  if (activePolyline) {
    activePolyline.setMap(null)
    activePolyline = null
  }
  activeMarkers.forEach(marker => marker.setMap(null))
  activeMarkers = []
}

watch([startNodeId, endNodeId, waypointIds], () => {
  routeResult.value = null
  orderedNames.value = []
  routeError.value = ''
  clearActivePath()
})

watch([transportMode, strategy], async () => {
  routeResult.value = null
  orderedNames.value = []
  routeError.value = ''
  if (activePanel.value === 'nearby' && nearbyOriginNodeId.value) {
    await fetchNearbyFacilities()
    return
  }
  clearActivePath()
  if (canPlanRoute.value) {
    await planRoute()
  }
})

watch(activePanel, () => {
  routeError.value = ''
  nearbyError.value = ''
  if (activePanel.value !== 'nearby') {
    activeNearbyNodeId.value = null
  }
  if (activePanel.value === 'indoor') {
    clearActivePath()
  }
})

watch([nearbyCategory, nearbyKeyword, nearbyStrategy], () => {
  if (activePanel.value === 'nearby' && nearbyOriginNodeId.value) {
    fetchNearbyFacilities()
  }
})

watch(activeIndoorScene, (scene) => {
  if (!scene) return
  const firstStep = scene.steps?.[0]
  if (firstStep) indoorFloorId.value = firstStep.floor_id
}, { immediate: true })

onMounted(async () => {
  await loadMapData()
  await nextTick()
  await initMap()
})

onBeforeUnmount(() => {
  roadPolylines.forEach(polyline => polyline.setMap(null))
  clearAnchorMarkers()
  clearActivePath()
  if (map) map.destroy()
})
</script>

<style scoped>
.internal-nav-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #ffffff;
  color: #0f172a;
}

.nav-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 18px;
  background: rgba(255, 255, 255, 0.96);
  border-bottom: 1px solid rgba(226, 232, 240, 0.95);
}

.back-btn,
.header-badge,
.mini-btn,
.top-tab,
.mode-tab,
.transport-tab,
.filter-chip,
.plan-btn,
.remove-btn,
.candidate-item {
  transition: all 0.18s ease;
}

.back-btn {
  width: 40px;
  height: 40px;
  border: 1px solid rgba(203, 213, 225, 1);
  border-radius: 50%;
  background: #fff;
  color: #0f172a;
  font-size: 18px;
  cursor: pointer;
}

.header-center {
  flex: 1;
  text-align: center;
}

.header-title {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
}

.header-sub {
  font-size: 12px;
  color: #64748b;
}

.header-badge {
  min-width: 52px;
  text-align: center;
  padding: 8px 10px;
  border-radius: 999px;
  background: #eff6ff;
  color: #2563eb;
  font-size: 12px;
  font-weight: 700;
}

.page-body {
  display: flex;
  flex: 1;
  min-height: 0;
}

.control-panel {
  width: 360px;
  padding: 16px;
  overflow-y: auto;
  border-right: 1px solid rgba(226, 232, 240, 0.95);
  background: #f8fafc;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.panel-card {
  background: #ffffff;
  border: 1px solid rgba(226, 232, 240, 1);
  border-radius: 18px;
  padding: 14px;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.04);
}

.section-heading {
  font-size: 13px;
  font-weight: 700;
  margin-bottom: 10px;
  color: #334155;
}

.search-input {
  width: 100%;
  padding: 11px 12px;
  border-radius: 12px;
  border: 1px solid rgba(203, 213, 225, 1);
  background: #fff;
  color: #0f172a;
  font-size: 13px;
  outline: none;
}

.search-input:focus {
  border-color: #60a5fa;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.08);
}

.candidate-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-top: 10px;
  max-height: 220px;
  overflow-y: auto;
}

.candidate-list.compact {
  max-height: 260px;
}

.candidate-item,
.nearby-item {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  text-align: left;
  border: 1px solid rgba(226, 232, 240, 1);
  background: #fff;
  border-radius: 12px;
  padding: 10px 12px;
  cursor: pointer;
}

.candidate-item:hover,
.nearby-item:hover,
.candidate-item.active,
.nearby-item.active {
  border-color: rgba(96, 165, 250, 0.9);
  background: rgba(239, 246, 255, 0.9);
}

.nearby-preview {
  width: 100%;
  border: none;
  background: transparent;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
  text-align: left;
  cursor: pointer;
}

.nearby-actions-row {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.primary-action {
  background: #2563eb;
  color: #fff;
  border-color: #2563eb;
}

.candidate-type-badge {
  font-size: 11px;
  padding: 3px 8px;
  border-radius: 999px;
  background: #f1f5f9;
  color: #475569;
}

.node-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.node-dot.entrance { background: #f97316; }
.node-dot.building { background: #2563eb; }
.node-dot.facility { background: #8b5cf6; }
.node-dot.crossing { background: #94a3b8; }

.route-slot-card {
  border-radius: 14px;
  border: 1px solid rgba(226, 232, 240, 1);
  background: #f8fafc;
  padding: 12px;
}

.route-slot-card.start {
  border-color: rgba(251, 146, 60, 0.28);
  background: rgba(255, 247, 237, 0.95);
}

.route-slot-card.end {
  border-color: rgba(37, 99, 235, 0.2);
  background: rgba(239, 246, 255, 0.95);
}

.route-slot-label {
  font-size: 12px;
  color: #64748b;
  margin-bottom: 4px;
}

.route-action-row {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.secondary-action {
  background: #fff;
  color: #334155;
  border: 1px solid rgba(203, 213, 225, 1);
}

.route-slot-hint {
  margin-top: 6px;
  font-size: 12px;
  color: #64748b;
  line-height: 1.5;
}
.selected-node-card,
.hint-card {
  border-radius: 14px;
  background: #f8fafc;
  border: 1px solid rgba(226, 232, 240, 1);
  padding: 12px;
}

.hint-card {
  color: #64748b;
  font-size: 13px;
  line-height: 1.6;
}

.hint-card.small {
  margin-top: 10px;
  font-size: 12px;
}

.selected-node-title-row,
.summary-row,
.nearby-main-row,
.nearby-meta-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.selected-node-title {
  font-weight: 700;
}

.selected-node-meta,
.nearby-meta-row,
.metric-label,
.order-title {
  color: #64748b;
  font-size: 12px;
}

.action-grid,
.top-tabs,
.mode-tabs,
.transport-tabs,
.chips-wrap {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.transport-tabs-icons {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.transport-tab-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.transport-icon {
  font-size: 18px;
  line-height: 1;
}

.top-tab,
.mode-tab,
.transport-tab,
.filter-chip,
.mini-btn {
  border: 1px solid rgba(203, 213, 225, 1);
  background: #fff;
  color: #334155;
  border-radius: 12px;
  padding: 9px 12px;
  cursor: pointer;
  font-size: 13px;
}

.top-tab.active,
.mode-tab.active,
.transport-tab.active,
.filter-chip.active {
  background: #2563eb;
  color: #fff;
  border-color: #2563eb;
}

.transport-tab.secondary.active {
  background: #0f766e;
  border-color: #0f766e;
}

.mini-btn {
  font-size: 12px;
  padding: 7px 10px;
}

.mini-btn.ghost {
  background: transparent;
}

.mini-btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.selected-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.selected-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  border-radius: 12px;
  background: #eff6ff;
}

.selected-idx {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: #2563eb;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
}

.remove-btn {
  border: none;
  background: transparent;
  color: #64748b;
  font-size: 18px;
  cursor: pointer;
}

.plan-btn {
  width: 100%;
  margin-top: 12px;
  border: none;
  border-radius: 14px;
  padding: 13px 14px;
  background: linear-gradient(135deg, #2563eb, #06b6d4);
  color: #fff;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
}

.plan-btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.secondary-btn {
  background: linear-gradient(135deg, #10b981, #0ea5e9);
}

.result-card {
  border-color: rgba(191, 219, 254, 1);
  background: linear-gradient(180deg, rgba(239, 246, 255, 0.95), rgba(255, 255, 255, 0.98));
}

.result-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  margin-bottom: 10px;
}

.metric-card {
  border-radius: 14px;
  background: #fff;
  border: 1px solid rgba(219, 234, 254, 1);
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.mode-chip,
.chip-label {
  padding: 4px 8px;
  border-radius: 999px;
  font-size: 12px;
}

.mode-chip {
  background: #dbeafe;
  color: #1d4ed8;
}

.chip-label {
  background: #e2e8f0;
  color: #475569;
}

.order-box {
  margin-top: 10px;
}

.order-chain {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
  margin-top: 8px;
}

.order-node {
  padding: 4px 10px;
  border-radius: 999px;
  background: #e0f2fe;
  color: #0369a1;
  font-size: 12px;
}

.order-node.start {
  background: #ffedd5;
  color: #c2410c;
}

.order-node.end {
  background: #dbeafe;
  color: #1d4ed8;
}

.order-arrow {
  color: #94a3b8;
}

.results-list {
  margin-top: 0;
}

.nearby-item {
  flex-direction: column;
  align-items: stretch;
}

.nearby-path-row {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  font-size: 12px;
  color: #475569;
}

.nearby-desc {
  font-size: 12px;
  line-height: 1.5;
  color: #64748b;
}

.indoor-canvas {
  margin-top: 12px;
  border-radius: 18px;
  background: linear-gradient(180deg, #ffffff, #f8fafc);
  border: 1px solid rgba(226, 232, 240, 1);
  padding: 12px;
}

.indoor-canvas svg {
  width: 100%;
  height: 220px;
}

.indoor-edge {
  stroke: #cbd5e1;
  stroke-width: 2.6;
}

.indoor-edge.active {
  stroke: #2563eb;
  stroke-width: 4;
}

.indoor-node {
  fill: #cbd5e1;
  stroke: #ffffff;
  stroke-width: 1.5;
}

.indoor-node.entrance { fill: #f97316; }
.indoor-node.elevator,
.indoor-node.stairs { fill: #8b5cf6; }
.indoor-node.room { fill: #2563eb; }
.indoor-node.corridor,
.indoor-node.hall,
.indoor-node.service { fill: #94a3b8; }
.indoor-node.active { stroke: #0f172a; stroke-width: 2.5; }

.indoor-label {
  font-size: 4.2px;
  fill: #334155;
  text-anchor: middle;
}

.top-gap {
  margin-top: 10px;
}

.status-stack {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.status-card {
  border-radius: 14px;
  padding: 12px 14px;
  font-size: 13px;
  line-height: 1.5;
}

.error-card {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #b91c1c;
}

.empty-card {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  color: #64748b;
}

.map-area {
  position: relative;
  flex: 1;
  min-width: 0;
  background: #fff;
}

.amap-container {
  width: 100%;
  height: 100%;
}

.map-loading {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 12px;
  background: rgba(255, 255, 255, 0.9);
  color: #475569;
}

.loading-spinner {
  width: 36px;
  height: 36px;
  border: 3px solid rgba(37, 99, 235, 0.18);
  border-top-color: #2563eb;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.map-floating-card {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 260px;
  padding: 14px;
  border-radius: 18px;
  border: 1px solid rgba(226, 232, 240, 1);
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 12px 30px rgba(15, 23, 42, 0.12);
}

.floating-title {
  font-size: 15px;
  font-weight: 700;
}

.floating-sub {
  font-size: 12px;
  color: #64748b;
  margin-top: 4px;
}

.floating-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
