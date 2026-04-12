<template>
  <div class="trip-detail-page">
    <!-- 顶部导航 -->
    <header class="page-header">
      <button class="back-btn" @click="goBack">
        <span class="back-icon">←</span>
      </button>
      <h1 class="page-title">{{ tripTitle }}</h1>
      <button class="action-btn" @click="saveTrip">
        {{ isFromAI ? "保存到我的行程" : "保存" }}
      </button>
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
              <div
                class="spot-card"
                title="按住拖动可调整顺序"
                @click="focusSpot(spot)"
              >
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
                    <span class="spot-rating"
                      >⭐ {{ spot.rating?.toFixed(1) || "4.5" }}</span
                    >
                    <span class="spot-duration"
                      >⏱️ {{ spot.duration || "2 小时" }}</span
                    >
                  </div>
                  <div class="spot-tags" v-if="spot.tags?.length">
                    <span
                      v-for="tag in spot.tags.slice(0, 2)"
                      :key="tag"
                      class="tag"
                      >{{ tag }}</span
                    >
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

        <!-- 算法控制面板 -->
        <div class="algo-controls">
          <!-- 交通方式 -->
          <div class="transport-group">
            <button
              v-for="t in transportOptions"
              :key="t.value"
              class="transport-btn"
              :class="{ active: currentTransport === t.value }"
              @click="switchTransport(t.value)"
            >{{ t.label }}</button>
          </div>
          <!-- 拥挤度 -->
          <div class="congestion-group">
            <span class="congestion-label">拥挤度</span>
            <input
              type="range" min="0" max="0.9" step="0.1"
              v-model.number="congestionLevel"
              @change="updateMapRoute"
              class="congestion-slider"
            />
            <span class="congestion-value">{{ Math.round(congestionLevel * 100) }}%</span>
          </div>
          <!-- TSP 最优顺序 -->
          <button class="map-btn tsp-btn" @click="runTSP">
            <span>🔀</span> 最优顺序
          </button>
        </div>

        <!-- 地图控制按钮 -->
        <div class="map-controls">
          <button class="map-btn" @click="fitView">
            <span>🎯</span> 适应视图
          </button>
          <button class="map-btn" @click="toggleTraffic">
            <span>🚦</span> {{ showTraffic ? "隐藏" : "显示" }}路况
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
          <div class="route-stat" v-if="routeInfo.orderedNames">
            <span class="route-icon">🗺️</span>
            <span>最优顺序: {{ routeInfo.orderedNames.join(' → ') }}</span>
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
              :class="{ 'already-added': usedSpotIds.has(spot.id) }"
              @click="!usedSpotIds.has(spot.id) && addSpot(spot)"
            >
              <img :src="spot.image" :alt="spot.name" class="spot-thumb" />
              <div class="spot-brief">
                <h4>{{ spot.name }}</h4>
                <span class="spot-rating-small"
                  >⭐ {{ spot.rating?.toFixed(1) || "4.5" }}</span
                >
              </div>
              <span
                class="add-icon"
                :class="{ disabled: usedSpotIds.has(spot.id) }"
              >
                {{ usedSpotIds.has(spot.id) ? "✓" : "+" }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, shallowRef, onMounted, computed, watch, nextTick } from "vue";
import { useRouter, useRoute } from "vue-router";
import { ElMessage } from "element-plus";
import draggable from "vuedraggable";
import AMapLoader from "@amap/amap-jsapi-loader";
import { buildGraphFromSpots, haversineDistance, TransportType } from "@/pathfinder/graph.js";
import { dijkstra, reconstructPath } from "@/pathfinder/dijkstra.js";
import { solveTSP, buildCostMatrix } from "@/pathfinder/tsp.js";

const router = useRouter();
const route = useRoute();

// 数据
const city = ref("");
const days = ref(3);
const preferences = ref([]);
const selectedSpots = ref([]);
const allSpots = ref([]);
const cityAllSpots = ref([]); // 该城市的所有景点（用于添加景点弹窗）
const selectedDay = ref(1);
const showModal = ref(false);
const searchQuery = ref("");
const routeInfo = ref(null);
const showTraffic = ref(false);
const isFromAI = ref(false); // 标记是否从AI助手跳转过来

// 每天的景点分配
const daySpotsMap = ref({});

// 高德地图相关
const map = shallowRef(null);
let markers = [];
let polylines = [];
let trafficLayer = null;
let drivingPlugin = null;

// 算法控制状态
const currentTransport = ref(TransportType.WALK);
const congestionLevel = ref(0.2);
const transportOptions = [
  { label: "🚶 步行", value: TransportType.WALK },
  { label: "🚲 自行车", value: TransportType.BIKE },
  { label: "🛵 电瓶车", value: TransportType.SCOOTER },
];

// 偏好映射
const prefMap = {
  must_visit: "必玩景点",
  history: "历史文化",
  landmark: "地标建筑",
  heritage: "非遗体验",
  scenery: "风景名胜",
  food: "逛吃逛喝",
  museum: "博物展览",
  citywalk: "citywalk",
  photo: "拍照出片",
  local_life: "市井烟火",
  leisure: "休闲娱乐",
};

const preferencesText = computed(() => {
  return preferences.value
    .map((p) => prefMap[p] || p)
    .slice(0, 2)
    .join("、");
});

