<template>
  <div class="ai-page">
    <!-- 导航栏 -->
    <Navbar />

    <!-- 顶部标题栏 -->
    <header class="page-header">
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
            
            <!-- 行程卡片 - 当消息包含行程数据时显示 -->
            <div v-if="msg.itinerary" class="itinerary-card" @click="viewItineraryDetail(msg.itinerary)">
              <div class="itinerary-header">
                <span class="itinerary-icon">🗺️</span>
                <div class="itinerary-title">
                  <h4>{{ msg.itinerary.title || msg.itinerary.destination + '之旅' }}</h4>
                  <span class="itinerary-meta">{{ msg.itinerary.destination }} · {{ msg.itinerary.days }}天</span>
                </div>
              </div>
              <div class="itinerary-spots" v-if="msg.itinerary.spots && msg.itinerary.spots.length > 0">
                <span class="spot-tag" v-for="(spot, idx) in msg.itinerary.spots.slice(0, 4)" :key="idx">
                  {{ spot }}
                </span>
                <span v-if="msg.itinerary.spots.length > 4" class="more-spots">+{{ msg.itinerary.spots.length - 4 }}</span>
              </div>
              <div class="itinerary-footer">
                <span class="click-hint">👆 点击查看详情并保存</span>
              </div>
            </div>
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
      <button class="action-btn session-trip-btn" @click="showSessionItineraryPreview" :class="{ 'has-content': sessionItinerary }">
        <span>🗺️</span> 会话内的行程
        <span v-if="sessionItinerary" class="trip-badge">●</span>
      </button>
      <button class="action-btn" @click="showHistoryModal = true">
        <span>📜</span> 对话历史
      </button>
      <button class="action-btn new-chat-btn" @click="startNewChat">
        <span>✨</span> 新对话
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
      <div class="modal-content import-modal">
        <h3>📥 导入小红书行程</h3>
        <p class="modal-desc">粘贴小红书笔记内容，AI自动提取行程信息</p>
        
        <textarea 
          class="tech-textarea content-input" 
          placeholder="请复制小红书笔记的标题和正文内容，粘贴到这里..."
          v-model="importContent"
          rows="8"
        ></textarea>
        <p class="input-tip">💡 复制笔记时建议包含：标题、行程安排、景点名称、美食推荐等信息</p>
        
        <button class="import-btn" @click="importFromXiaohongshu" :disabled="isImportDisabled">
          {{ isTyping ? 'AI解析中...' : '开始导入' }}
        </button>
      </div>
    </div>

    <!-- 会话内的行程弹窗 -->
    <div v-if="showSessionItineraryModal" class="modal-overlay" @click.self="showSessionItineraryModal = false">
      <div class="modal-content itinerary-modal">
        <div class="modal-header">
          <h3>🗺️ 会话内的行程</h3>
          <button class="close-btn" @click="showSessionItineraryModal = false">×</button>
        </div>
        
        <div v-if="!sessionItinerary" class="empty-itinerary">
          <div class="empty-icon">📝</div>
          <p>还没有行程哦~</p>
          <p class="empty-tip">和AI对话规划行程，内容会自动同步到这里</p>
        </div>
        
        <div v-else class="itinerary-detail">
          <div class="itinerary-header-info">
            <h4>{{ sessionItinerary.title || sessionItinerary.destination + '之旅' }}</h4>
            <p class="itinerary-meta-info">{{ sessionItinerary.destination }} · {{ sessionItinerary.days }}天</p>
          </div>
          
          <div class="itinerary-spots-list" v-if="sessionItinerary.spots && sessionItinerary.spots.length > 0">
            <h5>📍 景点安排</h5>
            <div class="spots-cards">
              <div class="spot-card-item" v-for="(spot, idx) in sessionItinerary.spots.filter(s => spotDetailsMap[s])" :key="idx">
                <div class="spot-order">{{ idx + 1 }}</div>
                <div class="spot-image">
                  <img :src="spotDetailsMap[spot]?.image || '/images/default-spot.jpg'" :alt="spot" />
                </div>
                <div class="spot-info">
                  <h4 class="spot-name">{{ spotDetailsMap[spot]?.name || spot }}</h4>
                  <div class="spot-meta">
                    <span class="spot-rating">⭐ {{ spotDetailsMap[spot]?.rating || 4.5 }}</span>
                    <span class="spot-duration">⏱️ {{ spotDetailsMap[spot]?.duration || '2小时' }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div class="itinerary-food" v-if="sessionItinerary.food && sessionItinerary.food.length > 0">
            <h5>🍜 美食推荐</h5>
            <p>{{ sessionItinerary.food.join('、') }}</p>
          </div>
          
          <div class="itinerary-actions">
            <button class="save-trip-btn" @click="goToSessionItinerary">
              查看行程详情
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 对话历史弹窗 -->
    <div v-if="showHistoryModal" class="modal-overlay" @click.self="showHistoryModal = false">
      <div class="modal-content history-modal">
        <div class="modal-header">
          <h3>📜 对话历史</h3>
          <button class="close-btn" @click="showHistoryModal = false">×</button>
        </div>
        
        <div v-if="chatHistoryList.length === 0" class="empty-history">
          <div class="empty-icon">📭</div>
          <p>还没有历史对话</p>
          <p class="empty-tip">点击"新对话"按钮开始新的对话，之前的对话会自动保存到这里</p>
        </div>
        
        <div v-else class="history-list">
          <div 
            v-for="item in chatHistoryList" 
            :key="item.id" 
            class="history-item"
            @click="loadHistoryChat(item)"
          >
            <div class="history-info">
              <h4 class="history-title">{{ item.title }}</h4>
              <p class="history-date">{{ item.date }}</p>
              <p class="history-preview" v-if="item.sessionItinerary">
                🗺️ {{ item.sessionItinerary.destination }} · {{ item.sessionItinerary.days }}天
              </p>
            </div>
            <button class="delete-history-btn" @click="deleteHistoryItem(item.id, $event)">🗑️</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 新对话确认弹窗 -->
    <div v-if="showNewChatConfirm" class="modal-overlay" @click.self="showNewChatConfirm = false">
      <div class="modal-content confirm-modal">
        <div class="confirm-icon">✨</div>
        <h3>开启新对话</h3>
        <p class="confirm-desc">
          开启新对话后，当前对话将被保存到历史记录中。<br>
          会话内的行程也会被清空。
        </p>
        <div class="confirm-buttons">
          <button class="cancel-btn" @click="showNewChatConfirm = false">取消</button>
          <button class="confirm-btn" @click="confirmNewChat">确认开启</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { marked } from 'marked'
import Navbar from '../components/Navbar.vue'

const router = useRouter()

const messages = ref([])
const userInput = ref('')
const isTyping = ref(false)
const showImportModal = ref(false)
const showFoodModal = ref(false)
const showSessionItineraryModal = ref(false)  // 会话内行程弹窗
const showHistoryModal = ref(false)  // 对话历史弹窗
const showNewChatConfirm = ref(false)  // 新对话确认弹窗
const importContent = ref('')  // 用户粘贴的笔记内容
const chatSection = ref(null)
const conversationHistory = ref([])  // 对话历史，用于上下文记忆
const sessionItinerary = ref(null)  // 会话内的行程
const chatHistoryList = ref([])  // 历史对话列表
const spotImagesMap = ref({})  // 景点图片映射

// 计算属性：判断导入按钮是否禁用
const isImportDisabled = computed(() => {
  if (isTyping.value) return true
  return !importContent.value.trim() || importContent.value.trim().length < 10
})

// 页面加载时恢复对话历史
onMounted(() => {
  const savedMessages = localStorage.getItem('aiChatMessages')
  const savedHistory = localStorage.getItem('aiConversationHistory')
  const savedItinerary = localStorage.getItem('aiSessionItinerary')
  const savedChatHistoryList = localStorage.getItem('aiChatHistoryList')

  if (savedMessages) {
    try {
      messages.value = JSON.parse(savedMessages)
    } catch (e) {
      console.error('恢复对话历史失败:', e)
    }
  }

  if (savedHistory) {
    try {
      conversationHistory.value = JSON.parse(savedHistory)
    } catch (e) {
      console.error('恢复对话历史失败:', e)
    }
  }

  if (savedItinerary) {
    try {
      sessionItinerary.value = JSON.parse(savedItinerary)
    } catch (e) {
      console.error('恢复行程数据失败:', e)
    }
  }

  if (savedChatHistoryList) {
    try {
      chatHistoryList.value = JSON.parse(savedChatHistoryList)
    } catch (e) {
      console.error('恢复历史对话列表失败:', e)
    }
  }
})

// 保存对话历史到 localStorage
const saveChatHistory = () => {
  localStorage.setItem('aiChatMessages', JSON.stringify(messages.value))
  localStorage.setItem('aiConversationHistory', JSON.stringify(conversationHistory.value))
  if (sessionItinerary.value) {
    localStorage.setItem('aiSessionItinerary', JSON.stringify(sessionItinerary.value))
  }
}

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

  // 添加到对话历史
  conversationHistory.value.push({ role: 'user', content: question })
  // 只保留最近10轮对话
  if (conversationHistory.value.length > 20) {
    conversationHistory.value = conversationHistory.value.slice(-20)
  }

  await nextTick()
  scrollToBottom()

  try {
    // 调用后端AI API - 使用POST body，带上对话历史
    const response = await fetch('http://localhost:8000/api/ai/travel-chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: question,
        history: conversationHistory.value.slice(0, -1) // 不包含当前消息
      })
    })

    const data = await response.json()

    if (data.reply) {
      // 再次调用AI API，让AI提取行程信息
      const itinerary = await extractItineraryWithAI(data.reply, question)

      // 添加到消息列表
      const msg = {
        role: 'assistant',
        content: data.reply,
        itinerary: itinerary  // 附加行程数据，如果有的话
      }
      messages.value.push(msg)
      // 添加到对话历史
      conversationHistory.value.push({ role: 'assistant', content: data.reply })

      // 保存对话历史
      saveChatHistory()
    } else if (data.detail) {
      messages.value.push({ role: 'assistant', content: '抱歉，我现在有点累，让我休息一下再回答你。' })
      conversationHistory.value.push({ role: 'assistant', content: '抱歉，我现在有点累，让我休息一下再回答你。' })
      saveChatHistory()
    } else {
      messages.value.push({ role: 'assistant', content: '收到你的消息了！让我想想怎么回答你...' })
      conversationHistory.value.push({ role: 'assistant', content: '收到你的消息了！让我想想怎么回答你...' })
      saveChatHistory()
    }
  } catch (error) {
    console.error('AI API Error:', error)
    // 如果API调用失败，使用本地响应
    const localReply = getLocalResponse(question)
    // 从本地响应中提取行程
    const itinerary = await extractItineraryWithAI(localReply, question)
    messages.value.push({
      role: 'assistant',
      content: localReply,
      itinerary: itinerary  // 附加行程数据，如果有的话
    })
    conversationHistory.value.push({ role: 'assistant', content: localReply })
  }

  isTyping.value = false
  await nextTick()
  scrollToBottom()
}

