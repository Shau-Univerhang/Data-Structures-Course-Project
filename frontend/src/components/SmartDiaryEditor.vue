<template>
  <div class="smart-editor">
    <!-- 顶部工具栏 -->
    <div class="editor-toolbar">
      <div class="toolbar-group">
        <span class="group-label">智能排版</span>
        <button class="tool-btn primary" @click="autoFormat" title="一键美化">
          <span class="btn-icon">✨</span>
          <span class="btn-text">一键排版</span>
        </button>
        <button class="tool-btn ai-btn" @click="openAIPanel" title="AI润色">
          <span class="btn-icon">🤖</span>
          <span class="btn-text">AI润色</span>
        </button>
      </div>
      
      <div class="toolbar-divider"></div>
      
      <div class="toolbar-group">
        <span class="group-label">快速插入</span>
        <button class="tool-btn" @click="insertWeather" title="插入天气">
          <span class="btn-icon">🌤️</span>
          <span class="btn-text">天气</span>
        </button>
        <button class="tool-btn" @click="insertLocation" title="插入地点">
          <span class="btn-icon">📍</span>
          <span class="btn-text">地点</span>
        </button>
        <button class="tool-btn" @click="insertStats" title="插入统计">
          <span class="btn-icon">📊</span>
          <span class="btn-text">数据</span>
        </button>
        <button class="tool-btn" @click="insertMood" title="插入心情">
          <span class="btn-icon">😊</span>
          <span class="btn-text">心情</span>
        </button>
        <button class="tool-btn" @click="insertFood" title="插入美食">
          <span class="btn-icon">🍜</span>
          <span class="btn-text">美食</span>
        </button>
        <button class="tool-btn" @click="insertTransport" title="插入交通">
          <span class="btn-icon">🚗</span>
          <span class="btn-text">交通</span>
        </button>
        <button class="tool-btn" @click="insertHotel" title="插入住宿">
          <span class="btn-icon">🏨</span>
          <span class="btn-text">住宿</span>
        </button>
        <button class="tool-btn" @click="insertCost" title="插入花费">
          <span class="btn-icon">💰</span>
          <span class="btn-text">花费</span>
        </button>
      </div>
      
      <div class="toolbar-divider"></div>
      
      <div class="toolbar-group">
        <span class="group-label">模板</span>
        <button class="tool-btn" @click="applyTemplate('travel')" title="行程模板">
          <span class="btn-icon">🏃</span>
          <span class="btn-text">行程</span>
        </button>
        <button class="tool-btn" @click="applyTemplate('food')" title="美食模板">
          <span class="btn-icon">🍜</span>
          <span class="btn-text">美食</span>
        </button>
        <button class="tool-btn" @click="applyTemplate('photo')" title="摄影模板">
          <span class="btn-icon">📸</span>
          <span class="btn-text">摄影</span>
        </button>
      </div>
    </div>
    
    <!-- 编辑区域 -->
    <div class="editor-container">
      <div class="editor-wrapper">
        <div class="editor-header">
          <input 
            type="text" 
            v-model="title" 
            class="title-input" 
            placeholder="给日记起个标题..."
          />
        </div>
        
        <textarea 
          ref="editorRef"
          v-model="content" 
          class="content-editor"
          placeholder="开始记录你的旅行故事...

