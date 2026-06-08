<template>
  <div class="diary-library-page">
    <Navbar />
    
    <!-- 背景装饰 -->
    <div class="gradient-blobs">
      <div class="blob blob-1"></div>
      <div class="blob blob-2"></div>
      <div class="blob blob-3"></div>
    </div>
    
    <!-- 主内容 -->
    <main class="library-content">
      <!-- 页面标题 -->
      <div class="library-header">
        <h1 class="page-title">📚 日记库</h1>
        <p class="page-subtitle">发现来自全国各地旅行者的精彩故事</p>
      </div>
      
      <!-- 筛选栏 -->
      <div class="filter-section">
        <!-- 搜索 & 目的地 -->
        <div class="filter-group search-group">
          <!-- 全文搜索 -->
          <div class="search-input-wrapper">
            <svg class="search-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="11" cy="11" r="8"/>
              <path d="m21 21-4.35-4.35"/>
            </svg>
            <input 
              type="text" 
              class="search-input"
              placeholder="全文搜索日记标题或内容..." 
              v-model="searchQuery"
              @keyup.enter="doSearch"
            />
            <button v-if="searchQuery" class="clear-btn" @click="clearSearch">×</button>
          </div>
          <!-- 目的地输入 -->
          <div class="destination-input-wrapper">
            <span class="dest-icon">📍</span>
            <input 
              type="text" 
              class="destination-input"
              placeholder="输入目的地，如：北京、上海" 
              v-model="destinationQuery"
              @keyup.enter="doDestinationSearch"
            />
          </div>
        </div>
        
        <!-- 城市筛选 -->
        <div class="filter-group">
          <span class="filter-label">📍 城市</span>
          <div class="filter-options">
            <button 
              :class="['filter-btn', { active: selectedCity === null }]"
              @click="selectCity(null)"
            >
              全部
            </button>
            <button 
              v-for="city in displayCities" 
              :key="city.id"
              :class="['filter-btn', { active: selectedCity === city.id }]"
              @click="selectCity(city.id)"
            >
              {{ city.name }}
              <span class="count">({{ city.diary_count }})</span>
            </button>
            <button 
              v-if="hasMoreCities"
              class="filter-btn more-btn"
              @click="showAllCities = !showAllCities"
            >
              {{ showAllCities ? '收起' : '更多...' }}
            </button>
          </div>
        </div>
        
        <!-- 类型筛选 -->
        <div class="filter-group">
          <span class="filter-label">📝 类型</span>
          <div class="filter-options">
            <button 
              :class="['filter-btn', { active: selectedType === null }]"
              @click="selectType(null)"
            >
              全部
            </button>
            <button 
              v-for="type in diaryTypes" 
              :key="type.value"
              :class="['filter-btn', { active: selectedType === type.value }]"
              @click="selectType(type.value)"
            >
              {{ type.emoji }} {{ type.label }}
            </button>
          </div>
        </div>
        
        <!-- 排序 -->
        <div class="filter-group sort-group">
          <span class="filter-label">⇅ 排序</span>
          <div class="filter-options">
            <button 
              v-for="option in sortOptions" 
              :key="option.value"
              :class="['filter-btn', { active: sortBy === option.value }]"
              @click="selectSort(option.value)"
            >
              {{ option.label }}
            </button>
          </div>
        </div>
        
        <!-- 搜索状态提示 -->
        <div v-if="isSearching" class="search-status">
          <span>🔍 搜索 "{{ searchQuery }}"，共 {{ total }} 条结果</span>
          <button class="back-to-library-btn" @click="backToLibrary">返回日记库</button>
        </div>
        <div v-if="isDestinationSearching" class="search-status">
          <span>📍 目的地 "{{ destinationQuery }}"，共 {{ total }} 条结果</span>
          <button class="back-to-library-btn" @click="backToLibrary">返回日记库</button>
        </div>
      </div>
      
      <!-- 日记网格 -->
      <div class="diary-grid" v-if="diaries.length > 0">
        <div 
          v-for="diary in diaries" 
          :key="diary.id"
          class="diary-card"
          @click="viewDiary(diary.id)"
        >
          <!-- 封面 -->
          <div class="card-cover">
            <img 
              v-if="diary.cover" 
              :src="diary.cover" 
              :alt="diary.title"
              loading="lazy"
            />
            <div v-else class="cover-placeholder">
              <span class="placeholder-emoji">{{ getTypeEmoji(diary.type) }}</span>
            </div>
            <!-- 类型标签 -->
            <span class="type-badge">{{ getTypeLabel(diary.type) }}</span>
          </div>
          
          <!-- 内容 -->
          <div class="card-content">
            <h3 class="card-title" v-html="isSearching && diary.snippet_title ? diary.snippet_title : diary.title"></h3>
            
            <!-- 搜索摘要 -->
            <p v-if="isSearching && diary.snippet_content" class="search-snippet" v-html="diary.snippet_content"></p>
            
            <!-- 城市标签 -->
            <div class="city-tags" v-if="diary.cities && diary.cities.length > 0">
              <span 
                v-for="city in diary.cities.slice(0, 2)" 
                :key="city"
                class="city-tag"
              >
                📍 {{ city }}
              </span>
              <span v-if="diary.cities.length > 2" class="city-tag more">
                +{{ diary.cities.length - 2 }}
              </span>
            </div>
            
            <!-- 作者信息 -->
            <div class="card-author">
              <div class="author-avatar">
                <img v-if="diary.avatar" :src="diary.avatar" :alt="diary.author" />
                <span v-else>{{ diary.author?.[0] || '👤' }}</span>
              </div>
              <span class="author-name">{{ diary.author }}</span>
            </div>
            
            <!-- 统计 -->
            <div class="card-stats">
              <span class="stat" title="评分">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/>
                </svg>
                {{ diary.rating || '0.0' }}
              </span>
              <span class="stat" title="浏览">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                  <circle cx="12" cy="12" r="3"/>
                </svg>
                {{ formatNumber(diary.view_count) }}
              </span>
              <span class="stat" title="评论">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/>
                </svg>
                {{ diary.comment_count || 0 }}
              </span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 空状态 -->
      <div v-else-if="!loading" class="empty-state">
        <div class="empty-icon">📖</div>
        <h3>暂无日记</h3>
        <p>还没有符合筛选条件的日记，换个条件试试吧~</p>
        <button class="reset-btn" @click="resetFilters">重置筛选</button>
      </div>
      
      <!-- 加载中 -->
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>加载中...</p>
      </div>
      
      <!-- 分页 -->
      <div class="pagination" v-if="totalPages > 1 && !loading">
        <button 
          :disabled="currentPage === 1"
          class="page-btn"
          @click="goToPage(currentPage - 1)"
        >
          ← 上一页
        </button>
        
        <div class="page-numbers">
          <button 
            v-for="page in displayedPages" 
            :key="page"
            :class="['page-number', { active: page === currentPage }]"
            @click="goToPage(page)"
          >
            {{ page }}
          </button>
        </div>
        
        <button 
          :disabled="currentPage === totalPages"
          class="page-btn"
          @click="goToPage(currentPage + 1)"
        >
          下一页 →
        </button>
      </div>
    </main>
    
    <!-- 返回顶部 -->
    <button 
      v-show="showBackToTop"
      class="back-to-top"
      @click="scrollToTop"
    >
      ↑
    </button>
    
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import Navbar from '../components/Navbar.vue'

