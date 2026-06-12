/**
 * 高德地图美食 Marker 联动工具
 * ————————————————————————————————————————
 * 在地图上标注附近美食位置，支持两种 InfoWindow 风格：
 *   1. createFoodInfoWindowContent — 浅色风格（向后兼容）
 *   2. createDarkFoodInfoWindow     — 深色赛博朋克风格（新增）
 *
 * 同时兼容新旧两种数据字段格式：
 *   新格式：lnglat, type, popularity, distance
 *   旧格式：location_lng/location_lat, cuisine_type, heat_score, distance_m
 */

// ═══════════════════════════════════════════════════════════
// 工具函数
// ═══════════════════════════════════════════════════════════

/** 安全获取经纬度数组 [lng, lat]（兼容新旧格式） */
function getPosition(food) {
  if (food.lnglat && Array.isArray(food.lnglat) && food.lnglat.length >= 2) {
    return [food.lnglat[0], food.lnglat[1]]
  }
  if (food.location_lng != null && food.location_lat != null) {
    return [food.location_lng, food.location_lat]
  }
  return null
}

/** 安全获取菜系类型 */
function getCuisineType(food) {
  return food.type || food.cuisine_type || ''
}

/** 安全获取热度 */
function getPopularity(food) {
  return food.popularity ?? food.heat_score ?? 0
}

/** 安全获取距离（米） */
function getDistance(food) {
  return food.distance ?? food.distance_m ?? 0
}

/** 安全获取评分 */
function getRating(food) {
  return food.rating ?? 0
}

/** 安全获取价格区间 */
function getPriceRange(food) {
  return food.price_range || ''
}

/** 安全获取标签数组 */
function getTags(food) {
  return food.tags || []
}

/** 格式化距离文本 */
function formatDistanceText(m) {
  if (!m && m !== 0) return '未知'
  if (m < 1000) return `${Math.round(m)}m`
  return `${(m / 1000).toFixed(1)}km`
}

/** 调整颜色亮度 */
function adjustColor(hex, percent) {
  const num = parseInt(hex.replace('#', ''), 16)
  const amt = Math.round(2.55 * percent)
  const R = Math.max(0, Math.min(255, (num >> 16) + amt))
  const G = Math.max(0, Math.min(255, ((num >> 8) & 0x00ff) + amt))
  const B = Math.max(0, Math.min(255, (num & 0x0000ff) + amt))
  return '#' + (0x1000000 + R * 0x10000 + G * 0x100 + B).toString(16).slice(1)
}

// ═══════════════════════════════════════════════════════════
// Marker 内容
// ═══════════════════════════════════════════════════════════

/**
 * 创建美食 Marker 的 HTML 内容（圆形编号图标）
 * @param {number} index   - 排名序号（0-based）
 * @param {boolean} isActive - 是否激活状态
 */
export function createFoodMarkerContent(index, isActive = false) {
  const colors = ['#FFD700', '#C0C0C0', '#CD7F32', '#00d4ff']
  const bgColor = index < 3 ? colors[index] : colors[3]
  const size = isActive ? 32 : 28
  const zIndex = isActive ? 130 : 120

  return `
    <div class="food-map-marker ${isActive ? 'active' : ''}" style="
      width: ${size}px;
      height: ${size}px;
      border-radius: 50%;
      background: linear-gradient(135deg, ${bgColor}, ${adjustColor(bgColor, -20)});
      border: 2px solid ${isActive ? '#fff' : 'rgba(255,255,255,0.3)'};
      box-shadow: 0 2px 8px rgba(0,0,0,0.3), 0 0 0 2px rgba(255,255,255,0.1);
      display: flex;
      align-items: center;
      justify-content: center;
      color: #fff;
      font-size: ${isActive ? 14 : 12}px;
      font-weight: 700;
      cursor: pointer;
      transition: all 0.3s ease;
      z-index: ${zIndex};
    ">
      ${index < 3 ? '🍜' : index + 1}
    </div>
  `
}

// ═══════════════════════════════════════════════════════════
// InfoWindow 内容 — 浅色版（向后兼容）
// ═══════════════════════════════════════════════════════════

