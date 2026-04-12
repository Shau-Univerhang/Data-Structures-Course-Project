<template>
  <div class="photos-page">
    <!-- 顶部导航 -->
    <header class="page-header">
      <button class="back-btn" @click="goBack">
        <span class="icon">←</span>
      </button>
      <h1 class="page-title">旅行相册</h1>
      <div class="header-actions">
        <button class="view-toggle-btn" @click="toggleViewMode">
          <span v-if="viewMode === 'trip'">📅</span>
          <span v-else>🗂️</span>
        </button>
      </div>
    </header>

    <main class="page-content">
      <!-- 统计信息卡片 -->
      <div class="stats-card" v-if="tripPhotos.length > 0">
        <div class="stat-item">
          <span class="stat-number">{{ totalTrips }}</span>
          <span class="stat-label">行程</span>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-item">
          <span class="stat-number">{{ totalPhotos }}</span>
          <span class="stat-label">照片</span>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-item">
          <span class="stat-number">{{ tripsWithPhotos }}</span>
          <span class="stat-label">有照片</span>
        </div>
      </div>

      <!-- 按行程分组视图 -->
      <div v-if="viewMode === 'trip' && tripPhotos.length > 0" class="trips-list">
        <div 
          v-for="tripGroup in tripPhotos" 
          :key="tripGroup.trip_id" 
          class="trip-card"
          :class="{ 'has-photos': tripGroup.photos && tripGroup.photos.length > 0 }"
        >
          <!-- 行程头部 -->
          <div class="trip-header" @click="toggleTripExpand(tripGroup.trip_id)">
            <div class="trip-info">
              <div class="trip-icon">🧳</div>
              <div class="trip-details">
                <h3 class="trip-title">{{ tripGroup.trip_title }}</h3>
                <span class="trip-photo-count">
                  {{ tripGroup.photos ? tripGroup.photos.length : 0 }} 张照片
                </span>
              </div>
            </div>
            <div class="trip-actions">
              <button 
                class="upload-btn-small" 
                @click.stop="openUploadModal(tripGroup.trip_id)"
              >
                <span class="icon">+</span>
                <span>添加</span>
              </button>
              <span class="expand-icon" :class="{ 'expanded': expandedTrips.includes(tripGroup.trip_id) }">
                ▼
              </span>
            </div>
          </div>

          <!-- 行程照片网格 -->
          <div 
            v-show="expandedTrips.includes(tripGroup.trip_id)" 
            class="trip-photos-container"
          >
            <div v-if="tripGroup.photos && tripGroup.photos.length > 0" class="photo-grid">
              <div 
                v-for="(photo, index) in tripGroup.photos" 
                :key="photo.id" 
                class="photo-item"
                :style="{ animationDelay: index * 0.05 + 's' }"
                @click="openPhotoPreview(photo)"
              >
                <img :src="photo.photo_url" :alt="photo.description || ''" />
                <div class="photo-overlay">
                  <button class="delete-btn" @click.stop="deletePhoto(photo.id)">
                    <span>🗑️</span>
                  </button>
                </div>
                <div v-if="photo.description" class="photo-desc">
                  {{ photo.description }}
                </div>
              </div>
            </div>
            <div v-else class="no-photos-tip">
              <div class="empty-illustration">
                <span class="big-icon">📷</span>
                <p>还没有照片</p>
                <p class="sub-text">点击"添加"按钮上传旅行照片</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 时间轴视图 -->
      <div v-else-if="viewMode === 'timeline' && allPhotos.length > 0" class="timeline-view">
        <div class="timeline">
          <div 
            v-for="(photo, index) in allPhotos" 
            :key="photo.id" 
            class="timeline-item"
            :style="{ animationDelay: index * 0.05 + 's' }"
          >
            <div class="timeline-dot"></div>
            <div class="timeline-content">
              <div class="photo-card" @click="openPhotoPreview(photo)">
                <img :src="photo.photo_url" :alt="photo.description || ''" />
                <div class="photo-info">
                  <span class="photo-trip">{{ photo.trip_title }}</span>
                  <span class="photo-date">{{ formatDate(photo.created_at) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 完全空状态 -->
      <div v-else-if="tripPhotos.length === 0" class="empty-state">
        <div class="empty-illustration">
          <div class="floating-icons">
            <span class="float-icon" style="--delay: 0s">📸</span>
            <span class="float-icon" style="--delay: 0.5s">✈️</span>
            <span class="float-icon" style="--delay: 1s">🗺️</span>
          </div>
          <h2>开始记录你的旅行</h2>
          <p>创建行程并上传照片，保存美好回忆</p>
        </div>
        <button class="create-trip-btn" @click="goToCreateTrip">
          <span>创建我的第一个行程</span>
          <span class="arrow">→</span>
        </button>
      </div>

      <!-- 有行程但无照片状态 -->
      <div v-else-if="totalPhotos === 0" class="empty-state has-trips">
        <div class="empty-illustration">
          <span class="big-icon">📷</span>
          <h2>上传你的第一张照片</h2>
          <p>你已经有 {{ totalTrips }} 个行程，开始添加照片吧</p>
        </div>
        <button class="upload-first-btn" @click="openUploadModal(tripPhotos[0].trip_id)">
          <span>上传照片</span>
          <span class="arrow">→</span>
        </button>
      </div>
    </main>

    <!-- 上传照片弹窗 -->
    <div v-if="showUploadModal" class="modal-overlay" @click.self="closeUploadModal">
      <div class="modal-content upload-modal">
        <div class="modal-header">
          <h3>上传照片</h3>
          <button class="close-btn" @click="closeUploadModal">×</button>
        </div>
        
        <div class="upload-body">
          <!-- 拖拽上传区域 -->
          <div 
            class="upload-dropzone"
            :class="{ 'drag-over': isDragging }"
            @click="triggerFileSelect"
            @drop.prevent="handleDrop"
            @dragover.prevent="isDragging = true"
            @dragleave.prevent="isDragging = false"
          >
            <input 
              type="file" 
              ref="fileInput"
              accept="image/*"
              multiple
              @change="handleFileChange"
              style="display: none"
            />
            <div v-if="!selectedFiles.length" class="upload-placeholder">
              <div class="upload-icon-wrapper">
                <span class="upload-icon">📤</span>
              </div>
              <p class="upload-title">点击或拖拽上传</p>
              <p class="upload-tip">支持 JPG、PNG、GIF 格式，最多 9 张</p>
            </div>
            <div v-else class="selected-preview">
              <div v-for="(file, index) in selectedFiles" :key="index" class="preview-item">
                <img :src="getFileUrl(file)" />
                <button class="remove-btn" @click.stop="removeFile(index)">×</button>
              </div>
              <div v-if="selectedFiles.length < 9" class="add-more" @click.stop="triggerFileSelect">
                <span>+</span>
              </div>
            </div>
          </div>

          <!-- 描述输入 -->
          <div class="description-section">
            <label>照片描述（可选）</label>
            <textarea 
              v-model="photoDescription"
              class="tech-textarea"
              placeholder="记录这张照片的故事..."
              rows="3"
            ></textarea>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="closeUploadModal">取消</button>
          <button 
            class="btn-primary" 
            @click="uploadPhotos" 
            :disabled="uploading || !selectedFiles.length"
          >
            <span v-if="uploading" class="loading-spinner"></span>
            <span>{{ uploading ? '上传中...' : `上传 ${selectedFiles.length} 张照片` }}</span>
          </button>
        </div>
      </div>
    </div>

    <!-- 图片预览弹窗 -->
    <div v-if="previewPhoto" class="modal-overlay preview-modal" @click.self="closePhotoPreview">
      <div class="preview-content">
        <button class="close-preview" @click="closePhotoPreview">×</button>
        <img :src="previewPhoto.photo_url" :alt="previewPhoto.description || ''" />
        <div v-if="previewPhoto.description" class="preview-desc">
          {{ previewPhoto.description }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()

// 数据
const tripPhotos = ref([])
const viewMode = ref('trip') // 'trip' 或 'timeline'
const expandedTrips = ref([])
const showUploadModal = ref(false)
const selectedFiles = ref([])
const photoDescription = ref('')
const currentTripId = ref(null)
const fileInput = ref(null)
const uploading = ref(false)
const isDragging = ref(false)
const previewPhoto = ref(null)

// 计算属性
const totalTrips = computed(() => tripPhotos.value.length)
const totalPhotos = computed(() => {
  return tripPhotos.value.reduce((sum, trip) => sum + (trip.photos ? trip.photos.length : 0), 0)
})
const tripsWithPhotos = computed(() => {
  return tripPhotos.value.filter(trip => trip.photos && trip.photos.length > 0).length
})
const allPhotos = computed(() => {
  const photos = []
  tripPhotos.value.forEach(trip => {
    if (trip.photos) {
      trip.photos.forEach(photo => {
        photos.push({
          ...photo,
          trip_title: trip.trip_title
        })
      })
    }
  })
  return photos.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
})

onMounted(() => {
  const userId = localStorage.getItem('userId')
  if (!userId) {
    router.push('/login')
    return
  }
  fetchPhotos(userId)
})

const fetchPhotos = async (userId) => {
  try {
    const response = await fetch(`http://localhost:8000/api/photos?user_id=${userId}`)
    if (response.ok) {
      tripPhotos.value = await response.json()
      // 默认展开第一个有照片的行程
      const firstWithPhotos = tripPhotos.value.find(trip => trip.photos && trip.photos.length > 0)
      if (firstWithPhotos) {
        expandedTrips.value = [firstWithPhotos.trip_id]
      } else if (tripPhotos.value.length > 0) {
        expandedTrips.value = [tripPhotos.value[0].trip_id]
      }
    }
  } catch (error) {
    console.error('获取照片失败:', error)
    ElMessage.error('获取照片失败')
  }
}

const toggleViewMode = () => {
  viewMode.value = viewMode.value === 'trip' ? 'timeline' : 'trip'
}

const toggleTripExpand = (tripId) => {
  if (expandedTrips.value.includes(tripId)) {
    expandedTrips.value = expandedTrips.value.filter(id => id !== tripId)
  } else {
    expandedTrips.value.push(tripId)
  }
}

const openUploadModal = (tripId) => {
  currentTripId.value = tripId
  selectedFiles.value = []
  photoDescription.value = ''
  showUploadModal.value = true
}

const closeUploadModal = () => {
  showUploadModal.value = false
  selectedFiles.value = []
  photoDescription.value = ''
}

const triggerFileSelect = () => {
  fileInput.value.click()
}

const handleFileChange = (event) => {
  const files = event.target.files
  if (files) {
    addFiles(Array.from(files))
  }
}

const handleDrop = (event) => {
  isDragging.value = false
  const files = event.dataTransfer.files
  if (files) {
    addFiles(Array.from(files).filter(f => f.type.startsWith('image/')))
  }
}

const addFiles = (files) => {
  const remainingSlots = 9 - selectedFiles.value.length
  const filesToAdd = files.slice(0, remainingSlots)
  selectedFiles.value.push(...filesToAdd)
  
  if (files.length > remainingSlots) {
    ElMessage.warning(`最多只能上传 9 张照片，已自动选择前 ${remainingSlots} 张`)
  }
}

const removeFile = (index) => {
  selectedFiles.value.splice(index, 1)
}

const getFileUrl = (file) => {
  return URL.createObjectURL(file)
}

const uploadPhotos = async () => {
  if (!selectedFiles.value.length) {
    ElMessage.warning('请选择照片')
    return
  }

  const userId = localStorage.getItem('userId')
  if (!userId) return

  uploading.value = true

  try {
    for (const file of selectedFiles.value) {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('user_id', userId)
      formData.append('trip_id', currentTripId.value)
      if (photoDescription.value) {
        formData.append('description', photoDescription.value)
      }

      const response = await fetch('http://localhost:8000/api/photos', {
        method: 'POST',
        body: formData
      })

      if (!response.ok) {
        throw new Error('上传失败')
      }
    }

    ElMessage.success(`成功上传 ${selectedFiles.value.length} 张照片`)
    closeUploadModal()
    fetchPhotos(userId)
    
    // 展开刚上传的行程
    if (!expandedTrips.value.includes(currentTripId.value)) {
      expandedTrips.value.push(currentTripId.value)
    }
  } catch (error) {
    console.error('上传照片失败:', error)
    ElMessage.error('上传失败')
  } finally {
    uploading.value = false
  }
}

const deletePhoto = async (photoId) => {
  const userId = localStorage.getItem('userId')
  if (!userId) return

  try {
    const response = await fetch(`http://localhost:8000/api/photos/${photoId}?user_id=${userId}`, {
      method: 'DELETE'
    })

    if (response.ok) {
      ElMessage.success('删除成功')
      fetchPhotos(userId)
    }
  } catch (error) {
    console.error('删除照片失败:', error)
    ElMessage.error('删除失败')
  }
}

const openPhotoPreview = (photo) => {
  previewPhoto.value = photo
}

const closePhotoPreview = () => {
  previewPhoto.value = null
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}月${date.getDate()}日`
}

const goBack = () => {
  router.back()
}

const goToCreateTrip = () => {
  router.push('/create-trip')
}
</script>

<style scoped>
.photos-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #0a0a1a 0%, #1a1a2e 100%);
  color: #fff;
}

/* 顶部导航 */
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: rgba(10, 10, 26, 0.95);
  backdrop-filter: blur(20px);
  position: sticky;
  top: 0;
  z-index: 100;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.back-btn {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  border: none;
  background: rgba(255, 255, 255, 0.05);
  color: #fff;
  font-size: 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}

.back-btn:hover {
  background: rgba(255, 255, 255, 0.1);
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  background: linear-gradient(135deg, #fff, rgba(255, 255, 255, 0.7));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.view-toggle-btn {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  border: none;
  background: rgba(0, 212, 255, 0.1);
  color: #00d4ff;
  font-size: 18px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}

.view-toggle-btn:hover {
  background: rgba(0, 212, 255, 0.2);
}

/* 页面内容 */
.page-content {
  padding: 20px;
  padding-bottom: 100px;
}

/* 统计卡片 */
.stats-card {
  display: flex;
  align-items: center;
  justify-content: space-around;
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.1), rgba(123, 44, 191, 0.1));
  border: 1px solid rgba(0, 212, 255, 0.2);
  border-radius: 20px;
  padding: 24px 20px;
  margin-bottom: 24px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.stat-number {
  font-size: 32px;
  font-weight: 700;
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-label {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
}

.stat-divider {
  width: 1px;
  height: 40px;
  background: rgba(255, 255, 255, 0.1);
}

/* 行程列表 */
.trips-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.trip-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 20px;
  overflow: hidden;
  transition: all 0.3s;
}

.trip-card:hover {
  border-color: rgba(0, 212, 255, 0.2);
}

.trip-card.has-photos {
  border-color: rgba(0, 212, 255, 0.15);
}

.trip-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px;
  cursor: pointer;
  transition: background 0.3s;
}

.trip-header:hover {
  background: rgba(255, 255, 255, 0.02);
}

.trip-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.trip-icon {
  width: 50px;
  height: 50px;
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.2), rgba(123, 44, 191, 0.2));
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.trip-details {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.trip-title {
  font-size: 18px;
  font-weight: 600;
  color: #fff;
}

.trip-photo-count {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
}

.trip-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.upload-btn-small {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 18px;
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  border: none;
  border-radius: 25px;
  color: #fff;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.upload-btn-small:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 212, 255, 0.3);
}

.upload-btn-small .icon {
  font-size: 18px;
}

.expand-icon {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
  transition: transform 0.3s;
}

.expand-icon.expanded {
  transform: rotate(180deg);
}

/* 行程照片容器 */
.trip-photos-container {
  padding: 0 20px 20px;
  animation: slideDown 0.3s ease;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 照片网格 */
.photo-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.photo-item {
  position: relative;
  aspect-ratio: 1;
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  animation: fadeIn 0.5s ease backwards;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.photo-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.photo-item:hover img {
  transform: scale(1.05);
}

.photo-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(to bottom, rgba(0,0,0,0.3), transparent 50%);
  opacity: 0;
  transition: opacity 0.3s;
  display: flex;
  justify-content: flex-end;
  padding: 10px;
}

.photo-item:hover .photo-overlay {
  opacity: 1;
}

.delete-btn {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(255, 59, 48, 0.9);
  border: none;
  color: #fff;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}

.delete-btn:hover {
  background: rgba(255, 59, 48, 1);
  transform: scale(1.1);
}

.photo-desc {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 20px 12px 12px;
  background: linear-gradient(to top, rgba(0,0,0,0.8), transparent);
  font-size: 12px;
  color: rgba(255, 255, 255, 0.9);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 无照片提示 */
.no-photos-tip {
  padding: 40px 20px;
  text-align: center;
}

.empty-illustration {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.big-icon {
  font-size: 64px;
  opacity: 0.5;
}

.empty-illustration p {
  color: rgba(255, 255, 255, 0.5);
  font-size: 16px;
}

.sub-text {
  font-size: 13px !important;
  opacity: 0.4 !important;
}

/* 时间轴视图 */
.timeline-view {
  padding: 20px 0;
}

.timeline {
  position: relative;
  padding-left: 30px;
}

.timeline::before {
  content: '';
  position: absolute;
  left: 8px;
  top: 0;
  bottom: 0;
  width: 2px;
  background: linear-gradient(to bottom, #00d4ff, #7b2cbf);
}

.timeline-item {
  position: relative;
  margin-bottom: 24px;
  animation: fadeIn 0.5s ease backwards;
}

.timeline-dot {
  position: absolute;
  left: -26px;
  top: 20px;
  width: 12px;
  height: 12px;
  background: #00d4ff;
  border-radius: 50%;
  border: 3px solid #0a0a1a;
}

.timeline-content {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  overflow: hidden;
}

.photo-card {
  cursor: pointer;
}

.photo-card img {
  width: 100%;
  aspect-ratio: 16/10;
  object-fit: cover;
}

.photo-info {
  padding: 12px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.photo-trip {
  font-size: 14px;
  font-weight: 500;
  color: #fff;
}

.photo-date {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.floating-icons {
  position: relative;
  height: 100px;
  margin-bottom: 30px;
}

.float-icon {
  position: absolute;
  font-size: 48px;
  animation: float 3s ease-in-out infinite;
  animation-delay: var(--delay);
}

.float-icon:nth-child(1) { left: 0; }
.float-icon:nth-child(2) { left: 50%; transform: translateX(-50%); }
.float-icon:nth-child(3) { right: 0; }

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-15px); }
}

.empty-state h2 {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 12px;
  background: linear-gradient(135deg, #fff, rgba(255, 255, 255, 0.7));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.empty-state > p {
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 30px;
}

.create-trip-btn,
.upload-first-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 16px 32px;
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  border: none;
  border-radius: 30px;
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.create-trip-btn:hover,
.upload-first-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 30px rgba(0, 212, 255, 0.3);
}

.arrow {
  transition: transform 0.3s;
}

.create-trip-btn:hover .arrow,
.upload-first-btn:hover .arrow {
  transform: translateX(5px);
}

/* 弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
  backdrop-filter: blur(10px);
}

.modal-content {
  background: linear-gradient(180deg, #1a1a2e 0%, #0a0a1a 100%);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 24px;
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.modal-header h3 {
  font-size: 20px;
  font-weight: 600;
}

.close-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.05);
  border: none;
  color: rgba(255, 255, 255, 0.6);
  font-size: 24px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}

.upload-body {
  padding: 24px;
  overflow-y: auto;
}

/* 上传区域 */
.upload-dropzone {
  border: 2px dashed rgba(0, 212, 255, 0.3);
  border-radius: 20px;
  padding: 40px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  margin-bottom: 20px;
}

.upload-dropzone:hover,
.upload-dropzone.drag-over {
  border-color: #00d4ff;
  background: rgba(0, 212, 255, 0.05);
}

.upload-icon-wrapper {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.2), rgba(123, 44, 191, 0.2));
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
}

.upload-icon {
  font-size: 36px;
}

.upload-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 8px;
}

.upload-tip {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.4);
}

/* 已选预览 */
.selected-preview {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.preview-item {
  position: relative;
  aspect-ratio: 1;
  border-radius: 12px;
  overflow: hidden;
}

.preview-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.remove-btn {
  position: absolute;
  top: 6px;
  right: 6px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: rgba(255, 59, 48, 0.9);
  border: none;
  color: #fff;
  font-size: 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.add-more {
  aspect-ratio: 1;
  border-radius: 12px;
  border: 2px dashed rgba(0, 212, 255, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  color: #00d4ff;
  cursor: pointer;
  transition: all 0.3s;
}

.add-more:hover {
  border-color: #00d4ff;
  background: rgba(0, 212, 255, 0.05);
}

/* 描述输入 */
.description-section {
  margin-top: 20px;
}

.description-section label {
  display: block;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 10px;
}

.tech-textarea {
  width: 100%;
  padding: 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  color: #fff;
  font-size: 14px;
  resize: none;
  font-family: inherit;
}

.tech-textarea:focus {
  outline: none;
  border-color: #00d4ff;
}

.tech-textarea::placeholder {
  color: rgba(255, 255, 255, 0.3);
}

/* 弹窗底部 */
.modal-footer {
  display: flex;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.btn-secondary,
.btn-primary {
  flex: 1;
  padding: 14px 24px;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.8);
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.1);
}

.btn-primary {
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  border: none;
  color: #fff;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 212, 255, 0.3);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.loading-spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 图片预览弹窗 */
.preview-modal {
  padding: 40px;
}

.preview-content {
  position: relative;
  max-width: 90vw;
  max-height: 90vh;
}

.preview-content img {
  max-width: 100%;
  max-height: 85vh;
  border-radius: 16px;
  object-fit: contain;
}

.close-preview {
  position: absolute;
  top: -40px;
  right: 0;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  color: #fff;
  font-size: 24px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}

.close-preview:hover {
  background: rgba(255, 255, 255, 0.2);
}

.preview-desc {
  position: absolute;
  bottom: 20px;
  left: 20px;
  right: 20px;
  padding: 16px 20px;
  background: rgba(0, 0, 0, 0.7);
  border-radius: 12px;
  font-size: 14px;
  color: #fff;
  text-align: center;
}
</style>