const router = useRouter()

// 状态
const diaries = ref([])
const cities = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const selectedCity = ref(null)
const selectedType = ref(null)
const sortBy = ref('hot')
const showAllCities = ref(false)
const showBackToTop = ref(false)

// 搜索 & 目的地
const searchQuery = ref('')
const destinationQuery = ref('')
const isSearching = ref(false)
const isDestinationSearching = ref(false)

// 日记类型
const diaryTypes = [
  { value: 'travel', label: '行程', emoji: '🏃' },
  { value: 'food', label: '美食', emoji: '🍜' },
  { value: 'photo', label: '摄影', emoji: '📸' },
  { value: 'notes', label: '随笔', emoji: '💭' }
]

// 排序选项（新增兴趣推荐）
const sortOptions = [
  { value: 'hot', label: '🔥 最热' },
  { value: 'new', label: '🕐 最新' },
  { value: 'rating', label: '⭐ 评分' },
  { value: 'interest', label: '💡 兴趣推荐' }
]

// 计算属性
const totalPages = computed(() => Math.ceil(total.value / pageSize.value))

const displayCities = computed(() => {
  if (showAllCities.value) {
    return cities.value
  }
  // 只显示前10个城市
  return cities.value.slice(0, 10)
})

const hasMoreCities = computed(() => cities.value.length > 10)