💡 小贴士：
• 点击'一键排版'让日记自动变美
• 使用模板快速开始
• 插入天气、地点让日记更完整"
          @keydown="handleKeydown"
        ></textarea>
        
        <!-- 字数统计 -->
        <div class="editor-footer">
          <span class="word-count">{{ content.length }} 字</span>
          <span class="last-saved" v-if="lastSaved">已保存 {{ formatTime(lastSaved) }}</span>
        </div>
      </div>
      
      <!-- 实时预览 -->
      <div class="preview-wrapper">
        <div class="preview-header">
          <span class="preview-title">👁️ 预览效果</span>
          <button class="preview-toggle" @click="showPreview = !showPreview">
            {{ showPreview ? '隐藏' : '显示' }}
          </button>
        </div>
        <div v-show="showPreview" class="preview-content" v-html="renderedContent"></div>
      </div>
    </div>
    
    <!-- 底部操作栏 -->
    <div class="editor-actions">
      <button class="action-btn secondary" @click="emit('cancel')">取消</button>
      <button class="action-btn secondary" @click="saveDraft">保存草稿</button>
      <button class="action-btn primary" @click="publish" :disabled="!canPublish">
        发布日记
      </button>
    </div>
    
    <!-- ========== AI 生成侧边面板 ========== -->
    <div v-if="showAIPanel" class="ai-panel-overlay" @click.self="closeAIPanel">
      <div class="ai-panel" :class="{ 'panel-open': showAIPanel }">
        <!-- 面板头部 -->
        <div class="ai-panel-header">
          <div class="ai-title">
            <span class="ai-icon">🤖</span>
            <span>AI 智能助手</span>
          </div>
          <button class="close-btn" @click="closeAIPanel">×</button>
        </div>
        
        <!-- 输入区域 -->
        <div class="ai-input-section">
          <label class="input-label">
            <span class="label-icon">💡</span>
            输入你的灵感或关键词
          </label>
          <textarea 
            v-model="aiInput"
            class="ai-input"
            placeholder="例如：今天在上海吃到了一家超赞的本帮菜，红烧肉肥而不腻..."
            rows="4"
          ></textarea>
          
          <!-- 快捷提示词 -->
          <div class="quick-prompts">
            <span class="prompt-label">快捷输入：</span>
            <button 
              v-for="prompt in quickPrompts" 
              :key="prompt"
              class="prompt-chip"
              @click="aiInput = prompt"
            >
              {{ prompt.length > 15 ? prompt.slice(0, 15) + '...' : prompt }}
            </button>
          </div>
        </div>
        
        <!-- 风格选择 -->
        <div class="ai-style-section">
          <label class="input-label">选择写作风格</label>
          <div class="style-options">
            <button 
              v-for="style in writingStyles" 
              :key="style.key"
              class="style-chip"
              :class="{ active: selectedStyle === style.key }"
              @click="selectedStyle = style.key"
            >
              <span class="style-emoji">{{ style.emoji }}</span>
              <span class="style-name">{{ style.name }}</span>
            </button>
          </div>
        </div>
        
        <!-- 生成按钮 -->
        <button 
          class="generate-btn"
          :disabled="!aiInput.trim() || aiGenerating"
          @click="generateWithAI"
        >
          <span v-if="!aiGenerating" class="btn-content">
            <span class="btn-icon">✨</span>
            <span>生成日记内容</span>
          </span>
          <span v-else class="btn-content">
            <span class="loading-spinner"></span>
            <span>AI 创作中...</span>
          </span>
        </button>
        
        <!-- 生成结果 -->
        <div v-if="aiGeneratedContent" class="ai-result-section">
          <div class="result-header">
            <span class="result-title">🎉 AI 生成结果</span>
            <div class="result-actions">
              <button class="action-icon-btn" @click="regenerate" title="重新生成">
                🔄
              </button>
              <button class="action-icon-btn" @click="copyResult" title="复制">
                📋
              </button>
            </div>
          </div>
          
          <div class="result-content">
            <div class="content-preview">{{ aiGeneratedContent }}</div>
          </div>
          
          <!-- 使用按钮 -->
          <div class="result-footer">
            <button class="use-btn" @click="useGeneratedContent">
              <span>✅ 使用这段内容</span>
            </button>
          </div>
        </div>
        
        <!-- 空状态提示 -->
        <div v-else-if="!aiGenerating" class="ai-empty-state">
          <div class="empty-icon">✨</div>
          <p class="empty-title">AI 帮你写日记</p>
          <p class="empty-desc">输入关键词，选择风格，一键生成精美日记</p>
        </div>
      </div>
    </div>
    
    <!-- 心情选择弹窗 -->
    <div v-if="showMoodPicker" class="mood-picker-modal" @click.self="showMoodPicker = false">
      <div class="mood-picker-content">
        <h3>选择今天的心情</h3>
        <div class="mood-grid">
          <button 
            v-for="mood in moods" 
            :key="mood.emoji"
            class="mood-item"
            @click="insertMoodText(mood)"
          >
            <span class="mood-emoji">{{ mood.emoji }}</span>
            <span class="mood-label">{{ mood.label }}</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  initialTitle: { type: String, default: '' },
  initialContent: { type: String, default: '' },
  initialType: { type: String, default: 'travel' }
})

const emit = defineEmits(['save', 'publish', 'cancel'])

// 编辑器状态
const title = ref(props.initialTitle)
const content = ref(props.initialContent)
const editorRef = ref(null)
const lastSaved = ref(null)
const showPreview = ref(true)
const showMoodPicker = ref(false)

// AI面板状态
const showAIPanel = ref(false)
const aiInput = ref('')
const aiGenerating = ref(false)
const aiGeneratedContent = ref('')
const selectedStyle = ref('healing')

// 快捷提示词
const quickPrompts = [
  '今天去了故宫，人很多但景色很美',
  '发现一家藏在巷子里的火锅店',
  '在西湖边散步，看到了很美的日落',
  '第一次尝试跳伞，太刺激了'
]

// 写作风格
const writingStyles = [
  { key: 'healing', name: '治愈系', emoji: '🌸' },
  { key: 'humorous', name: '幽默风', emoji: '😄' },
  { key: 'documentary', name: '纪实风', emoji: '📰' },
  { key: 'poetic', name: '诗意风', emoji: '🌙' },
  { key: 'concise', name: '简洁风', emoji: '✨' }
]

