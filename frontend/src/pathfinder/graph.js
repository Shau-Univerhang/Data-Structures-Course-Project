/**
 * graph.js — 基于邻接表的图结构
 *
 * 节点（Node）：包含景点 ID、名称、经纬度坐标
 * 边（Edge）：包含距离、理想速度、拥挤度、交通方式
 */

/**
 * 交通方式枚举
 */
export const TransportType = {
  WALK: 'walk',       // 步行
  BIKE: 'bike',       // 自行车
  SCOOTER: 'scooter', // 电瓶车
};

/**
 * 创建一个图节点
 * @param {string|number} id   景点唯一 ID
 * @param {string}        name 景点名称
 * @param {number}        lng  经度
 * @param {number}        lat  纬度
 * @returns {Object} 节点对象
 */
export function createNode(id, name, lng, lat) {
  return { id, name, lnglat: [lng, lat] };
}

/**
 * 创建一条有向边
 * @param {string|number} to            目标节点 ID
 * @param {number}        distance      距离（米）
 * @param {number}        idealSpeed    理想速度（米/分钟）
 * @param {number}        congestion    拥挤度 0~1（0=畅通，1=完全堵塞）
 * @param {string}        transportType 交通方式（TransportType 枚举值）
 * @returns {Object} 边对象
 */
export function createEdge(to, distance, idealSpeed, congestion, transportType) {
  return { to, distance, idealSpeed, congestion, transportType };
}

/**
 * 计算边的动态权重
 *
 * 公式：Weight = Distance / (IdealSpeed × (1 - Congestion))
 *
 * 物理含义：拥挤度越高，有效速度越低，通行时间越长，权重越大。
 * 当 congestion → 1 时权重趋向无穷大（道路不可通行）。
 *
 * @param {Object} edge 边对象
 * @returns {number} 权重（分钟，即预计通行时间）
 */
export function edgeWeight(edge) {
  // 防止除以零：有效速度最低取 0.01
  const effectiveSpeed = edge.idealSpeed * Math.max(1 - edge.congestion, 0.01);
  return edge.distance / effectiveSpeed;
}

/**
 * Graph 类 — 有向加权图（邻接表实现）
 */
export class Graph {
  constructor() {
    /** @type {Map<string|number, Object>} 节点表：id → node */
    this.nodes = new Map();
    /** @type {Map<string|number, Object[]>} 邻接表：id → edge[] */
    this.adjList = new Map();
  }

  /**
   * 添加节点
   * @param {Object} node createNode() 返回的节点对象
   */
  addNode(node) {
    this.nodes.set(node.id, node);
    if (!this.adjList.has(node.id)) {
      this.adjList.set(node.id, []);
    }
  }

  /**
   * 添加有向边（from → to）
   * @param {string|number} fromId 起点 ID
   * @param {Object}        edge   createEdge() 返回的边对象
   */
  addEdge(fromId, edge) {
    if (!this.adjList.has(fromId)) {
      this.adjList.set(fromId, []);
    }
    this.adjList.get(fromId).push(edge);
  }

  /**
   * 添加无向边（双向）
   * @param {string|number} aId
   * @param {string|number} bId
   * @param {number}        distance
   * @param {number}        idealSpeed
   * @param {number}        congestion
   * @param {string}        transportType
   */
  addUndirectedEdge(aId, bId, distance, idealSpeed, congestion, transportType) {
    this.addEdge(aId, createEdge(bId, distance, idealSpeed, congestion, transportType));
    this.addEdge(bId, createEdge(aId, distance, idealSpeed, congestion, transportType));
  }

  /**
   * 获取某节点的所有出边，可按交通方式过滤
   * @param {string|number} nodeId
   * @param {string|null}   transportFilter 若为 null 则不过滤
   * @returns {Object[]} 边数组
   */
  getEdges(nodeId, transportFilter = null) {
    const edges = this.adjList.get(nodeId) || [];
    if (!transportFilter) return edges;
    return edges.filter((e) => e.transportType === transportFilter);
  }

  /** 获取节点对象 */
  getNode(nodeId) {
    return this.nodes.get(nodeId);
  }

  /** 所有节点 ID 列表 */
  nodeIds() {
    return [...this.nodes.keys()];
  }
}

/**
 * 根据景点数组自动构建图（全连接，用 Haversine 公式估算距离）
 *
 * 适用于没有真实路网数据时的演示场景。
 * 每对景点之间建立双向边，默认步行速度 80 m/min，拥挤度 0.2。
 *
 * @param {Array<{id, name, location: [lng, lat]}>} spots 景点数组
 * @param {string} transportType 默认交通方式
 * @returns {Graph}
 */
export function buildGraphFromSpots(spots, transportType = TransportType.WALK) {
  const graph = new Graph();

  // 默认速度配置（米/分钟）
  const speedMap = {
    [TransportType.WALK]: 80,      // 步行约 4.8 km/h
    [TransportType.BIKE]: 250,     // 自行车约 15 km/h
    [TransportType.SCOOTER]: 400,  // 电瓶车约 24 km/h
  };
  const speed = speedMap[transportType] || 80;

  // 添加所有节点
  spots.forEach((spot) => {
    const [lng, lat] = spot.location || [0, 0];
    graph.addNode(createNode(spot.id, spot.name, lng, lat));
  });

  // 全连接：每对节点之间建立双向边
  for (let i = 0; i < spots.length; i++) {
    for (let j = i + 1; j < spots.length; j++) {
      const a = spots[i];
      const b = spots[j];
      const dist = haversineDistance(a.location, b.location);
      // 默认拥挤度 0.2（轻度拥挤）
      graph.addUndirectedEdge(a.id, b.id, dist, speed, 0.2, transportType);
    }
  }

  return graph;
}

/**
 * Haversine 公式计算两点球面距离（米）
 * @param {[number, number]} lnglatA [经度, 纬度]
 * @param {[number, number]} lnglatB [经度, 纬度]
 * @returns {number} 距离（米）
 */
export function haversineDistance([lng1, lat1], [lng2, lat2]) {
  const R = 6371000; // 地球半径（米）
  const toRad = (deg) => (deg * Math.PI) / 180;
  const dLat = toRad(lat2 - lat1);
  const dLng = toRad(lng2 - lng1);
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLng / 2) ** 2;
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}
