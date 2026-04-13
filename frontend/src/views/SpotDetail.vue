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
      <div class="hero-overlay"></div>
    </section>

    <!-- 景点基本信息 -->
    <section class="spot-info">
      <h2 class="spot-name">{{ spot.name }}</h2>
      <div class="spot-meta">
        <span class="meta-item">📍 {{ spot.city }}</span>
      </div>
      <p class="spot-desc">{{ spot.description }}</p>
      
      <div class="spot-tags">
        <span v-for="tag in filteredTags" :key="tag" class="tag">{{ tag }}</span>
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
        <div class="header-left">
          <h3>用户评价</h3>
          <span class="review-count">{{ reviews.length }}条评价</span>
          <span class="avg-rating" v-if="spot.rating">平均 {{ spot.rating.toFixed(1) }}分</span>
        </div>
        <button class="add-btn" @click="showAddReview = true" v-if="!hasReviewed && userId">+ 写评价</button>
      </div>
      
      <!-- 评价列表 -->
      <div class="reviews-list" v-if="reviews.length > 0">
        <div v-for="review in reviews" :key="review.id" class="review-card">
          <div class="review-header">
            <div class="review-avatar">{{ review.username?.[0] || '用' }}</div>
            <div class="review-info">
              <span class="review-user">{{ review.username || '用户' }}</span>
              <span class="review-date">{{ formatDate(review.created_at) }}</span>
            </div>
            <div class="review-actions">
              <div class="review-rating">
                <span v-for="i in 5" :key="i" :class="['star', { filled: i <= review.rating }]">★</span>
              </div>
              <button 
                v-if="review.user_id == userId" 
                class="delete-review-btn"
                @click="deleteReview(review.id)"
              >
                删除
              </button>
            </div>
          </div>
          <p class="review-content">{{ review.content }}</p>
          <div class="review-images" v-if="review.images?.length">
            <img v-for="(img, idx) in review.images" :key="idx" :src="img" />
          </div>
        </div>
      </div>
      
      <!-- 空状态 -->
      <div v-else class="empty-reviews">
        <p>暂无评价，快来发表第一条评价吧！</p>
      </div>
    </section>

    <!-- 拍照点位 -->
    <section class="photo-spots-section">
      <div class="section-header">
        <h3>拍照点位</h3>
        <button class="add-btn" @click="showAddPhoto = true">+ 上传</button>
      </div>
      <div class="photo-spots-grid" v-if="photoSpots.length > 0">
        <div v-for="ps in photoSpots" :key="ps.id" class="photo-spot-card">
          <img :src="getFullImageUrl(ps.image)" :alt="ps.name" />
          <div class="photo-info">
            <h4>{{ ps.name }}</h4>
            <p>{{ ps.description }}</p>
          </div>
        </div>
      </div>
      <div v-else class="empty-photo-spots">
        <p>暂无拍照点位，快来上传第一个吧！</p>
      </div>
    </section>

    <!-- 校园/园区导航入口 -->
    <section v-if="hasInternalMap" class="nav-entry-section">
      <button class="nav-entry-btn" @click="goInternalNav">
        <span class="nav-icon">🗺️</span>
        <div class="nav-entry-text">
          <span class="nav-entry-title">{{ internalNavTitle }}</span>
          <span class="nav-entry-sub">{{ internalNavSubtitle }}</span>
        </div>
        <span class="nav-arrow">›</span>
      </button>
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

    <!-- 写评价弹窗 -->
    <div v-if="showAddReview" class="modal-overlay" @click.self="showAddReview = false">
      <div class="modal-content">
        <h3>写评价</h3>
        <div class="rating-input">
          <span class="rating-label">评分：</span>
          <div class="star-input">
            <span 
              v-for="i in 5" 
              :key="i" 
              :class="['star', { filled: i <= newReview.rating }]"
              @click="newReview.rating = i"
            >★</span>
          </div>
          <span class="rating-text">{{ newReview.rating }}分</span>
        </div>
        <textarea class="tech-input" placeholder="分享您的游玩体验..." v-model="newReview.content" rows="4"></textarea>
        <div class="modal-actions">
          <button class="btn-cancel" @click="showAddReview = false">取消</button>
          <button class="btn-confirm" @click="submitReview" :disabled="newReview.rating === 0">提交</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()

