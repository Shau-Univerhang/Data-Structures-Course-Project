/**
 * 堆（Heap）数据结构 — 用于 Top-K 局部排序
 * ————————————————————————————————————————
 * 算法思想：
 *   老师要求"不经过完全排序，就能排好前 10 的美食"。
 *   传统 Array.prototype.sort() 的时间复杂度是 O(N log N)，
 *   而堆选 Top-K 仅需 O(N log K)，当 K << N 时优势明显。
 *
 * 实现方案：小顶堆 + 大顶堆
 *   - 求 Top-K 最大（评分、热度）：使用容量为 K 的【小顶堆】
 *     堆顶是"当前 K 个中最差的"，新元素比堆顶好就替换
 *   - 求 Top-K 最小（距离）：使用容量为 K 的【大顶堆】
 *     堆顶是"当前 K 个中最远的"，新元素比堆顶近就替换
 *
 * 最终对堆内 K 个元素排序输出（O(K log K)，K=10 很小）
 */

/**
 * 通用堆类
 * 通过 compareFn 控制是小顶堆还是大顶堆
 *   - 小顶堆: compareFn = (a, b) => a.val - b.val   （a<b 时返回负数，a在b上方）
 *   - 大顶堆: compareFn = (a, b) => b.val - a.val
 */
class Heap {
  constructor(compareFn) {
    this._data = []
    this._cmp = compareFn
  }

  /** 堆中元素个数 */
  get size() {
    return this._data.length
  }

  /** 查看堆顶元素（不移除） */
  peek() {
    return this._data[0] ?? null
  }

  /**
   * 入堆
   * 时间复杂度 O(log K)
   */
  push(item) {
    this._data.push(item)
    this._siftUp(this._data.length - 1)
  }

  /**
   * 出堆（移除并返回堆顶）
   * 时间复杂度 O(log K)
   */
  pop() {
    if (this._data.length === 0) return null
    const root = this._data[0]
    const last = this._data.pop()
    if (this._data.length > 0) {
      this._data[0] = last
      this._siftDown(0)
    }
    return root
  }

  /**
   * 替换堆顶（相当于 pop + push，但只需一次 heapify）
   * 时间复杂度 O(log K)
   */
  replaceTop(item) {
    const old = this._data[0]
    this._data[0] = item
    this._siftDown(0)
    return old
  }

  /** 上浮：新元素从底部向上找到正确位置 */
  _siftUp(idx) {
    const item = this._data[idx]
    while (idx > 0) {
      const parentIdx = (idx - 1) >>> 1 // Math.floor((idx-1)/2)
      const parent = this._data[parentIdx]
      // 如果 item 比 parent "小"（compare 返回负数），则上浮
      if (this._cmp(item, parent) < 0) {
        this._data[idx] = parent
        idx = parentIdx
      } else {
        break
      }
    }
    this._data[idx] = item
  }

  /** 下沉：堆顶元素向下找到正确位置 */
  _siftDown(idx) {
    const item = this._data[idx]
    const half = this._data.length >>> 1
    while (idx < half) {
      let childIdx = (idx << 1) + 1 // 2*idx + 1 (左子节点)
      let child = this._data[childIdx]
      const rightIdx = childIdx + 1
      // 如果右子节点存在且比左子节点"小"，选右子节点
      if (rightIdx < this._data.length && this._cmp(this._data[rightIdx], child) < 0) {
        childIdx = rightIdx
        child = this._data[rightIdx]
      }
      // 如果 item 比子节点"小"或相等，停止下沉
      if (this._cmp(item, child) <= 0) break
      this._data[idx] = child
      idx = childIdx
    }
    this._data[idx] = item
  }

  /**
   * 导出堆内所有元素（不保证顺序）
   */
  toArray() {
    return [...this._data]
  }
}

/**
 * Top-K 选择器 —— 不经过完全排序选出前 K 个最优元素
 * ————————————————————————————————————————
 * @param {Array}  list      - 完整数据列表
 * @param {string} criterion - 排序标准: 'distance' | 'rating' | 'popularity'
 * @param {number} k         - 返回前 K 个（默认 10）
 * @returns {Array} 排序后的前 K 个元素
 *
 * 算法流程：
 *   1. 根据 criterion 确定比较方向
 *      - distance 越小越好 → 用大顶堆（堆顶是 K 个中距离最大的）
 *      - rating/popularity 越大越好 → 用小顶堆（堆顶是 K 个中评分/热度最小的）
 *   2. 遍历列表中的每个元素（共 N 个）
 *      - 堆未满 K 个 → 直接入堆
 *      - 堆已满 → 如果当前元素比堆顶"更好"，则替换堆顶
 *   3. 遍历完成后，堆内就是 Top-K 元素
 *   4. 对堆内 K 个元素做最终排序（仅 K 个元素排序，可忽略不计）
 *
 * 复杂度分析：
 *   - 时间：O(N log K + K log K) < O(N log N)（当 K << N）
 *   - 空间：O(K)
 *   - 完全避免了 Array.prototype.sort() 的全量排序
 */
