<template>
  <div class="diary-page">
    <!-- 导航栏 -->
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
                    <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
                  </svg>
                  {{ publicDiaries[currentSlide]?.likes || 0 }}
                </span>
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
              @click="viewDiary(diary)"
            >
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
                <span class="card-count">{{ getDiaryCountByType('travel') }} 篇</span>
              </div>
              <div class="card-glow"></div>
            </button>
            <button class="category-glass-card food" @click="createWithTemplate('food')">
              <div class="card-icon">🍜</div>
              <div class="card-info">
                <span class="card-name">美食</span>
                <span class="card-count">{{ getDiaryCountByType('food') }} 篇</span>
              </div>
              <div class="card-glow"></div>
            </button>
            <button class="category-glass-card photo" @click="createWithTemplate('photo')">
              <div class="card-icon">📸</div>
              <div class="card-info">
                <span class="card-name">摄影</span>
                <span class="card-count">{{ getDiaryCountByType('photo') }} 篇</span>
              </div>
              <div class="card-glow"></div>
            </button>
            <button class="category-glass-card notes" @click="createWithTemplate('notes')">
              <div class="card-icon">💭</div>
              <div class="card-info">
                <span class="card-name">随笔</span>
                <span class="card-count">{{ getDiaryCountByType('notes') }} 篇</span>
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
              <span class="big-num">{{ diaries.length }}</span>
              <span class="big-label">篇日记</span>
            </div>
            
            <!-- 进度条 -->
            <div class="stat-progress-list">
              <div class="progress-item">
                <div class="progress-header">
                  <span class="progress-name">行程</span>
                  <span class="progress-value">{{ getDiaryCountByType('travel') }}</span>
                </div>
                <div class="progress-bar-bg">
                  <div class="progress-bar-fill travel" :style="{ width: getDiaryCountByType('travel') > 0 ? (getDiaryCountByType('travel') / Math.max(diaries.length, 1) * 100) + '%' : '0%' }"></div>
                </div>
              </div>
              <div class="progress-item">
                <div class="progress-header">
                  <span class="progress-name">美食</span>
                  <span class="progress-value">{{ getDiaryCountByType('food') }}</span>
                </div>
                <div class="progress-bar-bg">
                  <div class="progress-bar-fill food" :style="{ width: getDiaryCountByType('food') > 0 ? (getDiaryCountByType('food') / Math.max(diaries.length, 1) * 100) + '%' : '0%' }"></div>
                </div>
              </div>
              <div class="progress-item">
                <div class="progress-header">
                  <span class="progress-name">摄影</span>
                  <span class="progress-value">{{ getDiaryCountByType('photo') }}</span>
                </div>
                <div class="progress-bar-bg">
                  <div class="progress-bar-fill photo" :style="{ width: getDiaryCountByType('photo') > 0 ? (getDiaryCountByType('photo') / Math.max(diaries.length, 1) * 100) + '%' : '0%' }"></div>
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
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import Navbar from '../components/Navbar.vue'
import SmartDiaryEditor from '../components/SmartDiaryEditor.vue'

const router = useRouter()

const searchQuery = ref('')
const showCreateModal = ref(false)
const diaries = ref([])
const publicDiaries = ref([])
const currentSlide = ref(0)
const currentUserId = ref(null)

// 智能编辑器相关
const inspirationText = ref('')
const generating = ref(false)
const generatedContent = ref('')
const selectedStyle = ref('healing')
const uploadedImages = ref([])
const detectedType = ref('')
const generatedTags = ref([])
const showManualEditor = ref(false)
const imageInput = ref(null)

// 写作风格
const writingStyles = [
  { key: 'healing', name: '治愈系', emoji: '🌸' },
  { key: 'humorous', name: '幽默风', emoji: '😄' },
  { key: 'documentary', name: '纪实风', emoji: '📰' },
  { key: 'poetic', name: '诗意风', emoji: '🌙' },
  { key: 'concise', name: '简洁风', emoji: '✨' }
]

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

