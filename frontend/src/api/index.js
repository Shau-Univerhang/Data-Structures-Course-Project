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
  }
}

export default API
