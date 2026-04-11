<template>
  <div class="smart-editor">
    <!-- 分屏布局：桌面端 -->
    <div class="editor-layout" :class="{ 'mobile': isMobile }">
      <!-- 左侧：编辑区 -->
      <div class="edit-section">
        <!-- Magic Input 区域 -->
        <div class="magic-input-section">
          <div class="section-header">
            <h3 class="section-title">
              <span class="title-icon">✨</span>
              魔法输入
            </h3>
            <p class="section-desc">随意记录你的旅行点滴，AI会帮你整理成精美的日记</p>
          </div>
          
          <div class="input-wrapper">
            <textarea
              v-model="rawInput"
              class="magic-textarea"
              placeholder="在这里随意写下你的旅行笔记...

例如：
今天早上9点到了京都站，天气很好。先去酒店放了行李，然后去了清水寺，人很多但是景色超美。中午在二年坂吃了拉面，下午去了岚山看竹林。晚上回酒店休息。

或者上传图片，让AI帮你识别地点和场景！"
              @input="handleInput"
            ></textarea>
            
            <!-- 图片上传 -->
            <div class="upload-area" v-if="!uploadedImages.length">
              <input
                type="file"
                ref="fileInput"
                multiple
                accept="image/*"
                @change="handleImageUpload"
                class="file-input"
              />
              <button class="upload-btn" @click="$refs.fileInput.click()">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                  <circle cx="8.5" cy="8.5" r="1.5"/>
                  <polyline points="21 15 16 10 5 21"/>
                </svg>
                <span>添加图片</span>
              </button>
            </div>
            
            <!-- 已上传图片预览 -->
            <div class="image-preview-list" v-else>
              <div v-for="(img, index) in uploadedImages" :key="index" class="preview-item">
                <img :src="img" alt="预览" />
                <button class="remove-btn" @click="removeImage(index)">×</button>
              </div>
              <button class="add-more-btn" @click="$refs.fileInput.click()">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="12" y1="5" x2="12" y2="19"/>
                  <line x1="5" y1="12" x2="19" y2="12"/>
                </svg>
              </button>
            </div>
          </div>
          
          <!-- AI 整理按钮 -->
          <button
            class="ai-organize-btn"
            :class="{ 'loading': isOrganizing, 'has-content': rawInput.trim() }"
            :disabled="!rawInput.trim() || isOrganizing"
            @click="organizeWithAI"
          >
            <span v-if="!isOrganizing" class="btn-content">
              <svg class="sparkle-icon" width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2L14.09 8.26L20 9.27L15.55 13.14L16.82 19.02L12 15.77L7.18 19.02L8.45 13.14L4 9.27L9.91 8.26L12 2Z"/>
              </svg>
              <span>AI 智能整理</span>
            </span>
            <span v-else class="btn-content">
              <span class="loading-dots">
                <span></span>
                <span></span>
                <span></span>
              </span>
              <span>AI 正在整理...</span>
            </span>
          </button>
        </div>
        
        <!-- 手动编辑区（展开后显示） -->
        <div class="manual-edit-section" v-if="showManualEdit">
          <div class="section-header">
            <h3 class="section-title">手动编辑</h3>
            <button class="toggle-btn" @click="showManualEdit = false">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="18 15 12 9 6 15"/>
              </svg>
            </button>
          </div>
          <div class="manual-inputs">
            <div class="input-group">
              <label>标题</label>
              <input v-model="diaryTitle" type="text" placeholder="给你的日记起个标题" />
            </div>
            <div class="input-row">
              <div class="input-group">
                <label>预算</label>
                <input v-model="diaryBudget" type="text" placeholder="¥3,000" />
              </div>
              <div class="input-group">
                <label>同伴</label>
                <input v-model="diaryCompanion" type="text" placeholder="朋友" />
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 右侧：预览区 -->
      <div class="preview-section">
        <div class="preview-header">
          <h3 class="preview-title">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
              <circle cx="12" cy="12" r="3"/>
            </svg>
            实时预览
          </h3>
          <div class="preview-actions">
            <button class="action-btn" @click="showManualEdit = !showManualEdit">
              {{ showManualEdit ? '收起' : '编辑' }}
            </button>
          </div>
        </div>
        
        <div class="preview-content">
          <!-- 空状态 -->
          <div v-if="!structuredData.length && !isOrganizing" class="empty-state">
            <div class="empty-illustration">
              <svg width="120" height="120" viewBox="0 0 120 120" fill="none">
                <circle cx="60" cy="60" r="50" fill="#F3F4F6"/>
                <path d="M40 70L50 55L60 65L75 45L85 60" stroke="#6366F1" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
                <circle cx="45" cy="45" r="5" fill="#6366F1"/>
                <circle cx="75" cy="40" r="4" fill="#8B5CF6"/>
                <circle cx="85" cy="55" r="3" fill="#A78BFA"/>
              </svg>
            </div>
            <h4 class="empty-title">开始你的旅行记录</h4>
            <p class="empty-desc">
              在左侧输入你的旅行笔记<br>
              点击"AI 智能整理"按钮，见证魔法发生 ✨
            </p>
            <div class="empty-tips">
              <div class="tip-item">
                <span class="tip-icon">📝</span>
                <span>支持自然语言描述</span>
              </div>
              <div class="tip-item">
                <span class="tip-icon">🖼️</span>
                <span>上传图片自动识别</span>
              </div>
              <div class="tip-item">
                <span class="tip-icon">⚡</span>
                <span>一键生成时间轴</span>
              </div>
            </div>
          </div>
          
          <!-- 加载状态 -->
          <div v-else-if="isOrganizing" class="loading-state">
            <div class="loading-animation">
              <div class="loading-circle"></div>
              <div class="loading-circle"></div>
              <div class="loading-circle"></div>
            </div>
            <p class="loading-text">AI 正在分析你的旅行笔记...</p>
            <p class="loading-subtext">识别时间、地点、活动</p>
          </div>
          
          <!-- 预览卡片 -->
          <div v-else class="preview-card">
            <!-- Hero 区域 -->
            <div class="preview-hero" v-if="uploadedImages.length">
              <img :src="uploadedImages[0]" alt="封面" />
              <div class="hero-overlay"></div>
              <div class="hero-content">
                <h2 class="hero-title">{{ diaryTitle || '未命名日记' }}</h2>
                <div class="hero-meta">
                  <span>{{ formatDate(new Date()) }}</span>
                </div>
              </div>
            </div>
            
            <!-- 信息标签 -->
            <div class="info-pills">
              <div class="pill budget-pill" v-if="diaryBudget">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
                <span>{{ diaryBudget }}</span>
              </div>
              <div class="pill companion-pill" v-if="diaryCompanion">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"/>
                </svg>
                <span>{{ diaryCompanion }}</span>
              </div>
            </div>
            
            <!-- 时间轴 -->
            <div class="timeline-section">
              <h4 class="timeline-title">行程安排</h4>
              <div class="timeline">
                <div
                  v-for="(day, dayIndex) in structuredData"
                  :key="dayIndex"
                  class="timeline-day"
                >
                  <div class="day-header">
                    <div class="day-badge">Day {{ day.day }}</div>
                    <span class="day-theme">{{ day.theme || '精彩一天' }}</span>
                  </div>
                  <div class="day-content">
                    <div
                      v-for="(activity, actIndex) in day.activities"
                      :key="actIndex"
                      class="timeline-item"
                    >
                      <div class="timeline-marker">
                        <div class="timeline-dot"></div>
                        <div class="timeline-line" v-if="actIndex < day.activities.length - 1"></div>
                      </div>
                      <div class="timeline-card">
                        <div class="card-time">{{ activity.time }}</div>
                        <div class="card-content">
                          <h5 class="card-title">{{ activity.title }}</h5>
                          <p class="card-location" v-if="activity.location">
                            <span class="location-pin">
                              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"/>
                                <circle cx="12" cy="10" r="3"/>
                              </svg>
                            </span>
                            <span class="location-name">{{ activity.location }}</span>
                          </p>
                          <p class="card-insight" v-if="activity.insight">
                            <span class="insight-dot">✦</span>
                            {{ activity.insight }}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 图片画廊 -->
            <div class="gallery-section" v-if="uploadedImages.length > 1">
              <h4 class="gallery-title">旅行相册</h4>
              <div class="gallery-grid">
                <div
                  v-for="(img, index) in uploadedImages.slice(1)"
                  :key="index"
                  class="gallery-item"
                >
                  <img :src="img" alt="旅行照片" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 底部操作栏 -->
    <div class="editor-footer-bar">
      <button class="footer-btn secondary" @click="emit('cancel')">取消</button>
      <button
        class="footer-btn primary"
        :disabled="!canPublish"
        @click="publishDiary"
      >
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M19 21H5a2 2 0 01-2-2V5a2 2 0 012-2h11l5 5v11a2 2 0 01-2 2z"/>
          <polyline points="17 21 17 13 7 13 7 21"/>
          <polyline points="7 3 7 8 15 8"/>
        </svg>
        发布日记
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const emit = defineEmits(['save', 'publish', 'cancel'])

