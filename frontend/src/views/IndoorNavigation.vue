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
          <select
            v-model="selectedStartId"
            class="custom-select"
                      >
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
          <select
            v-model="selectedEndId"
            class="custom-select"
                      >
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
          <span class="nav-type-icon">{{
            computedNavType === "in-floor" ? "🏃" : "🛗"
          }}</span>
          <span>{{
            computedNavType === "in-floor" ? "楼层内导航" : "跨楼层导航"
          }}</span>
        </div>
        <p v-if="selectedStartId && selectedEndId" class="nav-hint">
          {{
            computedNavType === "in-floor"
              ? `起点和终点均在 ${startNode?.floorLabel}，已自动切换为楼层内导航`
              : `从 ${startNode?.floorLabel} 到 ${endNode?.floorLabel}，已自动切换为跨楼层导航`
          }}
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
            <span class="path-chain">
              <span
                v-for="(node, idx) in chainDisplayNodes"
                :key="node.id"
                class="path-node"
                :class="{ active: node.id === chainActiveNodeId }"
                @click="switchToNodeFloor(node)"
              >
                {{ node.label
                }}<span
                  v-if="idx < chainDisplayNodes.length - 1"
                  class="path-separator"
                >
                  →
                </span>
              </span>
            </span>
          </div>
          <div
            v-if="computedRoutePath.floorTransitions.length"
            class="floor-transition-box"
          >
            <span class="transition-label">楼层切换</span>
            <span class="transition-chain">{{
              computedRoutePath.floorTransitions.join(" → ")
            }}</span>
          </div>
        </div>
        <div v-else class="hint-box">选择起点和终点后自动生成导航路线</div>
      </div>

      <button
        class="start-nav-btn"
        :disabled="!canNavigate || isNavigating"
        @click="startNavigation"
      >
        {{ isNavigating ? "导航中..." : "开始导航" }}
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
            <linearGradient
              id="wallGradient"
              x1="0%"
              y1="0%"
              x2="100%"
              y2="100%"
            >
              <stop offset="0%" stop-color="rgba(99, 102, 241, 0.8)" />
              <stop offset="100%" stop-color="rgba(139, 92, 246, 0.8)" />
            </linearGradient>
            <linearGradient id="pathGradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stop-color="#06b6d4" />
              <stop offset="100%" stop-color="#3b82f6" />
            </linearGradient>
            <linearGradient
              id="crossFloorGradient"
              x1="0%"
              y1="0%"
              x2="0%"
              y2="100%"
            >
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

          <!-- 导航动点（唯一可见的导航指示器，不渲染静态路线） -->
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
            <g
              v-if="startNode && startNode.floorId === displayFloor"
              class="start-marker"
            >
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
            <g
              v-if="endNode && endNode.floorId === displayFloor"
              class="end-marker"
            >
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
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onBeforeUnmount, watch } from "vue";

const svgRef = ref(null);
const svgWidth = 900;
const svgHeight = 700;

const currentScene = ref("school");
const displayFloor = ref("1F");
const selectedStartId = ref("");
const selectedEndId = ref("");

const isNavigating = ref(false);
const showPointer = ref(false);
const pointerX = ref(0);
const pointerY = ref(0);
const currentPointerIndex = ref(0);
const navigationTimer = ref(null);

const scenes = [
  { id: "school", icon: "🏫", label: "教学楼" },
  { id: "museum", icon: "🏛️", label: "博物馆" },
];

