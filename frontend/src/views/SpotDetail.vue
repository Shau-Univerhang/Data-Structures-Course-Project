<template>
  <div class="spot-page">
    <!-- 顶部导航 -->
    <header class="page-header">
      <button class="back-btn" @click="goBack">←</button>
      <h1 class="page-title">{{ spot.name }}</h1>
      <button class="share-btn">分享</button>
    </header>

    <!-- 景点图片 -->
    <section class="spot-hero">
      <img :src="spot.image || defaultImage" :alt="spot.name" class="hero-image" />
      <div class="hero-overlay">
        <div class="rating-badge">
          <span class="heart">♥</span>
          <span class="rating-value">{{ spot.rating }}</span>
        </div>
      </div>
    </section>

    <!-- 景点基本信息 -->
    <section class="spot-info">
      <h2 class="spot-name">{{ spot.name }}</h2>
      <div class="spot-meta">
        <span class="meta-item">📍 {{ spot.city }}</span>
        <span class="meta-item">🏷️ {{ spot.category }}</span>
      </div>
      <p class="spot-desc">{{ spot.description }}</p>
      
      <div class="spot-tags">
        <span v-for="tag in (spot.tags || [])" :key="tag" class="tag">{{ tag }}</span>
      </div>

      <div class="spot-details">
        <div class="detail-item">
          <span class="detail-label">开放时间</span>
          <span class="detail-value">{{ spot.open_time || '全天' }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">门票</span>
          <span class="detail-value">{{ spot.ticket_price || '免费' }}</span>
        </div>
      </div>
    </section>

    <!-- 用户评价 -->
    <section class="reviews-section">
      <div class="section-header">
        <h3>用户评价</h3>
        <span class="review-count">{{ reviews.length }}条评价</span>
      </div>
      <div class="reviews-list">
        <div v-for="review in reviews" :key="review.id" class="review-card">
          <div class="review-header">
            <div class="review-avatar">{{ review.user[0] }}</div>
            <div class="review-info">
              <span class="review-user">{{ review.user }}</span>
              <span class="review-date">{{ review.date }}</span>
            </div>
            <div class="review-rating">
              <span v-for="i in 5" :key="i" :class="['star', { filled: i <= review.rating }]">★</span>
            </div>
          </div>
          <p class="review-content">{{ review.content }}</p>
          <div class="review-images" v-if="review.images?.length">
            <img v-for="(img, idx) in review.images" :key="idx" :src="img" />
          </div>
        </div>
      </div>
    </section>

    <!-- 拍照点位 -->
    <section class="photo-spots-section">
      <div class="section-header">
        <h3>拍照点位</h3>
        <button class="add-btn" @click="showAddPhoto = true">+ 上传</button>
      </div>
      <div class="photo-spots-grid">
        <div v-for="ps in photoSpots" :key="ps.id" class="photo-spot-card">
          <img :src="ps.image" :alt="ps.name" />
          <div class="photo-info">
            <h4>{{ ps.name }}</h4>
            <p>{{ ps.description }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- 添加到行程 -->
    <section class="add-to-trip">
      <button class="collect-btn" :class="{ collected: isCollected }" @click="toggleCollect">
        <span>{{ isCollected ? '❤️' : '🤍' }}</span>
        {{ isCollected ? '已收藏' : '收藏' }}
      </button>
      <button class="add-trip-btn" @click="showTripSelector = true">
        <span>➕</span> 添加到行程
      </button>
    </section>

    <!-- 行程选择弹窗 -->
    <div v-if="showTripSelector" class="modal-overlay" @click.self="showTripSelector = false">
      <div class="modal-content">
        <h3>添加到行程</h3>
        <div class="trips-list">
          <div 
            v-for="trip in userTrips" 
            :key="trip.id"
            class="trip-option"
            @click="addToTrip(trip.id)"
          >
            <span class="trip-name">{{ trip.title }}</span>
            <span class="trip-days">{{ trip.days }}天</span>
          </div>
        </div>
        <button class="new-trip-btn" @click="createNewTrip">+ 创建新行程</button>
      </div>
    </div>

    <!-- 上传拍照点位弹窗 -->
    <div v-if="showAddPhoto" class="modal-overlay" @click.self="showAddPhoto = false">
      <div class="modal-content">
        <h3>上传拍照点位</h3>
        <input type="text" class="tech-input" placeholder="点位名称" v-model="newPhoto.name" />
        <textarea class="tech-input" placeholder="点位描述" v-model="newPhoto.description"></textarea>
        <input type="file" class="tech-input" @change="handlePhotoUpload" accept="image/*" />
        <div class="modal-actions">
          <button class="btn-cancel" @click="showAddPhoto = false">取消</button>
          <button class="btn-confirm" @click="submitPhoto">提交</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const spot = ref({})
const reviews = ref([])
const photoSpots = ref([])
const showTripSelector = ref(false)
const showAddPhoto = ref(false)
const isCollected = ref(false)
const userTrips = ref([
  { id: 1, title: '北京三日游', days: 3 },
  { id: 2, title: '上海周末游', days: 2 }
])
const newPhoto = ref({ name: '', description: '', image: '' })
const defaultImage = 'https://images.unsplash.com/photo-1599571234909-29ed5d1321d6?w=800'

onMounted(async () => {
  const spotId = route.query.id
  await loadSpot(spotId)
})

const loadSpot = async (id) => {
  try {
    const response = await fetch(`http://localhost:8000/api/spots/${id}`)
    const data = await response.json()
    spot.value = { ...data, image: data.images?.[0] || defaultImage }
    
    // 检查是否已收藏
    const userId = localStorage.getItem('userId')
    if (userId) {
      const checkRes = await fetch(`http://localhost:8000/api/collections/check/${id}?user_id=${userId}`)
      if (checkRes.ok) {
        const checkData = await checkRes.json()
        isCollected.value = checkData.is_collected
      }
    }
  } catch (error) {
    spot.value = {
      id: id,
      name: '景点详情',
      city: route.query.city || '北京',
      rating: 4.8,
      category: '历史古迹',
      description: '景点描述加载中...',
      tags: ['必玩景点'],
      open_time: '08:00-18:00',
      ticket_price: '¥60'
    }
  }
  
  // 加载评价和拍照点位（模拟数据）
  reviews.value = [
    { id: 1, user: '张三', date: '2024-01-15', rating: 5, content: '非常棒的景点，建筑宏伟，值得一去！', images: [] },
    { id: 2, user: '李四', date: '2024-01-10', rating: 4, content: '风景很美，就是人太多了', images: [] },
  ]
  
  photoSpots.value = [
    { id: 1, name: '最佳拍摄点1', description: '可以拍到全景', image: 'https://images.unsplash.com/photo-1599571234909-29ed5d1321d6?w=300' },
    { id: 2, name: '最佳拍摄点2', description: '人少出片', image: 'https://images.unsplash.com/photo-1599571234909-29ed5d1321d6?w=300' },
  ]
}

const goBack = () => router.back()

const addToTrip = (tripId) => {
  showTripSelector.value = false
  alert(`已添加到行程 #${tripId}`)
}

const toggleCollect = async () => {
  const userId = localStorage.getItem('userId')
  if (!userId) {
    router.push('/login')
    return
  }
  
  try {
    if (isCollected.value) {
      // 取消收藏
      const response = await fetch(`http://localhost:8000/api/collections/${spot.value.id}?user_id=${userId}`, {
        method: 'DELETE'
      })
      if (response.ok) {
        isCollected.value = false
      }
    } else {
      // 添加收藏
      const response = await fetch(`http://localhost:8000/api/collections?user_id=${userId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ spot_id: spot.value.id })
      })
      if (response.ok) {
        isCollected.value = true
      }
    }
  } catch (error) {
    console.error('操作失败:', error)
  }
}

const createNewTrip = () => {
  showTripSelector.value = false
  router.push({ path: '/create-trip', query: { addSpot: spot.value.id } })
}

const handlePhotoUpload = (e) => {
  const file = e.target.files[0]
  if (file) {
    newPhoto.value.image = URL.createObjectURL(file)
  }
}

const submitPhoto = () => {
  if (newPhoto.value.name && newPhoto.value.image) {
    photoSpots.value.unshift({
      id: Date.now(),
      ...newPhoto.value
    })
    showAddPhoto.value = false
    newPhoto.value = { name: '', description: '', image: '' }
    alert('拍照点位已上传！')
  }
}
</script>

<style scoped>
.spot-page {
  min-height: 100vh;
  background: #0a0a1a;
  color: #fff;
  padding-bottom: 100px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 15px 20px;
  background: rgba(10, 10, 26, 0.9);
  backdrop-filter: blur(10px);
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
}

.back-btn, .share-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 1px solid rgba(0, 212, 255, 0.3);
  background: transparent;
  color: #fff;
  font-size: 18px;
  cursor: pointer;
}

.spot-hero {
  position: relative;
  height: 300px;
}

.hero-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.hero-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(transparent, #0a0a1a);
}

.rating-badge {
  position: absolute;
  bottom: 20px;
  right: 20px;
  background: rgba(0, 0, 0, 0.6);
  padding: 8px 16px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.heart { color: #ff6b6b; }
.rating-value { font-size: 16px; font-weight: 600; }

.spot-info {
  padding: 20px;
}

.spot-name {
  font-size: 28px;
  margin-bottom: 10px;
}

.spot-meta {
  display: flex;
  gap: 20px;
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 15px;
}

.spot-desc {
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.6;
  margin-bottom: 15px;
}

.spot-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 20px;
}

.tag {
  padding: 6px 14px;
  background: rgba(0, 212, 255, 0.1);
  border-radius: 15px;
  font-size: 13px;
  color: #00d4ff;
}

.spot-details {
  display: flex;
  gap: 30px;
  padding: 15px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.detail-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

.detail-value {
  font-size: 15px;
  color: #00d4ff;
}

/* 评价 */
.reviews-section, .photo-spots-section {
  padding: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.section-header h3 {
  font-size: 18px;
}

.review-count, .add-btn {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
}

.add-btn {
  background: none;
  border: 1px solid #00d4ff;
  color: #00d4ff;
  padding: 6px 14px;
  border-radius: 15px;
  cursor: pointer;
}

.review-card {
  background: rgba(20, 20, 40, 0.8);
  border-radius: 12px;
  padding: 15px;
  margin-bottom: 15px;
}

.review-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
}

.review-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
}

.review-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.review-user { font-size: 14px; }
.review-date { font-size: 12px; color: rgba(255, 255, 255, 0.5); }

.review-rating .star {
  color: rgba(255, 255, 255, 0.2);
}
.review-rating .star.filled { color: #ffd700; }

.review-content {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.5;
}

/* 拍照点位 */
.photo-spots-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
}

.photo-spot-card {
  background: rgba(20, 20, 40, 0.8);
  border-radius: 12px;
  overflow: hidden;
}

.photo-spot-card img {
  width: 100%;
  height: 120px;
  object-fit: cover;
}

.photo-info {
  padding: 10px;
}

.photo-info h4 { font-size: 14px; margin-bottom: 4px; }
.photo-info p { font-size: 12px; color: rgba(255, 255, 255, 0.5); }

/* 添加到行程按钮 */
.add-to-trip {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 20px;
  background: rgba(10, 10, 26, 0.9);
  backdrop-filter: blur(10px);
  display: flex;
  gap: 15px;
}

.collect-btn {
  flex: 0 0 auto;
  padding: 14px 20px;
  border-radius: 25px;
  border: 1px solid var(--border-color);
  background: transparent;
  color: #fff;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.collect-btn.collected {
  border-color: #ff6b6b;
  background: rgba(255, 107, 107, 0.1);
  color: #ff6b6b;
}

.add-trip-btn {
  width: 100%;
  padding: 16px;
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  border: none;
  border-radius: 30px;
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

/* 弹窗 */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: #1a1a2e;
  border: 1px solid rgba(0, 212, 255, 0.2);
  border-radius: 20px;
  padding: 25px;
  width: 90%;
  max-width: 400px;
}

.modal-content h3 {
  margin-bottom: 20px;
}

.tech-input {
  width: 100%;
  padding: 12px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(0, 212, 255, 0.2);
  border-radius: 10px;
  color: #fff;
  margin-bottom: 15px;
}

.tech-input::placeholder { color: rgba(255, 255, 255, 0.3); }

textarea.tech-input {
  min-height: 80px;
  resize: vertical;
}

.trips-list {
  max-height: 200px;
  overflow-y: auto;
}

.trip-option {
  display: flex;
  justify-content: space-between;
  padding: 15px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  margin-bottom: 10px;
  cursor: pointer;
}

.trip-option:hover { background: rgba(0, 212, 255, 0.1); }

.trip-name { font-size: 15px; }
.trip-days { font-size: 13px; color: rgba(255, 255, 255, 0.5); }

.new-trip-btn {
  width: 100%;
  padding: 12px;
  background: transparent;
  border: 1px dashed #00d4ff;
  border-radius: 10px;
  color: #00d4ff;
  cursor: pointer;
}

.modal-actions {
  display: flex;
  gap: 15px;
  margin-top: 15px;
}

.btn-cancel, .btn-confirm {
  flex: 1;
  padding: 12px;
  border-radius: 10px;
  cursor: pointer;
}

.btn-cancel {
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #fff;
}

.btn-confirm {
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  border: none;
  color: #fff;
}
</style>
