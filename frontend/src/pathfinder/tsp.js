/**
 * tsp.js — 旅行商问题（TSP）求解器
 *
 * 算法：状态压缩动态规划（Held-Karp 算法）
 *
 * 问题定义：
 *   给定 n 个景点，从起点出发，访问所有景点恰好一次，最后返回起点，
 *   求总代价最小的访问顺序。
 *
 * 状态定义：
 *   dp[mask][i] = 已访问了 mask 所表示的景点集合，当前停在第 i 个景点时的最小代价。
 *   mask 是一个 n 位二进制数，第 j 位为 1 表示第 j 个景点已被访问。
 *
 * 状态转移：
 *   dp[mask | (1 << j)][j] = min(dp[mask][i] + cost[i][j])
 *   其中 j 是 mask 中尚未访问的景点。
 *
 * 时间复杂度：O(n² × 2ⁿ)，适用于 n ≤ 20 的场景（景点数量）。
 * 空间复杂度：O(n × 2ⁿ)
 *
 * 注意：当 n > 15 时建议改用贪心启发式算法（见 greedyTSP）。
 */

const INF = Infinity;

/**
 * 状态压缩 DP 求解 TSP（精确算法）
 *
 * @param {number[][]} costMatrix  n×n 代价矩阵，costMatrix[i][j] = 从第 i 个节点到第 j 个节点的代价
 * @param {number}     startIndex  起点在节点数组中的下标（默认 0）
 * @returns {{
 *   order: number[],  // 最优访问顺序（下标数组，含起点，不含回程）
 *   cost: number,     // 总代价（含回程）
 * }}
 */
export function tspDP(costMatrix, startIndex = 0) {
  const n = costMatrix.length;

  if (n === 0) return { order: [], cost: 0 };
  if (n === 1) return { order: [startIndex], cost: 0 };

  // dp[mask][i]：已访问集合为 mask，当前在节点 i 时的最小代价
  // 使用 Float64Array 提升性能
  const dp = Array.from({ length: 1 << n }, () => new Float64Array(n).fill(INF));
  // parent[mask][i]：记录到达状态 (mask, i) 的前驱节点，用于路径重建
  const parent = Array.from({ length: 1 << n }, () => new Int16Array(n).fill(-1));

  // 初始状态：从起点出发，只访问了起点
  dp[1 << startIndex][startIndex] = 0;

  // 枚举所有状态（按 mask 从小到大）
  for (let mask = 0; mask < (1 << n); mask++) {
    // 起点必须在已访问集合中
    if (!(mask & (1 << startIndex))) continue;

    for (let i = 0; i < n; i++) {
      // 当前节点 i 必须在已访问集合中
      if (!(mask & (1 << i))) continue;
      if (dp[mask][i] === INF) continue;

      // 尝试从 i 出发，访问下一个未访问的节点 j
      for (let j = 0; j < n; j++) {
        // j 不能已经被访问
        if (mask & (1 << j)) continue;
        if (costMatrix[i][j] === INF) continue;

        const newMask = mask | (1 << j);
        const newCost = dp[mask][i] + costMatrix[i][j];

        // 状态转移：若新代价更小，则更新
        if (newCost < dp[newMask][j]) {
          dp[newMask][j] = newCost;
          parent[newMask][j] = i; // 记录前驱：到达 (newMask, j) 是从 i 转移来的
        }
      }
    }
  }

  // 所有节点都已访问时的 mask
  const fullMask = (1 << n) - 1;

  // 找到最优终点（从哪个节点回到起点代价最小）
  let bestCost = INF;
  let lastNode = -1;
  for (let i = 0; i < n; i++) {
    if (i === startIndex) continue;
    if (dp[fullMask][i] === INF) continue;
    const totalCost = dp[fullMask][i] + costMatrix[i][startIndex];
    if (totalCost < bestCost) {
      bestCost = totalCost;
      lastNode = i;
    }
  }

  // 若无法完成回路（图不连通），返回贪心结果
  if (lastNode === -1) {
    return greedyTSP(costMatrix, startIndex);
  }

  // 路径重建：从终点沿 parent 链回溯
  const order = [];
  let cur = lastNode;
  let curMask = fullMask;

  while (cur !== -1) {
    order.unshift(cur);
    const prev = parent[curMask][cur];
    curMask = curMask ^ (1 << cur); // 从集合中移除当前节点
    cur = prev;
  }

  return { order, cost: bestCost };
}

/**
 * 贪心启发式 TSP（最近邻算法）
 *
 * 适用于节点数较多（n > 15）时的快速近似解。
 * 每次从当前节点出发，选择代价最小的未访问节点。
 *
 * 时间复杂度：O(n²)
 *
 * @param {number[][]} costMatrix
 * @param {number}     startIndex
 * @returns {{ order: number[], cost: number }}
 */
export function greedyTSP(costMatrix, startIndex = 0) {
  const n = costMatrix.length;
  const visited = new Array(n).fill(false);
  const order = [startIndex];
  visited[startIndex] = true;
  let totalCost = 0;
  let current = startIndex;

  for (let step = 1; step < n; step++) {
    let nearest = -1;
    let nearestCost = INF;

    // 找到距当前节点最近的未访问节点
    for (let j = 0; j < n; j++) {
      if (!visited[j] && costMatrix[current][j] < nearestCost) {
        nearestCost = costMatrix[current][j];
        nearest = j;
      }
    }

    if (nearest === -1) break; // 图不连通，提前终止
    visited[nearest] = true;
    order.push(nearest);
    totalCost += nearestCost;
    current = nearest;
  }

  // 加上回程代价
  totalCost += costMatrix[current][startIndex];

  return { order, cost: totalCost };
}

/**
 * 主入口：根据节点数量自动选择算法
 *
 * n ≤ 12：使用精确的状态压缩 DP（Held-Karp）
 * n > 12：使用贪心最近邻启发式
 *
 * @param {number[][]} costMatrix  代价矩阵
 * @param {number}     startIndex  起点下标
 * @returns {{ order: number[], cost: number }}
 */
export function solveTSP(costMatrix, startIndex = 0) {
  const n = costMatrix.length;
  if (n <= 12) {
    return tspDP(costMatrix, startIndex);
  }
  return greedyTSP(costMatrix, startIndex);
}

/**
 * 从景点数组和代价函数构建代价矩阵
 *
 * @param {Array}    nodes       节点数组
 * @param {Function} costFn      costFn(nodeA, nodeB) → number，两节点间代价
 * @returns {number[][]}         n×n 代价矩阵
 */
export function buildCostMatrix(nodes, costFn) {
  const n = nodes.length;
  return Array.from({ length: n }, (_, i) =>
    Array.from({ length: n }, (_, j) => (i === j ? 0 : costFn(nodes[i], nodes[j])))
  );
}