// 心情选项
const moods = [
  { emoji: '😄', label: '开心', text: '今天心情超级棒！' },
  { emoji: '😋', label: '满足', text: '吃得满足，玩得尽兴！' },
  { emoji: '😲', label: '震撼', text: '被眼前的景色深深震撼了！' },
  { emoji: '🥰', label: '幸福', text: '幸福感爆棚的一天！' },
  { emoji: '😫', label: '疲惫', text: '虽然很累，但很值得！' },
  { emoji: '😢', label: '感动', text: '被这份美好感动到了...' },
  { emoji: '🤩', label: '兴奋', text: '太兴奋了，简直不敢相信！' },
  { emoji: '😌', label: '平静', text: '内心无比平静祥和。' }
]

// 模板定义
const templates = {
  travel: `【今日行程】
━━━━━━━━━━━━━━━━━━
📍 目的地：
⏰ 出发时间：
👥 同行伙伴：
🌤️ 天气情况：

【路线规划】
起点 → 途经点 → 终点
📏 总距离：约 __ 公里
⏱️ 总时长：约 __ 小时

【行程亮点】
1. 
2. 
3. 

【实用贴士】
• 交通：
• 门票：
• 注意事项：

【今日花费】
💰 交通：¥
💰 餐饮：¥
💰 门票：¥
💰 其他：¥
━━━━━━━━━━━━━━━━━━`,

  food: `【美食探店】
━━━━━━━━━━━━━━━━━━
🍽️ 店名：
📍 地址：
⏰ 营业时间：
💰 人均消费：¥

【必点菜品】
1. ⭐⭐⭐⭐⭐ 
   评价：
   
2. ⭐⭐⭐⭐⭐ 
   评价：
   
3. ⭐⭐⭐⭐⭐ 
   评价：

【环境服务】
• 环境：
• 服务：
• 等位时长：

【探店心得】

【推荐指数】
⭐⭐⭐⭐⭐
━━━━━━━━━━━━━━━━━━`,

  photo: `【摄影记录】
━━━━━━━━━━━━━━━━━━
📍 拍摄地点：
📅 拍摄时间：
🌤️ 天气状况：

【器材参数】
📷 相机：
🔭 镜头：
⚙️ 参数：光圈__ 快门__ ISO__

【拍摄心得】
• 最佳机位：
• 拍摄技巧：
• 后期思路：

【作品展示】
[插入照片]

【拍摄建议】
━━━━━━━━━━━━━━━━━━`
}

// 计算属性
const canPublish = computed(() => {
  return title.value.trim() && content.value.trim().length > 10
})

// 渲染预览内容
const renderedContent = computed(() => {
  return renderMarkdown(content.value)
})

// ========== AI 面板功能 ==========

// 打开AI面板
const openAIPanel = () => {
  showAIPanel.value = true
  aiInput.value = content.value.slice(0, 200) // 预填充当前内容的前200字
}

// 关闭AI面板
const closeAIPanel = () => {
  showAIPanel.value = false
  // 清空状态
  aiInput.value = ''
  aiGeneratedContent.value = ''
  aiGenerating.value = false
}

// AI生成内容
const generateWithAI = async () => {
  if (!aiInput.value.trim()) {
    ElMessage.warning('请输入一些关键词或灵感')
    return
  }
  
  aiGenerating.value = true
  aiGeneratedContent.value = ''
  
  try {
    // 模拟API调用（实际使用时替换为真实API）
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // 模拟生成结果
    const styleMap = {
      healing: '温柔治愈',
      humorous: '轻松幽默',
      documentary: '客观纪实',
      poetic: '诗意优美',
      concise: '简洁明了'
    }
    
    aiGeneratedContent.value = generateMockContent(aiInput.value, styleMap[selectedStyle.value])
    
    ElMessage.success('AI生成完成！')
  } catch (error) {
    ElMessage.error('生成失败，请重试')
  } finally {
    aiGenerating.value = false
  }
}

