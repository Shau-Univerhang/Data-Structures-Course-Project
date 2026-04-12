<template>
  <div class="trips-page">
    <!-- 导航栏 -->
    <Navbar />
    
    <div class="page-content">
      <header class="page-header">
        <h1 class="page-title">我的行程</h1>
        <button class="add-btn" @click="createTrip">+ 创建行程</button>
      </header>

      <section class="trips-list" v-if="trips.length > 0">
        <div 
          v-for="trip in trips" 
          :key="trip.id"
          class="trip-card"
        >
          <div class="trip-content" @click="viewTrip(trip)">
            <div class="trip-image" :style="{backgroundImage: trip.image ? `url(${trip.image})` : 'none'}">
            <div v-if="!trip.image" class="no-image">📷</div>
          </div>
            <div class="trip-info">
              <h3>{{ trip.title }}</h3>
              <p>{{ trip.city }} · {{ trip.days }}天</p>
              <div class="trip-meta">
                <span class="spot-count">{{ trip.spotCount }}个景点</span>
                <span class="trip-date">{{ trip.date }}</span>
              </div>
            </div>
            <div class="trip-status" :class="trip.status">{{ trip.statusText }}</div>
          </div>
          <button class="rename-btn" @click.stop="renameTrip(trip)" title="重命名">
            <span>✏️</span>
          </button>
          <button class="delete-btn" @click.stop="deleteTrip(trip)" title="删除行程">
            <span>🗑️</span>
          </button>
        </div>
      </section>

      <div v-if="trips.length === 0" class="empty-state">
        <span class="empty-icon">🗺️</span>
        <p>还没有行程</p>
        <button class="create-btn" @click="createTrip">创建第一个行程</button>
      </div>
    </div>

    <!-- 删除确认弹窗 -->
    <div v-if="showDeleteModal" class="modal-overlay" @click.self="cancelDelete">
      <div class="modal-content">
        <div class="modal-header">
          <h3>确认删除</h3>
        </div>
        <div class="modal-body">
          <p>确定要删除行程 <strong>"{{ tripToDelete?.title }}"</strong> 吗？</p>
          <p class="modal-tip">此操作不可恢复</p>
        </div>
        <div class="modal-footer">
          <button class="modal-btn cancel" @click="cancelDelete">取消</button>
          <button class="modal-btn confirm" @click="confirmDelete">删除</button>
        </div>
      </div>
    </div>

    <!-- 重命名弹窗 -->
    <div v-if="showRenameModal" class="modal-overlay" @click.self="cancelRename">
      <div class="modal-content">
        <div class="modal-header">
          <h3>重命名行程</h3>
        </div>
        <div class="modal-body">
          <input 
            v-model="newTitle" 
            type="text" 
            class="rename-input"
            placeholder="请输入新名称"
            @keyup.enter="confirmRename"
          />
        </div>
        <div class="modal-footer">
          <button class="modal-btn cancel" @click="cancelRename">取消</button>
          <button class="modal-btn confirm-rename" @click="confirmRename">确认</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import Navbar from '../components/Navbar.vue'

const router = useRouter()

const trips = ref([])
const showDeleteModal = ref(false)
const tripToDelete = ref(null)
const debugInfo = ref('')
const showRenameModal = ref(false)
const tripToRename = ref(null)
const newTitle = ref('')

