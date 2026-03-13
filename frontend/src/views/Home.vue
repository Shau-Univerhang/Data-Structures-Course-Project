<template>
  <div class="home-container">
    <!-- 导航 -->
    <nav class="navbar">
      <div class="nav-brand" @click="goHome">
        <span class="brand-icon">🌍</span>
        <span class="brand-text">邮游世界</span>
      </div>
      <div class="nav-menu">
        <a href="javascript:void(0)" class="nav-item" @click="goTrips">行程</a>
        <a href="javascript:void(0)" class="nav-item" @click="goDiary">日记</a>
        <a href="javascript:void(0)" class="nav-item" @click="goAI">AI助手</a>
        <a href="javascript:void(0)" class="nav-item" @click="goProfile">我的</a>
      </div>
    </nav>

    <!-- Hero区域 -->
    <section class="hero-section">
      <div class="hero-bg">
        <div class="stars"></div>
        <div class="glow-orb orb-1"></div>
        <div class="glow-orb orb-2"></div>
      </div>
      <div class="hero-content">
        <h1 class="hero-title">
          <span class="title-line">AI智能规划</span>
          <span class="title-line gradient">你的专属旅行</span>
        </h1>
        <p class="hero-desc">
          基于MiniMax大模型 × 自研算法<br>
          打造个性化旅游体验
        </p>
        <div class="hero-actions">
          <button class="btn-primary" @click="startPlan">
            <span class="btn-icon">🚀</span>
            开始规划
          </button>
          <button class="btn-secondary" @click="goAI">
            <span class="btn-icon">💬</span>
            AI助手
          </button>
        </div>
      </div>
      <div class="hero-visual">
        <div class="earth-container">
          <div class="earth">
            <div class="earth-layer layer-1"></div>
            <div class="earth-layer layer-2"></div>
            <div class="earth-layer layer-3"></div>
            <div class="earth-core"></div>
          </div>
          <div class="orbit orbit-1"></div>
          <div class="orbit orbit-2"></div>
          <div class="orbit orbit-3"></div>
        </div>
      </div>
    </section>

    <!-- 热门目的地 -->
    <section class="destinations-section">
      <h2 class="section-title">热门目的地</h2>
      <div class="carousel-container" @mouseenter="stopAutoPlay" @mouseleave="startAutoPlay">
        <button class="carousel-btn prev" @click="prevSlide">❮</button>
        <div class="carousel-viewport">
          <div class="carousel-track" :style="{ transform: 'translateX(' + slideOffset + 'px)' }">
            <div 
              class="dest-card" 
              v-for="dest in destinations" 
              :key="dest.name + dest.image"
              @click="goToCity(dest.name)"
            >
              <div class="dest-img" :style="{backgroundImage: 'url(' + dest.image + ')'}"></div>
              <div class="dest-info">
                <h3>{{ dest.name }}</h3>
              </div>
            </div>
          </div>
        </div>
        <button class="carousel-btn next" @click="nextSlide">❯</button>
      </div>
      <div class="carousel-dots">
        <span 
          v-for="(dot, index) in dots" 
          :key="index" 
          class="dot"
          :class="{ active: currentSlide === index }"
          @click="goToSlide(index)"
        ></span>
      </div>
    </section>

    <!-- 功能特点 -->
    <section class="features-section">
      <h2 class="section-title">核心功能</h2>
      <div class="features-grid">
        <div class="feature-card" v-for="feature in features" :key="feature.id" @click="handleFeatureClick(feature)">
          <div class="feature-icon">{{ feature.icon }}</div>
          <h3 class="feature-title">{{ feature.title }}</h3>
          <p class="feature-desc">{{ feature.desc }}</p>
          <div class="feature-tag">{{ feature.tag }}</div>
        </div>
      </div>
    </section>

    <!-- 页脚 -->
    <footer class="footer">
      <p>© 2024 邮游世界 - 北京邮电大学数据结构课程设计</p>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// Carousel state
const currentSlide = ref(0)
const cardWidth = 216
const cardGap = 30
const cardsPerSlide = 5
let autoPlayInterval = null

const slideOffset = computed(() => {
  return -currentSlide.value * (cardWidth + cardGap) * cardsPerSlide
})

const totalSlides = computed(() => {
  return Math.max(1, Math.ceil(destinations.value.length / cardsPerSlide))
})

