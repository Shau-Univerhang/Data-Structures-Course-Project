﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿<template>
  <div class="diary-page">
    <Navbar />
    
    <!-- SVG 渐变定义 -->
    <svg width="0" height="0" style="position: absolute;">
      <defs>
        <linearGradient id="gradientPurple" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stop-color="#00d4ff" />
          <stop offset="100%" stop-color="#7b2cbf" />
        </linearGradient>
        <linearGradient id="gradientOrange" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stop-color="#ff6b6b" />
          <stop offset="100%" stop-color="#ffd93d" />
        </linearGradient>
      </defs>
    </svg>

    <!-- 背景装饰色块 -->
    <div class="gradient-blobs">
      <div class="blob blob-1"></div>
      <div class="blob blob-2"></div>
      <div class="blob blob-3"></div>
    </div>
    
    <!-- 氛围灯效果 -->
    <div class="ambient-light-left"></div>
    <div class="ambient-light-right"></div>

    <!-- 主栏动态光斑背景 -->
    <div class="main-ambient-bg">
      <div class="ambient-orb orb-purple"></div>
      <div class="ambient-orb orb-blue"></div>
    </div>

    <main class="page-content two-column">
      <!-- 左侧主栏 (65%) -->
      <div class="main-column">
        <!-- AI 输入框 - 主角化，置于 Hero 上方 -->
        <div class="ai-input-wrapper hero-input">
          <div class="ai-input-bar glow-pulse" @click="openAIEditor">
            <div class="ai-input-content">
              <div class="ai-icon-wrapper">
                <span class="ai-icon">✨</span>
                <span class="ai-pulse-ring"></span>
              </div>
              <span class="ai-placeholder">输入一句话灵感，AI 帮你生成日记...</span>
            </div>
            <button class="camera-btn" @click.stop="openCameraUpload">
              <span>📷</span>
            </button>
          </div>
        </div>

        <!-- 发现精彩日记 - Hero Card -->
        <div class="hero-section">
          <div class="hero-card" @click="viewDiary(publicDiaries[currentSlide])">
            <div class="hero-image-wrapper">
              <img 
                v-if="publicDiaries[currentSlide]?.cover" 
                :src="publicDiaries[currentSlide].cover" 
                class="hero-image"
                alt="日记封面"
              />
              <div v-else class="hero-image-placeholder">
                <span class="hero-placeholder-icon">🌟</span>
              </div>
              <div class="hero-glow"></div>
            </div>
            <div class="hero-content">
              <div class="hero-badge">精选日记</div>
              <h3 class="hero-title">{{ publicDiaries[currentSlide]?.title || '发现精彩旅程' }}</h3>
              <p class="hero-author">by {{ publicDiaries[currentSlide]?.author || '旅行者' }}</p>
              <div class="hero-stats">
                <span class="hero-stat">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/>
                  </svg>
                  {{ publicDiaries[currentSlide]?.rating || 0 }}
                </span>
              </div>
            </div>
          </div>
          <div class="hero-dots">
            <button 
              v-for="(_, index) in publicDiaries" 
              :key="index"
              class="hero-dot"
              :class="{ active: currentSlide === index }"
              @click.stop="currentSlide = index"
            ></button>
          </div>
        </div>

        <!-- 我的日记列表 -->
        <div class="my-diary-section">
          <div class="section-header">
            <h2 class="section-title">📒 我的日记</h2>
            <span class="diary-count">{{ filteredDiaries.length }} 篇</span>
          </div>
          
          <!-- 搜索 -->
          <div class="search-bar">
            <input 
              type="text" 
              class="tech-input" 
              placeholder="搜索我的日记..." 
              v-model="searchQuery"
            />
          </div>

          <!-- 日记列表 -->
          <div class="diary-list" v-if="filteredDiaries.length > 0">
            <div 
              v-for="diary in filteredDiaries" 
              :key="diary.id"
              class="diary-card tech-card"
            >
              <div class="diary-main" @click="viewDiary(diary)">
                <div class="diary-images" v-if="diary.images?.length">
                  <img :src="diary.images[0]" :alt="diary.title" />
                </div>
                <div class="diary-images placeholder" v-else>
                  <span>{{ getTypeEmoji(diary.diary_type) }}</span>
                </div>
                <div class="diary-content">
                  <h3 class="diary-title">{{ diary.title }}</h3>
                  <p class="diary-excerpt">{{ diary.content?.slice(0, 60) }}...</p>
                  <div class="diary-meta">
                    <span class="meta-item">
                      <span>👁️</span>
                      {{ diary.view_count }}
                    </span>
                    <span class="meta-item">
                      <span>⭐</span>
                      {{ diary.avg_rating?.toFixed(1) || '0.0' }}
                    </span>
                    <span class="meta-item">
                      <span>📅</span>
                      {{ formatDate(diary.created_at) }}
                    </span>
                  </div>
                </div>
              </div>
              <button class="delete-btn" @click.stop="confirmDelete(diary)" title="删除日记">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/>
                </svg>
              </button>
            </div>
          </div>

          <!-- 空状态 -->
          <div v-else class="empty-state">
            <div class="empty-illustration">✈️</div>
            <h3>开启你的旅程</h3>
            <p class="empty-tip">记录每一次心动的瞬间</p>
          </div>
        </div>
      </div>

      <!-- 右侧边栏 (35%) - 毛玻璃卡片风格 -->
      <aside class="sidebar-column">
        <!-- 日记分类 - 毛玻璃卡片 -->
        <div class="sidebar-section">
          <h3 class="sidebar-section-title">📁 日记分类</h3>
          <div class="category-cards">
            <button class="category-glass-card travel" @click="createWithTemplate('travel')">
              <div class="card-icon">🏃</div>
              <div class="card-info">
                <span class="card-name">行程</span>
                <span class="card-count">{{ diaryStore.diaryCountByType('travel') }} 篇</span>
              </div>
              <div class="card-glow"></div>
            </button>
            <button class="category-glass-card food" @click="createWithTemplate('food')">
              <div class="card-icon">🍜</div>
              <div class="card-info">
                <span class="card-name">美食</span>
                <span class="card-count">{{ diaryStore.diaryCountByType('food') }} 篇</span>
              </div>
              <div class="card-glow"></div>
            </button>
            <button class="category-glass-card photo" @click="createWithTemplate('photo')">
              <div class="card-icon">📸</div>
              <div class="card-info">
                <span class="card-name">摄影</span>
                <span class="card-count">{{ diaryStore.diaryCountByType('photo') }} 篇</span>
              </div>
              <div class="card-glow"></div>
            </button>
            <button class="category-glass-card notes" @click="createWithTemplate('notes')">
              <div class="card-icon">💭</div>
              <div class="card-info">
                <span class="card-name">随笔</span>
                <span class="card-count">{{ diaryStore.diaryCountByType('notes') }} 篇</span>
              </div>
              <div class="card-glow"></div>
            </button>
          </div>
        </div>

        <!-- 个人成就/数据统计 - 可视化 -->
        <div class="sidebar-section">
          <h3 class="sidebar-section-title">📊 数据统计</h3>
          <div class="stats-visual">
            <!-- 大数字展示 -->
            <div class="stat-big-number">
              <span class="big-num">{{ diaryStore.diaryCount }}</span>
              <span class="big-label">篇日记</span>
            </div>
            
            <!-- 进度条 -->
            <div class="stat-progress-list">
              <div class="progress-item">
                <div class="progress-header">
                  <span class="progress-name">行程</span>
                  <span class="progress-value">{{ diaryStore.diaryCountByType('travel') }}</span>
                </div>
                <div class="progress-bar-bg">
                  <div class="progress-bar-fill travel" :style="{ width: getProgressWidth('travel') }"></div>
                </div>
              </div>
              <div class="progress-item">
                <div class="progress-header">
                  <span class="progress-name">美食</span>
                  <span class="progress-value">{{ diaryStore.diaryCountByType('food') }}</span>
                </div>
                <div class="progress-bar-bg">
                  <div class="progress-bar-fill food" :style="{ width: getProgressWidth('food') }"></div>
                </div>
              </div>
              <div class="progress-item">
                <div class="progress-header">
                  <span class="progress-name">摄影</span>
                  <span class="progress-value">{{ diaryStore.diaryCountByType('photo') }}</span>
                </div>
                <div class="progress-bar-bg">
                  <div class="progress-bar-fill photo" :style="{ width: getProgressWidth('photo') }"></div>
                </div>
              </div>
            </div>
            
            <!-- 环形图统计 -->
            <div class="stats-circles">
              <div class="stat-circle-item">
                <div class="circle-chart">
                  <svg viewBox="0 0 36 36">
                    <path class="circle-bg" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                    <path class="circle-fill" :stroke-dasharray="getTotalDays() > 0 ? Math.min(getTotalDays() / 30 * 100, 100) + ', 100' : '0, 100'" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                  </svg>
                  <div class="circle-text">
                    <span class="circle-num">{{ getTotalDays() }}</span>
                    <span class="circle-label">天</span>
                  </div>
                </div>
                <span class="circle-desc">记录天数</span>
              </div>
              <div class="stat-circle-item">
                <div class="circle-chart">
                  <svg viewBox="0 0 36 36">
                    <path class="circle-bg" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                    <path class="circle-fill orange" :stroke-dasharray="getTotalViews() > 0 ? Math.min(getTotalViews() / 1000 * 100, 100) + ', 100' : '0, 100'" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                  </svg>
                  <div class="circle-text">
                    <span class="circle-num">{{ getTotalViews() }}</span>
                    <span class="circle-label">次</span>
                  </div>
                </div>
                <span class="circle-desc">总浏览</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 我的日记入口 -->
        <div class="sidebar-section">
          <h3 class="sidebar-section-title">📝 我的日记</h3>
          <button class="user-diary-entry" @click="goToUserDiary">
            <div class="entry-icon">📚</div>
            <div class="entry-info">
              <span class="entry-title">管理我的日记</span>
              <span class="entry-desc">查看、编辑和管理你的所有日记</span>
            </div>
            <svg class="entry-arrow" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M9 18l6-6-6-6" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
        </div>

        <!-- 发现更多 - 日记库入口 -->
        <div class="sidebar-section">
          <h3 class="sidebar-section-title">🌍 发现更多</h3>
          <button class="user-diary-entry library-entry" @click="goToDiaryLibrary">
            <div class="entry-icon">🌐</div>
            <div class="entry-info">
              <span class="entry-title">探索日记库</span>
              <span class="entry-desc">发现更多用户的出游日记</span>
            </div>
            <svg class="entry-arrow" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M9 18l6-6-6-6" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
        </div>
      </aside>
      
      <!-- 悬浮添加按钮 -->
      <button class="fab-button" @click="openAIEditor" title="写日记">
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <path d="M12 5v14M5 12h14" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
    </main>

    <!-- 创建日记弹窗 - 使用 SmartDiaryEditor 组件 -->
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
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import Navbar from '../components/Navbar.vue'
import SmartDiaryEditor from '../components/SmartDiaryEditor.vue'
import { useDiaryStore } from '../stores/diary.js'