// 响应式状态
const isMobile = ref(window.innerWidth < 768)
const rawInput = ref('')
const isOrganizing = ref(false)
const uploadedImages = ref([])
const showManualEdit = ref(false)

// 日记元数据
const diaryTitle = ref('')
const diaryBudget = ref('')
const diaryCompanion = ref('')

// 结构化数据
const structuredData = ref([])

// 监听窗口大小变化
onMounted(() => {
  window.addEventListener('resize', () => {
    isMobile.value = window.innerWidth < 768
  })
})

// 计算属性
const canPublish = computed(() => {
  return structuredData.value.length > 0 || rawInput.value.trim().length > 10
})

// 处理输入
const handleInput = () => {
  // 可以在这里添加实时分析逻辑
}

// 处理图片上传
const handleImageUpload = (event) => {
  const files = event.target.files
  if (!files.length) return

  Array.from(files).forEach(file => {
    const reader = new FileReader()
    reader.onload = (e) => {
      uploadedImages.value.push(e.target.result)
    }
    reader.readAsDataURL(file)
  })
}

// 移除图片
const removeImage = (index) => {
  uploadedImages.value.splice(index, 1)
}

// AI 整理功能
const organizeWithAI = async () => {
  if (!rawInput.value.trim()) {
    ElMessage.warning('请先输入一些旅行笔记')
    return
  }

  isOrganizing.value = true

  try {
    // 模拟 AI 处理延迟
    await new Promise(resolve => setTimeout(resolve, 2000))

    // 解析输入文本
    const parsed = parseTravelNotes(rawInput.value)
    structuredData.value = parsed.timeline
    
    // 自动提取标题
    if (!diaryTitle.value) {
      diaryTitle.value = extractDiaryTitle(rawInput.value)
    }
    
    // 自动提取预算
    if (!diaryBudget.value) {
      diaryBudget.value = extractBudget(rawInput.value)
    }

    ElMessage.success('AI 整理完成！')
  } catch (error) {
    console.error('整理失败:', error)
    ElMessage.error('整理失败，请重试')
  } finally {
    isOrganizing.value = false
  }
}

