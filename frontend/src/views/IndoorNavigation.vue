<template>
  <div class="indoor-demo-page">
    <div class="sidebar">
      <div class="sidebar-header">
        <div class="logo-row">
          <span class="logo-icon">🏢</span>
          <span class="logo-text">室内导航</span>
        </div>
        <p class="logo-sub">建筑多层导航模拟演示</p>
      </div>

      <div class="scene-switcher">
        <label class="switch-label">场景选择</label>
        <div class="scene-tabs">
          <button
            v-for="scene in scenes"
            :key="scene.id"
            :class="['scene-tab', { active: currentScene === scene.id }]"
            @click="switchScene(scene.id)"
          >
            <span class="scene-icon">{{ scene.icon }}</span>
            <span>{{ scene.label }}</span>
          </button>
        </div>
      </div>

      <div class="point-selectors">
        <div class="selector-group">
          <label class="selector-label">起点选择</label>
          <select v-model="selectedStartId" class="custom-select" @change="onPointChange">
            <option value="" disabled>请选择起点</option>
            <option
              v-for="node in allSelectableNodes"
              :key="`start-${node.id}`"
              :value="node.id"
            >
              {{ node.floorLabel }} · {{ node.label }}
            </option>
          </select>
        </div>

        <div class="selector-group">
          <label class="selector-label">终点选择</label>
          <select v-model="selectedEndId" class="custom-select" @change="onPointChange">
            <option value="" disabled>请选择终点</option>
            <option
              v-for="node in allSelectableNodes"
              :key="`end-${node.id}`"
              :value="node.id"
            >
              {{ node.floorLabel }} · {{ node.label }}
            </option>
          </select>
        </div>
      </div>

      <div class="nav-type-display">
        <label class="control-label">导航类型</label>
        <div :class="['nav-type-badge', computedNavType]">
          <span class="nav-type-icon">{{ computedNavType === 'in-floor' ? '🏃' : '🛗' }}</span>
          <span>{{ computedNavType === 'in-floor' ? '楼层内导航' : '跨楼层导航' }}</span>
        </div>
        <p v-if="selectedStartId && selectedEndId" class="nav-hint">
          {{ computedNavType === 'in-floor' 
            ? `起点和终点均在 ${startNode?.floorLabel}，已自动切换为楼层内导航` 
            : `从 ${startNode?.floorLabel} 到 ${endNode?.floorLabel}，已自动切换为跨楼层导航` }}
        </p>
      </div>

      <div class="floor-control">
        <label class="control-label">楼层视图</label>
        <div class="floor-buttons">
          <button
            v-for="floor in currentFloors"
            :key="floor.id"
            :class="['floor-btn', { active: displayFloor === floor.id }]"
            @click="displayFloor = floor.id"
          >
            {{ floor.label }}
          </button>
        </div>
      </div>

      <div class="route-info">
        <label class="control-label">路径信息</label>
        <div v-if="computedRoutePath" class="route-path-box">
          <div class="path-row">
            <span class="path-label">起点</span>
            <strong>{{ computedRoutePath.startLabel }}</strong>
          </div>
          <div class="path-row">
            <span class="path-label">终点</span>
            <strong>{{ computedRoutePath.endLabel }}</strong>
          </div>
          <div class="path-row path-chain-row">
            <span class="path-label">路径</span>
            <span class="path-chain">{{ computedRoutePath.pathLabels.join(' → ') }}</span>
          </div>
          <div v-if="computedRoutePath.floorTransitions.length" class="floor-transition-box">
            <span class="transition-label">楼层切换</span>
            <span class="transition-chain">{{ computedRoutePath.floorTransitions.join(' → ') }}</span>
          </div>
        </div>
        <div v-else class="hint-box">
          选择起点和终点后自动生成导航路线
        </div>
      </div>

      <button
        class="start-nav-btn"
        :disabled="!canNavigate || isNavigating"
        @click="startNavigation"
      >
        {{ isNavigating ? '导航中...' : '开始导航' }}
      </button>

      <button v-if="isNavigating" class="stop-nav-btn" @click="stopNavigation">
        停止导航
      </button>
    </div>

    <div class="main-area">
      <div class="scene-header">
        <h2 class="scene-title">{{ currentSceneData.label }}</h2>
        <span class="scene-desc">{{ currentSceneData.description }}</span>
      </div>

      <div class="canvas-container">
        <svg
          ref="svgRef"
          class="nav-svg"
          :viewBox="`0 0 ${svgWidth} ${svgHeight}`"
          preserveAspectRatio="xMidYMid meet"
        >
          <defs>
            <linearGradient id="wallGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="rgba(99, 102, 241, 0.8)" />
              <stop offset="100%" stop-color="rgba(139, 92, 246, 0.8)" />
            </linearGradient>
            <linearGradient id="pathGradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stop-color="#06b6d4" />
              <stop offset="100%" stop-color="#3b82f6" />
            </linearGradient>
            <linearGradient id="crossFloorGradient" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stop-color="#8b5cf6" />
              <stop offset="100%" stop-color="#06b6d4" />
            </linearGradient>
            <filter id="glow">
              <feGaussianBlur stdDeviation="3" result="coloredBlur" />
              <feMerge>
                <feMergeNode in="coloredBlur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
            <marker
              id="arrowhead"
              markerWidth="10"
              markerHeight="7"
              refX="10"
              refY="3.5"
              orient="auto"
            >
              <polygon points="0 0, 10 3.5, 0 7" fill="#06b6d4" />
            </marker>
          </defs>

          <rect class="bg-rect" width="100%" height="100%" />

          <g class="floor-structure">
            <rect
              v-for="(wall, idx) in displayFloorWalls"
              :key="`wall-${idx}`"
              :x="wall.x"
              :y="wall.y"
              :width="wall.width"
              :height="wall.height"
              class="wall-rect"
            />
          </g>

          <g class="rooms">
            <rect
              v-for="(room, idx) in displayFloorRooms"
              :key="`room-${idx}`"
              :x="room.x"
              :y="room.y"
              :width="room.width"
              :height="room.height"
              class="room-rect"
              rx="4"
            />
            <text
              v-for="(room, idx) in displayFloorRooms"
              :key="`room-label-${idx}`"
              :x="room.x + room.width / 2"
              :y="room.y + room.height / 2 + 5"
              class="room-text"
              text-anchor="middle"
            >
              {{ room.label }}
            </text>
          </g>

          <g class="facilities">
            <g
              v-for="facility in displayFloorFacilities"
              :key="facility.id"
              class="facility-group"
            >
              <circle
                :cx="facility.x"
                :cy="facility.y"
                :r="facility.type === 'elevator' ? 18 : 14"
                class="facility-circle"
                :class="facility.type"
              />
              <text
                :x="facility.x"
                :y="facility.y + 5"
                class="facility-text"
                text-anchor="middle"
              >
                {{ facility.icon }}
              </text>
              <text
                :x="facility.x"
                :y="facility.y + 28"
                class="facility-label-text"
                text-anchor="middle"
              >
                {{ facility.label }}
              </text>
            </g>
          </g>

          <g class="path-overlay">
            <template v-if="displayPath.length > 1">
              <path
                v-for="(segment, idx) in pathSegments"
                :key="`path-segment-${idx}`"
                :d="segment.d"
                class="path-segment"
                :class="{ active: isSegmentActive(idx) }"
                fill="none"
                :stroke="segment.isVertical ? 'url(#crossFloorGradient)' : 'url(#pathGradient)'"
                stroke-width="4"
                stroke-linecap="round"
                stroke-linejoin="round"
                :stroke-dasharray="segment.isVertical ? '6 6' : '8 4'"
              />
            </template>
          </g>

          <g class="animated-pointer" filter="url(#glow)">
            <circle
              v-if="showPointer"
              :cx="pointerX"
              :cy="pointerY"
              r="8"
              class="pointer-circle"
            >
              <animate
                attributeName="r"
                :values="pointerRadiusValues"
                dur="1.5s"
                repeatCount="indefinite"
              />
              <animate
                attributeName="opacity"
                :values="pointerOpacityValues"
                dur="1.5s"
                repeatCount="indefinite"
              />
            </circle>
            <circle
              v-if="showPointer"
              :cx="pointerX"
              :cy="pointerY"
              r="5"
              class="pointer-core"
            />
          </g>

          <g class="start-end-markers">
            <g v-if="startNode" class="start-marker">
              <circle
                :cx="startNode.x"
                :cy="startNode.y"
                r="14"
                class="start-marker-circle"
              />
              <text
                :x="startNode.x"
                :y="startNode.y + 5"
                class="marker-text"
                text-anchor="middle"
              >
                🚪
              </text>
              <text
                :x="startNode.x"
                :y="startNode.y + 28"
                class="marker-label"
                text-anchor="middle"
              >
                起点
              </text>
            </g>
            <g v-if="endNode" class="end-marker">
              <circle
                :cx="endNode.x"
                :cy="endNode.y"
                r="14"
                class="end-marker-circle"
              />
              <text
                :x="endNode.x"
                :y="endNode.y + 5"
                class="marker-text"
                text-anchor="middle"
              >
                📍
              </text>
              <text
                :x="endNode.x"
                :y="endNode.y + 28"
                class="marker-label"
                text-anchor="middle"
              >
                终点
              </text>
            </g>
          </g>
        </svg>

        <div v-if="isNavigating" class="nav-overlay">
          <div class="nav-status-card">
            <div class="nav-status-icon">{{ navStatusIcon }}</div>
            <div class="nav-status-text">{{ navStatusText }}</div>
          </div>
        </div>
      </div>

      <div class="legend-bar">
        <div class="legend-item">
          <span class="legend-dot elevator"></span>
          <span>电梯</span>
        </div>
        <div class="legend-item">
          <span class="legend-dot stairs"></span>
          <span>楼梯</span>
        </div>
        <div class="legend-item">
          <span class="legend-dot entrance"></span>
          <span>入口</span>
        </div>
        <div class="legend-item">
          <span class="legend-dot room"></span>
          <span>房间/展厅</span>
        </div>
        <div class="legend-item path-legend">
          <span class="path-line horizontal"></span>
          <span>水平路径</span>
        </div>
        <div class="legend-item path-legend">
          <span class="path-line vertical"></span>
          <span>垂直路径</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onBeforeUnmount } from 'vue'

