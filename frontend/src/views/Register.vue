<template>
  <div class="register-page">
    <!-- 左侧 - 一比一复刻 careercompass -->
    <div class="left-section">
      <!-- Logo -->
      <div class="logo">
        <div class="logo-icon">
          🌍
        </div>
        <span>邮游世界</span>
      </div>

      <!-- 四个跟随鼠标的小人 -->
      <div class="characters-container">
        <!-- 紫色小人 -->
        <div ref="purpleRef" class="character purple" :style="{ height: isTyping ? '440px' : '400px', left: '70px' }">
          <div class="eyes" :style="{ left: isLookingAtEachOther ? '55px' : `${45 + purplePos.faceX}px`, top: isLookingAtEachOther ? '65px' : `${40 + purplePos.faceY}px` }">
            <div class="eye" :class="{ blinking: isPurpleBlinking }"><div class="pupil"></div></div>
            <div class="eye" :class="{ blinking: isPurpleBlinking }"><div class="pupil"></div></div>
          </div>
        </div>

        <!-- 黑色小人 -->
        <div ref="blackRef" class="character black" style="left: 240px;">
          <div class="eyes" :style="{ left: isLookingAtEachOther ? '32px' : `${26 + blackPos.faceX}px`, top: isLookingAtEachOther ? '12px' : `${32 + blackPos.faceY}px` }">
            <div class="eye" :class="{ blinking: isBlackBlinking }"><div class="pupil small"></div></div>
            <div class="eye" :class="{ blinking: isBlackBlinking }"><div class="pupil small"></div></div>
          </div>
        </div>

        <!-- 橙色半圆小人 -->
        <div ref="orangeRef" class="character orange" style="left: 0px;">
          <div class="eyes-pupil" :style="{ left: `${82 + orangePos.faceX}px`, top: `${90 + orangePos.faceY}px` }">
            <div class="pupil-only"></div>
            <div class="pupil-only"></div>
          </div>
        </div>

        <!-- 黄色小人 -->
        <div ref="yellowRef" class="character yellow" style="left: 310px;">
          <div class="eyes-pupil" :style="{ left: `${52 + yellowPos.faceX}px`, top: `${40 + yellowPos.faceY}px` }">
            <div class="pupil-only"></div>
            <div class="pupil-only"></div>
          </div>
          <div class="mouth" :style="{ left: `${40 + yellowPos.faceX}px`, top: `${88 + yellowPos.faceY}px` }"></div>
        </div>
      </div>

      <!-- 装饰元素 -->
      <div class="decoration-grid"></div>
      <div class="circle-decor circle-1"></div>
      <div class="circle-decor circle-2"></div>
    </div>

    <!-- 右侧 - 注册表单 -->
    <div class="right-section">
      <div class="register-container">
        <div class="register-header">
          <h2>创建账户</h2>
          <p>开始您的旅游规划之旅</p>
        </div>

        <form @submit.prevent="handleRegister" class="register-form">
          <div class="form-group">
            <label>用户名</label>
            <input 
              type="text" 
              v-model="form.username"
              placeholder="请输入用户名（唯一）"
              class="form-input"
              required
              @focus="handleFocus"
              @blur="handleBlur"
            />
            <span class="tip">用户名一旦创建不可更改</span>
          </div>

          <div class="form-group">
            <label>密码</label>
            <div class="password-input">
              <input 
                :type="showPassword ? 'text' : 'password'"
                v-model="form.password"
                placeholder="请输入密码（至少6位）"
                class="form-input"
                required
                minlength="6"
                @focus="handleFocus"
                @blur="handleBlur"
              />
              <button type="button" class="toggle-password" @click="showPassword = !showPassword">
                {{ showPassword ? '👁️' : '👁️‍🗨️' }}
              </button>
            </div>
          </div>

          <div class="form-group">
            <label>确认密码</label>
            <input 
              :type="showPassword ? 'text' : 'password'"
              v-model="form.confirmPassword"
              placeholder="请再次输入密码"
              class="form-input"
              required
            />
          </div>

          <div v-if="errorMsg" class="error-message">{{ errorMsg }}</div>
          <div v-if="successMsg" class="success-message">{{ successMsg }}</div>

          <button type="submit" class="register-btn" :disabled="loading">
            {{ loading ? '注册中...' : '立即注册' }}
          </button>
        </form>

        <div class="login-link">
          已有账户? 
          <router-link to="/login">立即登录</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()

const form = reactive({
  username: '',
  password: '',
  confirmPassword: ''
})

const showPassword = ref(false)
const loading = ref(false)
const errorMsg = ref('')
const successMsg = ref('')

// 小人动画
const isTyping = ref(false)
const isLookingAtEachOther = ref(false)
const isPurpleBlinking = ref(false)
const isBlackBlinking = ref(false)