// 模拟生成内容
const generateMockContent = (input, style) => {
  const contents = {
    healing: `${input}...

🌸 今天的旅程，像是一首温柔的诗。

阳光正好，微风不燥。走在陌生的街道上，心里却异常平静。那些平日里烦扰心头的琐事，在这一刻都烟消云散了。

或许，这就是旅行的意义吧。不是为了逃离，而是为了更好地回来。

愿每一个在路上的人，都能找到属于自己的那份宁静。✨`,

    humorous: `${input}...

😄 今天这趟出行，简直是一部喜剧片！

先说这个导航，明明说左转，结果转进去是个死胡同。我都怀疑它是不是在跟我开玩笑。

然后排队的时候，前面的大哥一直在跟店员砍价，我在后面数了数，整整砍了15分钟！最后便宜了5块钱...大哥，您的时薪这么低的吗？

不过说真的，虽然一路波折，但回想起来还挺有意思的。毕竟，没有这些意外，怎么叫旅行呢？

下次出门，我决定带个指南针。📱`,

    documentary: `${input}...

📍 时间：${new Date().toLocaleDateString()}
📍 地点：待补充
📍 天气：晴，22°C

今日行程按计划进行。上午9时出发，途经主要景点3处，总步行距离约8公里。

主要观察：
• 人流量较平日增加约40%
• 景点设施维护良好
• 餐饮价格处于正常区间

建议：
• 避开上午10-11时高峰时段
• 提前预订可节省等候时间
• 携带便携充电宝`,

    poetic: `${input}...

🌙 暮色四合，华灯初上。

这座城市的夜，像是一幅泼墨山水画。霓虹是点睛的朱砂，车流是流动的墨色。

我站在桥头，看万家灯火次第亮起。每一盏灯下，都有一个故事正在发生。

风从江面吹来，带着水汽和远方的气息。这一刻，忽然明白了古人为何总爱登高望远——

原来，站得高一些，不是为了看得更远，而是为了把心放得更宽。

今夜，愿好梦。🌙`,

    concise: `${input}...

✨ 今日要点：

📍 地点：待补充
⏱️ 时长：约X小时
💰 花费：约X元

✅ 完成事项：
• 
• 
• 

⭐ 评分：X/10

💡 下次改进：
• 
• `}
  
  return contents[selectedStyle.value] || contents.healing
}

// 重新生成
const regenerate = () => {
  generateWithAI()
}

// 复制结果
const copyResult = () => {
  navigator.clipboard.writeText(aiGeneratedContent.value)
  ElMessage.success('已复制到剪贴板')
}

// 使用生成的内容
const useGeneratedContent = () => {
  content.value = aiGeneratedContent.value
  closeAIPanel()
  ElMessage.success('已应用到编辑器')
}

// ========== 一键排版功能 ==========
const autoFormat = () => {
  let text = content.value
  if (!text.trim()) {
    ElMessage.warning('先写点什么再排版吧~')
    return
  }

  // 1. 智能分段（每2-4句一段）
  text = smartParagraph(text)
  
  // 2. 添加时间emoji
  text = addTimeEmoji(text)
  
  // 3. 添加地点标记
  text = addLocationMarker(text)
  
  // 4. 添加情绪emoji
  text = addEmotionEmoji(text)
  
  // 5. 格式化标题和分隔线
  text = formatHeaders(text)
  
  // 6. 美化列表
  text = beautifyLists(text)

  content.value = text
  ElMessage.success('✨ 排版完成！日记变美了~')
}

// 智能分段
const smartParagraph = (text) => {
  const sentences = text.split(/([。！？；\.\!\?\;]+)/)
  let result = []
  let currentPara = []
  
  for (let i = 0; i < sentences.length; i += 2) {
    const sentence = sentences[i] + (sentences[i + 1] || '')
    if (sentence.trim()) {
      currentPara.push(sentence.trim())
      if (currentPara.length >= 2 && (currentPara.length >= 4 || Math.random() > 0.5)) {
        result.push(currentPara.join(''))
        currentPara = []
      }
    }
  }
  
  if (currentPara.length > 0) {
    result.push(currentPara.join(''))
  }
  
  return result.join('\n\n')
}

// 添加时间emoji
const addTimeEmoji = (text) => {
  const timeMap = {
    '早上': '🌅 早上',
    '上午': '☀️ 上午',
    '中午': '🌤️ 中午',
    '下午': '☀️ 下午',
    '傍晚': '🌆 傍晚',
    '晚上': '🌙 晚上',
    '深夜': '🌃 深夜',
    '凌晨': '🌌 凌晨'
  }
  
  Object.entries(timeMap).forEach(([key, value]) => {
    text = text.replace(new RegExp(`^${key}|\\n${key}`, 'g'), (match) => {
      return match.startsWith('\n') ? `\n${value}` : value
    })
  })
  
  return text
}

// 添加地点标记
const addLocationMarker = (text) => {
  const locationPatterns = [
    /([^，。！？\n]{2,10})(公园|景区|景点|博物馆|美术馆|餐厅|酒店|机场|车站|广场|大街|路|街|巷|胡同)/g
  ]
  
  locationPatterns.forEach(pattern => {
    text = text.replace(pattern, '📍$1$2')
  })
  
  return text
}