// ========== 智能解析旅行笔记 ==========

// 去噪：移除填充词
const denoiseText = (text) => {
  const fillerWords = [
    '哎呀', '我觉得', '大概', '可能', '好像', '那个', '这个',
    '然后', '接着', '之后', '后来', '最后', '首先', '其实',
    '说实话', '说真的', '怎么说呢', '总之', '反正', '就是'
  ]
  
  let cleaned = text
  fillerWords.forEach(word => {
    cleaned = cleaned.replace(new RegExp(word, 'g'), '')
  })
  
  // 移除多余的空格和标点
  cleaned = cleaned.replace(/\s+/g, ' ').trim()
  
  return cleaned
}

// 时间标准化映射
const normalizeTime = (text) => {
  const timeMap = {
    // 早上
    '早上六七点': '06:30',
    '早上七八点': '07:30',
    '早上八九点': '08:30',
    '早上九点多': '09:30',
    '早上十点': '10:00',
    '早上十点多': '10:30',
    '早上': '08:00',
    // 上午
    '上午': '10:00',
    '上午九点多': '09:30',
    '上午十点': '10:00',
    '上午十点多': '10:30',
    '上午十一点': '11:00',
    // 中午
    '中午': '12:00',
    '中午十二点多': '12:30',
    '中午一点': '13:00',
    // 下午
    '下午': '14:00',
    '下午一两点': '13:30',
    '下午两点多': '14:30',
    '下午三四点': '15:30',
    '下午四点': '16:00',
    '傍晚': '17:30',
    // 晚上
    '晚上': '19:00',
    '晚上六七点': '18:30',
    '晚上七八点': '19:30',
    '晚上八点': '20:00',
    '晚上八点多': '20:30',
    '晚上九点': '21:00',
    '深夜': '23:00',
    '凌晨': '05:00'
  }
  
  // 先尝试匹配完整短语
  for (const [phrase, time] of Object.entries(timeMap)) {
    if (text.includes(phrase)) {
      return { time, matchedPhrase: phrase }
    }
  }
  
  // 匹配数字时间格式
  const numMatch = text.match(/(\d{1,2})[点:：](\d{0,2})?/)
  if (numMatch) {
    const hour = numMatch[1].padStart(2, '0')
    const minute = (numMatch[2] || '00').padStart(2, '0')
    return { time: `${hour}:${minute}`, matchedPhrase: numMatch[0] }
  }
  
  return { time: '09:00', matchedPhrase: '' }
}