const displayedPages = computed(() => {
  const pages = []
  const maxDisplay = 5
  let start = Math.max(1, currentPage.value - Math.floor(maxDisplay / 2))
  let end = Math.min(totalPages.value, start + maxDisplay - 1)
  
  if (end - start + 1 < maxDisplay) {
    start = Math.max(1, end - maxDisplay + 1)
  }
  
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  return pages
})

// 方法
const fetchCities = async () => {
  try {
    const response = await fetch('/api/library/diaries/cities?min_count=1')
    if (response.ok) {
      const data = await response.json()
      cities.value = data.cities || []
    }
  } catch (error) {
    console.error('获取城市列表失败:', error)
  }
}

const fetchDiaries = async () => {
  loading.value = true
  isSearching.value = false
  isDestinationSearching.value = false
  
  try {
    // 如果有搜索词，使用 FTS 全文搜索
    if (searchQuery.value) {
      const params = new URLSearchParams({
        q: searchQuery.value,
        page: currentPage.value.toString(),
        page_size: pageSize.value.toString(),
        sort: sortBy.value === 'hot' ? 'hot' : sortBy.value === 'new' ? 'date' : 'relevance'
      })
      
      const response = await fetch(`/api/diaries/search?${params}`)
      if (response.ok) {
        const data = await response.json()
        diaries.value = (data.diaries || []).map(d => ({
          id: d.id,
          title: d.title,
          cover: d.cover || d.cover_image,
          author: d.author,
          cities: d.cities || [],
          rating: d.avg_rating || d.rating || 0,
          view_count: d.view_count || 0,
          comment_count: d.comment_count || 0,
          created_at: d.created_at,
          snippet_title: d.snippet_title,
          snippet_content: d.snippet_content
        }))
        total.value = data.total || 0
        isSearching.value = true
      }
      loading.value = false
      return
    }
    
    // 如果有目的地查询，使用目的地接口
    if (destinationQuery.value) {
      const params = new URLSearchParams({
        destination: destinationQuery.value,
        sort: sortBy.value === 'interest' ? 'hot' : sortBy.value,
        page: currentPage.value.toString(),
        page_size: pageSize.value.toString()
      })
      
      const response = await fetch(`/api/diaries/by-destination?${params}`)
      if (response.ok) {
        const data = await response.json()
        diaries.value = (data.diaries || []).map(d => ({
          id: d.id,
          title: d.title,
          cover: d.cover || d.cover_image,
          author: d.author,
          cities: d.cities || [],
          rating: d.avg_rating || d.rating || 0,
          view_count: d.view_count || 0,
          comment_count: d.comment_count || 0,
          created_at: d.created_at
        }))
        total.value = data.total || 0
        isDestinationSearching.value = true
      }
      loading.value = false
      return
    }
    
    // 默认：使用日记库接口
    const params = new URLSearchParams({
      page: currentPage.value.toString(),
      page_size: pageSize.value.toString(),
      sort: sortBy.value === 'interest' ? 'hot' : sortBy.value
    })
    
    if (selectedCity.value) {
      params.append('city_id', selectedCity.value.toString())
    }
    if (selectedType.value) {
      params.append('diary_type', selectedType.value)
    }
    
    const response = await fetch(`/api/library/diaries?${params}`)
    if (response.ok) {
      const data = await response.json()
      diaries.value = data.diaries || []
      total.value = data.total || 0
    }
  } catch (error) {
    console.error('获取日记列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 全文搜索
const doSearch = () => {
  if (!searchQuery.value.trim()) {
    return
  }
  currentPage.value = 1
  destinationQuery.value = ''
  fetchDiaries()
}

// 目的地搜索
const doDestinationSearch = () => {
  if (!destinationQuery.value.trim()) {
    return
  }
  currentPage.value = 1
  searchQuery.value = ''
  fetchDiaries()
}

// 清除搜索
const clearSearch = () => {
  searchQuery.value = ''
  backToLibrary()
}

// 返回日记库
const backToLibrary = () => {
  searchQuery.value = ''
  destinationQuery.value = ''
  isSearching.value = false
  isDestinationSearching.value = false
  currentPage.value = 1
  fetchDiaries()
}

const selectCity = (cityId) => {
  selectedCity.value = cityId
  currentPage.value = 1
  fetchDiaries()
}

const selectType = (type) => {
  selectedType.value = type
  currentPage.value = 1
  fetchDiaries()
}

const selectSort = (sort) => {
  sortBy.value = sort
  currentPage.value = 1
  fetchDiaries()
}

const goToPage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
    fetchDiaries()
    scrollToTop()
  }
}

const resetFilters = () => {
  selectedCity.value = null
  selectedType.value = null
  sortBy.value = 'hot'
  currentPage.value = 1
  backToLibrary()
}

const viewDiary = (id) => {
  router.push(`/diary/${id}`)
}

const getTypeEmoji = (type) => {
  const found = diaryTypes.find(t => t.value === type)
  return found?.emoji || '📝'
}

const getTypeLabel = (type) => {
  const found = diaryTypes.find(t => t.value === type)
  return found?.label || '日记'
}

const formatNumber = (num) => {
  if (num >= 10000) {
    return (num / 10000).toFixed(1) + 'w'
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'k'
  }
  return num.toString()
}

const scrollToTop = () => {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const handleScroll = () => {
  showBackToTop.value = window.scrollY > 300
}

// 城市坐标映射表
const cityCoordinates = {
  '北京': { lat: 39.9042, lng: 116.4074 },
  '上海': { lat: 31.2304, lng: 121.4737 },
  '广州': { lat: 23.1291, lng: 113.2644 },
  '深圳': { lat: 22.5431, lng: 114.0579 },
  '成都': { lat: 30.5728, lng: 104.0668 },
  '杭州': { lat: 30.2741, lng: 120.1551 },
  '西安': { lat: 34.3416, lng: 108.9398 },
  '重庆': { lat: 29.5630, lng: 106.5516 },
  '武汉': { lat: 30.5928, lng: 114.3055 },
  '南京': { lat: 32.0603, lng: 118.7969 },
  '京都': { lat: 35.0116, lng: 135.7681 },
  '东京': { lat: 35.6762, lng: 139.6503 },
  '大阪': { lat: 34.6937, lng: 135.5023 },
  '首尔': { lat: 37.5665, lng: 126.9780 },
  '曼谷': { lat: 13.7563, lng: 100.5018 },
  '新加坡': { lat: 1.3521, lng: 103.8198 },
  '巴黎': { lat: 48.8566, lng: 2.3522 },
  '伦敦': { lat: 51.5074, lng: -0.1278 },
  '纽约': { lat: 40.7128, lng: -74.0060 },
  '洛杉矶': { lat: 34.0522, lng: -118.2437 },
  '悉尼': { lat: -33.8688, lng: 151.2093 },
  '雷克雅未克': { lat: 64.1466, lng: -21.9426 },
  '冰岛': { lat: 64.9631, lng: -19.0208 }
}

// 从日记中提取城市印痕数据
const diaryTraces = computed(() => {
  const traces = []
  const cityMap = new Map()
  
  diaries.value.forEach(diary => {
    const cityName = extractCityFromDiary(diary)
    if (cityName && cityCoordinates[cityName]) {
      if (!cityMap.has(cityName)) {
        cityMap.set(cityName, {
          name: cityName,
          lat: cityCoordinates[cityName].lat,
          lng: cityCoordinates[cityName].lng,
          diaries: []
        })
        traces.push(cityMap.get(cityName))
      }
      cityMap.get(cityName).diaries.push({
        id: diary.id,
        title: diary.title,
        cover: diary.cover_image || diary.images?.[0] || '',
        created_at: diary.created_at
      })
    }
  })
  
  // 如果没有真实数据，返回演示数据
  if (traces.length === 0) {
    return [
      {
        name: '京都',
        lat: 35.0116,
        lng: 135.7681,
        diaries: [
          { id: 1, title: '京都：千年古都的秋日私语', cover: 'https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=800&q=80', created_at: '2024-11-15' }
        ]
      },
      {
        name: '成都',
        lat: 30.5728,
        lng: 104.0668,
        diaries: [
          { id: 2, title: '成都美食探店：藏在巷子里的烟火气', cover: 'https://images.unsplash.com/photo-1563245372-f21724e3856d?w=800&q=80', created_at: '2024-12-01' }
        ]
      },
      {
        name: '雷克雅未克',
        lat: 64.1466,
        lng: -21.9426,
        diaries: [
          { id: 3, title: '冰岛环岛自驾：追逐极光的14天', cover: 'https://images.unsplash.com/photo-1531366936337-7c912a4589a7?w=800&q=80', created_at: '2024-10-20' }
        ]
      }
    ]
  }
  
  return traces
})

// 从日记中提取城市名
const extractCityFromDiary = (diary) => {
  if (!diary) return null
  
  const title = diary.title || ''
  for (const city of Object.keys(cityCoordinates)) {
    if (title.includes(city)) {
      return city
    }
  }
  
  const content = diary.content || ''
  for (const city of Object.keys(cityCoordinates)) {
    if (content.includes(city)) {
      return city
    }
  }
  
  return null
}

// 生命周期
onMounted(() => {
  fetchCities()
  fetchDiaries()
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})

// 监听筛选变化（可选：添加防抖）
watch([selectedCity, selectedType, sortBy], () => {
  // 已在各自方法中处理
})
</script>

<style scoped>
.diary-library-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #0a0a1a 0%, #12121f 50%, #0a0a1a 100%);
  position: relative;
  overflow-x: hidden;
  padding-top: 80px;
}

/* 背景装饰 */
.gradient-blobs {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  z-index: 0;
  overflow: hidden;
}

.blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(100px);
  opacity: 0.12;
  animation: float 20s ease-in-out infinite;
}