// 公开日记示例（轮播用）- 与详情页 Mock 数据保持一致
const samplePublicDiaries = [
  {
    id: 1,
    title: 'Kyoto 京都：千年古都的秋日私语',
    author: '旅行摄影师小林',
    cover: 'https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=800&q=80',
    likes: 3280,
    rating: 4.9
  },
  {
    id: 2,
    title: '成都美食探店：藏在巷子里的烟火气',
    author: '吃货小王',
    cover: 'https://images.unsplash.com/photo-1563245372-f21724e3856d?w=800&q=80',
    likes: 2156,
    rating: 4.8
  },
  {
    id: 3,
    title: '冰岛环岛自驾：追逐极光的14天',
    author: '极地探险者',
    cover: 'https://images.unsplash.com/photo-1531366936337-7c912a4589a7?w=800&q=80',
    likes: 5620,
    rating: 5.0
  },
  {
    id: 4,
    title: '杭州西湖美如画',
    author: '摄影爱好者',
    cover: 'https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800&q=80',
    likes: 412,
    rating: 4.7
  }
]

let slideInterval = null

onMounted(() => {
  const userId = localStorage.getItem('userId')
  if (!userId) {
    router.push('/login')
    return
  }
  currentUserId.value = parseInt(userId)
  
  fetchDiaries()
  fetchPublicDiaries()
  
  // 自动轮播
  slideInterval = setInterval(() => {
    currentSlide.value = (currentSlide.value + 1) % publicDiaries.value.length
  }, 4000)
})

onUnmounted(() => {
  if (slideInterval) clearInterval(slideInterval)
})

const fetchDiaries = async () => {
  try {
    const response = await fetch(`http://localhost:8000/api/diaries?user_id=${currentUserId.value}`)
    if (response.ok) {
      diaries.value = await response.json()
    }
  } catch (error) {
    console.error('获取日记失败:', error)
  }
}

const fetchPublicDiaries = async () => {
  // 强制使用 Mock 数据，确保轮播图显示正确的内容
  publicDiaries.value = samplePublicDiaries
}

const newDiary = ref({
  title: '',
  content: '',
  diary_type: 'travel'
})

const filteredDiaries = computed(() => {
  if (!searchQuery.value) return diaries.value
  return diaries.value.filter(d => 
    d.title?.includes(searchQuery.value) || 
    d.content?.includes(searchQuery.value)
  )
})

const getTypeEmoji = (type) => {
  const found = diaryTypes.find(t => t.value === type)
  return found?.emoji || '📝'
}

// 获取某类型的日记数量
const getDiaryCountByType = (type) => {
  return diaries.value.filter(d => d.diary_type === type).length
}

// 获取总记录天数
const getTotalDays = () => {
  if (diaries.value.length === 0) return 0
  const dates = diaries.value.map(d => new Date(d.created_at).toDateString())
  return new Set(dates).size
}

// 获取总浏览量
const getTotalViews = () => {
  return diaries.value.reduce((sum, d) => sum + (d.view_count || 0), 0)
}

// 获取平均评分
const getAvgRating = () => {
  if (diaries.value.length === 0) return '0.0'
  const total = diaries.value.reduce((sum, d) => sum + (d.avg_rating || 0), 0)
  return (total / diaries.value.length).toFixed(1)
}

const getPlaceholder = () => {
  return templates[newDiary.value.diary_type] || '记录你的旅行故事...'
}

const formatDate = (date) => {
  if (!date) return ''
  return date.split('T')[0]
}

const viewDiary = (diary) => {
  // 跳转到日记详情页
  router.push(`/diary/${diary.id}`)
}

// ========== 智能编辑器功能 ==========

// 计算属性：是否可以保存
const canSave = computed(() => {
  return newDiary.value.title && (generatedContent.value || newDiary.value.content)
})

// AI 生成日记内容
const generateWithAI = async () => {
  if (!inspirationText.value.trim()) {
    ElMessage.warning('请输入灵感内容')
    return
  }
  
  try {
    generating.value = true
    
    // 准备图片数据（base64）
    const imageBase64List = []
    for (const img of uploadedImages.value) {
      if (img.base64) {
        imageBase64List.push(img.base64)
      }
    }
    
    const response = await fetch('http://localhost:8000/api/diary-generator/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        inspiration: inspirationText.value.trim(),
        style: selectedStyle.value,
        images: imageBase64List
      })
    })
    
    if (response.ok) {
      const result = await response.json()
      
      // 填充生成的内容
      generatedContent.value = result.content
      detectedType.value = result.diary_type
      generatedTags.value = result.tags || []
      
      // 如果没有标题，使用生成的标题
      if (!newDiary.value.title && result.title) {
        newDiary.value.title = result.title
      }
      
      // 设置日记类型
      if (result.diary_type) {
        newDiary.value.diary_type = result.diary_type
      }
      
      ElMessage.success('AI 生成成功！')
    } else {
      const error = await response.json()
      throw new Error(error.detail || '生成失败')
    }
  } catch (error) {
    console.error('AI 生成失败:', error)
    ElMessage.error('AI 生成失败：' + error.message)
  } finally {
    generating.value = false
  }
}