// 从数据库加载行程列表
const loadTrips = async () => {
  const userId = localStorage.getItem('userId') || '1'
  
  try {
    // 从数据库获取行程
    const response = await fetch(`http://localhost:8000/api/trips?user_id=${userId}`)
    if (!response.ok) {
      throw new Error('获取行程失败')
    }
    
    const dbTrips = await response.json()
    console.log('从数据库读取的行程:', JSON.stringify(dbTrips, null, 2))
    console.log('行程数量:', dbTrips.length)
    console.log('dbTrips 类型:', typeof dbTrips)
    console.log('dbTrips 是数组?', Array.isArray(dbTrips))
    
    // 检查第一个行程的数据
    if (dbTrips.length > 0) {
      console.log('第一个行程:', dbTrips[0])
      console.log('第一个行程的键:', Object.keys(dbTrips[0]))
      console.log('spot_count:', dbTrips[0].spot_count, '类型:', typeof dbTrips[0].spot_count)
      console.log('created_at:', dbTrips[0].created_at, '类型:', typeof dbTrips[0].created_at)
    }
    
    // 转换数据格式以适配页面显示
    trips.value = dbTrips.map((trip, index) => {
      console.log(`处理第${index + 1}个行程:`, trip)
      
      // 格式化日期
      let dateStr = '未知日期'
      try {
        if (trip.created_at) {
          const createDate = new Date(trip.created_at)
          if (!isNaN(createDate.getTime())) {
            dateStr = `${createDate.getFullYear()}-${String(createDate.getMonth() + 1).padStart(2, '0')}-${String(createDate.getDate()).padStart(2, '0')}`
          }
        }
      } catch (e) {
        console.error('日期格式化失败:', e)
      }
      
      // 使用城市默认图片
      const image = getCityImage(trip.destination)
      
      // 获取景点数量
      const spotCount = trip.spot_count !== undefined ? trip.spot_count : 0
      
      return {
        id: trip.id,
        title: trip.title || `${trip.destination}${trip.total_days}日游`,
        city: trip.destination,
        days: trip.total_days,
        spotCount: spotCount,
        date: dateStr,
        status: trip.status || 'planned',
        statusText: trip.status === 'completed' ? '已完成' : '已规划',
        image: image,
        rawData: trip // 保存原始数据以便查看详情时使用
      }
    }).reverse() // 最新的排在前面
    
  } catch (error) {
    console.error('加载行程失败:', error)
    ElMessage.error('加载行程失败')
    trips.value = []
  }
}

// 获取城市默认图片
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
    '丽江': '/images/cities/lijiang.jpg',
  }
  return cityImages[city] || '/images/cities/beijing.jpg'
}

const createTrip = () => router.push('/create-trip')

const viewTrip = async (trip) => {
  try {
    // 从后端获取完整的行程数据（包含每日安排）
    const response = await fetch(`http://localhost:8000/api/trips/${trip.id}`)
    if (!response.ok) {
      throw new Error('获取行程详情失败')
    }
    
    const tripData = await response.json()
    console.log('获取到的行程详情:', tripData)
    
    // 将后端数据转换为前端需要的格式
    const formattedTrip = {
      id: tripData.id,
      title: tripData.title,
      city: tripData.destination,
      days: tripData.total_days,
      preferences: tripData.travel_preferences || [],
      daySpots: {},
      createTime: tripData.created_at
    }
    
    // 将 schedules 转换为 daySpots 格式
    if (tripData.schedules && tripData.schedules.length > 0) {
      tripData.schedules.forEach(schedule => {
        const dayKey = String(schedule.day_number)
        if (!formattedTrip.daySpots[dayKey]) {
          formattedTrip.daySpots[dayKey] = []
        }
        
        formattedTrip.daySpots[dayKey].push({
          id: schedule.spot_id,
          name: schedule.spot_name,
          image: schedule.spot_image,
          rating: schedule.spot_rating,
          location: schedule.spot_location_lng && schedule.spot_location_lat 
            ? [schedule.spot_location_lng, schedule.spot_location_lat] 
            : null
        })
      })
    }
    
    // 将转换后的数据保存到 localStorage 以便 TripDetail 页面读取
    localStorage.setItem('currentTrip', JSON.stringify(formattedTrip))
    
    // 跳转到行程详情页
    router.push(`/trip/${trip.id}?city=${trip.city}&days=${trip.days}`)
  } catch (error) {
    console.error('加载行程详情失败:', error)
    ElMessage.error('加载行程详情失败')
  }
}

// 删除行程
const deleteTrip = (trip) => {
  tripToDelete.value = trip
  showDeleteModal.value = true
}

// 取消删除
const cancelDelete = () => {
  showDeleteModal.value = false
  tripToDelete.value = null
}