/**
 * 创建美食信息窗体内容（浅色风格，向后兼容）
 * @param {Object} food - 美食数据
 */
export function createFoodInfoWindowContent(food) {
  const rating = getRating(food)
  const stars = '★'.repeat(Math.round(rating)) + '☆'.repeat(5 - Math.round(rating))
  const distance = formatDistanceText(getDistance(food))

  return `
    <div style="
      padding: 12px 14px;
      min-width: 200px;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    ">
      <h4 style="
        margin: 0 0 8px;
        font-size: 15px;
        font-weight: 700;
        color: #333;
        line-height: 1.3;
      ">${food.name}</h4>

      <div style="margin-bottom: 6px;">
        <span style="color: #ffc107; font-size: 13px; letter-spacing: 1px;">${stars}</span>
        <span style="color: #ff6b6b; font-size: 13px; font-weight: 600; margin-left: 6px;">
          ${rating.toFixed(1)}
        </span>
      </div>

      <div style="
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        margin-bottom: 8px;
      ">
        ${getCuisineType(food) ? `<span style="
          font-size: 11px;
          color: #ff9f43;
          background: rgba(255,159,67,0.1);
          padding: 2px 8px;
          border-radius: 6px;
        ">${getCuisineType(food)}</span>` : ''}
        ${getPriceRange(food) ? `<span style="
          font-size: 11px;
          color: #00d4ff;
          background: rgba(0,212,255,0.1);
          padding: 2px 8px;
          border-radius: 6px;
        ">${getPriceRange(food)}</span>` : ''}
      </div>

      <div style="
        font-size: 12px;
        color: #666;
        display: flex;
        align-items: center;
        gap: 12px;
      ">
        <span>📍 ${distance}</span>
        <span>🔥 ${getPopularity(food)}</span>
      </div>

      ${food.address ? `<p style="
        margin: 8px 0 0;
        font-size: 11px;
        color: #999;
        line-height: 1.4;
      ">${food.address}</p>` : ''}
    </div>
  `
}

// ═══════════════════════════════════════════════════════════
// InfoWindow 内容 — 深色赛博朋克版（NEW!）
// ═══════════════════════════════════════════════════════════

/**
 * 创建深色赛博朋克风格的美食 InfoWindow
 * ————————————————————————————————————————
 * 设计语言：匹配全局暗黑科技风主题
 *   - 主背景：#111827 (gray-900 级别深色)
 *   - 卡片背景：rgba(30, 30, 50, 0.95)
 *   - 高亮色：#00d4ff (cyan 霓虹)
 *   - 评分金色：#ffc107
 *   - 热度红色：#ff6b6b
 *   - 边框：rgba(0, 212, 255, 0.2)
 *
 * 展示信息：
 *   - 商家名称（大字加粗）
 *   - ⭐ 评分 + 星级条
 *   - 🔥 热度数值
 *   - 🏷️ 菜系分类标签
 *   - 💰 价格区间
 *   - 📍 距离
 *   - 🏠 地址（如有）
 *   - 特色标签（最多展示 3 个）
 *
 * @param {Object} food - 美食数据
 * @returns {string} InfoWindow HTML 字符串
 */
export function createDarkFoodInfoWindow(food) {
  const rating = getRating(food)
  const stars = '★'.repeat(Math.round(rating)) + '☆'.repeat(5 - Math.round(rating))
  const distance = formatDistanceText(getDistance(food))
  const cuisineType = getCuisineType(food)
  const popularity = getPopularity(food)
  const priceRange = getPriceRange(food)
  const tags = getTags(food)
  const address = food.address || ''

  // 生成标签 HTML
  const tagsHtml = tags.slice(0, 3).map((tag) => `
    <span style="
      display: inline-block;
      font-size: 10px;
      color: rgba(160, 160, 176, 0.85);
      background: rgba(255, 255, 255, 0.06);
      padding: 2px 8px;
      border-radius: 10px;
      border: 1px solid rgba(255, 255, 255, 0.08);
    ">${tag}</span>
  `).join('')

  return `
    <div style="
      padding: 14px 16px;
      min-width: 240px;
      max-width: 300px;
      font-family: 'Noto Sans SC', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      background: #111827;
      border-radius: 12px;
      box-shadow: 0 0 20px rgba(0, 212, 255, 0.15), 0 4px 16px rgba(0, 0, 0, 0.4);
      border: 1px solid rgba(0, 212, 255, 0.15);
    ">
      <!-- 商家名称 -->
      <h4 style="
        margin: 0 0 10px;
        font-size: 16px;
        font-weight: 700;
        color: #ffffff;
        line-height: 1.3;
        letter-spacing: 0.3px;
      ">${food.name}</h4>

      <!-- 评分 + 热度 -->
      <div style="
        display: flex;
        align-items: center;
        gap: 14px;
        margin-bottom: 10px;
      ">
        <!-- 星级 -->
        <div style="display: flex; align-items: center; gap: 4px;">
          <span style="
            color: #ffc107;
            font-size: 14px;
            letter-spacing: 1.5px;
            text-shadow: 0 0 6px rgba(255, 193, 7, 0.4);
          ">${stars}</span>
          <span style="
            color: #ffc107;
            font-size: 14px;
            font-weight: 700;
          ">${rating.toFixed(1)}</span>
        </div>

        <!-- 热度 -->
        <div style="display: flex; align-items: center; gap: 3px;">
          <span style="font-size: 12px;">🔥</span>
          <span style="
            color: #ff6b6b;
            font-size: 13px;
            font-weight: 600;
          ">${popularity}</span>
        </div>

        <!-- 距离 -->
        <div style="display: flex; align-items: center; gap: 3px;">
          <span style="font-size: 11px;">📍</span>
          <span style="
            color: rgba(160, 160, 176, 0.8);
            font-size: 12px;
            font-weight: 500;
          ">${distance}</span>
        </div>
      </div>

      <!-- 标签行：菜系 + 价格 -->
      <div style="
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        margin-bottom: 10px;
      ">
        ${cuisineType ? `<span style="
          display: inline-block;
          font-size: 11px;
          font-weight: 600;
          color: #ff9f43;
          background: rgba(255, 159, 67, 0.12);
          padding: 3px 10px;
          border-radius: 10px;
          border: 1px solid rgba(255, 159, 67, 0.2);
        ">🏷️ ${cuisineType}</span>` : ''}
        ${priceRange ? `<span style="
          display: inline-block;
          font-size: 11px;
          font-weight: 600;
          color: #00d4ff;
          background: rgba(0, 212, 255, 0.1);
          padding: 3px 10px;
          border-radius: 10px;
          border: 1px solid rgba(0, 212, 255, 0.15);
        ">💰 ${priceRange}</span>` : ''}
      </div>

      <!-- 特色标签 -->
      ${tagsHtml ? `<div style="
        display: flex;
        gap: 6px;
        flex-wrap: wrap;
        margin-bottom: ${address ? '8px' : '0'};
      ">${tagsHtml}</div>` : ''}

      <!-- 地址 -->
      ${address ? `<p style="
        margin: 0;
        font-size: 11px;
        color: rgba(160, 160, 176, 0.55);
        line-height: 1.5;
        display: flex;
        align-items: flex-start;
        gap: 4px;
      ">
        <span style="flex-shrink: 0;">🏠</span>
        <span>${address}</span>
      </p>` : ''}
    </div>
  `
}

// ═══════════════════════════════════════════════════════════
// Marker 渲染
// ═══════════════════════════════════════════════════════════

/**
 * 在地图上渲染美食 Marker 列表
 * ————————————————————————————————————————
 * 兼容新旧两种数据格式，默认使用深色 InfoWindow。
 *
 * @param {Object}   AMap          - 高德地图 AMap 全局对象
 * @param {Object}   map           - 地图实例
 * @param {Array}    foods         - 美食列表
 * @param {number|string} activeFoodId - 当前激活的美食 ID
 * @param {Function} onFoodClick   - 点击回调 (food) => void
 * @param {Object}   options       - 可选配置
 * @param {boolean}  options.darkTheme - 是否使用深色 InfoWindow（默认 true）
 * @returns {Array} marker 实例数组
 */
export function renderFoodMarkers(AMap, map, foods, activeFoodId, onFoodClick, options = {}) {
  if (!AMap || !map || !foods?.length) return []

  const { darkTheme = true } = options
  const markers = []

  foods.forEach((food, index) => {
    const position = getPosition(food)
    if (!position || !position[0] || !position[1]) return

    const isActive = String(activeFoodId) === String(food.id)

    // 创建 Marker
    const marker = new AMap.Marker({
      position,
      content: createFoodMarkerContent(index, isActive),
      offset: new AMap.Pixel(-14, -14),
      zIndex: isActive ? 130 : 120,
      extData: { foodId: food.id, index },
    })

    // 选择 InfoWindow 风格
    const infoContent = darkTheme
      ? createDarkFoodInfoWindow(food)
      : createFoodInfoWindowContent(food)

    // 深色 InfoWindow 需要设置背景透明（内容自带背景）
    const infoWindowOpts = {
      content: infoContent,
      offset: new AMap.Pixel(0, -20),
      closeWhenClickMap: true,
    }

    // 深色模式下，InfoWindow 容器背景设为透明
    if (darkTheme) {
      infoWindowOpts.isCustom = true
    }

    const infoWindow = new AMap.InfoWindow(infoWindowOpts)

    // 点击事件
    marker.on('click', () => {
      // 关闭其他信息窗体
      markers.forEach((m) => m._infoWindow?.close())
      infoWindow.open(map, marker.getPosition())
      if (onFoodClick) onFoodClick(food)
    })

    // 存储引用
    marker._infoWindow = infoWindow
    marker._foodId = food.id

    map.add(marker)
    markers.push(marker)
  })

  return markers
}

/**
 * 使用旧 API 签名渲染（向后兼容补丁）
 * 如果调用方仍传递 6 个参数且第 6 个是函数，自动兼容
 */
export function renderFoodMarkersCompat(AMap, map, foods, activeFoodId, onFoodClick) {
  return renderFoodMarkers(AMap, map, foods, activeFoodId, onFoodClick, { darkTheme: true })
}

/**
 * 清除所有美食 Marker
 * @param {Object} map     - 地图对象
 * @param {Array}  markers - marker 数组
 */
export function clearFoodMarkers(map, markers) {
  if (!map || !markers?.length) return
  markers.forEach((marker) => {
    marker._infoWindow?.close()
    map.remove(marker)
  })
  markers.length = 0
}

/**
 * 高亮指定美食 Marker
 * @param {Array}  markers - marker 数组
 * @param {number|string} foodId - 要激活的美食 ID
 * @param {Object} map     - 地图对象
 */
export function highlightFoodMarker(markers, foodId, map) {
  if (!markers?.length) return

  markers.forEach((marker) => {
    const isTarget = String(marker._foodId) === String(foodId)
    const index = marker.getExtData()?.index || 0
    marker.setContent(createFoodMarkerContent(index, isTarget))
    marker.setzIndex(isTarget ? 130 : 120)

    if (isTarget && map) {
      map.setZoomAndCenter(17, marker.getPosition(), true)
      marker._infoWindow?.open(map, marker.getPosition())
    }
  })
}

/**
 * 自适应视野以包含所有美食 Marker
 * @param {Object} map          - 地图对象
 * @param {Array}  markers      - marker 数组
 * @param {Array}  routeMarkers - 路线 marker 数组（可选）
 */
export function fitViewToFoods(map, markers, routeMarkers = []) {
  if (!map || !markers?.length) return
  const allMarkers = [...markers, ...(routeMarkers || [])]
  if (allMarkers.length > 0) {
    map.setFitView(allMarkers, false, [60, 60, 60, 60], 15)
  }
}

export default {
  createFoodMarkerContent,
  createFoodInfoWindowContent,
  createDarkFoodInfoWindow,
  renderFoodMarkers,
  renderFoodMarkersCompat,
  clearFoodMarkers,
  highlightFoodMarker,
  fitViewToFoods,
}