const svgRef = ref(null)
const svgWidth = 900
const svgHeight = 700

const currentScene = ref('school')
const displayFloor = ref('1F')
const selectedStartId = ref('')
const selectedEndId = ref('')

const isNavigating = ref(false)
const showPointer = ref(false)
const pointerX = ref(0)
const pointerY = ref(0)
const currentPointerIndex = ref(0)
const navigationTimer = ref(null)

const scenes = [
  { id: 'school', icon: '🏫', label: '教学楼' },
  { id: 'museum', icon: '🏛️', label: '博物馆' }
]

const schoolData = {
  label: '教学楼导航模拟',
  description: 'B1 / 1F / 2F 多层教学楼内部导航演示',
  floors: [
    {
      id: 'B1',
      label: '地下一层',
      walls: [{ x: 50, y: 50, width: 800, height: 600 }],
      rooms: [
        { id: 'b1-storage', label: '储藏室', x: 80, y: 80, width: 180, height: 130 },
        { id: 'b1-equipment', label: '设备间', x: 290, y: 80, width: 180, height: 130 },
        { id: 'b1-parking', label: '地下车库', x: 500, y: 80, width: 300, height: 200 },
        { id: 'b1-hall', label: 'B1大厅', x: 80, y: 240, width: 300, height: 200 },
        { id: 'b1-archive', label: '档案室', x: 410, y: 310, width: 200, height: 150 }
      ],
      facilities: [
        { id: 'elevator-b1', type: 'elevator', icon: '🛗', label: '电梯', x: 650, y: 500 },
        { id: 'stairs-b1', type: 'stairs', icon: '🪜', label: '楼梯', x: 780, y: 500 }
      ],
      nodes: [
        { id: 'b1-elevator', label: 'B1电梯', x: 650, y: 500, selectable: true },
        { id: 'b1-stairs', label: 'B1楼梯', x: 780, y: 500, selectable: false },
        { id: 'b1-hall-center', label: 'B1大厅', x: 230, y: 340, selectable: true },
        { id: 'b1-archive-door', label: '档案室门口', x: 510, y: 385, selectable: true }
      ]
    },
    {
      id: '1F',
      label: '1层',
      walls: [{ x: 50, y: 50, width: 800, height: 600 }],
      rooms: [
        { id: '101', label: '101阶梯教室', x: 80, y: 80, width: 200, height: 140 },
        { id: '102', label: '102教室', x: 310, y: 80, width: 160, height: 140 },
        { id: '103', label: '教务处', x: 500, y: 80, width: 180, height: 140 },
        { id: '104', label: '104教室', x: 80, y: 250, width: 180, height: 140 },
        { id: '105', label: '105教室', x: 290, y: 250, width: 180, height: 140 },
        { id: '106', label: '卫生间', x: 500, y: 250, width: 120, height: 100 },
        { id: 'lobby', label: '大厅', x: 650, y: 80, width: 170, height: 280 }
      ],
      facilities: [
        { id: 'entrance-school', type: 'entrance', icon: '🚪', label: '大门', x: 450, y: 620 },
        { id: 'elevator-1f', type: 'elevator', icon: '🛗', label: '电梯', x: 650, y: 500 },
        { id: 'stairs-1f', type: 'stairs', icon: '🪜', label: '楼梯', x: 780, y: 500 }
      ],
      nodes: [
        { id: 'school-gate', label: '大门', x: 450, y: 620, selectable: true },
        { id: '1f-elevator', label: '1F电梯', x: 650, y: 500, selectable: true },
        { id: '1f-stairs', label: '1F楼梯', x: 780, y: 500, selectable: false },
        { id: 'lobby-center', label: '大厅中心', x: 735, y: 220, selectable: true },
        { id: '101-door', label: '101阶梯教室门口', x: 180, y: 220, selectable: true },
        { id: '102-door', label: '102教室门口', x: 390, y: 220, selectable: true },
        { id: '104-door', label: '104教室门口', x: 170, y: 390, selectable: true },
        { id: '105-door', label: '105教室门口', x: 380, y: 390, selectable: true }
      ]
    },
    {
      id: '2F',
      label: '2层',
      walls: [{ x: 50, y: 50, width: 800, height: 600 }],
      rooms: [
        { id: '201', label: '201实验室', x: 80, y: 80, width: 200, height: 140 },
        { id: '202', label: '202实验室', x: 310, y: 80, width: 200, height: 140 },
        { id: '203', label: '203机房', x: 540, y: 80, width: 180, height: 140 },
        { id: '204', label: '204教室', x: 80, y: 250, width: 180, height: 140 },
        { id: '205', label: '205会议室', x: 290, y: 250, width: 180, height: 140 },
        { id: '206', label: '教师办公室', x: 500, y: 250, width: 200, height: 140 },
        { id: '2f-corridor', label: '走廊', x: 500, y: 420, width: 200, height: 120 }
      ],
      facilities: [
        { id: 'elevator-2f', type: 'elevator', icon: '🛗', label: '电梯', x: 650, y: 500 },
        { id: 'stairs-2f', type: 'stairs', icon: '🪜', label: '楼梯', x: 780, y: 500 }
      ],
      nodes: [
        { id: '2f-elevator', label: '2F电梯', x: 650, y: 500, selectable: true },
        { id: '2f-stairs', label: '2F楼梯', x: 780, y: 500, selectable: false },
        { id: '201-door', label: '201实验室门口', x: 180, y: 220, selectable: true },
        { id: '202-door', label: '202实验室门口', x: 410, y: 220, selectable: true },
        { id: '203-door', label: '203机房门口', x: 630, y: 220, selectable: true },
        { id: '204-door', label: '204教室门口', x: 170, y: 390, selectable: true },
        { id: '205-door', label: '205会议室门口', x: 380, y: 390, selectable: true },
        { id: 'corridor-center', label: '走廊中心', x: 600, y: 480, selectable: true }
      ]
    }
  ],
  elevatorNodes: {
    'B1': 'b1-elevator',
    '1F': '1f-elevator',
    '2F': '2f-elevator'
  },
  inFloorPaths: {
    'B1': {
      'b1-elevator__b1-hall-center': ['b1-elevator', 'b1-hall-center'],
      'b1-elevator__b1-archive-door': ['b1-elevator', 'b1-hall-center', 'b1-archive-door'],
      'b1-hall-center__b1-archive-door': ['b1-hall-center', 'b1-archive-door']
    },
    '1F': {
      'school-gate__1f-elevator': ['school-gate', 'lobby-center', '1f-elevator'],
      'school-gate__lobby-center': ['school-gate', 'lobby-center'],
      'school-gate__101-door': ['school-gate', 'lobby-center', '101-door'],
      'school-gate__102-door': ['school-gate', 'lobby-center', '102-door'],
      'school-gate__104-door': ['school-gate', 'lobby-center', '104-door'],
      'school-gate__105-door': ['school-gate', 'lobby-center', '105-door'],
      '1f-elevator__lobby-center': ['1f-elevator', 'lobby-center'],
      '1f-elevator__101-door': ['1f-elevator', 'lobby-center', '101-door'],
      '1f-elevator__102-door': ['1f-elevator', 'lobby-center', '102-door'],
      '1f-elevator__104-door': ['1f-elevator', 'lobby-center', '104-door'],
      '1f-elevator__105-door': ['1f-elevator', 'lobby-center', '105-door'],
      'lobby-center__101-door': ['lobby-center', '101-door'],
      'lobby-center__102-door': ['lobby-center', '102-door'],
      'lobby-center__104-door': ['lobby-center', '104-door'],
      'lobby-center__105-door': ['lobby-center', '105-door'],
      '101-door__102-door': ['101-door', '102-door'],
      '101-door__104-door': ['101-door', '102-door', 'lobby-center', '104-door'],
      '101-door__105-door': ['101-door', '102-door', 'lobby-center', '105-door'],
      '102-door__104-door': ['102-door', 'lobby-center', '104-door'],
      '102-door__105-door': ['102-door', 'lobby-center', '105-door'],
      '104-door__105-door': ['104-door', '105-door']
    },
    '2F': {
      '2f-elevator__corridor-center': ['2f-elevator', 'corridor-center'],
      '2f-elevator__201-door': ['2f-elevator', 'corridor-center', '201-door'],
      '2f-elevator__202-door': ['2f-elevator', 'corridor-center', '202-door'],
      '2f-elevator__203-door': ['2f-elevator', '203-door'],
      '2f-elevator__204-door': ['2f-elevator', 'corridor-center', '204-door'],
      '2f-elevator__205-door': ['2f-elevator', 'corridor-center', '205-door'],
      'corridor-center__201-door': ['corridor-center', '201-door'],
      'corridor-center__202-door': ['corridor-center', '202-door'],
      'corridor-center__204-door': ['corridor-center', '204-door'],
      'corridor-center__205-door': ['corridor-center', '205-door'],
      '201-door__202-door': ['201-door', '202-door'],
      '201-door__203-door': ['201-door', '202-door', '203-door'],
      '201-door__204-door': ['201-door', 'corridor-center', '204-door'],
      '201-door__205-door': ['201-door', 'corridor-center', '205-door'],
      '202-door__203-door': ['202-door', '203-door'],
      '202-door__204-door': ['202-door', 'corridor-center', '204-door'],
      '202-door__205-door': ['202-door', 'corridor-center', '205-door'],
      '203-door__204-door': ['203-door', '202-door', 'corridor-center', '204-door'],
      '203-door__205-door': ['203-door', '202-door', 'corridor-center', '205-door'],
      '204-door__205-door': ['204-door', '205-door']
    }
  }
}