const schoolData = {
  label: "教学楼导航模拟",
  description: "B1 / 1F / 2F 多层教学楼内部导航演示",
  // ─── 碰撞安全设计规范 ───
  // 房间边界框 (BBox): 101(80-280,80-220) 102(310-470,80-220) 103(500-680,80-220)
  //                     104(80-260,250-390) 105(290-470,250-390) 106(500-620,250-350)
  // 安全走廊: 中央走廊 y∈[220,250] 中心线 y=235
  //           右侧大厅 x∈[680,850] 中心线 x=735
  //           底部通道 y≥390, 入口通道 x∈[450,735] y≥560
  // 原则: 所有边必须完全位于安全走廊内，X或Y坐标绝不进入任何房间BBox
  floors: [
    {
      id: "B1",
      label: "地下一层",
      walls: [{ x: 50, y: 50, width: 800, height: 600 }],
      // ─── 走廊中心线 (corridor_center_lines) ───
      // 主水平脊线 y=290: 位于上排房间(max y=280)与档案室(min y=310)之间，全 x∈[80,800] 安全
      // 右侧垂直脊线 x=650: 停车场右侧至电梯，全 y∈[280,500] 安全
      // 下层水平脊线 y=465: 档案室下边缘(y=460)以下 5px，x∈[510,650] 安全
      rooms: [
        { id: "b1-storage", label: "储藏室", x: 80, y: 80, width: 180, height: 130 },
        { id: "b1-equipment", label: "设备间", x: 290, y: 80, width: 180, height: 130 },
        { id: "b1-parking", label: "地下车库", x: 500, y: 80, width: 300, height: 200 },
        { id: "b1-archive", label: "档案室", x: 410, y: 310, width: 200, height: 150 },
      ],
      facilities: [
        { id: "elevator-b1", type: "elevator", icon: "🛗", label: "电梯", x: 650, y: 500 },
        { id: "stairs-b1", type: "stairs", icon: "🪜", label: "楼梯", x: 780, y: 500 },
      ],
      nodes: [
        { id: "b1-elevator", label: "B1电梯", x: 650, y: 500, selectable: true, icon: "🛗" },
        { id: "b1-parking-door", label: "车库入口", x: 650, y: 280, selectable: true },
        { id: "b1-archive-door", label: "档案室门口", x: 510, y: 460, selectable: true },
        { id: "b1-storage-door", label: "储藏室门口", x: 170, y: 210, selectable: true },
        // ── 拐点：严格布设在走廊中心线上，每个门口垂直投影到脊线 ──
        // 主脊线 y=290
        { id: "b1-sp-storage", x: 170, y: 290, selectable: false },
        { id: "b1-sp-hall",    x: 230, y: 290, selectable: false },
        { id: "b1-sp-elev",    x: 650, y: 290, selectable: false },
        // 下层脊线 y=465 (档案室下方)
        { id: "b1-lo-archive", x: 510, y: 465, selectable: false },
        { id: "b1-lo-elev",    x: 650, y: 465, selectable: false },
      ],
      adjacency: {
        // 门口 → 脊线投影点（精确轴对齐，垂直连接）
        "b1-storage-door": ["b1-sp-storage"],
        "b1-sp-storage":   ["b1-storage-door", "b1-sp-hall"],
        "b1-parking-door": ["b1-sp-elev"],
        // 主脊线水平链 (y=290)
        "b1-sp-hall": ["b1-sp-storage", "b1-sp-elev"],
        "b1-sp-elev": ["b1-parking-door", "b1-sp-hall", "b1-lo-elev"],
        // 右侧垂直下降 (x=650)
        "b1-lo-elev": ["b1-sp-elev", "b1-elevator", "b1-lo-archive"],
        "b1-elevator": ["b1-lo-elev"],
        // 下层水平延伸至档案室 (y=465)
        "b1-lo-archive": ["b1-lo-elev", "b1-archive-door"],
        "b1-archive-door": ["b1-lo-archive"],
      },
    },
    {
      id: "1F",
      label: "1层",
      walls: [{ x: 50, y: 50, width: 800, height: 600 }],
      rooms: [
        // 上排 (y:80-220, 门在底边 y=220 朝向中央走廊)
        { id: "101", label: "101阶梯教室", x: 80, y: 80, width: 200, height: 140 },
        { id: "102", label: "102教室", x: 310, y: 80, width: 160, height: 140 },
        { id: "103", label: "教务处", x: 500, y: 80, width: 180, height: 140 },
        // 下排 (y:250-390, 门在顶边 y=250 朝向中央走廊)
        { id: "104", label: "104教室", x: 80, y: 250, width: 180, height: 140 },
        { id: "105", label: "105教室", x: 290, y: 250, width: 180, height: 140 },
        { id: "106", label: "卫生间", x: 500, y: 250, width: 120, height: 100 },
        // 大厅已移除，留白为公共通道
      ],
      facilities: [
        { id: "entrance-school", type: "entrance", icon: "🚪", label: "大门", x: 450, y: 620 },
        { id: "elevator-1f", type: "elevator", icon: "🛗", label: "电梯", x: 650, y: 500 },
        { id: "stairs-1f", type: "stairs", icon: "🪜", label: "楼梯", x: 780, y: 500 },
      ],
      nodes: [
        // ── 可选节点（门口 & 设施）──
        { id: "school-gate", label: "大门", x: 450, y: 620, selectable: true, icon: "🚪" },
        { id: "1f-elevator", label: "1F电梯", x: 650, y: 500, selectable: true, icon: "🛗" },
        // 上排门：房间底边中心
        { id: "101-door", label: "101门口", x: 180, y: 220, selectable: true },
        { id: "102-door", label: "102门口", x: 390, y: 220, selectable: true },
        { id: "103-door", label: "教务处门口", x: 590, y: 220, selectable: true },
        // 下排门：房间顶边中心（朝向中央走廊！）
        { id: "104-door", label: "104门口", x: 170, y: 250, selectable: true },
        { id: "105-door", label: "105门口", x: 380, y: 250, selectable: true },
        { id: "106-door", label: "卫生间门口", x: 560, y: 250, selectable: true },
        // ── 隐藏路网拐点：仅在中央走廊中心线 (y=235, 安全区间 y∈[220,250]) ──
        // 每个拐点对齐对应门口的 x 坐标，水平边均在 y=235 无碰撞
        { id: "w-104", x: 170, y: 235, selectable: false },
        { id: "w-101", x: 180, y: 235, selectable: false },
        { id: "w-105", x: 380, y: 235, selectable: false },
        { id: "w-102", x: 390, y: 235, selectable: false },
        { id: "w-106", x: 560, y: 235, selectable: false },
        { id: "w-103", x: 590, y: 235, selectable: false },
        { id: "w-lobby", x: 735, y: 235, selectable: false },
        // 右侧大厅垂直通道 (x=735, 安全区间 x∈[680,850])
        { id: "w-lobby-mid", x: 735, y: 420, selectable: false },
        { id: "w-lobby-bot", x: 735, y: 560, selectable: false },
        // 入口通道 (y=560, 安全区间 y≥390)
        { id: "w-ent", x: 450, y: 560, selectable: false },
        // 电梯/楼梯连接点 (大厅区域)
        { id: "w-elev-crn", x: 735, y: 500, selectable: false },
      ],
      // 邻接表：每条边的两个端点坐标共享 X 或 Y，且线段完全在安全走廊内
      adjacency: {
        // 上排门垂直连至中央走廊 (y:220→235)
        "101-door": ["w-101"], "102-door": ["w-102"], "103-door": ["w-103"],
        // 下排门垂直连至中央走廊 (y:250→235)
        "104-door": ["w-104"], "105-door": ["w-105"], "106-door": ["w-106"],
        // 中央走廊水平链 (y=235, 按 x 升序)
        "w-104": ["104-door", "w-101"],
        "w-101": ["101-door", "w-104", "w-105"],
        "w-105": ["105-door", "w-101", "w-102"],
        "w-102": ["102-door", "w-105", "w-106"],
        "w-106": ["106-door", "w-102", "w-103"],
        "w-103": ["103-door", "w-106", "w-lobby"],
        // 大厅垂直通道 (x=735, y:235→420→560)
        "w-lobby":     ["w-103", "w-lobby-mid"],
        "w-lobby-mid": ["w-lobby", "w-lobby-bot", "w-elev-crn"],
        "w-lobby-bot": ["w-lobby-mid", "w-ent", "w-elev-crn"],
        // 入口通道 (y=560)
        "w-ent":       ["w-lobby-bot", "school-gate"],
        "school-gate": ["w-ent"],
        // 电梯 / 楼梯 (大厅区域)
        "1f-elevator":  ["w-elev-crn"],
        "w-elev-crn":   ["1f-elevator", "w-lobby-mid", "w-lobby-bot"],
      },
    },
    {
      id: "2F",
      label: "2层",
      walls: [{ x: 50, y: 50, width: 800, height: 600 }],
      rooms: [
        // 上排 (y:80-220)
        { id: "201", label: "201实验室", x: 80, y: 80, width: 200, height: 140 },
        { id: "202", label: "202实验室", x: 310, y: 80, width: 200, height: 140 },
        { id: "203", label: "203机房", x: 540, y: 80, width: 180, height: 140 },
        // 下排 (y:250-390)
        { id: "204", label: "204教室", x: 80, y: 250, width: 180, height: 140 },
        { id: "205", label: "205会议室", x: 290, y: 250, width: 180, height: 140 },
        { id: "206", label: "教师办公室", x: 500, y: 250, width: 200, height: 140 },
      ],
      facilities: [
        { id: "elevator-2f", type: "elevator", icon: "🛗", label: "电梯", x: 650, y: 500 },
        { id: "stairs-2f", type: "stairs", icon: "🪜", label: "楼梯", x: 780, y: 500 },
      ],
      nodes: [
        { id: "2f-elevator", label: "2F电梯", x: 650, y: 500, selectable: true, icon: "🛗" },
        // 上排门：底边 y=220
        { id: "201-door", label: "201门口", x: 180, y: 220, selectable: true },
        { id: "202-door", label: "202门口", x: 410, y: 220, selectable: true },
        { id: "203-door", label: "203门口", x: 630, y: 220, selectable: true },
        // 下排门：顶边 y=250（朝向中央走廊）
        { id: "204-door", label: "204门口", x: 170, y: 250, selectable: true },
        { id: "205-door", label: "205门口", x: 380, y: 250, selectable: true },
        { id: "206-door", label: "206门口", x: 600, y: 250, selectable: true },
        // 拐点：中央走廊 y=235
        { id: "w2-204", x: 170, y: 235, selectable: false },
        { id: "w2-201", x: 180, y: 235, selectable: false },
        { id: "w2-205", x: 380, y: 235, selectable: false },
        { id: "w2-202", x: 410, y: 235, selectable: false },
        { id: "w2-206", x: 600, y: 235, selectable: false },
        { id: "w2-203", x: 630, y: 235, selectable: false },
        { id: "w2-lobby", x: 735, y: 235, selectable: false },
        { id: "w2-lobby-mid", x: 735, y: 420, selectable: false },
        { id: "w2-lobby-bot", x: 735, y: 560, selectable: false },
        { id: "w2-elev-crn", x: 735, y: 500, selectable: false },
      ],
      adjacency: {
        "201-door": ["w2-201"], "202-door": ["w2-202"], "203-door": ["w2-203"],
        "204-door": ["w2-204"], "205-door": ["w2-205"], "206-door": ["w2-206"],
        "w2-204": ["204-door", "w2-201"],
        "w2-201": ["201-door", "w2-204", "w2-205"],
        "w2-205": ["205-door", "w2-201", "w2-202"],
        "w2-202": ["202-door", "w2-205", "w2-206"],
        "w2-206": ["206-door", "w2-202", "w2-203"],
        "w2-203": ["203-door", "w2-206", "w2-lobby"],
        "w2-lobby":     ["w2-203", "w2-lobby-mid"],
        "w2-lobby-mid": ["w2-lobby", "w2-lobby-bot", "w2-elev-crn"],
        "w2-lobby-bot": ["w2-lobby-mid", "w2-elev-crn"],
        "2f-elevator":  ["w2-elev-crn"],
        "w2-elev-crn":  ["2f-elevator", "w2-lobby-mid", "w2-lobby-bot"],
      },
    },
  ],
  elevatorNodes: { B1: "b1-elevator", "1F": "1f-elevator", "2F": "2f-elevator" },
  crossFloorEdges: [
    ["b1-elevator", "1f-elevator"],
    ["1f-elevator", "2f-elevator"],
  ],
};

