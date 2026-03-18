<template>
  <div class="explore-page">
    <!-- 顶部导航栏 -->
    <Navbar />

    <div class="explore-container">
      <!-- 左侧导航栏 -->
      <aside class="sidebar">
        <div class="sidebar-header">
          <h2>探索发现</h2>
          <p>发现城市的美好</p>
        </div>
        
        <nav class="sidebar-nav">
          <button 
            class="nav-item" 
            :class="{ active: currentTab === 'spots' }"
            @click="currentTab = 'spots'"
          >
            <span class="nav-icon">📍</span>
            <span class="nav-label">景点推荐</span>
          </button>
          <button 
            class="nav-item" 
            :class="{ active: currentTab === 'food' }"
            @click="currentTab = 'food'"
          >
            <span class="nav-icon">🍜</span>
            <span class="nav-label">美食推荐</span>
          </button>
        </nav>

        <!-- 城市筛选 -->
        <div class="city-filter">
          <h3>选择城市</h3>
          <div class="city-list">
            <button 
              v-for="city in cities" 
              :key="city"
              class="city-btn"
              :class="{ active: selectedCity === city }"
              @click="selectedCity = city"
            >
              {{ city }}
            </button>
          </div>
        </div>
      </aside>

      <!-- 右侧内容区 -->
      <main class="content-area">
        <!-- 景点推荐内容 -->
        <div v-if="currentTab === 'spots'" class="content-section">
          <div class="section-header">
            <h1>{{ selectedCity }}热门景点</h1>
            <p>探索{{ selectedCity }}的精彩景点，发现城市之美</p>
          </div>

          <!-- 加载状态 -->
          <div v-if="loadingSpots" class="loading-container">
            <div class="loading-spinner"></div>
            <p>正在加载景点...</p>
          </div>

          <!-- 景点网格 -->
          <div v-else class="cards-grid">
            <div 
              v-for="spot in filteredSpots" 
              :key="spot.id" 
              class="card"
              @click="showSpotDetail(spot)"
            >
              <div class="card-image">
                <img :src="getSpotImage(spot.name, spot.city) || spot.images?.[0] || `/images/cities/${getCityImageName(spot.city)}`" :alt="spot.name" />
                <div class="card-badge" v-if="spot.rating >= 4.8">
                  <span>★</span>
                  <span>{{ spot.rating }}</span>
                </div>
              </div>
              <div class="card-info">
                <h3>{{ spot.name }}</h3>
                <div class="card-meta">
                  <span class="rating">⭐ {{ spot.rating?.toFixed(1) || '4.5' }}</span>
                  <span class="favorites" v-if="spot.favorites">❤️ {{ formatNumber(spot.favorites) }}</span>
                </div>
                <div class="card-tags">
                  <span v-for="tag in (spot.tags || []).slice(0, 2)" :key="tag" class="tag">
                    {{ tag }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- 空状态 -->
          <div v-if="!loadingSpots && filteredSpots.length === 0" class="empty-state">
            <span class="empty-icon">🔍</span>
            <p>暂无景点数据</p>
          </div>
        </div>

        <!-- 美食推荐内容 -->
        <div v-else class="content-section">
          <div class="section-header">
            <h1>{{ selectedCity }}特色美食</h1>
            <p>品味{{ selectedCity }}的地道美食，享受舌尖上的旅行</p>
          </div>

          <!-- 美食分类筛选 -->
          <div class="cuisine-filter">
            <button 
              v-for="cuisine in cuisines" 
              :key="cuisine"
              class="filter-btn"
              :class="{ active: selectedCuisine === cuisine }"
              @click="selectedCuisine = cuisine"
            >
              {{ cuisine }}
            </button>
          </div>

          <!-- 美食网格 -->
          <div class="cards-grid">
            <div 
              v-for="food in filteredFoods" 
              :key="food.id"
              class="card"
              @click="showFoodDetail(food)"
            >
              <div class="card-image">
                <img :src="getFoodImage(food.name) || `/images/cities/${getCityImageName(food.city)}`" :alt="food.name" />
                <div class="card-badge featured" v-if="food.is_featured">
                  <span>必吃</span>
                </div>
              </div>
              <div class="card-info">
                <h3>{{ food.name }}</h3>
                <div class="card-meta">
                  <span class="rating">★ {{ food.rating }}</span>
                  <span class="price">{{ food.price_range }}</span>
                </div>
                <div class="card-tags">
                  <span v-for="tag in food.tags.slice(0, 2)" :key="tag" class="tag">
                    {{ tag }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- 空状态 -->
          <div v-if="filteredFoods.length === 0" class="empty-state">
            <span class="empty-icon">🍽️</span>
            <p>暂无美食数据</p>
          </div>
        </div>
      </main>
    </div>

    <!-- 景点详情弹窗 -->
    <div v-if="showSpotModal" class="modal" @click.self="showSpotModal = false">
      <div class="modal-content">
        <button class="modal-close" @click="showSpotModal = false">×</button>
        <div class="modal-header">
          <img :src="getSpotImage(currentSpot.name, currentSpot.city) || currentSpot.images?.[0] || `/images/cities/${getCityImageName(currentSpot.city)}`" :alt="currentSpot.name" />
        </div>
        <div class="modal-body">
          <h2>{{ currentSpot.name }}</h2>
          <div class="modal-rating">
            <span class="star">★</span>
            <span>{{ currentSpot.rating }}</span>
          </div>
          <div class="modal-tags">
            <span v-for="tag in currentSpot.tags" :key="tag" class="tag">{{ tag }}</span>
          </div>
          <p class="modal-desc">{{ currentSpot.description || '暂无描述' }}</p>
        </div>
      </div>
    </div>

    <!-- 美食详情弹窗 -->
    <div v-if="showFoodModal" class="modal" @click.self="showFoodModal = false">
      <div class="modal-content">
        <button class="modal-close" @click="showFoodModal = false">×</button>
        <div class="modal-header">
          <img :src="getFoodImage(currentFood.name) || `/images/cities/${getCityImageName(currentFood.city)}`" :alt="currentFood.name" />
        </div>
        <div class="modal-body">
          <h2>{{ currentFood.name }}</h2>
          <div class="modal-meta">
            <span class="rating">★ {{ currentFood.rating }}</span>
            <span class="price">{{ currentFood.price_range }}</span>
          </div>
          <div class="modal-tags">
            <span v-for="tag in currentFood.tags" :key="tag" class="tag">{{ tag }}</span>
          </div>
          <p class="modal-desc">{{ currentFood.description }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import Navbar from '../components/Navbar.vue'

// 当前选中的标签
const currentTab = ref('spots')
const selectedCity = ref('北京')
const selectedCuisine = ref('全部')

// 弹窗状态
const showSpotModal = ref(false)
const showFoodModal = ref(false)
const currentSpot = ref({})
const currentFood = ref({})

// 城市列表 - 与主页轮播一致
const cities = ['北京', '上海', '西安', '成都', '杭州', '重庆', '青岛', '广州', '苏州', '厦门', '南京', '武汉', '长沙', '深圳', '三亚', '桂林', '张家界', '黄山', '九寨沟', '大理', '丽江']

// 美食分类
const cuisines = ['全部', '川菜', '火锅', '烧烤', '小吃', '粤菜', '湘菜', '西餐', '日料']

// 加载状态
const loadingSpots = ref(false)

// 景点数据
const spots = ref([])

// ========== 景点图片映射 - 和 City.vue 保持一致 ==========

// 上海景点图片映射
const shanghaiSpotImages = {
  '东方明珠': '/images/spots/shanghai/shanghai_dongfang_mingzhu.jpg',
  '外滩': '/images/spots/shanghai/shanghai_waitan.jpg',
  '豫园': '/images/spots/shanghai/shanghai_yuyuan.jpg',
  '田子坊': '/images/spots/shanghai/shanghai_tianzifang.jpg',
  '武康路': '/images/spots/shanghai/shanghai_wukanglu.jpg',
  '南京路': '/images/spots/shanghai/shanghai_nanjinglu_buxingjie.jpg',
  '南京路步行街': '/images/spots/shanghai/shanghai_nanjinglu_buxingjie.jpg',
  '上海博物馆': '/images/spots/shanghai/shanghai_shanghai_bowuguan.jpg',
  '静安寺': '/images/spots/shanghai/shanghai_jingansi.jpg',
  '召楼古镇': '/images/spots/shanghai/shanghai_zhaolou_guzhen.jpg',
  '迪士尼': '/images/spots/shanghai/shanghai_shanghai_dishini.jpg',
  '迪士尼乐园': '/images/spots/shanghai/shanghai_shanghai_dishini.jpg',
  '上海迪士尼': '/images/spots/shanghai/shanghai_shanghai_dishini.jpg',
  '上海迪士尼乐园': '/images/spots/shanghai/shanghai_shanghai_dishini.jpg',
}

// 北京景点图片映射
const beijingSpotImages = {
  '故宫': '/images/spots/beijing/beijing_gugong_bowuyuan.jpg',
  '故宫博物院': '/images/spots/beijing/beijing_gugong_bowuyuan.jpg',
  '长城': '/images/spots/beijing/beijing_badaling_changcheng.jpg',
  '八达岭': '/images/spots/beijing/beijing_badaling_changcheng.jpg',
  '天坛': '/images/spots/beijing/beijing_tiantan_gongyuan.jpg',
  '天坛公园': '/images/spots/beijing/beijing_tiantan_gongyuan.jpg',
  '天安门': '/images/spots/beijing/beijing_tiananmen_guangchang.jpg',
  '天安门广场': '/images/spots/beijing/beijing_tiananmen_guangchang.jpg',
  '颐和园': '/images/spots/beijing/beijing_yiheyuan.jpg',
  '圆明园': '/images/spots/beijing/beijing_yuanmingyuan.jpg',
  '北海公园': '/images/spots/beijing/beijing_beihai_gongyuan.jpg',
  '恭王府': '/images/spots/beijing/beijing_gongwangfu.jpg',
  '景山公园': '/images/spots/beijing/beijing_jingshan_gongyuan.jpg',
  '南锣鼓巷': '/images/spots/beijing/beijing_nanluoguxiang.jpg',
}

// 西安景点图片映射
const xianSpotImages = {
  '兵马俑': '/images/spots/xian/xian_bingmayong.jpg',
  '大雁塔': '/images/spots/xian/xian_dayanta.jpg',
  '古城墙': '/images/spots/xian/xian_xian_chengqiang.jpg',
  '城墙': '/images/spots/xian/xian_xian_chengqiang.jpg',
  '华清宫': '/images/spots/xian/xian_huaqinggong.jpg',
  '大唐芙蓉园': '/images/spots/xian/xian_datang_furongyuan.jpg',
  '回民街': '/images/spots/xian/xian_huiminjie.jpg',
}

// 城市景点映射表
const citySpotImages = {
  '北京': beijingSpotImages,
  '上海': shanghaiSpotImages,
  '西安': xianSpotImages,
}

// 获取景点对应的图片
const getSpotImage = (spotName, city) => {
  const cityImagesMap = citySpotImages[city]
  if (cityImagesMap) {
    // 优先完全匹配
    if (cityImagesMap[spotName]) {
      return cityImagesMap[spotName]
    }
    // 其次包含匹配
    for (const [key, value] of Object.entries(cityImagesMap)) {
      if (spotName.includes(key) || key.includes(spotName)) {
        return value
      }
    }
  }
  return null
}

// 城市图片名称映射
const getCityImageName = (cityName) => {
  const cityMap = {
    '北京': 'beijing.jpg',
    '上海': 'shanghai.jpg',
    '西安': 'xian.jpg',
    '成都': 'chengdu.jpg',
    '重庆': 'chongqing.jpg',
    '杭州': 'hangzhou.jpg',
    '广州': 'guangzhou.jpg',
    '苏州': 'suzhou.jpg',
    '厦门': 'xiamen.jpg',
    '三亚': 'sanya.jpg',
    '青岛': 'qingdao.jpg',
    '南京': 'nanjing.jpg',
    '武汉': 'wuhan.jpg',
    '长沙': 'changsha.jpg',
    '深圳': 'shenzhen.jpg',
    '桂林': 'guilin.jpg',
    '张家界': 'zhangjiajie.jpg',
    '黄山': 'huangshan.jpg',
    '九寨沟': 'jiuzhaigou.jpg',
    '大理': 'dali.jpg',
    '丽江': 'lijiang.jpg',
  }
  return cityMap[cityName] || 'beijing.jpg'
}

// 美食图片映射 - 从后端加载
const getFoodImage = (foodName) => {
  // 将食物名称转换为图片文件名
  const imageMap = {
    '北京烤鸭': 'beijing_kaoya.jpg',
    '涮羊肉': 'shuan_yangrou.jpg',
    '炸酱面': 'zhajiangmian.jpg',
    '本帮红烧肉': 'benbang_hongshaorou.jpg',
    '小笼包': 'xiaolongbao.jpg',
    '生煎包': 'shengjianbao.jpg',
    '麻辣火锅': 'mala_huoguo.jpg',
    '麻婆豆腐': 'mapo_doufu.jpg',
    '龙抄手': 'longchaoshou.jpg',
    '重庆火锅': 'chongqing_huoguo.jpg',
    '小面': 'chongqing_xiaomian.jpg',
    '西湖醋鱼': 'xihu_cuyu.jpg',
    '东坡肉': 'dongporou.jpg',
    '肉夹馍': 'roujiamo.jpg',
    '羊肉泡馍': 'yangrou_paomo.jpg',
    '早茶': 'guangdong_zaocha.jpg',
    '烧腊': 'shaola.jpg',
    '松鼠桂鱼': 'songshu_guiyu.jpg',
    '沙茶面': 'shachamian.jpg',
    '土笋冻': 'tusundong.jpg',
  }
  const imageName = imageMap[foodName]
  if (imageName) {
    return `/images/foods/${imageName}`
  }
  // 如果没有对应图片，返回 null 使用城市图片
  return null
}

// 美食数据
const foods = ref([
  // 北京
  { id: 1, name: '北京烤鸭', city: '北京', cuisine_type: '京菜', rating: 4.9, price_range: '¥80-150', is_featured: true, tags: ['必吃', '招牌'], description: '北京最著名的传统名菜，皮脆肉嫩' },
  { id: 2, name: '涮羊肉', city: '北京', cuisine_type: '火锅', rating: 4.7, price_range: '¥60-100', is_featured: false, tags: ['特色'], description: '老北京传统铜锅涮肉' },
  { id: 3, name: '炸酱面', city: '北京', cuisine_type: '小吃', rating: 4.5, price_range: '¥20-40', tags: ['特色'], description: '老北京特色面食' },
  // 上海
  { id: 4, name: '本帮红烧肉', city: '上海', cuisine_type: '本帮菜', rating: 4.8, price_range: '¥50-80', is_featured: true, tags: ['必吃'], description: '上海经典本帮菜，肥而不腻' },
  { id: 5, name: '小笼包', city: '上海', cuisine_type: '小吃', rating: 4.9, price_range: '¥15-30', is_featured: true, tags: ['必吃', '特色'], description: '上海传统小吃，汤汁鲜美' },
  { id: 6, name: '生煎包', city: '上海', cuisine_type: '小吃', rating: 4.6, price_range: '¥10-25', tags: ['特色'], description: '上海特色早餐' },
  // 成都
  { id: 7, name: '麻辣火锅', city: '成都', cuisine_type: '火锅', rating: 4.9, price_range: '¥70-120', is_featured: true, tags: ['必吃', '辣'], description: '成都特色麻辣火锅' },
  { id: 8, name: '麻婆豆腐', city: '成都', cuisine_type: '川菜', rating: 4.7, price_range: '¥25-45', tags: ['经典'], description: '川菜经典代表' },
  { id: 9, name: '龙抄手', city: '成都', cuisine_type: '小吃', rating: 4.5, price_range: '¥15-30', tags: ['特色'], description: '成都传统小吃' },
  // 重庆
  { id: 10, name: '重庆火锅', city: '重庆', cuisine_type: '火锅', rating: 4.9, price_range: '¥60-100', is_featured: true, tags: ['必吃', '辣'], description: '正宗重庆麻辣火锅' },
  { id: 11, name: '小面', city: '重庆', cuisine_type: '小吃', rating: 4.6, price_range: '¥10-20', tags: ['特色'], description: '重庆特色小面' },
  { id: 12, name: '酸辣粉', city: '重庆', cuisine_type: '小吃', rating: 4.5, price_range: '¥10-15', tags: ['特色'], description: '重庆街头美食' },
  // 杭州
  { id: 13, name: '西湖醋鱼', city: '杭州', cuisine_type: '浙菜', rating: 4.7, price_range: '¥60-100', is_featured: true, tags: ['必吃'], description: '杭州名菜' },
  { id: 14, name: '东坡肉', city: '杭州', cuisine_type: '浙菜', rating: 4.8, price_range: '¥40-70', tags: ['经典'], description: '杭州传统名菜' },
  { id: 15, name: '龙井虾仁', city: '杭州', cuisine_type: '浙菜', rating: 4.6, price_range: '¥50-80', tags: ['特色'], description: '杭州特色菜' },
  // 西安
  { id: 16, name: '肉夹馍', city: '西安', cuisine_type: '小吃', rating: 4.8, price_range: '¥10-20', is_featured: true, tags: ['必吃', '特色'], description: '西安经典小吃' },
  { id: 17, name: '羊肉泡馍', city: '西安', cuisine_type: '西北菜', rating: 4.6, price_range: '¥25-45', tags: ['特色'], description: '西安传统美食' },
  { id: 18, name: '凉皮', city: '西安', cuisine_type: '小吃', rating: 4.5, price_range: '¥8-15', tags: ['特色'], description: '西安夏日美食' },
  // 广州
  { id: 19, name: '早茶', city: '广州', cuisine_type: '粤菜', rating: 4.9, price_range: '¥40-80', is_featured: true, tags: ['必吃', '特色'], description: '广州特色早茶文化' },
  { id: 20, name: '烧腊', city: '广州', cuisine_type: '粤菜', rating: 4.7, price_range: '¥30-60', tags: ['特色'], description: '广州经典烧腊' },
  { id: 21, name: '肠粉', city: '广州', cuisine_type: '粤菜', rating: 4.6, price_range: '¥10-20', tags: ['特色'], description: '广州传统早餐' },
  // 苏州
  { id: 22, name: '松鼠桂鱼', city: '苏州', cuisine_type: '苏菜', rating: 4.8, price_range: '¥80-150', is_featured: true, tags: ['必吃'], description: '苏州名菜' },
  { id: 23, name: '响油鳝糊', city: '苏州', cuisine_type: '苏菜', rating: 4.6, price_range: '¥60-100', tags: ['特色'], description: '苏州传统菜' },
  // 厦门
  { id: 24, name: '沙茶面', city: '厦门', cuisine_type: '闽南菜', rating: 4.6, price_range: '¥20-40', tags: ['特色'], description: '厦门特色小吃' },
  { id: 25, name: '土笋冻', city: '厦门', cuisine_type: '闽南菜', rating: 4.4, price_range: '¥15-30', tags: ['特色'], description: '厦门特色凉菜' },
  // 三亚
  { id: 26, name: '海鲜大餐', city: '三亚', cuisine_type: '海鲜', rating: 4.8, price_range: '¥150-300', is_featured: true, tags: ['必吃', '特色'], description: '三亚新鲜海鲜' },
  { id: 27, name: '椰子鸡', city: '三亚', cuisine_type: '海南菜', rating: 4.7, price_range: '¥80-150', tags: ['特色'], description: '海南特色美食' },
  // 青岛
  { id: 28, name: '青岛啤酒', city: '青岛', cuisine_type: '饮品', rating: 4.9, price_range: '¥10-30', is_featured: true, tags: ['必喝', '特色'], description: '青岛著名啤酒' },
  { id: 29, name: '海鲜烧烤', city: '青岛', cuisine_type: '海鲜', rating: 4.7, price_range: '¥80-150', tags: ['特色'], description: '青岛特色海鲜烧烤' },
  // 南京
  { id: 30, name: '盐水鸭', city: '南京', cuisine_type: '苏菜', rating: 4.8, price_range: '¥40-80', is_featured: true, tags: ['必吃', '特色'], description: '南京传统名菜' },
  { id: 31, name: '鸭血粉丝汤', city: '南京', cuisine_type: '小吃', rating: 4.6, price_range: '¥15-25', tags: ['特色'], description: '南京特色小吃' },
  // 武汉
  { id: 32, name: '热干面', city: '武汉', cuisine_type: '小吃', rating: 4.8, price_range: '¥8-15', is_featured: true, tags: ['必吃', '特色'], description: '武汉经典早餐' },
  { id: 33, name: '武昌鱼', city: '武汉', cuisine_type: '鄂菜', rating: 4.6, price_range: '¥50-100', tags: ['特色'], description: '武汉传统名菜' },
  // 长沙
  { id: 34, name: '臭豆腐', city: '长沙', cuisine_type: '小吃', rating: 4.7, price_range: '¥10-20', is_featured: true, tags: ['必吃', '特色'], description: '长沙著名小吃' },
  { id: 35, name: '口味虾', city: '长沙', cuisine_type: '湘菜', rating: 4.6, price_range: '¥60-120', tags: ['特色'], description: '长沙夜宵首选' },
  // 深圳
  { id: 36, name: '潮汕牛肉火锅', city: '深圳', cuisine_type: '火锅', rating: 4.8, price_range: '¥80-150', is_featured: true, tags: ['必吃'], description: '深圳特色火锅' },
  { id: 37, name: '广式早茶', city: '深圳', cuisine_type: '粤菜', rating: 4.7, price_range: '¥50-100', tags: ['特色'], description: '深圳早茶文化' },
  // 桂林
  { id: 38, name: '桂林米粉', city: '桂林', cuisine_type: '小吃', rating: 4.8, price_range: '¥10-20', is_featured: true, tags: ['必吃', '特色'], description: '桂林传统美食' },
  { id: 39, name: '啤酒鱼', city: '桂林', cuisine_type: '桂菜', rating: 4.6, price_range: '¥60-100', tags: ['特色'], description: '桂林特色菜' },
  // 张家界
  { id: 40, name: '土家腊肉', city: '张家界', cuisine_type: '湘菜', rating: 4.7, price_range: '¥50-80', is_featured: true, tags: ['必吃', '特色'], description: '张家界特色美食' },
  { id: 41, name: '三下锅', city: '张家界', cuisine_type: '湘菜', rating: 4.5, price_range: '¥40-70', tags: ['特色'], description: '张家界传统菜' },
  // 黄山
  { id: 42, name: '臭鳜鱼', city: '黄山', cuisine_type: '徽菜', rating: 4.6, price_range: '¥60-100', is_featured: true, tags: ['必吃', '特色'], description: '黄山传统名菜' },
  { id: 43, name: '毛豆腐', city: '黄山', cuisine_type: '徽菜', rating: 4.5, price_range: '¥15-30', tags: ['特色'], description: '黄山特色小吃' },
  // 九寨沟
  { id: 44, name: '牦牛肉', city: '九寨沟', cuisine_type: '藏菜', rating: 4.7, price_range: '¥60-120', is_featured: true, tags: ['必吃', '特色'], description: '九寨沟特色美食' },
  { id: 45, name: '酥油茶', city: '九寨沟', cuisine_type: '藏菜', rating: 4.5, price_range: '¥10-20', tags: ['特色'], description: '藏族传统饮品' },
  // 大理
  { id: 46, name: '过桥米线', city: '大理', cuisine_type: '云南菜', rating: 4.8, price_range: '¥20-40', is_featured: true, tags: ['必吃', '特色'], description: '云南经典美食' },
  { id: 47, name: '乳扇', city: '大理', cuisine_type: '云南菜', rating: 4.5, price_range: '¥15-30', tags: ['特色'], description: '大理特色小吃' },
  // 丽江
  { id: 48, name: '腊排骨火锅', city: '丽江', cuisine_type: '云南菜', rating: 4.7, price_range: '¥60-100', is_featured: true, tags: ['必吃', '特色'], description: '丽江特色美食' },
  { id: 49, name: '鸡豆凉粉', city: '丽江', cuisine_type: '云南菜', rating: 4.5, price_range: '¥10-20', tags: ['特色'], description: '丽江传统小吃' },
])

// 筛选后的景点
const filteredSpots = computed(() => {
  return spots.value.filter(spot => spot.city === selectedCity.value)
})

// 筛选后的美食
const filteredFoods = computed(() => {
  let result = foods.value.filter(food => food.city === selectedCity.value)
  
  if (selectedCuisine.value !== '全部') {
    result = result.filter(food => food.cuisine_type.includes(selectedCuisine.value))
  }
  
  return result.sort((a, b) => b.rating - a.rating)
})

// 加载景点数据
const loadSpots = async () => {
  loadingSpots.value = true
  try {
    const response = await fetch(`http://localhost:8000/api/spots/recommend?city=${encodeURIComponent(selectedCity.value)}&limit=20`)
    const data = await response.json()
    
    if (data.spots) {
      spots.value = data.spots
    } else if (Array.isArray(data)) {
      spots.value = data
    }
  } catch (error) {
    console.error('加载景点失败:', error)
    // 使用模拟数据
    spots.value = getMockSpots()
  } finally {
    loadingSpots.value = false
  }
}

// 模拟景点数据
const getMockSpots = () => {
  const mockData = {
    '北京': [
      { id: 1, name: '故宫博物院', rating: 4.9, tags: ['建筑宏伟', '历史厚重'], images: ['/images/spots/beijing/beijing_gugong_bowuyuan.jpg'], description: '中国明清两代的皇家宫殿，是世界上现存规模最大、保存最为完整的木质结构古建筑之一。' },
      { id: 2, name: '天坛公园', rating: 4.9, tags: ['古建绝美', '声学奇迹'], images: ['/images/spots/beijing/beijing_tiantan_gongyuan.jpg'], description: '明清两代皇帝祭天的场所，是中国现存最大的古代祭祀建筑群。' },
      { id: 3, name: '颐和园', rating: 4.9, tags: ['皇家园林', '湖光山色'], images: ['/images/spots/beijing/beijing_yiheyuan.jpg'], description: '中国清朝时期皇家园林，被誉为"皇家园林博物馆"。' },
      { id: 4, name: '长城-八达岭', rating: 4.8, tags: ['必玩景点', '地标建筑'], images: ['/images/spots/beijing/beijing_badaling_changcheng.jpg'], description: '万里长城的重要组成部分，是明长城的一个隘口。' },
      { id: 5, name: '天安门广场', rating: 4.8, tags: ['升旗仪式', '庄严神圣'], images: ['/images/spots/beijing/beijing_tiananmen_guangchang.jpg'], description: '世界上最大的城市广场之一，是中国的象征。' },
      { id: 6, name: '圆明园', rating: 4.7, tags: ['历史遗址', '园林景观'], images: ['/images/spots/beijing/beijing_yuanmingyuan.jpg'], description: '清代大型皇家园林，有"万园之园"之称。' },
    ],
    '上海': [
      { id: 11, name: '外滩', rating: 4.9, tags: ['地标建筑', '夜景绝美'], images: ['/images/spots/shanghai/shanghai_waitan.jpg'], description: '上海的标志性景观，拥有万国建筑博览群。' },
      { id: 12, name: '东方明珠', rating: 4.7, tags: ['地标建筑', '登高望远'], images: ['/images/spots/shanghai/shanghai_dongfang_mingzhu.jpg'], description: '上海标志性文化景观之一，是亚洲第一、世界第三的高塔。' },
      { id: 13, name: '豫园', rating: 4.8, tags: ['江南园林', '历史文化'], images: ['/images/spots/shanghai/shanghai_yuyuan.jpg'], description: '明代私人园林，充分体现了中国古典园林的设计与建造水平。' },
    ],
    '西安': [
      { id: 21, name: '兵马俑', rating: 4.9, tags: ['世界遗产', '历史厚重'], images: ['/images/spots/xian/xian_bingmayong.jpg'], description: '世界第八大奇迹，秦始皇陵的陪葬坑。' },
      { id: 22, name: '大雁塔', rating: 4.8, tags: ['古建绝美', '佛教文化'], images: ['/images/spots/xian/xian_dayanta.jpg'], description: '唐代佛教建筑艺术杰作，是古城西安的独特标志。' },
      { id: 23, name: '古城墙', rating: 4.7, tags: ['历史遗迹', '骑行游览'], images: ['/images/spots/xian/xian_xian_chengqiang.jpg'], description: '中国现存规模最大、保存最完整的古代城垣。' },
    ],
  }
  return mockData[selectedCity.value] || []
}

// 显示景点详情
const showSpotDetail = (spot) => {
  currentSpot.value = spot
  showSpotModal.value = true
}

// 显示美食详情
const showFoodDetail = (food) => {
  currentFood.value = food
  showFoodModal.value = true
}

// 格式化数字
const formatNumber = (num) => {
  if (num >= 10000) {
    return (num / 10000).toFixed(1) + 'w'
  } else if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'k'
  }
  return num.toString()
}

// 监听城市变化，重新加载景点
watch(selectedCity, () => {
  loadSpots()
}, { immediate: true })
</script>

<style scoped>
.explore-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #0a0a1a 0%, #1a1a2e 50%, #16213e 100%);
  color: #fff;
}

/* 主容器 */
.explore-container {
  display: flex;
  padding-top: 70px;
  min-height: 100vh;
}

/* 左侧边栏 */
.sidebar {
  width: 280px;
  background: rgba(20, 20, 40, 0.6);
  backdrop-filter: blur(20px);
  border-right: 1px solid rgba(0, 212, 255, 0.1);
  padding: 30px 20px;
  position: fixed;
  left: 0;
  top: 70px;
  bottom: 0;
  overflow-y: auto;
}

.sidebar-header {
  margin-bottom: 30px;
}

.sidebar-header h2 {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 8px;
  background: linear-gradient(135deg, #00d4ff, #fff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.sidebar-header p {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.5);
}

/* 侧边栏导航 */
.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 30px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 18px;
  border-radius: 12px;
  border: 1px solid transparent;
  background: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.7);
  font-size: 15px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(0, 212, 255, 0.3);
}

