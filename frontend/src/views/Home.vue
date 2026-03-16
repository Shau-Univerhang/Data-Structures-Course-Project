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
    <section class="destinations-section" ref="sectionRef">
      <h2 class="section-title">热门目的地</h2>
      <div class="immersive-carousel" @mouseenter="stopAutoPlay" @mouseleave="startAutoPlay">
        <button class="nav-btn prev" @click="prevSlide">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="15 18 9 12 15 6"></polyline>
          </svg>
        </button>
        
        <div class="cards-container">
          <div 
            class="destination-card" 
            v-for="(dest, index) in destinations" 
            :key="dest.name + dest.image"
            :class="{ 
              'is-active': index === currentSlide,
              'is-prev': index === prevIndex,
              'is-prev-2': index === prevIndex2,
              'is-next': index === nextIndex,
              'is-next-2': index === nextIndex2
            }"
            @click="goToCity(dest.name)"
          >
            <div class="card-image">
              <img :src="dest.image" :alt="dest.name" />
            </div>
            <div class="card-overlay">
              <h3 class="card-title">{{ dest.name }}</h3>
            </div>
          </div>
        </div>
        
        <button class="nav-btn next" @click="nextSlide">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="9 18 15 12 9 6"></polyline>
          </svg>
        </button>
      </div>
      
      <div class="progress-bar" :key="currentSlide">
        <div 
          class="progress-track"
          v-for="(dot, index) in dots" 
          :key="index"
          @click="goToSlide(index)"
        >
          <div 
            class="progress-fill"
            :class="{ active: currentSlide === index }"
          ></div>
        </div>
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
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// Carousel state
const currentSlide = ref(0)
const cardWidth = 216
const cardGap = 30
const cardsPerSlide = 5
let autoPlayInterval = null

const prevIndex = computed(() => {
  return (currentSlide.value - 1 + destinations.value.length) % destinations.value.length
})

const prevIndex2 = computed(() => {
  return (currentSlide.value - 2 + destinations.value.length) % destinations.value.length
})

const nextIndex = computed(() => {
  return (currentSlide.value + 1) % destinations.value.length
})

const nextIndex2 = computed(() => {
  return (currentSlide.value + 2) % destinations.value.length
})

const currentBgImage = computed(() => {
  if (destinations.value[currentSlide.value]) {
    return `url(${destinations.value[currentSlide.value].image})`
  }
  return ''
})

const sectionRef = ref(null)
watch(currentSlide, () => {
  if (sectionRef.value) {
    sectionRef.value.style.setProperty('--bg-blur', currentBgImage.value)
  }
})

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
  }, 5000)
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
  { name: '北京', image: '/images/cities/beijing.jpg' },
  { name: '上海', image: '/images/cities/shanghai.jpg' },
  { name: '西安', image: '/images/cities/xian.jpg' },
  { name: '成都', image: '/images/cities/chengdu.jpg' },
  { name: '杭州', image: '/images/cities/hangzhou.jpg' },
  { name: '重庆', image: '/images/cities/chongqing.jpg' },
  { name: '青岛', image: '/images/cities/qingdao.jpg' },
  { name: '广州', image: '/images/cities/guangzhou.jpg' },
  { name: '苏州', image: '/images/cities/suzhou.jpg' },
  { name: '厦门', image: '/images/cities/xiamen.jpg' },
  { name: '南京', image: '/images/cities/nanjing.jpg' },
  { name: '武汉', image: '/images/cities/wuhan.jpg' },
  { name: '长沙', image: '/images/cities/changsha.jpg' },
  { name: '深圳', image: '/images/cities/shenzhen.jpg' },
  { name: '三亚', image: '/images/cities/sanya.jpg' },
  { name: '桂林', image: '/images/cities/guilin.jpg' },
  { name: '张家界', image: '/images/cities/zhangjiajie.jpg' },
  { name: '黄山', image: '/images/cities/huangshan.jpg' },
  { name: '九寨沟', image: '/images/cities/jiuzhaigou.jpg' },
  { name: '大理', image: '/images/cities/dali.jpg' },
  { name: '丽江', image: '/images/cities/lijiang.jpg' },
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
  position: relative;
  min-height: 700px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  overflow: hidden;
}

