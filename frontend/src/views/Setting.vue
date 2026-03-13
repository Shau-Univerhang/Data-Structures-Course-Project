<template>
  <div class="setting-page">
    <header class="page-header">
      <button class="back-btn" @click="goBack">←</button>
      <h1 class="page-title">设置</h1>
      <div style="width: 40px;"></div>
    </header>

    <main class="page-content">
      <!-- 用户信息 -->
      <section class="user-section">
        <div class="avatar-section">
          <div class="avatar-wrapper" @click="triggerUpload">
            <img v-if="user.avatar_url" :src="user.avatar_url" alt="头像" class="avatar-img" />
            <div v-else class="avatar-placeholder">{{ user.username?.charAt(0) || '游' }}</div>
            <div class="avatar-edit">
              <span>编辑</span>
            </div>
          </div>
          <input 
            type="file" 
            ref="fileInput"
            accept="image/*"
            @change="handleAvatarChange"
            style="display: none"
          />
        </div>
        
        <div class="user-detail">
          <h3>{{ user.username }}</h3>
          <p>加入于 {{ formatDate(user.created_at) }}</p>
        </div>
      </section>

      <!-- 设置列表 -->
      <section class="setting-section">
        <h4 class="section-title">账户设置</h4>
        
        <div class="setting-item" @click="showUsernameModal = true">
          <div class="setting-left">
            <span class="setting-icon">👤</span>
            <span>用户名</span>
          </div>
          <div class="setting-right">
            <span>{{ user.username }}</span>
            <span class="arrow">›</span>
          </div>
        </div>

        <div class="setting-item">
          <div class="setting-left">
            <span class="setting-icon">📧</span>
            <span>邮箱</span>
          </div>
          <div class="setting-right">
            <span class="text-gray">{{ user.email || '未设置' }}</span>
          </div>
        </div>
      </section>

      <section class="setting-section">
        <h4 class="section-title">其他</h4>
        
        <div class="setting-item" @click="showAboutModal = true">
          <div class="setting-left">
            <span class="setting-icon">ℹ️</span>
            <span>关于我们</span>
          </div>
          <div class="setting-right">
            <span class="arrow">›</span>
          </div>
        </div>

        <div class="setting-item">
          <div class="setting-left">
            <span class="setting-icon">📖</span>
            <span>版本</span>
          </div>
          <div class="setting-right">
            <span class="text-gray">v1.0.0</span>
          </div>
        </div>
      </section>

      <!-- 退出登录按钮 -->
      <div class="logout-section">
        <button class="logout-btn" @click="handleLogout">退出登录</button>
      </div>
    </main>

    <!-- 修改用户名弹窗 -->
    <div v-if="showUsernameModal" class="modal-overlay" @click.self="showUsernameModal = false">
      <div class="modal-content">
        <h3>修改用户名</h3>
        <input 
          type="text" 
          v-model="newUsername"
          class="tech-input"
          placeholder="请输入新用户名"
        />
        <p class="modal-tip">用户名一旦创建不可更改</p>
        <div class="modal-actions">
          <button class="tech-button secondary" @click="showUsernameModal = false">取消</button>
          <button class="tech-button" @click="updateUsername">保存</button>
        </div>
      </div>
    </div>

    <!-- 关于弹窗 -->
    <div v-if="showAboutModal" class="modal-overlay" @click.self="showAboutModal = false">
      <div class="modal-content">
        <h3>关于邮游世界</h3>
        <div class="about-content">
          <p>邮游世界 v1.0.0</p>
          <p>基于MiniMax大模型的个性化旅游规划系统</p>
          <p>北京邮电大学 · 数据结构课程设计</p>
        </div>
        <div class="modal-actions">
          <button class="tech-button" @click="showAboutModal = false">确定</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()

const user = reactive({
  id: null,
  username: '',
  avatar_url: '',
  email: '',
  created_at: ''
})

const showUsernameModal = ref(false)
const showAboutModal = ref(false)
const newUsername = ref('')
const fileInput = ref(null)

onMounted(() => {
  // 获取用户信息
  const userId = localStorage.getItem('userId')
  if (!userId) {
    router.push('/login')
    return
  }
  
  fetchUserInfo(userId)
})

const fetchUserInfo = async (userId) => {
  try {
    const response = await fetch(`http://localhost:8000/api/auth/me?user_id=${userId}`)
    if (response.ok) {
      const data = await response.json()
      Object.assign(user, data)
    }
  } catch (error) {
    console.error('获取用户信息失败:', error)
  }
}