const museumData = {
  label: '博物馆导航模拟',
  description: 'B1 / 1F / 2F 多层博物馆内部展厅导航演示',
  floors: [
    {
      id: 'B1',
      label: '地下一层',
      walls: [{ x: 50, y: 50, width: 800, height: 600 }],
      rooms: [
        { id: 'm-b1-archive', label: '档案库', x: 80, y: 80, width: 200, height: 150 },
        { id: 'm-b1-storage', label: '文物储藏', x: 310, y: 80, width: 180, height: 150 },
        { id: 'm-b1-restoration', label: '修复工作室', x: 520, y: 80, width: 200, height: 150 },
        { id: 'm-b1-temp', label: '临时展厅', x: 80, y: 260, width: 350, height: 250 },
        { id: 'm-b1-vault', label: '保险库', x: 460, y: 260, width: 250, height: 180 }
      ],
      facilities: [
        { id: 'elevator-mb1', type: 'elevator', icon: '🛗', label: '电梯', x: 650, y: 500 },
        { id: 'stairs-mb1', type: 'stairs', icon: '🪜', label: '楼梯', x: 780, y: 500 }
      ],
      nodes: [
        { id: 'mb1-elevator', label: 'B1电梯', x: 650, y: 500, selectable: true },
        { id: 'mb1-stairs', label: 'B1楼梯', x: 780, y: 500, selectable: false },
        { id: 'mb1-temp-door', label: '临时展厅门口', x: 255, y: 385, selectable: true },
        { id: 'mb1-vault-door', label: '保险库门口', x: 585, y: 350, selectable: true }
      ]
    },
    {
      id: '1F',
      label: '1层',
      walls: [{ x: 50, y: 50, width: 800, height: 600 }],
      rooms: [
        { id: 'm-lobby', label: '中央大厅', x: 200, y: 80, width: 400, height: 220 },
        { id: 'm-ticket', label: '售票处', x: 80, y: 80, width: 100, height: 120 },
        { id: 'm-shop', label: '纪念品店', x: 620, y: 80, width: 150, height: 120 },
        { id: 'm-ancient', label: '古代文物展厅', x: 80, y: 230, width: 140, height: 150 },
        { id: 'm-modern', label: '近现代艺术馆', x: 80, y: 410, width: 250, height: 200 },
        { id: 'm-cafe', label: '咖啡休息区', x: 620, y: 230, width: 150, height: 150 }
      ],
      facilities: [
        { id: 'entrance-museum', type: 'entrance', icon: '🚪', label: '正门', x: 450, y: 620 },
        { id: 'elevator-m1f', type: 'elevator', icon: '🛗', label: '中央电梯', x: 650, y: 500 },
        { id: 'stairs-m1f', type: 'stairs', icon: '🪜', label: '楼梯', x: 780, y: 500 }
      ],
      nodes: [
        { id: 'museum-entrance', label: '正门', x: 450, y: 620, selectable: true },
        { id: 'm1f-elevator', label: '1F中央电梯', x: 650, y: 500, selectable: true },
        { id: 'm1f-stairs', label: '1F楼梯', x: 780, y: 500, selectable: false },
        { id: 'm-lobby-center', label: '大厅中心', x: 400, y: 190, selectable: true },
        { id: 'm-ancient-door', label: '古代文物展厅门口', x: 150, y: 305, selectable: true },
        { id: 'm-modern-door', label: '近现代艺术馆门口', x: 205, y: 510, selectable: true },
        { id: 'm-cafe-door', label: '咖啡区门口', x: 695, y: 305, selectable: true }
      ]
    },
    {
      id: '2F',
      label: '2层',
      walls: [{ x: 50, y: 50, width: 800, height: 600 }],
      rooms: [
        { id: 'm-history', label: '历史文物展厅', x: 80, y: 80, width: 250, height: 200 },
        { id: 'm-art', label: '艺术珍品展厅', x: 360, y: 80, width: 250, height: 200 },
        { id: 'm-science', label: '科技展厅', x: 80, y: 310, width: 250, height: 200 },
        { id: 'm-special', label: '特展厅', x: 360, y: 310, width: 250, height: 200 },
        { id: 'm-rest', label: '休息区', x: 650, y: 80, width: 150, height: 180 },
        { id: 'm-library', label: '图书馆', x: 650, y: 290, width: 150, height: 180 }
      ],
      facilities: [
        { id: 'elevator-m2f', type: 'elevator', icon: '🛗', label: '电梯', x: 650, y: 500 },
        { id: 'stairs-m2f', type: 'stairs', icon: '🪜', label: '楼梯', x: 780, y: 500 }
      ],
      nodes: [
        { id: 'm2f-elevator', label: '2F电梯', x: 650, y: 500, selectable: true },
        { id: 'm2f-stairs', label: '2F楼梯', x: 780, y: 500, selectable: false },
        { id: 'm-history-door', label: '历史文物展厅门口', x: 205, y: 180, selectable: true },
        { id: 'm-art-door', label: '艺术珍品展厅门口', x: 485, y: 180, selectable: true },
        { id: 'm-science-door', label: '科技展厅门口', x: 205, y: 410, selectable: true },
        { id: 'm-special-door', label: '特展厅门口', x: 485, y: 410, selectable: true },
        { id: 'm-rest-center', label: '休息区', x: 725, y: 170, selectable: true }
      ]
    }
  ],
  elevatorNodes: {
    'B1': 'mb1-elevator',
    '1F': 'm1f-elevator',
    '2F': 'm2f-elevator'
  },
  inFloorPaths: {
    'B1': {
      'mb1-elevator__mb1-temp-door': ['mb1-elevator', 'mb1-temp-door'],
      'mb1-elevator__mb1-vault-door': ['mb1-elevator', 'mb1-vault-door'],
      'mb1-temp-door__mb1-vault-door': ['mb1-temp-door', 'mb1-vault-door']
    },
    '1F': {
      'museum-entrance__m1f-elevator': ['museum-entrance', 'm-lobby-center', 'm1f-elevator'],
      'museum-entrance__m-lobby-center': ['museum-entrance', 'm-lobby-center'],
      'museum-entrance__m-ancient-door': ['museum-entrance', 'm-lobby-center', 'm-ancient-door'],
      'museum-entrance__m-modern-door': ['museum-entrance', 'm-lobby-center', 'm-modern-door'],
      'museum-entrance__m-cafe-door': ['museum-entrance', 'm-lobby-center', 'm-cafe-door'],
      'm1f-elevator__m-lobby-center': ['m1f-elevator', 'm-lobby-center'],
      'm1f-elevator__m-ancient-door': ['m1f-elevator', 'm-lobby-center', 'm-ancient-door'],
      'm1f-elevator__m-modern-door': ['m1f-elevator', 'm-lobby-center', 'm-modern-door'],
      'm1f-elevator__m-cafe-door': ['m1f-elevator', 'm-lobby-center', 'm-cafe-door'],
      'm-lobby-center__m-ancient-door': ['m-lobby-center', 'm-ancient-door'],
      'm-lobby-center__m-modern-door': ['m-lobby-center', 'm-modern-door'],
      'm-lobby-center__m-cafe-door': ['m-lobby-center', 'm-cafe-door'],
      'm-ancient-door__m-modern-door': ['m-ancient-door', 'm-modern-door'],
      'm-ancient-door__m-cafe-door': ['m-ancient-door', 'm-lobby-center', 'm-cafe-door'],
      'm-modern-door__m-cafe-door': ['m-modern-door', 'm-lobby-center', 'm-cafe-door']
    },
    '2F': {
      'm2f-elevator__m-rest-center': ['m2f-elevator', 'm-rest-center'],
      'm2f-elevator__m-history-door': ['m2f-elevator', 'm-rest-center', 'm-history-door'],
      'm2f-elevator__m-art-door': ['m2f-elevator', 'm-rest-center', 'm-art-door'],
      'm2f-elevator__m-science-door': ['m2f-elevator', 'm-science-door'],
      'm2f-elevator__m-special-door': ['m2f-elevator', 'm-special-door'],
      'm-rest-center__m-history-door': ['m-rest-center', 'm-history-door'],
      'm-rest-center__m-art-door': ['m-rest-center', 'm-art-door'],
      'm-rest-center__m-science-door': ['m-rest-center', 'm-history-door', 'm-science-door'],
      'm-rest-center__m-special-door': ['m-rest-center', 'm-art-door', 'm-special-door'],
      'm-history-door__m-art-door': ['m-history-door', 'm-art-door'],
      'm-history-door__m-science-door': ['m-history-door', 'm-science-door'],
      'm-history-door__m-special-door': ['m-history-door', 'm-art-door', 'm-special-door'],
      'm-art-door__m-science-door': ['m-art-door', 'm-history-door', 'm-science-door'],
      'm-art-door__m-special-door': ['m-art-door', 'm-special-door'],
      'm-science-door__m-special-door': ['m-science-door', 'm-special-door']
    }
  }
}

