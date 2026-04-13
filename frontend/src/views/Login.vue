<template>
  <div class="login-page">
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
        <!-- 紫色小人 - 后面 -->
        <div 
          ref="purpleRef"
          class="character purple"
          :class="{ typing: isTyping, hiding: passwordLength > 0 && !showPassword }"
          :style="{
            height: (isTyping || (passwordLength > 0 && !showPassword)) ? '440px' : '400px',
            left: '70px',
            transform: (passwordLength > 0 && showPassword) ? '' : `skewX(${(purplePos.bodySkew || 0)}deg)`
          }"
        >
          <div class="eyes" :style="{
            left: (passwordLength > 0 && showPassword) ? '20px' : isLookingAtEachOther ? '55px' : `${45 + purplePos.faceX}px`,
            top: (passwordLength > 0 && showPassword) ? '35px' : isLookingAtEachOther ? '65px' : `${40 + purplePos.faceY}px`
          }">
            <div class="eye" :class="{ blinking: isPurpleBlinking }">
              <div class="pupil" :style="getPupilStyle(purplePos, 7, 5)"></div>
            </div>
            <div class="eye" :class="{ blinking: isPurpleBlinking }">
              <div class="pupil" :style="getPupilStyle(purplePos, 7, 5)"></div>
            </div>
          </div>
        </div>

        <!-- 黑色小人 - 中间 -->
        <div 
          ref="blackRef"
          class="character black"
          :class="{ typing: isTyping }"
          :style="{
            left: '240px',
            transform: (passwordLength > 0 && showPassword) ? '' : `skewX(${(blackPos.bodySkew || 0)}deg)`
          }"
        >
          <div class="eyes" :style="{
            left: (passwordLength > 0 && showPassword) ? '10px' : isLookingAtEachOther ? '32px' : `${26 + blackPos.faceX}px`,
            top: (passwordLength > 0 && showPassword) ? '28px' : isLookingAtEachOther ? '12px' : `${32 + blackPos.faceY}px`
          }">
            <div class="eye" :class="{ blinking: isBlackBlinking }">
              <div class="pupil" :style="getPupilStyle(blackPos, 6, 4)"></div>
            </div>
            <div class="eye" :class="{ blinking: isBlackBlinking }">
              <div class="pupil" :style="getPupilStyle(blackPos, 6, 4)"></div>
            </div>
          </div>
        </div>

        <!-- 橙色半圆小人 - 前面 -->
        <div 
          ref="orangeRef"
          class="character orange"
          :style="{
            left: '0px',
            transform: (passwordLength > 0 && showPassword) ? '' : `skewX(${(orangePos.bodySkew || 0)}deg)`
          }"
        >
          <div class="eyes-pupil" :style="{
            left: (passwordLength > 0 && showPassword) ? '50px' : `${82 + (orangePos.faceX || 0)}px`,
            top: (passwordLength > 0 && showPassword) ? '85px' : `${90 + (orangePos.faceY || 0)}px`
          }">
            <div class="pupil-only" :style="(passwordLength > 0 && showPassword) ? { transform: 'translateX(-5px)' } : {}"></div>
            <div class="pupil-only" :style="(passwordLength > 0 && showPassword) ? { transform: 'translateX(-5px)' } : {}"></div>
          </div>
        </div>

        <!-- 黄色小人 - 前面 -->
        <div 
          ref="yellowRef"
          class="character yellow"
          :style="{
            left: '310px',
            transform: (passwordLength > 0 && showPassword) ? '' : `skewX(${(yellowPos.bodySkew || 0)}deg)`
          }"
        >
          <div class="eyes-pupil" :style="{
            left: (passwordLength > 0 && showPassword) ? '20px' : `${52 + (yellowPos.faceX || 0)}px`,
            top: (passwordLength > 0 && showPassword) ? '35px' : `${40 + (yellowPos.faceY || 0)}px`
          }">
            <div class="pupil-only" :style="(passwordLength > 0 && showPassword) ? { transform: 'translateX(-5px)' } : {}"></div>
            <div class="pupil-only" :style="(passwordLength > 0 && showPassword) ? { transform: 'translateX(-5px)' } : {}"></div>
          </div>
          <div class="mouth" :style="(passwordLength > 0 && showPassword) ? { left: '10px', top: '88px' } : { left: `${40 + (yellowPos.faceX || 0)}px`, top: `${88 + (yellowPos.faceY || 0)}px` }"></div>
        </div>
      </div>

      <!-- 装饰元素 -->
      <div class="decoration-grid"></div>
      <div class="circle-decor circle-1"></div>
      <div class="circle-decor circle-2"></div>
    </div>

    <!-- 右侧 - 登录表单 -->
    <div class="right-section">
      <div class="login-container">
        <div class="login-header">
          <h2>欢迎回来!</h2>
          <p>请输入您的账户信息</p>
        </div>

        <form @submit.prevent="handleLogin" class="login-form">
          <div class="form-group">
            <label>用户名</label>
            <input 
              type="text" 
              v-model="form.username"
              placeholder="请输入用户名"
              class="form-input"
              required
              @focus="handleFocus"
              @blur="handleBlur"
            />
          </div>

          <div class="form-group">
            <label>密码</label>
            <div class="password-input">
              <input 
                :type="showPassword ? 'text' : 'password'"
                v-model="form.password"
                placeholder="请输入密码"
                class="form-input"
                required
                @input="handlePasswordInput"
                @focus="handleFocus"
                @blur="handleBlur"
              />
              <button type="button" class="toggle-password" @click="showPassword = !showPassword">
                {{ showPassword ? '👁️' : '👁️‍🗨️' }}
              </button>
            </div>
          </div>

          <div class="form-options">
            <label class="checkbox-label">
              <input type="checkbox" v-model="rememberMe" />
              <span>30天内免登录</span>
            </label>
            <a href="#" class="forgot-link">忘记密码?</a>
          </div>

          <div v-if="errorMsg" class="error-message">
            {{ errorMsg }}
          </div>

          <button type="submit" class="login-btn" :disabled="loading">
            {{ loading ? '登录中...' : '登录' }}
          </button>
        </form>

        <div class="divider">
          <span>或</span>
        </div>

        <div class="register-link">
          还没有账户? 
          <router-link to="/register">立即注册</router-link>
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
  password: ''
})