const tripTitle = computed(() => {
  return `${city.value}${days.value}日${preferencesText.value || "游"}`;
});

// 当前选中的天的景点列表
const currentDaySpots = computed({
  get() {
    return daySpotsMap.value[selectedDay.value] || [];
  },
  set(value) {
    // 使用 Vue 的响应式方式更新数组 - 必须创建新对象触发响应式
    const dayKey = selectedDay.value;
    daySpotsMap.value = {
      ...daySpotsMap.value,
      [dayKey]: [...value]
    };
  },
});

// 获取某天的景点
const getDaySpots = (day) => {
  return daySpotsMap.value[day] || [];
};

// 总景点数
const totalSpots = computed(() => {
  return Object.values(daySpotsMap.value).flat().length;
});

// 获取所有已添加的景点ID
const usedSpotIds = computed(() => {
  const usedIds = new Set();
  for (let day = 1; day <= days.value; day++) {
    const daySpots = daySpotsMap.value[day] || [];
    daySpots.forEach((spot) => usedIds.add(spot.id));
  }
  return usedIds;
});

// 可添加的景点（该城市所有景点，用于显示）
const availableSpots = computed(() => {
  return cityAllSpots.value;
});

// 过滤后的可添加景点
const filteredAvailableSpots = computed(() => {
  if (!searchQuery.value) return availableSpots.value;
  const query = searchQuery.value.toLowerCase();
  return availableSpots.value.filter((spot) =>
    spot.name.toLowerCase().includes(query),
  );
});

// 加载数据
onMounted(async () => {
  // 检查是否从AI助手跳转过来（URL包含 /trip/ 路径参数）
  const tripId = route.params.id;
  const fromAI = route.query.from === "ai";

  console.log("TripDetail onMounted:", { tripId, fromAI, query: route.query });

  if (tripId && tripId !== "new") {
    isFromAI.value = fromAI;

    // 检查 ID 格式，如果是字符串格式（如 trip_xxx 或 ai_temp_xxx），从 localStorage 读取
    if (typeof tripId === "string" && (tripId.startsWith("trip_") || tripId.startsWith("ai_temp_"))) {
      console.log("Loading trip from localStorage:", tripId);
      
      // 对于 ai_temp_ 开头的临时行程，从 currentTrip 读取
      let tripData = null;
      if (tripId.startsWith("ai_temp_")) {
        const currentTrip = JSON.parse(localStorage.getItem("currentTrip") || "{}");
        if (currentTrip.id === tripId) {
          tripData = currentTrip;
        }
      } else {
        // 对于 trip_ 开头的行程，从 savedTrips 读取
        const savedTrips = JSON.parse(localStorage.getItem("savedTrips") || "[]");
        tripData = savedTrips.find((t) => t.id === tripId);
      }

      if (tripData) {
        city.value = tripData.city;
        days.value = tripData.days;
        preferences.value = tripData.preferences || [];
        tripTitle.value =
          tripData.title || `${tripData.city}${tripData.days}日游`;

        // 恢复每天的景点分配
        console.log('从localStorage加载的tripData:', tripData);
        console.log('daySpots:', tripData.daySpots);
        if (tripData.daySpots) {
          daySpotsMap.value = tripData.daySpots;
          allSpots.value = Object.values(tripData.daySpots).flat();
          console.log('设置后的daySpotsMap:', daySpotsMap.value);
          console.log('allSpots:', allSpots.value);

          // 检查景点是否有坐标，如果没有，重新从 API 获取
          await ensureSpotsHaveCoordinates();
        } else {
          console.warn('tripData.daySpots 为空');
        }
      } else {
        alert("行程数据不存在");
      }
    } else {
      // 从后端加载行程数据（数字ID）
      try {
        console.log("Fetching trip data from API for ID:", tripId);
        const response = await fetch(
          `http://localhost:8000/api/trips/${tripId}`,
        );
        console.log("Trip API response status:", response.status);
        if (response.ok) {
          const tripData = await response.json();
          console.log("Trip data:", tripData);
          console.log("Schedules:", tripData.schedules);
          city.value = tripData.destination || "北京";
          days.value = tripData.total_days || 3;
          preferences.value = tripData.travel_preferences || [];

          // 加载行程中的景点
          if (tripData.schedules && tripData.schedules.length > 0) {
            console.log(`Loading ${tripData.schedules.length} schedules`);

            // 先加载该城市的所有景点数据，获取真实评分等信息
            const spotsResponse = await fetch(
              `http://localhost:8000/api/spots/recommend?city=${encodeURIComponent(city.value)}&limit=100`,
            );
            const spotsData = await spotsResponse.json();
            const spotsMap = {};
            if (spotsData.spots) {
              spotsData.spots.forEach((spot) => {
                spotsMap[spot.id] = spot;
              });
            }

            // 将景点分配到各天
            const spotsByDay = {};
            for (let i = 1; i <= days.value; i++) {
              spotsByDay[i] = [];
            }

            tripData.schedules.forEach((schedule) => {
              console.log("Processing schedule:", schedule);
              const dayNum = schedule.day_number || 1;
              if (!spotsByDay[dayNum]) spotsByDay[dayNum] = [];

              // 从景点API数据中获取完整信息
              const spotDetail = spotsMap[schedule.spot_id];

              spotsByDay[dayNum].push({
                id: schedule.spot_id,
                name: schedule.spot_name || spotDetail?.name || "未知景点",
                image:
                  schedule.spot_image ||
                  spotDetail?.images?.[0] ||
                  "/images/default-spot.jpg",
                rating: spotDetail?.rating || schedule.spot_rating || 0,
                duration: "2 小时",
                tags: spotDetail?.tags || [],
                location:
                  schedule.spot_location_lng && schedule.spot_location_lat
                    ? [schedule.spot_location_lng, schedule.spot_location_lat]
                    : spotDetail?.location_lng && spotDetail?.location_lat
                      ? [spotDetail.location_lng, spotDetail.location_lat]
                      : spotDetail?.location || null,
              });
            });

            daySpotsMap.value = spotsByDay;
            allSpots.value = Object.values(spotsByDay).flat();
            console.log("daySpotsMap:", daySpotsMap.value);
          } else {
            console.log("No schedules found, initializing empty trip");
            // 没有景点数据，初始化空行程（不加载默认景点）
            const spotsByDay = {};
            for (let i = 1; i <= days.value; i++) {
              spotsByDay[i] = [];
            }
            daySpotsMap.value = spotsByDay;
            allSpots.value = [];
          }
        } else {
          // API调用失败，显示错误
          console.error("API调用失败:", response.status);
          alert("加载行程失败，请刷新页面重试");
        }
      } catch (error) {
        console.error("加载行程失败:", error);
        alert("加载行程失败，请刷新页面重试");
      }
    }
  } else if (
    localStorage.getItem("currentTrip") &&
    route.query.id &&
    !route.params.id
  ) {
    // 从行程列表进入（没有 path 参数 id，只有 query 参数 id），读取保存的行程数据
    const currentTrip = JSON.parse(localStorage.getItem("currentTrip"));
    city.value = currentTrip.city;
    days.value = currentTrip.days;
    preferences.value = currentTrip.preferences || [];

    // 恢复每天的景点分配
    if (currentTrip.daySpots) {
      daySpotsMap.value = currentTrip.daySpots;
      allSpots.value = Object.values(currentTrip.daySpots).flat();

      // 检查景点是否有坐标，如果没有，重新从 API 获取
      await ensureSpotsHaveCoordinates();
    }
  } else {
    // 从创建流程进入
    city.value = route.query.city || localStorage.getItem("tripCity") || "北京";
    days.value =
      parseInt(route.query.days) ||
      parseInt(localStorage.getItem("tripDays")) ||
      3;

    const prefStr =
      route.query.preferences || localStorage.getItem("tripPreferences") || "";
    preferences.value = prefStr.split(",").filter((p) => p);

    // 从 localStorage 读取已选择的景点（现在是完整的对象数组）
    const spotsStr = localStorage.getItem("selectedSpots") || "[]";
    selectedSpots.value = JSON.parse(spotsStr);

    // 如果有已选择的景点，直接使用它们
    if (selectedSpots.value.length > 0) {
      allSpots.value = selectedSpots.value;
      // 平均分配景点到各天
      distributeSpotsToDays();
    } else {
      // 加载所有景点数据
      await loadAllSpots();
      // 平均分配景点到各天
      distributeSpotsToDays();
    }
  }

  // 初始化地图
  nextTick(() => {
    initMap();
  });
});

