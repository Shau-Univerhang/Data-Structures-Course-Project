<template>
  <div class="photos-page">
    <header class="page-header">
      <button class="back-btn" @click="goBack">←</button>
      <h1 class="page-title">我的照片</h1>
      <div style="width: 40px;"></div>
    </header>

    <main class="page-content">
      <!-- 按行程分组的照片 -->
      <div v-if="tripPhotos.length > 0">
        <div v-for="tripGroup in tripPhotos" :key="tripGroup.trip_id" class="trip-section">
          <div class="trip-header">
            <h3>{{ tripGroup.trip_title }}</h3>
            <button class="add-photo-btn" @click="openUploadModal(tripGroup.trip_id)">+ 添加</button>
          </div>
          
          <div class="photo-grid" v-if="tripGroup.photos && tripGroup.photos.length > 0">
            <div v-for="photo in tripGroup.photos" :key="photo.id" class="photo-item">
              <img :src="photo.photo_url" :alt="photo.description || ''" />
              <button class="delete-btn" @click="deletePhoto(photo.id)">×</button>
            </div>
          </div>
          <div v-else class="no-photos">
            <p>暂无照片</p>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-else class="empty-state">
        <span class="empty-icon">📸</span>
        <p>还没有旅行照片</p>
        <p class="empty-tip">创建行程后可以上传照片</p>
        <button class="tech-button" @click="goToCreateTrip">创建行程</button>
      </div>
    </main>

    <!-- 上传照片弹窗 -->
    <div v-if="showUploadModal" class="modal-overlay" @click.self="showUploadModal = false">
      <div class="modal-content">
        <h3>上传照片</h3>
        
        <div class="upload-area" @click="triggerFileSelect">
          <input 
            type="file" 
            ref="fileInput"
            accept="image/*"
            multiple
            @change="handleFileChange"
            style="display: none"
          />
          <div v-if="!selectedFiles.length" class="upload-placeholder">
            <span class="upload-icon">📤</span>
            <p>点击选择图片</p>
            <p class="upload-tip">支持 JPG、PNG 格式</p>
          </div>
          <div v-else class="selected-files">
            <div v-for="(file, index) in selectedFiles" :key="index" class="file-preview">
              <img :src="getFileUrl(file)" />
              <span>{{ file.name }}</span>
            </div>
          </div>
        </div>

        <input 
          type="text" 
          v-model="photoDescription"
          class="tech-input"
          placeholder="照片描述（可选）"
        />

        <div class="modal-actions">
          <button class="tech-button secondary" @click="showUploadModal = false">取消</button>
          <button class="tech-button" @click="uploadPhotos" :disabled="uploading">
            {{ uploading ? '上传中...' : '上传' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()

const tripPhotos = ref([])
const showUploadModal = ref(false)
const selectedFiles = ref([])
const photoDescription = ref('')
const currentTripId = ref(null)
const fileInput = ref(null)
const uploading = ref(false)

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
    }
  } catch (error) {
    console.error('获取照片失败:', error)
  }
}

const goBack = () => {
  router.back()
}

const goToCreateTrip = () => {
  router.push('/create-trip')
}

const openUploadModal = (tripId) => {
  currentTripId.value = tripId
  selectedFiles.value = []
  photoDescription.value = ''
  showUploadModal.value = true
}

const triggerFileSelect = () => {
  fileInput.value.click()
}

const getFileUrl = (file) => {
  return URL.createObjectURL(file)
}

const handleFileChange = (event) => {
  const files = event.target.files
  if (files) {
    selectedFiles.value = Array.from(files)
  }
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

    ElMessage.success('上传成功')
    showUploadModal.value = false
    // 刷新照片列表
    fetchPhotos(userId)
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
</script>

<style scoped>
.photos-page {
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

.trip-section {
  margin-bottom: 30px;
}

.trip-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.trip-header h3 {
  font-size: 18px;
  color: #fff;
}

.add-photo-btn {
  padding: 8px 16px;
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  border: none;
  border-radius: 20px;
  color: #fff;
  font-size: 14px;
  cursor: pointer;
}

.photo-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}

.photo-item {
  position: relative;
  aspect-ratio: 1;
  border-radius: 8px;
  overflow: hidden;
}

.photo-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.delete-btn {
  position: absolute;
  top: 5px;
  right: 5px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.6);
  border: none;
  color: #fff;
  font-size: 16px;
  cursor: pointer;
  opacity: 0;
  transition: opacity 0.3s;
}

.photo-item:hover .delete-btn {
  opacity: 1;
}

.no-photos {
  padding: 30px;
  text-align: center;
  color: rgba(255, 255, 255, 0.4);
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
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

/* 弹窗 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 25px;
  width: 100%;
  max-width: 400px;
}

.modal-content h3 {
  font-size: 20px;
  color: #fff;
  margin-bottom: 20px;
  text-align: center;
}

.upload-area {
  border: 2px dashed var(--border-color);
  border-radius: 12px;
  padding: 30px;
  margin-bottom: 15px;
  cursor: pointer;
  transition: all 0.3s;
}

.upload-area:hover {
  border-color: var(--primary-color);
}

.upload-placeholder {
  text-align: center;
  color: rgba(255, 255, 255, 0.5);
}

.upload-icon {
  font-size: 40px;
  display: block;
  margin-bottom: 10px;
}

.upload-tip {
  font-size: 12px;
  opacity: 0.6;
  margin-top: 8px;
}

.selected-files {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.file-preview {
  width: 80px;
  text-align: center;
}

.file-preview img {
  width: 60px;
  height: 60px;
  object-fit: cover;
  border-radius: 8px;
}

.file-preview span {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.5);
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.modal-actions {
  display: flex;
  gap: 15px;
  justify-content: center;
  margin-top: 20px;
}

.modal-actions .tech-button {
  padding: 10px 30px;
}
</style>
