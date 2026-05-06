/**
 * 智能标题生成器 - 基于TextRank和TF-IDF思想
 * 
 * 参考算法：
 * 1. TextRank (Mihalcea & Tarau, 2004) - 图排序算法提取关键词
 * 2. TF-IDF - 词频-逆文档频率
 * 3. 中文分词与关键词提取
 * 
 * 功能：
 * 1. 智能提取日记主标题
 * 2. 生成时间段小标题
 * 3. 提取关键地点和主题
 */

class SmartTitleGenerator {
  /**
   * 停用词表
   */
  static STOP_WORDS = new Set([
    '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这', '那', '这些', '那些', '这个', '那个',
    '今天', '明天', '昨天', '现在', '当时', '后来', '接着', '然后', '之后', '最后', '终于', '开始', '结束', '完成', '准备',
    '感觉', '觉得', '认为', '想', '觉得', '好像', '大概', '可能', '应该', '一定', '非常', '特别', '很', '太', '真', '挺', '比较', '相当',
    '我们', '你们', '他们', '她们', '它们', '咱们', '大家', '别人', '人家',
    '这里', '那里', '哪里', '到处', '处处', '处处', '到处',
    '一下', '一些', '一点', '一方面', '一直', '一切', '一样', '一般',
    '可以', '能够', '应该', '必须', '需要', '得', '地', '着', '过', '了',
    '因为', '所以', '因此', '于是', '但是', '可是', '不过', '然而', '虽然', '尽管',
    '如果', '假如', '假设', '即使', '哪怕', '不管', '无论', '只要', '只有', '除了',
    '关于', '对于', '由于', '根据', '按照', '通过', '经过', '随着',
    '从', '向', '往', '在', '到', '于', '给', '跟', '同', '与', '和', '及', '以及'
  ])

  /**
   * 主题关键词库 - 用于识别旅行主题
   */
  static THEME_KEYWORDS = {
    nature: {
      words: ['山', '海', '湖', '河', '森林', '草原', '沙漠', '瀑布', '海滩', '雪山', '峡谷', '湿地', '公园', '自然', '风景', '景色', '风光', '美景'],
      titleTemplates: ['探索{name}', '{name}之旅', '漫步{name}', '遇见{name}', '{name}风光']
    },
    city: {
      words: ['城市', '都市', '街头', '夜景', '建筑', '摩天大楼', '老城区', '市中心', '商圈', 'CBD', '地标', '繁华'],
      titleTemplates: ['{name}城市漫游', '探索{name}', '{name}印象', '漫步{name}街头', '{name}都市风情']
    },
    culture: {
      words: ['博物馆', '古迹', '遗址', '寺庙', '教堂', '历史', '文化', '艺术', '展览', '古建筑', '文物', '传统', '民俗'],
      titleTemplates: ['{name}文化之旅', '探寻{name}历史', '走进{name}', '{name}人文之旅', '品味{name}文化']
    },
    food: {
      words: ['美食', '小吃', '餐厅', '味道', '品尝', '特色菜', '当地美食', '夜市', '美食街', '好吃', '美味', '料理', '火锅', '烧烤', '海鲜'],
      titleTemplates: ['{name}美食地图', '寻味{name}', '{name}吃货指南', '舌尖上的{name}', '{name}美食探店']
    },
    adventure: {
      words: ['徒步', '登山', '潜水', '滑雪', '漂流', '攀岩', '露营', '探险', '挑战', '刺激', '户外', '极限'],
      titleTemplates: ['{name}探险记', '挑战{name}', '{name}户外之旅', '征服{name}', '勇闯{name}']
    },
    relax: {
      words: ['度假', '休闲', '放松', '温泉', 'SPA', '沙滩', '阳光', '慵懒', '惬意', '舒适', '慢生活', '发呆'],
      titleTemplates: ['{name}慢时光', '慵懒{name}假日', '享受{name}', '{name}度假日记', '惬意{name}之旅']
    }
  }

  /**
   * 地点后缀模式 - 用于识别地点名称
   */
  static LOCATION_SUFFIXES = [
    '市', '省', '县', '区', '镇', '村', '岛', '山', '湖', '海', '河', '江', '湾',
    '古城', '古镇', '景区', '景点', '公园', '博物馆', '寺庙', '教堂', '广场', '街道',
    '酒店', '民宿', '客栈', '机场', '车站', '码头', '餐厅', '咖啡馆', '店'
  ]