const currentSceneData = computed(() => {
  return currentScene.value === 'school' ? schoolData : museumData
})

const currentFloors = computed(() => currentSceneData.value.floors)

const displayFloorData = computed(() => {
  return currentSceneData.value.floors.find(f => f.id === displayFloor.value)
})

const displayFloorWalls = computed(() => displayFloorData.value?.walls || [])
const displayFloorRooms = computed(() => displayFloorData.value?.rooms || [])
const displayFloorFacilities = computed(() => displayFloorData.value?.facilities || [])

// Build a flat list of all selectable nodes with floor info
const allSelectableNodes = computed(() => {
  const result = []
  currentSceneData.value.floors.forEach(floor => {
    floor.nodes.forEach(node => {
      if (node.selectable) {
        result.push({ ...node, floorId: floor.id, floorLabel: floor.label })
      }
    })
  })
  return result
})

const startNode = computed(() => {
  if (!selectedStartId.value) return null
  return allSelectableNodes.value.find(n => n.id === selectedStartId.value) || null
})

const endNode = computed(() => {
  if (!selectedEndId.value) return null
  return allSelectableNodes.value.find(n => n.id === selectedEndId.value) || null
})

// Auto-determine nav type based on start/end floors
const computedNavType = computed(() => {
  if (!startNode.value || !endNode.value) return null
  return startNode.value.floorId === endNode.value.floorId ? 'in-floor' : 'cross-floor'
})

