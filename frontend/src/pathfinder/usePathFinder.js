/**
 * usePathFinder.js — Vue 3 Composition API 路径规划 Hook
 *
 * 职责：
 *   1. 接收景点数组，构建图结构
 *   2. 调用 Dijkstra / TSP 算法计算路径
 *   3. 将节点 ID 序列转换为 AMap.Polyline 可用的坐标数组
 *   4. 在高德地图上渲染带方向箭头的彩色路径
 *   5. 提供"点击景点卡片 → 规划到该景点最短路径"的接口
 *
 * 使用示例：
 *   const { planToSpot, planTSPRoute, clearRoute, routeInfo } = usePathFinder(mapRef, spots)
 */

import { ref, shallowRef } from 'vue';
import { buildGraphFromSpots, haversineDistance, TransportType } from './graph.js';
import { shortestPath } from './dijkstra.js';
import { solveTSP, buildCostMatrix } from './tsp.js';

/**
 * 路径规划 Composable
 *
 * @param {import('vue').Ref} mapRef         高德地图实例的 shallowRef（map.value = AMap.Map 实例）
 * @param {import('vue').Ref} spotsRef       景点数组的 ref，每个元素需含 { id, name, location: [lng, lat] }
 * @returns {Object} 路径规划相关方法和状态
 */