.nav-item.active {
  background: rgba(0, 212, 255, 0.15);
  border-color: rgba(0, 212, 255, 0.5);
  color: #00d4ff;
}

.nav-icon {
  font-size: 20px;
}

/* 城市筛选 */
.city-filter h3 {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 15px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.city-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.city-btn {
  padding: 8px 14px;
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  background: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.7);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.city-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.3);
}

.city-btn.active {
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  border-color: transparent;
  color: #fff;
}

/* 内容区域 */
.content-area {
  flex: 1;
  margin-left: 280px;
  padding: 30px 40px;
}

.section-header {
  margin-bottom: 30px;
}

.section-header h1 {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 10px;
}

.section-header p {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.5);
}

/* 美食分类筛选 */
.cuisine-filter {
  display: flex;
  gap: 10px;
  margin-bottom: 25px;
  flex-wrap: wrap;
}

.filter-btn {
  padding: 8px 16px;
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  background: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.7);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.filter-btn:hover {
  background: rgba(255, 255, 255, 0.1);
}

.filter-btn.active {
  background: rgba(0, 212, 255, 0.2);
  border-color: #00d4ff;
  color: #00d4ff;
}

/* 卡片网格 */
.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 20px;
}

.card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
}

.card:hover {
  transform: translateY(-5px);
  border-color: rgba(0, 212, 255, 0.3);
  box-shadow: 0 10px 30px rgba(0, 212, 255, 0.15);
}

