<template>
  <div class="user-diary-page">
    <!-- 背景装饰 -->
    <div class="gradient-blobs">
      <div class="blob blob-1"></div>
      <div class="blob blob-2"></div>
      <div class="blob blob-3"></div>
    </div>

    <Navbar />

    <main class="page-content">
      <!-- 页面标题区 -->
      <div class="page-header">
        <div class="header-content">
          <h1 class="page-title">
            <span class="title-icon">📝</span>
            我的日记
          </h1>
          <p class="page-subtitle">记录每一次心动的瞬间</p>
        </div>
        <button class="create-btn" @click="openCreateModal">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 5v14M5 12h14" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          写新日记
        </button>
      </div>

      <!-- 统计卡片 -->
      <div class="stats-cards">
        <div class="stat-card">
          <div class="stat-icon">📚</div>
          <div class="stat-info">
            <span class="stat-value">{{ diaryStore.diaryCount }}</span>
            <span class="stat-label">篇日记</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">📅</div>
          <div class="stat-info">
            <span class="stat-value">{{ getTotalDays() }}</span>
            <span class="stat-label">记录天数</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">👁️</div>
          <div class="stat-info">
            <span class="stat-value">{{ getTotalViews() }}</span>
            <span class="stat-label">总浏览</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">⭐</div>
          <div class="stat-info">
            <span class="stat-value">{{ getAvgRating() }}</span>
            <span class="stat-label">平均评分</span>
          </div>
        </div>
      </div>

      <!-- 筛选栏 -->
      <div class="filter-bar">
        <div class="search-box">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"/>
            <path d="m21 21-4.35-4.35"/>
          </svg>
          <input 
            type="text" 
            placeholder="搜索日记标题或内容..." 
            v-model="searchQuery"
          />
        </div>
        <div class="filter-group">
          <select v-model="filterType" class="filter-select">
            <option value="all">全部类型</option>
            <option value="travel">行程</option>
            <option value="food">美食</option>
            <option value="photo">摄影</option>
            <option value="notes">随笔</option>
          </select>
          <select v-model="sortBy" class="filter-select">
            <option value="newest">最新发布</option>
            <option value="oldest">最早发布</option>
            <option value="rating">评分最高</option>
            <option value="views">浏览最多</option>
          </select>
        </div>
      </div>

      <!-- 日记列表 -->
      <div class="diary-list-section">
        <div v-if="filteredDiaries.length > 0" class="diary-grid">
          <div 
            v-for="diary in filteredDiaries" 
            :key="diary.id"
            class="diary-card"
            :class="{ 'has-timeline': diary.itinerary && diary.itinerary.length > 0 }"
          >
            <!-- 时间轴标记 -->
            <div v-if="diary.itinerary && diary.itinerary.length > 0" class="timeline-badge">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <polyline points="12 6 12 12 16 14"/>
              </svg>
              {{ diary.itinerary.length }}天行程
            </div>

            <!-- 日记内容区 -->
            <div class="diary-content" @click="viewDiary(diary)">
              <!-- 封面图 -->
              <div class="diary-cover" v-if="diary.images && diary.images.length > 0">
                <img :src="diary.images[0]" :alt="diary.title" />
                <div class="cover-overlay"></div>
              </div>
              <div class="diary-cover placeholder" v-else>
                <span class="type-emoji">{{ getTypeEmoji(diary.diary_type) }}</span>
              </div>

              <!-- 信息区 -->
              <div class="diary-info">
                <div class="diary-header">
                  <span class="diary-type" :class="diary.diary_type">
                    {{ getTypeLabel(diary.diary_type) }}
                  </span>
                  <span class="diary-date">{{ formatDate(diary.created_at) }}</span>
                </div>
                <h3 class="diary-title">{{ diary.title }}</h3>
                <p class="diary-excerpt">{{ diary.content?.slice(0, 100) }}...</p>
                
                <!-- 统计信息 -->
                <div class="diary-stats">
                  <span class="stat-item">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
                    </svg>
                    {{ diary.likes || 0 }}
                  </span>
                  <span class="stat-item">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/>
                    </svg>
                    {{ diary.avg_rating?.toFixed(1) || '0.0' }}
                  </span>
                  <span class="stat-item">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                      <circle cx="12" cy="12" r="3"/>
                    </svg>
                    {{ diary.view_count || 0 }}
                  </span>
                </div>
              </div>
            </div>

            <!-- 操作按钮 -->
            <div class="diary-actions">
              <button class="action-btn edit" @click.stop="editDiary(diary)" title="编辑">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                  <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                </svg>
              </button>
              <button class="action-btn delete" @click.stop="confirmDelete(diary)" title="删除">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="3 6 5 6 21 6"/>
                  <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                </svg>
              </button>
            </div>
          </div>
        </div>

        <!-- 空状态 -->
        <div v-else class="empty-state">
          <div class="empty-illustration">✈️</div>
          <h3>还没有日记</h3>
          <p class="empty-tip">开始记录你的精彩旅程吧</p>
          <button class="primary-btn" @click="openCreateModal">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 5v14M5 12h14" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            写第一篇日记
          </button>
        </div>
      </div>
    </main>

    <!-- 创建/编辑日记弹窗 - 使用 SmartDiaryEditor 组件 -->
    <div v-if="showCreateModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content editor-modal">
        <SmartDiaryEditor
          :initial-title="newDiary.title"
          :initial-content="newDiary.content"
          :initial-type="newDiary.diary_type"
          @save="handleSaveDraft"
          @publish="handlePublish"
          @cancel="closeModal"
        />
      </div>
    </div>

    <!-- 悬浮添加按钮 -->
    <button class="fab-button" @click="openCreateModal" title="写日记">
      <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
        <path d="M12 5v14M5 12h14" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </button>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import Navbar from '../components/Navbar.vue'