// 触发文件选择
const triggerImageUpload = () => {
  imageInput.value?.click()
}

// 处理图片选择
const handleImageSelect = async (event) => {
  const files = event.target.files
  if (!files || files.length === 0) return
  
  await processFiles(files)
  
  // 清空 input，允许重复选择同一文件
  event.target.value = ''
}

// 处理拖拽
const handleDrop = async (event) => {
  const files = event.dataTransfer.files
  if (!files || files.length === 0) return
  
  await processFiles(files)
}

// 处理文件
const processFiles = async (files) => {
  for (const file of files) {
    if (!file.type.startsWith('image/')) {
      ElMessage.warning('请上传图片文件')
      continue
    }
    
    // 读取文件
    const base64 = await readFileAsBase64(file)
    const url = URL.createObjectURL(file)
    
    uploadedImages.value.push({
      name: file.name,
      url: url,
      base64: base64.split(',')[1], // 去掉 data:image/jpeg;base64, 前缀
      analyzing: true
    })
    
    // 分析图片内容
    analyzeImage(file, uploadedImages.value.length - 1)
  }
  
  ElMessage.success(`已添加 ${files.length} 张图片`)
}

// 读取文件为 Base64
const readFileAsBase64 = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(reader.result)
    reader.onerror = reject
    reader.readAsDataURL(file)
  })
}

// 分析图片内容
const analyzeImage = async (file, index) => {
  try {
    const formData = new FormData()
    formData.append('image', file)
    
    const response = await fetch('http://localhost:8000/api/diary-generator/analyze-image', {
      method: 'POST',
      body: formData
    })
    
    if (response.ok) {
      const result = await response.json()
      if (result.success && result.description) {
        // 将图片描述添加到灵感框
        if (inspirationText.value) {
          inspirationText.value += '\n图片内容：' + result.description
        } else {
          inspirationText.value = '图片内容：' + result.description
        }
        ElMessage.info('已识别图片内容，可点击 AI 生成按钮生成日记')
      }
    }
  } catch (error) {
    console.error('图片分析失败:', error)
  } finally {
    if (uploadedImages.value[index]) {
      uploadedImages.value[index].analyzing = false
    }
  }
}

// 移除图片
const removeImage = (index) => {
  const img = uploadedImages.value[index]
  if (img && img.url) {
    URL.revokeObjectURL(img.url)
  }
  uploadedImages.value.splice(index, 1)
}

// 获取类型标签
const getTypeLabel = (type) => {
  const found = diaryTypes.find(t => t.value === type)
  return found ? found.label : type
}

// 创建日记时使用 AI 生成的内容
const createDiary = async () => {
  if (!newDiary.value.title) {
    ElMessage.warning('请填写日记标题')
    return
  }
  
  // 使用 AI 生成的内容或手动输入的内容
  const contentToUse = generatedContent.value || newDiary.value.content
  
  if (!contentToUse) {
    ElMessage.warning('请生成内容或手动输入内容')
    return
  }
  
  try {
    const response = await fetch('http://localhost:8000/api/diaries', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title: newDiary.value.title,
        content: contentToUse,
        diary_type: detectedType.value || newDiary.value.diary_type || 'notes',
        user_id: currentUserId.value,
        is_public: false,
        view_count: 0,
        avg_rating: 0,
        images: uploadedImages.value.map(img => img.url)
      })
    })
    
    if (response.ok) {
      const diary = await response.json()
      diaries.value.unshift(diary)
      ElMessage.success('日记已保存')
      closeModal()
    } else {
      const error = await response.json()
      ElMessage.error('保存失败：' + (error.detail || '未知错误'))
    }
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败')
  }
}

const createWithTemplate = (type) => {
  newDiary.value = {
    title: '',
    content: templates[type],
    diary_type: type
  }
  showCreateModal.value = true
}

const addSection = (section) => {
  newDiary.value.content += '\n' + section + '\n'
}