// 导入小红书行程
const importFromXiaohongshu = async () => {
  if (isImportDisabled.value) return

  const content = importContent.value.trim()

  const userMsg = { role: 'user', content: '📋 导入小红书笔记内容' }
  messages.value.push(userMsg)
  conversationHistory.value.push(userMsg)
  showImportModal.value = false
  isTyping.value = true
  
  await nextTick()
  scrollToBottom()
  
  try {
    // 调用后端API分析笔记内容
    const response = await fetch('http://localhost:8000/api/xiaohongshu/extract-itinerary', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content })
    })
    
    const data = await response.json()
    
    if (data.itinerary) {
      // 成功解析，同步到会话内的行程
      const itinerary = data.itinerary
      sessionItinerary.value = itinerary
      
      // 构建景点列表显示
      const spotsList = itinerary.spots && itinerary.spots.length > 0
        ? itinerary.spots.map((spot, idx) => `${idx + 1}. ${spot}`).join('\n')
        : '暂无具体景点'
      
      // 构建美食列表
      const foodList = itinerary.food && itinerary.food.length > 0
        ? itinerary.food.join('、')
        : '暂无推荐'
      
      const assistantMsg = {
        role: 'assistant',
        content: `✅ **解析成功！** 已从笔记内容提取行程信息：

📍 **${itinerary.title || '行程'}**
🗺️ 目的地：${itinerary.destination || '未知'}
📅 天数：${itinerary.days || '未知'}天

🏛️ **景点安排**：
${spotsList}

🍜 **美食推荐**：${foodList}

💡 行程已同步到上方的"会话内的行程"，点击即可查看详情并保存！`,
        itinerary: itinerary
      }
      messages.value.push(assistantMsg)
      conversationHistory.value.push({ role: 'assistant', content: assistantMsg.content })

      // 保存对话历史
      saveChatHistory()

      // 清空输入
      importContent.value = ''
    } else {
      // 显示调试信息
      const debugInfo = data.debug_info ? JSON.stringify(data.debug_info, null, 2) : '无调试信息'
      const errorMsg = {
        role: 'assistant',
        content: `❌ 解析失败

${data.error || '无法从内容中识别行程信息'}

💡 **建议**：
- 确保粘贴的内容包含具体的行程信息
- 包含城市名称、景点名称、天数等关键信息
- 内容越详细，识别效果越好

**调试信息**：
\`\`\`
${debugInfo}
\`\`\``
      }
      messages.value.push(errorMsg)
      conversationHistory.value.push({ role: 'assistant', content: errorMsg.content })

      // 保存对话历史
      saveChatHistory()
    }
  } catch (error) {
    console.error('Import Error:', error)
    const networkErrorMsg = {
      role: 'assistant',
      content: `❌ 导入失败

网络错误或服务器异常，请稍后重试。

如果问题持续存在，你可以直接和AI对话，描述你想去的城市和天数，让AI帮你规划行程。`
    }
    messages.value.push(networkErrorMsg)
    conversationHistory.value.push({ role: 'assistant', content: networkErrorMsg.content })

    // 保存对话历史
    saveChatHistory()
  }
  
  isTyping.value = false
  await nextTick()
  scrollToBottom()
}