// Auto-switch display floor when start is selected
function onPointChange() {
  if (isNavigating.value) stopNavigation()
  if (startNode.value && !endNode.value) {
    displayFloor.value = startNode.value.floorId
  }
}

const canNavigate = computed(() => {
  return selectedStartId.value && selectedEndId.value && selectedStartId.value !== selectedEndId.value
})

// Build the display path for current floor visualization
const computedRoutePath = computed(() => {
  if (!startNode.value || !endNode.value) return null

  const startFloor = startNode.value.floorId
  const endFloor = endNode.value.floorId
  const data = currentSceneData.value

  if (startFloor === endFloor) {
    // Same floor - in-floor navigation
    const key1 = `${startNode.value.id}__${endNode.value.id}`
    const key2 = `${endNode.value.id}__${startNode.value.id}`
    const path = data.inFloorPaths[startFloor]?.[key1] || data.inFloorPaths[startFloor]?.[key2]
    if (!path) return null

    const reversed = data.inFloorPaths[startFloor]?.[key2]
    const actualPath = data.inFloorPaths[startFloor]?.[key1] || (reversed ? [...reversed].reverse() : null)
    if (!actualPath) return null

    const nodeMap = {}
    data.floors.forEach(floor => {
      floor.nodes.forEach(node => { nodeMap[node.id] = node })
    })

    return {
      startLabel: startNode.value.label,
      endLabel: endNode.value.label,
      pathLabels: actualPath.map(id => nodeMap[id]?.label).filter(Boolean),
      floorTransitions: [],
      displayNodes: actualPath.map(id => nodeMap[id]).filter(Boolean)
    }
  }

  // Cross-floor navigation
  const floorOrder = data.floors.map(f => f.id)
  const startIdx = floorOrder.indexOf(startFloor)
  const endIdx = floorOrder.indexOf(endFloor)
  const goingUp = startIdx < endIdx
  const floorsInRange = goingUp
    ? floorOrder.slice(startIdx, endIdx + 1)
    : floorOrder.slice(endIdx, startIdx + 1).reverse()

  const elevatorIds = floorsInRange.map(f => data.elevatorNodes[f])
  const nodeMap = {}
  data.floors.forEach(floor => {
    floor.nodes.forEach(node => { nodeMap[node.id] = node })
  })

  // Build full path: start -> ... -> start-floor elevator -> ... -> end-floor elevator -> ... -> end
  const fullPath = []
  fullPath.push(startNode.value.id)

  // From start to start-floor elevator
  const startFloorKey1 = `${startNode.value.id}__${data.elevatorNodes[startFloor]}`
  const startFloorKey2 = `${data.elevatorNodes[startFloor]}__${startNode.value.id}`
  const startPath = data.inFloorPaths[startFloor]?.[startFloorKey1]
    || (data.inFloorPaths[startFloor]?.[startFloorKey2] ? [...data.inFloorPaths[startFloor][startFloorKey2]].reverse() : null)
  if (startPath) {
    fullPath.push(...startPath.slice(1))
  } else {
    fullPath.push(data.elevatorNodes[startFloor])
  }

  // Elevator segments between floors
  floorsInRange.slice(1).forEach((floorId) => {
    fullPath.push(data.elevatorNodes[floorId])
  })

  // From end-floor elevator to end
  const endFloorKey1 = `${data.elevatorNodes[endFloor]}__${endNode.value.id}`
  const endFloorKey2 = `${endNode.value.id}__${data.elevatorNodes[endFloor]}`
  const endPath = data.inFloorPaths[endFloor]?.[endFloorKey1]
    || (data.inFloorPaths[endFloor]?.[endFloorKey2] ? [...data.inFloorPaths[endFloor][endFloorKey2]].reverse() : null)
  if (endPath) {
    fullPath.push(...endPath.slice(1))
  } else {
    fullPath.push(endNode.value.id)
  }

  const floorTransitions = floorsInRange.map(f => {
    const fl = data.floors.find(ff => ff.id === f)
    return fl?.label || f
  })

  return {
    startLabel: startNode.value.label,
    endLabel: endNode.value.label,
    pathLabels: fullPath.map(id => nodeMap[id]?.label).filter(Boolean),
    floorTransitions,
    displayNodes: fullPath.map(id => nodeMap[id]).filter(Boolean)
  }
})