const router = useRouter()
const route = useRoute()
const diaryStore = useDiaryStore()

const searchQuery = ref('')
const showCreateModal = ref(false)
const publicDiaries = ref([])
const currentSlide = ref(0)

// 日记类型
const diaryTypes = [
  { value: 'travel', label: '行程', emoji: '🏃' },
  { value: 'food', label: '美食', emoji: '🍜' },
  { value: 'photo', label: '摄影', emoji: '📸' },
  { value: 'notes', label: '随笔', emoji: '💭' }
]

// 模板内容
const templates = {
  travel: `【行程概览】
📅 出发日期：
👥 同行伙伴：
💰 预算花费：

【第一天】
🏨 住宿：
📍 上午：
📍 中午：
📍 下午：
📍 晚上：

【第二天】


【第三天】


【推荐指数】⭐⭐⭐⭐⭐

【实用贴士】
• 
• 

【总体感受】

`,
  food: `【美食清单】
🥘 必吃菜品：
1. 
2. 
3. 

【餐厅信息】
📍 店名：
📍 地址：
💰 人均：元

【口味评价】
• 招牌菜：
• 特色菜：
• 人气菜：

【推荐指数】⭐⭐⭐⭐⭐

【探店心得】

`,
  photo: `【拍摄信息】
📍 拍摄地点：
📅 拍摄时间：
🌤️ 天气状况：

【器材参数】
📷 相机：
🔭 镜头：
⚙️ 参数：

【拍摄参数】
• 光圈：
• 快门：
• ISO：

【后期处理】
• 调色思路：
• 滤镜选择：

【推荐指数】⭐⭐⭐⭐⭐

【拍摄建议】

`,
  notes: `【出行信息】
📅 日期：
📍 地点：

【随笔内容】


【感悟分享】


【美好瞬间】

`
}

