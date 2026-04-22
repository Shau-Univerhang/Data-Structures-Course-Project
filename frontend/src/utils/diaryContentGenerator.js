/**
 * 智能日记内容生成器（纯文本版）
 * 根据行程数据生成连贯的游记文本（无 Markdown 格式）
 */

export class DiaryContentGenerator {
  /**
   * 生成完整的游记内容（纯文本）
   * @param {Object} tripData - 行程数据
   * @param {Object} options - 生成选项
   * @returns {string} 生成的游记文本（纯文本）
   */
  static generate(tripData, options = {}) {
    const {
      includeEmojis = true,
      includeTips = true
    } = options

    const lines = []
    
    // 1. 生成标题和开头
    lines.push(this._generateHeader(tripData, includeEmojis))
    lines.push('')
    
    // 2. 生成行程概述
    lines.push(this._generateOverview(tripData, includeEmojis))
    lines.push('')
    
    // 3. 按天生成详细内容
    const dayGroups = this._groupByDay(tripData.schedules)
    Object.entries(dayGroups)
      .sort(([a], [b]) => parseInt(a) - parseInt(b))
      .forEach(([day, spots], index) => {
        lines.push(this._generateDayContent(day, spots, index + 1, {
          includeEmojis,
          includeTips
        }))
        lines.push('')
      })
    
    // 4. 生成结尾
    lines.push(this._generateEnding(tripData, includeEmojis))
    
    return lines.join('\n')
  }

  /**
   * 生成标题和开头（纯文本）
   */
  static _generateHeader(tripData, includeEmojis) {
    const title = tripData.title || `${tripData.destination}之旅`
    const emoji = includeEmojis ? '🎒 ' : ''
    const greetings = [
      '一段难忘的旅程',
      '说走就走的旅行',
      '探索未知的旅程',
      '心之所向，素履以往'
    ]
    const greeting = greetings[Math.floor(Math.random() * greetings.length)]
    
    return `${emoji}${title}\n\n${greeting}`
  }

  /**
   * 生成行程概述（纯文本）
   */
  static _generateOverview(tripData, includeEmojis) {
    const lines = []
    lines.push('📋 行程概览')
    lines.push('')
    
    const destination = tripData.destination || '未知目的地'
    const days = tripData.total_days || 1
    const spotCount = tripData.schedules?.length || 0
    
    if (includeEmojis) {
      lines.push(`📍 目的地：${destination}`)
      lines.push(`📅 天数：${days}天`)
      lines.push(`🏛️ 景点数：${spotCount}个`)
    } else {
      lines.push(`目的地：${destination}`)
      lines.push(`天数：${days}天`)
      lines.push(`景点数：${spotCount}个`)
    }
    
    // 添加路线概览
    const cities = this._extractCities(tripData.schedules)
    if (cities.length > 0) {
      lines.push('')
      lines.push(`🗺️ 路线：${cities.join(' → ')}`)
    }
    
    lines.push('')
    lines.push('─'.repeat(40))
    
    return lines.join('\n')
  }

  /**
   * 生成一天的详细内容（纯文本）
   */
  static _generateDayContent(day, spots, dayIndex, options) {
    const { includeEmojis, includeTips } = options
    const lines = []
    
    // 日期标题
    const dateEmoji = includeEmojis ? this._getDayEmoji(dayIndex) : ''
    const theme = this._generateDayTheme(spots)
    lines.push(`${dateEmoji}第${day}天：${theme}`)
    lines.push('')
    
    // 开场白
    const openings = this._getDayOpenings(dayIndex)
    lines.push(openings[Math.floor(Math.random() * openings.length)])
    lines.push('')
    
    // 按顺序描述每个景点
    const sortedSpots = [...spots].sort((a, b) => 
      (a.order_index || 0) - (b.order_index || 0)
    )
    
    sortedSpots.forEach((spot, index) => {
      // 景点标题
      const spotEmoji = includeEmojis ? this._getSpotEmoji(spot.spot_name) : ''
      lines.push(`${spotEmoji}${spot.spot_name}`)
      lines.push('')
      
      // 生成内容
      const content = this._generateSpotDescription(spot)
      lines.push(content)
      lines.push('')
      
      // 添加小提示
      if (includeTips && spot.notes) {
        lines.push(`💡 小贴士：${spot.notes}`)
        lines.push('')
      }
      
      // 添加过渡（如果不是最后一个景点）
      if (index < sortedSpots.length - 1) {
        const transitions = [
          '接着，我们前往下一个目的地...',
          '游览结束后，我们启程前往...',
          '带着满满的回忆，我们继续前往...',
          '下一站是...'
        ]
        lines.push(transitions[Math.floor(Math.random() * transitions.length)])
        lines.push('')
      }
    })
    
    // 每日小结
    const summaries = this._getDaySummaries()
    lines.push(`今日小结：${summaries[Math.floor(Math.random() * summaries.length)]}`)
    
    return lines.join('\n')
  }

  /**
   * 生成景点描述（纯文本）
   */
  static _generateSpotDescription(spot) {
    const name = spot.spot_name
    const time = spot.visit_time_start ? spot.visit_time_start.substring(0, 5) : ''
    
    // 根据景点名称生成描述
    const descriptions = this._getSpotDescriptions(name)
    const baseDesc = descriptions[Math.floor(Math.random() * descriptions.length)]
    
    if (time) {
      return `早上${time}，我们来到了${name}。${baseDesc}在这里，我们度过了愉快的时光。`
    }
    
    return `我们来到了${name}。${baseDesc}在这里，我们度过了愉快的时光。`
  }