.destinations-section::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #0a0a1a 0%, #0f1923 50%, #0a0a1a 100%);
  background-size: cover;
  background-position: center;
  filter: blur(30px);
  transform: scale(1.2);
  z-index: 0;
  transition: background 0.8s ease;
}

.destinations-section > * {
  position: relative;
  z-index: 1;
}

/* Immersive Carousel */
.immersive-carousel {
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  height: 500px;
  margin-top: 40px;
  perspective: 1500px;
}

.cards-container {
  display: flex;
  align-items: center;
  justify-content: center;
  transform-style: preserve-3d;
  gap: 30px;
}

/* Destination Card - 3D Stacking */
.destination-card {
  position: absolute;
  width: 270px;
  height: 360px;
  border-radius: 24px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.7s cubic-bezier(0.34, 1.56, 0.64, 1);
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
}

/* Active (center) card - 3:4 ratio */
.destination-card.is-active {
  width: 300px;
  height: 400px;
  transform: translateX(0) scale(1) translateZ(50px);
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.8), 0 0 60px rgba(102, 126, 234, 0.3);
  z-index: 10;
}

/* Previous cards */
.destination-card.is-prev {
  transform: translateX(-180px) scale(0.85) translateZ(-30px);
  opacity: 0.5;
  z-index: 5;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
}

.destination-card.is-prev-2 {
  transform: translateX(-340px) scale(0.7) translateZ(-60px);
  opacity: 0.2;
  z-index: 3;
}

/* Next cards */
.destination-card.is-next {
  transform: translateX(180px) scale(0.85) translateZ(-30px);
  opacity: 0.5;
  z-index: 5;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
}

.destination-card.is-next-2 {
  transform: translateX(340px) scale(0.7) translateZ(-60px);
  opacity: 0.2;
  z-index: 3;
}

/* Card Image */
.card-image {
  position: absolute;
  inset: 0;
  overflow: hidden;
}

.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.destination-card:hover .card-image img {
  transform: scale(1.1);
}

/* Card Overlay */
.card-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 40%;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.7) 0%, rgba(0, 0, 0, 0.3) 50%, transparent 100%);
  display: flex;
  align-items: flex-end;
  padding: 24px;
}

.card-title {
  font-size: 32px;
  font-weight: 700;
  color: white;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.destination-card.is-active .card-title {
  animation: titleFadeIn 0.6s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
}

@keyframes titleFadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.destination-card:hover .card-title {
  transform: translateY(-5px);
  text-shadow: 0 0 20px rgba(255, 255, 255, 0.5), 0 2px 10px rgba(0, 0, 0, 0.5);
}

/* Navigation Buttons */
.nav-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  z-index: 20;
}

.nav-btn.prev { left: 5%; }
.nav-btn.next { right: 5%; }

.nav-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-50%) scale(1.1);
  border-color: rgba(255, 255, 255, 0.4);
}

.nav-btn svg {
  width: 24px;
  height: 24px;
}

/* Progress Bar */
.progress-bar {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-top: 50px;
}

.progress-track {
  width: 40px;
  height: 4px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 2px;
  cursor: pointer;
  overflow: hidden;
}

.progress-fill {
  width: 0;
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  border-radius: 2px;
  transition: width 0s;
}

.progress-fill.active {
  width: 100%;
  animation: progressFill 5s linear forwards;
}

@keyframes progressFill {
  from {
    width: 0;
  }
  to {
    width: 100%;
  }
}

/* Footer */
.footer {
  text-align: center;
  padding: 40px;
  color: rgba(255, 255, 255, 0.3);
  font-size: 14px;
}
</style>
