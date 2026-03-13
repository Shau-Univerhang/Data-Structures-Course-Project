<template>
  <div class="trips-page">
    <header class="page-header">
      <button class="back-btn" @click="goBack">←</button>
      <h1 class="page-title">我的行程</h1>
      <button class="add-btn" @click="createTrip">+</button>
    </header>

    <section class="trips-list">
      <div 
        v-for="trip in trips" 
        :key="trip.id"
        class="trip-card"
        @click="viewTrip(trip)"
      >
        <div class="trip-image" :style="{backgroundImage: `url(${trip.image})`}"></div>
        <div class="trip-info">
          <h3>{{ trip.title }}</h3>
          <p>{{ trip.city }} · {{ trip.days }}天</p>
          <div class="trip-meta">
            <span class="spot-count">{{ trip.spotCount }}个景点</span>
            <span class="trip-date">{{ trip.date }}</span>
          </div>
        </div>
        <div class="trip-status" :class="trip.status">{{ trip.statusText }}</div>
      </div>
    </section>

    <div v-if="trips.length === 0" class="empty-state">
      <span class="empty-icon">🗺️</span>
      <p>还没有行程</p>
      <button class="create-btn" @click="createTrip">创建第一个行程</button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const trips = ref([
  { id: 1, title: '北京三日游', city: '北京', days: 3, spotCount: 8, date: '2024-01-15', status: 'completed', statusText: '已完成', image: 'https://images.unsplash.com/photo-1599571234909-29ed5d1321d6?w=400' },
  { id: 2, title: '上海周末游', city: '上海', days: 2, spotCount: 5, date: '2024-02-20', status: 'published', statusText: '进行中', image: 'https://images.unsplash.com/photo-1474181487882-5abf3f0ba6c2?w=400' },
])

const goBack = () => router.back()

const createTrip = () => router.push('/create-trip')

const viewTrip = (trip) => {
  router.push({ path: '/trip', query: { id: trip.id } })
}
</script>

<style scoped>
.trips-page {
  min-height: 100vh;
  background: #0a0a1a;
  color: #fff;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 15px 20px;
  background: rgba(10, 10, 26, 0.9);
  backdrop-filter: blur(10px);
}

.back-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 1px solid rgba(0, 212, 255, 0.3);
  background: transparent;
  color: #fff;
  font-size: 20px;
  cursor: pointer;
}

.page-title { font-size: 18px; }

.add-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  border: none;
  color: #fff;
  font-size: 24px;
  cursor: pointer;
}

.trips-list {
  padding: 20px;
}

.trip-card {
  display: flex;
  gap: 15px;
  background: rgba(20, 20, 40, 0.8);
  border: 1px solid rgba(0, 212, 255, 0.1);
  border-radius: 16px;
  padding: 15px;
  margin-bottom: 15px;
  cursor: pointer;
  transition: all 0.3s;
}

.trip-card:hover {
  border-color: #00d4ff;
}

.trip-image {
  width: 100px;
  height: 100px;
  border-radius: 12px;
  background-size: cover;
  background-position: center;
  flex-shrink: 0;
}

.trip-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.trip-info h3 { font-size: 16px; margin-bottom: 6px; }
.trip-info p { font-size: 13px; color: rgba(255, 255, 255, 0.5); margin-bottom: 8px; }

.trip-meta {
  display: flex;
  gap: 15px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

.trip-status {
  align-self: flex-start;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
}

.trip-status.completed {
  background: rgba(0, 212, 255, 0.2);
  color: #00d4ff;
}

.trip-status.published {
  background: rgba(123, 44, 191, 0.2);
  color: #7b2cbf;
}

.empty-state {
  text-align: center;
  padding: 80px 20px;
}

.empty-icon {
  font-size: 60px;
  display: block;
  margin-bottom: 20px;
}

.empty-state p {
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 20px;
}

.create-btn {
  padding: 14px 30px;
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  border: none;
  border-radius: 25px;
  color: #fff;
  font-size: 15px;
  cursor: pointer;
}
</style>