// 确保所有景点都有坐标（从 API 获取）
const ensureSpotsHaveCoordinates = async () => {
  const spotsToUpdate = [];

  // 收集所有缺少坐标的景点
  Object.values(daySpotsMap.value).forEach((daySpots) => {
    daySpots.forEach((spot) => {
      console.log("检查景点坐标:", spot.name, "location:", spot.location);
      if (!spot.location && spot.id) {
        spotsToUpdate.push(spot);
      }
    });
  });

  if (spotsToUpdate.length === 0) {
    console.log("所有景点已有坐标，无需更新");
    return;
  }

  console.log(`需要更新 ${spotsToUpdate.length} 个景点的坐标`);

  try {
    // 从 API 获取景点详情
    const response = await fetch(
      `http://localhost:8000/api/spots/recommend?city=${encodeURIComponent(city.value)}&limit=100`,
    );

    if (!response.ok) {
      throw new Error("API 请求失败");
    }

    const data = await response.json();
    const spotsFromAPI = data.spots || data;

    console.log("API 返回的景点数量:", spotsFromAPI.length);

    // 更新景点坐标
    let updatedCount = 0;
    spotsToUpdate.forEach((spot) => {
      // 先尝试通过 ID 匹配
      let apiSpot = spotsFromAPI.find((s) => s.id === spot.id);

      // 如果 ID 匹配失败，尝试通过名称匹配
      if (!apiSpot) {
        apiSpot = spotsFromAPI.find((s) => s.name === spot.name);
        if (apiSpot) {
          console.log(`通过名称匹配到景点 ${spot.name}`);
        }
      }

      if (apiSpot) {
        console.log(
          `找到景点 ${spot.name}:`,
          `lng=${apiSpot.location_lng}, lat=${apiSpot.location_lat}`,
        );
        if (apiSpot.location_lng && apiSpot.location_lat) {
          spot.location = [apiSpot.location_lng, apiSpot.location_lat];
          updatedCount++;
        }
      } else {
        console.warn(`未找到景点 ${spot.name} 的 API 数据`);
      }
    });

    console.log(`更新了 ${updatedCount} 个景点的坐标`);

    // 重新生成 daySpotsMap 以触发响应式更新
    const newDaySpotsMap = {};
    Object.entries(daySpotsMap.value).forEach(([day, spots]) => {
      newDaySpotsMap[day] = [...spots];
    });
    daySpotsMap.value = newDaySpotsMap;

    // 同时更新 localStorage 中的行程数据
    const tripId = route.query.tripId || localStorage.getItem("currentTripId");
    if (tripId) {
      const savedTrips = JSON.parse(localStorage.getItem("savedTrips") || "[]");
      const tripIndex = savedTrips.findIndex((t) => t.tripId === tripId);
      if (tripIndex !== -1) {
        savedTrips[tripIndex].daySpots = daySpotsMap.value;
        localStorage.setItem("savedTrips", JSON.stringify(savedTrips));
        console.log("已更新 localStorage 中的景点坐标");
      }
    }

    // 更新地图
    nextTick(() => {
      console.log("调用 updateMapRoute");
      updateMapRoute();
    });
  } catch (error) {
    console.error("获取景点坐标失败:", error);
  }
};