.blob-1 {
  width: 500px;
  height: 500px;
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  top: -150px;
  left: -150px;
  animation-delay: 0s;
}

.blob-2 {
  width: 400px;
  height: 400px;
  background: linear-gradient(135deg, #ff6b6b, #ffd93d);
  top: 30%;
  right: -100px;
  animation-delay: -5s;
}

.blob-3 {
  width: 450px;
  height: 450px;
  background: linear-gradient(135deg, #4ecdc4, #44a08d);
  bottom: 10%;
  left: 5%;
  animation-delay: -10s;
}

@keyframes float {
  0%, 100% { transform: translate(0, 0) scale(1); }
  25% { transform: translate(30px, -30px) scale(1.05); }
  50% { transform: translate(-20px, 20px) scale(0.95); }
  75% { transform: translate(20px, 10px) scale(1.02); }
}

/* 主内容 */
.library-content {
  max-width: 1280px;
  margin: 0 auto;
  padding: 40px 24px 80px;
  position: relative;
  z-index: 1;
}

/* 页面标题 */
.library-header {
  text-align: center;
  margin-bottom: 48px;
}

.page-title {
  font-size: 36px;
  font-weight: 700;
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 12px;
}

.page-subtitle {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.5);
}

/* 筛选栏 */
.filter-section {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 32px;
}

/* 搜索组 */
.search-group {
  display: flex;
  gap: 16px;
  align-items: stretch;
}

.search-input-wrapper {
  flex: 2;
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 16px;
  color: rgba(255, 255, 255, 0.3);
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding: 12px 44px 12px 44px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  color: #fff;
  font-size: 14px;
  outline: none;
  transition: all 0.3s ease;
}

.search-input:focus {
  border-color: rgba(0, 212, 255, 0.4);
  background: rgba(255, 255, 255, 0.08);
  box-shadow: 0 0 0 3px rgba(0, 212, 255, 0.1);
}

.search-input::placeholder {
  color: rgba(255, 255, 255, 0.35);
}

.clear-btn {
  position: absolute;
  right: 12px;
  width: 24px;
  height: 24px;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 50%;
  color: rgba(255, 255, 255, 0.6);
  font-size: 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.clear-btn:hover {
  background: rgba(255, 71, 87, 0.3);
  color: #ff4757;
}

.destination-input-wrapper {
  flex: 1;
  position: relative;
  display: flex;
  align-items: center;
}

.dest-icon {
  position: absolute;
  left: 14px;
  font-size: 16px;
  pointer-events: none;
}

.destination-input {
  width: 100%;
  padding: 12px 14px 12px 38px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  color: #fff;
  font-size: 14px;
  outline: none;
  transition: all 0.3s ease;
}

.destination-input:focus {
  border-color: rgba(0, 212, 255, 0.4);
  background: rgba(255, 255, 255, 0.08);
  box-shadow: 0 0 0 3px rgba(0, 212, 255, 0.1);
}

.destination-input::placeholder {
  color: rgba(255, 255, 255, 0.35);
}

/* 搜索状态 */
.search-status {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: rgba(0, 212, 255, 0.08);
  border: 1px solid rgba(0, 212, 255, 0.2);
  border-radius: 10px;
  margin-top: 16px;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
}

.back-to-library-btn {
  padding: 6px 14px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s;
}

.back-to-library-btn:hover {
  background: rgba(255, 255, 255, 0.15);
  color: #fff;
}

/* 搜索摘要 */
.search-snippet {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
  line-height: 1.5;
  margin: 8px 0 12px 0;
}

.search-snippet :deep(em) {
  color: #00d4ff;
  font-style: normal;
  font-weight: 600;
  background: rgba(0, 212, 255, 0.15);
  padding: 1px 4px;
  border-radius: 3px;
}

.card-title :deep(em) {
  color: #00d4ff;
  font-style: normal;
  font-weight: 600;
  background: rgba(0, 212, 255, 0.15);
  padding: 1px 4px;
  border-radius: 3px;
}

.filter-group {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 20px;
}

.filter-group:last-child {
  margin-bottom: 0;
}

.filter-label {
  font-size: 14px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.7);
  white-space: nowrap;
  padding-top: 8px;
  min-width: 60px;
}

.filter-options {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  flex: 1;
}

.filter-btn {
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.filter-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
}

.filter-btn.active {
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  border-color: transparent;
  color: #fff;
}

.filter-btn .count {
  opacity: 0.6;
  font-size: 12px;
}

.filter-btn.more-btn {
  background: transparent;
  border-style: dashed;
  color: rgba(255, 255, 255, 0.5);
}

/* 日记网格 */
.diary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
  margin-bottom: 48px;
}