// 添加情绪emoji
const addEmotionEmoji = (text) => {
  const emotionMap = {
    '好吃': '😋好吃',
    '美味': '🤤美味',
    '推荐': '👍推荐',
    '不错': '👍不错',
    '棒': '👍棒',
    '累': '😫累',
    '疲惫': '😮‍💨疲惫',
    '走': '🚶走',
    '逛': '🚶逛',
    '拍照': '📸拍照',
    '照片': '🖼️照片',
    '风景': '🏞️风景',
    '景色': '✨景色',
    '美': '😍美',
    '漂亮': '✨漂亮',
    '震撼': '😲震撼',
    '壮观': '✨壮观',
    '开心': '😄开心',
    '高兴': '🥳高兴',
    '喜欢': '❤️喜欢',
    '爱': '❤️爱',
    '感动': '🥺感动',
    '幸福': '🥰幸福',
    '兴奋': '🤩兴奋',
    '惊讶': '😲惊讶',
    '舒服': '😌舒服',
    '惬意': '😌惬意'
  }
  
  Object.entries(emotionMap).forEach(([word, emojiWord]) => {
    if (!text.includes(emojiWord)) {
      text = text.replace(new RegExp(word, 'g'), emojiWord)
    }
  })
  
  return text
}

// 格式化标题
const formatHeaders = (text) => {
  const headerPatterns = [
    { pattern: /^(【.+?】|Day \d+|[一二三四五六七八九十]+、.+?)$/gm, prefix: '\n━━━━━━━━━━━━━━━━━━\n', suffix: '\n━━━━━━━━━━━━━━━━━━\n' },
    { pattern: /^(早上|上午|中午|下午|晚上).+?$/gm, prefix: '\n📝 ' },
    { pattern: /^(早餐|午餐|晚餐|美食|景点|住宿|交通).+?$/gm, prefix: '\n📍 ' }
  ]
  
  headerPatterns.forEach(({ pattern, prefix, suffix }) => {
    text = text.replace(pattern, (match) => {
      return `${prefix || ''}${match}${suffix || ''}`
    })
  })
  
  return text
}

// 美化列表
const beautifyLists = (text) => {
  text = text.replace(/^[•·\-]\s*/gm, '• ')
  text = text.replace(/^(\d+[\.、])\s*/gm, '$1 ')
  text = text.replace(/\n([•·\-\d])/g, '\n\n$1')
  
  return text
}

// ========== 一键插入功能 ==========

const insertWeather = async () => {
  const weatherTemplate = `🌤️ 今日天气
━━━━━━━━━━━━━━━━━━
📍 地点：北京
🌡️ 温度：22°C / 15°C
☁️ 天气：晴转多云
💨 风力：东北风 2级
💧 湿度：45%
━━━━━━━━━━━━━━━━━━`
  
  insertAtCursor(weatherTemplate)
  ElMessage.success('已插入天气模板')
}

const insertLocation = () => {
  const locationTemplate = `📍 当前位置
━━━━━━━━━━━━━━━━━━
🏠 地点名称：
🗺️ 详细地址：
⏰ 到达时间：
⏱️ 停留时长：
━━━━━━━━━━━━━━━━━━`
  
  insertAtCursor(locationTemplate)
}

const insertStats = () => {
  const statsTemplate = `📊 今日数据
━━━━━━━━━━━━━━━━━━
👣 步数：____ 步
📏 距离：____ 公里
⏱️ 时长：____ 小时
💰 消费：¥____
📷 照片：____ 张
⭐ 评分：____ / 10
━━━━━━━━━━━━━━━━━━`
  
  insertAtCursor(statsTemplate)
}

const insertMood = () => {
  showMoodPicker.value = true
}

const insertMoodText = (mood) => {
  const moodTemplate = `${mood.emoji} 今日心情
━━━━━━━━━━━━━━━━━━
${mood.text}

具体描述：

━━━━━━━━━━━━━━━━━━`
  
  insertAtCursor(moodTemplate)
  showMoodPicker.value = false
}

const insertFood = () => {
  const foodTemplate = `🍜 美食记录
━━━━━━━━━━━━━━━━━━
🍽️ 店名：
📍 地址：
💰 人均：¥
⭐ 评分：

【必点菜品】
• 
• 
• 

【口味评价】

【推荐指数】⭐⭐⭐⭐⭐
━━━━━━━━━━━━━━━━━━`
  
  insertAtCursor(foodTemplate)
  ElMessage.success('已插入美食模板')
}

const insertTransport = () => {
  const transportTemplate = `🚗 交通信息
━━━━━━━━━━━━━━━━━━
🚆 交通方式：
📍 出发地：
📍 目的地：
⏰ 出发时间：
⏱️ 行程时长：
💰 费用：¥

【交通体验】

【实用贴士】
• 
• 
━━━━━━━━━━━━━━━━━━`
  
  insertAtCursor(transportTemplate)
  ElMessage.success('已插入交通模板')
}

const insertHotel = () => {
  const hotelTemplate = `🏨 住宿信息
━━━━━━━━━━━━━━━━━━
🏠 酒店名称：
📍 地址：
💰 价格：¥/晚
⭐ 评分：

【房型设施】
• 
• 
• 

【入住体验】

【周边便利】
• 
• 
━━━━━━━━━━━━━━━━━━`
  
  insertAtCursor(hotelTemplate)
  ElMessage.success('已插入住宿模板')
}

