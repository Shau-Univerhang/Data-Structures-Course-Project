/**
 * 美食数据管道 —— 过滤 → 模糊搜索 → Top-K 局部排序
 * ————————————————————————————————————————
 * 这是附近美食推荐的核心数据流：
 *
 *  原始美食列表 (30-50条)
 *       │
 *       ▼
 *  [1] 菜系过滤 (type filter)
 *       │  用户点击「陕菜正餐」「面食」等标签
 *       ▼
 *  [2] KMP 模糊搜索 (keyword search)
 *       │  用户在输入框键入关键词
 *       ▼
 *  [3] 堆选 Top-K 局部排序 (heap-based top-K)
 *       │  按距离/评分/热度排序，不经过完全排序
 *       ▼
 *  最终输出 Top-10 结果 → 渲染列表 + 绘制地图 Marker
 *
 * 每一步都保持纯函数风格，便于测试和维护。
 */

import { fuzzySearchFoods, multiKeywordSearch } from './kmpFuzzySearch.js'
import { getTopK } from './heapTopK.js'

/**
 * 菜系类型过滤
 * ————————————————————————————————————————
 * @param {Array}  foods     - 美食列表
 * @param {string} typeFilter - 菜系过滤条件（'' 或 '全部' 表示不过滤）
 * @returns {Array} 过滤后的列表
 */
export function filterByType(foods, typeFilter) {
  if (!typeFilter || typeFilter === '全部' || typeFilter === 'all') {
    return [...foods]
  }
  return foods.filter((f) => f.type === typeFilter)
}

/**
 * 完整数据处理管道
 * ————————————————————————————————————————
 * 按顺序执行：菜系过滤 → KMP 模糊搜索 → Top-K 局部排序
 *
 * @param {Object}  options
 * @param {Array}   options.foods      - 原始美食列表
 * @param {string}  options.typeFilter - 菜系过滤条件
 * @param {string}  options.keyword    - 模糊搜索关键词
 * @param {string}  options.sortBy     - 排序标准: 'distance' | 'rating' | 'popularity'
 * @param {number}  options.topK       - 返回前 K 条（默认 10）
 * @returns {Object} { results, stats }
 *   - results: 最终的前 K 条数据
 *   - stats:   { total, filtered, searched, final } 各阶段数量
 */
export function runFoodPipeline({
  foods = [],
  typeFilter = '',
  keyword = '',
  sortBy = 'distance',
  topK = 10,
} = {}) {
  // 记录各阶段数量（用于调试和 UI 展示）
  const stats = {
    total: foods.length,
    filtered: 0,
    searched: 0,
    final: 0,
  }

  // ─── 阶段1: 菜系过滤 ───
  let result = filterByType(foods, typeFilter)
  stats.filtered = result.length

  // ─── 阶段2: KMP 模糊搜索 ───
  // 支持空格分隔的多关键词 AND 搜索
  if (keyword && keyword.trim()) {
    const trimmedKeyword = keyword.trim()
    if (trimmedKeyword.includes(' ')) {
      // 多关键词搜索（空格分隔）
      result = multiKeywordSearch(result, trimmedKeyword)
    } else {
      // 单关键词搜索
      result = fuzzySearchFoods(result, trimmedKeyword)
    }
  }
  stats.searched = result.length

  // ─── 阶段3: 堆选 Top-K 局部排序 ───
  // ★ 核心算法：不经过 Array.prototype.sort() 全量排序 ★
  result = getTopK(result, sortBy, topK)
  stats.final = result.length

  return {
    results: result,
    stats,
  }
}

/**
 * 获取菜系过滤器选项列表
 * ————————————————————————————————————————
 * 从美食数据中提取所有唯一的 type 值
 *
 * @param {Array} foods - 美食列表
 * @returns {string[]} 菜系类型数组
 */
export function getCuisineTypeOptions(foods) {
  const types = new Set(foods.map((f) => f.type).filter(Boolean))
  return Array.from(types).sort()
}

export default runFoodPipeline