// 从API获取公开日记作为精美日记
const fetchPublicDiaries = async () => {
  try {
    const response = await fetch('/api/diaries/public?page=1&page_size=5')
    if (response.ok) {
      const data = await response.json()
      console.log('获取到的公开日记:', data)
      // 转换数据格式以适配轮播组件
      publicDiaries.value = data.map(diary => ({
        id: diary.id,
        title: diary.title,
        author: diary.author || '匿名用户',
        cover: diary.cover || '',
        likes: diary.likes || 0,
        rating: diary.rating || 0
      }))
      console.log('转换后的公开日记:', publicDiaries.value)
    }
  } catch (error) {
    console.error('获取公开日记失败:', error)
  }
}

let slideInterval = null

onMounted(() => {
  // 从 store 加载用户
  const isLoggedIn = diaryStore.loadUserFromStorage()
  if (!isLoggedIn) {
    router.push('/login')
    return
  }
  
  // 获取用户日记列表
  diaryStore.fetchDiaries()
  
  // 从API加载公开日记（精美日记）
  fetchPublicDiaries()
  
  // 自动轮播
  slideInterval = setInterval(() => {
    if (publicDiaries.value.length > 0) {
      currentSlide.value = (currentSlide.value + 1) % publicDiaries.value.length
    }
  }, 4000)
  
  // 检查是否有从行程导入的数据
  const draftData = localStorage.getItem('draftDiaryFromTrip')
  if (draftData) {
    try {
      const parsed = JSON.parse(draftData)
      // 自动打开编辑器并填充数据
      newDiary.value = {
        title: parsed.title || '',
        content: parsed.content || '',
        diary_type: parsed.diary_type || 'travel'
      }
      showCreateModal.value = true
      // 清除，避免重复加载
      localStorage.removeItem('draftDiaryFromTrip')
      ElMessage.success(`已导入行程：${parsed.sourceTripTitle || parsed.title}`)
    } catch (e) {
      console.error('解析行程数据失败:', e)
    }
  }
})