const insertCost = () => {
  const costTemplate = `💰 今日花费
━━━━━━━━━━━━━━━━━━
🚗 交通：¥
🍜 餐饮：¥
🏨 住宿：¥
🎫 门票：¥
🛍️ 购物：¥
🎁 其他：¥

━━━━━━━━━━━━━━━━━━
💵 总计：¥
━━━━━━━━━━━━━━━━━━`
  
  insertAtCursor(costTemplate)
  ElMessage.success('已插入花费模板')
}

const applyTemplate = (type) => {
  const template = templates[type]
  if (template) {
    if (content.value.trim()) {
      if (!confirm('当前内容将被替换，确定使用模板吗？')) {
        return
      }
    }
    content.value = template
    
    const titles = {
      travel: '我的旅行日记',
      food: '美食探店记录',
      photo: '摄影随拍笔记'
    }
    if (!title.value) {
      title.value = titles[type]
    }
    
    ElMessage.success(`已应用${type === 'travel' ? '行程' : type === 'food' ? '美食' : '摄影'}模板`)
  }
}

const aiPolish = async () => {
  if (!content.value.trim()) {
    ElMessage.warning('先写点什么再润色吧~')
    return
  }
  
  // 打开AI面板并预填充内容
  openAIPanel()
}

const insertAtCursor = (text) => {
  const textarea = editorRef.value
  if (!textarea) return
  
  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  const before = content.value.substring(0, start)
  const after = content.value.substring(end)
  
  content.value = before + '\n' + text + '\n' + after
  
  setTimeout(() => {
    const newPos = start + text.length + 2
    textarea.setSelectionRange(newPos, newPos)
    textarea.focus()
  }, 0)
}

const renderMarkdown = (text) => {
  if (!text) return ''
  
  // 先处理HTML转义
  let html = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
  
  // 处理分隔线（使用CSS样式替代特殊字符）
  html = html.replace(/━{10,}/g, '<div class="divider-line"></div>')
  
  // 处理标题
  html = html.replace(/^(【.+?】)$/gm, '<h3 class="preview-header">$1</h3>')
  
  // 处理Markdown风格的标题
  html = html.replace(/^###\s+(.+)$/gm, '<h4 class="preview-subheader">$1</h4>')
  html = html.replace(/^##\s+(.+)$/gm, '<h3 class="preview-header">$1</h3>')
  html = html.replace(/^#\s+(.+)$/gm, '<h2 class="preview-title">$1</h2>')
  
  // 处理列表项
  html = html.replace(/^•\s+(.+)$/gm, '<div class="list-item">• $1</div>')
  html = html.replace(/^(\d+[.、])\s+(.+)$/gm, '<div class="list-item num">$1 $2</div>')
  
  // 处理引用块
  html = html.replace(/^>\s+(.+)$/gm, '<blockquote class="quote-block">$1</blockquote>')
  
  // 处理高亮文本
  html = html.replace(/==(.+?)==/g, '<mark class="highlight">$1</mark>')
  
  // 处理粗体和斜体
  html = html.replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>')
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
  html = html.replace(/\*(.+?)\*/g, '<em>$1</em>')
  
  // 处理emoji - 使用更广泛的匹配
  // 匹配常见的emoji范围
  html = html.replace(
    /([\u{1F300}-\u{1F9FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]|[\u{1F100}-\u{1F1FF}]|[\u{1F200}-\u{1F2FF}]|[\u{1F600}-\u{1F64F}]|[\u{1F680}-\u{1F6FF}]|[\u{1F1E0}-\u{1F1FF}]|[⭐✨❤️������❣️�������])/gu,
    '<span class="big-emoji">$1</span>'
  )
  
  // 处理换行
  html = html.replace(/\n/g, '<br>')
  
  return html
}

const handleKeydown = (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === 's') {
    e.preventDefault()
    saveDraft()
  }
  
  if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
    e.preventDefault()
    if (canPublish.value) {
      publish()
    }
  }
}

const saveDraft = () => {
  const draft = {
    title: title.value,
    content: content.value,
    savedAt: new Date().toISOString()
  }
  localStorage.setItem('diary_draft', JSON.stringify(draft))
  lastSaved.value = new Date()
  ElMessage.success('草稿已保存')
  emit('save', draft)
}

const autoSave = () => {
  if (content.value.trim()) {
    saveDraft()
  }
}

const publish = () => {
  if (!canPublish.value) {
    ElMessage.warning('标题和内容不能为空哦~')
    return
  }
  
  const diary = {
    title: title.value,
    content: content.value,
    createdAt: new Date().toISOString()
  }
  
  emit('publish', diary)
  localStorage.removeItem('diary_draft')
  ElMessage.success('日记发布成功！')
}

const formatTime = (date) => {
  const now = new Date()
  const diff = now - date
  
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  return `${Math.floor(diff / 86400000)}天前`
}

const loadDraft = () => {
  const draft = localStorage.getItem('diary_draft')
  if (draft) {
    const data = JSON.parse(draft)
    title.value = data.title || ''
    content.value = data.content || ''
    lastSaved.value = new Date(data.savedAt)
  }
}

let autoSaveTimer = null
watch(content, () => {
  clearTimeout(autoSaveTimer)
  autoSaveTimer = setTimeout(() => {
    autoSave()
  }, 30000)
})

loadDraft()
</script>

<style scoped>
.smart-editor {
  background: linear-gradient(180deg, #0a0a1a 0%, #12121f 100%);
  border-radius: 16px;
  padding: 20px;
  color: #fff;
  position: relative;
}

/* 工具栏 */
.editor-toolbar {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.toolbar-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.group-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
  margin-right: 4px;
  white-space: nowrap;
}

.toolbar-divider {
  width: 1px;
  height: 24px;
  background: rgba(255, 255, 255, 0.1);
}

.tool-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s;
}

.tool-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateY(-2px);
}

.tool-btn.primary {
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.2), rgba(123, 44, 191, 0.2));
  border-color: rgba(0, 212, 255, 0.3);
}