// 确认删除
const confirmDelete = async () => {
  if (!tripToDelete.value) return
  
  try {
    // 1. 先删除数据库中的行程
    const response = await fetch(`http://localhost:8000/api/trips/${tripToDelete.value.id}`, {
      method: 'DELETE'
    })
    
    if (!response.ok) {
      console.error('删除数据库行程失败')
    }
    
    // 2. 从 localStorage 读取保存的行程
    const savedTrips = JSON.parse(localStorage.getItem('savedTrips') || '[]')
    
    // 3. 过滤掉要删除的行程
    const updatedTrips = savedTrips.filter(t => t.id !== tripToDelete.value.id)
    
    // 4. 保存回 localStorage
    localStorage.setItem('savedTrips', JSON.stringify(updatedTrips))
    
    // 5. 如果删除的是当前行程，也清除 currentTrip
    const currentTrip = JSON.parse(localStorage.getItem('currentTrip') || '{}')
    if (currentTrip.id === tripToDelete.value.id) {
      localStorage.removeItem('currentTrip')
    }
    
    // 6. 刷新列表
    loadTrips()
    
    // 7. 关闭弹窗
    showDeleteModal.value = false
    tripToDelete.value = null
    
    ElMessage.success('行程已删除')
  } catch (error) {
    console.error('删除行程失败:', error)
    ElMessage.error('删除失败')
  }
}

// 重命名行程
const renameTrip = (trip) => {
  tripToRename.value = trip
  newTitle.value = trip.title
  showRenameModal.value = true
}

// 取消重命名
const cancelRename = () => {
  showRenameModal.value = false
  tripToRename.value = null
  newTitle.value = ''
}

// 确认重命名
const confirmRename = async () => {
  if (!tripToRename.value || !newTitle.value.trim()) return
  
  const newTitleStr = newTitle.value.trim()
  const tripId = tripToRename.value.id
  
  try {
    // 1. 更新数据库
    // 检查ID类型：数字ID是数据库行程，字符串ID是localStorage行程
    if (typeof tripId === 'number' || !isNaN(parseInt(tripId))) {
      const numericId = typeof tripId === 'number' ? tripId : parseInt(tripId)
      const response = await fetch(`http://localhost:8000/api/trips/${numericId}?title=${encodeURIComponent(newTitleStr)}`, {
        method: 'PUT'
      })
      
      if (!response.ok) {
        console.error('更新数据库失败')
      } else {
        console.log('数据库更新成功')
      }
    }
    
    // 2. 更新 localStorage
    const savedTrips = JSON.parse(localStorage.getItem('savedTrips') || '[]')
    const tripIndex = savedTrips.findIndex(t => t.id === tripId)
    if (tripIndex !== -1) {
      savedTrips[tripIndex].title = newTitleStr
      localStorage.setItem('savedTrips', JSON.stringify(savedTrips))
    }
    
    // 3. 如果重命名的是当前行程，也更新 currentTrip
    const currentTrip = JSON.parse(localStorage.getItem('currentTrip') || '{}')
    if (currentTrip.id === tripId) {
      currentTrip.title = newTitleStr
      localStorage.setItem('currentTrip', JSON.stringify(currentTrip))
    }
    
    // 4. 刷新列表
    await loadTrips()
    
    ElMessage.success('行程已重命名')
  } catch (error) {
    console.error('重命名失败:', error)
    ElMessage.error('重命名失败')
  }
  
  // 关闭弹窗
  showRenameModal.value = false
  tripToRename.value = null
  newTitle.value = ''
}

// 初始化默认行程数据（如果没有数据）
const initDefaultTrips = () => {
  // 不再自动创建默认数据，让用户自己创建行程
  console.log('等待用户创建行程')
}

// 页面加载时读取行程列表
onMounted(async () => {
  // 检查 localStorage 是否可用
  try {
    localStorage.setItem('test', 'test')
    localStorage.removeItem('test')
    console.log('localStorage 可用')
  } catch (e) {
    console.error('localStorage 不可用:', e)
  }
  
  // 初始化默认数据
  initDefaultTrips()
  
  // 加载行程列表
  await loadTrips()
})
</script>

<style scoped>
.trips-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #0a0a1a 0%, #1a1a2e 50%, #16213e 100%);
  color: #fff;
}

.page-content {
  padding-top: 80px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 40px;
  background: rgba(10, 10, 26, 0.5);
  backdrop-filter: blur(10px);
}

.page-title { 
  font-size: 24px;
  font-weight: 700;
}

.add-btn {
  padding: 10px 20px;
  border-radius: 25px;
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  border: none;
  color: #fff;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.add-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 20px rgba(0, 212, 255, 0.3);
}

.trips-list {
  padding: 20px 40px;
}

.trip-card {
  display: flex;
  align-items: center;
  gap: 15px;
  background: rgba(20, 20, 40, 0.8);
  border: 1px solid rgba(0, 212, 255, 0.1);
  border-radius: 16px;
  padding: 15px;
  margin-bottom: 15px;
  transition: all 0.3s;
}