const showPassword = ref(false)
const rememberMe = ref(false)
const loading = ref(false)
const errorMsg = ref('')

// 小人动画相关
const isTyping = ref(false)
const isLookingAtEachOther = ref(false)
const isPurpleBlinking = ref(false)
const isBlackBlinking = ref(false)
const passwordLength = ref(0)

// refs
const purpleRef = ref(null)
const blackRef = ref(null)
const orangeRef = ref(null)
const yellowRef = ref(null)

// 位置计算
const purplePos = ref({ faceX: 0, faceY: 0, bodySkew: 0 })
const blackPos = ref({ faceX: 0, faceY: 0, bodySkew: 0 })
const orangePos = ref({ faceX: 0, faceY: 0, bodySkew: 0 })
const yellowPos = ref({ faceX: 0, faceY: 0, bodySkew: 0 })

let mouseX = 0
let mouseY = 0

const handleMouseMove = (e) => {
  mouseX = e.clientX
  mouseY = e.clientY
  calculatePositions()
}

const calculatePositions = () => {
  // 使用窗口中心点作为参考
  const windowCenterX = window.innerWidth / 2
  const windowCenterY = window.innerHeight / 2
  
  // 紫色小人位置 - 基于窗口位置
  if (purpleRef.value) {
    const rect = purpleRef.value.getBoundingClientRect()
    const eyeX = rect.left + 90
    const eyeY = rect.top + 60
    const deltaX = mouseX - eyeX
    const deltaY = mouseY - eyeY
    purplePos.value = {
      faceX: Math.max(-15, Math.min(15, deltaX / 15)),
      faceY: Math.max(-10, Math.min(10, deltaY / 20)),
      bodySkew: Math.max(-6, Math.min(6, -deltaX / 100))
    }
  }
  
  // 黑色小人位置
  if (blackRef.value) {
    const rect = blackRef.value.getBoundingClientRect()
    const eyeX = rect.left + 60
    const eyeY = rect.top + 50
    const deltaX = mouseX - eyeX
    const deltaY = mouseY - eyeY
    blackPos.value = {
      faceX: Math.max(-15, Math.min(15, deltaX / 15)),
      faceY: Math.max(-10, Math.min(10, deltaY / 20)),
      bodySkew: Math.max(-6, Math.min(6, -deltaX / 100))
    }
  }
  
  // 橙色半圆小人 - 使用ref
  if (orangeRef.value) {
    const rect = orangeRef.value.getBoundingClientRect()
    const eyeX = rect.left + 100
    const eyeY = rect.top + 100
    const deltaX = mouseX - eyeX
    const deltaY = mouseY - eyeY
    orangePos.value = {
      faceX: Math.max(-15, Math.min(15, deltaX / 15)),
      faceY: Math.max(-10, Math.min(10, deltaY / 20)),
      bodySkew: Math.max(-6, Math.min(6, -deltaX / 100))
    }
  }
  
  // 黄色小人 - 使用ref
  if (yellowRef.value) {
    const rect = yellowRef.value.getBoundingClientRect()
    const eyeX = rect.left + 70
    const eyeY = rect.top + 50
    const deltaX = mouseX - eyeX
    const deltaY = mouseY - eyeY
    yellowPos.value = {
      faceX: Math.max(-15, Math.min(15, deltaX / 15)),
      faceY: Math.max(-10, Math.min(10, deltaY / 20)),
      bodySkew: Math.max(-6, Math.min(6, -deltaX / 100))
    }
  }
}