  /**
   * 生成日记主标题
   * @param {string} content - 日记全文
   * @param {Array} timeline - 时间轴数据
   * @returns {string} 生成的标题
   */
  static generateMainTitle(content, timeline = []) {
    if (!content || content.length < 10) {
      return '我的旅行日记'
    }

    // 1. 提取关键词
    const keywords = this.extractKeywords(content, 10)
    
    // 2. 识别主要地点
    const locations = this.extractAllLocations(content)
    const mainLocation = locations.length > 0 ? locations[0] : null
    
    // 3. 识别旅行主题
    const theme = this.identifyTheme(content)
    
    // 4. 根据时间轴提取关键活动
    const keyActivities = this.extractKeyActivities(timeline)
    
    // 5. 生成候选标题
    const candidates = this.generateTitleCandidates(mainLocation, theme, keywords, keyActivities)
    
    // 6. 选择最佳标题
    return this.selectBestTitle(candidates, content)
  }

  /**
   * 生成时间段小标题
   * @param {Array} activities - 该时间段的活动列表
   * @param {number} dayIndex - 天数索引
   * @returns {string} 生成的小标题
   */
  static generateSectionTitle(activities, dayIndex = 0) {
    if (!activities || activities.length === 0) {
      return `第${dayIndex + 1}天`
    }

    // 1. 提取该时间段的所有文本
    const allText = activities.map(a => a.title || a.description || '').join(' ')
    
    // 2. 提取关键词
    const keywords = this.extractKeywords(allText, 5)
    
    // 3. 提取地点
    const locations = activities
      .map(a => a.location)
      .filter(l => l && l.length > 1)
    
    // 4. 识别主要活动类型
    const activityTypes = this.identifyActivityTypes(allText)
    
    // 5. 生成候选小标题
    const candidates = this.generateSectionCandidates(locations, keywords, activityTypes, dayIndex)
    
    // 6. 选择最佳小标题
    return this.selectBestSectionTitle(candidates, activities)
  }

  /**
   * 基于TextRank思想提取关键词
   * @param {string} text - 输入文本
   * @param {number} topN - 返回前N个关键词
   * @returns {Array} 关键词列表（带权重）
   */
  static extractKeywords(text, topN = 10) {
    // 1. 分词（简化版中文分词）
    const words = this.segmentWords(text)
    
    // 2. 过滤停用词和短词
    const filteredWords = words.filter(word => 
      word.length >= 2 && 
      !this.STOP_WORDS.has(word) &&
      !/^\d+$/.test(word) &&
      !/[，。！？；：""''（）【】\[\]]/.test(word)
    )
    
    // 3. 计算词频 (TF)
    const wordFreq = {}
    filteredWords.forEach(word => {
      wordFreq[word] = (wordFreq[word] || 0) + 1
    })
    
    // 4. 构建共现图（窗口大小为3）
    const cooccurrence = {}
    const windowSize = 3
    
    for (let i = 0; i < filteredWords.length; i++) {
      const word = filteredWords[i]
      if (!cooccurrence[word]) cooccurrence[word] = {}
      
      // 窗口内的词建立连接
      const start = Math.max(0, i - windowSize)
      const end = Math.min(filteredWords.length, i + windowSize + 1)
      
      for (let j = start; j < end; j++) {
        if (i !== j) {
          const neighbor = filteredWords[j]
          cooccurrence[word][neighbor] = (cooccurrence[word][neighbor] || 0) + 1
        }
      }
    }
    
    // 5. TextRank迭代计算
    const dampingFactor = 0.85
    const iterations = 30
    const scores = {}
    
    // 初始化
    Object.keys(wordFreq).forEach(word => {
      scores[word] = 1
    })
    
    // 迭代
    for (let i = 0; i < iterations; i++) {
      const newScores = {}
      
      Object.keys(scores).forEach(word => {
        let score = (1 - dampingFactor)
        
        const neighbors = cooccurrence[word] || {}
        Object.keys(neighbors).forEach(neighbor => {
          const weight = neighbors[neighbor]
          const neighborOutSum = Object.values(cooccurrence[neighbor] || {}).reduce((a, b) => a + b, 0)
          
          if (neighborOutSum > 0) {
            score += dampingFactor * weight * scores[neighbor] / neighborOutSum
          }
        })
        
        newScores[word] = score
      })
      
      Object.assign(scores, newScores)
    }
    
    // 6. 返回排序后的关键词
    return Object.entries(scores)
      .sort((a, b) => b[1] - a[1])
      .slice(0, topN)
      .map(([word, score]) => ({ word, score }))
  }

