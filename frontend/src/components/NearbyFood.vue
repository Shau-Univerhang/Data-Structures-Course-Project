<template>
  <div class="nearby-food-panel">
    <!-- 头部 -->
    <div class="food-header">
      <div class="food-title-row">
        <div class="food-icon">🍜</div>
        <div class="food-title-text">
          <h3>附近美食</h3>
          <p v-if="activeSpot" class="food-subtitle">
            {{ activeSpot.name }} · Top {{ displayFoods.length }} 推荐
          </p>
          <p v-else class="food-subtitle">点击景点探索周边美味</p>
        </div>
        <div v-if="displayFoods.length > 0" class="food-count">{{ displayFoods.length }}</div>
      </div>
    </div>

    <!-- 搜索栏 -->
    <div class="food-search-bar" :class="{ disabled: !hasData }">
      <span class="search-icon">🔍</span>
      <input
        v-model="localKeyword"
        type="text"
        placeholder="搜索美食名称、菜系..."
        :disabled="!hasData"
        @input="onKeywordInput"
      />
      <button v-if="localKeyword" class="clear-btn" @click="clearKeyword">×</button>
    </div>

    <!-- 排序标签 -->
    <div class="food-sort-bar" :class="{ disabled: !hasData }">
      <button
        v-for="opt in sortOptions"
        :key="opt.value"
        class="sort-chip"
        :class="{ active: localSortBy === opt.value }"
        :disabled="!hasData"
        @click="setSort(opt.value)"
      >
        <span class="sort-icon">{{ opt.icon }}</span>
        {{ opt.label }}
      </button>
    </div>

    <!-- 菜系过滤标签（NEW!） -->
    <div v-if="cuisineTypeOptions.length > 0" class="food-cuisine-filter" :class="{ disabled: !hasData }">
      <button
        v-for="ctype in cuisineTypeOptions"
        :key="ctype"
        class="cuisine-chip"
        :class="{ active: activeTypeFilter === ctype }"
        :disabled="!hasData"
        @click="toggleTypeFilter(ctype)"
      >
        {{ ctype }}
      </button>
    </div>

    <!-- 管道统计（调试/展示用，展示算法的中间步骤） -->
    <div v-if="pipelineStats && displayFoods.length > 0" class="pipeline-stats">
      <span class="stat-item">
        <span class="stat-dot"></span>
        全部 {{ pipelineStats.total }} → 过滤 {{ pipelineStats.filtered }} → 搜索 {{ pipelineStats.searched }} → Top {{ pipelineStats.final }}
      </span>
    </div>

    <!-- 内容区域 -->
    <div class="food-content">
      <!-- 未选中景点 -->
      <div v-if="!hasData" class="food-empty-state">
        <div class="empty-illustration">🗺️</div>
        <p class="empty-title">选中左侧景点后，这里会显示附近美食</p>
        <p class="empty-desc">我们通过堆排序算法为您推荐周边 Top 10 人气餐厅</p>
      </div>

      <!-- 加载中 -->
      <div v-else-if="loading" class="food-loading">
        <div class="loading-spinner"></div>
        <p>正在搜寻周边美食...</p>
      </div>

      <!-- 错误 -->
      <div v-else-if="error" class="food-error">
        <span class="error-icon">⚠️</span>
        <p>{{ error }}</p>
        <button class="retry-btn" @click="$emit('retry')">重试</button>
      </div>

      <!-- 无结果 -->
      <div v-else-if="displayFoods.length === 0" class="food-empty-state">
        <div class="empty-illustration">🍽️</div>
        <p class="empty-title">暂无匹配的美食商家</p>
        <p class="empty-desc">尝试切换排序方式、菜系标签或更换关键词</p>
      </div>

      <!-- 美食列表 -->
      <div v-else class="food-list">
        <div
          v-for="(food, index) in displayFoods"
          :key="food.id"
          class="food-card"
          :class="{ active: activeFoodId === food.id, 'top-three': index < 3 }"
          @click="onFoodClick(food)"
        >
          <!-- 排名标识 -->
          <div class="rank-badge" :class="`rank-${index + 1}`">
            <span v-if="index < 3">{{ ['🥇', '🥈', '🥉'][index] }}</span>
            <span v-else>{{ index + 1 }}</span>
          </div>

          <!-- 主体内容 -->
          <div class="food-card-body">
            <div class="food-name-row">
              <h4 class="food-name">{{ food.name }}</h4>
              <span v-if="food.price_range" class="price-tag">{{ food.price_range }}</span>
            </div>

            <div class="food-meta-row">
              <div class="rating-group">
                <div class="stars">
                  <span
                    v-for="i in 5"
                    :key="i"
                    class="star"
                    :class="{ filled: i <= Math.round(food.rating || 0) }"
                  >★</span>
                </div>
                <span class="rating-score">{{ (food.rating || 0).toFixed(1) }}</span>
              </div>
              <span class="distance-badge">
                <span class="dist-icon">📍</span>
                {{ formatDistance(food.distance || food.distance_m) }}
              </span>
            </div>

            <div class="food-tags-row">
              <span v-if="food.type || food.cuisine_type" class="cuisine-tag">
                {{ food.type || food.cuisine_type }}
              </span>
              <span v-if="food.popularity || food.heat_score" class="heat-tag">
                <span class="fire-icon">🔥</span>
                {{ food.popularity || food.heat_score }}
              </span>
              <span
                v-for="tag in (food.tags || []).slice(0, 2)"
                :key="tag"
                class="feature-tag"
              >
                {{ tag }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { runFoodPipeline, getCuisineTypeOptions as buildCuisineOptions } from '../utils/foodDataPipeline.js'
import { getFoodsBySpot } from '../data/xianFoodMock.js'

// ═══════════════════════════════════════════════════════════
// Props（保持向后兼容）
// ═══════════════════════════════════════════════════════════
const props = defineProps({
  // 景点信息（需包含 belongToSpot 字段以自动加载数据）
  activeSpot: { type: Object, default: null },

  // 管道模式：传入全量数据，组件内部执行过滤→搜索→Top-K
  allFoods: { type: Array, default: null },

  // 传统模式（向后兼容）：父组件预处理好的数据直接展示
  foods: { type: Array, default: () => [] },

  loading: { type: Boolean, default: false },
  error: { type: String, default: '' },
  activeFoodId: { type: [Number, String], default: null },
  sortBy: { type: String, default: 'distance' },
  keyword: { type: String, default: '' },
})

const emit = defineEmits([
  'select-food',
  'update:sortBy',
  'update:keyword',
  'retry',
])

// ═══════════════════════════════════════════════════════════
// 排序选项
// ═══════════════════════════════════════════════════════════
const sortOptions = [
  { label: '距离最近', value: 'distance', icon: '📍' },
  { label: '评分最高', value: 'rating', icon: '⭐' },
  { label: '热度最高', value: 'popularity', icon: '🔥' },
]

// ═══════════════════════════════════════════════════════════
// 内部响应式状态
// ═══════════════════════════════════════════════════════════
const localSortBy = ref(props.sortBy)
const localKeyword = ref(props.keyword)
const activeTypeFilter = ref('') // 空字符串 = 不筛选（「全部」）

// 同步外部 prop → 内部
watch(() => props.sortBy, (v) => { localSortBy.value = v })
watch(() => props.keyword, (v) => { localKeyword.value = v })

// ═══════════════════════════════════════════════════════════
// 数据源：根据 activeSpot.belongToSpot 自动加载
// ═══════════════════════════════════════════════════════════
const spotFoods = computed(() => {
  // 父组件显式传了 allFoods → 优先用
  if (props.allFoods && props.allFoods.length > 0) {
    if (props.activeSpot?.belongToSpot) {
      return props.allFoods.filter((f) => f.belongToSpot === props.activeSpot.belongToSpot)
    }
    return props.allFoods
  }

  // 从 xianFoodMock 自动加载
  if (props.activeSpot?.belongToSpot) {
    return getFoodsBySpot(props.activeSpot.belongToSpot)
  }

  return []
})

// ═══════════════════════════════════════════════════════════
// 菜系过滤选项（动态提取）
// ═══════════════════════════════════════════════════════════
const cuisineTypeOptions = computed(() => {
  const source = spotFoods.value.length > 0 ? spotFoods.value : props.foods
  if (!source || source.length === 0) return []
  return buildCuisineOptions(source)
})

// ═══════════════════════════════════════════════════════════
// ★ 核心计算属性：管道 Pipeline ★
//
// 流程：菜系过滤 → KMP 模糊搜索 → 堆选 Top-K 局部排序
//
// 关键：
//   - runFoodPipeline 内部调用 getTopK() 使用 Heap 选 Top-K，
//     不会对整个数组做 Array.prototype.sort() 全量排序
//   - KMP 算法进行 O(N+M) 多字段模糊匹配
// ═══════════════════════════════════════════════════════════
const pipelineResult = computed(() => {
  const source = spotFoods.value.length > 0 ? spotFoods.value : props.foods
  if (!source || source.length === 0) {
    return { results: [], stats: { total: 0, filtered: 0, searched: 0, final: 0 } }
  }
  return runFoodPipeline({
    foods: source,
    typeFilter: activeTypeFilter.value,
    keyword: localKeyword.value,
    sortBy: localSortBy.value,
    topK: 10,
  })
})

// 最终展示列表
const displayFoods = computed(() => pipelineResult.value.results)

// 管道统计
const pipelineStats = computed(() => pipelineResult.value.stats)

// 是否有数据
const hasData = computed(() => {
  return !!(props.activeSpot && (spotFoods.value.length > 0 || props.foods.length > 0))
})

// ═══════════════════════════════════════════════════════════
// 方法
// ═══════════════════════════════════════════════════════════

const setSort = (value) => {
  localSortBy.value = value
  emit('update:sortBy', value)
}

let keywordTimer = null
const onKeywordInput = () => {
  clearTimeout(keywordTimer)
  keywordTimer = setTimeout(() => {
    emit('update:keyword', localKeyword.value)
  }, 300)
}

const clearKeyword = () => {
  localKeyword.value = ''
  emit('update:keyword', '')
}

/** 切换菜系过滤：点击已选中 → 取消过滤；点击其他 → 切换 */
const toggleTypeFilter = (ctype) => {
  activeTypeFilter.value = activeTypeFilter.value === ctype ? '' : ctype
}

const onFoodClick = (food) => {
  emit('select-food', food)
}

const formatDistance = (m) => {
  if (!m && m !== 0) return '未知'
  if (m < 1000) return `${Math.round(m)}m`
  return `${(m / 1000).toFixed(1)}km`
}
</script>

<style scoped>
.nearby-food-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: rgba(10, 10, 26, 0.72);
  backdrop-filter: blur(20px);
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}

