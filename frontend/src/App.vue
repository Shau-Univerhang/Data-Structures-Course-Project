<template>
  <div class="app-container">
    <router-view v-slot="{ Component }">
      <transition name="fade" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

onMounted(() => {
  // 可以在这里检查登录状态等
})
</script>

<style>
/* 全局高科技感样式 */
:root {
  --primary-color: #00d4ff;
  --secondary-color: #7b2cbf;
  --accent-color: #ff6b6b;
  --bg-dark: #0a0a1a;
  --bg-card: rgba(20, 20, 40, 0.8);
  --text-primary: #ffffff;
  --text-secondary: #a0a0b0;
  --border-color: rgba(0, 212, 255, 0.3);
  --glow-color: rgba(0, 212, 255, 0.5);
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Noto Sans SC', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: linear-gradient(135deg, #0a0a1a 0%, #1a1a2e 50%, #16213e 100%);
  min-height: 100vh;
  color: var(--text-primary);
  overflow-x: hidden;
}

/* 滚动条美化 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: var(--bg-dark);
}

::-webkit-scrollbar-thumb {
  background: var(--primary-color);
  border-radius: 3px;
}

/* 页面过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 科技感按钮 */
.tech-button {
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  border: none;
  border-radius: 25px;
  padding: 12px 30px;
  color: white;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
  box-shadow: 0 0 20px var(--glow-color);
}

.tech-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 0 30px var(--glow-color);
}

.tech-button:active {
  transform: translateY(0);
}

/* 科技感卡片 */
.tech-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 20px;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.tech-card:hover {
  border-color: var(--primary-color);
  box-shadow: 0 0 30px rgba(0, 212, 255, 0.2);
  transform: translateY(-5px);
}

/* 科技感输入框 */
.tech-input {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 12px 16px;
  color: var(--text-primary);
  font-size: 14px;
  width: 100%;
  transition: all 0.3s ease;
}

.tech-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 15px var(--glow-color);
}

.tech-input::placeholder {
  color: var(--text-secondary);
}

/* 标签样式 */
.tech-tag {
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.2), rgba(123, 44, 191, 0.2));
  border: 1px solid var(--border-color);
  border-radius: 20px;
  padding: 6px 16px;
  font-size: 14px;
  color: var(--primary-color);
  cursor: pointer;
  transition: all 0.3s ease;
}

.tech-tag:hover,
.tech-tag.active {
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  color: white;
  box-shadow: 0 0 20px var(--glow-color);
}

/* 页面标题 */
.page-title {
  font-size: 24px;
  font-weight: 700;
  background: linear-gradient(135deg, var(--primary-color), #ffffff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 20px;
}

/* Element Plus 覆盖样式 */
.el-button--primary {
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color)) !important;
  border: none !important;
}

.el-input__wrapper {
  background: rgba(255, 255, 255, 0.05) !important;
  border: 1px solid var(--border-color) !important;
  box-shadow: none !important;
}

.el-input__inner {
  color: var(--text-primary) !important;
}

.el-slider__runway {
  background: rgba(255, 255, 255, 0.1) !important;
}

.el-slider__bar {
  background: linear-gradient(90deg, var(--primary-color), var(--secondary-color)) !important;
}

.el-slider__button {
  border-color: var(--primary-color) !important;
}
</style>