onUnmounted(() => {
  if (slideInterval) clearInterval(slideInterval)
})

// 监听路由变化，返回日记页面时刷新数据
watch(() => route.path, (newPath) => {
  if (newPath === '/diary') {
    diaryStore.fetchDiaries()
  }
})

const newDiary = ref({
  title: '',
  content: '',
  diary_type: 'travel'
})

// 使用 store 的日记列表
const filteredDiaries = computed(() => {
  if (!searchQuery.value) return diaryStore.diaryList
  return diaryStore.diaryList.filter(d => 
    d.title?.includes(searchQuery.value) || 
    d.content?.includes(searchQuery.value)
  )
})

const getTypeEmoji = (type) => {
  const found = diaryTypes.find(t => t.value === type)
  return found?.emoji || '📝'
}

// 获取进度条宽度
const getProgressWidth = (type) => {
  const count = diaryStore.diaryCountByType(type)
  const total = Math.max(diaryStore.diaryCount, 1)
  return count > 0 ? (count / total * 100) + '%' : '0%'
}

// 获取总记录天数
const getTotalDays = () => {
  if (diaryStore.diaryList.length === 0) return 0
  const dates = diaryStore.diaryList.map(d => new Date(d.created_at).toDateString())
  return new Set(dates).size
}

// 获取总浏览量
const getTotalViews = () => {
  return diaryStore.diaryList.reduce((sum, d) => sum + (d.view_count || 0), 0)
}

const formatDate = (date) => {
  if (!date) return ''
  return date.split('T')[0]
}

const viewDiary = (diary) => {
  router.push(`/diary/${diary.id}`)
}

const createWithTemplate = (type) => {
  newDiary.value = {
    title: '',
    content: templates[type],
    diary_type: type
  }
  showCreateModal.value = true
}