import SmartDiaryEditor from '../components/SmartDiaryEditor.vue'
import { useDiaryStore } from '../stores/diary.js'

const router = useRouter()
const diaryStore = useDiaryStore()

// 状态
const searchQuery = ref('')
const filterType = ref('all')
const sortBy = ref('newest')
const showCreateModal = ref(false)
const isEditing = ref(false)
const editingId = ref(null)

// 日记类型
const diaryTypes = [
  { value: 'travel', label: '行程', emoji: '🏃' },
  { value: 'food', label: '美食', emoji: '🍜' },
  { value: 'photo', label: '摄影', emoji: '📸' },
  { value: 'notes', label: '随笔', emoji: '💭' }
]

// 新日记数据
const newDiary = ref({
  title: '',
  content: '',
  diary_type: 'travel',
  images: [],
  budget: '',
  companion: '',
  itinerary: []
})

// 加载数据
onMounted(() => {
  const isLoggedIn = diaryStore.loadUserFromStorage()
  if (!isLoggedIn) {
    router.push('/login')
    return
  }
  diaryStore.fetchDiaries()
})

// 过滤和排序日记
const filteredDiaries = computed(() => {
  let result = [...diaryStore.diaryList]
  
  // 按类型过滤
  if (filterType.value !== 'all') {
    result = result.filter(d => d.diary_type === filterType.value)
  }
  
  // 按搜索词过滤
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(d => 
      d.title?.toLowerCase().includes(query) || 
      d.content?.toLowerCase().includes(query)
    )
  }
  
  // 排序
  switch (sortBy.value) {
    case 'newest':
      result.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
      break
    case 'oldest':
      result.sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
      break
    case 'rating':
      result.sort((a, b) => (b.avg_rating || 0) - (a.avg_rating || 0))
      break
    case 'views':
      result.sort((a, b) => (b.view_count || 0) - (a.view_count || 0))
      break
  }
  
  return result
})

// 获取类型标签
const getTypeLabel = (type) => {
  const typeMap = { travel: '行程', food: '美食', photo: '摄影', notes: '随笔' }
  return typeMap[type] || '其他'
}

// 获取类型表情
const getTypeEmoji = (type) => {
  const typeMap = { travel: '🏃', food: '🍜', photo: '📸', notes: '💭' }
  return typeMap[type] || '📝'
}

// 格式化日期
const formatDate = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

// 统计函数
const getTotalDays = () => {
  if (diaryStore.diaryList.length === 0) return 0
  const dates = diaryStore.diaryList.map(d => new Date(d.created_at).toDateString())
  return new Set(dates).size
}