const purpleRef = ref(null)
const blackRef = ref(null)
const orangeRef = ref(null)
const yellowRef = ref(null)

const purplePos = ref({ faceX: 0, faceY: 0 })
const blackPos = ref({ faceX: 0, faceY: 0 })
const orangePos = ref({ faceX: 0, faceY: 0 })
const yellowPos = ref({ faceX: 0, faceY: 0 })

let mouseX = 0, mouseY = 0

const handleMouseMove = (e) => {
  mouseX = e.clientX
  mouseY = e.clientY
  calculatePositions()
}

const calculatePositions = () => {
  // 紫色和黑色小人使用ref
  const updatePos = (ref, pos) => {
    if (ref.value) {
      const rect = ref.value.getBoundingClientRect()
      const eyeX = rect.left + rect.width / 2
      const eyeY = rect.top + rect.height / 4
      pos.value = {
        faceX: Math.max(-15, Math.min(15, (mouseX - eyeX) / 15)),
        faceY: Math.max(-10, Math.min(10, (mouseY - eyeY) / 20))
      }
    }
  }
  updatePos(purpleRef, purplePos)
  updatePos(blackRef, blackPos)
  
  // 橙色半圆小人 - 使用ref
  if (orangeRef.value) {
    const rect = orangeRef.value.getBoundingClientRect()
    const eyeX = rect.left + 100
    const eyeY = rect.top + 100
    orangePos.value = {
      faceX: Math.max(-15, Math.min(15, (mouseX - eyeX) / 15)),
      faceY: Math.max(-10, Math.min(10, (mouseY - eyeY) / 20))
    }
  }
  
  // 黄色小人 - 使用ref
  if (yellowRef.value) {
    const rect = yellowRef.value.getBoundingClientRect()
    const eyeX = rect.left + 70
    const eyeY = rect.top + 50
    yellowPos.value = {
      faceX: Math.max(-15, Math.min(15, (mouseX - eyeX) / 15)),
      faceY: Math.max(-10, Math.min(10, (mouseY - eyeY) / 20))
    }
  }
}

const startBlinking = () => {
  const loop = (ref, setBlink) => {
    setTimeout(() => {
      setBlink(true)
      setTimeout(() => {
        setBlink(false)
        loop(ref, setBlink)
      }, 150)
    }, Math.random() * 4000 + 3000)
  }
  loop(purpleRef, v => isPurpleBlinking.value = v)
  loop(blackRef, v => isBlackBlinking.value = v)
}

const handleFocus = () => {
  isTyping.value = true
  isLookingAtEachOther.value = true
  setTimeout(() => isLookingAtEachOther.value = false, 800)
}

const handleBlur = () => {
  isTyping.value = false
  isLookingAtEachOther.value = false
}

const handleRegister = async () => {
  errorMsg.value = ''
  successMsg.value = ''

  if (!form.username || !form.password) {
    errorMsg.value = '请填写完整信息'
    return
  }
  if (form.password.length < 6) {
    errorMsg.value = '密码至少需要6位'
    return
  }
  if (form.password !== form.confirmPassword) {
    errorMsg.value = '两次输入的密码不一致'
    return
  }

  loading.value = true
  try {
    const response = await fetch('http://localhost:8000/api/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: form.username, password: form.password })
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || '注册失败')
    }

    successMsg.value = '注册成功！正在跳转到登录页...'
    ElMessage.success('注册成功!')
    setTimeout(() => router.push('/login'), 1500)
  } catch (error) {
    errorMsg.value = error.message
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  window.addEventListener('mousemove', handleMouseMove)
  startBlinking()
})

onUnmounted(() => {
  window.removeEventListener('mousemove', handleMouseMove)
})
</script>

<style scoped>
.register-page {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 1fr 1fr;
  overflow: hidden;
}

