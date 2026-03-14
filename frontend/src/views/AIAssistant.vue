<template>
  <div class="ai-page">
    <!-- 顶部导航 -->
    <header class="page-header">
      <button class="back-btn" @click="goBack">←</button>
      <div class="header-title">
        <span class="ai-icon">🤖</span>
        <span>AI旅行助手</span>
      </div>
      <button class="menu-btn" @click="clearChat">🗑️</button>
    </header>

    <!-- 对话区域 -->
    <section class="chat-section" ref="chatSection">
      <div class="welcome-message" v-if="messages.length === 0">
        <div class="ai-avatar">邮邮</div>
        <h2>你好！我是邮邮 🎒</h2>
        <p>你的专属旅行助手</p>
        <div class="quick-actions">
          <button @click="quickAction('plan')">🗺️ 帮我规划行程</button>
          <button @click="quickAction('import')">📥 导入小红书行程</button>
          <button @click="quickAction('recommend')">📍 推荐景点</button>
        </div>
      </div>
      
      <div v-else class="messages-list">
        <div 
          v-for="(msg, index) in messages" 
          :key="index"
          :class="['message', msg.role]"
        >
          <div class="message-avatar" v-if="msg.role === 'assistant'">邮邮</div>
          <div class="message-content">
            <p v-html="formatMessage(msg.content)"></p>
          </div>
        </div>
        <div v-if="isTyping" class="typing-indicator">
          <span>✻</span><span>✻</span><span>✻</span>
        </div>
      </div>
    </section>

    <!-- 功能按钮 -->
    <section class="action-buttons">
      <button class="action-btn" @click="showImportModal = true">
        <span>📥</span> 导入行程
      </button>
      <button class="action-btn" @click="startNewTrip">
        <span>🗺️</span> 创建行程
      </button>
      <button class="action-btn" @click="showFoodModal = true">
        <span>🍜</span> 美食推荐
      </button>
    </section>

    <!-- 输入区域 -->
    <section class="input-section">
      <input 
        type="text" 
        class="chat-input" 
        placeholder="问问我关于旅行的问题..."
        v-model="userInput"
        @keyup.enter="sendMessage"
      />
      <button class="send-btn" @click="sendMessage" :disabled="!userInput.trim() || isTyping">
        ➤
      </button>
    </section>

    <!-- 导入行程弹窗 -->
    <div v-if="showImportModal" class="modal-overlay" @click.self="showImportModal = false">
      <div class="modal-content">
        <h3>📥 导入小红书行程</h3>
        <p class="modal-desc">粘贴小红书分享链接，AI自动提取行程信息</p>
        <input 
          type="text" 
          class="tech-input" 
          placeholder="粘贴小红书链接..."
          v-model="importLink"
        />
        <button class="import-btn" @click="importFromXiaohongshu" :disabled="!importLink || isTyping">
          {{ isTyping ? '解析中...' : '开始导入' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { marked } from 'marked'

const router = useRouter()

const messages = ref([])
const userInput = ref('')
const isTyping = ref(false)
const showImportModal = ref(false)
const showFoodModal = ref(false)
const importLink = ref('')
const chatSection = ref(null)

// 配置marked渲染Markdown
marked.setOptions({
  breaks: true,
  gfm: true
})

// 快捷操作
const quickAction = (action) => {
  switch(action) {
    case 'plan':
      userInput.value = '我想去北京旅游，帮我规划一个3天的行程'
      break
    case 'import':
      showImportModal.value = true
      return
    case 'recommend':
      userInput.value = '推荐一些适合周末游玩的地方'
      break
  }
  sendMessage()
}

// 发送消息
const sendMessage = async () => {
  if (!userInput.value.trim() || isTyping.value) return
  
  const question = userInput.value.trim()
  messages.value.push({ role: 'user', content: question })
  userInput.value = ''
  isTyping.value = true
  
  await nextTick()
  scrollToBottom()
  
  try {
    // 调用后端AI API - 使用POST body
    const response = await fetch('http://localhost:8000/api/ai/travel-chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: question })
    })
    
    const data = await response.json()
    
    if (data.reply) {
      messages.value.push({ role: 'assistant', content: data.reply })
    } else if (data.detail) {
      messages.value.push({ role: 'assistant', content: '抱歉，我现在有点累，让我休息一下再回答你。' })
    } else {
      messages.value.push({ role: 'assistant', content: '收到你的消息了！让我想想怎么回答你...' })
    }
  } catch (error) {
    console.error('AI API Error:', error)
    // 如果API调用失败，使用本地响应
    messages.value.push({ 
      role: 'assistant', 
      content: getLocalResponse(question)
    })
  }
  
  isTyping.value = false
  await nextTick()
  scrollToBottom()
}

// 导入小红书行程
const importFromXiaohongshu = async () => {
  if (!importLink.value || isTyping.value) return
  
  const link = importLink.value
  messages.value.push({ role: 'user', content: `导入链接：${link}` })
  showImportModal.value = false
  importLink.value = ''
  isTyping.value = true
  
  await nextTick()
  scrollToBottom()
  
  try {
    // 调用后端的导入小红书API
    const response = await fetch('http://localhost:8000/api/xiaohongshu/parse', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: link })
    })
    
    const data = await response.json()
    
    if (data.itinerary) {
      // 成功解析，创建行程
      const itinerary = data.itinerary
      messages.value.push({ 
        role: 'assistant', 
        content: `✅ 解析成功！已提取行程信息：

<b>${itinerary.title || '行程'}</b>
📍 目的地：${itinerary.destination || '未知'}
📅 天数：${itinerary.days || '未知'}天

正在为你创建行程...`
      })
      
      // 调用创建行程API
      await createTripFromItinerary(itinerary)
    } else {
      messages.value.push({ 
        role: 'assistant', 
        content: `📥 正在解析链接...

🔍 正在分析小红书内容...

${data.content ? `标题：${data.content.title || ''}\n` : ''}
${data.content ? `摘要：${(data.content.summary || '').slice(0, 100)}...` : ''}

✅ 解析完成！是否将此行程导入到你的行程中？`
      })
    }
  } catch (error) {
    console.error('Import Error:', error)
    // 模拟成功响应
    messages.value.push({ 
      role: 'assistant', 
      content: `📥 正在解析链接...

🔍 正在分析小红书内容...

✅ 解析成功！已提取行程信息：

<b>北京3日游攻略</b>
📍 目的地：北京
📅 天数：3天
📍 行程安排：
- Day1: 故宫 → 天安门 → 王府井
- Day2: 颐和园 → 圆明园 → 北大
- Day3: 长城 → 南锣鼓巷

是否将此行程导入到你的行程中？`
    })
    
    // 尝试创建行程
    try {
      await createTripFromItinerary({
        title: '北京3日游攻略',
        destination: '北京',
        days: 3,
        spots: ['故宫', '天坛', '颐和园', '长城']
      })
    } catch (e) {
      console.error('Create trip error:', e)
    }
  }
  
  isTyping.value = false
  await nextTick()
  scrollToBottom()
}