// 根据解析结果创建行程
const createTripFromItinerary = async (itinerary) => {
  const userId = localStorage.getItem('userId') || 1

  try {
    // 使用小红书专用API直接创建行程
    const response = await fetch('http://localhost:8000/api/xiaohongshu/create-trip', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        url: importLink.value || 'manual',
        content: JSON.stringify(itinerary)
      })
    })

    const data = await response.json()

    if (data.trip_id) {
      messages.value.push({
        role: 'assistant',
        content: `🎉 行程创建成功！

我已经为你创建了「${itinerary.title || itinerary.destination}」行程，包含${itinerary.days || 3}天的安排。

📋 行程信息：
• 目的地：${itinerary.destination}
• 天数：${itinerary.days}天
${itinerary.spots && itinerary.spots.length > 0 ? `• 包含景点：${itinerary.spots.join('、')}` : ''}

正在跳转到行程预览页面...`
      })
      
      // 延迟后跳转到行程预览页面
      setTimeout(() => {
        router.push(`/trip/${data.trip_id}`)
      }, 1500)
    }
  } catch (error) {
    console.error('Create trip error:', error)
    // 如果API调用失败，使用备用方案
    messages.value.push({
      role: 'assistant',
      content: `❌ 创建行程失败，请稍后重试或手动创建行程。`
    })
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

// 使用AI从回答中提取行程信息
const extractItineraryWithAI = async (aiReply, originalQuestion) => {
  try {
    // 构建提取提示词 - 要求AI按照天数分配景点
    const extractPrompt = `请从以下旅行推荐内容中提取行程信息，并按照固定格式返回。

用户问题：${originalQuestion}

AI回答内容：
${aiReply}

请提取以下信息并以JSON格式返回，**重点是将景点按照AI回答中提到的天数进行分配**：
{
  "has_route": true/false,  // 是否有具体行程路线
  "destination": "城市名",  // 目的地城市
  "days": 数字,  // 行程天数
  "daySpots": {  // 按天数分配的景点，这是最重要的字段
    "1": ["第1天景点1", "第1天景点2", ...],
    "2": ["第2天景点1", "第2天景点2", ...],
    ...
  },
  "spots": ["景点1", "景点2", ...],  // 所有景点列表（可选，用于展示）
  "food": ["美食1", "美食2", ...],  // 美食推荐，最多4个
  "title": "行程标题"  // 如"北京3日游"
}

**重要说明**：
- 请仔细阅读AI回答，根据"Day 1"、"第一天"、"第1天"等标识，将景点分配到对应的天数
- 例如：如果AI回答"Day 1: 天安门、故宫"，则 daySpots["1"] = ["天安门", "故宫"]
- 如果AI回答"第二天：长城、颐和园"，则 daySpots["2"] = ["长城", "颐和园"]

如果回答中没有具体行程路线（只是闲聊、问候、或没有提到具体景点），请返回：
{
  "has_route": false
}

注意：
- 只返回JSON格式，不要返回其他文字
- 景点名称要简洁，不要包含时间、价格等额外信息
- 天数根据回答中的"Day X"、"第X天"、"第X日"等信息判断
- 目的地根据回答中的城市名判断`;

    const response = await fetch('http://localhost:8000/api/ai/travel-chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: extractPrompt,
        history: []
      })
    })

    const data = await response.json()

    if (data.reply) {
      // 从AI回复中解析JSON
      try {
        // 尝试提取JSON部分
        const jsonMatch = data.reply.match(/\{[\s\S]*\}/)
        if (jsonMatch) {
          const extracted = JSON.parse(jsonMatch[0])

          if (extracted.has_route === true) {
            // 有路线，创建行程（使用AI分配的daySpots）
            console.log('AI extracted:', extracted)
            const days = extracted.days || Object.keys(extracted.daySpots || {}).length || 3

            // 如果没有daySpots，但有spots，则平均分配
            let daySpots = extracted.daySpots || {}
            console.log('daySpots from AI:', daySpots)
            if (Object.keys(daySpots).length === 0 && extracted.spots && extracted.spots.length > 0) {
              const spots = extracted.spots
              const spotsPerDay = Math.ceil(spots.length / days)
              for (let i = 1; i <= days; i++) {
                const startIdx = (i - 1) * spotsPerDay
                const endIdx = Math.min(startIdx + spotsPerDay, spots.length)
                daySpots[i.toString()] = spots.slice(startIdx, endIdx)
              }
            }

            // 收集所有景点并拆分斜杠分隔的景点（如"豫园/城隍庙"）
            const allSpots = Object.values(daySpots).flat()
            
            // 拆分斜杠分隔的景点
            const splitSpots = []
            allSpots.forEach(spot => {
              if (spot.includes('/') || spot.includes('\\') || spot.includes('、')) {
                // 使用 / \ 、 作为分隔符拆分
                const parts = spot.split(/[/\\、]/).map(s => s.trim()).filter(s => s)
                splitSpots.push(...parts)
              } else {
                splitSpots.push(spot)
              }
            })
            
            // 同样拆分 daySpots 中的景点
            const splitDaySpots = {}
            Object.entries(daySpots).forEach(([day, spots]) => {
              const daySplitSpots = []
              spots.forEach(spot => {
                if (spot.includes('/') || spot.includes('\\') || spot.includes('、')) {
                  const parts = spot.split(/[/\\、]/).map(s => s.trim()).filter(s => s)
                  daySplitSpots.push(...parts)
                } else {
                  daySplitSpots.push(spot)
                }
              })
              splitDaySpots[day] = daySplitSpots
            })
            
            console.log('Final daySpots:', splitDaySpots)
            console.log('All spots:', splitSpots)

            const itinerary = {
              title: extracted.title || `${extracted.destination}${days}日游`,
              destination: extracted.destination,
              days: days,
              spots: splitSpots,
              daySpots: splitDaySpots,
              food: extracted.food || ['当地特色美食'],
              preferences: ['必玩景点']
            }

            sessionItinerary.value = itinerary
            return itinerary
          } else {
            // 没有路线，清空会话行程
            sessionItinerary.value = null
            return null
          }
        }
      } catch (parseError) {
        console.error('解析AI提取结果失败:', parseError)
        // 解析失败，尝试使用备用提取方法
        const fallbackItinerary = extractItineraryFromReply(aiReply, originalQuestion)
        if (fallbackItinerary) {
          sessionItinerary.value = fallbackItinerary
          return fallbackItinerary
        }
      }
    }
  } catch (error) {
    console.error('AI提取行程失败:', error)
    // 使用备用提取方法
    const fallbackItinerary = extractItineraryFromReply(aiReply, originalQuestion)
    if (fallbackItinerary) {
      sessionItinerary.value = fallbackItinerary
      return fallbackItinerary
    }
  }
  return null
}