.tool-btn.primary:hover {
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.3), rgba(123, 44, 191, 0.3));
  box-shadow: 0 4px 15px rgba(0, 212, 255, 0.2);
}

.tool-btn.ai-btn {
  background: linear-gradient(135deg, rgba(255, 107, 107, 0.2), rgba(255, 217, 61, 0.2));
  border-color: rgba(255, 107, 107, 0.3);
}

.tool-btn.ai-btn:hover {
  background: linear-gradient(135deg, rgba(255, 107, 107, 0.3), rgba(255, 217, 61, 0.3));
  box-shadow: 0 4px 15px rgba(255, 107, 107, 0.2);
}

.btn-icon {
  font-size: 16px;
}

/* 编辑区域 */
.editor-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

@media (max-width: 900px) {
  .editor-container {
    grid-template-columns: 1fr;
  }
}

.editor-wrapper {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.title-input {
  width: 100%;
  padding: 14px 18px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  color: #fff;
  font-size: 18px;
  font-weight: 600;
  transition: all 0.3s;
}

.title-input:focus {
  outline: none;
  border-color: rgba(0, 212, 255, 0.4);
  background: rgba(255, 255, 255, 0.08);
}

.title-input::placeholder {
  color: rgba(255, 255, 255, 0.3);
}

.content-editor {
  width: 100%;
  min-height: 400px;
  padding: 18px;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  color: #fff;
  font-size: 15px;
  line-height: 1.8;
  resize: vertical;
  font-family: inherit;
  transition: all 0.3s;
}

.content-editor:focus {
  outline: none;
  border-color: rgba(0, 212, 255, 0.3);
}

.content-editor::placeholder {
  color: rgba(255, 255, 255, 0.3);
}

.editor-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 4px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
}

/* 预览区域 */
.preview-wrapper {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  overflow: hidden;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.03);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.preview-title {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
}

.preview-toggle {
  padding: 4px 12px;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  color: rgba(255, 255, 255, 0.6);
  font-size: 12px;
  cursor: pointer;
}

.preview-content {
  padding: 20px;
  min-height: 400px;
  max-height: 500px;
  overflow-y: auto;
  line-height: 1.8;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.9);
}

.preview-content :deep(.divider-line) {
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  margin: 16px 0;
}

.preview-content :deep(.preview-title) {
  color: #00d4ff;
  font-size: 20px;
  font-weight: 700;
  margin: 16px 0 12px;
  padding-bottom: 8px;
  border-bottom: 2px solid rgba(0, 212, 255, 0.3);
}

.preview-content :deep(.preview-header) {
  color: #00d4ff;
  font-size: 16px;
  font-weight: 600;
  margin: 12px 0 8px;
}

.preview-content :deep(.preview-subheader) {
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
  font-weight: 600;
  margin: 10px 0 6px;
}

.preview-content :deep(.big-emoji) {
  font-size: 1.3em;
  margin: 0 2px;
  display: inline-block;
}

.preview-content :deep(.list-item) {
  padding: 4px 0;
  padding-left: 8px;
  border-left: 2px solid rgba(0, 212, 255, 0.3);
  margin: 4px 0;
}

.preview-content :deep(.list-item.num) {
  border-left-color: rgba(123, 44, 191, 0.3);
}