const museumData = {
  label: "博物馆导航模拟",
  description: "B1 / 1F / 2F 多层博物馆内部展厅导航演示",
  // 碰撞安全设计：所有边均为轴对齐，且在房间 BBox 之外的公共区域
  floors: [
    {
      id: "B1",
      label: "地下一层",
      walls: [{ x: 50, y: 50, width: 800, height: 600 }],
      // 走廊中心线: 水平脊线 y=245 (上排 max y=230 与下排 min y=260 之间)
      //            垂直脊线 x=435 (temp 右边界 430 与 vault 左边界 460 之间)
      rooms: [
        { id: "m-b1-archive", label: "档案库", x: 80, y: 80, width: 200, height: 150 },
        { id: "m-b1-storage", label: "文物储藏", x: 310, y: 80, width: 180, height: 150 },
        { id: "m-b1-restoration", label: "修复工作室", x: 520, y: 80, width: 200, height: 150 },
        { id: "m-b1-temp", label: "临时展厅", x: 80, y: 260, width: 350, height: 250 },
        { id: "m-b1-vault", label: "保险库", x: 460, y: 260, width: 250, height: 180 },
      ],
      facilities: [
        { id: "elevator-mb1", type: "elevator", icon: "🛗", label: "电梯", x: 650, y: 500 },
        { id: "stairs-mb1", type: "stairs", icon: "🪜", label: "楼梯", x: 780, y: 500 },
      ],
      nodes: [
        { id: "mb1-elevator", label: "B1电梯", x: 650, y: 500, selectable: true, icon: "🛗" },
        // 门在房间底边/顶边朝向最近走廊中心线
        { id: "mb1-temp-door", label: "临时展厅门口", x: 255, y: 260, selectable: true },
        { id: "mb1-vault-door", label: "保险库门口", x: 585, y: 260, selectable: true },
        { id: "mb1-archive-door", label: "档案库门口", x: 180, y: 230, selectable: true },
        // 拐点：严格在走廊中心线上
        { id: "mb1-sp-a", x: 180, y: 245, selectable: false },
        { id: "mb1-sp-t", x: 255, y: 245, selectable: false },
        { id: "mb1-sp-v", x: 585, y: 245, selectable: false },
        { id: "mb1-sp-gap", x: 435, y: 245, selectable: false },
        { id: "mb1-v-bot", x: 435, y: 500, selectable: false },
      ],
      adjacency: {
        "mb1-elevator":   ["mb1-v-bot"],
        "mb1-v-bot":      ["mb1-elevator", "mb1-sp-gap"],
        "mb1-sp-gap":     ["mb1-v-bot", "mb1-sp-t", "mb1-sp-v"],
        // 水平脊线 y=245
        "mb1-sp-a":       ["mb1-archive-door", "mb1-sp-t"],
        "mb1-sp-t":       ["mb1-temp-door", "mb1-sp-a", "mb1-sp-gap"],
        "mb1-sp-v":       ["mb1-vault-door", "mb1-sp-gap"],
        // 门口垂直连至脊线
        "mb1-archive-door": ["mb1-sp-a"],
        "mb1-temp-door":    ["mb1-sp-t"],
        "mb1-vault-door":   ["mb1-sp-v"],
      },
    },
    {
      id: "1F",
      label: "1层",
      walls: [{ x: 50, y: 50, width: 800, height: 600 }],
      // m-lobby 中央大厅已移除，留白为公共空间
      // 房间 BBox: ticket(80-180,80-200) shop(620-770,80-200)
      //            ancient(80-220,230-380) cafe(620-770,230-380)
      //            modern(80-330,410-610)
      // 安全公共区: 中央大厅 x∈[180,620] y∈[80,610]
      rooms: [
        { id: "m-ticket", label: "售票处", x: 80, y: 80, width: 100, height: 120 },
        { id: "m-shop", label: "纪念品店", x: 620, y: 80, width: 150, height: 120 },
        { id: "m-ancient", label: "古代文物展厅", x: 80, y: 230, width: 140, height: 150 },
        { id: "m-modern", label: "近现代艺术馆", x: 80, y: 410, width: 250, height: 200 },
        { id: "m-cafe", label: "咖啡休息区", x: 620, y: 230, width: 150, height: 150 },
      ],
      facilities: [
        { id: "entrance-museum", type: "entrance", icon: "🚪", label: "正门", x: 450, y: 620 },
        { id: "elevator-m1f", type: "elevator", icon: "🛗", label: "中央电梯", x: 650, y: 500 },
        { id: "stairs-m1f", type: "stairs", icon: "🪜", label: "楼梯", x: 780, y: 500 },
      ],
      nodes: [
        { id: "museum-entrance", label: "正门", x: 450, y: 620, selectable: true, icon: "🚪" },
        { id: "m1f-elevator", label: "1F中央电梯", x: 650, y: 500, selectable: true, icon: "🛗" },
        { id: "m-ticket-door", label: "售票处门口", x: 180, y: 140, selectable: true },
        { id: "m-shop-door", label: "纪念品店门口", x: 620, y: 140, selectable: true },
        { id: "m-ancient-door", label: "古代展厅门口", x: 220, y: 305, selectable: true },
        { id: "m-modern-door", label: "近现代艺术馆门口", x: 330, y: 510, selectable: true },
        { id: "m-cafe-door", label: "咖啡区门口", x: 620, y: 305, selectable: true },
        // 拐点：完全位于中央大厅安全区内 (x∈[180,620] y∈[80,610])
        { id: "mw-lobby-n", x: 400, y: 140, selectable: false },
        { id: "mw-lobby-c", x: 400, y: 305, selectable: false },
        { id: "mw-lobby-s", x: 400, y: 510, selectable: false },
        { id: "mw-ent", x: 450, y: 580, selectable: false },
        // 右侧通道
        { id: "mw-right", x: 650, y: 305, selectable: false },
        { id: "mw-elev", x: 650, y: 500, selectable: false },
      ],
      adjacency: {
        // 门 → 大厅边界（水平，均在安全区）
        "m-ticket-door": ["mw-lobby-n"],
        "m-shop-door":   ["mw-lobby-n"],
        "m-ancient-door":["mw-lobby-c"],
        "m-cafe-door":   ["mw-lobby-c", "mw-right"],
        "m-modern-door": ["mw-lobby-s"],
        // 大厅垂直通道 (x=400, 完全在安全区)
        "mw-lobby-n": ["m-ticket-door", "m-shop-door", "mw-lobby-c"],
        "mw-lobby-c": ["mw-lobby-n", "mw-lobby-s", "m-ancient-door", "m-cafe-door", "mw-right"],
        "mw-lobby-s": ["mw-lobby-c", "m-modern-door", "mw-ent"],
        // 入口
        "mw-ent": ["mw-lobby-s", "museum-entrance"],
        "museum-entrance": ["mw-ent"],
        // 右侧 → 电梯
        "mw-right": ["mw-lobby-c", "mw-elev"],
        "mw-elev": ["mw-right", "m1f-elevator"],
        "m1f-elevator": ["mw-elev"],
      },
    },
    {
      id: "2F",
      label: "2层",
      walls: [{ x: 50, y: 50, width: 800, height: 600 }],
      // 安全走廊: y∈[280,310] 中心线 y=295 (上下排房间之间)
      rooms: [
        { id: "m-history", label: "历史文物展厅", x: 80, y: 80, width: 250, height: 200 },
        { id: "m-art", label: "艺术珍品展厅", x: 360, y: 80, width: 250, height: 200 },
        { id: "m-science", label: "科技展厅", x: 80, y: 310, width: 250, height: 200 },
        { id: "m-special", label: "特展厅", x: 360, y: 310, width: 250, height: 200 },
        { id: "m-rest", label: "休息区", x: 650, y: 80, width: 150, height: 180 },
        { id: "m-library", label: "图书馆", x: 650, y: 290, width: 150, height: 180 },
      ],
      facilities: [
        { id: "elevator-m2f", type: "elevator", icon: "🛗", label: "电梯", x: 650, y: 500 },
        { id: "stairs-m2f", type: "stairs", icon: "🪜", label: "楼梯", x: 780, y: 500 },
      ],
      nodes: [
        { id: "m2f-elevator", label: "2F电梯", x: 650, y: 500, selectable: true, icon: "🛗" },
        { id: "m-history-door", label: "历史展厅门口", x: 205, y: 280, selectable: true },
        { id: "m-art-door", label: "艺术展厅门口", x: 485, y: 280, selectable: true },
        { id: "m-science-door", label: "科技展厅门口", x: 205, y: 310, selectable: true },
        { id: "m-special-door", label: "特展厅门口", x: 485, y: 310, selectable: true },
        { id: "m-rest-door", label: "休息区门口", x: 725, y: 260, selectable: true },
        { id: "m-library-door", label: "图书馆门口", x: 725, y: 380, selectable: true },
        // 拐点：中央走廊 y=295 (安全区 y∈[280,310])
        { id: "m2w-hist", x: 205, y: 295, selectable: false },
        { id: "m2w-art", x: 485, y: 295, selectable: false },
        { id: "m2w-mid", x: 345, y: 295, selectable: false },
        // 右侧通道 (x≥650, 安全区)
        { id: "m2w-right-n", x: 650, y: 260, selectable: false },
        { id: "m2w-right-c", x: 650, y: 295, selectable: false },
        { id: "m2w-right-s", x: 650, y: 500, selectable: false },
      ],
      adjacency: {
        // 上排门 → 走廊 (y:280→295)
        "m-history-door": ["m2w-hist"],
        "m-art-door": ["m2w-art"],
        // 下排门 → 走廊 (y:310→295)
        "m-science-door": ["m2w-hist"],
        "m-special-door": ["m2w-art"],
        // 中央走廊水平链 (y=295)
        "m2w-hist": ["m-history-door", "m-science-door", "m2w-mid"],
        "m2w-mid":  ["m2w-hist", "m2w-art"],
        "m2w-art":  ["m-art-door", "m-special-door", "m2w-mid", "m2w-right-c"],
        // 右侧通道
        "m2w-right-c": ["m2w-art", "m2w-right-n", "m2w-right-s"],
        "m2w-right-n": ["m2w-right-c", "m-rest-door"],
        "m2w-right-s": ["m2w-right-c", "m2f-elevator"],
        "m-rest-door": ["m2w-right-n"],
        "m-library-door": ["m2w-right-s"],
        "m2f-elevator": ["m2w-right-s"],
      },
    },
  ],
  elevatorNodes: { B1: "mb1-elevator", "1F": "m1f-elevator", "2F": "m2f-elevator" },
  crossFloorEdges: [
    ["mb1-elevator", "m1f-elevator"],
    ["m1f-elevator", "m2f-elevator"],
  ],
};