// 加载所有景点
const loadAllSpots = async () => {
  try {
    const response = await fetch(
      `/api/spots?city=${encodeURIComponent(city.value)}`,
    );
    const data = await response.json();
    if (data && data.length > 0) {
      allSpots.value = data;
    } else {
      // 使用模拟数据
      allSpots.value = getMockSpots();
    }
  } catch (error) {
    console.error("加载景点失败:", error);
    allSpots.value = getMockSpots();
  }
};

// 模拟景点数据
const getMockSpots = () => {
  const baseSpots = [
    {
      id: 1,
      name: "故宫博物院",
      rating: 4.9,
      favorites: 12580,
      tags: ["history", "landmark", "must_visit"],
      duration: "4小时",
      image: "/images/spots/beijing/beijing_gugong_bowuyuan.jpg",
      location: [116.397477, 39.903738],
    },
    {
      id: 2,
      name: "天安门广场",
      rating: 4.8,
      favorites: 9876,
      tags: ["landmark", "must_visit", "photo"],
      duration: "1小时",
      image: "/images/spots/beijing/beijing_tiananmen_guangchang.jpg",
      location: [116.397477, 39.905489],
    },
    {
      id: 3,
      name: "颐和园",
      rating: 4.8,
      favorites: 8654,
      tags: ["scenery", "history", "must_visit"],
      duration: "4小时",
      image: "/images/spots/beijing/beijing_yiheyuan.jpg",
      location: [116.275467, 39.994867],
    },
    {
      id: 4,
      name: "八达岭长城",
      rating: 4.9,
      favorites: 11234,
      tags: ["scenery", "history", "must_visit"],
      duration: "5小时",
      image: "/images/spots/beijing/beijing_badaling_changcheng.jpg",
      location: [116.016953, 40.353469],
    },
    {
      id: 5,
      name: "天坛公园",
      rating: 4.7,
      favorites: 6543,
      tags: ["history", "scenery"],
      duration: "2小时",
      image: "/images/spots/beijing/beijing_tiantan_gongyuan.jpg",
      location: [116.406588, 39.883365],
    },
    {
      id: 6,
      name: "南锣鼓巷",
      rating: 4.5,
      favorites: 7890,
      tags: ["food", "local_life", "citywalk"],
      duration: "2小时",
      image: "/images/spots/beijing/beijing_nanluoguxiang.jpg",
      location: [116.403147, 39.937243],
    },
    {
      id: 7,
      name: "798艺术区",
      rating: 4.6,
      favorites: 5432,
      tags: ["photo", "leisure", "art"],
      duration: "3小时",
      image: "/images/spots/beijing/beijing_798_art.jpg",
      location: [116.500876, 39.985432],
    },
    {
      id: 8,
      name: "什刹海",
      rating: 4.6,
      favorites: 6789,
      tags: ["scenery", "food", "local_life"],
      duration: "2小时",
      image: "/images/spots/beijing/beijing_shichahai.jpg",
      location: [116.387654, 39.94321],
    },
    {
      id: 9,
      name: "圆明园",
      rating: 4.5,
      favorites: 4567,
      tags: ["history", "scenery"],
      duration: "3小时",
      image: "/images/spots/beijing/beijing_yuanmingyuan.jpg",
      location: [116.298765, 40.009876],
    },
  ];

  // 根据已选择的景点ID过滤，如果没有则使用全部
  if (selectedSpots.value.length > 0) {
    const selectedIds = selectedSpots.value.map((s) => s.id || s);
    return baseSpots.filter((s) => selectedIds.includes(s.id));
  }
  return baseSpots;
};

// 平均分配景点到各天
const distributeSpotsToDays = () => {
  const spots = [...allSpots.value];
  const spotsPerDay = Math.ceil(spots.length / days.value);

  // 创建新的 daySpotsMap 对象以触发响应式
  const newDaySpotsMap = { ...daySpotsMap.value };
  for (let day = 1; day <= days.value; day++) {
    const startIndex = (day - 1) * spotsPerDay;
    const endIndex = Math.min(startIndex + spotsPerDay, spots.length);
    newDaySpotsMap[day] = spots.slice(startIndex, endIndex);
  }
  daySpotsMap.value = newDaySpotsMap;
};

