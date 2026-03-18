<template>
  <div class="home-container">
    <!-- 全屏风景背景 -->
    <div class="hero-background">
      <img :src="backgroundImage" alt="background" class="bg-image" />
      <div class="bg-overlay"></div>
    </div>

    <!-- 导航栏 -->
    <Navbar />

    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 左侧标语区 -->
      <div class="hero-content">
        <h1 class="hero-title">
          <span class="title-main">跨越山海</span>
          <span class="title-sub">丈量世界之美</span>
        </h1>
        <p class="hero-desc">
          智能规划你的专属旅行路线<br />
          探索未知的美食与风景
        </p>
      </div>
    </div>

    <!-- 底部城市轮播 -->
    <div class="carousel-section">
      <div class="carousel-container">
        <button class="carousel-nav prev" @click="prevSlide">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="15 18 9 12 15 6"></polyline>
          </svg>
        </button>

        <div 
          class="carousel-track"
          @mouseleave="onCarouselMouseLeave"
        >
          <div
            class="city-card"
            v-for="(dest, index) in visibleDestinations"
            :key="dest.name"
            :class="{ active: index === 1 }"
            @click="goToCity(dest.name)"
            @mouseenter="onCityHover(dest.name)"
          >
            <img :src="dest.image" :alt="dest.name" class="city-image" />
            <div class="city-info">
              <span class="city-name">{{ dest.name }}</span>
            </div>
          </div>
        </div>

        <button class="carousel-nav next" @click="nextSlide">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="9 18 15 12 9 6"></polyline>
          </svg>
        </button>
      </div>

      <!-- 轮播指示器 -->
      <div class="carousel-dots">
        <span
          v-for="(_, index) in destinations"
          :key="index"
          class="dot"
          :class="{ active: activeIndex === index }"
          @click="goToSlide(index)"
        ></span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";
import { useRouter } from "vue-router";
import Navbar from "../components/Navbar.vue";

const router = useRouter();
const activeIndex = ref(0);
let autoPlayTimer = null;
let hoverTimeout = null;

// 背景图片路径
const backgroundImage = '/images/background/test01.jpg'

// 城市数据 - 使用相对路径
const destinations = ref([
  { name: "北京", image: "/images/cities/beijing.jpg" },
  { name: "上海", image: "/images/cities/shanghai.jpg" },
  { name: "西安", image: "/images/cities/xian.jpg" },
  { name: "成都", image: "/images/cities/chengdu.jpg" },
  { name: "杭州", image: "/images/cities/hangzhou.jpg" },
  { name: "重庆", image: "/images/cities/chongqing.jpg" },
  { name: "青岛", image: "/images/cities/qingdao.jpg" },
  { name: "广州", image: "/images/cities/guangzhou.jpg" },
  { name: "苏州", image: "/images/cities/suzhou.jpg" },
  { name: "厦门", image: "/images/cities/xiamen.jpg" },
  { name: "南京", image: "/images/cities/nanjing.jpg" },
  { name: "武汉", image: "/images/cities/wuhan.jpg" },
  { name: "长沙", image: "/images/cities/changsha.jpg" },
  { name: "深圳", image: "/images/cities/shenzhen.jpg" },
  { name: "三亚", image: "/images/cities/sanya.jpg" },
  { name: "桂林", image: "/images/cities/guilin.jpg" },
  { name: "张家界", image: "/images/cities/zhangjiajie.jpg" },
  { name: "黄山", image: "/images/cities/huangshan.jpg" },
  { name: "九寨沟", image: "/images/cities/jiuzhaigou.jpg" },
  { name: "大理", image: "/images/cities/dali.jpg" },
  { name: "丽江", image: "/images/cities/lijiang.jpg" },
]);

// 计算可见的城市（显示5个）
const visibleDestinations = computed(() => {
  const result = [];
  const total = destinations.value.length;
  for (let i = -2; i <= 2; i++) {
    const index = (activeIndex.value + i + total) % total;
    result.push(destinations.value[index]);
  }
  return result;
});

// 轮播控制
const nextSlide = () => {
  activeIndex.value = (activeIndex.value + 1) % destinations.value.length;
};

const prevSlide = () => {
  activeIndex.value = (activeIndex.value - 1 + destinations.value.length) % destinations.value.length;
};

const goToSlide = (index) => {
  activeIndex.value = index;
};

// 鼠标悬停城市卡片 - 跳转到该城市（带延迟）
const onCityHover = (cityName) => {
  stopAutoPlay();
  // 清除之前的定时器
  if (hoverTimeout) {
    clearTimeout(hoverTimeout);
  }
  // 延迟 300ms 后跳转
  hoverTimeout = setTimeout(() => {
    const index = destinations.value.findIndex(d => d.name === cityName);
    if (index !== -1) {
      activeIndex.value = index;
    }
  }, 300);
};