export function usePathFinder(mapRef, spotsRef) {
  // 当前渲染在地图上的覆盖物（Polyline + 箭头标记）
  const overlays = shallowRef([]);

  // 路线统计信息（供 UI 展示）
  const routeInfo = ref(null);

  // 当前交通模式
  const transportMode = ref(TransportType.WALK);

  /**
   * 清除地图上所有路径覆盖物
   */
  function clearRoute() {
    if (!mapRef.value) return;
    overlays.value.forEach((o) => mapRef.value.remove(o));
    overlays.value = [];
    routeInfo.value = null;
  }

  /**
   * 将节点 ID 序列转换为经纬度坐标数组
   *
   * @param {Array<string|number>} nodeIds  节点 ID 序列
   * @param {import('./graph.js').Graph} graph
   * @returns {Array<[number, number]>}     [[lng, lat], ...]
   */
  function nodeIdsToLngLats(nodeIds, graph) {
    return nodeIds
      .map((id) => graph.getNode(id)?.lnglat)
      .filter(Boolean);
  }

  /**
   * 在地图上绘制路径
   *
   * @param {Array<[number, number]>} lngLats  坐标数组
   * @param {Object} options                   样式选项
   * @param {string} options.color             线条颜色（默认青色）
   * @param {number} options.weight            线宽（默认 5）
   * @param {boolean} options.showArrow        是否显示方向箭头（默认 true）
   */
  function drawPolyline(lngLats, { color = '#00d4ff', weight = 5, showArrow = true } = {}) {
    if (!mapRef.value || lngLats.length < 2) return;

    const AMap = window.AMap;
    if (!AMap) {
      console.error('AMap 未加载，无法绘制路径');
      return;
    }

    // 创建 Polyline（高德地图折线）
    const polyline = new AMap.Polyline({
      path: lngLats,
      strokeColor: color,
      strokeWeight: weight,
      strokeOpacity: 0.9,
      strokeStyle: 'solid',
      // showDir: true 会在线上显示方向箭头（高德 2.0 API 支持）
      showDir: showArrow,
      lineJoin: 'round',
      lineCap: 'round',
    });

    polyline.setMap(mapRef.value);
    overlays.value = [...overlays.value, polyline];

    // 在每个途经点绘制小圆点标记（增强可读性）
    lngLats.forEach((lnglat, idx) => {
      // 起点和终点用不同颜色
      const isEndpoint = idx === 0 || idx === lngLats.length - 1;
      const marker = new AMap.CircleMarker({
        center: lnglat,
        radius: isEndpoint ? 8 : 5,
        strokeColor: color,
        strokeWeight: 2,
        fillColor: isEndpoint ? color : '#ffffff',
        fillOpacity: 0.9,
        zIndex: 10,
      });
      marker.setMap(mapRef.value);
      overlays.value = [...overlays.value, marker];
    });
  }

  /**
   * 计算并展示从"当前位置/起点"到指定景点的最短路径（Dijkstra）
   *
   * 这是"点击景点卡片即时规划"功能的核心接口。
   *
   * @param {string|number} fromSpotId   起点景点 ID
   * @param {string|number} toSpotId     目标景点 ID
   * @param {string|null}   mode         交通方式（null = 使用当前 transportMode）
   */
  function planToSpot(fromSpotId, toSpotId, mode = null) {
    const spots = spotsRef.value;
    if (!spots || spots.length === 0) return;

    // 构建图
    const graph = buildGraphFromSpots(spots, mode || transportMode.value);

    // 调用 Dijkstra 求最短路径
    const { path, cost } = shortestPath(graph, fromSpotId, toSpotId, mode || transportMode.value);

    if (path.length === 0) {
      console.warn(`无法找到从 ${fromSpotId} 到 ${toSpotId} 的路径`);
      return;
    }

    // 清除旧路径
    clearRoute();

    // 将节点 ID 序列转换为坐标数组
    const lngLats = nodeIdsToLngLats(path, graph);

    // 计算实际距离（米）
    let totalDistance = 0;
    for (let i = 0; i < lngLats.length - 1; i++) {
      totalDistance += haversineDistance(lngLats[i], lngLats[i + 1]);
    }

    // 绘制路径（青色，带方向箭头）
    drawPolyline(lngLats, { color: '#00d4ff', weight: 5, showArrow: true });

    // 更新路线统计
    routeInfo.value = {
      type: 'shortest',
      from: graph.getNode(fromSpotId)?.name,
      to: graph.getNode(toSpotId)?.name,
      distance: (totalDistance / 1000).toFixed(2),  // 公里
      duration: Math.ceil(cost),                     // 分钟
      nodeCount: path.length,
    };

    // 自适应视野
    if (mapRef.value && lngLats.length > 0) {
      mapRef.value.setFitView();
    }

    return { path, lngLats, cost };
  }

  /**
   * 计算并展示多景点 TSP 最优巡游路线
   *
   * 给定景点列表，从第一个景点出发，访问所有景点后返回起点，
   * 求总代价最小的访问顺序。
   *
   * @param {Array<string|number>} spotIds   景点 ID 数组（第一个为起点）
   * @param {string|null}          mode      交通方式
   * @returns {{ orderedSpots: Array, cost: number }}
   */
  function planTSPRoute(spotIds, mode = null) {
    const spots = spotsRef.value;
    if (!spots || spotIds.length < 2) return;

    // 只取参与规划的景点
    const targetSpots = spotIds
      .map((id) => spots.find((s) => s.id === id))
      .filter(Boolean);

    if (targetSpots.length < 2) return;

    // 构建图
    const graph = buildGraphFromSpots(targetSpots, mode || transportMode.value);

    // 构建代价矩阵：使用 Dijkstra 计算任意两点间最短代价
    // 对于全连接图，直接用边权重即可（Haversine 距离 / 速度）
    const costMatrix = buildCostMatrix(targetSpots, (a, b) => {
      const { cost } = shortestPath(graph, a.id, b.id, mode || transportMode.value);
      return cost === Infinity ? 1e9 : cost;
    });

    // 起点下标（第一个景点）
    const startIndex = 0;

    // 调用 TSP 求解器
    const { order, cost } = solveTSP(costMatrix, startIndex);

    // 将下标序列转换为景点 ID 序列
    const orderedSpotIds = order.map((idx) => targetSpots[idx].id);

    // 清除旧路径
    clearRoute();

    // 构建完整路径坐标（依次连接各景点）
    const allLngLats = [];
    let totalDistance = 0;

    for (let i = 0; i < orderedSpotIds.length; i++) {
      const fromId = orderedSpotIds[i];
      const toId = orderedSpotIds[(i + 1) % orderedSpotIds.length]; // 最后一段回到起点

      const { path } = shortestPath(graph, fromId, toId, mode || transportMode.value);
      const segLngLats = nodeIdsToLngLats(path, graph);

      // 避免重复添加连接点
      if (allLngLats.length > 0 && segLngLats.length > 0) {
        allLngLats.push(...segLngLats.slice(1));
      } else {
        allLngLats.push(...segLngLats);
      }

      // 累计距离
      for (let j = 0; j < segLngLats.length - 1; j++) {
        totalDistance += haversineDistance(segLngLats[j], segLngLats[j + 1]);
      }
    }

    // 绘制 TSP 路径（紫色渐变，带方向箭头）
    drawPolyline(allLngLats, { color: '#7b2cbf', weight: 5, showArrow: true });

    // 更新路线统计
    routeInfo.value = {
      type: 'tsp',
      orderedNames: order.map((idx) => targetSpots[idx].name),
      distance: (totalDistance / 1000).toFixed(2),
      duration: Math.ceil(cost),
      spotCount: targetSpots.length,
    };

    if (mapRef.value && allLngLats.length > 0) {
      mapRef.value.setFitView();
    }

    return { orderedSpots: order.map((idx) => targetSpots[idx]), cost };
  }

  /**
   * 设置交通模式（步行/自行车/电瓶车）
   * @param {string} mode TransportType 枚举值
   */
  function setTransportMode(mode) {
    transportMode.value = mode;
  }

  return {
    // 状态
    routeInfo,
    transportMode,
    // 方法
    planToSpot,
    planTSPRoute,
    clearRoute,
    setTransportMode,
    // 工具（供外部使用）
    TransportType,
  };
}