const getPupilStyle = (pos, size, maxDist) => {
  if (passwordLength.value > 0 && showPassword.value) {
    return { transform: 'translate(-4px, -4px)' }
  }
  if (isLookingAtEachOther.value) {
    return { transform: 'translate(3px, 4px)' }
  }
  return {}
}

// 眨眼动画
const startBlinking = () => {
  const schedulePurpleBlink = () => {
    const delay = Math.random() * 4000 + 3000
    setTimeout(() => {
      isPurpleBlinking.value = true
      setTimeout(() => {
        isPurpleBlinking.value = false
        schedulePurpleBlink()
      }, 150)
    }, delay)
  }
  schedulePurpleBlink()

  const scheduleBlackBlink = () => {
    const delay = Math.random() * 4000 + 3000
    setTimeout(() => {
      isBlackBlinking.value = true
      setTimeout(() => {
        isBlackBlinking.value = false
        scheduleBlackBlink()
      }, 150)
    }, delay)
  }
  scheduleBlackBlink()
}

const handleFocus = () => {
  isTyping.value = true
  isLookingAtEachOther.value = true
  setTimeout(() => {
    isLookingAtEachOther.value = false
  }, 800)
}

const handleBlur = () => {
  isTyping.value = false
  isLookingAtEachOther.value = false
}

const handlePasswordInput = (e) => {
  passwordLength.value = e.target.value.length
}

