<template>
  <div class="diary-page">
    <header class="page-header">
      <button class="back-btn" @click="goBack">←</button>
      <h1 class="page-title">我的日记</h1>
      <button class="action-btn" @click="showCreate">+</button>
    </header>

    <main class="page-content">
      <!-- 搜索 -->
      <div class="search-bar">
        <input 
          type="text" 
          class="tech-input" 
          placeholder="搜索日记..." 
          v-model="searchQuery"
        />
      </div>

      <!-- 日记列表 -->
      <div class="diary-list">
        <div 
          v-for="diary in filteredDiaries" 
          :key="diary.id"
          class="diary-card tech-card"
          @click="viewDiary(diary)"
        >
          <div class="diary-images" v-if="diary.images?.length">
            <img :src="diary.images[0]" :alt="diary.title" />
          </div>
          <div class="diary-content">
            <h3 class="diary-title">{{ diary.title }}</h3>
            <p class="diary-excerpt">{{ diary.content?.slice(0, 80) }}...</p>
            <div class="diary-meta">
              <span class="meta-item">
                <span>👁️</span>
                {{ diary.view_count }}
              </span>
              <span class="meta-item">
                <span>⭐</span>
                {{ diary.avg_rating }}
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
      <div v-if="filteredDiaries.length === 0" class="empty-state">
        <span class="empty-icon">📝</span>
        <p>还没有旅游日记</p>
        <p class="empty-tip">开始记录你的旅行吧</p>
      </div>
    </main>

    <!-- 创建日记弹窗 -->
    <div v-if="showCreateModal" class="modal-overlay" @click.self="showCreateModal = false">
      <div class="modal-content">
        <h2>写日记</h2>

        <!-- 模板选择 -->
        <div class="template-section">
          <p class="template-label">选择模板：</p>
          <div class="template-buttons">
            <button
              class="template-btn"
              :class="{ active: selectedTemplate === 'travel' }"
              @click="selectTemplate('travel')"
            >
              🏃 行程攻略
            </button>
            <button
              class="template-btn"
              :class="{ active: selectedTemplate === 'food' }"
              @click="selectTemplate('food')"
            >
              🍜 美食记录
            </button>
            <button
              class="template-btn"
              :class="{ active: selectedTemplate === 'photo' }"
              @click="selectTemplate('photo')"
            >
              📸 摄影大片
            </button>
          </div>
        </div>

        <input
          type="text"
          class="tech-input"
          placeholder="日记标题"
          v-model="newDiary.title"
        />
        <textarea
          class="tech-input diary-textarea"
          placeholder="记录你的旅行..."
          v-model="newDiary.content"
        ></textarea>
        <div class="modal-actions">
          <button class="tech-button secondary" @click="showCreateModal = false">取消</button>
          <button class="tech-button" @click="createDiary">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()

const searchQuery = ref('')
const showCreateModal = ref(false)
const diaries = ref([])
const currentUserId = ref(null)
const selectedTemplate = ref('')

// 日记模板
const diaryTemplates = {
  travel: `【行程概览】
📅 出行日期：
👥 出行人数：
💰 预算：

【每日行程】
📍 Day 1 ：
• 上午：
• 中午：
• 下午：
• 晚上：

📍 Day 2 ：

📍 Day 3 ：

【推荐指数】⭐⭐⭐⭐⭐

【实用贴士】
✓
✓
✓

【总体感受】
`,
  food: `【美食清单】
🍜 推荐菜品：
• 1.
• 2.
• 3.

【餐厅信息】
📍 店名：
📍 地址：
💰 人均：

【必吃推荐】⭐⭐⭐⭐⭐

【美食亮点】
• 口味：
• 环境：
• 服务：

【总评】
`,
  photo: `【拍摄地点】
📍 位置：
📅 拍摄时间：

【器材参数】
📷 相机：
🔭 镜头：
⚙️ 参数：

【拍摄亮点】
• 光线：
• 构图：
• 色彩：

【后期处理】
• 调色：
• 滤镜：

【推荐指数】⭐⭐⭐⭐⭐

【拍摄建议】
`
}