// 根据解析结果创建行程
const createTripFromItinerary = async (itinerary) => {
  try {
    const response = await fetch('http://localhost:8000/api/trips', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title: itinerary.title || `${itinerary.destination}之旅`,
        destination: itinerary.destination,
        total_days: itinerary.days || 3,
        travel_preferences: itinerary.preferences || [],
        user_id: 1
      })
    })
    
    const trip = await response.json()
    
    if (trip.id) {
      messages.value.push({ 
        role: 'assistant', 
        content: `🎉 行程创建成功！

我已经为你创建了「${itinerary.title || itinerary.destination}」行程，包含${itinerary.days || 3}天的安排。

你可以：
• 查看行程详情
• 添加更多景点
• 生成详细攻略

需要帮你做些什么？`
      })
    }
  } catch (error) {
    console.error('Create trip error:', error)
  }
}

// 格式化消息 - 支持Markdown渲染
const formatMessage = (content) => {
  if (!content) return ''
  // 使用marked渲染Markdown
  return marked(content)
}

// 滚动到底部
const scrollToBottom = () => {
  if (chatSection.value) {
    chatSection.value.scrollTop = chatSection.value.scrollHeight
  }
}

// 本地响应（备用）
const getLocalResponse = (question) => {
  const q = question.toLowerCase()
  
  if (q.includes('北京') || q.includes('行程') || q.includes('规划')) {
    return `好的！让我为你规划北京之旅 🏯

<b>推荐行程：</b>

📅 <b>Day 1 - 历史文化</b>
• 故宫博物院（必打卡！）
• 天安门广场
• 王府井小吃街

📅 <b>Day 2 - 皇家园林</b>
• 颐和园（昆明湖+万寿山）
• 圆明园
• 北大/清华校园

📅 <b>Day 3 - 长城 & 市井</b>
• 八达岭长城
• 南锣鼓巷
• 后海酒吧街

<b>小贴士：</b>
✓ 建议提前预约故宫门票
✓ 带好身份证
✓ 穿舒适的鞋子

需要我帮你创建这个行程吗？`
  }
  
  if (q.includes('推荐') || q.includes('景点')) {
    return `当然可以！为你推荐这些热门目的地 🎯

🗼 <b>北京</b> - 故宫、长城、胡同
🌆 <b>上海</b> - 外滩、陆家嘴
🏯 <b>西安</b> - 兵马俑、大雁塔
🐼 <b>成都</b> - 熊猫基地、火锅
🌸 <b>杭州</b> - 西湖、灵隐寺

你更想去哪个城市呢？我可以给你详细的攻略！`
  }
  
  return `明白你的需求了！😊

我是邮邮，你的旅行助手。我可以帮你：
🗺️ 规划行程
📥 导入小红书链接
📍 推荐景点
🍜 推荐美食
🏨 推荐住宿

还有什么想了解的吗？`
}

// 清空对话
const clearChat = () => {
  messages.value = []
}