/* ─── 头部 ─── */
.food-header {
  padding: 16px 16px 10px;
  flex-shrink: 0;
}

.food-title-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.food-icon {
  width: 38px;
  height: 38px;
  border-radius: 12px;
  background: linear-gradient(135deg, rgba(255, 159, 67, 0.2), rgba(255, 107, 107, 0.2));
  border: 1px solid rgba(255, 159, 67, 0.25);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
}

.food-title-text {
  flex: 1;
  min-width: 0;
}

.food-title-text h3 {
  font-size: 15px;
  font-weight: 700;
  color: var(--text-primary, #fff);
  margin: 0;
  line-height: 1.3;
}

.food-subtitle {
  font-size: 12px;
  color: var(--text-secondary, rgba(255,255,255,0.5));
  margin: 2px 0 0;
  line-height: 1.3;
}

.food-count {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: linear-gradient(135deg, #ff9f43, #ff6b6b);
  color: #fff;
  font-size: 12px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

/* ─── 搜索栏 ─── */
.food-search-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 16px 10px;
  padding: 0 12px;
  height: 38px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.food-search-bar:focus-within {
  border-color: rgba(0, 212, 255, 0.4);
  background: rgba(255, 255, 255, 0.07);
}

.food-search-bar.disabled {
  opacity: 0.4;
  pointer-events: none;
}

.search-icon {
  font-size: 13px;
  opacity: 0.6;
  flex-shrink: 0;
}

.food-search-bar input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  color: var(--text-primary, #fff);
  font-size: 13px;
  min-width: 0;
}

.food-search-bar input::placeholder {
  color: var(--text-secondary, rgba(255,255,255,0.4));
}

.clear-btn {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.15);
  border: none;
  color: var(--text-secondary, rgba(255,255,255,0.6));
  font-size: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  line-height: 1;
}

/* ─── 排序标签 ─── */
.food-sort-bar {
  display: flex;
  gap: 8px;
  padding: 0 16px 8px;
  flex-shrink: 0;
  overflow-x: auto;
}

.food-sort-bar.disabled {
  opacity: 0.4;
  pointer-events: none;
}

.food-sort-bar::-webkit-scrollbar {
  display: none;
}

.sort-chip {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.04);
  color: var(--text-secondary, rgba(255,255,255,0.6));
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
  flex-shrink: 0;
}

.sort-chip:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.15);
}