.left-section {
  background: linear-gradient(135deg, #1e3a5f 0%, #2d4a6f 50%, #1a365d 100%);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 48px;
  position: relative;
  overflow: hidden;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  position: relative;
  z-index: 20;
  color: white;
  font-weight: 600;
  font-size: 18px;
}

.logo-icon {
  background: rgba(255,255,255,0.1);
  backdrop-filter: blur(10px);
  padding: 4px;
  border-radius: 8px;
  font-size: 24px;
}

.characters-container {
  position: relative;
  width: 550px;
  height: 400px;
  margin: 0 auto;
  z-index: 10;
}

.character {
  position: absolute;
  bottom: 0;
  transition: all 0.7s ease-in-out;
}

.character .eyes {
  position: absolute;
  display: flex;
  gap: 32px;
}

.eye {
  width: 18px;
  height: 18px;
  background: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.eye.blinking { height: 2px; }

.pupil {
  width: 7px;
  height: 7px;
  background: #2D2D2D;
  border-radius: 50%;
}

.pupil.small { width: 6px; height: 6px; }

.eyes-pupil {
  position: absolute;
  display: flex;
  gap: 32px;
}

.pupil-only {
  width: 12px;
  height: 12px;
  background: #2D2D2D;
  border-radius: 50%;
}

.purple {
  width: 180px;
  height: 400px;
  background: #6C3FF5;
  border-radius: 10px 10px 0 0;
  z-index: 1;
}

.black {
  width: 120px;
  height: 310px;
  background: #2D2D2D;
  border-radius: 8px 8px 0 0;
  z-index: 2;
}

.black .eyes { gap: 24px; }
.black .eye { width: 16px; height: 16px; }

.orange {
  width: 240px;
  height: 200px;
  background: #FF9B6B;
  border-radius: 120px 120px 0 0;
  z-index: 3;
}

.yellow {
  width: 140px;
  height: 230px;
  background: #E8D754;
  border-radius: 70px 70px 0 0;
  z-index: 4;
}

.yellow .eyes-pupil { gap: 24px; }

.yellow .mouth {
  position: absolute;
  width: 80px;
  height: 4px;
  background: #2D2D2D;
  border-radius: 2px;
}

.bottom-links {
  display: flex;
  gap: 32px;
  position: relative;
  z-index: 20;
}

.bottom-links a {
  color: rgba(255,255,255,0.7);
  font-size: 14px;
  text-decoration: none;
}

.bottom-links a:hover { color: white; }

.decoration-grid {
  position: absolute;
  inset: 0;
  background-image: radial-gradient(circle, rgba(255,255,255,0.05) 1px, transparent 1px);
  background-size: 20px 20px;
  pointer-events: none;
}

.circle-decor {
  position: absolute;
  border-radius: 50%;
  pointer-events: none;
}

.circle-1 {
  width: 256px;
  height: 256px;
  background: rgba(255,255,255,0.1);
  top: 25%;
  right: 25%;
  filter: blur(60px);
}

.circle-2 {
  width: 384px;
  height: 384px;
  background: rgba(255,255,255,0.05);
  bottom: 25%;
  left: 25%;
  filter: blur(80px);
}

.right-section {
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(180deg, #0a0a1a 0%, #1a1a2e 50%, #16213e 100%);
  padding: 40px;
  position: relative;
  overflow: hidden;
}

.right-section::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image: 
    radial-gradient(2px 2px at 20px 30px, #fff, rgba(0,0,0,0)),
    radial-gradient(2px 2px at 40px 70px, #fff, rgba(0,0,0,0)),
    radial-gradient(2px 2px at 50px 160px, #fff, rgba(0,0,0,0)),
    radial-gradient(2px 2px at 90px 40px, #fff, rgba(0,0,0,0)),
    radial-gradient(2px 2px at 130px 80px, #fff, rgba(0,0,0,0)),
    radial-gradient(2px 2px at 160px 120px, #fff, rgba(0,0,0,0));
  background-repeat: repeat;
  background-size: 200px 200px;
  opacity: 0.5;
}

.right-section::after {
  content: '';
  position: absolute;
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, rgba(102, 126, 234, 0.3) 0%, transparent 70%);
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  filter: blur(40px);
}

.register-container {
  width: 100%;
  max-width: 420px;
  background: rgba(10, 10, 26, 0.8);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 24px;
  padding: 40px;
  position: relative;
  z-index: 10;
}

.register-header {
  text-align: center;
  margin-bottom: 30px;
}

.register-header h2 {
  font-size: 30px;
  font-weight: 700;
  color: #ffffff;
  margin-bottom: 8px;
}

.register-header p { 
  color: rgba(255, 255, 255, 0.6); 
  font-size: 14px; 
}

.register-form {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 14px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.8);
}

.form-group .tip {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
}

.form-input {
  height: 48px;
  padding: 0 16px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  font-size: 14px;
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
  transition: all 0.2s;
}

.form-input::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.form-input::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.form-input:focus {
  outline: none;
  border-color: #667eea;
  background: rgba(255, 255, 255, 0.15);
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
}

.password-input { position: relative; width: 100%; }

.password-input .form-input { width: 100%; padding-right: 48px; }

.toggle-password {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  font-size: 16px;
}

.error-message {
  padding: 12px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  color: #dc2626;
  font-size: 14px;
}

.success-message {
  padding: 12px;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: 8px;
  color: #667eea;
  font-size: 14px;
}

.register-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 25px;
  color: white;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
  margin-top: 10px;
}

.register-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
}

.register-btn:disabled { opacity: 0.6; cursor: not-allowed; }

.login-link {
  text-align: center;
  color: rgba(255, 255, 255, 0.6);
  font-size: 14px;
  margin-top: 24px;
}

.login-link a {
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
}

@media (max-width: 1024px) {
  .left-section { display: none; }
}
</style>