const displayPath = computed(() => {
  if (!computedRoutePath.value) return []
  return computedRoutePath.value.displayNodes
})

const pathSegments = computed(() => {
  return displayPath.value.slice(0, -1).map((from, idx) => {
    const to = displayPath.value[idx + 1]
    const isVertical = from.floorId !== to.floorId
    return {
      d: `M ${from.x} ${from.y} L ${to.x} ${to.y}`,
      from,
      to,
      isVertical
    }
  })
})

const navStatusIcon = computed(() => {
  if (!canNavigate.value) return '📍'
  const idx = currentPointerIndex.value
  if (idx === 0) return '🚀'
  if (idx >= displayPath.value.length - 1) return '🏁'
  return computedNavType.value === 'cross-floor' ? '🛗' : '🚶'
})

const navStatusText = computed(() => {
  if (!canNavigate.value || displayPath.value.length === 0) return '准备出发...'
  const idx = currentPointerIndex.value
  if (idx === 0) return '正在出发...'
  if (idx >= displayPath.value.length - 1) return '已到达目的地!'
  const nextNode = displayPath.value[idx + 1]
  return `前往: ${nextNode.label}`
})

const pointerRadiusValues = '8;12;8'
const pointerOpacityValues = '1;0.5;1'

function switchScene(sceneId) {
  currentScene.value = sceneId
  displayFloor.value = currentSceneData.value.floors[0].id
  selectedStartId.value = ''
  selectedEndId.value = ''
  stopNavigation()
}