export function getTopK(list, criterion = 'distance', k = 10) {
  if (!list || list.length === 0) return []

  // 如果数据量 ≤ K，直接对这少量数据排序即可（不需要堆）
  if (list.length <= k) {
    return [...list].sort(makeSortFn(criterion))
  }

  // ─── 步骤1: 构造合适的堆 ───
  let heap
  if (criterion === 'distance') {
    // 距离越小越好 → 大顶堆：堆顶是"最远"的那个
    // 平局时评分高者优先保留
    heap = new Heap((a, b) => b.distance - a.distance || (b.rating || 0) - (a.rating || 0))
  } else if (criterion === 'rating') {
    // 评分越大越好 → 小顶堆：堆顶是"评分最低"的那个
    // 平局时热度高者优先保留（热度高的更可能在堆深处，不易被替换）
    heap = new Heap((a, b) => a.rating - b.rating || (a.popularity || 0) - (b.popularity || 0))
  } else if (criterion === 'popularity') {
    // 热度越大越好 → 小顶堆：堆顶是"热度最低"的那个
    // 平局时评分高者优先保留
    heap = new Heap((a, b) => a.popularity - b.popularity || (a.rating || 0) - (b.rating || 0))
  } else {
    // 未知排序标准，fallback 到距离
    heap = new Heap((a, b) => b.distance - a.distance || (b.rating || 0) - (a.rating || 0))
  }

  // ─── 步骤2: 遍历所有元素，维护大小为 K 的堆 ───
  for (let i = 0; i < list.length; i++) {
    const item = list[i]

    // 跳过无效数据
    if (criterion === 'distance' && (item.distance == null || item.distance < 0)) continue
    if (criterion === 'rating' && (item.rating == null || item.rating < 0)) continue
    if (criterion === 'popularity' && (item.popularity == null || item.popularity < 0)) continue

    if (heap.size < k) {
      // 堆未满，直接入堆
      heap.push(item)
    } else {
      // 堆已满，判断是否需要替换
      const top = heap.peek()
      let shouldReplace = false

      if (criterion === 'distance') {
        // 大顶堆：堆顶是当前 K 个中距离最大的
        // 如果新元素距离更小，替换
        shouldReplace = item.distance < top.distance
      } else if (criterion === 'rating') {
        // 小顶堆：堆顶是当前 K 个中评分最低的
        // 如果新元素评分更高，替换
        shouldReplace = item.rating > top.rating
      } else if (criterion === 'popularity') {
        // 小顶堆：堆顶是当前 K 个中热度最低的
        shouldReplace = item.popularity > top.popularity
      }

      if (shouldReplace) {
        heap.replaceTop(item)
      }
    }
  }

  // ─── 步骤3: 取出堆内 K 个元素并排序 ───
  // 堆内是 K 个最优元素但无序，只需对这 K 个排序
  const topK = heap.toArray()
  topK.sort(makeSortFn(criterion))

  return topK
}

/** 获取排序标准对应的值 */
function getCriterionVal(item, criterion) {
  if (criterion === 'distance') return item.distance
  if (criterion === 'rating') return item.rating
  if (criterion === 'popularity') return item.popularity
  return item.distance
}

/**
 * 创建排序比较函数（用于最终 K 个元素的排序）
 */
function makeSortFn(criterion) {
  if (criterion === 'distance') {
    return (a, b) => (a.distance ?? Infinity) - (b.distance ?? Infinity)
  }
  if (criterion === 'rating') {
    return (a, b) => (b.rating ?? 0) - (a.rating ?? 0)
  }
  if (criterion === 'popularity') {
    return (a, b) => (b.popularity ?? 0) - (a.popularity ?? 0)
  }
  return (a, b) => (a.distance ?? Infinity) - (b.distance ?? Infinity)
}

/**
 * 验证 Top-K 算法的正确性
 * （开发调试用，可注释掉）
 */
export function validateTopK(list, criterion, k = 10) {
  const heapResult = getTopK(list, criterion, k)
  const fullSortResult = [...list]
    .filter((item) => {
      if (criterion === 'distance') return item.distance != null && item.distance >= 0
      if (criterion === 'rating') return item.rating != null && item.rating >= 0
      if (criterion === 'popularity') return item.popularity != null && item.popularity >= 0
      return true
    })
    .sort(makeSortFn(criterion))
    .slice(0, k)

  // 验证指标1：数量一致
  const sameLength = heapResult.length === fullSortResult.length

  // 验证指标2：堆选的每个元素，其排序值都不差于全排序的第K个元素
  // （允许边界值存在并列导致的集合差异，这是堆选Top-K的正确语义）
  const kthVal = fullSortResult.length > 0 ? getCriterionVal(fullSortResult[fullSortResult.length - 1], criterion) : null
  const allAtLeastKth = heapResult.every((item) => {
    if (criterion === 'distance') return (item.distance ?? Infinity) <= (kthVal ?? Infinity)
    return (getCriterionVal(item, criterion) ?? -Infinity) >= (kthVal ?? -Infinity)
  })
  const heapIdSet = new Set(heapResult.map((f) => f.id))
  const fullIdSet = new Set(fullSortResult.map((f) => f.id))
  // 验证指标3：集合大小一致（K个元素）
  const sameSize = heapResult.length === fullSortResult.length

  // 验证指标4：无"遗漏"——全排序Top-K中值严格大于kthVal的元素必须全部在堆结果中
  const strictBetterIds = fullSortResult
    .filter((f) => {
      const v = getCriterionVal(f, criterion)
      if (criterion === 'distance') return v < kthVal
      return v > kthVal
    })
    .map((f) => f.id)
  const noMissing = strictBetterIds.every((id) => heapIdSet.has(id))

  const isCorrect = sameLength && sameSize && allAtLeastKth && noMissing

  if (!isCorrect) {
    console.warn('[TopK Validation FAILED]', {
      criterion,
      sameLength,
      sameSize,
      allAtLeastKth,
      noMissing,
      kthVal,
      heapIds: heapResult.map((f) => f.id),
      fullSortIds: fullSortResult.map((f) => f.id),
    })
  }
  return isCorrect
}

export default getTopK
