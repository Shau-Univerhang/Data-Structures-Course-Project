<template>
  <div class="amap-container">
    <!-- 地图容器 -->
    <div ref="mapContainer" class="map-container"></div>

    <!-- 控制面板 -->
    <div class="control-panel">
      <div class="panel-header">
        <h3>地图控制</h3>
      </div>

      <!-- 起点设置 -->
      <div class="control-section">
        <label class="section-title">起点设置</label>
        <div class="input-group">
          <input
            v-model="startPoint.lng"
            type="number"
            placeholder="经度"
            class="coord-input"
            step="0.000001"
          />
          <input
            v-model="startPoint.lat"
            type="number"
            placeholder="纬度"
            class="coord-input"
            step="0.000001"
          />
          <button @click="setStartPoint" class="btn btn-primary">
            设置起点
          </button>
        </div>
        <p class="hint-text">提示：也可直接点击地图设置起点</p>
      </div>

      <!-- 终点设置 -->
      <div class="control-section">
        <label class="section-title">终点设置</label>
        <div class="input-group">
          <input
            v-model="endPoint.lng"
            type="number"
            placeholder="经度"
            class="coord-input"
            step="0.000001"
          />
          <input
            v-model="endPoint.lat"
            type="number"
            placeholder="纬度"
            class="coord-input"
            step="0.000001"
          />
          <button @click="setEndPoint" class="btn btn-primary">设置终点</button>
        </div>
      </div>

      <!-- 路径规划按钮 -->
      <div class="control-section">
        <button
          @click="planRoute"
          class="btn btn-success"
          :disabled="!canPlanRoute"
        >
          规划路线
        </button>
        <button @click="clearRoute" class="btn btn-secondary">清除路线</button>
        <button @click="clearAllMarkers" class="btn btn-danger">
          清除所有标记
        </button>
      </div>

      <!-- 批量添加标记 -->
      <div class="control-section">
        <label class="section-title">批量添加标记 (JSON格式)</label>
        <textarea
          v-model="markersJson"
          class="json-input"
          placeholder="[[116.397428, 39.90923], [116.407428, 39.91923]]"
        ></textarea>
        <button @click="addBatchMarkers" class="btn btn-primary">
          批量添加
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from "vue";
import AMapLoader from "@amap/amap-jsapi-loader";

// 高德地图 Key - 从环境变量读取
const AMAP_KEY = import.meta.env.VITE_AMAP_KEY || "";

// 高德地图安全密钥 - 从环境变量读取
const AMAP_SECURITY_KEY = import.meta.env.VITE_AMAP_SECURITY_KEY || "";

// DOM 引用
const mapContainer = ref(null);

// 地图实例
let map = null;
let startMarker = null;
let endMarker = null;
let driving = null;
let markers = [];

// 响应式数据
const startPoint = ref({ lng: 116.397428, lat: 39.90923 });
const endPoint = ref({ lng: 116.407428, lat: 39.91923 });
const markersJson = ref("");

// 计算属性：是否可以规划路线
const canPlanRoute = computed(() => {
  return (
    startPoint.value.lng &&
    startPoint.value.lat &&
    endPoint.value.lng &&
    endPoint.value.lat
  );
});

/**
 * 初始化地图
 */
const initMap = async () => {
  try {
    // 设置安全密钥（必须在加载地图前设置）
    if (AMAP_SECURITY_KEY) {
      window._AMapSecurityConfig = {
        securityJsCode: AMAP_SECURITY_KEY,
      };
    }

    // 加载高德地图 JSAPI
    const AMap = await AMapLoader.load({
      key: AMAP_KEY,
      version: "2.0",
      plugins: [
        "AMap.Driving", // 驾车路线规划
        "AMap.Marker", // 标记点
        "AMap.InfoWindow", // 信息窗体
        "AMap.Scale", // 比例尺
        "AMap.ToolBar", // 工具条
      ],
    });

    // 创建地图实例
    map = new AMap.Map(mapContainer.value, {
      zoom: 12, // 初始缩放级别
      center: [116.397428, 39.90923], // 北京中心点
      viewMode: "2D", // 2D 视图模式
      resizeEnable: true, // 启用自适应
    });

    // 添加地图控件
    map.addControl(new AMap.Scale());
    map.addControl(new AMap.ToolBar());

    // 绑定地图点击事件
    map.on("click", handleMapClick);

    // 初始化驾车路线规划插件
    driving = new AMap.Driving({
      map: map,
      panel: "panel", // 路线详情面板 (可选)
      policy: AMap.DrivingPolicy.LEAST_TIME, // 最快路线策略
    });

    console.log("地图初始化成功");
  } catch (error) {
    console.error("地图初始化失败:", error);
  }
};