// 备用：从AI回答中提取行程信息（正则提取）
const extractItineraryFromReply = (reply, question) => {
  // 常见城市列表
  const cities = ['北京', '上海', '广州', '深圳', '杭州', '西安', '成都', '重庆', '南京', '苏州',
                  '武汉', '长沙', '厦门', '青岛', '大连', '昆明', '丽江', '大理', '桂林', '三亚',
                  '黄山', '张家界', '西藏', '拉萨', '新疆', '哈尔滨', '长春', '沈阳']

  // 提取目的地
  let destination = null
  for (const city of cities) {
    if (reply.includes(city) || question.includes(city)) {
      destination = city
      break
    }
  }

  // 如果没有找到城市，返回null
  if (!destination) return null

  // 提取天数
  let days = 3
  // 匹配 "X天"、"X日"、"Day X" 等格式
  const dayMatches = reply.match(/(\d+)\s*[天日]/g)
  if (dayMatches) {
    // 取最大的天数
    const dayNumbers = dayMatches.map(m => parseInt(m.match(/\d+/)[0]))
    days = Math.max(...dayNumbers)
  }
  // 匹配 "Day X" 格式
  const dayMatches2 = reply.match(/Day\s*(\d+)/gi)
  if (dayMatches2) {
    const dayNumbers = dayMatches2.map(m => parseInt(m.match(/\d+/)[0]))
    days = Math.max(days, ...dayNumbers)
  }
  days = Math.max(1, Math.min(days, 7)) // 限制1-7天

  // 提取景点（匹配常见景点名称模式）
  const spots = []
  // 匹配 "• 景点名" 或 "- 景点名" 或 "1. 景点名" 格式
  const spotPatterns = [
    /[•\-\*]\s*([^\n•\-\*]+)/g,
    /\d+\.\s*([^\n]+)/g,
    /[:：]\s*([^\n]+)/g
  ]

  for (const pattern of spotPatterns) {
    let match
    while ((match = pattern.exec(reply)) !== null) {
      const spot = match[1].trim()
      // 过滤掉太短或太长的文本
      if (spot.length > 2 && spot.length < 30 && !spots.includes(spot)) {
        // 过滤掉包含特定关键词的（如时间、价格等）
        if (!/[:：\d]{2,}/.test(spot) && !spot.includes('元') && !spot.includes('¥')) {
          spots.push(spot)
        }
      }
    }
  }

  // 提取美食（匹配 "美食" 后面的内容）
  const foodMatch = reply.match(/美食[：:]\s*([^\n]+)/)
  const food = foodMatch ? foodMatch[1].split(/[,，、]/).map(f => f.trim()).filter(f => f.length > 0) : []

  // 如果没有提取到景点，返回null
  if (spots.length === 0) return null

  return {
    title: `${destination}${days}日游`,
    destination: destination,
    days: days,
    spots: spots.slice(0, 12), // 最多12个景点
    food: food.length > 0 ? food : ['当地特色美食'],
    preferences: ['必玩景点'],
    rawReply: reply // 保存原始回复用于调试
  }
}

