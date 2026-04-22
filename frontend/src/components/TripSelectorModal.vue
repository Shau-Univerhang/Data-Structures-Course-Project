<template>
  <div v-if="visible" class="modal-overlay" @click.self="close">
    <div class="modal-content">
      <div class="modal-header">
        <h3>选择行程</h3>
        <button class="close-btn" @click="close">✕</button>
      </div>
      
      <div class="modal-body">
        <!-- 加载状态 -->
        <div v-if="loading" class="loading-state">
          <span>加载中...</span>
        </div>
        
        <!-- 空状态 -->
        <div v-else-if="trips.length === 0" class="empty-state">
          <p>暂无可用行程</p>
          <button class="create-btn" @click="goCreateTrip">创建行程</button>
        </div>
        
        <!-- 行程列表 -->
        <div v-else class="trip-list">
          <div
            v-for="trip in trips"
            :key="trip.id"
            class="trip-item"
            :class="{ 'has-diary': trip.hasDiary }"
            @click="selectTrip(trip)"
          >
            <div class="trip-image" :style="{ backgroundImage: `url(${trip.image})` }">
              <span v-if="trip.hasDiary" class="badge">已有日记</span>
            </div>
            <div class="trip-info">
              <h4>{{ trip.title }}</h4>
              <p>{{ trip.city }} · {{ trip.days }}天</p>
            </div>
            <div class="trip-arrow">→</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  visible: Boolean
})

const emit = defineEmits(['update:visible', 'select'])

const router = useRouter()

const trips = ref([])
const loading = ref(false)

// 加载行程列表
const loadTrips = async () => {
  loading.value = true
  try {
    const userId = localStorage.getItem('userId') || '1'
    const response = await fetch(`http://localhost:8000/api/trips?user_id=${userId}`)
    
    if (response.ok) {
      const data = await response.json()
      // 检查每个行程是否已有日记
      const tripsWithStatus = await Promise.all(
        data.map(async (trip) => {
          const diaryRes = await fetch(`http://localhost:8000/api/diaries?trip_id=${trip.id}`)
          const diaries = diaryRes.ok ? await diaryRes.json() : []
          return {
            ...trip,
            hasDiary: diaries.length > 0,
            city: trip.destination,
            days: trip.total_days,
            image: getCityImage(trip.destination)
          }
        })
      )
      trips.value = tripsWithStatus
    }
  } catch (error) {
    console.error('加载行程失败:', error)
  } finally {
    loading.value = false
  }
}

// 监听可见性
watch(() => props.visible, (newVal) => {
  if (newVal) loadTrips()
})

const close = () => {
  emit('update:visible', false)
}

const selectTrip = (trip) => {
  if (trip.hasDiary) {
    // 已有日记，提示用户
    if (!confirm('该行程已有日记，确定要重新生成吗？')) {
      return
    }
  }
  emit('select', trip)
  close()
}

const goCreateTrip = () => {
  close()
  router.push('/create-trip')
}

const getCityImage = (city) => {
  const cityImages = {
    '北京': '/images/cities/beijing.jpg',
    '上海': '/images/cities/shanghai.jpg',
    '西安': '/images/cities/xian.jpg',
    '成都': '/images/cities/chengdu.jpg',
    '杭州': '/images/cities/hangzhou.jpg',
    '重庆': '/images/cities/chongqing.jpg',
    '广州': '/images/cities/guangzhou.jpg',
    '苏州': '/images/cities/suzhou.jpg',
    '厦门': '/images/cities/xiamen.jpg',
    '三亚': '/images/cities/sanya.jpg',
    '青岛': '/images/cities/qingdao.jpg',
    '南京': '/images/cities/nanjing.jpg',
    '武汉': '/images/cities/wuhan.jpg',
    '长沙': '/images/cities/changsha.jpg',
    '深圳': '/images/cities/shenzhen.jpg',
    '桂林': '/images/cities/guilin.jpg',
    '张家界': '/images/cities/zhangjiajie.jpg',
    '黄山': '/images/cities/huangshan.jpg',
    '九寨沟': '/images/cities/jiuzhaigou.jpg',
    '大理': '/images/cities/dali.jpg',
    '丽江': '/images/cities/lijiang.jpg'
  }
  return cityImages[city] || '/images/cities/beijing.jpg'
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(5px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  width: 100%;
  max-width: 480px;
  max-height: 80vh;
  background: linear-gradient(180deg, #1a1a2e 0%, #0a0a1a 100%);
  border: 1px solid rgba(0, 212, 255, 0.2);
  border-radius: 20px;
  overflow: hidden;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid rgba(0, 212, 255, 0.1);
}

.modal-header h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #fff;
  margin: 0;
}

.close-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 50%;
  color: #fff;
  cursor: pointer;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.modal-body {
  padding: 16px;
  max-height: 60vh;
  overflow-y: auto;
}

.loading-state {
  text-align: center;
  padding: 40px;
  color: rgba(255, 255, 255, 0.6);
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: rgba(255, 255, 255, 0.6);
}

.empty-state p {
  margin-bottom: 20px;
}

.create-btn {
  padding: 12px 24px;
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  border: none;
  border-radius: 25px;
  color: #fff;
  font-size: 0.9375rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.create-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 20px rgba(0, 212, 255, 0.3);
}

.trip-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.trip-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: rgba(20, 20, 40, 0.8);
  border: 1px solid rgba(0, 212, 255, 0.1);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.trip-item:hover {
  border-color: rgba(0, 212, 255, 0.3);
  transform: translateY(-2px);
}

.trip-item.has-diary {
  opacity: 0.6;
}

.trip-image {
  width: 60px;
  height: 60px;
  border-radius: 10px;
  background-size: cover;
  background-position: center;
  position: relative;
  background-color: rgba(255, 255, 255, 0.05);
}

.badge {
  position: absolute;
  bottom: 4px;
  left: 4px;
  right: 4px;
  padding: 2px 6px;
  background: rgba(123, 44, 191, 0.9);
  color: white;
  font-size: 0.625rem;
  text-align: center;
  border-radius: 4px;
}

.trip-info {
  flex: 1;
}

.trip-info h4 {
  font-size: 0.9375rem;
  font-weight: 600;
  color: #fff;
  margin: 0 0 4px 0;
}

.trip-info p {
  font-size: 0.8125rem;
  color: rgba(255, 255, 255, 0.5);
  margin: 0;
}

.trip-arrow {
  color: #00d4ff;
  font-size: 1.25rem;
}
</style>