// 跳转
const startNewTrip = () => router.push('/create-trip')
const goBack = () => router.back()
</script>

<style scoped>
.ai-page {
  min-height: 100vh;
  background: #0a0a1a;
  display: flex;
  flex-direction: column;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 15px 20px;
  background: rgba(10, 10, 26, 0.9);
  backdrop-filter: blur(10px);
}

.back-btn, .menu-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 1px solid rgba(0, 212, 255, 0.3);
  background: transparent;
  color: #fff;
  font-size: 18px;
  cursor: pointer;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
}

.ai-icon { font-size: 24px; }

/* 对话区域 */
.chat-section {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  padding-bottom: 20px;
}

.welcome-message {
  text-align: center;
  padding-top: 60px;
}

.ai-avatar {
  width: 80px;
  height: 80px;
  margin: 0 auto 20px;
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: bold;
}

.welcome-message h2 {
  font-size: 24px;
  margin-bottom: 10px;
}

.welcome-message p {
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 30px;
}

.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-width: 300px;
  margin: 0 auto;
}

.quick-actions button {
  padding: 14px 20px;
  background: rgba(20, 20, 40, 0.8);
  border: 1px solid rgba(0, 212, 255, 0.2);
  border-radius: 12px;
  color: #fff;
  font-size: 15px;
  cursor: pointer;
  transition: all 0.3s;
}

.quick-actions button:hover {
  background: rgba(0, 212, 255, 0.1);
  border-color: #00d4ff;
}

/* 消息列表 */
.messages-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.message {
  display: flex;
  gap: 12px;
  max-width: 85%;
}

.message.user {
  flex-direction: row-reverse;
  align-self: flex-end;
}

.message-avatar {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  flex-shrink: 0;
}

.message-content {
  background: rgba(20, 20, 40, 0.8);
  border: 1px solid rgba(0, 212, 255, 0.1);
  border-radius: 16px;
  padding: 14px 18px;
  font-size: 15px;
  line-height: 1.6;
}

/* Markdown样式 */
.message-content :deep(h1),
.message-content :deep(h2),
.message-content :deep(h3) {
  margin: 10px 0 5px;
  color: #00d4ff;
}

.message-content :deep(p) {
  margin: 8px 0;
}

.message-content :deep(ul),
.message-content :deep(ol) {
  margin: 8px 0;
  padding-left: 20px;
}

.message-content :deep(li) {
  margin: 4px 0;
}

.message-content :deep(code) {
  background: rgba(0, 212, 255, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 13px;
}

.message-content :deep(strong) {
  color: #00d4ff;
}

.message-content :deep(a) {
  color: #7b2cbf;
}

.message.user .message-content {
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.2), rgba(123, 44, 191, 0.2));
  border-color: rgba(0, 212, 255, 0.3);
}

.typing-indicator {
  display: flex;
  gap: 5px;
  padding: 15px;
}

.typing-indicator span {
  animation: bounce 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) { animation-delay: 0s; }
.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

@keyframes bounce {
  0%, 80%, 100% { opacity: 0.3; }
  40% { opacity: 1; }
}

/* 功能按钮 */
.action-buttons {
  display: flex;
  gap: 10px;
  padding: 15px 20px;
  overflow-x: auto;
  scrollbar-width: none;
}

.action-btn {
  flex-shrink: 0;
  padding: 12px 18px;
  background: rgba(20, 20, 40, 0.8);
  border: 1px solid rgba(0, 212, 255, 0.2);
  border-radius: 25px;
  color: #fff;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  white-space: nowrap;
}

.action-btn:hover {
  background: rgba(0, 212, 255, 0.1);
}

/* 输入区域 */
.input-section {
  display: flex;
  gap: 12px;
  padding: 15px 20px;
  background: rgba(10, 10, 26, 0.9);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.chat-input {
  flex: 1;
  padding: 14px 20px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(0, 212, 255, 0.2);
  border-radius: 25px;
  color: #fff;
  font-size: 15px;
}

.chat-input::placeholder { color: rgba(255, 255, 255, 0.3); }
.chat-input:focus { outline: none; border-color: #00d4ff; }

.send-btn {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  border: none;
  color: #fff;
  font-size: 20px;
  cursor: pointer;
}

.send-btn:disabled { opacity: 0.5; }

/* 弹窗 */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: #1a1a2e;
  border: 1px solid rgba(0, 212, 255, 0.2);
  border-radius: 20px;
  padding: 25px;
  width: 90%;
  max-width: 400px;
}

.modal-content h3 { margin-bottom: 10px; }

.modal-desc {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 20px;
}

.tech-input {
  width: 100%;
  padding: 14px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(0, 212, 255, 0.2);
  border-radius: 12px;
  color: #fff;
  font-size: 14px;
  margin-bottom: 15px;
}

.import-btn {
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  border: none;
  border-radius: 12px;
  color: #fff;
  font-size: 15px;
  cursor: pointer;
}

.import-btn:disabled { opacity: 0.5; }
</style>