.sort-chip.active {
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.18), rgba(123, 44, 191, 0.18));
  border-color: rgba(0, 212, 255, 0.4);
  color: var(--primary-color, #00d4ff);
  font-weight: 600;
}

.sort-icon {
  font-size: 11px;
}

/* ─── 菜系过滤标签（NEW!） ─── */
.food-cuisine-filter {
  display: flex;
  gap: 6px;
  padding: 0 16px 10px;
  flex-shrink: 0;
  overflow-x: auto;
  flex-wrap: wrap;
}

.food-cuisine-filter.disabled {
  opacity: 0.4;
  pointer-events: none;
}

.food-cuisine-filter::-webkit-scrollbar {
  display: none;
}

.cuisine-chip {
  padding: 4px 10px;
  border-radius: 14px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.04);
  color: var(--text-secondary, rgba(255,255,255,0.6));
  font-size: 11px;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
  flex-shrink: 0;
}

.cuisine-chip:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(0, 212, 255, 0.2);
  color: #fff;
}

.cuisine-chip.active {
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.2), rgba(123, 44, 191, 0.2));
  border-color: var(--primary-color, #00d4ff);
  color: var(--primary-color, #00d4ff);
  font-weight: 600;
  text-shadow: 0 0 8px rgba(0, 212, 255, 0.3);
}

/* ─── 管道统计 ─── */
.pipeline-stats {
  padding: 0 16px 8px;
  flex-shrink: 0;
}

.stat-item {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 10px;
  color: rgba(255, 255, 255, 0.3);
  font-family: 'SF Mono', 'Fira Code', monospace;
}

.stat-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #00d4ff;
  opacity: 0.5;
}