  /**
   * 生成结尾（纯文本）
   */
  static _generateEnding(tripData, includeEmojis) {
    const lines = []
    lines.push('─'.repeat(40))
    lines.push('')
    lines.push('📝 旅行总结')
    lines.push('')
    
    const endings = [
      `这次${tripData.total_days || ''}天的${tripData.destination || ''}之旅，让我收获满满。每一个景点都留下了深刻的印象，每一次体验都是难忘的回忆。旅行不只是在路上，更是在心中留下的那些美好瞬间。`,
      `转眼间，${tripData.title || '这次旅行'}就要结束了。回首这几天的点点滴滴，有惊喜，有感动，有欢笑。旅行最大的意义，或许就是让我们在陌生的地方，发现久违的自己。`,
      `告别${tripData.destination || '这座城市'}，心中满是不舍。这次旅行让我看到了不一样的风景，遇见了有趣的人，收获了珍贵的回忆。期待下一次的旅程，继续探索这个美丽的世界。`,
      `${tripData.total_days || ''}天的行程虽然短暂，但留下的回忆却是永恒的。从第一天到最后一天，每一天都充满了惊喜。感谢这次旅行，让我重新找回了对生活的热爱。`
    ]
    
    lines.push(endings[Math.floor(Math.random() * endings.length)])
    lines.push('')
    
    if (includeEmojis) {
      lines.push('✨ 期待下一次出发！🌟')
    } else {
      lines.push('期待下一次出发！')
    }
    
    lines.push('')
    lines.push('─'.repeat(40))
    lines.push('')
    lines.push(`📅 记录时间：${new Date().toLocaleString()}`)
    
    return lines.join('\n')
  }

  /**
   * 工具方法：按天分组
   */
  static _groupByDay(schedules) {
    if (!schedules) return {}
    return schedules.reduce((groups, schedule) => {
      const day = schedule.day_number || 1
      if (!groups[day]) groups[day] = []
      groups[day].push(schedule)
      return groups
    }, {})
  }

  /**
   * 工具方法：提取城市列表
   */
  static _extractCities(schedules) {
    if (!schedules) return []
    const cities = new Set()
    schedules.forEach(s => {
      if (s.spot?.city) cities.add(s.spot.city)
      else if (s.city) cities.add(s.city)
    })
    return Array.from(cities)
  }

  /**
   * 获取天数 emoji
   */
  static _getDayEmoji(day) {
    const emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
    return emojis[day - 1] || '📅'
  }

  /**
   * 获取景点 emoji
   */
  static _getSpotEmoji(spotName) {
    if (!spotName) return '📍'
    if (/故宫|博物馆|寺|庙/.test(spotName)) return '🏛️'
    if (/山|峰|岭/.test(spotName)) return '⛰️'
    if (/湖|海|河|潭/.test(spotName)) return '🌊'
    if (/公园|园|林/.test(spotName)) return '🌳'
    if (/街|路|巷/.test(spotName)) return '🛤️'
    if (/塔|楼|阁/.test(spotName)) return '🏯'
    if (/长城/.test(spotName)) return '🧱'
    if (/美食|街|小吃/.test(spotName)) return '🍜'
    return '📍'
  }

  /**
   * 生成当天主题
   */
  static _generateDayTheme(spots) {
    if (!spots || spots.length === 0) return '精彩一天'
    
    const spotNames = spots.map(s => s.spot_name || '').join('')
    
    const themes = [
      { pattern: /故宫|博物馆|古迹|文化/, theme: '文化探索之旅' },
      { pattern: /山|湖|海|公园|自然|森林/, theme: '自然风光之旅' },
      { pattern: /街|巷|城|古镇|老街/, theme: '城市漫步时光' },
      { pattern: /寺|庙|塔|宗教/, theme: '人文古迹寻踪' },
      { pattern: /美食|街|小吃|味道/, theme: '美食寻味之旅' },
      { pattern: /乐园|欢乐|主题/, theme: '欢乐游玩时光' }
    ]
    
    for (const { pattern, theme } of themes) {
      if (pattern.test(spotNames)) return theme
    }
    
    return '精彩的一天'
  }

  /**
   * 获取每日开场白
   */
  static _getDayOpenings(dayIndex) {
    return [
      '清晨的阳光洒进房间，新的一天开始了。',
      '带着满满的期待，我们迎来了新的旅程。',
      '今天的行程同样精彩，让我们继续探索。',
      '新的一天，新的发现，新的惊喜在等着我们。',
      '昨晚休息得很好，今天精力充沛，准备出发！'
    ]
  }

  /**
   * 获取每日小结
   */
  static _getDaySummaries() {
    return [
      '充实而美好的一天，收获满满！',
      '今天的每一处风景都值得被记住。',
      '疲惫但快乐着，这就是旅行的意义。',
      '明天还有更多精彩等着我们。',
      '带着美好的回忆，期待明天的旅程。'
    ]
  }

  /**
   * 获取景点描述模板
   */
  static _getSpotDescriptions(spotName) {
    return [
      '这里景色宜人，让人流连忘返。',
      '独特的建筑风格让人眼前一亮。',
      '浓厚的历史氛围让人沉醉其中。',
      '美丽的自然风光让人心旷神怡。',
      '这里的人文气息让人印象深刻。',
      '不愧是著名的旅游景点，果然名不虚传。'
    ]
  }
}

/**
 * 快速生成函数（纯文本）
 */
export const generateDiaryContent = (tripData, options = {}) => {
  return DiaryContentGenerator.generate(tripData, {
    includeEmojis: true,
    includeTips: true,
    ...options
  })
}

export default DiaryContentGenerator