// 提取地点
const extractLocation = (text) => {
  // 地点关键词模式
  const locationPatterns = [
    /在([\u4e00-\u9fa5]{2,8})(?:站|寺|宫|社|园|馆|店|场|街|路|巷|阁|塔|桥|山|湖|海|岛|村|镇|城|区)/,
    /去([\u4e00-\u9fa5]{2,8})(?:站|寺|宫|社|园|馆|店|场|街|路|巷|阁|塔|桥|山|湖|海|岛|村|镇|城|区)?/,
    /([\u4e00-\u9fa5]{2,8})(?:火锅|餐厅|饭店|酒店|民宿|客栈|机场|车站|地铁站|公交站|景区|景点|博物馆|美术馆|公园|广场|商场|超市)/,
    /([\u4e00-\u9fa5]{2,6})(?:家|个)?(?:店|馆|厅|吧|屋|坊)/
  ]
  
  for (const pattern of locationPatterns) {
    const match = text.match(pattern)
    if (match) {
      return match[1] || match[0]
    }
  }
  
  return ''
}

// 提取活动标题（简短动作）
const extractTitle = (text, location) => {
  // 动作关键词
  const actionPatterns = [
    /(?:吃|品尝|尝试)(?:了)?([\u4e00-\u9fa5]{2,8})/,
    /(?:去|到|逛|游览|参观|打卡)(?:了)?([\u4e00-\u9fa5]{2,8})/,
    /(?:住|入住|住在)(?:了)?([\u4e00-\u9fa5]{2,8})/,
    /(?:拍|拍照|拍摄)(?:了)?([\u4e00-\u9fa5]{2,8})/,
    /(?:买|购买|逛)(?:了)?([\u4e00-\u9fa5]{2,8})/,
    /(?:看|观看|欣赏)(?:了)?([\u4e00-\u9fa5]{2,8})/
  ]
  
  for (const pattern of actionPatterns) {
    const match = text.match(pattern)
    if (match) {
      const action = match[0].replace(/了/g, '')
      return action
    }
  }
  
  // 如果没有匹配到动作，返回简化描述
  return text.slice(0, 12).replace(/[，,。！!]/g, '')
}