/**
 * 处理地图点击事件
 * @param {Object} e - 点击事件对象
 */
const handleMapClick = (e) => {
  const lng = e.lnglat.getLng();
  const lat = e.lnglat.getLat();

  // 如果没有起点，设置起点
  if (!startMarker) {
    startPoint.value = { lng, lat };
    setStartPoint();
  } else if (!endMarker) {
    // 如果已有起点但没有终点，设置终点
    endPoint.value = { lng, lat };
    setEndPoint();
  }
};

/**
 * 设置起点标记
 */
const setStartPoint = () => {
  if (!map) return;

  // 清除已有起点标记
  if (startMarker) {
    map.remove(startMarker);
  }

  const { lng, lat } = startPoint.value;

  // 创建起点标记
  startMarker = new window.AMap.Marker({
    position: [lng, lat],
    title: "起点",
    label: {
      content: "起点",
      direction: "top",
    },
    icon: new window.AMap.Icon({
      image:
        "//a.amap.com/jsapi_demos/static/demo-center/icons/poi-marker-default.png",
      size: new window.AMap.Size(25, 34),
      imageSize: new window.AMap.Size(25, 34),
    }),
  });

  map.add(startMarker);

  // 设置地图中心
  map.setCenter([lng, lat]);
};

/**
 * 设置终点标记
 */
const setEndPoint = () => {
  if (!map) return;

  // 清除已有终点标记
  if (endMarker) {
    map.remove(endMarker);
  }

  const { lng, lat } = endPoint.value;

  // 创建终点标记
  endMarker = new window.AMap.Marker({
    position: [lng, lat],
    title: "终点",
    label: {
      content: "终点",
      direction: "top",
    },
    icon: new window.AMap.Icon({
      image:
        "//a.amap.com/jsapi_demos/static/demo-center/icons/poi-marker-red.png",
      size: new window.AMap.Size(25, 34),
      imageSize: new window.AMap.Size(25, 34),
    }),
  });

  map.add(endMarker);
};

/**
 * 规划驾车路线
 */
const planRoute = () => {
  if (!driving || !canPlanRoute.value) return;

  const start = [startPoint.value.lng, startPoint.value.lat];
  const end = [endPoint.value.lng, endPoint.value.lat];

  // 清除之前的路线
  driving.clear();

  // 搜索驾车路线
  driving.search(start, end, (status, result) => {
    if (status === "complete") {
      console.log("路线规划成功:", result);

      // 获取路线信息
      if (result.routes && result.routes[0]) {
        const route = result.routes[0];
        console.log(`总距离: ${(route.distance / 1000).toFixed(2)} 公里`);
        console.log(`预计时间: ${Math.ceil(route.time / 60)} 分钟`);
      }
    } else {
      console.error("路线规划失败:", result);
    }
  });
};

/**
 * 清除路线
 */
const clearRoute = () => {
  if (driving) {
    driving.clear();
  }
};

/**
 * 清除所有标记
 */
const clearAllMarkers = () => {
  if (!map) return;

  // 清除起点和终点标记
  if (startMarker) {
    map.remove(startMarker);
    startMarker = null;
  }
  if (endMarker) {
    map.remove(endMarker);
    endMarker = null;
  }

  // 清除批量添加的标记
  if (markers.length > 0) {
    map.remove(markers);
    markers = [];
  }

  // 清除路线
  clearRoute();
};

/**
 * 批量添加标记
 */