/* ─── 内容区域 ─── */
.food-content {
  flex: 1;
  overflow-y: auto;
  padding: 0 16px 16px;
}

.food-content::-webkit-scrollbar {
  width: 4px;
}

.food-content::-webkit-scrollbar-track {
  background: transparent;
}

.food-content::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
}

/* ─── 空状态 ─── */
.food-empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  text-align: center;
}

.empty-illustration {
  font-size: 48px;
  margin-bottom: 12px;
  opacity: 0.7;
}

.empty-title {
  font-size: 14px;
  color: var(--text-primary, rgba(255,255,255,0.8));
  margin: 0 0 6px;
}

.empty-desc {
  font-size: 12px;
  color: var(--text-secondary, rgba(255,255,255,0.45));
  margin: 0;
}

/* ─── 加载 ─── */
.food-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 50px 20px;
  gap: 12px;
}

.loading-spinner {
  width: 28px;
  height: 28px;
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-top-color: var(--primary-color, #00d4ff);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.food-loading p {
  font-size: 13px;
  color: var(--text-secondary, rgba(255,255,255,0.5));
  margin: 0;
}

/* ─── 错误 ─── */
.food-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  gap: 8px;
  text-align: center;
}

.error-icon {
  font-size: 32px;
}

.food-error p {
  font-size: 13px;
  color: var(--text-secondary, rgba(255,255,255,0.6));
  margin: 0;
}

