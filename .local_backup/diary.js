import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

const API_BASE_URL = 'http://localhost:8000'

export const useDiaryStore = defineStore('diary', () => {
  // State
  const currentUser = ref(null)
  const diaryList = ref([])
  const diaryStats = ref({
    total: 0,
    byType: { travel: 0, food: 0, photo: 0, notes: 0 }
  })
  const loading = ref(false)

  // Getters
  const hasDiaries = computed(() => diaryList.value.length > 0)
  const diaryCount = computed(() => diaryList.value.length)
  
  const diaryCountByType = computed(() => (type) => {
    return diaryList.value.filter(d => d.diary_type === type).length
  })

  // Actions
  // 从 localStorage 加载用户
  const loadUserFromStorage = () => {
    const userId = localStorage.getItem('userId')
    const username = localStorage.getItem('username')
    if (userId && username) {
      currentUser.value = {
        id: parseInt(userId),
        username: username,
        avatar_url: localStorage.getItem('avatar_url') || ''
      }
      return true
    }
    return false
  }

  // 设置当前用户并保存到 localStorage
  const setCurrentUser = (user) => {
    currentUser.value = user
    localStorage.setItem('userId', user.id)
    localStorage.setItem('username', user.username)
    if (user.avatar_url) {
      localStorage.setItem('avatar_url', user.avatar_url)
    }
  }

  // 清空数据（退出登录）
  const clearData = () => {
    currentUser.value = null
    diaryList.value = []
    diaryStats.value = { total: 0, byType: { travel: 0, food: 0, photo: 0, notes: 0 } }
    localStorage.removeItem('userId')
    localStorage.removeItem('username')
    localStorage.removeItem('avatar_url')
  }

  // 从服务器获取日记列表
  const fetchDiaries = async () => {
    if (!currentUser.value?.id) {
      console.warn('No current user, cannot fetch diaries')
      return
    }

    loading.value = true
    try {
      const response = await fetch(`${API_BASE_URL}/api/diaries?user_id=${currentUser.value.id}`)
      if (response.ok) {
        const data = await response.json()
        diaryList.value = data
        
        // 更新统计
        diaryStats.value = {
          total: data.length,
          byType: {
            travel: data.filter(d => d.diary_type === 'travel').length,
            food: data.filter(d => d.diary_type === 'food').length,
            photo: data.filter(d => d.diary_type === 'photo').length,
            notes: data.filter(d => d.diary_type === 'notes').length
          }
        }
      } else {
        console.error('Failed to fetch diaries:', response.status)
      }
    } catch (error) {
      console.error('Error fetching diaries:', error)
    } finally {
      loading.value = false
    }
  }

  // 创建新日记
  const createDiary = async (diaryData) => {
    if (!currentUser.value?.id) {
      throw new Error('User not logged in')
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/diaries?user_id=${currentUser.value.id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: diaryData.title,
          content: diaryData.content,
          diary_type: diaryData.diary_type || 'notes',
          is_public: diaryData.is_public || false,
          images: diaryData.images || [],
          budget: diaryData.budget,
          companion: diaryData.companion
        })
      })

      if (response.ok) {
        const newDiary = await response.json()
        addDiary(newDiary)
        return newDiary
      } else {
        const error = await response.json()
        throw new Error(error.detail || 'Failed to create diary')
      }
    } catch (error) {
      console.error('Error creating diary:', error)
      throw error
    }
  }

  // 添加日记到列表（本地）
  const addDiary = (diary) => {
    diaryList.value.unshift(diary)
    diaryStats.value.total++
    if (diary.diary_type) {
      diaryStats.value.byType[diary.diary_type] = (diaryStats.value.byType[diary.diary_type] || 0) + 1
    }
  }

  // 更新日记（调用后端API）
  const updateDiary = async (id, data) => {
    if (!currentUser.value?.id) {
      throw new Error('User not logged in')
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/diaries/${id}?user_id=${currentUser.value.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      })

      if (response.ok) {
        const updatedDiary = await response.json()
        // 更新本地数据
        const index = diaryList.value.findIndex(d => d.id === id)
        if (index !== -1) {
          diaryList.value[index] = { ...diaryList.value[index], ...updatedDiary }
        }
        return updatedDiary
      } else {
        const error = await response.json()
        throw new Error(error.detail || 'Failed to update diary')
      }
    } catch (error) {
      console.error('Error updating diary:', error)
      throw error
    }
  }

  // 删除日记（本地）
  const removeDiary = (id) => {
    const diary = diaryList.value.find(d => d.id === id)
    if (diary) {
      diaryList.value = diaryList.value.filter(d => d.id !== id)
      diaryStats.value.total--
      if (diary.diary_type) {
        diaryStats.value.byType[diary.diary_type] = Math.max(0, (diaryStats.value.byType[diary.diary_type] || 0) - 1)
      }
    }
  }

  // 删除日记（调用后端API）
  const deleteDiary = async (id) => {
    if (!currentUser.value?.id) {
      throw new Error('User not logged in')
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/diaries/${id}?user_id=${currentUser.value.id}`, {
        method: 'DELETE'
      })

      if (response.ok) {
        removeDiary(id)
        return true
      } else {
        const error = await response.json()
        throw new Error(error.detail || 'Failed to delete diary')
      }
    } catch (error) {
      console.error('Error deleting diary:', error)
      throw error
    }
  }

  // 获取日记详情
  const getDiaryById = async (id) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/diaries/${id}`)
      if (response.ok) {
        return await response.json()
      }
    } catch (error) {
      console.error('Error fetching diary:', error)
    }
    return null
  }

  return {
    // State
    currentUser,
    diaryList,
    diaryStats,
    loading,
    // Getters
    hasDiaries,
    diaryCount,
    diaryCountByType,
    // Actions
    loadUserFromStorage,
    setCurrentUser,
    clearData,
    fetchDiaries,
    createDiary,
    addDiary,
    updateDiary,
    removeDiary,
    deleteDiary,
    getDiaryById
  }
})