const closeModal = () => {
  showCreateModal.value = false
  newDiary.value = { title: '', content: '', diary_type: 'travel' }
  // 重置智能编辑器状态
  inspirationText.value = ''
  generatedContent.value = ''
  uploadedImages.value = []
  detectedType.value = ''
  generatedTags.value = []
}

// 打开 AI 编辑器
const openAIEditor = () => {
  newDiary.value = { title: '', content: '', diary_type: 'travel' }
  showCreateModal.value = true
}

// 处理编辑器保存草稿事件
const handleSaveDraft = (draft) => {
  // 草稿已保存在 localStorage，这里可以添加额外逻辑
  console.log('草稿已保存:', draft)
}

// 处理编辑器发布事件
const handlePublish = async (diary) => {
  try {
    const response = await fetch('http://localhost:8000/api/diaries', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title: diary.title,
        content: diary.content,
        diary_type: newDiary.value.diary_type || 'notes',
        user_id: currentUserId.value,
        is_public: false,
        view_count: 0,
        avg_rating: 0
      })
    })
    
    if (response.ok) {
      const savedDiary = await response.json()
      diaries.value.unshift(savedDiary)
      ElMessage.success('日记发布成功！')
      closeModal()
    } else {
      const error = await response.json()
      ElMessage.error('保存失败：' + (error.detail || '未知错误'))
    }
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败')
  }
}

// 打开相机上传
const openCameraUpload = () => {
  newDiary.value = { title: '', content: '', diary_type: 'travel' }
  showCreateModal.value = true
  // 触发图片上传
  setTimeout(() => {
    imageInput.value?.click()
  }, 100)
}
</script>

<style scoped>
.diary-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #0a0a1a 0%, #1a1a2e 100%);
}

.page-content {
  padding: 80px 20px 100px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 模板选择区 */
.template-section {
  margin-bottom: 30px;
}

.template-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.template-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 15px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(0, 212, 255, 0.15);
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.3s;
}

.template-card:hover {
  background: rgba(0, 212, 255, 0.1);
  border-color: rgba(0, 212, 255, 0.4);
  transform: translateY(-2px);
}

.template-icon {
  font-size: 32px;
  margin-bottom: 8px;
}

.template-name {
  font-size: 15px;
  font-weight: 600;
  color: #fff;
  margin-bottom: 4px;
}

.template-desc {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

/* 轮播区 */
.discover-section {
  margin-bottom: 30px;
}

.carousel-container {
  position: relative;
  overflow: hidden;
  border-radius: 16px;
}

.carousel {
  display: flex;
  transition: transform 0.5s ease;
}

.carousel-item {
  min-width: 100%;
  padding: 0 5px;
  box-sizing: border-box;
}

.diary-showcase {
  border-radius: 16px;
  overflow: hidden;
}

.showcase-image {
  height: 180px;
  background-size: cover;
  background-position: center;
  position: relative;
}

.showcase-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 20px;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.8));
  color: #fff;
}

.showcase-overlay h3 {
  font-size: 18px;
  margin-bottom: 4px;
}

.showcase-overlay p {
  font-size: 13px;
  opacity: 0.8;
  margin-bottom: 8px;
}

.showcase-stats {
  display: flex;
  gap: 15px;
  font-size: 13px;
}

.carousel-dots {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-top: 12px;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
  cursor: pointer;
  transition: all 0.3s;
}

.dot.active {
  background: #00d4ff;
  width: 20px;
  border-radius: 4px;
}

/* 我的日记区 */
.my-diary-section {
  margin-bottom: 30px;
}

.search-bar {
  margin-bottom: 15px;
}

.diary-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.diary-card {
  display: flex;
  gap: 12px;
  cursor: pointer;
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
  padding: 50px 20px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 16px;
  border: 1px dashed rgba(0, 212, 255, 0.2);
}

.empty-illustration {
  font-size: 64px;
  margin-bottom: 20px;
}

.empty-state h3 {
  font-size: 18px;
  margin-bottom: 8px;
  color: #fff;
}

.empty-state p {
  font-size: 14px;
  color: var(--text-secondary);
}

.empty-tip {
  margin-top: 8px;
  font-size: 13px;
  color: rgba(0, 212, 255, 0.7);
}