.card-image {
  position: relative;
  height: 160px;
  overflow: hidden;
}

.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.card:hover .card-image img {
  transform: scale(1.05);
}

.card-badge {
  position: absolute;
  top: 10px;
  right: 10px;
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 10px;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(5px);
  border-radius: 20px;
  font-size: 13px;
}

.card-badge.featured {
  background: linear-gradient(135deg, #ff6b6b, #ff8e53);
}

.card-info {
  padding: 16px;
}

.card-info h3 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 10px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.card-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
}

.rating {
  color: #ffd700;
  font-size: 14px;
}

.favorites {
  color: #ff6b6b;
  font-size: 14px;
}

.price {
  color: #00d4ff;
  font-size: 14px;
}

.card-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.tag {
  padding: 4px 10px;
  background: rgba(0, 212, 255, 0.1);
  border-radius: 10px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
}

/* 加载状态 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  color: rgba(255, 255, 255, 0.5);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(255, 255, 255, 0.1);
  border-top-color: #00d4ff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  color: rgba(255, 255, 255, 0.5);
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 15px;
}

/* 弹窗 */
.modal {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(10px);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.modal-content {
  background: rgba(20, 20, 40, 0.95);
  border: 1px solid rgba(0, 212, 255, 0.2);
  border-radius: 20px;
  overflow: hidden;
  max-width: 500px;
  width: 100%;
  position: relative;
}

.modal-close {
  position: absolute;
  top: 15px;
  right: 15px;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: none;
  background: rgba(0, 0, 0, 0.5);
  color: #fff;
  font-size: 20px;
  cursor: pointer;
  z-index: 10;
  transition: all 0.3s ease;
}

.modal-close:hover {
  background: rgba(255, 255, 255, 0.2);
}

.modal-header {
  height: 200px;
  overflow: hidden;
}

.modal-header img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.modal-body {
  padding: 25px;
}

.modal-body h2 {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 12px;
}

.modal-rating {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 15px;
  font-size: 16px;
}

.modal-rating .star {
  color: #ffd700;
}

.modal-meta {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 15px;
}

.modal-tags {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.modal-desc {
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.7;
  font-size: 15px;
}

/* 响应式 */
@media (max-width: 1024px) {
  .sidebar {
    width: 240px;
  }
  
  .content-area {
    margin-left: 240px;
    padding: 20px;
  }
  
  .cards-grid {
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  }
}

@media (max-width: 768px) {
  .navbar {
    padding: 12px 20px;
  }
  
  .nav-menu {
    display: none;
  }
  
  .sidebar {
    width: 100%;
    position: relative;
    top: 0;
    border-right: none;
    border-bottom: 1px solid rgba(0, 212, 255, 0.1);
  }
  
  .explore-container {
    flex-direction: column;
  }
  
  .content-area {
    margin-left: 0;
  }
  
  .cards-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 15px;
  }
}
</style>