const handleLogin = async () => {
  if (!form.username || !form.password) {
    errorMsg.value = '请填写用户名和密码'
    return
  }

  loading.value = true
  errorMsg.value = ''

  try {
    const response = await fetch('http://localhost:8000/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: form.username, password: form.password })
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || '登录失败')
    }

    const user = await response.json()
    localStorage.setItem('user', JSON.stringify(user))
    localStorage.setItem('userId', user.id)
    localStorage.setItem('username', user.username || user.name || user.email || '用户' + user.id)
    if (user.avatar_url) {
      localStorage.setItem('avatar_url', user.avatar_url)
    }
    ElMessage.success('登录成功!')
    router.push('/')
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
.login-page {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 1fr 1fr;
  overflow: hidden;
}

/* 左侧区域 - 完全复刻 careercompass */
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

/* 小人容器 */
.characters-container {
  position: relative;
  width: 550px;
  height: 400px;
  margin: 0 auto;
  z-index: 10;
}

/* 通用小人样式 */
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

.eye.blinking {
  height: 2px;
}

.pupil {
  width: 7px;
  height: 7px;
  background: #2D2D2D;
  border-radius: 50%;
  transition: transform 0.1s ease-out;
}

/* 橙色和黄色小人的眼睛 */
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

/* 紫色小人 */
.purple {
  width: 180px;
  height: 400px;
  background: #6C3FF5;
  border-radius: 10px 10px 0 0;
  z-index: 1;
}

.purple.typing, .purple.hiding {
  transform: skewX(-12deg) translateX(40px) !important;
}

/* 黑色小人 */
.black {
  width: 120px;
  height: 310px;
  background: #2D2D2D;
  border-radius: 8px 8px 0 0;
  z-index: 2;
}

.black .eyes {
  gap: 24px;
}

.black .eye {
  width: 16px;
  height: 16px;
}

.black .pupil {
  width: 6px;
  height: 6px;
}

/* 橙色半圆小人 */
.orange {
  width: 240px;
  height: 200px;
  background: #FF9B6B;
  border-radius: 120px 120px 0 0;
  z-index: 3;
}

.orange .eyes-pupil {
  gap: 32px;
}

/* 黄色小人 */
.yellow {
  width: 140px;
  height: 230px;
  background: #E8D754;
  border-radius: 70px 70px 0 0;
  z-index: 4;
}

.yellow .eyes-pupil {
  gap: 24px;
}

.yellow .mouth {
  position: absolute;
  width: 80px;
  height: 4px;
  background: #2D2D2D;
  border-radius: 2px;
}

/* 底部链接 */
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

.bottom-links a:hover {
  color: white;
}

/* 装饰 */
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

/* 右侧登录区 */
.right-section {
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(180deg, #0a0a1a 0%, #1a1a2e 50%, #16213e 100%);
  padding: 40px;
  position: relative;
  overflow: hidden;
}

/* 宇宙背景装饰 */
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
  animation: twinkle 5s ease-in-out infinite alternate;
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

@keyframes twinkle {
  0% { opacity: 0.3; }
  100% { opacity: 0.7; }
}

.login-container {
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

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.login-header h2 {
  font-size: 30px;
  font-weight: 700;
  color: #ffffff;
  margin-bottom: 8px;
}

.login-header p {
  color: rgba(255, 255, 255, 0.6);
  font-size: 14px;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
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

.password-input {
  position: relative;
  width: 100%;
}

.password-input .form-input {
  width: 100%;
  padding-right: 48px;
}

/* 隐藏密码输入框右侧的小眼睛图标 */
.toggle-password {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  font-size: 16px;
  opacity: 0.6;
  z-index: 10;
}

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

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
  cursor: pointer;
}

.forgot-link {
  font-size: 14px;
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
}

.error-message {
  padding: 12px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  color: #dc2626;
  font-size: 14px;
}

.login-btn {
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
}

.login-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
}

.login-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.divider {
  display: flex;
  align-items: center;
  margin: 24px 0;
}

.divider::before, .divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: rgba(255, 255, 255, 0.1);
}

.divider span {
  padding: 0 16px;
  color: rgba(255, 255, 255, 0.4);
  font-size: 14px;
}

.register-link {
  text-align: center;
  color: rgba(255, 255, 255, 0.6);
  font-size: 14px;
}

.register-link a {
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
}

/* 响应式 */
@media (max-width: 1024px) {
  .left-section {
    display: none;
  }
}
</style>