  /**
   * 简化的中文分词
   * @param {string} text - 输入文本
   * @returns {Array} 词列表
   */
  static segmentWords(text) {
    // 基于词典和规则的简单分词
    const words = []
    let i = 0
    
    while (i < text.length) {
      // 尝试匹配最长的词
      let matched = false
      
      // 优先匹配地点模式
      for (let len = Math.min(10, text.length - i); len >= 2; len--) {
        const substr = text.substr(i, len)
        
        // 检查是否是地点
        if (this.isLocationPattern(substr)) {
          words.push(substr)
          i += len
          matched = true
          break
        }
      }
      
      if (!matched) {
        // 双字分词
        if (i + 1 < text.length) {
          words.push(text.substr(i, 2))
          i += 2
        } else {
          words.push(text[i])
          i++
        }
      }
    }
    
    return words
  }

  /**
   * 检查是否是地点模式
   */
  static isLocationPattern(text) {
    return this.LOCATION_SUFFIXES.some(suffix => text.endsWith(suffix))
  }

  /**
   * 提取所有地点
   */
  static extractAllLocations(text) {
    const locations = []
    const patterns = [
      /([^，。！？\s]{2,8})(?:市|省|县|区|镇|村|岛|山|湖|海|河|江)/g,
      /(?:在|前往|抵达|位于|打卡|游览|参观了?|到达|去往)(?:了|到)?(?:\s*)([^，。！？\n]{2,20})/g,
      /([^，。！？\n]{2,15})(?:景区|景点|公园|博物馆|寺庙|教堂|广场|大街|酒店|民宿)/g
    ]
    
    patterns.forEach(pattern => {
      let match
      while ((match = pattern.exec(text)) !== null) {
        const location = match[1].trim()
        if (location.length >= 2 && !this.STOP_WORDS.has(location)) {
          locations.push(location)
        }
      }
    })
    
    // 统计频率，返回最频繁的地点
    const freq = {}
    locations.forEach(loc => {
      freq[loc] = (freq[loc] || 0) + 1
    })
    
    return Object.entries(freq)
      .sort((a, b) => b[1] - a[1])
      .map(([loc]) => loc)
  }

  /**
   * 识别旅行主题
   */
  static identifyTheme(text) {
    const scores = {}
    
    Object.entries(this.THEME_KEYWORDS).forEach(([theme, data]) => {
      scores[theme] = 0
      data.words.forEach(word => {
        const regex = new RegExp(word, 'g')
        const matches = text.match(regex)
        if (matches) {
          scores[theme] += matches.length
        }
      })
    })
    
    // 返回得分最高的主题
    const sorted = Object.entries(scores).sort((a, b) => b[1] - a[1])
    return sorted[0][1] > 0 ? sorted[0][0] : 'general'
  }

  /**
   * 提取关键活动
   */
  static extractKeyActivities(timeline) {
    const activities = []
    
    timeline.forEach(day => {
      if (day.activities) {
        day.activities.forEach(act => {
          if (act.title) activities.push(act.title)
          if (act.description) activities.push(act.description)
        })
      }
      if (day.spots) {
        day.spots.forEach(spot => {
          if (spot.description) activities.push(spot.description)
        })
      }
    })
    
    return activities.slice(0, 5)
  }

  /**
   * 识别活动类型
   */
  static identifyActivityTypes(text) {
    const types = []
    
    const patterns = {
      sightseeing: ['游览', '参观', '打卡', '观光', '游玩', '逛'],
      dining: ['吃', '品尝', '美食', '餐厅', '用餐', '喝', '奶茶', '咖啡'],
      shopping: ['买', '购物', '逛街', '商店', '市场', '特产'],
      transport: ['坐', '乘', '飞机', '高铁', '地铁', '打车', '开车'],
      accommodation: ['住', '酒店', '民宿', '客栈', '入住', '房间'],
      photography: ['拍', '照片', '摄影', '打卡', '风景', '美景']
    }
    
    Object.entries(patterns).forEach(([type, keywords]) => {
      if (keywords.some(kw => text.includes(kw))) {
        types.push(type)
      }
    })
    
    return types
  }

