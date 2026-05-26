/**
 * 高德地图美食 Marker 联动工具
 * 在地图上标注附近美食位置，使用轻量级美食图标
 */

/**
 * 创建美食 Marker 的 HTML 内容（小橘点/美食图标）
 * @param {number} index - 排名序号
 * @param {boolean} isActive - 是否激活状态
 */
export function createFoodMarkerContent(index, isActive = false) {
  const colors = ['#FFD700', '#C0C0C0', '#CD7F32', '#ff9f43']
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

/**
 * 创建美食信息窗体内容
 * @param {Object} food - 美食数据
 */
export function createFoodInfoWindowContent(food) {
  const stars = '★'.repeat(Math.round(food.rating || 0)) + '☆'.repeat(5 - Math.round(food.rating || 0))
  const distance = food.distance_m
    ? food.distance_m < 1000
      ? `${Math.round(food.distance_m)}m`
      : `${(food.distance_m / 1000).toFixed(1)}km`
    : '未知'

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
          ${(food.rating || 0).toFixed(1)}
        </span>
      </div>

      <div style="
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        margin-bottom: 8px;
      ">
        ${food.cuisine_type ? `<span style="
          font-size: 11px;
          color: #ff9f43;
          background: rgba(255,159,67,0.1);
          padding: 2px 8px;
          border-radius: 6px;
        ">${food.cuisine_type}</span>` : ''}
        ${food.price_range ? `<span style="
          font-size: 11px;
          color: #00d4ff;
          background: rgba(0,212,255,0.1);
          padding: 2px 8px;
          border-radius: 6px;
        ">${food.price_range}</span>` : ''}
      </div>

      <div style="
        font-size: 12px;
        color: #666;
        display: flex;
        align-items: center;
        gap: 12px;
      ">
        <span>📍 ${distance}</span>
        <span>🔥 ${food.heat_score || 0}</span>
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

/**
 * 在地图上渲染美食 Marker 列表
 * @param {Object} AMap - 高德地图实例
 * @param {Object} map - 地图对象
 * @param {Array} foods - 美食列表
 * @param {number|string} activeFoodId - 当前激活的美食ID
 * @param {Function} onFoodClick - 点击回调
 * @returns {Array} marker 实例数组
 */
export function renderFoodMarkers(AMap, map, foods, activeFoodId, onFoodClick) {
  if (!AMap || !map || !foods?.length) return []

  const markers = []

  foods.forEach((food, index) => {
    const position = [food.location_lng, food.location_lat]
    if (!position[0] || !position[1]) return

    const isActive = String(activeFoodId) === String(food.id)

    const marker = new AMap.Marker({
      position,
      content: createFoodMarkerContent(index, isActive),
      offset: new AMap.Pixel(-14, -14),
      zIndex: isActive ? 130 : 120,
      extData: { foodId: food.id, index },
    })

    const infoWindow = new AMap.InfoWindow({
      content: createFoodInfoWindowContent(food),
      offset: new AMap.Pixel(0, -20),
      closeWhenClickMap: true,
    })

    marker.on('click', () => {
      // 关闭其他信息窗体
      markers.forEach((m) => m._infoWindow?.close())
      infoWindow.open(map, marker.getPosition())
      if (onFoodClick) onFoodClick(food)
    })

    marker._infoWindow = infoWindow
    marker._foodId = food.id

    map.add(marker)
    markers.push(marker)
  })

  return markers
}

/**
 * 清除所有美食 Marker
 * @param {Object} map - 地图对象
 * @param {Array} markers - marker 数组
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
 * @param {Array} markers - marker 数组
 * @param {number|string} foodId - 要激活的美食ID
 * @param {Object} map - 地图对象
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
 * 调整颜色亮度
 * @param {string} hex - 十六进制颜色
 * @param {number} percent - 调整百分比
 */
function adjustColor(hex, percent) {
  const num = parseInt(hex.replace('#', ''), 16)
  const amt = Math.round(2.55 * percent)
  const R = Math.max(0, Math.min(255, (num >> 16) + amt))
  const G = Math.max(0, Math.min(255, ((num >> 8) & 0x00ff) + amt))
  const B = Math.max(0, Math.min(255, (num & 0x0000ff) + amt))
  return '#' + (0x1000000 + R * 0x10000 + G * 0x100 + B).toString(16).slice(1)
}

/**
 * 自适应视野以包含所有美食 Marker
 * @param {Object} map - 地图对象
 * @param {Array} markers - marker 数组
 * @param {Array} routeMarkers - 路线 marker 数组（可选）
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
  renderFoodMarkers,
  clearFoodMarkers,
  highlightFoodMarker,
  fitViewToFoods,
}