.preview-content :deep(.quote-block) {
  border-left: 3px solid rgba(255, 107, 107, 0.5);
  padding: 8px 12px;
  margin: 8px 0;
  background: rgba(255, 107, 107, 0.05);
  border-radius: 0 8px 8px 0;
  font-style: italic;
  color: rgba(255, 255, 255, 0.8);
}

.preview-content :deep(.highlight) {
  background: linear-gradient(120deg, rgba(255, 217, 61, 0.3), rgba(255, 217, 61, 0.1));
  padding: 2px 6px;
  border-radius: 4px;
  color: #ffd93d;
}

.preview-content :deep(strong) {
  color: #fff;
  font-weight: 600;
}

.preview-content :deep(em) {
  color: rgba(255, 255, 255, 0.9);
  font-style: italic;
}

/* 底部操作 */
.editor-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.action-btn {
  padding: 12px 28px;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.action-btn.secondary {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.7);
}

.action-btn.secondary:hover {
  background: rgba(255, 255, 255, 0.1);
}

.action-btn.primary {
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  border: none;
  color: #fff;
}

.action-btn.primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 212, 255, 0.3);
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ========== AI 侧边面板 ========== */
.ai-panel-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  z-index: 1000;
  display: flex;
  justify-content: flex-end;
}

.ai-panel {
  width: 420px;
  max-width: 100%;
  height: 100%;
  background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
  border-left: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  flex-direction: column;
  animation: slideIn 0.3s ease;
  overflow-y: auto;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.ai-panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.ai-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: 600;
  color: #fff;
}

.ai-icon {
  font-size: 24px;
}

.close-btn {
  width: 32px;
  height: 32px;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.6);
  font-size: 20px;
  cursor: pointer;
  transition: all 0.3s;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
}

/* AI输入区域 */
.ai-input-section {
  padding: 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.input-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 12px;
}

.label-icon {
  font-size: 16px;
}

.ai-input {
  width: 100%;
  padding: 14px;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  color: #fff;
  font-size: 14px;
  line-height: 1.6;
  resize: vertical;
  font-family: inherit;
  transition: all 0.3s;
}

.ai-input:focus {
  outline: none;
  border-color: rgba(0, 212, 255, 0.5);
  background: rgba(0, 0, 0, 0.4);
}

.ai-input::placeholder {
  color: rgba(255, 255, 255, 0.3);
}

/* 快捷提示词 */
.quick-prompts {
  margin-top: 12px;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}

.prompt-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
}

.prompt-chip {
  padding: 6px 12px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  color: rgba(255, 255, 255, 0.6);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.3s;
}

.prompt-chip:hover {
  background: rgba(0, 212, 255, 0.1);
  border-color: rgba(0, 212, 255, 0.3);
  color: rgba(255, 255, 255, 0.9);
}

/* 风格选择 */
.ai-style-section {
  padding: 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.style-options {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.style-chip {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s;
}

.style-chip:hover {
  background: rgba(255, 255, 255, 0.1);
}

.style-chip.active {
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.3), rgba(123, 44, 191, 0.3));
  border-color: rgba(0, 212, 255, 0.5);
  color: #fff;
}

.style-emoji {
  font-size: 16px;
}

/* 生成按钮 */
.generate-btn {
  margin: 0 24px 24px;
  padding: 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 12px;
  color: #fff;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.generate-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

.generate-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.loading-spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 生成结果区域 */
.ai-result-section {
  flex: 1;
  margin: 0 24px 24px;
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: rgba(255, 255, 255, 0.03);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.result-title {
  font-size: 14px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}

.result-actions {
  display: flex;
  gap: 8px;
}

.action-icon-btn {
  width: 32px;
  height: 32px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.action-icon-btn:hover {
  background: rgba(255, 255, 255, 0.1);
}

.result-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  max-height: 400px;
}

.content-preview {
  font-size: 14px;
  line-height: 1.8;
  color: rgba(255, 255, 255, 0.85);
  white-space: pre-wrap;
}

.result-footer {
  padding: 16px 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.use-btn {
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  border: none;
  border-radius: 10px;
  color: #fff;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.use-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 212, 255, 0.3);
}

/* 空状态 */
.ai-empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 24px;
  text-align: center;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
  opacity: 0.8;
}

.empty-title {
  font-size: 18px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 8px;
}

.empty-desc {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.5);
  line-height: 1.6;
}

/* 心情选择弹窗 */
.mood-picker-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1001;
}

.mood-picker-content {
  background: linear-gradient(135deg, #1a1a2e, #16213e);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 28px;
  max-width: 400px;
  width: 90%;
}

.mood-picker-content h3 {
  text-align: center;
  margin-bottom: 24px;
  font-size: 18px;
  color: #fff;
}

.mood-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.mood-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px 8px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
}

.mood-item:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateY(-4px);
}

.mood-emoji {
  font-size: 32px;
}

.mood-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
}
</style>