const dots = computed(() => {
  return Array.from({ length: totalSlides.value }, (_, i) => i)
})

const nextSlide = () => {
  currentSlide.value = currentSlide.value >= totalSlides.value - 1 ? 0 : currentSlide.value + 1
}

const prevSlide = () => {
  currentSlide.value = currentSlide.value <= 0 ? totalSlides.value - 1 : currentSlide.value - 1
}

const goToSlide = (index) => {
  currentSlide.value = index
}

// Auto play
const startAutoPlay = () => {
  stopAutoPlay()
  autoPlayInterval = setInterval(() => {
    nextSlide()
  }, 4000)
}

const stopAutoPlay = () => {
  if (autoPlayInterval) {
    clearInterval(autoPlayInterval)
    autoPlayInterval = null
  }
}

onMounted(() => {
  startAutoPlay()
})

onUnmounted(() => {
  stopAutoPlay()
})

const stats = [
  { value: '205+', label: '热门景点' },
  { value: '50+', label: '特色美食' },
  { value: '210+', label: '道路数据' },
  { value: '20+', label: '城市覆盖' },
]

const features = [
  { id: 1, icon: '🤖', title: 'AI智能规划', desc: 'MiniMax大模型生成个性化行程', tag: 'TopK算法', action: 'ai' },
  { id: 2, icon: '🗺️', title: '最短路径', desc: 'Dijkstra + TSP智能路线优化', tag: 'O((V+E)logV)', action: 'route' },
  { id: 3, icon: '📍', title: '景点推荐', desc: '部分排序算法精准推荐', tag: 'Top10', action: 'spots' },
  { id: 4, icon: '📝', title: '旅游日记', desc: '无损压缩存储，全文检索', tag: 'Gzip', action: 'diary' },
  { id: 5, icon: '🍜', title: '美食推荐', desc: '基于偏好的智能推荐', tag: '模糊匹配', action: 'food' },
  { id: 6, icon: '🖼️', title: '3D地图', desc: '高德地图集成可视化', tag: 'AMap', action: 'map' },
]

const destinations = ref([
  { name: '北京', image: 'https://images.unsplash.com/photo-1599571234909-29ed5d1321d6?w=800' },
  { name: '上海', image: 'https://images.unsplash.com/photo-1474181487882-5abf3f0ba6c2?w=800' },
  { name: '西安', image: 'https://images.unsplash.com/photo-1724458589661-a2f42eb58aca?w=800' },
  { name: '成都', image: 'https://images.unsplash.com/photo-1622613744987-0e3527fae518?w=800' },
  { name: '杭州', image: 'https://images.unsplash.com/photo-1697730047280-01082430a28a?w=800' },
  { name: '重庆', image: 'https://images.unsplash.com/photo-1567014688543-cc4abffb061a?w=800' },
  { name: '青岛', image: 'https://images.unsplash.com/photo-1718085875432-98c61c603b54?w=800' },
  { name: '广州', image: 'https://images.unsplash.com/photo-1559035871-4b9dcf31885c?w=800' },
  { name: '苏州', image: 'https://images.unsplash.com/photo-1521022741625-63f57c752f95?w=800' },
  { name: '厦门', image: 'https://images.unsplash.com/photo-1660531141240-d5fb7a955822?w=800' },
  { name: '南京', image: 'https://images.unsplash.com/photo-1569517282132-25d22f4573e6?w=800' },
  { name: '武汉', image: 'https://images.unsplash.com/photo-1596496050827-8299e0220de1?w=800' },
  { name: '长沙', image: 'https://images.unsplash.com/photo-1585351363283-95e3d5041053?w=800' },
  { name: '深圳', image: 'https://images.unsplash.com/photo-1558539320-1c71c5c5d8e8?w=800' },
  { name: '三亚', image: 'https://images.unsplash.com/photo-1580821810645-11a8fd7c9f37?w=800' },
  { name: '桂林', image: 'https://images.unsplash.com/photo-1548919973-5cef591cdbc9?w=800' },
  { name: '张家界', image: 'https://images.unsplash.com/photo-1565060169194-19fabf63012f?w=800' },
  { name: '黄山', image: 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800' },
  { name: '九寨沟', image: 'https://images.unsplash.com/photo-1574169208507-84376144848b?w=800' },
  { name: '大理', image: 'https://images.unsplash.com/photo-1580821810645-11a8fd7c9f37?w=800' },
])

// 导航功能
const goHome = () => router.push('/')
const goTrips = () => router.push('/trips')
const goDiary = () => router.push('/diary')
const goAI = () => router.push('/ai')

// 检查是否登录
const checkLogin = () => {
  const userId = localStorage.getItem('userId')
  if (!userId) {
    router.push('/login')
    return false
  }
  return true
}

const goProfile = () => {
  if (!checkLogin()) return
  router.push('/profile')
}

const startPlan = () => {
  if (!checkLogin()) return
  router.push('/create-trip')
}

// 功能卡片点击
const handleFeatureClick = (feature) => {
  if (!checkLogin()) return
  
  switch(feature.action) {
    case 'ai':
      router.push('/ai')
      break
    case 'diary':
      router.push('/diary')
      break
    case 'spots':
      router.push('/spot-recommend')
      break
    case 'route':
      router.push('/route/demo')
      break
    case 'food':
      router.push('/food')
      break
    case 'map':
      router.push('/map')
      break
    default:
      router.push('/create-trip')
  }
}

// 城市点击 - 进入城市景点页面
const goToCity = (city) => {
  router.push({ path: '/city', query: { name: city } })
}
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  background: #0a0a1a;
  color: #fff;
}