const addBatchMarkers = () => {
  if (!map || !markersJson.value) return;

  try {
    const coords = JSON.parse(markersJson.value);

    if (!Array.isArray(coords)) {
      alert("请输入有效的坐标数组");
      return;
    }

    coords.forEach((coord, index) => {
      if (Array.isArray(coord) && coord.length >= 2) {
        const marker = new window.AMap.Marker({
          position: coord,
          title: `标记点 ${index + 1}`,
          label: {
            content: `标记 ${index + 1}`,
            direction: "top",
          },
        });

        markers.push(marker);
      }
    });

    if (markers.length > 0) {
      map.add(markers);
      // 自适应视野
      map.setFitView(markers);
    }

    console.log(`成功添加 ${markers.length} 个标记`);
  } catch (error) {
    console.error("解析坐标失败:", error);
    alert("JSON 格式错误，请检查输入");
  }
};

/**
 * 暴露方法给父组件
 */
defineExpose({
  // 设置起点
  setStart: (lng, lat) => {
    startPoint.value = { lng, lat };
    setStartPoint();
  },
  // 设置终点
  setEnd: (lng, lat) => {
    endPoint.value = { lng, lat };
    setEndPoint();
  },
  // 规划路线
  planRoute,
  // 清除所有
  clearAll: clearAllMarkers,
  // 添加单个标记
  addMarker: (lng, lat, title = "") => {
    if (!map) return;
    const marker = new window.AMap.Marker({
      position: [lng, lat],
      title: title || `标记 ${markers.length + 1}`,
    });
    markers.push(marker);
    map.add(marker);
  },
});

// 组件挂载时初始化地图
onMounted(() => {
  initMap();
});

// 组件卸载时销毁地图实例
onUnmounted(() => {
  if (map) {
    // 清除所有事件监听
    map.off("click", handleMapClick);

    // 销毁地图实例
    map.destroy();
    map = null;
  }

  // 清理引用
  startMarker = null;
  endMarker = null;
  driving = null;
  markers = [];

  console.log("地图实例已销毁");
});
</script>

<style scoped>
.amap-container {
  display: flex;
  width: 100%;
  height: 100%;
  min-height: 600px;
}

/* 地图容器 - 自适应高度 */
.map-container {
  flex: 1;
  height: 100%;
  min-height: 600px;
  border-radius: 8px;
  overflow: hidden;
}

/* 控制面板 */
.control-panel {
  width: 320px;
  padding: 16px;
  background: #fff;
  border-left: 1px solid #e0e0e0;
  overflow-y: auto;
}

.panel-header {
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 2px solid #409eff;
}

.panel-header h3 {
  margin: 0;
  color: #303133;
  font-size: 18px;
}

/* 控制区块 */
.control-section {
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #ebeef5;
}

.control-section:last-child {
  border-bottom: none;
}

.section-title {
  display: block;
  margin-bottom: 8px;
  color: #606266;
  font-size: 14px;
  font-weight: 500;
}

/* 输入组 */
.input-group {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.coord-input {
  width: 80px;
  padding: 6px 10px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 13px;
  transition: border-color 0.2s;
}

.coord-input:focus {
  outline: none;
  border-color: #409eff;
}

/* JSON 输入框 */
.json-input {
  width: 100%;
  height: 80px;
  padding: 8px 12px;
  margin-bottom: 8px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 13px;
  font-family: monospace;
  resize: vertical;
  box-sizing: border-box;
}

.json-input:focus {
  outline: none;
  border-color: #409eff;
}

/* 按钮样式 */
.btn {
  padding: 6px 16px;
  border: none;
  border-radius: 4px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: #409eff;
  color: #fff;
}

.btn-primary:hover:not(:disabled) {
  background: #66b1ff;
}

.btn-success {
  background: #67c23a;
  color: #fff;
  margin-right: 8px;
  margin-bottom: 8px;
}

.btn-success:hover:not(:disabled) {
  background: #85ce61;
}

.btn-secondary {
  background: #909399;
  color: #fff;
  margin-right: 8px;
  margin-bottom: 8px;
}

.btn-secondary:hover {
  background: #a6a9ad;
}

.btn-danger {
  background: #f56c6c;
  color: #fff;
  margin-bottom: 8px;
}

.btn-danger:hover {
  background: #f78989;
}

/* 提示文字 */
.hint-text {
  margin: 8px 0 0;
  color: #909399;
  font-size: 12px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .amap-container {
    flex-direction: column;
  }

  .control-panel {
    width: 100%;
    border-left: none;
    border-top: 1px solid #e0e0e0;
    max-height: 300px;
  }

  .map-container {
    min-height: 400px;
  }
}
</style>
} .map-container { } .map-container {