const getTotalViews = () => {
  return diaryStore.diaryList.reduce((sum, d) => sum + (d.view_count || 0), 0)
}

const getAvgRating = () => {
  if (diaryStore.diaryList.length === 0) return '0.0'
  const avg = diaryStore.diaryList.reduce((sum, d) => sum + (d.avg_rating || 0), 0) / diaryStore.diaryList.length
  return avg.toFixed(1)
}

// 查看日记详情
const viewDiary = (diary) => {
  router.push(`/diary/${diary.id}`)
}

// 打开创建弹窗
const openCreateModal = () => {
  isEditing.value = false
  editingId.value = null
  newDiary.value = {
    title: '',
    content: '',
    diary_type: 'travel',
    images: [],
    budget: '',
    companion: '',
    itinerary: []
  }
  showCreateModal.value = true
}

// 编辑日记
const editDiary = (diary) => {
  isEditing.value = true
  editingId.value = diary.id
  newDiary.value = {
    title: diary.title || '',
    content: diary.content || '',
    diary_type: diary.diary_type || 'travel',
    images: diary.images || [],
    budget: diary.budget || '',
    companion: diary.companion || '',
    itinerary: diary.itinerary || []
  }
  showCreateModal.value = true
}

// 关闭弹窗
const closeModal = () => {
  showCreateModal.value = false
  isEditing.value = false
  editingId.value = null
}

// 处理保存草稿
const handleSaveDraft = (diary) => {
  // 保存到本地草稿
  localStorage.setItem('diary_draft', JSON.stringify(diary))
  ElMessage.success('草稿已保存')
  closeModal()
}

// 处理发布日记
const handlePublish = async (diary) => {
  try {
    const diaryData = {
      title: diary.title,
      content: diary.content,
      diary_type: diary.diary_type,
      images: diary.images || [],
      budget: diary.budget,
      companion: diary.companion,
      itinerary: diary.itinerary || []
    }
    
    if (isEditing.value && editingId.value) {
      await diaryStore.updateDiary(editingId.value, diaryData)
      ElMessage.success('日记更新成功！')
    } else {
      await diaryStore.createDiary(diaryData)
      ElMessage.success('日记发布成功！')
    }
    
    // 清除草稿
    localStorage.removeItem('diary_draft')
    closeModal()
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败：' + (error.message || '未知错误'))
  }
}

// 确认删除
const confirmDelete = (diary) => {
  ElMessageBox.confirm(
    `确定要删除日记 "${diary.title}" 吗？此操作不可恢复。`,
    '删除确认',
    {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning',
      confirmButtonClass: 'el-button--danger'
    }
  ).then(() => {
    handleDelete(diary.id)
  }).catch(() => {})
}

// 删除日记
const handleDelete = async (diaryId) => {
  try {
    await diaryStore.deleteDiary(diaryId)
    ElMessage.success('日记已删除')
  } catch (error) {
    console.error('删除失败:', error)
    ElMessage.error('删除失败：' + (error.message || '未知错误'))
  }
}
</script>

<style scoped>
.user-diary-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #0a0a1a 0%, #12121f 50%, #0a0a1a 100%);
  position: relative;
  overflow-x: hidden;
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
}

.blob-1 {
  width: 500px;
  height: 500px;
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  top: -150px;
  left: -150px;
}

.blob-2 {
  width: 400px;
  height: 400px;
  background: linear-gradient(135deg, #ff6b6b, #ffd93d);
  top: 30%;
  right: -100px;
}

.blob-3 {
  width: 450px;
  height: 450px;
  background: linear-gradient(135deg, #4ecdc4, #44a08d);
  bottom: 10%;
  left: 5%;
}

/* 页面内容 */
.page-content {
  position: relative;
  z-index: 1;
  padding: 100px 32px 120px;
  max-width: 1200px;
  margin: 0 auto;
}

/* 页面标题 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.header-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.page-title {
  font-size: 32px;
  font-weight: 700;
  color: #fff;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 12px;
}

.title-icon {
  font-size: 36px;
}

.page-subtitle {
  font-size: 15px;
  color: rgba(255, 255, 255, 0.5);
  margin: 0;
}

.create-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 24px;
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  border: none;
  border-radius: 12px;
  color: white;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 20px rgba(0, 212, 255, 0.3);
}

.create-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(0, 212, 255, 0.4);
}

/* 统计卡片 */
.stats-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 32px;
}

.stat-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  transition: all 0.3s ease;
}