// ─── 工具函数：欧几里得距离 ───
function euclideanDist(a, b) {
  const dx = a.x - b.x;
  const dy = a.y - b.y;
  return Math.sqrt(dx * dx + dy * dy);
}

// ─── Dijkstra 最短路径算法（防循环增强版）───
// 在给定的邻接表上寻找从 startId 到 endId 的最短路径
// nodeMap: { [id]: { x, y } }  用于计算边权
// 返回节点 ID 数组（从起点到终点），找不到路径返回 null
// 安全机制: visited 集合严格去重，prev 链无环检测，结果去重
function dijkstra(adjacency, nodeMap, startId, endId) {
  if (startId === endId) return [startId];
  if (!adjacency[startId] || !adjacency[endId]) return null;

  // 确保起点终点都在邻接表键中
  const allKeys = new Set(Object.keys(adjacency));
  if (!allKeys.has(startId) || !allKeys.has(endId)) return null;

  const dist = {};
  const prev = {};
  const visited = new Set();   // 已处理节点（从 unvisited 中移除的）
  const unvisited = new Set(allKeys);

  for (const id of unvisited) {
    dist[id] = Infinity;
  }
  dist[startId] = 0;

  while (unvisited.size > 0) {
    // 找到未访问节点中距离最小的
    let minId = null;
    let minDist = Infinity;
    for (const id of unvisited) {
      if (dist[id] < minDist) {
        minDist = dist[id];
        minId = id;
      }
    }
    // 无可达节点或已到达终点
    if (minId === null) break;
    if (minId === endId) break;

    unvisited.delete(minId);
    visited.add(minId);

    const neighbors = adjacency[minId] || [];
    for (const neighborId of neighbors) {
      // 严格跳过已处理节点，防止回溯
      if (visited.has(neighborId)) continue;
      if (!unvisited.has(neighborId)) continue;
      const nA = nodeMap[minId];
      const nB = nodeMap[neighborId];
      if (!nA || !nB) continue;
      const alt = dist[minId] + euclideanDist(nA, nB);
      if (alt < dist[neighborId]) {
        dist[neighborId] = alt;
        prev[neighborId] = minId;
      }
    }
  }

  // 不可达
  if (dist[endId] === Infinity) return null;

  // 重建路径（带环检测安全阀）
  const path = [];
  const seen = new Set();
  let cur = endId;
  let safety = 0;
  const maxSteps = Object.keys(adjacency).length + 1;
  while (cur && safety < maxSteps) {
    if (seen.has(cur)) {
      // 检测到环！截断路径
      console.warn("[Dijkstra] Cycle detected at node:", cur, "truncating path");
      break;
    }
    seen.add(cur);
    path.unshift(cur);
    cur = prev[cur];
    safety++;
  }

  // 验证起点在路径首位
  if (path[0] !== startId) {
    console.warn("[Dijkstra] Path doesn't start at startId, prepending");
    path.unshift(startId);
  }

  // 去重连续重复节点
  const deduped = [path[0]];
  for (let i = 1; i < path.length; i++) {
    if (path[i] !== path[i - 1]) {
      deduped.push(path[i]);
    }
  }

  return deduped.length >= 2 ? deduped : null;
}

