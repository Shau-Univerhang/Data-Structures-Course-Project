<template>
  <div class="food-page">
    <header class="page-header">
      <button class="back-btn" @click="goBack">←</button>
      <h1 class="page-title">美食推荐</h1>
    </header>

    <!-- 城市筛选 -->
    <section class="city-filter">
      <div class="city-scroll">
        <button 
          v-for="city in cities" 
          :key="city"
          class="city-tag"
          :class="{ active: selectedCity === city }"
          @click="selectedCity = city"
        >
          {{ city }}
        </button>
      </div>
    </section>

    <!-- 筛选排序 -->
    <section class="filter-bar">
      <div class="filter-tags">
        <span 
          v-for="cuisine in cuisines" 
          :key="cuisine"
          class="filter-tag"
          :class="{ active: selectedCuisine === cuisine }"
          @click="selectedCuisine = cuisine"
        >
          {{ cuisine }}
        </span>
      </div>
      <select v-model="sortBy" class="sort-select">
        <option value="rating">评分优先</option>
        <option value="popularity">热度优先</option>
        <option value="price">价格优先</option>
      </select>
    </section>

    <!-- 美食列表 -->
    <section class="food-section">
      <div class="food-grid">
        <div 
          v-for="food in filteredFoods" 
          :key="food.id"
          class="food-card"
          @click="showFoodDetail(food)"
        >
          <div class="food-image">
            <img :src="food.image || defaultImage" :alt="food.name" />
            <div class="food-badge" v-if="food.is_featured">必吃</div>
          </div>
          <div class="food-info">
            <h3>{{ food.name }}</h3>
            <p class="food-cuisine">{{ food.cuisine_type }}</p>
            <div class="food-rating">
              <span class="star">★</span>
              <span>{{ food.rating }}</span>
              <span class="price">{{ food.price_range }}</span>
            </div>
            <div class="food-tags">
              <span v-for="tag in food.tags" :key="tag">{{ tag }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 空状态 -->
    <div v-if="filteredFoods.length === 0" class="empty-state">
      <p>暂无美食数据</p>
    </div>

    <!-- 美食详情弹窗 -->
    <div v-if="showDetail" class="detail-modal" @click.self="showDetail = false">
      <div class="detail-content">
        <button class="close-btn" @click="showDetail = false">×</button>
        
        <div class="detail-header">
          <img :src="currentFood.image || defaultImage" :alt="currentFood.name" />
        </div>
        
        <div class="detail-body">
          <h2>{{ currentFood.name }}</h2>
          <p class="detail-cuisine">{{ currentFood.cuisine_type }}</p>
          
          <div class="detail-rating">
            <span class="star">★</span>
            <span class="rating-value">{{ currentFood.rating }}</span>
            <span class="reviews">({{ currentFood.reviews?.length || 0 }}条评价)</span>
          </div>
          
          <div class="detail-price">
            <span class="price-label">人均:</span>
            <span class="price-value">{{ currentFood.price_range }}</span>
          </div>
          
          <div class="detail-tags">
            <span v-for="tag in currentFood.tags" :key="tag" class="tag">{{ tag }}</span>
          </div>
          
          <div class="detail-desc">
            <p>{{ currentFood.description }}</p>
          </div>
          
          <!-- 用户评论 -->
          <div class="reviews-section">
            <h3>用户评论</h3>
            <div class="reviews-list">
              <div 
                v-for="(review, index) in currentFood.reviews" 
                :key="index"
                class="review-item"
              >
                <div class="review-header">
                  <span class="review-user">{{ review.user }}</span>
                  <span class="review-rating">★ {{ review.rating }}</span>
                </div>
                <p class="review-content">{{ review.content }}</p>
                <span class="review-date">{{ review.date }}</span>
              </div>
              
              <div v-if="!currentFood.reviews || currentFood.reviews.length === 0" class="no-reviews">
                暂无评论，快来抢先评价！
              </div>
            </div>
            
            <!-- 添加评论 -->
            <div class="add-review">
              <input 
                type="text" 
                class="review-input" 
                placeholder="添加评论..."
                v-model="newReview"
              />
              <button @click="submitReview" class="submit-review">发布</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// 城市列表
const cities = ['全部', '北京', '上海', '成都', '重庆', '杭州', '西安', '广州', '苏州', '厦门']
const cuisines = ['全部', '川菜', '火锅', '烧烤', '小吃', '粤菜', '湘菜', '西餐', '日料']
const defaultImage = '/images/foods/bbq.jpg'

// 状态
const selectedCity = ref('全部')
const selectedCuisine = ref('全部')
const sortBy = ref('rating')
const showDetail = ref(false)
const currentFood = ref({})
const newReview = ref('')

// 美食数据
const foods = ref([
  // 北京
  { id: 1, name: '北京烤鸭', city: '北京', cuisine_type: '京菜', rating: 4.9, price_range: '¥80-150', image: 'https://images.unsplash.com/photo-1563245372-f21724e3856f?w=400', is_featured: true, tags: ['必吃', '招牌'], description: '北京最著名的传统名菜，皮脆肉嫩', reviews: [{user: '游客1', rating: 5, content: '非常好吃！', date: '2024-01-15'}] },
  { id: 2, name: '涮羊肉', city: '北京', cuisine_type: '火锅', rating: 4.7, price_range: '¥60-100', image: 'https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=400', is_featured: false, tags: ['特色'], description: '老北京传统铜锅涮肉' },
  { id: 3, name: '炸酱面', city: '北京', cuisine_type: '小吃', rating: 4.5, price_range: '¥20-40', image: 'https://images.unsplash.com/photo-1563245372-f21724e3856f?w=400', tags: ['特色'], description: '老北京特色面食' },
  // 上海
  { id: 4, name: '本帮红烧肉', city: '上海', cuisine_type: '本帮菜', rating: 4.8, price_range: '¥50-80', image: 'https://images.unsplash.com/photo-1544025162-d76694265947?w=400', is_featured: true, tags: ['必吃'], description: '上海经典本帮菜，肥而不腻' },
  { id: 5, name: '小笼包', city: '上海', cuisine_type: '小吃', rating: 4.9, price_range: '¥15-30', image: 'https://images.unsplash.com/photo-1563245372-f21724e3856f?w=400', is_featured: true, tags: ['必吃', '特色'], description: '上海传统小吃，汤汁鲜美' },
  { id: 6, name: '生煎包', city: '上海', cuisine_type: '小吃', rating: 4.6, price_range: '¥10-25', image: 'https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=400', tags: ['特色'], description: '上海特色早餐' },
  // 成都
  { id: 7, name: '麻辣火锅', city: '成都', cuisine_type: '火锅', rating: 4.9, price_range: '¥70-120', image: 'https://images.unsplash.com/photo-1587895929328-6226a77f5c0f?w=400', is_featured: true, tags: ['必吃', '辣'], description: '成都特色麻辣火锅' },
  { id: 8, name: '麻婆豆腐', city: '成都', cuisine_type: '川菜', rating: 4.7, price_range: '¥25-45', image: 'https://images.unsplash.com/photo-1587895929328-6226a77f5c0f?w=400', tags: ['经典'], description: '川菜经典代表' },
  { id: 9, name: '龙抄手', city: '成都', cuisine_type: '小吃', rating: 4.5, price_range: '¥15-30', image: 'https://images.unsplash.com/photo-1563245372-f21724e3856f?w=400', tags: ['特色'], description: '成都传统小吃' },
  // 重庆
  { id: 10, name: '重庆火锅', city: '重庆', cuisine_type: '火锅', rating: 4.9, price_range: '¥60-100', image: 'https://images.unsplash.com/photo-1587895929328-6226a77f5c0f?w=400', is_featured: true, tags: ['必吃', '辣'], description: '正宗重庆麻辣火锅' },
  { id: 11, name: '小面', city: '重庆', cuisine_type: '小吃', rating: 4.6, price_range: '¥10-20', image: 'https://images.unsplash.com/photo-1563245372-f21724e3856f?w=400', tags: ['特色'], description: '重庆特色小面' },
  // 杭州
  { id: 12, name: '西湖醋鱼', city: '杭州', cuisine_type: '浙菜', rating: 4.7, price_range: '¥60-100', image: 'https://images.unsplash.com/photo-1544025162-d76694265947?w=400', is_featured: true, tags: ['必吃'], description: '杭州名菜' },
  { id: 13, name: '东坡肉', city: '杭州', cuisine_type: '浙菜', rating: 4.8, price_range: '¥40-70', image: 'https://images.unsplash.com/photo-1544025162-d76694265947?w=400', tags: ['经典'], description: '杭州传统名菜' },
  // 西安
  { id: 14, name: '肉夹馍', city: '西安', cuisine_type: '小吃', rating: 4.8, price_range: '¥10-20', image: 'https://images.unsplash.com/photo-1563245372-f21724e3856f?w=400', is_featured: true, tags: ['必吃', '特色'], description: '西安经典小吃' },
  { id: 15, name: '羊肉泡馍', city: '西安', cuisine_type: '西北菜', rating: 4.6, price_range: '¥25-45', image: 'https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=400', tags: ['特色'], description: '西安传统美食' },
  // 广州
  { id: 16, name: '早茶', city: '广州', cuisine_type: '粤菜', rating: 4.9, price_range: '¥40-80', image: 'https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=400', is_featured: true, tags: ['必吃', '特色'], description: '广州特色早茶文化' },
  { id: 17, name: '烧腊', city: '广州', cuisine_type: '粤菜', rating: 4.7, price_range: '¥30-60', image: 'https://images.unsplash.com/photo-1544025162-d76694265947?w=400', tags: ['特色'], description: '广州经典烧腊' },
  // 苏州
  { id: 18, name: '松鼠桂鱼', city: '苏州', cuisine_type: '苏菜', rating: 4.8, price_range: '¥80-150', image: 'https://images.unsplash.com/photo-1544025162-d76694265947?w=400', is_featured: true, tags: ['必吃'], description: '苏州名菜' },
  // 厦门
  { id: 19, name: '沙茶面', city: '厦门', cuisine_type: '闽南菜', rating: 4.6, price_range: '¥20-40', image: 'https://images.unsplash.com/photo-1563245372-f21724e3856f?w=400', tags: ['特色'], description: '厦门特色小吃' },
  { id: 20, name: '土笋冻', city: '厦门', cuisine_type: '闽南菜', rating: 4.4, price_range: '¥15-30', image: 'https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=400', tags: ['特色'], description: '厦门特色凉菜' },
])

// 筛选
const filteredFoods = computed(() => {
  let result = foods.value
  
  if (selectedCity.value !== '全部') {
    result = result.filter(f => f.city === selectedCity.value)
  }
  
  if (selectedCuisine.value !== '全部') {
    result = result.filter(f => f.cuisine_type.includes(selectedCuisine.value))
  }
  
  if (sortBy.value === 'rating') {
    result = [...result].sort((a, b) => b.rating - a.rating)
  } else if (sortBy.value === 'popularity') {
    result = [...result].sort((a, b) => (b.reviews?.length || 0) - (a.reviews?.length || 0))
  }
  
  return result
})

// 显示详情
const showFoodDetail = (food) => {
  currentFood.value = food
  showDetail.value = true
}

// 提交评论
const submitReview = () => {
  if (!newReview.value.trim()) return
  
  if (!currentFood.value.reviews) {
    currentFood.value.reviews = []
  }
  
  currentFood.value.reviews.unshift({
    user: '我',
    rating: 5,
    content: newReview.value,
    date: new Date().toISOString().split('T')[0]
  })
  
  newReview.value = ''
}

const goBack = () => router.back()
</script>

<style scoped>
.food-page {
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
}

.city-filter {
  padding: 10px 20px;
  background: rgba(0, 212, 255, 0.05);
  overflow-x: auto;
}

.city-scroll {
  display: flex;
  gap: 10px;
  min-width: max-content;
}

.city-tag, .filter-tag {
  padding: 8px 16px;
  border-radius: 20px;
  border: 1px solid rgba(0, 212, 255, 0.3);
  background: transparent;
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  white-space: nowrap;
}

.city-tag.active, .filter-tag.active {
  background: rgba(0, 212, 255, 0.2);
  border-color: #00D4FF;
  color: #00D4FF;
}

.filter-bar {
  display: flex;
  justify-content: space-between;
  padding: 10px 20px;
  align-items: center;
}

.filter-tags {
  display: flex;
  gap: 8px;
  overflow-x: auto;
}

.sort-select {
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(0, 212, 255, 0.3);
  color: #fff;
  border-radius: 8px;
}

.food-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
  padding: 15px 20px;
}