const onCarouselMouseLeave = () => {
  // 清除悬停定时器
  if (hoverTimeout) {
    clearTimeout(hoverTimeout);
    hoverTimeout = null;
  }
  startAutoPlay();
};

// 自动播放
const startAutoPlay = () => {
  autoPlayTimer = setInterval(() => {
    nextSlide();
  }, 4000);
};

const stopAutoPlay = () => {
  if (autoPlayTimer) {
    clearInterval(autoPlayTimer);
    autoPlayTimer = null;
  }
};

onMounted(() => {
  startAutoPlay();
});

onUnmounted(() => {
  stopAutoPlay();
  if (hoverTimeout) {
    clearTimeout(hoverTimeout);
  }
});

const goToCity = (city) => {
  router.push({ path: "/city", query: { name: city } });
};
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  position: relative;
  overflow: hidden;
}

/* 全屏背景 */
.hero-background {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
}

.bg-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.bg-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    to bottom,
    rgba(0, 0, 0, 0.3) 0%,
    rgba(0, 0, 0, 0.2) 50%,
    rgba(0, 0, 0, 0.5) 100%
  );
}

/* 主内容区 */
.main-content {
  position: relative;
  z-index: 10;
  min-height: 100vh;
  display: flex;
  align-items: center;
  padding: 120px 60px 300px;
}

.hero-content {
  max-width: 500px;
  color: #fff;
}

.hero-title {
  font-size: 56px;
  font-weight: 700;
  line-height: 1.2;
  margin-bottom: 20px;
}

.title-main {
  display: block;
}

.title-sub {
  display: block;
  font-weight: 300;
  opacity: 0.9;
}

.hero-desc {
  font-size: 18px;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.8;
  margin-bottom: 40px;
}

/* 底部轮播区 */
.carousel-section {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 20;
  padding: 40px 60px 60px;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.6), transparent);
}

.carousel-container {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
}

.carousel-nav {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.carousel-nav:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.5);
}

.carousel-nav svg {
  width: 20px;
  height: 20px;
}

.carousel-track {
  display: flex;
  gap: 16px;
  align-items: center;
  justify-content: center;
  cursor: grab;
}

.carousel-track:active {
  cursor: grabbing;
}

.city-card {
  width: 160px;
  height: 200px;
  border-radius: 16px;
  overflow: hidden;
  position: relative;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
  flex-shrink: 0;
  opacity: 0.6;
  transform: scale(0.9);
}

.city-card:nth-child(2),
.city-card:nth-child(4) {
  opacity: 0.8;
  transform: scale(0.95);
}

.city-card:nth-child(3) {
  opacity: 1;
  transform: scale(1);
  width: 180px;
  height: 240px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
}

.city-card:hover {
  transform: scale(1.05);
  opacity: 1;
}

.city-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s ease;
}

.city-card:hover .city-image {
  transform: scale(1.1);
}

.city-info {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 16px;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.7), transparent);
}

.city-name {
  color: #fff;
  font-size: 16px;
  font-weight: 600;
}

/* 轮播指示器 */
.carousel-dots {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-top: 24px;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
  cursor: pointer;
  transition: all 0.3s ease;
}

.dot.active {
  background: #fff;
  width: 24px;
  border-radius: 4px;
}

.dot:hover {
  background: rgba(255, 255, 255, 0.6);
}

/* 响应式 */
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

  .main-content {
    padding: 100px 30px 280px;
  }

  .hero-title {
    font-size: 42px;
  }

  .carousel-section {
    padding: 30px 30px 40px;
  }

  .city-card {
    width: 120px;
    height: 160px;
  }

  .city-card:nth-child(3) {
    width: 140px;
    height: 180px;
  }
}

@media (max-width: 768px) {
  .navbar {
    flex-direction: column;
    gap: 16px;
    padding: 16px 20px;
  }

  .nav-menu {
    flex-wrap: wrap;
    justify-content: center;
  }

  .main-content {
    padding: 140px 20px 260px;
    justify-content: center;
    text-align: center;
  }

  .hero-content {
    max-width: 100%;
  }

  .carousel-track {
    gap: 10px;
  }

  .city-card {
    width: 100px;
    height: 130px;
  }

  .city-card:nth-child(3) {
    width: 110px;
    height: 140px;
  }

  .carousel-nav {
    width: 36px;
    height: 36px;
  }
}
</style>