// 本地响应（备用）
const getLocalResponse = (question) => {
  const q = question.toLowerCase()
  
  if (q.includes('北京') || q.includes('行程') || q.includes('规划')) {
    // 设置会话内的行程
    sessionItinerary.value = {
      title: "北京3日游",
      destination: "北京",
      days: 3,
      spots: ["故宫博物院", "天安门广场", "景山公园", "颐和园", "圆明园", "八达岭长城", "南锣鼓巷", "什刹海"],
      food: ["北京烤鸭", "炸酱面", "豆汁儿"],
      preferences: ["必玩景点", "历史文化"]
    }
    
    return `好的！让我为你规划北京之旅 🏯

<b>推荐行程：</b>

📅 <b>Day 1 - 历史文化</b>
• 故宫博物院（必打卡！）
• 天安门广场
• 景山公园

📅 <b>Day 2 - 皇家园林</b>
• 颐和园（昆明湖+万寿山）
• 圆明园
• 北大/清华校园

📅 <b>Day 3 - 长城 & 市井</b>
• 八达岭长城
• 南锣鼓巷
• 什刹海

<b>小贴士：</b>
✓ 建议提前预约故宫门票
✓ 带好身份证
✓ 穿舒适的鞋子

💡 行程已同步到上方的"会话内的行程"，点击即可保存！`
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
  conversationHistory.value = []  // 同时清空对话历史
  sessionItinerary.value = null  // 清空会话内的行程
  // 清除 localStorage
  localStorage.removeItem('aiChatMessages')
  localStorage.removeItem('aiConversationHistory')
  localStorage.removeItem('aiSessionItinerary')
}

// 开始新对话 - 保存当前对话到历史，然后清空
const startNewChat = () => {
  showNewChatConfirm.value = true
}

// 确认开始新对话
const confirmNewChat = () => {
  // 如果当前有对话内容，保存到历史记录
  if (messages.value.length > 0) {
    const firstUserMessage = messages.value.find(m => m.role === 'user')
    const title = firstUserMessage 
      ? firstUserMessage.content.slice(0, 20) + (firstUserMessage.content.length > 20 ? '...' : '')
      : '新对话'
    
    const historyItem = {
      id: Date.now(),
      title: title,
      date: new Date().toLocaleString('zh-CN'),
      messages: [...messages.value],
      conversationHistory: [...conversationHistory.value],
      sessionItinerary: sessionItinerary.value ? {...sessionItinerary.value} : null
    }
    
    chatHistoryList.value.unshift(historyItem)
    // 只保留最近20条历史记录
    if (chatHistoryList.value.length > 20) {
      chatHistoryList.value = chatHistoryList.value.slice(0, 20)
    }
    localStorage.setItem('aiChatHistoryList', JSON.stringify(chatHistoryList.value))
  }
  
  // 清空当前对话
  messages.value = []
  conversationHistory.value = []
  sessionItinerary.value = null
  localStorage.removeItem('aiChatMessages')
  localStorage.removeItem('aiConversationHistory')
  localStorage.removeItem('aiSessionItinerary')
  
  showNewChatConfirm.value = false
}

// 加载历史对话
const loadHistoryChat = (historyItem) => {
  messages.value = [...historyItem.messages]
  conversationHistory.value = [...historyItem.conversationHistory]
  sessionItinerary.value = historyItem.sessionItinerary
  
  // 保存到当前会话
  saveChatHistory()
  
  showHistoryModal.value = false
  
  // 滚动到底部
  nextTick(() => {
    scrollToBottom()
  })
}

// 删除历史记录
const deleteHistoryItem = (id, event) => {
  event.stopPropagation()
  chatHistoryList.value = chatHistoryList.value.filter(item => item.id !== id)
  localStorage.setItem('aiChatHistoryList', JSON.stringify(chatHistoryList.value))
}

// 景点详细信息缓存
const spotDetailsMap = ref({})

// 景点别名映射表 - 与后端保持一致
const SPOT_ALIAS_MAP = {
  '国家博物院': '国家博物馆',
  '博物院': '博物馆',
  '鸟巢/水立方': '鸟巢',
  '水立方/鸟巢': '鸟巢',
  '王府井小吃街': '王府井',
  '故宫博物院': '故宫',
}

// 根据别名获取标准名称
const getStandardSpotName = (spotName) => {
  return SPOT_ALIAS_MAP[spotName] || spotName
}

// 加载景点详细信息 - 使用与 TripDetail.vue 相同的数据源
const loadSpotDetails = async (spots, destination) => {
  if (!spots || !destination) return
  
  console.log('Loading spot details for:', spots, 'in', destination)
  
  try {
    // 使用与 TripDetail.vue 相同的 API 获取该城市所有景点数据
    const response = await fetch(`http://localhost:8000/api/spots/recommend?city=${encodeURIComponent(destination)}&limit=100`)
    if (response.ok) {
      const data = await response.json()
      
      if (data.spots) {
        // 建立景点名称到数据的映射
        const spotsDataMap = {}
        data.spots.forEach(spot => {
          spotsDataMap[spot.name] = spot
          // 也使用 ID 作为 key，方便通过 ID 查找
          spotsDataMap[spot.id] = spot
        })
        
        // 为每个景点查找详细信息 - 只保留存在于该城市景点列表中的景点
        for (const spot of spots) {
          // 如果已经加载过，跳过
          if (spotDetailsMap.value[spot]) {
            console.log('Details already cached for:', spot)
            continue
          }
          
          // 在数据中查找匹配的景点
          let spotData = spotsDataMap[spot]
          
          // 如果没有精确匹配，尝试别名映射
          if (!spotData) {
            const standardName = getStandardSpotName(spot)
            if (standardName !== spot) {
              spotData = spotsDataMap[standardName]
              console.log(`Alias mapping: ${spot} -> ${standardName}`, spotData ? 'found' : 'not found')
            }
          }
          
          // 如果没有精确匹配，尝试部分匹配
          if (!spotData) {
            for (const [name, data] of Object.entries(spotsDataMap)) {
              if (typeof name === 'string' && (name.includes(spot) || spot.includes(name))) {
                spotData = data
                break
              }
            }
          }
          
          // 只添加存在于该城市景点列表中的景点
          if (spotData) {
            console.log('Found spot data for', spot, ':', spotData)
            spotDetailsMap.value[spot] = {
              id: spotData.id,  // 添加 id 字段！
              name: spotData.name,
              image: spotData.images && spotData.images.length > 0 ? spotData.images[0] : '/images/default-spot.jpg',
              rating: spotData.rating || 0,
              duration: '2小时',
              tags: spotData.tags || [],
              location: spotData.location_lng && spotData.location_lat 
                ? [spotData.location_lng, spotData.location_lat] 
                : null
            }
          } else {
            console.log('Spot not found in city database, ignoring:', spot)
            // 不存在的景点不添加到 spotDetailsMap，即直接忽略
          }
        }
      }
    } else {
      console.error('API error:', response.status)
      // API 错误时不添加任何景点
    }
  } catch (error) {
    console.error('获取景点信息失败:', error)
    // 出错时不添加任何景点
  }
  
  console.log('Final spotDetailsMap:', spotDetailsMap.value)
}

// 显示会话内的行程预览弹窗
const showSessionItineraryPreview = async () => {
  if (!sessionItinerary.value) {
    alert('还没有行程哦，先和AI对话规划一个行程吧~')
    return
  }

  // 加载景点详细信息
  await loadSpotDetails(sessionItinerary.value.spots, sessionItinerary.value.destination)

  // 显示弹窗
  showSessionItineraryModal.value = true
}

// 点击会话内的行程按钮 - 只保存到localStorage，不保存到数据库
const goToSessionItinerary = async () => {
  if (!sessionItinerary.value) {
    // 如果没有行程数据，显示提示
    alert('还没有行程哦，先和AI对话规划一个行程吧~')
    return
  }

  try {
    console.log('sessionItinerary:', sessionItinerary.value)
    
    // 首先确保加载了景点详细信息（包含别名映射）
    await loadSpotDetails(sessionItinerary.value.spots, sessionItinerary.value.destination)
    
    // 过滤掉不在该城市景点列表中的景点
    const validSpots = sessionItinerary.value.spots.filter(spot => spotDetailsMap.value[spot])
    
    if (validSpots.length === 0) {
      alert('该城市暂无推荐的景点，请尝试其他城市')
      return
    }
    
    // 构建包含完整信息的 daySpots（包含图片、评分等）
    let enrichedDaySpots = {}
    
    // 如果有原始的 daySpots，使用它来构建
    if (sessionItinerary.value.daySpots && Object.keys(sessionItinerary.value.daySpots).length > 0) {
      Object.entries(sessionItinerary.value.daySpots).forEach(([day, spots]) => {
        const validDaySpots = spots.filter(spot => spotDetailsMap.value[spot])
        if (validDaySpots.length > 0) {
          // 将景点名称转换为包含完整信息的对象
          enrichedDaySpots[day] = validDaySpots.map(spotName => {
            const spotDetail = spotDetailsMap.value[spotName]
            return {
              id: spotDetail.id || spotName,
              name: spotDetail.name || spotName,
              image: spotDetail.image || '/images/default-spot.jpg',
              rating: spotDetail.rating || 4.5,
              duration: spotDetail.duration || '2小时',
              tags: spotDetail.tags || [],
              location: spotDetail.location || null
            }
          })
        }
      })
    }
    
    // 如果没有有效的 daySpots，重新创建
    if (Object.keys(enrichedDaySpots).length === 0) {
      // 按天数平均分配景点
      const days = sessionItinerary.value.days || 3
      const spotsPerDay = Math.ceil(validSpots.length / days)
      
      for (let i = 1; i <= days; i++) {
        const startIdx = (i - 1) * spotsPerDay
        const endIdx = Math.min(startIdx + spotsPerDay, validSpots.length)
        const daySpotNames = validSpots.slice(startIdx, endIdx)
        
        enrichedDaySpots[i] = daySpotNames.map(spotName => {
          const spotDetail = spotDetailsMap.value[spotName]
          return {
            id: spotDetail?.id || spotName,
            name: spotDetail?.name || spotName,
            image: spotDetail?.image || '/images/default-spot.jpg',
            rating: spotDetail?.rating || 4.5,
            duration: spotDetail?.duration || '2小时',
            tags: spotDetail?.tags || [],
            location: spotDetail?.location || null
          }
        })
      }
    }

    console.log('Enriched daySpots:', enrichedDaySpots)

    // 生成临时ID，只保存到localStorage，不保存到数据库
    const tempTripId = 'ai_temp_' + Date.now()
    const tripData = {
      id: tempTripId,
      title: sessionItinerary.value.title,
      city: sessionItinerary.value.destination || sessionItinerary.value.city,
      days: sessionItinerary.value.days,
      preferences: sessionItinerary.value.preferences || [],
      daySpots: enrichedDaySpots,  // 现在包含完整的景点信息
      totalSpots: validSpots.length,
      createTime: new Date().toISOString(),
      updateTime: new Date().toISOString(),
      isAITemp: true // 标记为AI临时行程
    }
    
    // 保存到localStorage作为当前行程
    localStorage.setItem('currentTrip', JSON.stringify(tripData))
    
    // 保存当前AI会话状态，以便返回时恢复
    saveChatHistory()
    
    // 跳转到行程预览页面（临时ID）
    router.push(`/trip/${tempTripId}?from=ai`)
    
  } catch (error) {
    console.error('预览行程失败:', error)
    alert('预览行程失败，请重试')
  }
}

// 创建按天数分配景点的行程数据（备用方案）
const createItineraryWithDaySpots = (itinerary) => {
  const days = itinerary.days || 3
  const spots = itinerary.spots || []
  const spotsPerDay = Math.ceil(spots.length / days)

  // 创建每天的景点分配
  const daySpots = {}
  for (let i = 1; i <= days; i++) {
    const startIdx = (i - 1) * spotsPerDay
    const endIdx = Math.min(startIdx + spotsPerDay, spots.length)
    daySpots[i] = spots.slice(startIdx, endIdx)
  }

  return {
    ...itinerary,
    daySpots: daySpots
  }
}

// 跳转
const startNewTrip = () => router.push('/create-trip')
const goBack = () => router.back()

// 查看行程详情 - 只保存到localStorage，不保存到数据库
const viewItineraryDetail = async (itinerary) => {
  try {
    // 首先确保加载了景点详细信息（包含别名映射）
    await loadSpotDetails(itinerary.spots, itinerary.destination)
    
    // 过滤掉不在该城市景点列表中的景点
    const validSpots = itinerary.spots.filter(spot => spotDetailsMap.value[spot])
    
    if (validSpots.length === 0) {
      alert('该城市暂无推荐的景点，请尝试其他城市')
      return
    }
    
    // 构建包含完整信息的 daySpots（包含图片、评分等）
    let enrichedDaySpots = {}
    
    // 如果有原始的 daySpots，使用它来构建
    if (itinerary.daySpots && Object.keys(itinerary.daySpots).length > 0) {
      Object.entries(itinerary.daySpots).forEach(([day, spots]) => {
        const validDaySpots = spots.filter(spot => spotDetailsMap.value[spot])
        if (validDaySpots.length > 0) {
          // 将景点名称转换为包含完整信息的对象
          enrichedDaySpots[day] = validDaySpots.map(spotName => {
            const spotDetail = spotDetailsMap.value[spotName]
            return {
              id: spotDetail.id || spotName,
              name: spotDetail.name || spotName,
              image: spotDetail.image || '/images/default-spot.jpg',
              rating: spotDetail.rating || 4.5,
              duration: spotDetail.duration || '2小时',
              tags: spotDetail.tags || [],
              location: spotDetail.location || null
            }
          })
        }
      })
    }
    
    // 如果没有有效的 daySpots，重新创建
    if (Object.keys(enrichedDaySpots).length === 0) {
      // 按天数平均分配景点
      const days = itinerary.days || 3
      const spotsPerDay = Math.ceil(validSpots.length / days)
      
      for (let i = 1; i <= days; i++) {
        const startIdx = (i - 1) * spotsPerDay
        const endIdx = Math.min(startIdx + spotsPerDay, validSpots.length)
        const daySpotNames = validSpots.slice(startIdx, endIdx)
        
        enrichedDaySpots[i] = daySpotNames.map(spotName => {
          const spotDetail = spotDetailsMap.value[spotName]
          return {
            id: spotDetail?.id || spotName,
            name: spotDetail?.name || spotName,
            image: spotDetail?.image || '/images/default-spot.jpg',
            rating: spotDetail?.rating || 4.5,
            duration: spotDetail?.duration || '2小时',
            tags: spotDetail?.tags || [],
            location: spotDetail?.location || null
          }
        })
      }
    }

    console.log('Preview itinerary from card - enriched:', enrichedDaySpots)

    // 生成临时ID，只保存到localStorage，不保存到数据库
    const tempTripId = 'ai_temp_' + Date.now()
    const tripData = {
      id: tempTripId,
      title: itinerary.title,
      city: itinerary.destination || itinerary.city,
      days: itinerary.days,
      preferences: itinerary.preferences || [],
      daySpots: enrichedDaySpots,  // 现在包含完整的景点信息
      totalSpots: validSpots.length,
      createTime: new Date().toISOString(),
      updateTime: new Date().toISOString(),
      isAITemp: true // 标记为AI临时行程
    }
    
    // 保存到localStorage作为当前行程
    localStorage.setItem('currentTrip', JSON.stringify(tripData))
    
    // 跳转到行程预览页面（临时ID）
    router.push(`/trip/${tempTripId}?from=ai`)
    
  } catch (error) {
    console.error('预览行程失败:', error)
    alert('预览行程失败，请重试')
  }
}
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

/* 导入弹窗样式 */
.import-modal {
  max-width: 480px;
}

.tech-textarea {
  width: 100%;
  padding: 14px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(0, 212, 255, 0.2);
  border-radius: 12px;
  color: #fff;
  font-size: 14px;
  resize: vertical;
  font-family: inherit;
  margin-bottom: 10px;
  line-height: 1.6;
}

.tech-textarea.content-input {
  min-height: 150px;
}

.tech-textarea::placeholder {
  color: rgba(255, 255, 255, 0.3);
}

.tech-textarea:focus {
  outline: none;
  border-color: #00d4ff;
}

.input-tip {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
  margin: 0 0 15px 0;
  line-height: 1.4;
}

/* 行程卡片样式 */
.itinerary-card {
  margin-top: 15px;
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.1), rgba(123, 44, 191, 0.1));
  border: 1px solid rgba(0, 212, 255, 0.3);
  border-radius: 16px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.itinerary-card:hover {
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.2), rgba(123, 44, 191, 0.2));
  border-color: #00d4ff;
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 212, 255, 0.2);
}