const closeModal = () => {
  showCreateModal.value = false
  newDiary.value = { title: '', content: '', diary_type: 'travel' }
}

// 打开 AI 编辑器
const openAIEditor = () => {
  newDiary.value = { title: '', content: '', diary_type: 'travel' }
  showCreateModal.value = true
}

// 处理编辑器保存草稿事件
const handleSaveDraft = (draft) => {
  console.log('草稿已保存:', draft)
}

// 处理编辑器发布事件
const handlePublish = async (diary) => {
  try {
    const newDiaryData = await diaryStore.createDiary({
      title: diary.title,
      content: diary.content,
      diary_type: newDiary.value.diary_type || 'notes',
      images: diary.images || [],
      budget: diary.budget,
      companion: diary.companion,
      itinerary: diary.timeline || [],
      is_public: true
    })
    ElMessage.success('日记发布成功！')
    closeModal()
    // 发布成功后刷新日记列表
    await diaryStore.fetchDiaries()
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败：' + (error.message || '未知错误'))
  }
}

// 打开相机上传
const openCameraUpload = () => {
  newDiary.value = { title: '', content: '', diary_type: 'travel' }
  showCreateModal.value = true
}

// 确认删除日记
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
  }).catch(() => {
    // 取消删除，不做任何操作
  })
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

// 跳转到用户日记管理页面
const goToUserDiary = () => {
  router.push('/user-diary')
}

// 跳转到日记库页面
const goToDiaryLibrary = () => {
  router.push('/diary-library')
}
</script>

<style scoped>
.diary-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #0a0a1a 0%, #12121f 50%, #0a0a1a 100%);
  position: relative;
  overflow-x: hidden;
  padding-top: 80px;
}

.page-content {
  padding: 80px 20px 100px;
}

/* 背景氛围灯 */
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

.ambient-light-left {
  position: fixed;
  width: 600px;
  height: 600px;
  background: linear-gradient(135deg, rgba(123, 44, 191, 0.4), rgba(0, 212, 255, 0.2));
  border-radius: 50%;
  filter: blur(100px);
  opacity: 0.15;
  left: -300px;
  top: 20%;
  pointer-events: none;
  z-index: 0;
  animation: ambientFloat 25s ease-in-out infinite;
}

.ambient-light-right {
  position: fixed;
  width: 500px;
  height: 500px;
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.3), rgba(123, 44, 191, 0.4));
  border-radius: 50%;
  filter: blur(100px);
  opacity: 0.12;
  right: -250px;
  bottom: 15%;
  pointer-events: none;
  z-index: 0;
  animation: ambientFloat 30s ease-in-out infinite reverse;
}

@keyframes ambientFloat {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  33% {
    transform: translate(30px, -20px) scale(1.05);
  }
  66% {
    transform: translate(-20px, 30px) scale(0.95);
  }
}

@keyframes float {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  25% {
    transform: translate(30px, -30px) scale(1.05);
  }
  50% {
    transform: translate(-20px, 20px) scale(0.95);
  }
  75% {
    transform: translate(20px, 10px) scale(1.02);
  }
}

/* 主栏动态光斑背景 */
.main-ambient-bg {
  position: fixed;
  top: 0;
  left: 0;
  width: 65%;
  height: 100%;
  pointer-events: none;
  z-index: -1;
  overflow: hidden;
}

.ambient-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.08;
  animation: orbFloat 15s ease-in-out infinite;
}

.orb-purple {
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, #7b2cbf 0%, transparent 70%);
  top: 10%;
  left: 20%;
  animation-delay: 0s;
}