const spot = ref({})
const reviews = ref([])
const photoSpots = ref([])
const showTripSelector = ref(false)
const showAddPhoto = ref(false)
const showAddReview = ref(false)
const isCollected = ref(false)
const hasReviewed = ref(false)
const hasInternalMap = ref(false)
const userId = computed(() => localStorage.getItem('userId'))
const internalNavTitle = computed(() => spot.value?.type === 'campus' ? '校园内导航' : '景区内部导航')
const internalNavSubtitle = computed(() => spot.value?.type === 'campus' ? '校园路网 · 多目标路线规划' : '内部路网 · 多目标路线规划')

// 允许的tag列表
const ALLOWED_TAGS = [
  '必玩景点',
  '历史文化',
  '地标建筑',
  '非遗体验',
  '风景名胜',
  '逛吃逛喝',
  '博物展览',
  'citywalk',
  '拍照出片',
  '市井烟火',
  '休闲娱乐'
]

// 过滤后的tags
const filteredTags = computed(() => {
  if (!spot.value.tags || !Array.isArray(spot.value.tags)) return []
  return spot.value.tags.filter(tag => ALLOWED_TAGS.includes(tag))
})

const userTrips = ref([
  { id: 1, title: '北京三日游', days: 3 },
  { id: 2, title: '上海周末游', days: 2 }
])
const newPhoto = ref({ name: '', description: '', image: '' })
const photoFile = ref(null)
const newReview = ref({ rating: 0, content: '' })
const defaultImage = 'https://images.unsplash.com/photo-1599571234909-29ed5d1321d6?w=800'
const API_BASE_URL = 'http://localhost:8000'

// 获取完整图片URL
const getFullImageUrl = (url) => {
  if (!url) return ''
  if (url.startsWith('http')) return url
  return `${API_BASE_URL}${url}`
}

onMounted(async () => {
  const spotId = route.query.id
  if (spotId) {
    await loadSpot(spotId)
    await loadReviews(spotId)
    await checkIfReviewed(spotId)
    await loadPhotoSpots(spotId)
    await checkInternalMap(spotId)
  }
})

const loadSpot = async (id) => {
  try {
    const response = await fetch(`http://localhost:8000/api/spots/${id}`)
    const data = await response.json()
    console.log('[DEBUG] API返回数据:', data)
    console.log('[DEBUG] favorites_count:', data.favorites_count)
    spot.value = { 
      ...data, 
      image: data.images?.[0] || defaultImage,
      rating: data.rating || 0,
      favorites_count: data.favorites_count || 0
    }
    console.log('[DEBUG] spot.value:', spot.value)
    
    // 检查是否已收藏
    if (userId.value) {
      const checkRes = await fetch(`http://localhost:8000/api/collections/check/${id}?user_id=${userId.value}`)
      if (checkRes.ok) {
        const checkData = await checkRes.json()
        isCollected.value = checkData.is_collected
      }
    }
  } catch (error) {
    console.error('加载景点失败:', error)
    spot.value = {
      id: id,
      name: '景点详情',
      city: route.query.city || '北京',
      rating: 0,
      favorites_count: 0,
      category: '历史古迹',
      description: '景点描述加载中...',
      tags: ['必玩景点'],
      open_time: '08:00-18:00',
      ticket_price: '¥60'
    }
  }
  
}

const loadReviews = async (spotId) => {
  try {
    const response = await fetch(`http://localhost:8000/api/collections/spot-reviews/${spotId}`)
    if (response.ok) {
      const data = await response.json()
      console.log('[DEBUG] 加载评价列表:', data)
      reviews.value = data
    }
  } catch (error) {
    console.error('加载评价失败:', error)
    reviews.value = []
  }
}

const checkIfReviewed = async (spotId) => {
  if (!userId.value) return
  try {
    const response = await fetch(`http://localhost:8000/api/collections/spot-reviews/check/${spotId}?user_id=${userId.value}`)
    if (response.ok) {
      const data = await response.json()
      hasReviewed.value = data.has_reviewed
    }
  } catch (error) {
    console.error('检查评价状态失败:', error)
  }
}