  /**
   * 生成标题候选
   */
  static generateTitleCandidates(location, theme, keywords, activities) {
    const candidates = []
    const topKeywords = keywords.slice(0, 3).map(k => k.word)
    
    // 基于地点生成
    if (location) {
      const themeData = this.THEME_KEYWORDS[theme]
      if (themeData) {
        themeData.titleTemplates.forEach(template => {
          candidates.push(template.replace('{name}', location))
        })
      }
      
      candidates.push(
        `${location}之旅`,
        `探索${location}`,
        `漫步${location}`,
        `${location}游记`,
        `遇见${location}`
      )
    }
    
    // 基于关键词生成
    if (topKeywords.length >= 2) {
      candidates.push(
        `${topKeywords[0]}与${topKeywords[1]}`,
        `${topKeywords[0]}之旅`,
        `探索${topKeywords[0]}`,
        `${topKeywords[0]}的${topKeywords[1]}`,
        `${topKeywords[0]}·${topKeywords[1]}`
      )
    }
    
    // 通用标题
    candidates.push(
      '我的旅行日记',
      '旅途中的美好',
      '行走的记忆',
      '在路上',
      '探索未知'
    )
    
    return [...new Set(candidates)]
  }

  /**
   * 生成时间段小标题候选
   */
  static generateSectionCandidates(locations, keywords, activityTypes, dayIndex) {
    const candidates = []
    const topKeywords = keywords.slice(0, 2).map(k => k.word)
    
    // 基于地点
    if (locations.length > 0) {
      const mainLoc = locations[0]
      candidates.push(
        `探索${mainLoc}`,
        `漫步${mainLoc}`,
        `${mainLoc}时光`,
        `遇见${mainLoc}`,
        `${mainLoc}印象`
      )
    }
    
    // 基于活动类型
    if (activityTypes.includes('dining')) {
      candidates.push('美食时光', '舌尖上的旅行', '寻味之旅')
    }
    if (activityTypes.includes('sightseeing')) {
      candidates.push('观光游览', '探索发现', '风景这边独好')
    }
    if (activityTypes.includes('shopping')) {
      candidates.push('购物时光', '买买买', '淘货之旅')
    }
    if (activityTypes.includes('photography')) {
      candidates.push('光影记录', '定格美好', '镜头里的风景')
    }
    
    // 基于关键词
    if (topKeywords.length > 0) {
      candidates.push(
        `${topKeywords[0]}体验`,
        `${topKeywords[0]}之旅`,
        `感受${topKeywords[0]}`
      )
    }
    
    // 默认标题
    candidates.push(
      `第${dayIndex + 1}天`,
      '精彩一天',
      '美好时光',
      '难忘时刻'
    )
    
    return [...new Set(candidates)]
  }

  /**
   * 选择最佳标题
   */
  static selectBestTitle(candidates, content) {
    // 评分标准：
    // 1. 包含地点名称 +10
    // 2. 长度适中（8-15字）+5
    // 3. 不包含停用词开头 +3
    // 4. 有情感色彩 +2
    
    const scored = candidates.map(title => {
      let score = 0
      
      // 长度评分
      if (title.length >= 6 && title.length <= 16) {
        score += 5
      }
      
      // 情感词加分
      const emotionalWords = ['遇见', '探索', '漫步', '发现', '美好', '精彩', '难忘', '惬意', '慵懒']
      if (emotionalWords.some(w => title.includes(w))) {
        score += 3
      }
      
      // 避免过于通用的标题
      const genericTitles = ['我的旅行日记', '旅途中的美好', '在路上']
      if (genericTitles.includes(title)) {
        score -= 5
      }
      
      return { title, score }
    })
    
    scored.sort((a, b) => b.score - a.score)
    return scored[0].title
  }

  /**
   * 选择最佳时间段小标题
   */
  static selectBestSectionTitle(candidates, activities) {
    const scored = candidates.map(title => {
      let score = 0
      
      // 长度评分
      if (title.length >= 4 && title.length <= 10) {
        score += 5
      }
      
      // 避免过于通用的标题
      if (title === '精彩一天' || title === '美好时光') {
        score -= 3
      }
      
      // 包含具体地点加分
      const hasLocation = activities.some(a => 
        a.location && title.includes(a.location)
      )
      if (hasLocation) {
        score += 5
      }
      
      return { title, score }
    })
    
    scored.sort((a, b) => b.score - a.score)
    return scored[0].title
  }
}

export default SmartTitleGenerator