.quick-start-btn {
  margin-top: 20px;
  padding: 12px 30px;
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  border: none;
  border-radius: 25px;
  color: #fff;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.quick-start-btn:hover {
  transform: scale(1.05);
  box-shadow: 0 5px 20px rgba(0, 212, 255, 0.4);
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

.modal-content h2 {
  font-size: 20px;
  margin-bottom: 20px;
}

.type-selector {
  margin-bottom: 15px;
}

.type-label {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
  display: block;
  margin-bottom: 10px;
}

.type-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.type-btn {
  padding: 8px 14px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s;
}

.type-btn:hover {
  background: rgba(0, 212, 255, 0.1);
}

.type-btn.active {
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  border-color: transparent;
  color: #fff;
}

.diary-textarea {
  min-height: 200px;
  resize: vertical;
  margin: 15px 0;
}

.quick-inputs {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 15px;
}

.quick-input-btn {
  padding: 6px 12px;
  background: rgba(0, 212, 255, 0.1);
  border: 1px solid rgba(0, 212, 255, 0.2);
  border-radius: 15px;
  color: rgba(0, 212, 255, 0.8);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.3s;
}

.quick-input-btn:hover {
  background: rgba(0, 212, 255, 0.2);
}

/* ========== 智能输入条样式已合并到下方 ========== */

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

.ai-placeholder {
  color: rgba(255, 255, 255, 0.5);
  font-size: 13px;
  flex: 1;
}

/* ========== 横向分类 Avatar ========== */
.category-avatars {
  display: flex;
  justify-content: space-around;
  gap: 16px;
  padding: 10px 0;
}

.category-avatar {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  background: transparent;
  border: none;
  cursor: pointer;
  transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.category-avatar:hover {
  transform: scale(1.05);
}

.category-avatar:active {
  transform: scale(0.95);
}

.avatar-glass {
  width: 64px;
  height: 64px;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 
    0 4px 20px rgba(0, 0, 0, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
}

.category-avatar:hover .avatar-glass {
  background: rgba(0, 212, 255, 0.15);
  border-color: rgba(0, 212, 255, 0.4);
  box-shadow: 
    0 4px 25px rgba(0, 212, 255, 0.25),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

.avatar-icon {
  font-size: 28px;
}

.avatar-label {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
  font-weight: 500;
}

/* ========== 推荐区卡片优化 ========== */
.showcase-image {
  height: 220px;
  aspect-ratio: 16 / 9;
  background-size: cover;
  background-position: center;
  position: relative;
  border-radius: 16px;
  box-shadow: 
    0 10px 40px rgba(0, 0, 0, 0.3),
    0 0 0 1px rgba(255, 255, 255, 0.05);
}

.diary-showcase {
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.25);
}

/* ========== 空状态优化 ========== */
.empty-illustration.small {
  font-size: 48px;
  margin-bottom: 16px;
}

.placeholder-cards {
  display: flex;
  gap: 12px;
  margin: 20px 0;
  flex-wrap: wrap;
  justify-content: center;
}

.placeholder-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 20px 24px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.placeholder-card.dashed {
  border: 2px dashed rgba(0, 212, 255, 0.25);
}

.placeholder-card:hover {
  background: rgba(0, 212, 255, 0.08);
  border-color: rgba(0, 212, 255, 0.4);
  transform: translateY(-3px);
}

.placeholder-icon {
  font-size: 32px;
}

.placeholder-text {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
}

/* ========== 导航容器 - 居中毛玻璃 ========== */
.nav-container {
  display: flex;
  justify-content: center;
  margin-bottom: 24px;
}

.nav-glass {
  display: flex;
  gap: 32px;
  padding: 16px 32px;
  max-width: 600px;
  background: rgba(255, 255, 255, 0.04);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 24px;
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.05);
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  background: transparent;
  border: none;
  cursor: pointer;
  transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  padding: 4px 8px;
}

.nav-item:hover {
  transform: scale(1.08) translateY(-2px);
}

.nav-item:active {
  transform: scale(0.95);
}

.nav-icon-3d {
  width: 52px;
  height: 52px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 
    0 8px 24px rgba(0, 0, 0, 0.3),
    inset 0 2px 4px rgba(255, 255, 255, 0.2),
    inset 0 -2px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.nav-icon-3d svg {
  width: 28px;
  height: 28px;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
}

.nav-item:hover .nav-icon-3d {
  transform: translateY(-4px);
  box-shadow: 
    0 12px 32px rgba(0, 0, 0, 0.4),
    inset 0 2px 4px rgba(255, 255, 255, 0.3),
    inset 0 -2px 4px rgba(0, 0, 0, 0.1);
}

.nav-icon-3d.travel {
  background: linear-gradient(135deg, rgba(255, 107, 107, 0.2), rgba(255, 142, 83, 0.1));
}

.nav-icon-3d.food {
  background: linear-gradient(135deg, rgba(255, 217, 61, 0.2), rgba(255, 107, 107, 0.1));
}

.nav-icon-3d.photo {
  background: linear-gradient(135deg, rgba(78, 205, 196, 0.2), rgba(68, 160, 141, 0.1));
}

.nav-icon-3d.notes {
  background: linear-gradient(135deg, rgba(167, 139, 250, 0.2), rgba(124, 58, 237, 0.1));
}

.nav-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
  font-weight: 500;
  letter-spacing: 0.5px;
}

/* ========== Hero Card 大卡片 ========== */
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

/* ========== 空状态 - 简洁优雅 ========== */
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

/* ========== 悬浮按钮 FAB ========== */
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

/* ========== 统一背景色 ========== */
.diary-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #0a0a1a 0%, #12121f 50%, #0a0a1a 100%);
  position: relative;
  overflow-x: hidden;
}

/* ========== 背景氛围灯 - blur 100px ========== */
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

/* 新增氛围灯 - 左右两侧 */
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

/* ========== 双栏布局 - 65:35 比例 ========== */
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

/* 统一中轴宽度 - 800px */
.main-column > * {
  width: 100%;
  max-width: 800px;
}

/* 响应式：移动端单列 */
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
}

