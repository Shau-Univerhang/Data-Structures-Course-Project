/**
 * 时间轴解析器 - 从日记内容智能提取时间轴信息
 * 
 * 功能：
 * 1. 解析天数标记（Day 1、第一天、第1天等）
 * 2. 提取时间段（上午、下午、晚上等）
 * 3. 识别地点信息（📍标记、在、前往等）
 * 4. 提取活动描述
 * 5. 生成结构化时间轴数据
 */

class TimelineParser {
  /**
   * 解析日记内容，提取时间轴信息
   * @param {string} content - 日记内容
   * @returns {Array} 时间轴数据数组
   */
  static parse(content) {
    if (!content || typeof content !== 'string') {
      return []
    }

    const timeline = []
    const lines = content.split('\n')
    let currentDay = null
    let dayCounter = 1
    let lastDayIndex = -1

    lines.forEach((line, index) => {
      const trimmedLine = line.trim()
      if (!trimmedLine) return

      // 检测日期/天数标记
      const dayMatch = this.detectDay(trimmedLine)
      if (dayMatch) {
        // 保存之前的天数数据
        if (currentDay && currentDay.spots.length > 0) {
          timeline.push(currentDay)
        }

        currentDay = {
          day: dayMatch.label || `Day ${dayCounter}`,
          title: dayMatch.customTitle || `第${dayCounter}天`,
          spots: []
        }
        dayCounter++
        lastDayIndex = index
        return
      }

      // 如果没有检测到日期，但检测到时间段，创建默认天数
      if (!currentDay && this.detectTimeOfDay(trimmedLine)) {
        currentDay = {
          day: `Day ${dayCounter}`,
          title: `第${dayCounter}天`,
          spots: []
        }
        dayCounter++
      }

      // 提取时间点信息
      if (currentDay) {
        const timeInfo = this.extractTimeInfo(trimmedLine)
        const location = this.extractLocation(trimmedLine)
        const activity = this.extractActivity(trimmedLine)

        // 只处理包含实质内容的行
        if (timeInfo || location || activity || this.isContentLine(trimmedLine)) {
          const description = this.cleanDescription(trimmedLine, timeInfo, location)
          
          if (description || location) {
            currentDay.spots.push({
              time: timeInfo || '全天',
              description: description || '记录美好时光',
              location: location,
              activity: activity,
              raw: trimmedLine
            })
          }
        }
      }
    })

    // 添加最后一天
    if (currentDay && currentDay.spots.length > 0) {
      timeline.push(currentDay)
    }

    return this.cleanTimeline(timeline)
  }

  /**
   * 检测天数标记
   * 支持的格式：
   * - Day 1 / Day1 / day 1
   * - 第一天 / 第1天 / 第 1 天
   * - 【第一天】/ [Day 1]
   * - Day One / Day One: 标题
   */
  static detectDay(line) {
    const patterns = [
      { 
        regex: /Day\s*(\d+)/i, 
        format: (m) => ({ label: `Day ${m[1]}`, title: `第${m[1]}天` })
      },
      { 
        regex: /第\s*([一二三四五六七八九十\d]+)\s*天/, 
        format: (m) => {
          const num = this.chineseToNumber(m[1])
          return { label: `Day ${num}`, title: `第${m[1]}天` }
        }
      },
      { 
        regex: /【?第\s*([一二三四五六七八九十\d]+)\s*天】?/, 
        format: (m) => {
          const num = this.chineseToNumber(m[1])
          return { label: `Day ${num}`, title: `第${m[1]}天` }
        }
      },
      { 
        regex: /【?(Day\s*\d+)】?/i, 
        format: (m) => ({ label: m[1], title: m[1] })
      }
    ]

    for (const pattern of patterns) {
      const match = line.match(pattern.regex)
      if (match) {
        // 提取标题（去掉天数标记后的内容）
        let title = line.replace(pattern.regex, '').trim()
        // 移除常见的分隔符
        title = title.replace(/^[：:\-–—\s]+/, '').trim()
        
        const base = pattern.format(match)
        return {
          ...base,
          customTitle: title || undefined
        }
      }
    }

    return null
  }

  /**
   * 检测时间段关键词
   */
  static detectTimeOfDay(line) {
    const timeKeywords = [
      '清晨', '早上', '早晨', '上午', '中午', '午后',
      '下午', '傍晚', '晚上', '深夜', '凌晨', '夜间',
      '早', '中', '晚'
    ]
    return timeKeywords.some(keyword => line.includes(keyword))
  }

  /**
   * 提取时间信息
   */
  static extractTimeInfo(line) {
    const timeMap = {
      '清晨': '清晨',
      '早上': '早上',
      '早晨': '早晨',
      '上午': '上午',
      '中午': '中午',
      '午后': '午后',
      '下午': '下午',
      '傍晚': '傍晚',
      '晚上': '晚上',
      '深夜': '深夜',
      '凌晨': '凌晨',
      '夜间': '夜间'
    }

    for (const [keyword, label] of Object.entries(timeMap)) {
      if (line.includes(keyword)) {
        return label
      }
    }

    // 匹配具体时间 (8:00, 8点, 八点半)
    const timeMatch = line.match(/(\d{1,2})[:：](\d{2})/)
    if (timeMatch) {
      return `${timeMatch[1]}:${timeMatch[2]}`
    }

    // 匹配X点/X点半
    const hourMatch = line.match(/(\d{1,2})点(?:半)?/)
    if (hourMatch) {
      return `${hourMatch[1]}:00`
    }

    return null
  }