const loadPhotoSpots = async (spotId) => {
  try {
    const response = await fetch(`http://localhost:8000/api/photo-spots/${spotId}`)
    if (response.ok) {
      const data = await response.json()
      photoSpots.value = data
    }
  } catch (error) {
    console.error('加载拍照点位失败:', error)
    photoSpots.value = []
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}

const goBack = () => router.back()

const checkInternalMap = async (spotId) => {
  try {
    const res = await fetch(`http://localhost:8000/api/route/nodes/${spotId}`)
    if (res.ok) {
      const data = await res.json()
      hasInternalMap.value = (data.nodes || []).length > 0
    }
  } catch {
    hasInternalMap.value = false
  }
}

const goInternalNav = () => {
  router.push({ path: '/internal-nav', query: { id: spot.value.id } })
}

const addToTrip = (tripId) => {
  showTripSelector.value = false
  alert(`已添加到行程 #${tripId}`)
}

const toggleCollect = async () => {
  if (!userId.value) {
    router.push('/login')
    return
  }
  
  try {
    if (isCollected.value) {
      // 取消收藏
      const response = await fetch(`http://localhost:8000/api/collections/${spot.value.id}?user_id=${userId.value}`, {
        method: 'DELETE'
      })
      if (response.ok) {
        isCollected.value = false
        spot.value.favorites_count = Math.max(0, (spot.value.favorites_count || 0) - 1)
        ElMessage.success('已取消收藏')
      }
    } else {
      // 添加收藏
      const response = await fetch(`http://localhost:8000/api/collections?user_id=${userId.value}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ spot_id: spot.value.id })
      })
      if (response.ok) {
        isCollected.value = true
        spot.value.favorites_count = (spot.value.favorites_count || 0) + 1
        ElMessage.success('收藏成功')
      }
    }
  } catch (error) {
    console.error('操作失败:', error)
    ElMessage.error('操作失败')
  }
}

const submitReview = async () => {
  if (!userId.value) {
    router.push('/login')
    return
  }
  
  if (newReview.value.rating === 0) {
    ElMessage.warning('请选择评分')
    return
  }
  
  try {
    const response = await fetch(`http://localhost:8000/api/collections/spot-reviews?user_id=${userId.value}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        spot_id: spot.value.id,
        rating: newReview.value.rating,
        content: newReview.value.content
      })
    })
    
    if (response.ok) {
      const data = await response.json()
      reviews.value.unshift(data)
      hasReviewed.value = true
      showAddReview.value = false
      newReview.value = { rating: 0, content: '' }
      
      // 更新景点评分
      spot.value.rating = data.new_rating || spot.value.rating
      spot.value.review_count = (spot.value.review_count || 0) + 1
      
      ElMessage.success('评价提交成功')
      
      // 重新加载评价
      await loadReviews(spot.value.id)
    } else {
      const error = await response.json()
      ElMessage.error(error.detail || '评价失败')
    }
  } catch (error) {
    console.error('提交评价失败:', error)
    ElMessage.error('提交失败')
  }
}

const deleteReview = async (reviewId) => {
  if (!confirm('确定要删除这条评价吗？')) return
  
  console.log('[DEBUG] 删除评价 - reviewId:', reviewId, 'userId:', userId.value)
  
  try {
    const url = `http://localhost:8000/api/collections/reviews/delete/${reviewId}?user_id=${userId.value}`
    console.log('[DEBUG] 请求URL:', url)
    
    const response = await fetch(url, {
      method: 'DELETE'
    })
    
    console.log('[DEBUG] 响应状态:', response.status, response.statusText)
    
    if (response.ok) {
      const data = await response.json()
      console.log('[DEBUG] 删除成功:', data)
      ElMessage.success('评价已删除')
      
      // 重新加载评价
      await loadReviews(spot.value.id)
      
      // 更新评价状态
      hasReviewed.value = false
      
      // 重新加载景点信息以更新评分
      await loadSpot(spot.value.id)
    } else {
      const errorText = await response.text()
      console.error('[DEBUG] 删除失败:', response.status, errorText)
      try {
        const error = JSON.parse(errorText)
        ElMessage.error(error.detail || '删除失败')
      } catch {
        ElMessage.error(`删除失败: ${response.status} ${errorText}`)
      }
    }
  } catch (error) {
    console.error('[DEBUG] 删除评价异常:', error)
    ElMessage.error('删除失败: ' + error.message)
  }
}

