<template>
  <div class="diary-page">
    <!-- 导航栏 -->
    <Navbar />

    <main class="page-content">
      <!-- 快速创建模板区 -->
      <div class="template-section">
        <h2 class="section-title">📝 开始写日记</h2>
        <div class="template-grid">
          <button class="template-card" @click="createWithTemplate('travel')">
            <span class="template-icon">🏃</span>
            <span class="template-name">行程攻略</span>
            <span class="template-desc">记录每日行程安排</span>
          </button>
          <button class="template-card" @click="createWithTemplate('food')">
            <span class="template-icon">🍜</span>
            <span class="template-name">美食探索</span>
            <span class="template-desc">分享地道美食体验</span>
          </button>
          <button class="template-card" @click="createWithTemplate('photo')">
            <span class="template-icon">📸</span>
            <span class="template-name">摄影大片</span>
            <span class="template-desc">记录绝美风景瞬间</span>
          </button>
          <button class="template-card" @click="createWithTemplate('notes')">
            <span class="template-icon">💭</span>
            <span class="template-name">随笔感悟</span>
            <span class="template-desc">自由书写旅行故事</span>
          </button>
        </div>
      </div>

      <!-- 欣赏他人日记 - 轮播 -->
      <div class="discover-section">
        <h2 class="section-title">🌟 发现精彩日记</h2>
        <div class="carousel-container">
          <div class="carousel" :style="{ transform: `translateX(-${currentSlide * 100}%)` }">
            <div 
              v-for="(diary, index) in publicDiaries" 
              :key="index" 
              class="carousel-item"
            >
              <div class="diary-showcase">
                <div class="showcase-image" :style="{ backgroundImage: `url(${diary.cover})` }">
                  <div class="showcase-overlay">
                    <h3>{{ diary.title }}</h3>
                    <p>{{ diary.author }}</p>
                    <div class="showcase-stats">
                      <span>❤️ {{ diary.likes }}</span>
                      <span>⭐ {{ diary.rating }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="carousel-dots">
            <span 
              v-for="(_, index) in publicDiaries" 
              :key="index"
              class="dot"
              :class="{ active: currentSlide === index }"
              @click="currentSlide = index"
            ></span>
          </div>
        </div>
      </div>

      <!-- 我的日记列表 -->
      <div class="my-diary-section">
        <h2 class="section-title">📒 我的日记</h2>
        
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
          <h3>还没有开始记录旅行</h3>
          <p>点击上方的模板卡片</p>
          <p class="empty-tip">开始记录你的第一篇旅游日记吧！</p>
          <button class="quick-start-btn" @click="createWithTemplate('travel')">
            立即开始 ✏️
          </button>
        </div>
      </div>
    </main>

    <!-- 创建日记弹窗 -->
    <div v-if="showCreateModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content">
        <h2>新建日记</h2>
        
        <input
          type="text"
          class="tech-input"
          placeholder="给日记起个标题吧"
          v-model="newDiary.title"
        />

        <div class="type-selector">
          <span class="type-label">日记类型：</span>
          <div class="type-buttons">
            <button 
              v-for="type in diaryTypes" 
              :key="type.value"
              class="type-btn"
              :class="{ active: newDiary.diary_type === type.value }"
              @click="newDiary.diary_type = type.value"
            >
              {{ type.emoji }} {{ type.label }}
            </button>
          </div>
        </div>

        <textarea
          class="tech-input diary-textarea"
          :placeholder="getPlaceholder()"
          v-model="newDiary.content"
        ></textarea>

        <!-- 便捷输入按钮 -->
        <div class="quick-inputs">
          <button class="quick-input-btn" @click="addSection('【今日行程】')">+ 行程</button>
          <button class="quick-input-btn" @click="addSection('【美食推荐】')">+ 美食</button>
          <button class="quick-input-btn" @click="addSection('【住宿推荐】')">+ 住宿</button>
          <button class="quick-input-btn" @click="addSection('【实用贴士】')">+ 贴士</button>
          <button class="quick-input-btn" @click="addSection('【推荐指数】⭐⭐⭐⭐⭐')">+ 评分</button>
        </div>

        <div class="modal-actions">
          <button class="tech-button secondary" @click="closeModal">取消</button>
          <button class="tech-button" @click="createDiary">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import Navbar from '../components/Navbar.vue'

const router = useRouter()

const searchQuery = ref('')
const showCreateModal = ref(false)
const diaries = ref([])
const publicDiaries = ref([])
const currentSlide = ref(0)
const currentUserId = ref(null)

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

// 公开日记示例（轮播用）
const samplePublicDiaries = [
  {
    title: '北京三日深度游',
    author: '旅行达人小明',
    cover: 'https://images.unsplash.com/photo-1599571234909-29ed5d1321d6?w=800&q=80',
    likes: 328,
    rating: 4.8
  },
  {
    title: '成都美食探店记',
    author: '吃货小王',
    cover: 'https://images.unsplash.com/photo-1622613744987-0e3527fae518?w=800&q=80',
    likes: 256,
    rating: 4.9
  },
  {
    title: '杭州西湖美如画',
    author: '摄影爱好者',
    cover: 'https://images.unsplash.com/photo-1537531383496-f4749a4c0b4d?w=800&q=80',
    likes: 412,
    rating: 4.7
  },
  {
    title: '西安古城墙骑行',
    author: '户外探索者',
    cover: 'https://images.unsplash.com/photo-1724458589661-a2f42eb58aca?w=800&q=80',
    likes: 189,
    rating: 4.6
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
  try {
    const response = await fetch('http://localhost:8000/api/diaries/public')
    if (response.ok) {
      const data = await response.json()
      publicDiaries.value = data.length > 0 ? data : samplePublicDiaries
    } else {
      publicDiaries.value = samplePublicDiaries
    }
  } catch (error) {
    publicDiaries.value = samplePublicDiaries
  }
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

const getPlaceholder = () => {
  return templates[newDiary.value.diary_type] || '记录你的旅行故事...'
}

const formatDate = (date) => {
  if (!date) return ''
  return date.split('T')[0]
}

const viewDiary = (diary) => {
  // 查看日记详情
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
}

const createDiary = async () => {
  if (!newDiary.value.title) {
    ElMessage.warning('请填写日记标题')
    return
  }
  
  try {
    const response = await fetch('http://localhost:8000/api/diaries', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ...newDiary.value,
        user_id: currentUserId.value,
        is_public: false,
        view_count: 0,
        avg_rating: 0
      })
    })
    
    if (response.ok) {
      const diary = await response.json()
      diaries.value.unshift(diary)
      ElMessage.success('日记已保存')
      closeModal()
    }
  } catch (error) {
    console.error('保存日记失败:', error)
    ElMessage.error('保存失败，请重试')
  }
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
  padding: 25px;
  width: 100%;
  max-width: 500px;
  max-height: 80vh;
  overflow-y: auto;
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
  color: #00d4ff;
}

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.modal-actions .tech-button {
  padding: 10px 24px;
}
</style>