.food-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
}

.food-image {
  position: relative;
  height: 120px;
}

.food-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.food-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  padding: 4px 10px;
  background: linear-gradient(135deg, #FF6B6B, #FF8E53);
  border-radius: 12px;
  font-size: 12px;
}

.food-info {
  padding: 12px;
}

.food-info h3 {
  font-size: 14px;
  margin-bottom: 4px;
}

.food-cuisine {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 8px;
}

.food-rating {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}

.star {
  color: #FFD700;
}

.price {
  color: #00D4FF;
}

.food-tags {
  display: flex;
  gap: 4px;
  margin-top: 8px;
}

.food-tags span {
  padding: 2px 8px;
  background: rgba(0, 212, 255, 0.1);
  border-radius: 8px;
  font-size: 10px;
  color: rgba(255, 255, 255, 0.6);
}

/* 详情弹窗 */
.detail-modal {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.9);
  z-index: 1000;
  overflow-y: auto;
}

.detail-content {
  max-width: 500px;
  margin: 20px auto;
  background: #1a1a2e;
  border-radius: 20px;
  overflow: hidden;
  position: relative;
}

.close-btn {
  position: absolute;
  top: 15px;
  right: 15px;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.5);
  color: #fff;
  border: none;
  cursor: pointer;
  z-index: 10;
}

