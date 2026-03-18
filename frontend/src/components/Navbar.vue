<template>
  <nav class="navbar" :class="{ transparent: isHome }">
    <div class="nav-brand" @click="goHome">
      <span class="brand-icon">🌍</span>
      <span class="brand-text" :class="{ 'text-white': isHome }">邮游世界</span>
    </div>
    <div class="nav-menu">
      <button class="nav-btn" :class="{ active: currentRoute === 'home' }" @click="goHome">主页</button>
      <button class="nav-btn" :class="{ active: currentRoute === 'plan' }" @click="goPlan">旅行规划</button>
      <button class="nav-btn" :class="{ active: currentRoute === 'explore' }" @click="goExplore">探索</button>
      <button class="nav-btn" :class="{ active: currentRoute === 'diary' }" @click="goDiary">日记</button>
      <button class="nav-btn" :class="{ active: currentRoute === 'ai' }" @click="goAI">AI助手</button>
      <button class="nav-btn" :class="{ active: currentRoute === 'route' }" @click="goRoute">最短路径</button>
      <button class="nav-btn" :class="{ active: currentRoute === 'profile' }" @click="goProfile">我的</button>
    </div>
  </nav>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

// 判断是否在主页
const isHome = computed(() => route.path === '/')

// 根据当前路由判断哪个按钮应该高亮
const currentRoute = computed(() => {
  const path = route.path
  if (path === '/') return 'home'
  if (path === '/trips' || path === '/create-trip' || path.startsWith('/trip')) return 'plan'
  if (path === '/explore' || path === '/spot-recommend' || path === '/food') return 'explore'
  if (path === '/diary') return 'diary'
  if (path === '/ai') return 'ai'
  if (path.startsWith('/route')) return 'route'
  if (path === '/profile' || path === '/setting' || path === '/photos' || path === '/collection') return 'profile'
  return ''
})

// 检查登录状态
const checkLogin = () => {
  const userId = localStorage.getItem("userId")
  if (!userId) {
    router.push("/login")
    return false
  }
  return true
}

// 导航功能
const goHome = () => router.push('/')

const goPlan = () => {
  if (!checkLogin()) return
  router.push('/trips')
}

const goExplore = () => {
  router.push('/explore')
}

const goDiary = () => {
  if (!checkLogin()) return
  router.push('/diary')
}

const goAI = () => {
  router.push('/ai')
}

const goRoute = () => {
  if (!checkLogin()) return
  router.push('/route/demo')
}

const goProfile = () => {
  if (!checkLogin()) return
  router.push('/profile')
}
</script>

<style scoped>
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 60px;
  background: rgba(10, 10, 26, 0.9);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(0, 212, 255, 0.1);
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
}

.navbar.transparent {
  background: linear-gradient(to bottom, rgba(0, 0, 0, 0.4), transparent);
  border-bottom: none;
  backdrop-filter: none;
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}

.brand-icon {
  font-size: 28px;
}

.brand-text {
  font-size: 22px;
  font-weight: 700;
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.brand-text.text-white {
  background: none;
  -webkit-text-fill-color: #fff;
  color: #fff;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}

.nav-menu {
  display: flex;
  gap: 12px;
  align-items: center;
}

.nav-btn {
  padding: 10px 24px;
  border-radius: 30px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  color: #fff;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.nav-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.5);
  transform: translateY(-2px);
}

.nav-btn.active {
  background: #fff;
  color: #333;
  border-color: #fff;
}

@media (max-width: 1200px) {
  .navbar {
    padding: 20px 30px;
  }

  .nav-menu {
    gap: 8px;
  }

  .nav-btn {
    padding: 8px 16px;
    font-size: 13px;
  }
}

@media (max-width: 768px) {
  .navbar {
    padding: 16px 20px;
  }
  
  .nav-menu {
    display: none;
  }
}
</style>