function isSegmentActive(idx) {
  return idx < currentPointerIndex.value
}

function startNavigation() {
  if (!canNavigate.value || displayPath.value.length === 0) return

  isNavigating.value = true
  showPointer.value = true
  currentPointerIndex.value = 0

  const startN = displayPath.value[0]
  pointerX.value = startN.x
  pointerY.value = startN.y

  if (computedNavType.value === 'cross-floor') {
    const targetFloor = endNode.value.floorId
    displayFloor.value = targetFloor
  }

  animateStep(0)
}

function animateStep(stepIndex) {
  if (!navigationTimer.value && !isNavigating.value) return

  const totalSteps = displayPath.value.length - 1
  if (stepIndex >= totalSteps) {
    setTimeout(() => stopNavigation(), 1200)
    return
  }

  const from = displayPath.value[stepIndex]
  const to = displayPath.value[stepIndex + 1]

  if (from.floorId !== to.floorId) {
    displayFloor.value = to.floorId
  }

  const duration = 800
  const startTime = Date.now()

  function animate() {
    const elapsed = Date.now() - startTime
    const progress = Math.min(elapsed / duration, 1)
    const eased = 1 - Math.pow(1 - progress, 3)

    pointerX.value = from.x + (to.x - from.x) * eased
    pointerY.value = from.y + (to.y - from.y) * eased
    currentPointerIndex.value = stepIndex

    if (progress < 1) {
      requestAnimationFrame(animate)
    } else {
      currentPointerIndex.value = stepIndex + 1
      navigationTimer.value = setTimeout(() => {
        if (isNavigating.value) {
          animateStep(stepIndex + 1)
        }
      }, 400)
    }
  }

  requestAnimationFrame(animate)
}

function stopNavigation() {
  if (navigationTimer.value) {
    clearTimeout(navigationTimer.value)
    navigationTimer.value = null
  }
  isNavigating.value = false
  showPointer.value = false
  currentPointerIndex.value = 0
}

onBeforeUnmount(() => {
  stopNavigation()
})
</script>