// 初始化高德地图
const initMap = () => {
  const amapKey = import.meta.env.VITE_AMAP_KEY;
  const securityKey = import.meta.env.VITE_AMAP_SECURITY_KEY;

  // 若配置了安全密钥，则在加载前注入（高德 2.0+ 要求）
  if (securityKey) {
    window._AMapSecurityConfig = { securityJsCode: securityKey };
  }

  AMapLoader.load({
    key: amapKey,
    version: "2.0",
    plugins: ["AMap.ToolBar", "AMap.Scale", "AMap.Walking", "AMap.Riding"],
  })
    .then((AMap) => {
      window.AMap = AMap;

      map.value = new AMap.Map("amap-container", {
        zoom: 12,
        center: getCityCenter(),
        viewMode: "2D",
      });

      map.value.addControl(new AMap.ToolBar());
      map.value.addControl(new AMap.Scale());

      updateMapRoute();
    })
    .catch((err) => {
      console.error("高德地图加载失败:", err);
    });
};

// 获取城市中心坐标
const getCityCenter = () => {
  const cityCenters = {
    北京: [116.397477, 39.903738],
    上海: [121.473667, 31.230525],
    广州: [113.264434, 23.129163],
    深圳: [114.057868, 22.543099],
    杭州: [120.15507, 30.274085],
    成都: [104.066541, 30.572269],
    西安: [108.93977, 34.341574],
    南京: [118.796877, 32.060255],
    武汉: [114.305539, 30.593099],
    长沙: [112.938823, 28.228208],
    重庆: [106.551557, 29.563009],
    厦门: [118.089425, 24.479833],
    青岛: [120.382642, 36.067082],
    苏州: [120.585316, 31.298886],
    桂林: [110.299621, 25.274215],
    丽江: [100.228975, 26.855571],
    大理: [100.267638, 25.60689],
    黄山: [118.315582, 29.71477],
    九寨沟: [104.246246, 33.111847],
    张家界: [110.479648, 29.117238],
    三亚: [109.511909, 18.252847],
  };

  const cityName = city.value?.trim() || "";
  console.log("当前城市:", cityName);

  if (cityCenters[cityName]) {
    return cityCenters[cityName];
  }

  for (const [key, value] of Object.entries(cityCenters)) {
    if (cityName.includes(key) || key.includes(cityName)) {
      return value;
    }
  }

  return [116.397477, 39.903738];
};

// 获取有效经纬度坐标
const getValidLngLat = (spot) => {
  if (!spot) {
    console.error("spot 参数无效:", spot);
    return null;
  }

  let lng = null;
  let lat = null;

  if (spot.location_lng !== undefined && spot.location_lat !== undefined) {
    lng = spot.location_lng;
    lat = spot.location_lat;
  } else if (
    spot.location &&
    Array.isArray(spot.location) &&
    spot.location.length === 2
  ) {
    lng = spot.location[0];
    lat = spot.location[1];
  }

  if (lng === null || lat === null) {
    console.error(`景点 "${spot.name}" 缺少有效坐标，已跳过:`, spot);
    return null;
  }

  if (lng < -180 || lng > 180 || lat < -90 || lat > 90) {
    console.error(
      `景点 "${spot.name}" 坐标超出有效范围 [lng:${lng}, lat:${lat}]，已跳过`,
    );
    return null;
  }

  return [lng, lat];
};

/**
 * 用高德插件获取两点间真实道路坐标折点（仅获取坐标，不做导航决策）
 * 步行用 AMap.Walking，自行车/电瓶车用 AMap.Riding
 * @returns {Promise<[number,number][]>} 坐标数组
 */
const getRoadPath = (from, to) => {
  return new Promise((resolve) => {
    const AMap = window.AMap;
    const useRiding = currentTransport.value !== TransportType.WALK;

    const extractCoords = (steps) => {
      const coords = [];
      (steps || []).forEach((step) => {
        (step.path || []).forEach((p) => coords.push([p.lng, p.lat]));
      });
      return coords;
    };

    if (useRiding) {
      const riding = new AMap.Riding({ map: null });
      riding.search(from, to, (status, result) => {
        console.log("[Riding] status:", status);
        console.log("[Riding] result keys:", result ? Object.keys(result) : result);
        if (status === "complete") {
          // 尝试所有可能的路由字段
          const route = result.rideRoutes?.[0] ?? result.routes?.[0];
          console.log("[Riding] route keys:", route ? Object.keys(route) : route);
          // AMap 2.0 Riding 的步骤字段可能是 rides 而非 steps
          const steps = route?.rides ?? route?.steps ?? [];
          console.log("[Riding] steps length:", steps.length, "steps[0]:", steps[0]);
          // 每个 ride/step 的坐标可能直接在 path 或 passedPolyline
          const coords = [];
          steps.forEach((s) => {
            const pts = s.path ?? s.passedPolyline ?? [];
            pts.forEach((p) => coords.push([p.lng ?? p[0], p.lat ?? p[1]]));
          });
          console.log("[Riding] coords length:", coords.length);
          resolve(coords.length > 0 ? coords : [from, to]);
        } else {
          console.warn("[Riding] 失败:", status, result);
          resolve([from, to]);
        }
      });
    } else {
      const walking = new AMap.Walking({ map: null });
      walking.search(from, to, (status, result) => {
        if (status === "complete" && result.routes?.[0]) {
          const coords = extractCoords(result.routes[0].steps || []);
          resolve(coords.length > 0 ? coords : [from, to]);
        } else {
          console.warn("[Walking] 失败，降级直线:", status, result);
          resolve([from, to]);
        }
      });
    }
  });
};

