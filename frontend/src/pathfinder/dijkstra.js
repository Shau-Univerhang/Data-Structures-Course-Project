/**
 * dijkstra.js — Dijkstra 单源最短路径算法
 *
 * 核心思想：
 *   维护一个"已确定最短距离"的节点集合 S，和一个"候选节点"优先队列。
 *   每次从优先队列中取出当前距离最小的节点 u，将其加入 S，
 *   然后对 u 的所有邻居 v 执行"松弛"操作：
 *     若 dist[u] + weight(u→v) < dist[v]，则更新 dist[v] 并记录前驱。
 *
 * 时间复杂度：O((V + E) log V)，使用最小堆优先队列。
 */

import { edgeWeight } from './graph.js';

/**
 * 最小堆优先队列（简单实现）
 * 存储 { id, priority } 对象，按 priority 升序排列。
 */
class MinHeap {
  constructor() {
    this._heap = [];
  }

  push(item) {
    this._heap.push(item);
    this._bubbleUp(this._heap.length - 1);
  }

  pop() {
    const top = this._heap[0];
    const last = this._heap.pop();
    if (this._heap.length > 0) {
      this._heap[0] = last;
      this._siftDown(0);
    }
    return top;
  }

  get size() {
    return this._heap.length;
  }

  _bubbleUp(i) {
    while (i > 0) {
      const parent = (i - 1) >> 1;
      if (this._heap[parent].priority <= this._heap[i].priority) break;
      [this._heap[parent], this._heap[i]] = [this._heap[i], this._heap[parent]];
      i = parent;
    }
  }

  _siftDown(i) {
    const n = this._heap.length;
    while (true) {
      let smallest = i;
      const l = 2 * i + 1;
      const r = 2 * i + 2;
      if (l < n && this._heap[l].priority < this._heap[smallest].priority) smallest = l;
      if (r < n && this._heap[r].priority < this._heap[smallest].priority) smallest = r;
      if (smallest === i) break;
      [this._heap[smallest], this._heap[i]] = [this._heap[i], this._heap[smallest]];
      i = smallest;
    }
  }
}

/**
 * Dijkstra 算法
 *
 * @param {import('./graph.js').Graph} graph         图实例
 * @param {string|number}              sourceId      起点节点 ID
 * @param {string|null}                transportMode 交通方式过滤（null = 不过滤）
 * @returns {{
 *   dist: Map<id, number>,   // 起点到各节点的最短权重（分钟）
 *   prev: Map<id, id|null>,  // 最短路径前驱节点表
 * }}
 */
export function dijkstra(graph, sourceId, transportMode = null) {
  // dist[v] = 起点到 v 的当前最短权重，初始化为 +∞
  const dist = new Map();
  // prev[v] = 在最短路径中，v 的前驱节点 ID
  const prev = new Map();
  // visited[v] = 是否已确定最短距离
  const visited = new Set();

  // 初始化所有节点距离为无穷大
  for (const id of graph.nodeIds()) {
    dist.set(id, Infinity);
    prev.set(id, null);
  }
  dist.set(sourceId, 0);

  // 优先队列：{ id, priority }，priority = 当前已知最短距离
  const pq = new MinHeap();
  pq.push({ id: sourceId, priority: 0 });

  while (pq.size > 0) {
    const { id: u, priority: d } = pq.pop();

    // 如果取出的距离已经过时（被更短路径替代），跳过
    if (visited.has(u)) continue;
    visited.add(u);

    // 如果当前距离已大于已知最短距离，剪枝
    if (d > dist.get(u)) continue;

    // 松弛操作：遍历 u 的所有出边
    const edges = graph.getEdges(u, transportMode);
    for (const edge of edges) {
      const v = edge.to;
      if (visited.has(v)) continue;

      // 计算经过 u 到达 v 的新距离
      const newDist = dist.get(u) + edgeWeight(edge);

      // 松弛：若新距离更短，则更新
      if (newDist < dist.get(v)) {
        dist.set(v, newDist);
        prev.set(v, u);
        // 将 v 以新距离加入优先队列
        pq.push({ id: v, priority: newDist });
      }
    }
  }

  return { dist, prev };
}

/**
 * 从 Dijkstra 结果中重建从 source 到 target 的完整路径
 *
 * @param {Map}           prev     dijkstra() 返回的前驱表
 * @param {string|number} sourceId 起点 ID
 * @param {string|number} targetId 终点 ID
 * @returns {Array<string|number>} 节点 ID 数组（含起点和终点），若不可达则返回 []
 */
export function reconstructPath(prev, sourceId, targetId) {
  const path = [];
  let cur = targetId;

  // 从终点沿前驱链回溯到起点
  while (cur !== null) {
    path.unshift(cur);
    if (cur === sourceId) break;
    cur = prev.get(cur);
    // 防止无限循环（不可达情况）
    if (cur === undefined) return [];
  }

  // 验证路径确实从 source 开始
  if (path[0] !== sourceId) return [];
  return path;
}

/**
 * 便捷函数：计算图中两点间的最短路径
 *
 * @param {import('./graph.js').Graph} graph
 * @param {string|number}              sourceId
 * @param {string|number}              targetId
 * @param {string|null}                transportMode
 * @returns {{
 *   path: Array<string|number>,  // 节点 ID 序列
 *   cost: number,                // 总权重（分钟）
 * }}
 */
export function shortestPath(graph, sourceId, targetId, transportMode = null) {
  const { dist, prev } = dijkstra(graph, sourceId, transportMode);
  const path = reconstructPath(prev, sourceId, targetId);
  return {
    path,
    cost: dist.get(targetId) ?? Infinity,
  };
}