const currentSceneData = computed(() => {
  return currentScene.value === "school" ? schoolData : museumData;
});

const currentFloors = computed(() => currentSceneData.value.floors);

const displayFloorData = computed(() => {
  return currentSceneData.value.floors.find((f) => f.id === displayFloor.value);
});

const displayFloorWalls = computed(() => displayFloorData.value?.walls || []);
const displayFloorRooms = computed(() => displayFloorData.value?.rooms || []);
const displayFloorFacilities = computed(
  () => displayFloorData.value?.facilities || [],
);

// Build a flat list of all selectable nodes with floor info
const allSelectableNodes = computed(() => {
  const result = [];
  currentSceneData.value.floors.forEach((floor) => {
    floor.nodes.forEach((node) => {
      if (node.selectable) {
        result.push({ ...node, floorId: floor.id, floorLabel: floor.label });
      }
    });
  });
  return result;
});

const startNode = computed(() => {
  if (!selectedStartId.value) return null;
  return (
    allSelectableNodes.value.find((n) => n.id === selectedStartId.value) || null
  );
});

const endNode = computed(() => {
  if (!selectedEndId.value) return null;
  return (
    allSelectableNodes.value.find((n) => n.id === selectedEndId.value) || null
  );
});

// Auto-determine nav type based on start/end floors
const computedNavType = computed(() => {
  if (!startNode.value || !endNode.value) return null;
  return startNode.value.floorId === endNode.value.floorId
    ? "in-floor"
    : "cross-floor";
});