.orb-blue {
  width: 350px;
  height: 350px;
  background: radial-gradient(circle, #1a3a5c 0%, transparent 70%);
  bottom: 20%;
  right: 10%;
  animation-delay: -7s;
}

@keyframes orbFloat {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  25% {
    transform: translate(20px, -30px) scale(1.05);
  }
  50% {
    transform: translate(-10px, 20px) scale(0.95);
  }
  75% {
    transform: translate(15px, 10px) scale(1.02);
  }
}

/* 双栏布局 */
.page-content.two-column {
  display: flex;
  gap: 40px;
  padding: 80px 32px 120px;
  max-width: 1280px;
  margin: 0 auto;
  position: relative;
  z-index: 1;
}

.main-column {
  flex: 0 0 65%;
  min-width: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.sidebar-column {
  flex: 0 0 35%;
  min-width: 320px;
  max-width: 400px;
  padding-top: 0;
}

.main-column > * {
  width: 100%;
  max-width: 800px;
}

@media (max-width: 1024px) {
  .page-content.two-column {
    flex-direction: column;
    padding: 80px 20px 120px;
    gap: 32px;
  }
  
  .main-column {
    flex: 1;
    width: 100%;
  }
  
  .sidebar-column {
    flex: 1;
    max-width: 100%;
    min-width: auto;
  }
  
  .main-column > * {
    max-width: 100%;
  }
  
  .main-ambient-bg {
    width: 100%;
  }
}

/* AI 输入条 */
.ai-input-wrapper {
  margin-bottom: 16px;
  width: 100%;
  max-width: 800px;
  padding: 0;
}

.ai-input-wrapper.hero-input {
  margin-bottom: 20px;
  margin-top: 8px;
  width: 100%;
  max-width: 800px;
}

.ai-input-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 20px 12px 24px;
  height: 56px;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
  border-radius: 50px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow:
    0 4px 20px rgba(0, 0, 0, 0.3),
    0 4px 30px rgba(0, 0, 0, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.15);
  position: relative;
}

.ai-input-bar::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 50px;
  padding: 2px;
  background: linear-gradient(135deg, #00d4ff, #7b2cbf, #00d4ff);
  background-size: 200% 200%;
  animation: gradientShift 3s ease infinite;
  -webkit-mask: 
    linear-gradient(#fff 0 0) content-box, 
    linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  opacity: 0.8;
  transition: opacity 0.3s ease;
}

@keyframes gradientShift {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}

.ai-input-bar:hover {
  background: rgba(255, 255, 255, 0.1);
  box-shadow: 
    0 8px 40px rgba(0, 212, 255, 0.25),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
}

.ai-input-bar:hover::before {
  opacity: 1;
}

.ai-input-bar.glow-pulse::after {
  content: '';
  position: absolute;
  top: -4px;
  left: -4px;
  right: -4px;
  bottom: -4px;
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.5), rgba(123, 44, 191, 0.5));
  border-radius: 50px;
  z-index: -1;
  animation: glowPulse 2s ease-in-out infinite;
  opacity: 0.5;
  filter: blur(12px);
}

@keyframes glowPulse {
  0%, 100% {
    opacity: 0.4;
    transform: scale(1);
  }
  50% {
    opacity: 0.7;
    transform: scale(1.02);
  }
}

.ai-input-content {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
}

.ai-icon-wrapper {
  position: relative;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.ai-icon {
  font-size: 16px;
  z-index: 1;
}

.ai-pulse-ring {
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  border: 2px solid rgba(0, 212, 255, 0.4);
  animation: pulseRing 2s ease-out infinite;
}

@keyframes pulseRing {
  0% {
    transform: scale(1);
    opacity: 0.8;
  }
  100% {
    transform: scale(1.5);
    opacity: 0;
  }
}

.ai-placeholder {
  color: rgba(255, 255, 255, 0.85);
  font-size: 15px;
  font-weight: 500;
  flex: 1;
  letter-spacing: 0.3px;
}

.camera-btn {
  width: 32px;
  height: 32px;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.camera-btn:hover {
  background: rgba(0, 212, 255, 0.2);
  transform: scale(1.1);
}

.camera-btn span {
  font-size: 16px;
}

/* Hero Card */
.hero-section {
  margin-bottom: 16px;
  width: 100%;
  max-width: 800px;
}

.hero-card {
  width: 100%;
  margin: 0 auto;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 24px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
  box-shadow: 
    0 4px 20px rgba(0, 0, 0, 0.3),
    0 20px 60px rgba(0, 0, 0, 0.4),
    0 0 0 1px rgba(255, 255, 255, 0.05);
}

.hero-card:hover {
  transform: translateY(-8px);
  box-shadow: 
    0 30px 80px rgba(0, 0, 0, 0.5),
    0 0 40px rgba(0, 212, 255, 0.15),
    0 0 0 1px rgba(0, 212, 255, 0.2);
}

.hero-image-wrapper {
  position: relative;
  width: 100%;
  height: 320px;
  overflow: hidden;
}

.hero-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.6s ease;
}

.hero-card:hover .hero-image {
  transform: scale(1.05);
}

.hero-image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.1), rgba(123, 44, 191, 0.1));
}