.itinerary-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.itinerary-icon {
  font-size: 32px;
}

.itinerary-title h4 {
  font-size: 16px;
  font-weight: 600;
  color: #fff;
  margin: 0 0 4px 0;
}

.itinerary-meta {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
}

.itinerary-spots {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}

.spot-tag {
  padding: 4px 10px;
  background: rgba(0, 212, 255, 0.15);
  border: 1px solid rgba(0, 212, 255, 0.3);
  border-radius: 12px;
  font-size: 12px;
  color: #00d4ff;
}

.more-spots {
  padding: 4px 10px;
  background: rgba(123, 44, 191, 0.15);
  border: 1px solid rgba(123, 44, 191, 0.3);
  border-radius: 12px;
  font-size: 12px;
  color: #7b2cbf;
}

.itinerary-footer {
  display: flex;
  justify-content: center;
  padding-top: 10px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.click-hint {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
}

/* 会话内的行程按钮样式 */
.session-trip-btn {
  position: relative;
}

.session-trip-btn.has-content {
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.3), rgba(123, 44, 191, 0.3));
  border-color: #00d4ff;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(0, 212, 255, 0.4); }
  50% { box-shadow: 0 0 0 10px rgba(0, 212, 255, 0); }
}

.trip-badge {
  position: absolute;
  top: -5px;
  right: -5px;
  color: #00d4ff;
  font-size: 10px;
}