// ─── 智能楼层联动：选择起终点时自动切换地图视图 ───
// 监听起点变化 → 自动切换到起点所在楼层
watch(selectedStartId, (newId) => {
  if (!newId) return;
  if (isNavigating.value) stopNavigation();
  const node = allSelectableNodes.value.find((n) => n.id === newId);
  if (node && node.floorId !== displayFloor.value) {
    displayFloor.value = node.floorId;
  }
});

// 监听终点变化 → 若起点未选，则切换到终点楼层
watch(selectedEndId, (newId) => {
  if (!newId) return;
  if (isNavigating.value) stopNavigation();
  // 如果起点已选且同层，则不切换；否则切换以便预览
  if (!selectedStartId.value) {
    const node = allSelectableNodes.value.find((n) => n.id === newId);
    if (node && node.floorId !== displayFloor.value) {
      displayFloor.value = node.floorId;
    }
  }
});

const canNavigate = computed(() => {
  return (
    selectedStartId.value &&
    selectedEndId.value &&
    selectedStartId.value !== selectedEndId.value
  );
});

// Build the display path for current floor visualization
// ─── 构建全场景节点查找表 ───
function buildGlobalNodeMap(data) {
  const map = {};
  data.floors.forEach((floor) => {
    (floor.nodes || []).forEach((node) => {
      map[node.id] = { ...node, floorId: floor.id };
    });
  });
  return map;
}