.detail-header img {
  width: 100%;
  height: 200px;
  object-fit: cover;
}

.detail-body {
  padding: 20px;
}

.detail-body h2 {
  font-size: 20px;
  margin-bottom: 5px;
}

.detail-cuisine {
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 10px;
}

.detail-rating {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
}

.rating-value {
  font-size: 18px;
  font-weight: bold;
  color: #FFD700;
}

.reviews {
  color: rgba(255, 255, 255, 0.5);
  font-size: 12px;
}

.detail-price {
  margin-bottom: 15px;
}

.price-label {
  color: rgba(255, 255, 255, 0.6);
  margin-right: 10px;
}

.price-value {
  color: #00D4FF;
  font-size: 18px;
}

.detail-tags {
  display: flex;
  gap: 8px;
  margin-bottom: 15px;
}

.tag {
  padding: 4px 12px;
  background: rgba(0, 212, 255, 0.2);
  border-radius: 12px;
  font-size: 12px;
}

.detail-desc {
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.6;
  margin-bottom: 20px;
}

/* 评论 */
.reviews-section h3 {
  font-size: 16px;
  margin-bottom: 15px;
}

.review-item {
  padding: 12px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  margin-bottom: 10px;
}

.review-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.review-user {
  font-weight: bold;
}

.review-rating {
  color: #FFD700;
  font-size: 12px;
}

.review-content {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 8px;
}

.review-date {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
}

.no-reviews {
  text-align: center;
  padding: 20px;
  color: rgba(255, 255, 255, 0.5);
}

.add-review {
  display: flex;
  gap: 10px;
  margin-top: 15px;
}

.review-input {
  flex: 1;
  padding: 10px 15px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(0, 212, 255, 0.3);
  border-radius: 20px;
  color: #fff;
}

.submit-review {
  padding: 10px 20px;
  background: #00D4FF;
  border: none;
  border-radius: 20px;
  color: #000;
  cursor: pointer;
}
</style>