/* 导航 */
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 50px;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  background: rgba(10, 10, 26, 0.8);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(0, 212, 255, 0.1);
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

.nav-menu {
  display: flex;
  gap: 30px;
}

.nav-item {
  color: rgba(255, 255, 255, 0.7);
  text-decoration: none;
  font-size: 15px;
  transition: color 0.3s;
  cursor: pointer;
}

.nav-item:hover,
.nav-item.active {
  color: #00d4ff;
}

/* Hero */
.hero-section {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 120px 50px 80px;
  position: relative;
  overflow: hidden;
}

.hero-bg {
  position: absolute;
  inset: 0;
  overflow: hidden;
}

.stars {
  position: absolute;
  inset: 0;
  background-image: 
    radial-gradient(2px 2px at 20px 30px, #fff, rgba(0,0,0,0)),
    radial-gradient(2px 2px at 40px 70px, rgba(255,255,255,0.8), rgba(0,0,0,0)),
    radial-gradient(1px 1px at 90px 40px, #fff, rgba(0,0,0,0)),
    radial-gradient(2px 2px at 130px 80px, rgba(255,255,255,0.6), rgba(0,0,0,0));
  background-size: 200px 200px;
  animation: twinkle 5s infinite;
}

@keyframes twinkle {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.glow-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.4;
}

.orb-1 {
  width: 400px;
  height: 400px;
  background: #00d4ff;
  top: -100px;
  right: 10%;
}

.orb-2 {
  width: 300px;
  height: 300px;
  background: #7b2cbf;
  bottom: -50px;
  left: 10%;
}

.hero-content {
  max-width: 600px;
  z-index: 10;
}

.hero-title {
  font-size: 56px;
  font-weight: 800;
  line-height: 1.2;
  margin-bottom: 24px;
}

.title-line {
  display: block;
}

.title-line.gradient {
  background: linear-gradient(135deg, #00d4ff, #7b2cbf, #ff6b6b);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hero-desc {
  font-size: 18px;
  color: rgba(255, 255, 255, 0.6);
  line-height: 1.8;
  margin-bottom: 40px;
}

.hero-actions {
  display: flex;
  gap: 20px;
}

.btn-primary,
.btn-secondary {
  padding: 16px 36px;
  border-radius: 30px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 10px;
  transition: all 0.3s ease;
}

.btn-primary {
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  border: none;
  color: #fff;
  box-shadow: 0 0 30px rgba(0, 212, 255, 0.4);
}

.btn-primary:hover {
  transform: translateY(-3px);
  box-shadow: 0 0 50px rgba(0, 212, 255, 0.6);
}

.btn-secondary {
  background: transparent;
  border: 2px solid rgba(0, 212, 255, 0.5);
  color: #00d4ff;
}

.btn-secondary:hover {
  background: rgba(0, 212, 255, 0.1);
  border-color: #00d4ff;
}

/* Earth Visual */
.hero-visual {
  position: relative;
  width: 500px;
  height: 500px;
}

.earth-container {
  position: relative;
  width: 100%;
  height: 100%;
}

.earth {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 280px;
  height: 280px;
  border-radius: 50%;
  background: radial-gradient(circle at 30% 30%, #00d4ff, #1a1a2e);
  box-shadow: 
    inset -30px -30px 60px rgba(0, 0, 0, 0.5),
    0 0 60px rgba(0, 212, 255, 0.5);
}

.earth-layer {
  position: absolute;
  inset: -20px;
  border-radius: 50%;
  border: 1px solid rgba(0, 212, 255, 0.2);
  animation: rotate 20s linear infinite;
}

.layer-2 {
  inset: -40px;
  animation-duration: 15s;
  animation-direction: reverse;
}

.layer-3 {
  inset: -60px;
  animation-duration: 25s;
}

.orbit {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  border-radius: 50%;
  border: 1px dashed rgba(0, 212, 255, 0.3);
  animation: rotate 30s linear infinite;
}

.orbit-1 {
  width: 350px;
  height: 350px;
}

.orbit-2 {
  width: 420px;
  height: 420px;
  animation-duration: 25s;
}

.orbit-3 {
  width: 490px;
  height: 490px;
  animation-duration: 20s;
  animation-direction: reverse;
}

/* Stats */
.stats-section {
  display: flex;
  justify-content: center;
  gap: 80px;
  padding: 60px 50px;
  background: rgba(0, 212, 255, 0.03);
}

.stat-card {
  text-align: center;
}

.stat-value {
  font-size: 42px;
  font-weight: 800;
  background: linear-gradient(135deg, #00d4ff, #fff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-label {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.5);
  margin-top: 8px;
}

/* Features */
.features-section {
  padding: 80px 50px;
}

.section-title {
  font-size: 32px;
  text-align: center;
  margin-bottom: 50px;
  background: linear-gradient(135deg, #00d4ff, #fff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 30px;
  max-width: 1200px;
  margin: 0 auto;
}

.feature-card {
  background: rgba(20, 20, 40, 0.8);
  border: 1px solid rgba(0, 212, 255, 0.2);
  border-radius: 20px;
  padding: 30px;
  transition: all 0.3s ease;
  cursor: pointer;
}

.feature-card:hover {
  transform: translateY(-10px);
  border-color: #00d4ff;
  box-shadow: 0 20px 40px rgba(0, 212, 255, 0.2);
}

.feature-icon {
  font-size: 40px;
  margin-bottom: 20px;
}

.feature-title {
  font-size: 20px;
  margin-bottom: 12px;
}

.feature-desc {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 16px;
}

.feature-tag {
  display: inline-block;
  padding: 4px 12px;
  background: rgba(0, 212, 255, 0.1);
  border-radius: 12px;
  font-size: 12px;
  color: #00d4ff;
}

/* Destinations */
.destinations-section {
  padding: 80px 50px;
}

/* Carousel styles */
.carousel-container {
  display: flex;
  align-items: center;
  gap: 10px;
  position: relative;
}

.carousel-viewport {
  overflow: hidden;
  width: calc(5 * 216px + 4 * 30px);
  margin: 0 auto;
}

.carousel-track {
  display: flex;
  gap: 30px;
  transition: transform 0.5s ease;
}

.carousel-btn {
  background: rgba(255, 255, 255, 0.1);
  border: none;
  color: white;
  font-size: 24px;
  width: 50px;
  height: 50px;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.3s;
  z-index: 10;
}

.carousel-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.1);
}

.carousel-dots {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-top: 20px;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
  cursor: pointer;
  transition: all 0.3s;
}

.dot.active {
  background: #667eea;
  transform: scale(1.3);
}

.dest-card {
  flex-shrink: 0;
  width: 216px;
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
}

.dest-card:hover {
  transform: scale(1.05);
}

.dest-img {
  height: 120px;
  background-size: cover;
  background-position: center;
}

.dest-info {
  padding: 15px;
  background: rgba(20, 20, 40, 0.9);
}

.dest-info h3 {
  font-size: 18px;
  margin-bottom: 5px;
}

.dest-info p {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
}

/* Footer */
.footer {
  text-align: center;
  padding: 40px;
  color: rgba(255, 255, 255, 0.3);
  font-size: 14px;
}
</style>