// 提取Insight（氛围/感受）
const extractInsight = (text) => {
  // 感受关键词
  const insightPatterns = [
    /(?:感觉|觉得|体验)(?:很|特别|超级|真的)?([\u4e00-\u9fa5]{3,20})/,
    /(?:景色|风景|环境|氛围|服务|味道)(?:很|特别|超级|真的)?([\u4e00-\u9fa5]{3,20})/,
    /(?:推荐|值得|不错|很棒|超赞|绝美|震撼)([\u4e00-\u9fa5]{0,15})/,
    /([\u4e00-\u9fa5]{3,20})(?:拍照|出片|打卡|必去|必吃)/
  ]
  
  for (const pattern of insightPatterns) {
    const match = text.match(pattern)
    if (match) {
      let insight = match[0]
      // 限制长度
      if (insight.length > 20) {
        insight = insight.slice(0, 20) + '...'
      }
      return insight
    }
  }
  
  // 默认返回简化描述
  return text.slice(0, 18) + (text.length > 18 ? '...' : '')
}

// 主解析函数
const parseTravelNotes = (text) => {
  // 1. 去噪
  const cleanedText = denoiseText(text)
  
  // 2. 按句子分割
  const sentences = cleanedText
    .split(/[。！!\n]+/)
    .map(s => s.trim())
    .filter(s => s.length > 3)
  
  const timeline = []
  let currentDay = {
    day: 1,
    theme: '精彩一天',
    activities: []
  }
  
  sentences.forEach((sentence, index) => {
    // 检测是否是新一天的开始
    if (sentence.includes('第') && sentence.includes('天')) {
      if (currentDay.activities.length > 0) {
        timeline.push({ ...currentDay })
        currentDay = {
          day: currentDay.day + 1,
          theme: '精彩一天',
          activities: []
        }
      }
      return
    }
    
    // 提取时间
    const { time, matchedPhrase } = normalizeTime(sentence)
    
    // 提取地点
    const location = extractLocation(sentence)
    
    // 提取标题
    const title = extractTitle(sentence, location)
    
    // 提取Insight
    const insight = extractInsight(sentence)
    
    // 只有当有实质内容时才添加
    if (title || location) {
      currentDay.activities.push({
        time,
        title: title || '旅行活动',
        location: location || '',
        insight: insight || sentence.slice(0, 20)
      })
    }
  })
  
  // 添加最后一天
  if (currentDay.activities.length > 0) {
    timeline.push(currentDay)
  }
  
  // 如果没有解析出任何内容，创建一个默认的
  if (timeline.length === 0 || timeline[0].activities.length === 0) {
    timeline.push({
      day: 1,
      theme: '精彩一天',
      activities: [{
        time: '09:00',
        title: '开始旅行',
        location: '',
        insight: cleanedText.slice(0, 20) || '期待已久的旅程'
      }]
    })
  }
  
  return { timeline }
}

// 提取日记主标题
const extractDiaryTitle = (text) => {
  const lines = text.split('\n')
  for (const line of lines) {
    if (line.includes('京都')) return '京都之旅'
    if (line.includes('东京')) return '东京漫步'
    if (line.includes('大阪')) return '大阪美食行'
    if (line.includes('北海道')) return '北海道之旅'
    if (line.includes('成都')) return '成都美食行'
    if (line.includes('重庆')) return '山城漫步'
  }
  return '我的旅行日记'
}

// 提取预算
const extractBudget = (text) => {
  const budgetMatch = text.match(/(\d{3,5})元?/)
  if (budgetMatch) {
    return `¥${budgetMatch[1]}`
  }
  return '¥3,000'
}

