<template>
  <div class="amap-example-page">
    <h1>高德地图组件使用示例</h1>
    
    <!-- 外部控制按钮 -->
    <div class="external-controls">
      <h3>父组件控制</h3>
      <button @click="setRandomStart" class="btn btn-primary">随机设置起点</button>
      <button @click="setRandomEnd" class="btn btn-primary">随机设置终点</button>
      <button @click="planRouteFromParent" class="btn btn-success">父组件规划路线</button>
      <button @click="addRandomMarker" class="btn btn-info">添加随机标记</button>
      <button @click="clearAllFromParent" class="btn btn-danger">清除所有</button>
    </div>
    
    <!-- 地图组件 -->
    <div class="map-wrapper">
      <AmapContainer ref="amapRef" />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import AmapContainer from './AmapContainer.vue'

// 地图组件引用
const amapRef = ref(null)

/**
 * 随机设置起点 - 北京附近
 */
const setRandomStart = () => {
  // 北京中心点附近的随机坐标
  const baseLng = 116.397428
  const baseLat = 39.90923
  const randomLng = baseLng + (Math.random() - 0.5) * 0.1
  const randomLat = baseLat + (Math.random() - 0.5) * 0.1
  
  amapRef.value?.setStart(randomLng, randomLat)
}

/**
 * 随机设置终点 - 北京附近
 */
const setRandomEnd = () => {
  const baseLng = 116.397428
  const baseLat = 39.90923
  const randomLng = baseLng + (Math.random() - 0.5) * 0.15
  const randomLat = baseLat + (Math.random() - 0.5) * 0.15
  
  amapRef.value?.setEnd(randomLng, randomLat)
}

/**
 * 从父组件调用规划路线
 */
const planRouteFromParent = () => {
  amapRef.value?.planRoute()
}

/**
 * 添加随机标记
 */
const addRandomMarker = () => {
  const baseLng = 116.397428
  const baseLat = 39.90923
  const randomLng = baseLng + (Math.random() - 0.5) * 0.2
  const randomLat = baseLat + (Math.random() - 0.5) * 0.2
  
  amapRef.value?.addMarker(randomLng, randomLat, `随机标记 ${Date.now()}`)
}

/**
 * 从父组件清除所有
 */
const clearAllFromParent = () => {
  amapRef.value?.clearAll()
}
</script>

<style scoped>
.amap-example-page {
  padding: 20px;
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.amap-example-page h1 {
  margin: 0 0 16px 0;
  color: #303133;
  font-size: 24px;
}

.external-controls {
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
  margin-bottom: 16px;
}

.external-controls h3 {
  margin: 0 0 12px 0;
  color: #606266;
  font-size: 16px;
}

.map-wrapper {
  flex: 1;
  min-height: 500px;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

/* 按钮样式 */
.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  margin-right: 8px;
  margin-bottom: 8px;
}

.btn-primary {
  background: #409eff;
  color: #fff;
}

.btn-primary:hover {
  background: #66b1ff;
}

.btn-success {
  background: #67c23a;
  color: #fff;
}

.btn-success:hover {
  background: #85ce61;
}

.btn-info {
  background: #909399;
  color: #fff;
}

.btn-info:hover {
  background: #a6a9ad;
}

.btn-danger {
  background: #f56c6c;
  color: #fff;
}

.btn-danger:hover {
  background: #f78989;
}
</style>
