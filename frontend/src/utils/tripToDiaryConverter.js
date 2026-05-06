/**
 * 行程数据 → 日记时间轴 转换器
 * 核心算法：将行程的每日安排转换为日记时间轴格式
 */

export class TripToDiaryConverter {
  /**
   * 主要转换方法
   * @param {Object} trip - 行程数据
   * @param {Object} options - 转换选项
   * @returns {Object} 日记数据结构
   */
  static convert(trip, options = {}) {
    const {
      generateContent = false,  // 是否生成日记正文
      includeImages = true,      // 是否包含图片
      timeSlotDuration = 2       // 每个景点默认游览时长（小时）
    } = options

    // 1. 提取基础信息
    const diaryBase = this._extractBaseInfo(trip)
    
    // 2. 转换时间轴（核心算法）
    const timeline = this._convertTimeline(trip.schedules, timeSlotDuration)
    
    // 3. 提取图片
    const images = includeImages ? this._extractImages(trip.schedules) : []
    
    // 4. 生成日记正文（可选）
    const content = generateContent ? this._generateContent(trip, timeline) : ''
    
    return {
      title: diaryBase.title,
      content,
      trip_id: trip.id,
      diary_type: 'travel',
      destination: diaryBase.destination,
      total_days: diaryBase.totalDays,
      itinerary: timeline,
      images,
      budget: null,
      companion: null
    }
  }

  /**
   * 提取基础信息
   */
  static _extractBaseInfo(trip) {
    return {
      title: `${trip.title || trip.destination}游记`,
      destination: trip.destination || '未知目的地',
      totalDays: trip.total_days || 1
    }
  }

  /**
   * 核心算法：转换时间轴
   * 将行程的 schedules 数组转换为日记的 itinerary 格式
   */
  static _convertTimeline(schedules, timeSlotDuration) {
    if (!schedules || schedules.length === 0) return []

    // 按天分组
    const dayGroups = this._groupByDay(schedules)
    
    // 为每一天生成时间轴
    return Object.entries(dayGroups)
      .sort(([a], [b]) => parseInt(a) - parseInt(b))
      .map(([dayNumber, spots]) => {
        return {
          day: parseInt(dayNumber),
          title: `第${dayNumber}天`,
          theme: this._generateDayTheme(spots),
          activities: this._convertDayActivities(spots, timeSlotDuration)
        }
      })
  }

  /**
   * 按天分组
   */
  static _groupByDay(schedules) {
    return schedules.reduce((groups, schedule) => {
      const day = schedule.day_number || 1
      if (!groups[day]) groups[day] = []
      groups[day].push(schedule)
      return groups
    }, {})
  }

  /**
   * 生成当天主题
   */
  static _generateDayTheme(spots) {
    if (spots.length === 0) return '精彩一天'
    
    // 根据景点类型生成主题
    const spotNames = spots.map(s => s.spot_name || '').join('')
    
    const themes = [
      { pattern: /故宫|博物馆|古迹/, theme: '文化探索' },
      { pattern: /山|湖|海|公园|自然/, theme: '自然风光' },
      { pattern: /街|巷|城|古镇/, theme: '城市漫步' },
      { pattern: /寺|庙|塔/, theme: '人文古迹' },
      { pattern: /美食|街|小吃/, theme: '美食之旅' }
    ]
    
    for (const { pattern, theme } of themes) {
      if (pattern.test(spotNames)) return theme
    }
    
    return '精彩一天'
  }

  /**
   * 转换一天的活动列表
   * 核心：为每个景点分配合理的时间段
   */
  static _convertDayActivities(spots, timeSlotDuration) {
    // 按 order_index 排序
    const sortedSpots = [...spots].sort((a, b) => 
      (a.order_index || 0) - (b.order_index || 0)
    )

    let currentTime = 9 * 60  // 从早上9点开始（分钟）
    const activities = []

    sortedSpots.forEach((spot, index) => {
      // 如果有预设时间，使用预设时间
      let timeStr
      if (spot.visit_time_start) {
        timeStr = spot.visit_time_start.substring(0, 5) // HH:MM
        const [h, m] = timeStr.split(':').map(Number)
        currentTime = h * 60 + m
      } else {
        // 自动生成时间
        timeStr = this._minutesToTime(currentTime)
      }

      // 计算结束时间
      const duration = spot.duration 
        ? this._parseDuration(spot.duration) 
        : timeSlotDuration * 60
      const endTime = currentTime + duration

      // 生成活动描述
      const activity = {
        time: timeStr,
        title: `游览${spot.spot_name}`,
        location: spot.spot_name,
        spot_id: spot.spot_id,
        duration: this._formatDuration(duration),
        // 额外信息
        insight: spot.notes || this._generateSpotInsight(spot),
        image: spot.spot_image,
        start_time: timeStr,
        end_time: this._minutesToTime(endTime)
      }

      activities.push(activity)

      // 下一个景点的开始时间（加30分钟过渡时间）
      currentTime = endTime + 30
    })

    return activities
  }

  /**
   * 分钟数转时间字符串
   */
  static _minutesToTime(minutes) {
    const h = Math.floor(minutes / 60)
    const m = minutes % 60
    return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}`
  }

  /**
   * 解析时长字符串
   */
  static _parseDuration(durationStr) {
    if (!durationStr) return 120  // 默认2小时
    
    const match = durationStr.match(/(\d+)/)
    if (match) {
      const num = parseInt(match[1])
      // 如果是"2小时"格式，返回分钟
      if (durationStr.includes('小时')) return num * 60
      // 如果是"30分钟"格式
      if (durationStr.includes('分钟')) return num
      // 纯数字，假设是小时
      return num * 60
    }
    return 120
  }

  /**
   * 格式化时长显示
   */
  static _formatDuration(minutes) {
    const h = Math.floor(minutes / 60)
    const m = minutes % 60
    if (h > 0 && m > 0) return `${h}小时${m}分钟`
    if (h > 0) return `${h}小时`
    return `${m}分钟`
  }

  /**
   * 生成景点洞察
   */
  static _generateSpotInsight(spot) {
    const insights = [
      '值得一去的景点',
      '记得带上相机',
      '建议提前购票',
      '人流量较大，注意时间',
      '当地特色景点'
    ]
    // 根据 spot_id 或 name 生成固定的洞察
    const index = (spot.spot_id || 0) % insights.length
    return insights[index]
  }

  /**
   * 提取图片
   */
  static _extractImages(schedules) {
    const images = []
    schedules?.forEach(s => {
      if (s.spot_image && !images.includes(s.spot_image)) {
        images.push(s.spot_image)
      }
    })
    return images.slice(0, 9) // 最多9张
  }

  /**
   * 生成日记正文
   */
  static _generateContent(trip, timeline) {
    const lines = []
    lines.push(`# ${trip.title || trip.destination}游记`)
    lines.push('')
    lines.push(`📍 目的地：${trip.destination || '未知'}`)
    lines.push(`📅 天数：${trip.total_days || 1}天`)
    lines.push(`⏰ 记录时间：${new Date().toLocaleString()}`)
    lines.push('')
    lines.push('---')
    lines.push('')

    timeline.forEach(day => {
      lines.push(`## ${day.title}：${day.theme}`)
      lines.push('')
      
      day.activities.forEach((act, idx) => {
        lines.push(`${idx + 1}. **${act.time}** ${act.title}`)
        if (act.insight) lines.push(`   💡 ${act.insight}`)
        lines.push('')
      })
    })

    lines.push('---')
    lines.push('')
    lines.push('✨ 这次旅行留下了美好的回忆...')

    return lines.join('\n')
  }
}