/**
 * 更新地图路线
 * 决策层：自研 Dijkstra 算法（权重 = 距离 / 速度×(1-拥挤度)）
 * 可视化层：高德插件获取真实道路坐标折点
 */
const updateMapRoute = async () => {
  if (!map.value) return;

  map.value.clearMap();
  markers = [];
  polylines = [];

  const spots = currentDaySpots.value;
  if (spots.length === 0) return;

  const validSpots = spots
    .map((s) => { const pos = getValidLngLat(s); return pos ? { ...s, location: pos } : null; })
    .filter(Boolean);

  if (validSpots.length === 0) return;

  // 绘制景点编号标记
  validSpots.forEach((spot, index) => {
    const marker = new AMap.Marker({
      position: spot.location,
      content: `<div class="custom-marker">${index + 1}</div>`,
      offset: new AMap.Pixel(-15, -30),
      zIndex: 110,
    });
    marker.setMap(map.value);
    markers.push(marker);

    const infoWindow = new AMap.InfoWindow({
      content: `<div style="padding:10px"><h4>${spot.name}</h4><p>⭐ ${spot.rating?.toFixed(1) || "4.5"}</p></div>`,
      offset: new AMap.Pixel(0, -30),
    });
    marker.on("click", () => infoWindow.open(map.value, marker.getPosition()));
  });

  if (validSpots.length < 2) {
    routeInfo.value = null;
    nextTick(() => map.value.setFitView(markers));
    return;
  }

  // ── 自研算法决策层 ──
  // 构建图，注入当前交通方式和拥挤度
  const graph = buildGraphFromSpots(validSpots, currentTransport.value);
  for (const edges of graph.adjList.values()) {
    edges.forEach((e) => { e.congestion = congestionLevel.value; });
  }

  // Dijkstra 计算各段权重（时间代价），用于 routeInfo 统计
  let totalDistance = 0;
  let totalDuration = 0;

  for (let i = 0; i < validSpots.length - 1; i++) {
    const { dist } = dijkstra(graph, validSpots[i].id);
    const segCost = dist.get(validSpots[i + 1].id) ?? 0;
    totalDuration += segCost;
    totalDistance += haversineDistance(validSpots[i].location, validSpots[i + 1].location);
  }

  // ── 可视化层：高德插件获取真实道路折线坐标 ──
  // 逐段异步获取，然后拼接绘制
  const segPromises = [];
  for (let i = 0; i < validSpots.length - 1; i++) {
    segPromises.push(getRoadPath(validSpots[i].location, validSpots[i + 1].location));
  }

  const segments = await Promise.all(segPromises);

  // 拼接所有段坐标（去重连接点）
  const allCoords = [];
  segments.forEach((seg, i) => {
    if (i === 0) allCoords.push(...seg);
    else allCoords.push(...seg.slice(1));
  });

  // 绘制真实道路折线（带方向箭头）
  const polyline = new AMap.Polyline({
    path: allCoords,
    strokeColor: "#00d4ff",
    strokeWeight: 5,
    strokeOpacity: 0.9,
    showDir: true,
    lineJoin: "round",
    lineCap: "round",
  });
  polyline.setMap(map.value);
  polylines.push(polyline);

  routeInfo.value = {
    distance: (totalDistance / 1000).toFixed(2),
    duration: Math.ceil(totalDuration),
  };

  nextTick(() => { if (markers.length > 0) map.value.setFitView(markers); });
};

// 切换交通方式：先 TSP 重排景点顺序，再重绘真实路径
const switchTransport = (mode) => {
  currentTransport.value = mode;

  const spots = currentDaySpots.value;
  const validSpots = spots
    .map((s) => { const pos = getValidLngLat(s); return pos ? { ...s, location: pos } : null; })
    .filter(Boolean);

  if (validSpots.length < 2) {
    updateMapRoute();
    return;
  }

  const graph = buildGraphFromSpots(validSpots, mode);
  for (const edges of graph.adjList.values()) {
    edges.forEach((e) => { e.congestion = congestionLevel.value; });
  }

  const costMatrix = buildCostMatrix(validSpots, (a, b) => {
    const { dist } = dijkstra(graph, a.id, mode);
    const c = dist.get(b.id);
    return c === Infinity || c === undefined ? 1e9 : c;
  });

  const { order } = solveTSP(costMatrix, 0);
  const reordered = order.map((idx) => validSpots[idx]);
  daySpotsMap.value = { ...daySpotsMap.value, [selectedDay.value]: reordered };

  nextTick(() => updateMapRoute());
};