// 选择模板
const selectTemplate = (template) => {
  if (selectedTemplate.value === template) {
    selectedTemplate.value = ''
    newDiary.value.content = ''
  } else {
    selectedTemplate.value = template
    newDiary.value.content = diaryTemplates[template]
  }
}

onMounted(() => {
  // 检查登录状态
  const userId = localStorage.getItem('userId')
  if (!userId) {
    // 未登录时跳转到登录页
    router.push('/login')
    return
  } else {
    currentUserId.value = parseInt(userId)
  }
  fetchDiaries()
})

const fetchDiaries = async () => {
  try {
    const response = await fetch(`http://localhost:8000/api/diaries?user_id=${currentUserId.value}`)
    if (response.ok) {
      diaries.value = await response.json()
    }
  } catch (error) {
    console.error('获取日记失败:', error)
    // 使用默认数据
    diaries.value = [
      {
        id: 1,
        title: '北京三日游',
        content: '终于去了心心念念的故宫，真的太震撼了！',
        images: [],
        view_count: 128,
        avg_rating: 4.8,
        created_at: '2024-01-15'
      }
    ]
  }
}

const newDiary = ref({
  title: '',
  content: ''
})

const filteredDiaries = computed(() => {
  if (!searchQuery.value) return diaries.value
  return diaries.value.filter(d => 
    d.title.includes(searchQuery.value) || 
    d.content.includes(searchQuery.value)
  )
})

const formatDate = (date) => {
  return date || ''
}

const goBack = () => {
  router.back()
}

const viewDiary = (diary) => {
  // 查看日记详情
}

const showCreate = () => {
  showCreateModal.value = true
}

const createDiary = () => {
  if (!newDiary.value.title || !newDiary.value.content) {
    ElMessage.warning('请填写标题和内容')
    return
  }
  
  diaries.value.unshift({
    id: Date.now(),
    ...newDiary.value,
    images: [],
    view_count: 0,
    avg_rating: 0,
    created_at: new Date().toISOString().split('T')[0]
  })
  
  showCreateModal.value = false
  newDiary.value = { title: '', content: '' }
  ElMessage.success('日记已保存')
}
</script>

<style scoped>
.diary-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #0a0a1a 0%, #1a1a2e 100%);
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 15px 20px;
  background: rgba(10, 10, 26, 0.9);
  backdrop-filter: blur(10px);
  position: sticky;
  top: 0;
  z-index: 100;
}

.back-btn, .action-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 1px solid var(--border-color);
  background: transparent;
  color: var(--text-primary);
  font-size: 18px;
  cursor: pointer;
}

.action-btn {
  font-size: 24px;
}

.page-content {
  padding: 20px;
  padding-bottom: 80px;
}

.search-bar {
  margin-bottom: 20px;
}

.diary-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.diary-card {
  display: flex;
  gap: 15px;
  cursor: pointer;
}

.diary-images {
  width: 100px;
  height: 100px;
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
}

.diary-images img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.diary-content {
  flex: 1;
  min-width: 0;
}

.diary-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 8px;
}

.diary-excerpt {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 10px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.diary-meta {
  display: flex;
  gap: 15px;
  font-size: 12px;
  color: var(--text-secondary);
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  color: var(--text-secondary);
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 15px;
}

.empty-tip {
  font-size: 13px;
  opacity: 0.6;
}

/* 弹窗 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.template-section {
  margin-bottom: 15px;
}

.template-label {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 10px;
}

.template-buttons {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.template-btn {
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(0, 212, 255, 0.2);
  border-radius: 20px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s;
}

.template-btn:hover {
  background: rgba(0, 212, 255, 0.1);
}

.template-btn.active {
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  border-color: transparent;
  color: #fff;
}

.modal-content {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 25px;
  width: 100%;
  max-width: 500px;
}

.modal-content h2 {
  font-size: 20px;
  margin-bottom: 20px;
}

.diary-textarea {
  min-height: 150px;
  resize: vertical;
  margin: 15px 0;
}

.modal-actions {
  display: flex;
  gap: 15px;
  justify-content: flex-end;
}

.modal-actions .tech-button {
  padding: 10px 20px;
}
</style>