.hero-placeholder-icon {
  font-size: 80px;
  opacity: 0.5;
}

.hero-glow {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 150px;
  background: linear-gradient(transparent, rgba(10, 10, 26, 0.9));
  pointer-events: none;
}

.hero-content {
  padding: 24px;
  position: relative;
}

.hero-badge {
  display: inline-block;
  padding: 6px 14px;
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
  color: #fff;
  letter-spacing: 1px;
  text-transform: uppercase;
  margin-bottom: 12px;
}

.hero-title {
  font-size: 22px;
  font-weight: 700;
  color: #fff;
  margin-bottom: 8px;
  line-height: 1.3;
}

.hero-author {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 16px;
}

.hero-stats {
  display: flex;
  gap: 20px;
}

.hero-stat {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
}

.hero-stat svg {
  opacity: 0.8;
}

.hero-dots {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-top: 20px;
}

.hero-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
}

.hero-dot.active {
  background: #00d4ff;
  width: 24px;
  border-radius: 4px;
}

/* 我的日记区 */
.my-diary-section {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  padding: 20px;
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 16px;
  color: rgba(255, 255, 255, 0.9);
  letter-spacing: 0.5px;
}

.diary-count {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
  background: rgba(255, 255, 255, 0.05);
  padding: 6px 12px;
  border-radius: 10px;
}

.search-bar {
  margin-bottom: 16px;
}

.tech-input {
  width: 100%;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  color: #fff;
  font-size: 14px;
  transition: all 0.3s ease;
}

.tech-input:focus {
  outline: none;
  border-color: rgba(0, 212, 255, 0.4);
  background: rgba(255, 255, 255, 0.08);
}

.tech-input::placeholder {
  color: rgba(255, 255, 255, 0.3);
}

.diary-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.diary-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}

.diary-card:hover {
  background: rgba(255, 255, 255, 0.04);
  border-color: rgba(255, 255, 255, 0.1);
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
}

.diary-main {
  display: flex;
  gap: 12px;
  flex: 1;
  cursor: pointer;
  min-width: 0;
}

.delete-btn {
  width: 36px;
  height: 36px;
  background: rgba(255, 71, 87, 0.1);
  border: 1px solid rgba(255, 71, 87, 0.2);
  border-radius: 8px;
  color: rgba(255, 71, 87, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.delete-btn:hover {
  background: rgba(255, 71, 87, 0.2);
  border-color: rgba(255, 71, 87, 0.4);
  color: #ff4757;
  transform: scale(1.05);
}

.delete-btn:active {
  transform: scale(0.95);
}

.diary-images {
  width: 80px;
  height: 80px;
  border-radius: 12px;
  overflow: hidden;
  flex-shrink: 0;
}

.diary-images img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.diary-images.placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 212, 255, 0.1);
  font-size: 28px;
}

.diary-content {
  flex: 1;
  min-width: 0;
}

.diary-title {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 6px;
}

.diary-excerpt {
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.diary-meta {
  display: flex;
  gap: 12px;
  font-size: 11px;
  color: var(--text-secondary);
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  margin: 0 16px;
}

.empty-illustration {
  font-size: 56px;
  margin-bottom: 20px;
  opacity: 0.6;
}

.empty-state h3 {
  font-size: 20px;
  font-weight: 600;
  color: #fff;
  margin-bottom: 8px;
}

.empty-tip {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.4);
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
}

.modal-content {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 20px;
  padding: 0;
  width: 100%;
  max-width: 900px;
  max-height: 90vh;
  overflow: hidden;
}

.modal-content.editor-modal {
  background: transparent;
  border: none;
  max-width: 1000px;
}

/* 悬浮按钮 FAB */
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
  box-shadow: 
    0 6px 20px rgba(0, 212, 255, 0.4),
    0 0 0 1px rgba(255, 255, 255, 0.1) inset;
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  z-index: 100;
}