// 格式化日期
const formatDate = (date) => {
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

// 发布日记
const publishDiary = () => {
  if (!canPublish.value) {
    ElMessage.warning('请先输入内容并整理')
    return
  }

  const diary = {
    title: diaryTitle.value || '我的旅行日记',
    content: rawInput.value,
    budget: diaryBudget.value,
    companion: diaryCompanion.value,
    images: uploadedImages.value,
    timeline: structuredData.value,
    createdAt: new Date().toISOString()
  }

  emit('publish', diary)
  ElMessage.success('日记发布成功！')
}
</script>

<style scoped>
.smart-editor {
  min-height: 100vh;
  background: linear-gradient(135deg, #F8F9FC 0%, #FFFFFF 50%, #F0F4F8 100%);
  position: relative;
}

/* 分屏布局 */
.editor-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  min-height: calc(100vh - 80px);
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
  gap: 24px;
}

.editor-layout.mobile {
  grid-template-columns: 1fr;
  padding: 16px;
}

/* 左侧编辑区 */
.edit-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* Magic Input 区域 */
.magic-input-section {
  background: white;
  border-radius: 24px;
  padding: 32px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
}

.section-header {
  margin-bottom: 24px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1.25rem;
  font-weight: 700;
  color: #1F2937;
  margin: 0 0 8px 0;
}

.title-icon {
  font-size: 1.5rem;
}

.section-desc {
  font-size: 0.9375rem;
  color: #6B7280;
  margin: 0;
  line-height: 1.5;
}

.input-wrapper {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.magic-textarea {
  width: 100%;
  min-height: 280px;
  padding: 20px;
  border: 2px solid #E5E7EB;
  border-radius: 16px;
  font-size: 1rem;
  line-height: 1.7;
  resize: vertical;
  transition: all 0.3s ease;
  font-family: inherit;
  color: #374151;
}

.magic-textarea:focus {
  outline: none;
  border-color: #6366F1;
  box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1);
}

.magic-textarea::placeholder {
  color: #9CA3AF;
}

/* 上传区域 */
.upload-area {
  border: 2px dashed #D1D5DB;
  border-radius: 12px;
  padding: 24px;
  text-align: center;
  transition: all 0.3s ease;
}

.upload-area:hover {
  border-color: #6366F1;
  background: rgba(99, 102, 241, 0.02);
}

.file-input {
  display: none;
}

.upload-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: transparent;
  border: none;
  color: #6B7280;
  font-size: 0.9375rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.upload-btn:hover {
  color: #6366F1;
}

.upload-btn svg {
  stroke: currentColor;
}

/* 图片预览 */
.image-preview-list {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.preview-item {
  position: relative;
  width: 80px;
  height: 80px;
  border-radius: 12px;
  overflow: hidden;
}

.preview-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.remove-btn {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 24px;
  height: 24px;
  background: rgba(0, 0, 0, 0.5);
  border: none;
  border-radius: 50%;
  color: white;
  font-size: 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.remove-btn:hover {
  background: rgba(239, 68, 68, 0.8);
}

.add-more-btn {
  width: 80px;
  height: 80px;
  border: 2px dashed #D1D5DB;
  border-radius: 12px;
  background: transparent;
  color: #9CA3AF;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.add-more-btn:hover {
  border-color: #6366F1;
  color: #6366F1;
  background: rgba(99, 102, 241, 0.05);
}

/* AI 整理按钮 */
.ai-organize-btn {
  width: 100%;
  padding: 16px 24px;
  background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);
  border: none;
  border-radius: 14px;
  color: white;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 8px;
  position: relative;
  overflow: hidden;
}

.ai-organize-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s ease;
}

.ai-organize-btn:hover::before {
  left: 100%;
}

.ai-organize-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(99, 102, 241, 0.35);
}

