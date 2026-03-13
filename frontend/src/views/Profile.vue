<template>
  <div class="profile-page">
    <header class="page-header">
      <button class="back-btn" @click="goBack">←</button>
      <h1 class="page-title">我的</h1>
      <div style="width: 40px;"></div>
    </header>

    <!-- 用户信息 -->
    <section class="user-section">
      <div class="user-avatar">
        <img v-if="user.avatar_url" :src="user.avatar_url" alt="头像" />
        <span v-else>{{ user.username?.charAt(0) || '游' }}</span>
      </div>
      <div class="user-info">
        <h3>{{ user.username || '旅行者' }}</h3>
        <p>ID: {{ user.id || '-' }}</p>
      </div>
    </section>

    <!-- 统计 -->
    <section class="stats-section">
      <div class="stat-item">
        <span class="stat-value">{{ stats.trips }}</span>
        <span class="stat-label">行程</span>
      </div>
      <div class="stat-item">
        <span class="stat-value">{{ stats.spots }}</span>
        <span class="stat-label">景点</span>
      </div>
      <div class="stat-item">
        <span class="stat-value">{{ stats.diaries }}</span>
        <span class="stat-label">日记</span>
      </div>
      <div class="stat-item">
        <span class="stat-value">{{ stats.photos }}</span>
        <span class="stat-label">照片</span>
      </div>
    </section>

    <!-- 功能列表 -->
    <section class="menu-section">
      <div class="menu-item" @click="goTrips">
        <span class="menu-icon">🗺️</span>
        <span class="menu-text">我的行程</span>
        <span class="menu-arrow">›</span>
      </div>
      <div class="menu-item" @click="goDiary">
        <span class="menu-icon">📝</span>
        <span class="menu-text">我的日记</span>
        <span class="menu-arrow">›</span>
      </div>
      <div class="menu-item" @click="goCollection">
        <span class="menu-icon">❤️</span>
        <span class="menu-text">我的收藏</span>
        <span class="menu-arrow">›</span>
      </div>
      <div class="menu-item" @click="goPhotos">
        <span class="menu-icon">🖼️</span>
        <span class="menu-text">我的照片</span>
        <span class="menu-arrow">›</span>
      </div>
    </section>

    <section class="menu-section">
      <div class="menu-item" @click="goSettings">
        <span class="menu-icon">⚙️</span>
        <span class="menu-text">设置</span>
        <span class="menu-arrow">›</span>
      </div>
      <div class="menu-item" @click="goAbout">
        <span class="menu-icon">ℹ️</span>
        <span class="menu-text">关于我们</span>
        <span class="menu-arrow">›</span>
      </div>
    </section>

    <footer class="footer">
      <p>邮游世界 v1.0.0</p>
      <p>北京邮电大学 · 数据结构课程设计</p>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const user = ref({
  id: null,
  username: '',
  avatar_url: ''
})

const stats = ref({
  trips: 0,
  spots: 0,
  diaries: 0,
  photos: 0
})

onMounted(() => {
  // 从 localStorage 加载用户信息
  const storedUser = localStorage.getItem('user')
  const userId = localStorage.getItem('userId')
  
  // 如果未登录，跳转到登录页
  if (!storedUser || !userId) {
    router.push('/login')
    return
  }
  
  if (storedUser) {
    const userData = JSON.parse(storedUser)
    user.value = userData
  }
  
  // 加载真实统计数据
  fetchStats()
})

const fetchStats = async () => {
  const userId = localStorage.getItem('userId')
  
  if (!userId) return
  
  try {
    // 获取行程数
    const tripsRes = await fetch(`http://localhost:8000/api/trips?user_id=${userId}`)
    if (tripsRes.ok) {
      const tripsData = await tripsRes.json()
      stats.value.trips = Array.isArray(tripsData) ? tripsData.length : 0
    }
  } catch (e) {
    console.error('获取行程失败:', e)
  }
  
  try {
    // 获取收藏的景点数
    const collRes = await fetch(`http://localhost:8000/api/collections?user_id=${userId}`)
    if (collRes.ok) {
      const collData = await collRes.json()
      stats.value.spots = Array.isArray(collData) ? collData.length : 0
    }
  } catch (e) {
    console.error('获取收藏失败:', e)
  }
  
  try {
    // 获取日记数
    const diaryRes = await fetch(`http://localhost:8000/api/diaries?user_id=${userId}`)
    if (diaryRes.ok) {
      const diaryData = await diaryRes.json()
      stats.value.diaries = Array.isArray(diaryData) ? diaryData.length : 0
    }
  } catch (e) {
    console.error('获取日记失败:', e)
  }
  
  try {
    // 获取照片数
    const photosRes = await fetch(`http://localhost:8000/api/photos?user_id=${userId}`)
    if (photosRes.ok) {
      const photosData = await photosRes.json()
      // photosData 是按行程分组的，需要计算总照片数
      let totalPhotos = 0
      if (Array.isArray(photosData)) {
        photosData.forEach(trip => {
          if (trip.photos && Array.isArray(trip.photos)) {
            totalPhotos += trip.photos.length
          }
        })
      }
      stats.value.photos = totalPhotos
    }
  } catch (e) {
    console.error('获取照片失败:', e)
  }
}

const goBack = () => router.back()
const goTrips = () => router.push('/trips')
const goDiary = () => router.push('/diary')
const goCollection = () => router.push('/collection')
const goPhotos = () => router.push('/photos')
const goSettings = () => router.push('/setting')
const goAbout = () => alert('邮游世界 v1.0.0\n基于MiniMax大模型\n北京邮电大学课程设计')
</script>

<style scoped>
.profile-page {
  min-height: 100vh;
  background: #0a0a1a;
  color: #fff;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 15px 20px;
  background: rgba(10, 10, 26, 0.9);
}

.back-btn, .settings-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 1px solid rgba(0, 212, 255, 0.3);
  background: transparent;
  color: #fff;
  font-size: 18px;
  cursor: pointer;
}

.page-title { font-size: 18px; }

.user-section {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 30px 20px;
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.1), rgba(123, 44, 191, 0.1));
}

.user-avatar {
  width: 70px;
  height: 70px;
  border-radius: 50%;
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  overflow: hidden;
}

.user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-info h3 { font-size: 20px; margin-bottom: 5px; }
.user-info p { font-size: 14px; color: rgba(255, 255, 255, 0.5); }

.stats-section {
  display: flex;
  justify-content: space-around;
  padding: 25px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.stat-item {
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 24px;
  font-weight: 700;
  background: linear-gradient(135deg, #00d4ff, #fff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-label {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
}

.menu-section {
  padding: 10px 20px;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 18px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  cursor: pointer;
}

.menu-icon { font-size: 22px; }
.menu-text { flex: 1; font-size: 16px; }
.menu-arrow { color: rgba(255, 255, 255, 0.3); font-size: 20px; }

.footer {
  text-align: center;
  padding: 40px 20px;
  color: rgba(255, 255, 255, 0.3);
  font-size: 13px;
}

.footer p { margin: 5px 0; }
</style>