/* ========== 我的日记区统一 ========== */
.my-diary-section {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 20px;
  padding: 20px;
  margin-top: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 16px;
  color: rgba(255, 255, 255, 0.9);
  letter-spacing: 0.5px;
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

/* ========== AI 输入条 - 主角化 Hero Input ========== */
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

/* 2px 渐变边框 - 紫青色 */
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

/* 呼吸灯外发光效果 */
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

/* 主角化占位符 */
.ai-placeholder {
  color: rgba(255, 255, 255, 0.85);
  font-size: 15px;
  font-weight: 500;
  flex: 1;
  letter-spacing: 0.3px;
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

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.modal-actions .tech-button {
  padding: 10px 24px;
}

/* ========== 智能编辑器样式 ========== */

.smart-editor {
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
}

.editor-title {
  font-size: 1.5rem;
  margin-bottom: 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.section-label {
  display: block;
  font-weight: 600;
  margin-bottom: 0.75rem;
  color: #e2e8f0;
  font-size: 0.95rem;
}

/* 灵感输入区 */
.inspiration-section {
  margin-bottom: 1.5rem;
  padding: 1.25rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.inspiration-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.ai-generate-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: white;
  padding: 0.5rem 1.25rem;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.ai-generate-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.ai-generate-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.ai-generate-btn.loading {
  background: linear-gradient(135deg, #a0aec0 0%, #718096 100%);
}

.loading-spinner {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.inspiration-input-wrapper {
  margin-bottom: 0.5rem;
}

.inspiration-textarea {
  width: 100%;
  min-height: 80px;
  padding: 0.75rem;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: #e2e8f0;
  font-size: 0.95rem;
  resize: vertical;
  transition: border-color 0.3s;
}

.inspiration-textarea:focus {
  outline: none;
  border-color: #667eea;
}

.inspiration-tip {
  font-size: 0.8rem;
  color: #a0aec0;
  margin: 0;
}

/* 风格选择器 */
.style-selector {
  margin-bottom: 1.5rem;
}

.style-buttons {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.style-btn {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #e2e8f0;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 0.875rem;
}

.style-btn:hover {
  background: rgba(255, 255, 255, 0.1);
}

.style-btn.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-color: transparent;
  color: white;
}

/* 图片上传区 */
.image-upload-section {
  margin-bottom: 1.5rem;
}

.image-dropzone {
  border: 2px dashed rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  padding: 2rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  background: rgba(0, 0, 0, 0.2);
  min-height: 150px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.image-dropzone:hover {
  border-color: #667eea;
  background: rgba(102, 126, 234, 0.05);
}

.dropzone-placeholder {
  color: #a0aec0;
}

.dropzone-icon {
  font-size: 3rem;
  display: block;
  margin-bottom: 1rem;
}

.dropzone-hint {
  font-size: 0.8rem;
  color: #718096;
  margin-top: 0.5rem;
}

.image-preview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 1rem;
  width: 100%;
}

.image-preview-item {
  position: relative;
  aspect-ratio: 1;
  border-radius: 8px;
  overflow: hidden;
  background: rgba(0, 0, 0, 0.3);
}

.preview-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 0.5rem;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.5rem;
}

.image-name {
  font-size: 0.75rem;
  color: white;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
}

.remove-image-btn {
  background: rgba(239, 68, 68, 0.8);
  border: none;
  color: white;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.3s;
}

.remove-image-btn:hover {
  background: rgba(239, 68, 68, 1);
}

.analyzing-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  color: white;
  font-size: 0.875rem;
}

.spinner-small {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

/* AI 生成内容区 */
.ai-content-section {
  margin-bottom: 1.5rem;
  padding: 1.25rem;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 12px;
  border: 1px solid rgba(102, 126, 234, 0.3);
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.content-actions {
  display: flex;
  gap: 0.5rem;
}

.regenerate-btn {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #e2e8f0;
  padding: 0.375rem 0.75rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.875rem;
  transition: all 0.3s;
}

.regenerate-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.generated-result {
  position: relative;
}

.generated-textarea {
  width: 100%;
  min-height: 200px;
  padding: 1rem;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: 8px;
  color: #e2e8f0;
  font-size: 0.95rem;
  line-height: 1.6;
  resize: vertical;
  font-family: inherit;
}

.generated-textarea:focus {
  outline: none;
  border-color: #667eea;
}

.generated-meta {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.meta-tag {
  background: rgba(102, 126, 234, 0.2);
  color: #a3bffa;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.tag-icon {
  font-size: 1rem;
}

/* 手动编辑切换 */
.manual-edit-toggle {
  margin-bottom: 1rem;
  text-align: center;
}

.toggle-btn {
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #a0aec0;
  padding: 0.5rem 1.5rem;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.875rem;
  transition: all 0.3s;
}

.toggle-btn:hover {
  border-color: #667eea;
  color: #667eea;
}

.manual-editor {
  margin-bottom: 1.5rem;
  padding: 1.25rem;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.hidden {
  display: none;
}

.title-input {
  margin-bottom: 1.5rem;
  font-size: 1.125rem;
  font-weight: 600;
}

/* ========== 侧边栏透明挂件风格 ========== */
.sidebar-widget {
  margin-bottom: 32px;
  padding-bottom: 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.sidebar-widget:last-child {
  border-bottom: none;
}

.widget-title {
  font-size: 11px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.4);
  margin-bottom: 12px;
  letter-spacing: 1px;
  text-transform: uppercase;
}

/* 分类列表 - 极简风格 */
.widget-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.widget-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 0;
  background: transparent;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  width: 100%;
  text-align: left;
}

.widget-item:hover {
  opacity: 0.8;
}

.widget-item:hover .widget-name {
  color: rgba(255, 255, 255, 0.9);
}

.widget-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}

.widget-dot.travel {
  background: #ff6b6b;
}

.widget-dot.food {
  background: #ffd93d;
}

.widget-dot.photo {
  background: #4ecdc4;
}

.widget-dot.notes {
  background: #a78bfa;
}

.widget-name {
  flex: 1;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
  transition: color 0.2s ease;
}

.widget-count {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.3);
  font-variant-numeric: tabular-nums;
}

/* 统计数据 - 横向排列 */
.widget-stats {
  display: flex;
  gap: 24px;
}

.widget-stat {
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.widget-stat-num {
  font-size: 20px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.8);
  font-variant-numeric: tabular-nums;
}

.widget-stat-label {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
}

/* 旧侧边栏样式保留兼容 */
.sidebar-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  padding: 20px;
  margin-bottom: 20px;
}

.sidebar-title {
  font-size: 15px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 16px;
  letter-spacing: 0.5px;
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

/* 主栏区域优化 */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.diary-count {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
  background: rgba(255, 255, 255, 0.05);
  padding: 6px 12px;
  border-radius: 10px;
}

.my-diary-section {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  padding: 20px;
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
}

/* Hero section 居中 */
.hero-section {
  width: 100%;
  max-width: 800px;
  margin: 0 auto 16px;
}

/* ========== 侧边栏毛玻璃卡片风格 ========== */
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

/* 分类毛玻璃卡片 - 轻量化 */
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

/* 数据统计可视化 - 轻量化 */
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
</style>