// ─── 路径计算：基于 Dijkstra 寻路 ───
const computedRoutePath = computed(() => {
  if (!startNode.value || !endNode.value) return null;

  const startFloor = startNode.value.floorId;
  const endFloor = endNode.value.floorId;
  const data = currentSceneData.value;
  const globalNodeMap = buildGlobalNodeMap(data);

  if (startFloor === endFloor) {
    // 同层导航：在邻接图上跑 Dijkstra
    const floorData = data.floors.find((f) => f.id === startFloor);
    if (!floorData || !floorData.adjacency) return null;

    const pathIds = dijkstra(
      floorData.adjacency,
      globalNodeMap,
      startNode.value.id,
      endNode.value.id,
    );
    if (!pathIds || pathIds.length < 2) return null;

    return {
      startLabel: startNode.value.label,
      endLabel: endNode.value.label,
      floorTransitions: [],
      displayNodes: pathIds.map((id) => globalNodeMap[id]).filter(Boolean),
    };
  }

  // 跨层导航：起点层 → 电梯 → ... → 电梯 → 终点层
  const floorOrder = data.floors.map((f) => f.id);
  const startIdx = floorOrder.indexOf(startFloor);
  const endIdx = floorOrder.indexOf(endFloor);
  const goingUp = startIdx < endIdx;
  const floorsInRange = goingUp
    ? floorOrder.slice(startIdx, endIdx + 1)
    : floorOrder.slice(endIdx, startIdx + 1).reverse();

  const fullPathIds = [startNode.value.id];

  // 起点 → 起点层电梯
  const startFloorData = data.floors.find((f) => f.id === startFloor);
  const startElevId = data.elevatorNodes[startFloor];
  if (startFloorData?.adjacency && startElevId && startNode.value.id !== startElevId) {
    const seg = dijkstra(startFloorData.adjacency, globalNodeMap, startNode.value.id, startElevId);
    if (seg) fullPathIds.push(...seg.slice(1));
    else fullPathIds.push(startElevId);
  }

  // 跨层电梯跃迁
  floorsInRange.slice(1).forEach((floorId) => {
    fullPathIds.push(data.elevatorNodes[floorId]);
  });

  // 终点层电梯 → 终点
  const endFloorData = data.floors.find((f) => f.id === endFloor);
  const endElevId = data.elevatorNodes[endFloor];
  if (endFloorData?.adjacency && endElevId && endNode.value.id !== endElevId) {
    const seg = dijkstra(endFloorData.adjacency, globalNodeMap, endElevId, endNode.value.id);
    if (seg) fullPathIds.push(...seg.slice(1));
    else fullPathIds.push(endNode.value.id);
  }

  const floorTransitions = floorsInRange.map((f) => {
    const fl = data.floors.find((ff) => ff.id === f);
    return fl?.label || f;
  });

  return {
    startLabel: startNode.value.label,
    endLabel: endNode.value.label,
    floorTransitions,
    displayNodes: fullPathIds.map((id) => globalNodeMap[id]).filter(Boolean),
  };
});