.diary-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
}

.diary-card:hover {
  transform: translateY(-4px);
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.15);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
}

.card-cover {
  position: relative;
  width: 100%;
  height: 180px;
  overflow: hidden;
}

.card-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.diary-card:hover .card-cover img {
  transform: scale(1.05);
}

.cover-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.1), rgba(123, 44, 191, 0.1));
}

.placeholder-emoji {
  font-size: 48px;
}

.type-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  padding: 4px 10px;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  font-size: 12px;
  color: #fff;
}

.card-content {
  padding: 16px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #fff;
  margin-bottom: 12px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.city-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 12px;
}

.city-tag {
  padding: 4px 8px;
  background: rgba(0, 212, 255, 0.1);
  border: 1px solid rgba(0, 212, 255, 0.2);
  border-radius: 8px;
  font-size: 12px;
  color: #00d4ff;
}

.city-tag.more {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.5);
}

.card-author {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.author-avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
}

.author-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.author-name {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
}

.card-stats {
  display: flex;
  gap: 16px;
}

.stat {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
}

.stat svg {
  opacity: 0.7;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 80px 20px;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 20px;
}

.empty-state h3 {
  font-size: 20px;
  font-weight: 600;
  color: #fff;
  margin-bottom: 8px;
}

.empty-state p {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 24px;
}

