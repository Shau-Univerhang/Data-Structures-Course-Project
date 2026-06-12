/**
 * KMP (Knuth-Morris-Pratt) 字符串匹配算法 — 用于美食模糊搜索
 * ————————————————————————————————————————
 * 算法思想：
 *   KMP 算法通过预处理模式串，构建 LPS（最长公共前后缀）数组，
 *   在匹配失败时利用已匹配的信息跳过不必要的比较，
 *   将暴力匹配的 O(N*M) 优化为 O(N+M)。
 *
 * 应用场景：
 *   用户在搜索框输入关键词，系统需要在每个美食商家的
 *   name（名称）、type（菜系）、tags（标签）等多个字段中
 *   进行模糊查找。使用 KMP 可避免重复扫描。
 *
 * 为什么用 KMP 而不是简单的 includes()：
 *   1. 课程要求展示算法能力
 *   2. KMP 预处理一次模式串，可复用于多条数据的匹配
 *   3. 更高效，尤其在模式串较长时
 */

/**
 * 构建 LPS (Longest Prefix Suffix) 数组
 * ————————————————————————————————————————
 * LPS[i] = 模式串 [0..i] 中，最长的"真前缀同时是真后缀"的长度
 *
 * 示例：pattern = "ABABC"
 *   i=0 'A'       → lps[0]=0
 *   i=1 'AB'      → lps[1]=0
 *   i=2 'ABA'     → lps[2]=1 (前缀"A"==后缀"A")
 *   i=3 'ABAB'    → lps[3]=2 (前缀"AB"==后缀"AB")
 *   i=4 'ABABC'   → lps[4]=0
 *
 * 时间复杂度：O(M)，M = pattern.length
 *
 * @param {string} pattern - 搜索关键词（已转为小写）
 * @returns {number[]} LPS 数组
 */
export function buildLPS(pattern) {
  const m = pattern.length
  if (m === 0) return []

  const lps = new Array(m).fill(0)
  let len = 0 // 当前已匹配的最长前缀长度
  let i = 1

  while (i < m) {
    if (pattern[i] === pattern[len]) {
      // 当前字符与"已匹配前缀的下一个字符"相同
      len++
      lps[i] = len
      i++
    } else {
      if (len !== 0) {
        // 回退到上一个可能的前缀位置（关键步骤！）
        len = lps[len - 1]
      } else {
        // len 已经是 0，无法继续回退
        lps[i] = 0
        i++
      }
    }
  }

  return lps
}

/**
 * KMP 字符串匹配
 * ————————————————————————————————————————
 * 在 text 中查找 pattern，返回是否找到。
 *
 * 时间复杂度：O(N + M)，N = text.length，M = pattern.length
 *
 * @param {string} text    - 被搜索的文本（已转为小写）
 * @param {string} pattern - 搜索关键词（已转为小写）
 * @param {number[]} lps   - 预计算的 LPS 数组（可选，复用）
 * @returns {boolean} 是否匹配成功
 */
export function kmpSearch(text, pattern, lps = null) {
  if (!pattern) return true // 空关键词匹配一切
  if (!text) return false

  const n = text.length
  const m = pattern.length
  if (m > n) return false

  // 如果未提供 LPS，现场构建
  const lpsArr = lps || buildLPS(pattern)

  let i = 0 // text 的指针
  let j = 0 // pattern 的指针

  while (i < n) {
    if (text[i] === pattern[j]) {
      // 当前字符匹配，两个指针都前进
      i++
      j++

      // 完整匹配到了 pattern
      if (j === m) {
        return true // 找到匹配！
        // 如果要找所有匹配位置，这里可以记录 (i - j) 然后 j = lpsArr[j - 1]
      }
    } else {
      if (j !== 0) {
        // 利用 LPS 跳过已匹配的部分
        j = lpsArr[j - 1]
      } else {
        // j 已经是 0，直接移动 text 指针
        i++
      }
    }
  }

  return false
}

/**
 * 多字段 KMP 模糊搜索
 * ————————————————————————————————————————
 * 将美食商家的 name、type、tags 拼接为搜索域，
 * 使用 KMP 算法进行关键词匹配。
 *
 * 匹配策略：
 *   1. 关键词为空 → 返回全部（不筛选）
 *   2. 关键词非空 → 在拼接字段中 KMP 匹配
 *   3. 支持部分匹配："肉夹馍" 可匹配到 "袁记肉夹馍·新快餐"
 *   4. 大小写不敏感
 *
 * 时间复杂度：O(F * (N + M))
 *   F = 美食数量，N = 搜索域平均长度，M = 关键词长度
 *
 * @param {Array}  foods   - 美食列表
 * @param {string} keyword - 搜索关键词
 * @returns {Array} 匹配的美食列表
 */
export function fuzzySearchFoods(foods, keyword) {
  // 空关键词 → 返回全部
  if (!keyword || !keyword.trim()) {
    return [...foods]
  }

  const pattern = keyword.trim().toLowerCase()
  if (pattern.length === 0) return [...foods]

  // 预计算 LPS 数组（复用，避免为每条数据重复计算）
  const lps = buildLPS(pattern)

  return foods.filter((food) => {
    // 构建搜索域：名称 + 菜系 + 标签 → 拼接为一个字符串
    const searchFields = [
      food.name || '',
      food.type || '',
      ...(food.tags || []),
    ]
      .filter(Boolean)
      .join(' ')
      .toLowerCase()

    // KMP 匹配
    return kmpSearch(searchFields, pattern, lps)
  })
}

/**
 * 基于 KMP 的多关键词搜索（空格分隔）
 * ————————————————————————————————————————
 * 用户输入"泡馍 清真"时，要求食品同时包含"泡馍"和"清真"两个词。
 * 多个关键词之间是 AND 关系。
 *
 * @param {Array}  foods   - 美食列表
 * @param {string} keyword - 空格分隔的多关键词
 * @returns {Array} 同时匹配所有关键词的美食列表
 */
export function multiKeywordSearch(foods, keyword) {
  if (!keyword || !keyword.trim()) return [...foods]

  const keywords = keyword
    .trim()
    .toLowerCase()
    .split(/\s+/)
    .filter(Boolean)

  if (keywords.length === 0) return [...foods]

  // 为每个关键词预计算 LPS
  const lpsCache = keywords.map((kw) => buildLPS(kw))

  return foods.filter((food) => {
    const searchFields = [
      food.name || '',
      food.type || '',
      ...(food.tags || []),
    ]
      .filter(Boolean)
      .join(' ')
      .toLowerCase()

    // 所有关键词都必须匹配（AND 逻辑）
    return keywords.every((kw, idx) => kmpSearch(searchFields, kw, lpsCache[idx]))
  })
}

export default fuzzySearchFoods
