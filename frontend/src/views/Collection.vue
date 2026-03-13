<template>
  <div class="collection-page">
    <header class="page-header">
      <button class="back-btn" @click="goBack">←</button>
      <h1 class="page-title">我的收藏</h1>
      <div style="width: 40px;"></div>
    </header>

    <main class="page-content">
      <!-- 收藏列表 -->
      <div v-if="collections.length > 0" class="collection-list">
        <div 
          v-for="spot in collections" 
          :key="spot.id"
          class="collection-card tech-card"
          @click="goToSpot(spot)"
        >
          <div class="spot-image">
            <img v-if="spot.images && spot.images.length" :src="spot.images[0]" :alt="spot.name" />
            <div v-else class="image-placeholder">🏞️</div>
          </div>
          <div class="spot-info">
            <h3>{{ spot.name }}</h3>
            <p class="spot-city">📍 {{ spot.city }}</p>
            <div class="spot-rating">
              <span class="star">⭐</span>
              <span>{{ spot.rating }}</span>
            </div>
          </div>
          <button class="collect-btn collected" @click.stop="removeCollect(spot.id)">
            ❤️
          </button>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-else class="empty-state">
        <span class="empty-icon">💝</span>
        <p>还没有收藏</p>
        <p class="empty-tip">去发现喜欢的景点吧</p>
        <button class="tech-button" @click="goToSpots">发现景点</button>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()

const collections = ref([])

onMounted(() => {
  const userId = localStorage.getItem('userId')
  if (!userId) {
    router.push('/login')
    return
  }
  fetchCollections(userId)
})

const fetchCollections = async (userId) => {
  try {
    const response = await fetch(`http://localhost:8000/api/collections?user_id=${userId}`)
    if (response.ok) {
      collections.value = await response.json()
    }
  } catch (error) {
    console.error('获取收藏失败:', error)
  }
}

const goBack = () => {
  router.back()
}

const goToSpot = (spot) => {
  router.push({ path: '/spot', query: { id: spot.id } })
}

const goToSpots = () => {
  router.push('/spot-recommend')
}

const removeCollect = async (spotId) => {
  const userId = localStorage.getItem('userId')
  if (!userId) return

  try {
    const response = await fetch(`http://localhost:8000/api/collections/${spotId}?user_id=${userId}`, {
      method: 'DELETE'
    })

    if (response.ok) {
      collections.value = collections.value.filter(s => s.id !== spotId)
      ElMessage.success('已取消收藏')
    }
  } catch (error) {
    console.error('取消收藏失败:', error)
  }
}
</script>

<style scoped>
.collection-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #0a0a1a 0%, #1a1a2e 100%);
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 15px 20px;
  background: rgba(10, 10, 26, 0.9);
  backdrop-filter: blur(10px);
  position: sticky;
  top: 0;
  z-index: 100;
}

.back-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 1px solid var(--border-color);
  background: transparent;
  color: #fff;
  font-size: 18px;
  cursor: pointer;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
  color: #fff;
}

.page-content {
  padding: 20px;
  padding-bottom: 80px;
}

.collection-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.collection-card {
  display: flex;
  gap: 15px;
  cursor: pointer;
}

.spot-image {
  width: 100px;
  height: 100px;
  border-radius: 12px;
  overflow: hidden;
  flex-shrink: 0;
}

.spot-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-placeholder {
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.05);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36px;
}

.spot-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.spot-info h3 {
  font-size: 16px;
  font-weight: 600;
  color: #fff;
  margin-bottom: 8px;
}

.spot-city {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 8px;
}

.spot-rating {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #ffd700;
}

.collect-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: none;
  background: rgba(255, 255, 255, 0.1);
  font-size: 20px;
  cursor: pointer;
  align-self: center;
}

.collect-btn.collected {
  background: rgba(255, 107, 107, 0.2);
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  color: rgba(255, 255, 255, 0.5);
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 20px;
}

.empty-tip {
  font-size: 13px;
  opacity: 0.6;
  margin-top: 8px;
  margin-bottom: 25px;
}
</style>