const createNewTrip = () => {
  showTripSelector.value = false
  router.push({ path: '/create-trip', query: { addSpot: spot.value.id } })
}

const handlePhotoUpload = (e) => {
  const file = e.target.files[0]
  if (file) {
    photoFile.value = file
    newPhoto.value.image = URL.createObjectURL(file)
  }
}

const submitPhoto = async () => {
  if (!userId.value) {
    router.push('/login')
    return
  }
  
  if (newPhoto.value.name && photoFile.value) {
    try {
      const formData = new FormData()
      formData.append('spot_id', spot.value.id)
      formData.append('name', newPhoto.value.name)
      formData.append('description', newPhoto.value.description || '')
      formData.append('image', photoFile.value)
      
      const response = await fetch(`http://localhost:8000/api/photo-spots/?user_id=${userId.value}`, {
        method: 'POST',
        body: formData
      })
      
      if (response.ok) {
        const data = await response.json()
        photoSpots.value.unshift(data)
        showAddPhoto.value = false
        newPhoto.value = { name: '', description: '', image: '' }
        photoFile.value = null
        ElMessage.success('拍照点位已上传！')
      } else {
        const error = await response.json()
        ElMessage.error(error.detail || '上传失败')
      }
    } catch (error) {
      console.error('上传拍照点位失败:', error)
      ElMessage.error('上传失败')
    }
  } else {
    ElMessage.warning('请填写名称并选择图片')
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
  flex-wrap: wrap;
}

.rating-item {
  color: #ffc107;
  font-weight: 500;
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

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.section-header h3 {
  font-size: 18px;
}

.review-count, .avg-rating {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
}

.avg-rating {
  color: #ffc107;
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

.review-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.delete-review-btn {
  background: none;
  border: 1px solid #ff6b6b;
  color: #ff6b6b;
  padding: 4px 10px;
  border-radius: 10px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.3s;
}

.delete-review-btn:hover {
  background: rgba(255, 107, 107, 0.1);
}

.review-content {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.5;
}

.empty-reviews {
  text-align: center;
  padding: 40px;
  color: rgba(255, 255, 255, 0.5);
}

.empty-photo-spots {
  text-align: center;
  padding: 30px;
  color: rgba(255, 255, 255, 0.5);
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  margin-top: 10px;
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
  height: auto;
  max-height: 300px;
  object-fit: contain;
  display: block;
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

/* 校园导航入口 */
.nav-entry-section {
  padding: 15px 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.nav-entry-btn {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px 18px;
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.08), rgba(123, 44, 191, 0.08));
  border: 1px solid rgba(0, 212, 255, 0.25);
  border-radius: 16px;
  color: #fff;
  cursor: pointer;
  transition: all 0.25s;
}

.nav-entry-btn:hover {
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.18), rgba(123, 44, 191, 0.18));
  border-color: rgba(0, 212, 255, 0.5);
}

.nav-icon { font-size: 28px; }

.nav-entry-text {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 3px;
}

.nav-entry-title {
  font-size: 16px;
  font-weight: 600;
  color: #00d4ff;
}

.nav-entry-sub {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

.nav-arrow {
  font-size: 22px;
  color: rgba(0, 212, 255, 0.6);
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

/* 评分输入 */
.rating-input {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
}

.rating-label {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
}

.star-input {
  display: flex;
  gap: 5px;
}

.star-input .star {
  font-size: 24px;
  color: rgba(255, 255, 255, 0.2);
  cursor: pointer;
  transition: color 0.2s;
}

.star-input .star.filled {
  color: #ffd700;
}

.rating-text {
  font-size: 14px;
  color: #ffd700;
  margin-left: 10px;
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

.btn-confirm:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