.stat-card:hover {
  background: rgba(255, 255, 255, 0.05);
  transform: translateY(-2px);
}

.stat-icon {
  font-size: 32px;
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
}

.stat-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #fff;
  line-height: 1;
}

.stat-label {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
}

@media (max-width: 768px) {
  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* 筛选栏 */
.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.search-box {
  flex: 1;
  min-width: 280px;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
}

.search-box svg {
  color: rgba(255, 255, 255, 0.4);
  flex-shrink: 0;
}

.search-box input {
  flex: 1;
  background: transparent;
  border: none;
  color: #fff;
  font-size: 14px;
  outline: none;
}

.search-box input::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.filter-group {
  display: flex;
  gap: 12px;
}

.filter-select {
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  color: #fff;
  font-size: 14px;
  cursor: pointer;
  outline: none;
}

.filter-select option {
  background: #1a1a2e;
  color: #fff;
}

/* 日记列表 */
.diary-list-section {
  min-height: 400px;
}

.diary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
}

.diary-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  overflow: hidden;
  transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
  position: relative;
}

.diary-card:hover {
  transform: translateY(-8px);
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.15);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
}

.diary-card.has-timeline {
  border-color: rgba(0, 212, 255, 0.2);
}

.timeline-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: rgba(0, 212, 255, 0.2);
  border: 1px solid rgba(0, 212, 255, 0.3);
  border-radius: 20px;
  font-size: 12px;
  color: #00d4ff;
  z-index: 2;
}

.timeline-badge svg {
  stroke: #00d4ff;
}

.diary-content {
  cursor: pointer;
}

.diary-cover {
  position: relative;
  height: 180px;
  overflow: hidden;
}

.diary-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.6s ease;
}

.diary-card:hover .diary-cover img {
  transform: scale(1.05);
}

.cover-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, rgba(10, 10, 26, 0.9) 0%, transparent 50%);
}

.diary-cover.placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.1), rgba(123, 44, 191, 0.1));
}

.type-emoji {
  font-size: 48px;
  opacity: 0.6;
}

.diary-info {
  padding: 20px;
}

.diary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.diary-type {
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
}

.diary-type.travel {
  background: rgba(255, 107, 107, 0.2);
  color: #ff6b6b;
}

.diary-type.food {
  background: rgba(255, 217, 61, 0.2);
  color: #ffd93d;
}

.diary-type.photo {
  background: rgba(78, 205, 196, 0.2);
  color: #4ecdc4;
}

.diary-type.notes {
  background: rgba(167, 139, 250, 0.2);
  color: #a78bfa;
}

.diary-date {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
}

.diary-title {
  font-size: 17px;
  font-weight: 600;
  color: #fff;
  margin: 0 0 10px 0;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.diary-excerpt {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
  line-height: 1.6;
  margin: 0 0 16px 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.diary-stats {
  display: flex;
  gap: 16px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
}

.stat-item svg {
  opacity: 0.7;
}

.diary-actions {
  display: flex;
  gap: 8px;
  padding: 0 20px 20px;
}

.action-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 10px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.action-btn:hover {
  background: rgba(255, 255, 255, 0.1);
}

.action-btn.edit:hover {
  border-color: rgba(0, 212, 255, 0.3);
  color: #00d4ff;
}

.action-btn.delete:hover {
  border-color: rgba(255, 71, 87, 0.3);
  color: #ff4757;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;
}

.empty-illustration {
  font-size: 80px;
  margin-bottom: 24px;
  opacity: 0.6;
}

.empty-state h3 {
  font-size: 24px;
  font-weight: 600;
  color: #fff;
  margin: 0 0 8px 0;
}

.empty-tip {
  font-size: 15px;
  color: rgba(255, 255, 255, 0.4);
  margin: 0 0 24px 0;
}

.primary-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 28px;
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  border: none;
  border-radius: 12px;
  color: white;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.primary-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(0, 212, 255, 0.4);
}

/* 弹窗 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
  backdrop-filter: blur(10px);
}

.modal-content {
  background: linear-gradient(135deg, #1a1a2e 0%, #16162a 100%);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 24px;
  width: 100%;
  max-width: 700px;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: 0 25px 80px rgba(0, 0, 0, 0.6);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 28px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.modal-header h3 {
  font-size: 20px;
  font-weight: 600;
  color: #fff;
  margin: 0;
}

.close-btn {
  width: 36px;
  height: 36px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  color: rgba(255, 255, 255, 0.6);
  font-size: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  background: rgba(255, 71, 87, 0.2);
  border-color: rgba(255, 71, 87, 0.3);
  color: #ff4757;
}

.modal-body {
  padding: 24px 28px;
  overflow-y: auto;
  flex: 1;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px 28px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

/* 表单样式 */
.form-group {
  margin-bottom: 24px;
}

.form-group label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 10px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.type-selector {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.type-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.type-btn:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.15);
}