.fab-button:hover {
  transform: scale(1.1) rotate(90deg);
  box-shadow: 
    0 8px 30px rgba(0, 212, 255, 0.5),
    0 0 0 1px rgba(255, 255, 255, 0.2) inset;
}

.fab-button:active {
  transform: scale(0.95);
}

/* 侧边栏 */
.sidebar-section {
  margin-bottom: 32px;
}

.sidebar-section-title {
  font-size: 14px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 16px;
  letter-spacing: 0.5px;
}

/* 分类毛玻璃卡片 */
.category-cards {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.category-glass-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  background: transparent;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}

.category-glass-card:hover {
  background: rgba(255, 255, 255, 0.02);
  border-color: rgba(255, 255, 255, 0.12);
  transform: translateX(4px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.category-glass-card.travel:hover {
  border-color: rgba(255, 107, 107, 0.3);
}

.category-glass-card.food:hover {
  border-color: rgba(255, 217, 61, 0.3);
}

.category-glass-card.photo:hover {
  border-color: rgba(78, 205, 196, 0.3);
}

.category-glass-card.notes:hover {
  border-color: rgba(167, 139, 250, 0.3);
}

.card-icon {
  font-size: 20px;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
  flex-shrink: 0;
}

.card-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
}

.card-name {
  font-size: 13px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.85);
}

.card-count {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
}

.card-glow {
  position: absolute;
  top: 0;
  right: 0;
  width: 60px;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.02));
  opacity: 0;
  transition: opacity 0.3s ease;
}

.category-glass-card:hover .card-glow {
  opacity: 1;
}

/* 数据统计可视化 */
.stats-visual {
  background: transparent;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}

.stat-big-number {
  text-align: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.big-num {
  font-size: 48px;
  font-weight: 700;
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1;
}

.big-label {
  display: block;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
  margin-top: 4px;
}

/* 进度条 */
.stat-progress-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 20px;
}

.progress-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.progress-name {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
}

.progress-value {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
  font-variant-numeric: tabular-nums;
}

.progress-bar-bg {
  height: 4px;
  background: rgba(255, 255, 255, 0.06);
  border-radius: 2px;
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.6s ease;
}

.progress-bar-fill.travel {
  background: linear-gradient(90deg, #ff6b6b, #ff8e53);
}

.progress-bar-fill.food {
  background: linear-gradient(90deg, #ffd93d, #ff6b6b);
}

.progress-bar-fill.photo {
  background: linear-gradient(90deg, #4ecdc4, #44a08d);
}

/* 环形图 */
.stats-circles {
  display: flex;
  justify-content: center;
  gap: 32px;
  padding-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.stat-circle-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.circle-chart {
  position: relative;
  width: 60px;
  height: 60px;
}

.circle-chart svg {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}

.circle-bg {
  fill: none;
  stroke: rgba(255, 255, 255, 0.06);
  stroke-width: 3;
}

.circle-fill {
  fill: none;
  stroke: url(#gradientPurple);
  stroke-width: 3;
  stroke-linecap: round;
  transition: stroke-dasharray 0.6s ease;
}

.circle-fill.orange {
  stroke: url(#gradientOrange);
}

.circle-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  line-height: 1;
}

.circle-num {
  font-size: 16px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}

.circle-label {
  font-size: 9px;
  color: rgba(255, 255, 255, 0.4);
}

.circle-desc {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
}

/* 我的日记入口 */
.user-diary-entry {
  display: flex;
  align-items: center;
  gap: 14px;
  width: 100%;
  padding: 16px;
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.1), rgba(123, 44, 191, 0.1));
  border: 1px solid rgba(0, 212, 255, 0.2);
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: left;
}

.user-diary-entry:hover {
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.15), rgba(123, 44, 191, 0.15));
  border-color: rgba(0, 212, 255, 0.4);
  transform: translateX(4px);
}

.entry-icon {
  font-size: 28px;
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 212, 255, 0.1);
  border-radius: 12px;
}

.entry-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.entry-title {
  font-size: 15px;
  font-weight: 600;
  color: #fff;
}

.entry-desc {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

.entry-arrow {
  color: rgba(255, 255, 255, 0.4);
  transition: all 0.3s ease;
}

.user-diary-entry:hover .entry-arrow {
  color: #00d4ff;
  transform: translateX(4px);
}
</style>
