// frontend/src/bridge/tripDiaryBridge.js
// 行程-日记 Bridge：完成行程并自动生成日记

import { useTripStore } from '../stores/trip'
import { useDiaryStore } from '../stores/diary'

const API_BASE_URL = 'http://localhost:8000'

export const useTripDiaryBridge = () => {
  const tripStore = useTripStore()
  const diaryStore = useDiaryStore()

  /**
   * 完成行程并创建日记
   * @param {number} tripId - 行程ID
   * @param {Object} tripData - 行程数据
   * @returns {Promise<{success: boolean, tripId: number, diaryId: number, diary: Object}>}
   */
  const completeTripAndCreateDiary = async (tripId, tripData) => {
    // 1. 检查是否已有日记
    const existing = await checkExistingDiary(tripId)
    if (existing) {
      return {
        success: false,
        error: 'ALREADY_EXISTS',
        diaryId: existing.id,
        message: '该行程已有日记'
      }
    }

    // 2. 更新行程状态为 completed
    try {
      const res = await fetch(
        `${API_BASE_URL}/api/trips/${tripId}/status?status=completed`,
        { method: 'PUT' }
      )
      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}))
        throw new Error(errorData.detail || `状态更新失败: ${res.status}`)
      }
    } catch (error) {
      throw new Error(`无法完成行程: ${error.message}`)
    }

    // 3. 同步更新本地 Store 状态
    _syncTripStatus(tripId, 'completed')

    // 4. 生成日记数据
    const diaryPayload = {
      title: `${tripData.title || tripData.destination} - 游记`,
      content: generateDiaryFromTrip(tripData),
      trip_id: tripId,
      diary_type: 'travel',
      is_public: false,
      images: extractImages(tripData),
      videos: [],
      itinerary: buildItinerary(tripData.schedules),
      budget: null,
      companion: null,
      compress: true
    }

    // 5. 通过 diaryStore 创建日记
    let newDiary = null
    try {
      newDiary = await diaryStore.createDiary(diaryPayload)

      // 验证返回值
      if (!newDiary || !newDiary.id) {
        console.error('日记返回值异常:', newDiary)
        await rollbackTripStatus(tripId)
        throw new Error('日记创建失败：返回值缺少 id 字段')
      }

      console.log('✅ 日记创建成功:', newDiary.id)
    } catch (error) {
      console.error('❌ 日记创建失败，回滚行程状态:', error)
      await rollbackTripStatus(tripId)
      throw error
    }

    return {
      success: true,
      tripId,
      diaryId: newDiary.id,
      diary: newDiary
    }
  }

  /**
   * 检查行程是否已有日记
   * @param {number} tripId
   * @returns {Promise<Object|null>}
   */
  const checkExistingDiary = async (tripId) => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/diaries?trip_id=${tripId}`)
      if (!res.ok) {
        console.warn('检查已有日记时API错误:', res.status)
        return null
      }
      const diaries = await res.json()
      return diaries.length > 0 ? diaries[0] : null
    } catch (error) {
      console.error('检查已有日记失败:', error)
      return null
    }
  }

  /**
   * 回滚行程状态
   * @param {number} tripId
   */
  const rollbackTripStatus = async (tripId) => {
    try {
      await fetch(
        `${API_BASE_URL}/api/trips/${tripId}/status?status=published`,
        { method: 'PUT' }
      )
      _syncTripStatus(tripId, 'published')
      console.log('↩️ 行程状态已回滚为 published')
    } catch (error) {
      console.error('⚠️ 行程状态回滚失败:', error)
    }
  }

  /**
   * 同步本地 Store 中的行程状态
   * @param {number} tripId
   * @param {string} status
   */
  const _syncTripStatus = (tripId, status) => {
    // 更新 currentTrip
    if (tripStore.currentTrip?.id === tripId) {
      tripStore.currentTrip = { ...tripStore.currentTrip, status }
    }
    // 更新 tripList
    const index = tripStore.tripList.findIndex(t => t.id === tripId)
    if (index !== -1) {
      tripStore.tripList[index] = { ...tripStore.tripList[index], status }
    }
  }

  /**
   * 从行程数据生成日记正文
   * @param {Object} tripData
   * @returns {string}
   */
  const generateDiaryFromTrip = (tripData) => {
    if (!tripData) {
      console.warn('tripData 为空')
      return '# 游记\n\n暂无内容'
    }

    const lines = []
    lines.push(`# ${tripData.title || tripData.destination || '未知行程'}游记`)
    lines.push('')
    lines.push(`📍 目的地：${tripData.destination || '未知'}`)
    lines.push(`📅 行程天数：${tripData.total_days || 1}天`)
    lines.push(`⏰ 记录时间：${new Date().toLocaleString()}`)
    lines.push('')
    lines.push('---')
    lines.push('')

    // 按天分组
    const schedules = tripData.schedules || []
    const dayGroups = {}

    schedules.forEach(s => {
      const day = s.day_number || 1
      if (!dayGroups[day]) dayGroups[day] = []
      dayGroups[day].push(s)
    })

    const sortedDays = Object.keys(dayGroups).sort((a, b) => parseInt(a) - parseInt(b))

    if (sortedDays.length === 0) {
      lines.push('（暂无详细行程）')
    } else {
      sortedDays.forEach(day => {
        lines.push(`## 第${day}天`)
        lines.push('')
        dayGroups[day].forEach((s, idx) => {
          lines.push(`${idx + 1}. **${s.spot_name || '未知景点'}**`)
          if (s.notes) lines.push(`   > ${s.notes}`)
          lines.push('')
        })
      })
    }

    lines.push('---')
    lines.push('')
    lines.push('✨ 这次旅行留下了美好的回忆...')

    return lines.join('\n')
  }

  /**
   * 构建日记时间轴数据
   * @param {Array} schedules
   * @returns {Array}
   */
  const buildItinerary = (schedules) => {
    if (!schedules || schedules.length === 0) return []

    const dayGroups = {}
    schedules.forEach(s => {
      const day = s.day_number || 1
      if (!dayGroups[day]) dayGroups[day] = []
      dayGroups[day].push({
        time: s.visit_time_start || '09:00',
        description: `游览${s.spot_name || '景点'}`,
        location: s.spot_name || '未知地点',
        spot_id: s.spot_id
      })
    })

    return Object.entries(dayGroups)
      .sort(([a], [b]) => parseInt(a) - parseInt(b))
      .map(([day, spots]) => ({
        day: parseInt(day),
        title: `第${day}天`,
        spots: spots.sort((a, b) => a.time.localeCompare(b.time))
      }))
  }

  /**
   * 提取行程中的图片
   * @param {Object} tripData
   * @returns {Array<string>}
   */
  const extractImages = (tripData) => {
    const images = []
    const schedules = tripData.schedules || []
    schedules.forEach(s => {
      if (s.spot_image && !images.includes(s.spot_image)) {
        images.push(s.spot_image)
      }
    })
    return images.slice(0, 9)
  }

  return {
    completeTripAndCreateDiary,
    checkExistingDiary,
    generateDiaryFromTrip
  }
}