// TSP 最优顺序规划
const runTSP = () => {
  const spots = currentDaySpots.value;
  if (spots.length < 2) return;

  const validSpots = spots
    .map((s) => { const pos = getValidLngLat(s); return pos ? { ...s, location: pos } : null; })
    .filter(Boolean);
  if (validSpots.length < 2) return;

  const graph = buildGraphFromSpots(validSpots, currentTransport.value);
  for (const edges of graph.adjList.values()) {
    edges.forEach((e) => { e.congestion = congestionLevel.value; });
  }

  // 构建代价矩阵（Dijkstra 两两最短代价）
  const costMatrix = buildCostMatrix(validSpots, (a, b) => {
    const { dist } = dijkstra(graph, a.id, currentTransport.value);
    const c = dist.get(b.id);
    return c === Infinity ? 1e9 : c;
  });

  const { order } = solveTSP(costMatrix, 0);

  // 按 TSP 最优顺序重排当前天景点
  const reordered = order.map((idx) => validSpots[idx]);
  // 触发响应式：替换整个 daySpotsMap 对象
  daySpotsMap.value = { ...daySpotsMap.value, [selectedDay.value]: reordered };

  ElMessage.success("已按最优顺序重排景点");
  nextTick(() => updateMapRoute());
};

// 清除地图覆盖物
const clearMapOverlays = () => {
  if (map.value) {
    map.value.clearMap();
  }
  markers = [];
  polylines = [];
};

// 计算路线信息
const calculateRouteInfo = (path) => {
  let totalDistance = 0;
  for (let i = 0; i < path.length - 1; i++) {
    totalDistance += AMap.GeometryUtil.distance(path[i], path[i + 1]);
  }

  routeInfo.value = {
    distance: (totalDistance / 1000).toFixed(1),
    duration: Math.ceil((totalDistance / 1000 / 30) * 60), // 假设平均速度30km/h
  };
};

// 聚焦到指定景点
const focusSpot = (spot) => {
  if (!map.value || !spot.location) return;

  // 根据景点类型和位置动态调整缩放级别
  // 城市中心区域使用更大的缩放级别（17-18），郊区使用较小的缩放级别（15-16）
  let zoomLevel = 17;

  // 对于某些特殊景点，使用更大的缩放级别
  const largeAreaSpots = ["博物馆", "公园", "广场", "古城", "遗址"];
  if (
    spot.tags?.some((tag) => largeAreaSpots.some((area) => tag.includes(area)))
  ) {
    zoomLevel = 16; // 大型景点稍微缩小一点，展示全貌
  }

  // 放大到景点位置，使用平滑动画
  // 第三个参数 true 表示使用动画过渡
  map.value.setZoomAndCenter(zoomLevel, spot.location, true);

  console.log(`聚焦景点：${spot.name} [缩放级别：${zoomLevel}]`, spot.location);
};

// 适应视图
const fitView = () => {
  if (!map.value || markers.length === 0) return;
  map.value.setFitView(markers);
};

// 切换路况
const toggleTraffic = () => {
  if (!map.value) return;

  if (showTraffic.value) {
    if (trafficLayer) {
      trafficLayer.hide();
    }
    showTraffic.value = false;
  } else {
    if (!trafficLayer) {
      trafficLayer = new AMap.TileLayer.Traffic({
        zIndex: 10,
      });
      trafficLayer.setMap(map.value);
    } else {
      trafficLayer.show();
    }
    showTraffic.value = true;
  }
};

// 选择天数
const selectDay = (day) => {
  selectedDay.value = day;
  nextTick(() => {
    updateMapRoute();
  });
};

// 拖拽结束
const onDragEnd = (evt) => {
  console.log("拖拽结束", evt);
  // 强制更新视图
  nextTick(() => {
    updateMapRoute();
    ElMessage.success("顺序已更新");
  });
};

// 显示添加景点弹窗
// 显示添加景点弹窗
const showAddSpotModal = async () => {
  showModal.value = true;
  searchQuery.value = "";

  // 如果还没有加载该城市所有景点，从API获取
  if (cityAllSpots.value.length === 0 && city.value) {
    try {
      const response = await fetch(
        `http://localhost:8000/api/spots/recommend?city=${encodeURIComponent(city.value)}&limit=100`,
      );
      if (response.ok) {
        const data = await response.json();
        if (data.spots) {
          cityAllSpots.value = data.spots.map((spot) => ({
            id: spot.id,
            name: spot.name,
            image:
              spot.images && spot.images.length > 0
                ? spot.images[0]
                : "/images/default-spot.jpg",
            rating: spot.rating || 0,
            duration: "2小时",
            tags: spot.tags || [],
          }));
        }
      }
    } catch (error) {
      console.error("获取城市景点失败:", error);
    }
  }
};

// 关闭弹窗
const closeModal = () => {
  showModal.value = false;
};

// 添加景点
const addSpot = (spot) => {
  // 创建新数组而不是直接修改，以触发响应式更新
  currentDaySpots.value = [...currentDaySpots.value, spot];
  closeModal();
  nextTick(() => {
    updateMapRoute();
  });
  ElMessage.success(`已添加 ${spot.name}`);
};

// 删除景点
const removeSpot = (index) => {
  const spot = currentDaySpots.value[index];
  // 创建新数组而不是直接修改，以触发响应式更新
  const newSpots = [...currentDaySpots.value];
  newSpots.splice(index, 1);
  currentDaySpots.value = newSpots;
  nextTick(() => {
    updateMapRoute();
  });
  ElMessage.success(`已删除 ${spot.name}`);
};

// 返回
const goBack = () => {
  // 检查是否从AI界面跳转过来
  if (route.query.from === "ai") {
    router.push("/ai");
  } else {
    router.push("/trips");
  }
};