/* 新对话按钮样式 */
.new-chat-btn {
  background: linear-gradient(135deg, rgba(255, 107, 107, 0.2), rgba(238, 90, 36, 0.2));
  border-color: rgba(255, 107, 107, 0.4);
}

.new-chat-btn:hover {
  background: linear-gradient(135deg, rgba(255, 107, 107, 0.3), rgba(238, 90, 36, 0.3));
  border-color: #ff6b6b;
}

/* 对话历史弹窗样式 */
.history-modal {
  max-width: 450px;
  max-height: 70vh;
  overflow-y: auto;
}

.empty-history {
  text-align: center;
  padding: 40px 20px;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.history-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 15px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.history-item:hover {
  background: rgba(0, 212, 255, 0.1);
  border-color: rgba(0, 212, 255, 0.3);
}

.history-info {
  flex: 1;
  min-width: 0;
}

.history-title {
  font-size: 15px;
  font-weight: 500;
  color: #fff;
  margin: 0 0 5px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.history-date {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  margin: 0 0 3px 0;
}

.history-preview {
  font-size: 12px;
  color: #00d4ff;
  margin: 0;
}

.delete-history-btn {
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.4);
  font-size: 16px;
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
  transition: all 0.3s;
}

.delete-history-btn:hover {
  background: rgba(255, 107, 107, 0.2);
  color: #ff6b6b;
}

/* 确认弹窗样式 */
.confirm-modal {
  max-width: 350px;
  text-align: center;
  padding: 30px;
}

.confirm-icon {
  font-size: 48px;
  margin-bottom: 15px;
}

.confirm-modal h3 {
  margin: 0 0 15px 0;
  font-size: 20px;
}

.confirm-desc {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
  line-height: 1.6;
  margin-bottom: 25px;
}

.confirm-buttons {
  display: flex;
  gap: 12px;
}

.confirm-buttons button {
  flex: 1;
  padding: 12px 20px;
  border-radius: 10px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.cancel-btn {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #fff;
}

.cancel-btn:hover {
  background: rgba(255, 255, 255, 0.15);
}

.confirm-btn {
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  border: none;
  color: #fff;
}

.confirm-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 212, 255, 0.4);
}