.reset-btn {
  padding: 12px 24px;
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  border: none;
  border-radius: 24px;
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.reset-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 212, 255, 0.3);
}

/* 加载中 */
.loading-state {
  text-align: center;
  padding: 80px 20px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(255, 255, 255, 0.1);
  border-top-color: #00d4ff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 分页 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
}

.page-btn {
  padding: 10px 20px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.page-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
}

.page-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.page-numbers {
  display: flex;
  gap: 8px;
}

.page-number {
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.page-number:hover {
  background: rgba(255, 255, 255, 0.1);
}

.page-number.active {
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  border-color: transparent;
  color: #fff;
}

/* 返回顶部 */
.back-to-top {
  position: fixed;
  bottom: 100px;
  right: 24px;
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  border: none;
  border-radius: 50%;
  color: #fff;
  font-size: 20px;
  cursor: pointer;
  box-shadow: 0 4px 20px rgba(0, 212, 255, 0.3);
  transition: all 0.3s ease;
  z-index: 100;
}

.back-to-top:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 30px rgba(0, 212, 255, 0.4);
}

/* 探索印痕入口 - 更醒目的设计 */
.earth-trace-entry {
  position: fixed;
  bottom: 28px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 50;
  cursor: pointer;
  padding: 3px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  background-size: 200% 200%;
  border-radius: 60px;
  animation: gradient-shift 4s ease infinite, glow-pulse 2s ease-in-out infinite;
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.4);
}