// 保存行程
const saveTrip = async () => {
  // 获取用户ID
  const userId = localStorage.getItem('userId') || '1';

  try {
    // 1. 保存行程基本信息到数据库
    const dbTripData = {
      title: tripTitle.value,
      destination: city.value,
      total_days: days.value,
      travel_preferences: preferences.value,
    };

    const response = await fetch(`http://localhost:8000/api/trips?user_id=${userId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(dbTripData)
    });

    if (!response.ok) {
      throw new Error('保存行程基本信息失败');
    }

    const result = await response.json();
    const newTripId = result.id;
    console.log('行程已保存到数据库，ID:', newTripId);

    // 2. 保存每日安排的景点到数据库
    const savePromises = [];
    
    console.log('保存行程时的 daySpotsMap:', JSON.stringify(daySpotsMap.value, null, 2));
    console.log('daySpotsMap keys:', Object.keys(daySpotsMap.value));
    
    for (const [dayNumber, spots] of Object.entries(daySpotsMap.value)) {
      console.log(`处理第${dayNumber}天，景点数量:`, spots?.length);
      if (spots && spots.length > 0) {
        for (let i = 0; i < spots.length; i++) {
          const spot = spots[i];
          console.log(`  景点${i}:`, spot.name, 'ID:', spot.id);
          const spotData = {
            spot_id: spot.id,
            day_number: parseInt(dayNumber),
            order_index: i
          };
          
          const promise = fetch(`http://localhost:8000/api/trips/${newTripId}/spots`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(spotData)
          });
          
          savePromises.push(promise);
        }
      }
    }
    
    console.log(`准备保存 ${savePromises.length} 个景点到数据库`);
    
    // 等待所有景点保存完成
    if (savePromises.length > 0) {
      const results = await Promise.all(savePromises);
      console.log(`已保存 ${savePromises.length} 个景点到数据库`, results);
    } else {
      console.warn('没有景点需要保存');
    }

    // 3. 生成前端用的 tripData
    const tripId = "trip_" + Date.now();
    const tripData = {
      id: tripId,
      title: tripTitle.value,
      city: city.value,
      days: days.value,
      preferences: preferences.value,
      daySpots: daySpotsMap.value,
      totalSpots: totalSpots.value,
      createTime: new Date().toISOString(),
      updateTime: new Date().toISOString(),
    };

    // 4. 如果是从AI助手跳转过来的，同时保存到 localStorage
    if (isFromAI.value) {
      const savedTrips = JSON.parse(localStorage.getItem("savedTrips") || "[]");

      // 检查是否已存在相同行程
      const existingIndex = savedTrips.findIndex(
        (t) =>
          t.city === tripData.city &&
          t.days === tripData.days &&
          t.createTime === tripData.createTime,
      );

      if (existingIndex > -1) {
        savedTrips[existingIndex] = tripData;
      } else {
        savedTrips.push(tripData);
      }

      localStorage.setItem("savedTrips", JSON.stringify(savedTrips));
      ElMessage.success("行程已保存到我的行程");
    } else {
      ElMessage.success("行程已保存");
    }

    // 5. 保存为当前行程
    localStorage.setItem("currentTrip", JSON.stringify(tripData));

  } catch (error) {
    console.error('保存行程失败:', error);
    ElMessage.error('保存失败，请重试');
  }
};

// 监听当前天变化，更新地图
watch(selectedDay, () => {
  nextTick(() => {
    updateMapRoute();
  });
});
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
  background: linear-gradient(
    135deg,
    var(--primary-color),
    var(--secondary-color)
  );
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
  background: linear-gradient(
    135deg,
    var(--primary-color),
    var(--secondary-color)
  );
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
  background: linear-gradient(
    135deg,
    var(--primary-color),
    var(--secondary-color)
  );
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
  min-height: 400px;
}

.map-container {
  width: 100%;
  height: 100%;
  min-height: 400px;
}

/* 算法控制面板 */
.algo-controls {
  position: absolute;
  top: 15px;
  left: 15px;
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  z-index: 100;
  background: rgba(10, 10, 26, 0.88);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  padding: 8px 12px;
  backdrop-filter: blur(10px);
}

.transport-group {
  display: flex;
  gap: 6px;
}

.transport-btn {
  padding: 5px 12px;
  border-radius: 16px;
  border: 1px solid var(--border-color);
  background: transparent;
  color: var(--text-secondary);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.transport-btn.active {
  background: var(--primary-color);
  border-color: var(--primary-color);
  color: #000;
  font-weight: 600;
}

.congestion-group {
  display: flex;
  align-items: center;
  gap: 6px;
}

.congestion-label {
  font-size: 12px;
  color: var(--text-secondary);
  white-space: nowrap;
}

.congestion-slider {
  width: 80px;
  accent-color: var(--primary-color);
  cursor: pointer;
}

.congestion-value {
  font-size: 12px;
  color: var(--primary-color);
  min-width: 30px;
}

.tsp-btn {
  font-size: 12px;
  padding: 5px 12px;
  white-space: nowrap;
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

.add-icon.disabled {
  background: rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.5);
}

.available-spot-item.already-added {
  opacity: 0.5;
  cursor: not-allowed;
}

.available-spot-item.already-added:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: var(--border-color);
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