/* 行程弹窗样式 */
.itinerary-modal {
  max-width: 450px;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
}

.close-btn {
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.6);
  font-size: 24px;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  color: #fff;
}

.empty-itinerary {
  text-align: center;
  padding: 40px 20px;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 15px;
}

.empty-itinerary p {
  color: rgba(255, 255, 255, 0.8);
  margin: 5px 0;
}

.empty-tip {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
}

.itinerary-detail {
  padding: 10px 0;
}

.itinerary-header-info {
  text-align: center;
  margin-bottom: 25px;
  padding-bottom: 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.itinerary-header-info h4 {
  font-size: 20px;
  margin: 0 0 8px 0;
  color: #00d4ff;
}

.itinerary-meta-info {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
  margin: 0;
}

.itinerary-spots-list,
.itinerary-food {
  margin-bottom: 20px;
}

.itinerary-spots-list h5,
.itinerary-food h5 {
  font-size: 14px;
  margin: 0 0 10px 0;
  color: rgba(255, 255, 255, 0.8);
}

.spots-cards {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.spot-card-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  transition: all 0.3s ease;
}

.spot-card-item:hover {
  background: rgba(0, 212, 255, 0.1);
  border-color: rgba(0, 212, 255, 0.3);
}

.spot-order {
  width: 28px;
  height: 28px;
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 600;
  color: #fff;
  flex-shrink: 0;
}

.spot-image {
  width: 60px;
  height: 60px;
  border-radius: 10px;
  overflow: hidden;
  flex-shrink: 0;
}

.spot-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.spot-info {
  flex: 1;
  min-width: 0;
}

.spot-name {
  font-size: 15px;
  font-weight: 500;
  color: #fff;
  margin: 0 0 6px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.spot-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
}

.spot-rating {
  color: #ffd700;
}

.spot-duration {
  color: rgba(255, 255, 255, 0.5);
}

.itinerary-food p {
  color: rgba(255, 255, 255, 0.7);
  margin: 0;
  line-height: 1.6;
}

.save-trip-btn {
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  border: none;
  border-radius: 12px;
  color: #fff;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  margin-top: 20px;
  transition: all 0.3s ease;
}

.save-trip-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 212, 255, 0.4);
}
</style>