const goBack = () => {
  router.back()
}

const triggerUpload = () => {
  fileInput.value.click()
}

const handleAvatarChange = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  const userId = localStorage.getItem('userId')
  if (!userId) return

  const formData = new FormData()
  formData.append('file', file)

  try {
    const response = await fetch(`http://localhost:8000/api/auth/avatar?user_id=${userId}`, {
      method: 'POST',
      body: formData
    })

    if (response.ok) {
      const data = await response.json()
      user.avatar_url = data.avatar_url
      // 更新本地存储的用户信息
      const storedUser = JSON.parse(localStorage.getItem('user') || '{}')
      storedUser.avatar_url = data.avatar_url
      localStorage.setItem('user', JSON.stringify(storedUser))
      ElMessage.success('头像上传成功')
    } else {
      ElMessage.error('头像上传失败')
    }
  } catch (error) {
    console.error('上传头像失败:', error)
    ElMessage.error('头像上传失败')
  }
}

const updateUsername = async () => {
  if (!newUsername.value || newUsername.value === user.username) {
    showUsernameModal.value = false
    return
  }

  const userId = localStorage.getItem('userId')
  if (!userId) return

  try {
    const response = await fetch(`http://localhost:8000/api/auth/profile?user_id=${userId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        username: newUsername.value
      })
    })

    if (response.ok) {
      const data = await response.json()
      user.username = data.username
      // 更新本地存储
      const storedUser = JSON.parse(localStorage.getItem('user') || '{}')
      storedUser.username = data.username
      localStorage.setItem('user', JSON.stringify(storedUser))
      ElMessage.success('用户名修改成功')
      showUsernameModal.value = false
    } else {
      const error = await response.json()
      ElMessage.error(error.detail || '修改失败')
    }
  } catch (error) {
    console.error('修改用户名失败:', error)
    ElMessage.error('修改失败')
  }
}

const handleLogout = () => {
  localStorage.removeItem('user')
  localStorage.removeItem('userId')
  ElMessage.success('已退出登录')
  router.push('/login')
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return dateStr.split('T')[0]
}
</script>

<style scoped>
.setting-page {
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

/* 用户信息 */
.user-section {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 25px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  margin-bottom: 25px;
}

.avatar-section {
  position: relative;
}

.avatar-wrapper {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  overflow: hidden;
  cursor: pointer;
  position: relative;
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  color: #fff;
}

.avatar-edit {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(0, 0, 0, 0.6);
  color: #fff;
  font-size: 12px;
  text-align: center;
  padding: 4px;
  opacity: 0;
  transition: opacity 0.3s;
}

.avatar-wrapper:hover .avatar-edit {
  opacity: 1;
}

.user-detail h3 {
  font-size: 20px;
  color: #fff;
  margin-bottom: 5px;
}

.user-detail p {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
}

/* 设置列表 */
.setting-section {
  margin-bottom: 25px;
}

.section-title {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 12px;
  padding-left: 5px;
}

.setting-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  margin-bottom: 10px;
  cursor: pointer;
  transition: all 0.3s;
}

.setting-item:hover {
  border-color: var(--primary-color);
}

.setting-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.setting-icon {
  font-size: 18px;
}

.setting-right {
  display: flex;
  align-items: center;
  gap: 8px;
  color: rgba(255, 255, 255, 0.6);
}

.text-gray {
  color: rgba(255, 255, 255, 0.4) !important;
}

.arrow {
  color: rgba(255, 255, 255, 0.3);
  font-size: 18px;
}

/* 退出登录 */
.logout-section {
  margin-top: 40px;
}

.logout-btn {
  width: 100%;
  padding: 16px;
  background: rgba(255, 107, 107, 0.1);
  border: 1px solid rgba(255, 107, 107, 0.3);
  border-radius: 12px;
  color: #ff6b6b;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s;
}

.logout-btn:hover {
  background: rgba(255, 107, 107, 0.2);
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

.modal-tip {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
  margin-top: 8px;
}

.about-content {
  text-align: center;
  color: rgba(255, 255, 255, 0.7);
  line-height: 2;
}

.modal-actions {
  display: flex;
  gap: 15px;
  justify-content: center;
  margin-top: 25px;
}

.modal-actions .tech-button {
  padding: 10px 30px;
}
</style>