.retry-btn {
  margin-top: 8px;
  padding: 6px 18px;
  border-radius: 16px;
  border: 1px solid rgba(0, 212, 255, 0.3);
  background: rgba(0, 212, 255, 0.1);
  color: var(--primary-color, #00d4ff);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.retry-btn:hover {
  background: rgba(0, 212, 255, 0.2);
}

/* ─── 美食列表 ─── */
.food-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.food-card {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 14px;
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.food-card::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 14px;
  padding: 1px;
  background: linear-gradient(135deg, rgba(255,255,255,0.08), transparent 50%);
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.25s ease;
}

.food-card:hover::before,
.food-card.active::before {
  opacity: 1;
}

.food-card:hover {
  background: rgba(255, 255, 255, 0.07);
  border-color: rgba(0, 212, 255, 0.2);
  transform: translateY(-1px);
}

.food-card.active {
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.08), rgba(123, 44, 191, 0.06));
  border-color: rgba(0, 212, 255, 0.3);
}

.food-card.top-three {
  border-color: rgba(255, 159, 67, 0.15);
}

.food-card.top-three:hover {
  border-color: rgba(255, 159, 67, 0.3);
}

/* ─── 排名徽章 ─── */
.rank-badge {
  width: 32px;
  height: 32px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 700;
  color: var(--text-secondary, rgba(255,255,255,0.5));
  flex-shrink: 0;
  margin-top: 2px;
}

.rank-badge.rank-1 {
  background: linear-gradient(135deg, rgba(255, 215, 0, 0.15), rgba(255, 159, 67, 0.15));
  border-color: rgba(255, 215, 0, 0.3);
  color: #ffd700;
}

.rank-badge.rank-2 {
  background: linear-gradient(135deg, rgba(192, 192, 192, 0.15), rgba(169, 169, 169, 0.15));
  border-color: rgba(192, 192, 192, 0.3);
  color: #c0c0c0;
}

.rank-badge.rank-3 {
  background: linear-gradient(135deg, rgba(205, 127, 50, 0.15), rgba(180, 110, 40, 0.15));
  border-color: rgba(205, 127, 50, 0.3);
  color: #cd7f32;
}

/* ─── 卡片主体 ─── */
.food-card-body {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.food-name-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.food-name {
  font-size: 14px;
  font-weight: 700;
  color: var(--text-primary, #fff);
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.3;
}

.price-tag {
  font-size: 11px;
  color: var(--primary-color, #00d4ff);
  background: rgba(0, 212, 255, 0.1);
  padding: 2px 8px;
  border-radius: 8px;
  white-space: nowrap;
  flex-shrink: 0;
  font-weight: 600;
}

.food-meta-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.rating-group {
  display: flex;
  align-items: center;
  gap: 6px;
}

.stars {
  display: flex;
  gap: 1px;
}

.star {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.15);
  line-height: 1;
}

.star.filled {
  color: #ffc107;
}

.rating-score {
  font-size: 12px;
  font-weight: 700;
  color: #ffc107;
}

.distance-badge {
  display: flex;
  align-items: center;
  gap: 3px;
  font-size: 11px;
  color: var(--text-secondary, rgba(255,255,255,0.5));
  background: rgba(255, 255, 255, 0.05);
  padding: 3px 8px;
  border-radius: 8px;
  white-space: nowrap;
  flex-shrink: 0;
}

.dist-icon {
  font-size: 10px;
}

.food-tags-row {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.cuisine-tag {
  font-size: 11px;
  color: #ff9f43;
  background: rgba(255, 159, 67, 0.1);
  padding: 3px 8px;
  border-radius: 8px;
  font-weight: 500;
}

.heat-tag {
  display: flex;
  align-items: center;
  gap: 2px;
  font-size: 11px;
  color: #ff6b6b;
  background: rgba(255, 107, 107, 0.1);
  padding: 3px 8px;
  border-radius: 8px;
  font-weight: 500;
}

.fire-icon {
  font-size: 10px;
}

.feature-tag {
  font-size: 11px;
  color: var(--text-secondary, rgba(255,255,255,0.55));
  background: rgba(255, 255, 255, 0.05);
  padding: 3px 8px;
  border-radius: 8px;
}
</style>