const displayPath = computed(() => {
  if (!computedRoutePath.value) return [];
  return computedRoutePath.value.displayNodes;
});

// 路径链展示节点（过滤掉隐藏拐点，只显示有标签的节点）
const chainDisplayNodes = computed(() => {
  if (!computedRoutePath.value) return [];
  return computedRoutePath.value.displayNodes.filter((n) => n.label);
});

const navStatusIcon = computed(() => {
  if (!canNavigate.value) return "📍";
  const idx = currentPointerIndex.value;
  if (idx === 0) return "🚀";
  if (idx >= displayPath.value.length - 1) return "🏁";
  return computedNavType.value === "cross-floor" ? "🛗" : "🚶";
});

const navStatusText = computed(() => {
  if (!canNavigate.value || displayPath.value.length === 0)
    return "准备出发...";
  const idx = currentPointerIndex.value;
  if (idx === 0) return "正在出发...";
  if (idx >= displayPath.value.length - 1) return "已到达目的地!";
  const nextNode = displayPath.value[idx + 1];
  return `前往: ${nextNode?.label || "途经拐点"}`;
});

// 导航时当前所在节点 ID（用于路径链高亮）
const chainActiveNodeId = computed(() => {
  if (!isNavigating.value || currentPointerIndex.value >= displayPath.value.length)
    return null;
  return displayPath.value[currentPointerIndex.value]?.id || null;
});

const pointerRadiusValues = "8;12;8";
const pointerOpacityValues = "1;0.5;1";

function switchScene(sceneId) {
  currentScene.value = sceneId;
  displayFloor.value = currentSceneData.value.floors[0].id;
  selectedStartId.value = "";
  selectedEndId.value = "";
  stopNavigation();
}

// 点击路径节点时切换到对应楼层
function switchToNodeFloor(node) {
  if (isNavigating.value) stopNavigation();
  displayFloor.value = node.floorId;
}

function startNavigation() {
  if (!canNavigate.value || displayPath.value.length === 0) return;

  isNavigating.value = true;
  showPointer.value = true;
  currentPointerIndex.value = 0;

  const startN = displayPath.value[0];
  pointerX.value = startN.x;
  pointerY.value = startN.y;

  // 始终先切换到起点所在楼层，确保用户看到出发画面
  displayFloor.value = startNode.value.floorId;

  animateStep(0);
}

function animateStep(stepIndex) {
  if (!navigationTimer.value && !isNavigating.value) return;

  const totalSteps = displayPath.value.length - 1;
  if (stepIndex >= totalSteps) {
    setTimeout(() => stopNavigation(), 1200);
    return;
  }

  const from = displayPath.value[stepIndex];
  const to = displayPath.value[stepIndex + 1];

  if (from.floorId !== to.floorId) {
    displayFloor.value = to.floorId;
  }

  const duration = 800;
  const startTime = Date.now();

  function animate() {
    const elapsed = Date.now() - startTime;
    const progress = Math.min(elapsed / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);

    pointerX.value = from.x + (to.x - from.x) * eased;
    pointerY.value = from.y + (to.y - from.y) * eased;
    currentPointerIndex.value = stepIndex;

    if (progress < 1) {
      requestAnimationFrame(animate);
    } else {
      currentPointerIndex.value = stepIndex + 1;
      navigationTimer.value = setTimeout(() => {
        if (isNavigating.value) {
          animateStep(stepIndex + 1);
        }
      }, 400);
    }
  }

  requestAnimationFrame(animate);
}

function stopNavigation() {
  if (navigationTimer.value) {
    clearTimeout(navigationTimer.value);
    navigationTimer.value = null;
  }
  isNavigating.value = false;
  showPointer.value = false;
  currentPointerIndex.value = 0;
}

onBeforeUnmount(() => {
  stopNavigation();
});
</script>

<style scoped>
.indoor-demo-page {
  display: flex;
  height: 100vh;
  background: linear-gradient(135deg, #0a0a1a 0%, #1a1a3e 50%, #0f0f2f 100%);
  color: #e0e7ff;
  font-family:
    "Inter",
    -apple-system,
    BlinkMacSystemFont,
    "Segoe UI",
    sans-serif;
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
  background: linear-gradient(
    135deg,
    rgba(6, 182, 212, 0.2),
    rgba(59, 130, 246, 0.2)
  );
  border: 1px solid rgba(6, 182, 212, 0.4);
  color: #67e8f9;
}

.nav-type-badge.cross-floor {
  background: linear-gradient(
    135deg,
    rgba(139, 92, 246, 0.2),
    rgba(6, 182, 212, 0.2)
  );
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

</style>
