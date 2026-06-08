// 前端API配置
const API_BASE_URL = 'http://localhost:8000'

async function fetchJSON(url, options = {}) {
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers
    }
  })
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`)
  }
  return response.json()
}

export const API = {
  // 景点相关
  spots: {
    list: (params = {}) => {
      const query = new URLSearchParams(params).toString()
      return fetchJSON(`${API_BASE_URL}/api/spots${query ? '?' + query : ''}`)
    },
    search: (q, city) => fetchJSON(`${API_BASE_URL}/api/spots/search?q=${encodeURIComponent(q || '')}&city=${encodeURIComponent(city || '')}`),
    get: (id) => fetchJSON(`${API_BASE_URL}/api/spots/${id}`),
    getNearbyRestaurants: (params = {}) => {
      const query = new URLSearchParams(params).toString()
      return fetchJSON(`${API_BASE_URL}/api/spots/restaurants/nearby${query ? '?' + query : ''}`)
    },
  },
  
  // 行程相关
  trips: {
    create: (data) => fetchJSON(`${API_BASE_URL}/api/trips`, {
      method: 'POST',
      body: JSON.stringify({...data, user_id: 1})
    }),
    list: (userId = 1) => fetchJSON(`${API_BASE_URL}/api/trips?user_id=${userId}`),
    get: (id) => fetchJSON(`${API_BASE_URL}/api/trips/${id}`),
  },
  
  // 路线规划
  route: {
    plan: (data) => fetchJSON(`${API_BASE_URL}/api/route/plan`, {
      method: 'POST',
      body: JSON.stringify(data)
    }),
  },
  
  // AI接口
  ai: {
    generateGuide: (data) => fetchJSON(`${API_BASE_URL}/api/ai/generate`, {
      method: 'POST',
      body: JSON.stringify(data)
    }),
    chat: (message) => fetchJSON(`${API_BASE_URL}/api/ai/chat?message=${encodeURIComponent(message)}`),
    tourGuide: (spotId, style = 'rational') => fetchJSON(`${API_BASE_URL}/api/ai/tour-guide`, {
      method: 'POST',
      body: JSON.stringify({ spot_id: spotId, style })
    }),
    getTourGuide: (spotId) => fetchJSON(`${API_BASE_URL}/api/ai/tour-guide/${spotId}`),
    vlogGenerate: (tripId, userId = 1) => fetchJSON(`${API_BASE_URL}/api/ai/vlog/generate`, {
      method: 'POST',
      body: JSON.stringify({ trip_id: tripId, user_id: userId })
    }),
    vlogStatus: (taskId) => fetchJSON(`${API_BASE_URL}/api/ai/vlog/status/${taskId}`),
  },
  
  // 日记
  diary: {
    list: (params = {}) => {
      const query = new URLSearchParams(params).toString()
      return fetchJSON(`${API_BASE_URL}/api/diaries${query ? '?' + query : ''}`)
    },
    create: (data) => fetchJSON(`${API_BASE_URL}/api/diaries`, {
      method: 'POST',
      body: JSON.stringify({...data, user_id: 1})
    }),
    uploadVideo: async (file, userId = 1) => {
      const formData = new FormData()
      formData.append('file', file)
      const response = await fetch(`${API_BASE_URL}/api/diaries/upload-video?user_id=${userId}`, {
        method: 'POST',
        body: formData
      })
      if (!response.ok) throw new Error(`HTTP ${response.status}`)
      return response.json()
    },
    analyzeVideo: async (videoUrl) => {
      const formData = new FormData()
      formData.append('video_url', videoUrl)
      const response = await fetch(`${API_BASE_URL}/api/diary-generator/analyze-video`, {
        method: 'POST',
        body: formData
      })
      if (!response.ok) throw new Error(`HTTP ${response.status}`)
      return response.json()
    },
  },
  
  // 认证
  auth: {
    register: (data) => fetchJSON(`${API_BASE_URL}/api/auth/register`, {
      method: 'POST',
      body: JSON.stringify(data)
    }),
    login: (data) => fetchJSON(`${API_BASE_URL}/api/auth/login`, {
      method: 'POST',
      body: JSON.stringify(data)
    }),
    getUser: (userId) => fetchJSON(`${API_BASE_URL}/api/auth/me?user_id=${userId}`),
    updateProfile: (userId, data) => fetchJSON(`${API_BASE_URL}/api/auth/profile?user_id=${userId}`, {
      method: 'PUT',
      body: JSON.stringify(data)
    }),
  },
  
  // 收藏
  collections: {
    list: (userId) => fetchJSON(`${API_BASE_URL}/api/collections?user_id=${userId}`),
    add: (userId, spotId) => fetchJSON(`${API_BASE_URL}/api/collections?user_id=${userId}`, {
      method: 'POST',
      body: JSON.stringify({ spot_id: spotId })
    }),
    remove: (userId, spotId) => {
      return fetch(`${API_BASE_URL}/api/collections/${spotId}?user_id=${userId}`, {
        method: 'DELETE'
      })
    },
    check: (userId, spotId) => fetchJSON(`${API_BASE_URL}/api/collections/check/${spotId}?user_id=${userId}`),
  },
  
  // 照片
  photos: {
    list: (userId) => fetchJSON(`${API_BASE_URL}/api/photos?user_id=${userId}`),
    getByTrip: (userId, tripId) => fetchJSON(`${API_BASE_URL}/api/photos/by-trip/${tripId}?user_id=${userId}`),
  },

  // 旅行人格测试
  personality: {
    getQuestions: () => fetchJSON(`${API_BASE_URL}/api/personality/questions`),
    submitTest: (answers) => fetchJSON(`${API_BASE_URL}/api/personality/test`, {
      method: 'POST',
      body: JSON.stringify({ answers })
    }),
    saveResult: (answers, userId) => fetchJSON(`${API_BASE_URL}/api/personality/save`, {
      method: 'POST',
      body: JSON.stringify({ answers, user_id: userId })
    }),
    getMyResult: (userId) => fetchJSON(`${API_BASE_URL}/api/personality/my?user_id=${userId}`),
    getAllTypes: () => fetchJSON(`${API_BASE_URL}/api/personality/types`),
    getTypeDetail: (typeCode) => fetchJSON(`${API_BASE_URL}/api/personality/types/${typeCode}`),
    deleteResult: (userId) => fetch(`${API_BASE_URL}/api/personality/my?user_id=${userId}`, {
      method: 'DELETE'
    }),
  }
}

export default API