.type-btn.active {
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.2), rgba(123, 44, 191, 0.2));
  border-color: rgba(0, 212, 255, 0.4);
  color: #fff;
}

.type-emoji {
  font-size: 18px;
}

.form-input,
.form-textarea {
  width: 100%;
  padding: 14px 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  color: #fff;
  font-size: 14px;
  transition: all 0.3s ease;
  outline: none;
}

.form-input:focus,
.form-textarea:focus {
  border-color: rgba(0, 212, 255, 0.4);
  background: rgba(255, 255, 255, 0.08);
}

.form-input::placeholder,
.form-textarea::placeholder {
  color: rgba(255, 255, 255, 0.3);
}

.form-textarea {
  resize: vertical;
  min-height: 120px;
  line-height: 1.6;
}

.form-hint {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
  margin: 8px 0 0 0;
}

/* 图片上传 */
.image-upload {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.uploaded-image {
  position: relative;
  width: 100px;
  height: 100px;
  border-radius: 12px;
  overflow: hidden;
}

.uploaded-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.remove-image {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 24px;
  height: 24px;
  background: rgba(255, 71, 87, 0.9);
  border: none;
  border-radius: 6px;
  color: white;
  font-size: 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.remove-image:hover {
  background: #ff4757;
  transform: scale(1.1);
}

.upload-btn {
  width: 100px;
  height: 100px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.03);
  border: 2px dashed rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  color: rgba(255, 255, 255, 0.5);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.upload-btn:hover {
  background: rgba(255, 255, 255, 0.06);
  border-color: rgba(255, 255, 255, 0.25);
  color: rgba(255, 255, 255, 0.7);
}

.upload-btn svg {
  stroke: currentColor;
}

/* 时间轴编辑器 */
.timeline-group {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 16px;
  padding: 20px;
}

.timeline-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.timeline-header label {
  margin-bottom: 0;
}

.editor-modal {
  max-width: 900px;
  background: transparent;
  border: none;
  box-shadow: none;
}

/* 悬浮按钮 */
.fab-button {
  position: fixed;
  bottom: 100px;
  right: 24px;
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  border: none;
  border-radius: 50%;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 6px 20px rgba(0, 212, 255, 0.4), 0 0 0 1px rgba(255, 255, 255, 0.1) inset;
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  z-index: 100;
}

.fab-button:hover {
  transform: scale(1.1) rotate(90deg);
  box-shadow: 0 8px 30px rgba(0, 212, 255, 0.5), 0 0 0 1px rgba(255, 255, 255, 0.2) inset;
}

.fab-button:active {
  transform: scale(0.95);
}

/* 响应式 */
@media (max-width: 768px) {
  .page-content {
    padding: 80px 16px 100px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .page-title {
    font-size: 24px;
  }

  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }

  .stat-card {
    padding: 16px;
  }

  .stat-icon {
    width: 44px;
    height: 44px;
    font-size: 24px;
  }

  .stat-value {
    font-size: 22px;
  }

  .filter-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .search-box {
    min-width: auto;
  }

  .filter-group {
    justify-content: stretch;
  }

  .filter-select {
    flex: 1;
  }

  .diary-grid {
    grid-template-columns: 1fr;
  }

  .editor-modal {
    max-width: 100%;
    margin: 10px;
  }
}
</style>