<style scoped>
.indoor-demo-page {
  display: flex;
  height: 100vh;
  background: linear-gradient(135deg, #0a0a1a 0%, #1a1a3e 50%, #0f0f2f 100%);
  color: #e0e7ff;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.sidebar {
  width: 360px;
  background: rgba(15, 23, 42, 0.85);
  backdrop-filter: blur(20px);
  border-right: 1px solid rgba(99, 102, 241, 0.3);
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 18px;
  overflow-y: auto;
}

.sidebar-header {
  text-align: center;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(99, 102, 241, 0.2);
}

.logo-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.logo-icon {
  font-size: 36px;
}

.logo-text {
  font-size: 24px;
  font-weight: 700;
  background: linear-gradient(135deg, #06b6d4, #8b5cf6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.logo-sub {
  font-size: 12px;
  color: #94a3b8;
  margin-top: 4px;
}

.switch-label,
.control-label,
.selector-label {
  font-size: 13px;
  font-weight: 600;
  color: #94a3b8;
  margin-bottom: 8px;
  display: block;
}

.scene-tabs {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.scene-tab {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 14px 10px;
  border-radius: 12px;
  border: 1px solid rgba(99, 102, 241, 0.3);
  background: rgba(30, 41, 59, 0.6);
  color: #e0e7ff;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.scene-tab:hover {
  background: rgba(99, 102, 241, 0.2);
  border-color: rgba(99, 102, 241, 0.5);
}

.scene-tab.active {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  border-color: transparent;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
}

.scene-icon {
  font-size: 28px;
}

.point-selectors {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.selector-group {
  display: flex;
  flex-direction: column;
}

.custom-select {
  width: 100%;
  padding: 12px 14px;
  border-radius: 10px;
  border: 1px solid rgba(99, 102, 241, 0.3);
  background: rgba(30, 41, 59, 0.8);
  color: #e0e7ff;
  font-size: 13px;
  cursor: pointer;
  outline: none;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' fill='%2394a3b8' viewBox='0 0 16 16'%3E%3Cpath d='M8 11L3 6h10l-5 5z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 12px center;
  transition: all 0.2s;
}

.custom-select:hover {
  border-color: rgba(99, 102, 241, 0.5);
}

.custom-select:focus {
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
}

.custom-select option {
  background: #1e293b;
  color: #e0e7ff;
  padding: 8px;
}

.nav-type-display {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.nav-type-badge {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 16px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.3s;
}

.nav-type-badge.in-floor {
  background: linear-gradient(135deg, rgba(6, 182, 212, 0.2), rgba(59, 130, 246, 0.2));
  border: 1px solid rgba(6, 182, 212, 0.4);
  color: #67e8f9;
}

.nav-type-badge.cross-floor {
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.2), rgba(6, 182, 212, 0.2));
  border: 1px solid rgba(139, 92, 246, 0.4);
  color: #c4b5fd;
}

.nav-type-icon {
  font-size: 22px;
}

.nav-hint {
  font-size: 12px;
  color: #64748b;
  margin: 0;
  line-height: 1.5;
}

.floor-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.floor-btn {
  padding: 10px 16px;
  border-radius: 8px;
  border: 1px solid rgba(99, 102, 241, 0.3);
  background: rgba(30, 41, 59, 0.6);
  color: #e0e7ff;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.floor-btn:hover {
  background: rgba(99, 102, 241, 0.2);
  border-color: rgba(99, 102, 241, 0.5);
}

.floor-btn.active {
  background: #6366f1;
  border-color: transparent;
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.4);
}

.route-info {
  flex: 1;
}

.route-path-box {
  background: rgba(30, 41, 59, 0.8);
  border: 1px solid rgba(99, 102, 241, 0.3);
  border-radius: 12px;
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.path-row {
  display: flex;
  gap: 8px;
  font-size: 13px;
  align-items: flex-start;
}

.path-label {
  color: #94a3b8;
  min-width: 50px;
  flex-shrink: 0;
}

.path-chain-row {
  align-items: flex-start;
}

.path-chain {
  color: #06b6d4;
  font-size: 12px;
  line-height: 1.6;
  word-break: break-all;
}

.floor-transition-box {
  display: flex;
  gap: 8px;
  font-size: 12px;
  padding-top: 8px;
  border-top: 1px dashed rgba(99, 102, 241, 0.2);
}

.transition-label {
  color: #94a3b8;
  min-width: 50px;
}

.transition-chain {
  color: #c4b5fd;
}

.hint-box {
  background: rgba(30, 41, 59, 0.6);
  border: 1px dashed rgba(99, 102, 241, 0.3);
  border-radius: 12px;
  padding: 14px;
  font-size: 13px;
  color: #94a3b8;
  text-align: center;
}

.start-nav-btn {
  width: 100%;
  padding: 14px;
  border-radius: 12px;
  border: none;
  background: linear-gradient(135deg, #06b6d4, #3b82f6);
  color: #fff;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 16px rgba(6, 182, 212, 0.4);
}

.start-nav-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(6, 182, 212, 0.6);
}

.start-nav-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.stop-nav-btn {
  width: 100%;
  padding: 12px;
  border-radius: 12px;
  border: 1px solid #ef4444;
  background: transparent;
  color: #ef4444;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.stop-nav-btn:hover {
  background: rgba(239, 68, 68, 0.1);
}

.main-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 24px;
  gap: 20px;
  overflow: hidden;
}

.scene-header {
  text-align: center;
}

.scene-title {
  margin: 0;
  font-size: 22px;
  font-weight: 700;
  background: linear-gradient(135deg, #06b6d4, #8b5cf6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.scene-desc {
  font-size: 13px;
  color: #94a3b8;
  margin-top: 4px;
}

.canvas-container {
  flex: 1;
  background: rgba(15, 23, 42, 0.6);
  border-radius: 16px;
  border: 1px solid rgba(99, 102, 241, 0.3);
  position: relative;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.nav-svg {
  width: 100%;
  height: 100%;
}

.bg-rect {
  fill: url(#wallGradient);
  opacity: 0.05;
}

.wall-rect {
  fill: rgba(99, 102, 241, 0.15);
  stroke: rgba(99, 102, 241, 0.5);
  stroke-width: 2;
}

.room-rect {
  fill: rgba(30, 41, 59, 0.6);
  stroke: rgba(148, 163, 184, 0.3);
  stroke-width: 1.5;
}

.room-text {
  font-size: 11px;
  fill: #cbd5e1;
}

.facility-circle {
  stroke: #fff;
  stroke-width: 2;
}

.facility-circle.elevator {
  fill: #8b5cf6;
}

.facility-circle.stairs {
  fill: #f59e0b;
}

.facility-circle.entrance {
  fill: #10b981;
}

.facility-text {
  font-size: 14px;
}

.facility-label-text {
  font-size: 10px;
  fill: #94a3b8;
}

.path-segment {
  opacity: 0.25;
}

.path-segment.active {
  opacity: 1;
  animation: dashFlow 0.8s linear infinite;
}

@keyframes dashFlow {
  to {
    stroke-dashoffset: -12;
  }
}

.pointer-circle {
  fill: #06b6d4;
  opacity: 0.5;
}

.pointer-core {
  fill: #fff;
  filter: drop-shadow(0 0 6px #06b6d4);
}

.start-marker-circle {
  fill: #10b981;
  filter: drop-shadow(0 0 8px rgba(16, 185, 129, 0.6));
}

.end-marker-circle {
  fill: #ef4444;
  filter: drop-shadow(0 0 8px rgba(239, 68, 68, 0.6));
}

.marker-text {
  font-size: 12px;
}

.marker-label {
  font-size: 9px;
  fill: #94a3b8;
  font-weight: 600;
}

.nav-overlay {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  pointer-events: none;
}

.nav-status-card {
  background: rgba(15, 23, 42, 0.95);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(99, 102, 241, 0.4);
  border-radius: 14px;
  padding: 14px 24px;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
}

.nav-status-icon {
  font-size: 24px;
}

.nav-status-text {
  font-size: 14px;
  font-weight: 500;
  color: #e0e7ff;
}

.legend-bar {
  display: flex;
  justify-content: center;
  gap: 24px;
  padding: 12px 20px;
  background: rgba(15, 23, 42, 0.8);
  border-radius: 12px;
  border: 1px solid rgba(99, 102, 241, 0.3);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #94a3b8;
}

.legend-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.legend-dot.elevator {
  background: #8b5cf6;
}

.legend-dot.stairs {
  background: #f59e0b;
}

.legend-dot.entrance {
  background: #10b981;
}

.legend-dot.room {
  background: #3b82f6;
}

.path-legend {
  gap: 10px;
}

.path-line {
  width: 20px;
  height: 3px;
  border-radius: 2px;
}

.path-line.horizontal {
  background: linear-gradient(90deg, #06b6d4, #3b82f6);
}

.path-line.vertical {
  background: linear-gradient(180deg, #8b5cf6, #06b6d4);
}
</style>