.ai-organize-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.ai-organize-btn.loading {
  background: linear-gradient(135deg, #8B5CF6 0%, #A78BFA 100%);
}

.btn-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.sparkle-icon {
  animation: sparkle 2s ease-in-out infinite;
}

@keyframes sparkle {
  0%, 100% { transform: scale(1) rotate(0deg); }
  50% { transform: scale(1.1) rotate(10deg); }
}

.loading-dots {
  display: flex;
  gap: 4px;
}

.loading-dots span {
  width: 8px;
  height: 8px;
  background: white;
  border-radius: 50%;
  animation: bounce 1.4s ease-in-out infinite both;
}

.loading-dots span:nth-child(1) { animation-delay: -0.32s; }
.loading-dots span:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

/* 手动编辑区 */
.manual-edit-section {
  background: white;
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
}

.manual-edit-section .section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.toggle-btn {
  width: 32px;
  height: 32px;
  background: #F3F4F6;
  border: none;
  border-radius: 8px;
  color: #6B7280;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.toggle-btn:hover {
  background: #E5E7EB;
  color: #374151;
}

.manual-inputs {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.input-group label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
}

.input-group input {
  padding: 12px 16px;
  border: 1px solid #E5E7EB;
  border-radius: 10px;
  font-size: 0.9375rem;
  transition: all 0.2s ease;
}

.input-group input:focus {
  outline: none;
  border-color: #6366F1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.input-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

/* 右侧预览区 */
.preview-section {
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
  overflow: hidden;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #F3F4F6;
}

.preview-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 1rem;
  font-weight: 600;
  color: #374151;
  margin: 0;
}

.preview-title svg {
  stroke: #6366F1;
}

.preview-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  padding: 8px 16px;
  background: #F3F4F6;
  border: none;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-btn:hover {
  background: #E5E7EB;
}

.preview-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 48px 24px;
  min-height: 400px;
}

.empty-illustration {
  margin-bottom: 24px;
}

.empty-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1F2937;
  margin: 0 0 12px 0;
}

.empty-desc {
  font-size: 0.9375rem;
  color: #6B7280;
  margin: 0 0 32px 0;
  line-height: 1.6;
}

.empty-tips {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.tip-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 20px;
  background: #F9FAFB;
  border-radius: 10px;
  font-size: 0.875rem;
  color: #4B5563;
}

.tip-icon {
  font-size: 1.125rem;
}

/* 加载状态 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 64px 24px;
  min-height: 400px;
}

.loading-animation {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
}

.loading-circle {
  width: 12px;
  height: 12px;
  background: linear-gradient(135deg, #6366F1, #8B5CF6);
  border-radius: 50%;
  animation: pulse 1.4s ease-in-out infinite both;
}

.loading-circle:nth-child(1) { animation-delay: -0.32s; }
.loading-circle:nth-child(2) { animation-delay: -0.16s; }

@keyframes pulse {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.5; }
  40% { transform: scale(1); opacity: 1; }
}

.loading-text {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1F2937;
  margin: 0 0 8px 0;
}

.loading-subtext {
  font-size: 0.875rem;
  color: #6B7280;
  margin: 0;
}

/* 预览卡片 */
.preview-card {
  background: white;
}

/* Hero 区域 */
.preview-hero {
  position: relative;
  aspect-ratio: 16/9;
  border-radius: 16px;
  overflow: hidden;
  margin-bottom: 20px;
}

.preview-hero img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.hero-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.7) 0%, rgba(0, 0, 0, 0.3) 50%, transparent 100%);
}

.hero-content {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 32px;
  color: white;
}

.hero-title {
  font-size: 1.75rem;
  font-weight: 700;
  margin: 0 0 8px 0;
  line-height: 1.2;
}

.hero-meta {
  font-size: 0.9375rem;
  opacity: 0.9;
}

/* 信息标签 */
.info-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 24px;
}

.pill {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 500;
  border: 1px solid;
}

.budget-pill {
  background: rgba(16, 185, 129, 0.08);
  border-color: rgba(16, 185, 129, 0.2);
  color: #059669;
}

.companion-pill {
  background: rgba(99, 102, 241, 0.08);
  border-color: rgba(99, 102, 241, 0.2);
  color: #4F46E5;
}