.earth-entry-content {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 28px;
  background: linear-gradient(135deg, rgba(20, 20, 35, 0.98) 0%, rgba(30, 30, 50, 0.98) 100%);
  backdrop-filter: blur(20px);
  border-radius: 58px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.earth-trace-entry:hover .earth-entry-content {
  background: linear-gradient(135deg, rgba(30, 30, 50, 0.98) 0%, rgba(40, 40, 65, 0.98) 100%);
  transform: scale(1.03);
  border-color: rgba(255, 255, 255, 0.25);
}

.earth-entry-icon {
  font-size: 28px;
  filter: drop-shadow(0 0 8px rgba(102, 126, 234, 0.6));
  animation: earth-float 3s ease-in-out infinite;
}

.earth-entry-text h3 {
  font-size: 15px;
  font-weight: 700;
  color: #fff;
  margin: 0;
  letter-spacing: 0.5px;
  background: linear-gradient(135deg, #fff 0%, #c9d6ff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.earth-entry-text p {
  font-size: 12px;
  color: rgba(201, 214, 255, 0.7);
  margin: 4px 0 0 0;
  font-weight: 400;
}

.earth-entry-arrow {
  font-size: 20px;
  color: #fff;
  transition: all 0.3s ease;
  opacity: 0.8;
}

.earth-trace-entry:hover .earth-entry-arrow {
  transform: translateX(6px);
  opacity: 1;
}

@keyframes glow-pulse {
  0%, 100% {
    box-shadow: 0 8px 32px rgba(102, 126, 234, 0.4), 0 0 0 0 rgba(102, 126, 234, 0.4);
  }
  50% {
    box-shadow: 0 8px 32px rgba(102, 126, 234, 0.6), 0 0 0 8px rgba(102, 126, 234, 0);
  }
}

@keyframes gradient-shift {
  0%, 100% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
}

@keyframes earth-float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-3px);
  }
}

/* 3D地球弹窗 */
.earth-globe-modal {
  position: fixed;
  inset: 0;
  z-index: 1000;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-earth-btn {
  position: absolute;
  top: 24px;
  right: 24px;
  width: 48px;
  height: 48px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  z-index: 1001;
}

.close-earth-btn:hover {
  background: rgba(255, 71, 87, 0.3);
  border-color: rgba(255, 71, 87, 0.5);
  transform: rotate(90deg);
}

.fade-scale-enter-active,
.fade-scale-leave-active {
  transition: all 0.4s ease;
}

.fade-scale-enter-from,
.fade-scale-leave-to {
  opacity: 0;
  transform: scale(0.9);
}

/* 响应式 */
@media (max-width: 768px) {
  .library-content {
    padding: 24px 16px 60px;
  }
  
  .page-title {
    font-size: 28px;
  }
  
  .search-group {
    flex-direction: column;
    gap: 12px;
  }
  
  .filter-group {
    flex-direction: column;
    gap: 12px;
  }
  
  .filter-label {
    padding-top: 0;
  }
  
  .search-status {
    flex-direction: column;
    gap: 8px;
    text-align: center;
  }
  
  .diary-grid {
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
    gap: 16px;
  }
  
  .pagination {
    flex-wrap: wrap;
  }
}
</style>