  /**
   * 提取地点信息
   */
  static extractLocation(line) {
    // 匹配 📍 🏨 📸 等标记
    const emojiMatch = line.match(/[📍🏨📸✈️🚗🚄🚇](?:\s*)([^，。！？\n]{2,30})/)
    if (emojiMatch) {
      return emojiMatch[1].trim()
    }

    // 匹配地点关键词
    const locationPatterns = [
      /(?:在|前往|抵达|位于|打卡|游览|参观了?|到达|去往)(?:了|到)?(?:\s*)([^，。！？\n]{2,25})/,
      /([^，。！？\n]{2,20})(?:景区|景点|公园|博物馆|餐厅|酒店|机场|车站|广场|大街|路|街)/
    ]

    for (const pattern of locationPatterns) {
      const match = line.match(pattern)
      if (match) {
        const location = match[1].trim()
        // 过滤掉一些常见的非地点词
        const nonLocations = ['这里', '那里', '家里', '酒店', '机场', '车站']
        if (!nonLocations.includes(location)) {
          return location
        }
      }
    }

    return null
  }

  /**
   * 提取活动类型
   */
  static extractActivity(line) {
    const activities = [
      '游览', '参观', '打卡', '品尝', '体验', '入住',
      '出发', '抵达', '漫步', '拍摄', '购物', '休息',
      '用餐', '早餐', '午餐', '晚餐', '夜宵', '吃饭',
      '游玩', '逛街', '爬山', '看展', '听音乐会'
    ]
    
    for (const activity of activities) {
      if (line.includes(activity)) {
        return activity
      }
    }
    return null
  }

  /**
   * 判断是否为内容行（非空、非标记行）
   */
  static isContentLine(line) {
    // 排除纯符号行
    if (/^[\s\-–—*•·]+$/.test(line)) return false
    // 排除纯数字行
    if (/^\d+$/.test(line)) return false
    // 长度至少为5个字符
    if (line.length < 5) return false
    
    return true
  }

  /**
   * 清理描述文本
   */
  static cleanDescription(line, timeInfo, location) {
    let cleaned = line
    
    // 移除时间标记
    if (timeInfo) {
      cleaned = cleaned.replace(new RegExp(timeInfo, 'g'), '')
    }
    
    // 移除地点标记
    if (location) {
      cleaned = cleaned.replace(new RegExp(location, 'g'), '')
    }
    
    // 移除特殊符号和多余空格
    cleaned = cleaned
      .replace(/[📍🏨📸✈️🚗🚄🚇🍜🍲🥘🍱]/g, '')
      .replace(/[【】\[\]()（）]/g, '')
      .replace(/^\s*[-•·–—*]\s*/, '')
      .replace(/\s+/g, ' ')
      .trim()

    return cleaned
  }

  /**
   * 清理和优化时间轴
   */
  static cleanTimeline(timeline) {
    return timeline.map(day => ({
      ...day,
      // 合并相同时间点的活动
      spots: this.mergeSpots(day.spots),
      // 如果没有标题，使用第一个地点或默认标题
      title: day.title || day.customTitle || (day.spots[0]?.location ? `探索${day.spots[0].location}` : '精彩一天')
    })).filter(day => day.spots.length > 0)
  }

  /**
   * 合并相同时间点的活动
   */
  static mergeSpots(spots) {
    const merged = []
    let lastTime = null

    spots.forEach(spot => {
      if (spot.time === lastTime && merged.length > 0) {
        // 合并到上一个spot的描述中
        const prevSpot = merged[merged.length - 1]
        if (spot.description && spot.description !== '记录美好时光') {
          prevSpot.description += `；${spot.description}`
        }
        // 保留地点信息
        if (spot.location && !prevSpot.location) {
          prevSpot.location = spot.location
        }
      } else {
        merged.push({ ...spot })
        lastTime = spot.time
      }
    })

    return merged
  }

  /**
   * 中文数字转阿拉伯数字
   */
  static chineseToNumber(chinese) {
    const map = {
      '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
      '六': 6, '七': 7, '八': 8, '九': 9, '十': 10
    }
    
    if (/^\d+$/.test(chinese)) {
      return parseInt(chinese)
    }
    
    let result = 0
    for (const char of chinese) {
      if (map[char]) {
        result = result * 10 + map[char]
      }
    }
    
    return result || 1
  }

  /**
   * 生成时间轴文本预览
   */
  static generatePreview(timeline) {
    if (!timeline || timeline.length === 0) {
      return ''
    }

    return timeline.map(day => {
      const spotsText = day.spots.map(spot => {
        const location = spot.location ? `📍${spot.location} ` : ''
        return `  ${spot.time}: ${location}${spot.description}`
      }).join('\n')
      
      return `${day.day} - ${day.title}\n${spotsText}`
    }).join('\n\n')
  }

  /**
   * 验证时间轴数据是否有效
   */
  static validate(timeline) {
    if (!Array.isArray(timeline) || timeline.length === 0) {
      return { valid: false, error: '时间轴为空' }
    }

    for (const day of timeline) {
      if (!day.day || !day.title) {
        return { valid: false, error: '天数信息不完整' }
      }
      
      if (!Array.isArray(day.spots) || day.spots.length === 0) {
        return { valid: false, error: `${day.day} 没有时间点` }
      }

      for (const spot of day.spots) {
        if (!spot.time) {
          return { valid: false, error: '时间点信息不完整' }
        }
      }
    }

    return { valid: true }
  }
}

export default TimelineParser