/* 时间轴 */
.timeline-section {
  margin-bottom: 32px;
}

.timeline-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: #1F2937;
  margin: 0 0 20px 0;
}

.timeline {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.timeline-day {
  position: relative;
}

.day-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.day-badge {
  background: linear-gradient(135deg, #6366F1, #8B5CF6);
  color: white;
  padding: 6px 12px;
  border-radius: 16px;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.05em;
}

.day-theme {
  font-size: 1rem;
  font-weight: 600;
  color: #374151;
}

.day-content {
  padding-left: 8px;
}

.timeline-item {
  display: flex;
  gap: 16px;
  position: relative;
  padding-bottom: 20px;
}

.timeline-item:last-child {
  padding-bottom: 0;
}

.timeline-marker {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 20px;
  flex-shrink: 0;
}

.timeline-dot {
  width: 12px;
  height: 12px;
  background: white;
  border: 3px solid #6366F1;
  border-radius: 50%;
  z-index: 2;
}

.timeline-line {
  width: 2px;
  flex: 1;
  background: linear-gradient(to bottom, #E0E7FF, #C7D2FE);
  margin-top: 4px;
}

.timeline-card {
  flex: 1;
  background: #F9FAFB;
  border-radius: 12px;
  padding: 16px;
  border: 1px solid #F3F4F6;
}

.card-time {
  font-size: 0.75rem;
  font-weight: 600;
  color: #6366F1;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 6px;
}

.card-title {
  font-size: 1rem;
  font-weight: 600;
  color: #1F2937;
  margin: 0 0 6px 0;
}

.card-location {
  display: flex;
  align-items: center;
  gap: 6px;
  margin: 0 0 8px 0;
}

.location-pin {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  background: linear-gradient(135deg, #6366F1, #8B5CF6);
  border-radius: 50%;
  flex-shrink: 0;
}

.location-pin svg {
  stroke: white;
  width: 12px;
  height: 12px;
}

.location-name {
  font-size: 0.875rem;
  font-weight: 500;
  color: #4B5563;
}

.card-insight {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  font-size: 0.8125rem;
  color: #8B5CF6;
  line-height: 1.5;
  margin: 0;
  padding: 8px 10px;
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.08), rgba(167, 139, 250, 0.08));
  border-radius: 8px;
  border-left: 3px solid #8B5CF6;
}

.insight-dot {
  font-size: 0.75rem;
  line-height: 1.4;
  flex-shrink: 0;
}

/* 图片画廊 */
.gallery-section {
  margin-top: 32px;
}

.gallery-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: #1F2937;
  margin: 0 0 16px 0;
}

.gallery-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.gallery-item {
  aspect-ratio: 1;
  border-radius: 12px;
  overflow: hidden;
}

.gallery-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.gallery-item:hover img {
  transform: scale(1.05);
}

/* 底部操作栏 */
.editor-footer-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  background: white;
  border-top: 1px solid #E5E7EB;
  box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.05);
  z-index: 100;
}

.footer-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border-radius: 10px;
  font-size: 0.9375rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.footer-btn.secondary {
  background: #F3F4F6;
  border: none;
  color: #4B5563;
}

.footer-btn.secondary:hover {
  background: #E5E7EB;
}

.footer-btn.primary {
  background: linear-gradient(135deg, #6366F1, #8B5CF6);
  border: none;
  color: white;
}

.footer-btn.primary:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.35);
}

.footer-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .magic-input-section {
    padding: 20px;
  }
  
  .magic-textarea {
    min-height: 200px;
  }
  
  .preview-content {
    padding: 16px;
  }
  
  .hero-content {
    padding: 20px;
  }
  
  .hero-title {
    font-size: 1.375rem;
  }
  
  .timeline-card {
    padding: 12px;
  }
  
  .editor-footer-bar {
    padding: 12px 16px;
  }
  
  .footer-btn {
    padding: 10px 18px;
    font-size: 0.875rem;
  }
}
</style>