.trip-card:hover {
  border-color: #00d4ff;
  transform: translateY(-2px);
}

.trip-content {
  flex: 1;
  display: flex;
  gap: 15px;
  cursor: pointer;
}

.trip-image {
  width: 100px;
  height: 100px;
  border-radius: 12px;
  background-size: cover;
  background-position: center;
  flex-shrink: 0;
  background-color: rgba(255, 255, 255, 0.05);
  display: flex;
  align-items: center;
  justify-content: center;
}

.no-image {
  font-size: 32px;
  opacity: 0.5;
}

.trip-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.trip-info h3 { font-size: 16px; margin-bottom: 6px; }
.trip-info p { font-size: 13px; color: rgba(255, 255, 255, 0.5); margin-bottom: 8px; }

.trip-meta {
  display: flex;
  gap: 15px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

.trip-status {
  align-self: flex-start;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
}

.trip-status.planned {
  background: rgba(0, 212, 255, 0.2);
  color: #00d4ff;
}

.trip-status.completed {
  background: rgba(123, 44, 191, 0.2);
  color: #7b2cbf;
}

.rename-btn {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 212, 255, 0.1);
  border: 1px solid rgba(0, 212, 255, 0.3);
  border-radius: 10px;
  color: #00d4ff;
  font-size: 18px;
  cursor: pointer;
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.rename-btn:hover {
  background: rgba(0, 212, 255, 0.2);
  border-color: #00d4ff;
  transform: scale(1.05);
}

.delete-btn {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 71, 87, 0.1);
  border: 1px solid rgba(255, 71, 87, 0.3);
  border-radius: 10px;
  color: #ff4757;
  font-size: 18px;
  cursor: pointer;
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.delete-btn:hover {
  background: rgba(255, 71, 87, 0.2);
  border-color: #ff4757;
  transform: scale(1.05);
}

.rename-input {
  width: 100%;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(0, 212, 255, 0.3);
  border-radius: 10px;
  color: #fff;
  font-size: 14px;
  outline: none;
}

.rename-input:focus {
  border-color: #00d4ff;
}

.modal-btn.confirm-rename {
  background: rgba(0, 212, 255, 0.2);
  color: #00d4ff;
  border: 1px solid rgba(0, 212, 255, 0.3);
}

.modal-btn.confirm-rename:hover {
  background: rgba(0, 212, 255, 0.3);
}

.empty-state {
  text-align: center;
  padding: 80px 20px;
}

.empty-icon {
  font-size: 60px;
  display: block;
  margin-bottom: 20px;
}

.empty-state p {
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 20px;
}

.create-btn {
  padding: 14px 30px;
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  border: none;
  border-radius: 25px;
  color: #fff;
  font-size: 15px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.create-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 20px rgba(0, 212, 255, 0.3);
}

/* 删除确认弹窗 */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(5px);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.modal-content {
  background: linear-gradient(180deg, #1a1a2e 0%, #0a0a1a 100%);
  border: 1px solid rgba(0, 212, 255, 0.2);
  border-radius: 16px;
  width: 100%;
  max-width: 400px;
  overflow: hidden;
}

.modal-header {
  padding: 20px 20px 10px;
}

.modal-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: #fff;
}

.modal-body {
  padding: 10px 20px 20px;
}

.modal-body p {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.6;
}

.modal-body strong {
  color: #00d4ff;
}

.modal-tip {
  margin-top: 10px;
  font-size: 13px;
  color: rgba(255, 71, 87, 0.8);
}

.modal-footer {
  display: flex;
  gap: 12px;
  padding: 0 20px 20px;
}

.modal-btn {
  flex: 1;
  padding: 12px 20px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
}

.modal-btn.cancel {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.8);
}

.modal-btn.cancel:hover {
  background: rgba(255, 255, 255, 0.15);
}

.modal-btn.confirm {
  background: rgba(255, 71, 87, 0.2);
  color: #ff4757;
  border: 1px solid rgba(255, 71, 87, 0.3);
}

.modal-btn.confirm:hover {
  background: rgba(255, 71, 87, 0.3);
}

@media (max-width: 768px) {
  .page-header {
    padding: 15px 20px;
  }
  
  .trips-list {
    padding: 15px 20px;
  }
  
  .trip-content {
    gap: 12px;
  }
  
  .trip-image {
    width: 80px;
    height: 80px;
  }
}
</style>
