﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿<template>
  <div class="diary-detail-page">
    <!-- 大背景层：用户图片 + 亮度降低 -->
    <div class="page-background">
      <transition name="bg-switch">
        <div 
          v-show="currentBgImage"
          :key="currentBgImage"
          class="bg-image"
          :style="{ backgroundImage: `url(${currentBgImage})` }"
        ></div>
      </transition>
      <div v-show="!currentBgImage" class="bg-white"></div>
      <div class="bg-dim-overlay"></div>
    </div>
    
    <Navbar />
    
    <main class="page-content">
      <div class="detail-container">
        <!-- 返回按钮 -->
        <button class="back-btn" @click="$router.back()">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M19 12H5M12 19l-7-7 7-7"/>
          </svg>
          <span>返回</span>
        </button>
        
        <!-- 日记内容卡片 - 模糊白底背景 -->
        <article class="diary-card glass-card">
          <!-- Hero区域：封面图 + 标题叠加 -->
          <div class="hero-section" v-if="diary.images && diary.images.length">
            <div class="hero-image-wrapper">
              <img :src="diary.images[0]" :alt="diary.title" class="hero-image" />
              <div class="hero-overlay"></div>
              <div class="hero-content">
                <h1 class="diary-title">{{ diary.title }}</h1>
                <div class="hero-meta">
                  <span class="author">{{ diary.username || '作者' }}</span>
                  <span class="separator">·</span>
                  <span class="date">{{ formatDate(diary.created_at) }}</span>
                </div>
              </div>
            </div>
          </div>
          <div class="title-section" v-else>
            <h1 class="diary-title">{{ diary.title }}</h1>
            <div class="hero-meta">
              <span class="author">{{ diary.username || '作者' }}</span>
              <span class="separator">·</span>
              <span class="date">{{ formatDate(diary.created_at) }}</span>
            </div>
          </div>
          
          <!-- 玻璃拟态标签栏 -->
          <div class="metadata-pills">
            <div class="pill budget-pill">
              <svg class="pill-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
              <span class="pill-label">预算</span>
              <span class="pill-value">{{ diary.budget || '¥3,000' }}</span>
            </div>
            <div class="pill companion-pill">
              <svg class="pill-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"/>
              </svg>
              <span class="pill-label">同伴</span>
              <span class="pill-value">{{ diary.companion || '朋友' }}</span>
            </div>
            <div class="pill date-pill">
              <svg class="pill-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                <line x1="16" y1="2" x2="16" y2="6"/>
                <line x1="8" y1="2" x2="8" y2="6"/>
                <line x1="3" y1="10" x2="21" y2="10"/>
              </svg>
              <span class="pill-label">日期</span>
              <span class="pill-value">{{ formatDate(diary.created_at) }}</span>
            </div>
            <div class="pill rating-pill">
              <svg class="pill-icon" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
              </svg>
              <span class="pill-value">{{ (diary.avg_rating || 0).toFixed(1) }}</span>
              <span class="pill-label">({{ diary.rating_count || 0 }})</span>
            </div>
          </div>
          
          <!-- 内容区域 -->
          <div class="content-section">
            <!-- 时间轴行程 -->
            <div class="timeline-section" v-if="parsedItinerary.length > 0">
              <h3 class="section-title">行程安排</h3>
              <div class="timeline">
                <div 
                  v-for="(day, index) in parsedItinerary" 
                  :key="index"
                  class="timeline-day"
                >
                  <div class="timeline-header">
                    <div class="day-badge">{{ day.day }}</div>
                    <h4 class="day-title">{{ day.title }}</h4>
                  </div>
                  <div class="timeline-content">
                    <div 
                      v-for="(spot, spotIndex) in day.spots" 
                      :key="spotIndex"
                      class="timeline-item"
                    >
                      <div class="timeline-dot"></div>
                      <div class="timeline-line" v-if="spotIndex < day.spots.length - 1"></div>
                      <div class="timeline-item-body">
                        <div class="timeline-item-content">
                          <span class="time-marker">{{ spot.time }}</span>
                          <p class="spot-description">{{ spot.description }}</p>
                          <span v-if="spot.location" class="spot-location">📍 {{ spot.location }}</span>
                        </div>
                        <div class="timeline-item-image" v-if="getSpotImage(day.day, spotIndex)">
                          <img 
                            :src="getSpotImage(day.day, spotIndex)" 
                            :alt="spot.location || spot.time"
                            @click="openImagePreview(getSpotImage(day.day, spotIndex))"
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 日记正文 -->
            <div class="diary-body" v-html="renderContent(diary.content)"></div>
          </div>
          
          <!-- 图片画廊 -->
        <div class="gallery-section" v-if="diary.images && diary.images.length > 1">
          <h3 class="section-title">旅行相册</h3>
          <div class="gallery-grid">
            <div 
              v-for="(img, index) in diary.images.slice(1)" 
              :key="index"
              class="gallery-item"
              :class="{ 'large': index === 0 }"
            >
              <img :src="img" :alt="`${diary.title} - ${index + 2}`" />
            </div>
          </div>
        </div>
        
        <!-- 旅行视频 -->
        <div class="travel-video-section" v-if="parsedVideos && parsedVideos.length > 0">
          <h3 class="section-title">旅行视频</h3>
          <div class="video-grid">
            <div 
              v-for="(video, index) in parsedVideos" 
              :key="index"
              class="video-item"
            >
              <div class="video-aspect-ratio">
                <video 
                  :src="video" 
                  controls 
                  preload="metadata"
                  class="video-player"
                  :poster="getVideoPoster(index)"
                >
                  您的浏览器不支持视频播放
                </video>
              </div>
            </div>
          </div>
        </div>
        
        <!-- AIGC 动画区域 -->
        <div class="aigc-animation-section">
          <div class="aigc-header">
            <h3 class="section-title">
              <svg class="aigc-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
              </svg>
              AI 旅游动画
            </h3>
            <p class="aigc-desc">基于您的旅行照片，AI 自动生成电影级动画视频</p>
          </div>
          
          <!-- 已生成动画：显示播放器 -->
          <div v-if="animationUrl" class="aigc-video-wrapper">
            <video 
              :src="animationUrl" 
              controls 
              autoplay 
              loop 
              preload="auto"
              class="aigc-video-player"
              poster="https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&q=80"
            >
              您的浏览器不支持视频播放
            </video>
            <div class="aigc-badge">AI 生成</div>
          </div>
          
          <!-- 未生成：显示生成按钮 -->
          <div v-else class="aigc-generate-area">
            <div class="aigc-preview-grid" v-if="diary.images && diary.images.length > 0">
              <div class="aigc-preview-item">
                <img :src="diary.images[0]" alt="封面图" />
              </div>
              <div class="aigc-arrow">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M5 12h14M12 5l7 7-7 7"/>
                </svg>
              </div>
              <div class="aigc-preview-placeholder">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <polygon points="5 3 19 12 5 21 5 3"/>
                </svg>
                <span>AI 动画</span>
              </div>
            </div>
            
            <button 
              class="aigc-generate-btn" 
              @click="generateAnimation"
              :disabled="isGenerating"
            >
              <svg v-if="!isGenerating" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
              </svg>
              <span v-if="isGenerating" class="loading-spinner"></span>
              {{ isGenerating ? 'AI 正在生成中...' : '一键生成 AI 动画' }}
            </button>
            <p v-if="generatingProgress" class="generating-tip">{{ generatingProgress }}</p>
          </div>
        </div>
      </article>
        
        <!-- 评论和评分组件 -->
        <div class="interaction-section">
          <CommentsRatings :diary-id="diaryId" />
        </div>
      </div>
    </main>
    
    <!-- 图片预览弹窗 -->
    <div v-if="showPreview" class="image-preview-overlay" @click="closeImagePreview">
      <div class="image-preview-container">
        <img :src="previewImage" alt="预览" />
        <button class="preview-close-btn" @click.stop="closeImagePreview">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M18 6L6 18M6 6l12 12"/>
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import Navbar from '../components/Navbar.vue'
import CommentsRatings from '../components/CommentsRatings.vue'

const route = useRoute()
const diaryId = ref(parseInt(route.params.id))
const diary = ref({
  id: diaryId.value,
  title: '',
  content: '',
  username: '',
  created_at: '',
  view_count: 0,
  avg_rating: 0,
  rating_count: 0,
  images: [],
  budget: '',
  companion: ''
})

// 每篇日记专属的时间轴数据
const mockItineraries = {
  1: [
    {
      day: 'Day 1',
      title: '初抵京都',
      spots: [
        { time: '上午', description: '从大阪关西机场出发，乘坐Haruka特急列车抵达京都站' },
        { time: '下午', description: '入住祇园附近传统日式旅馆，感受榻榻米与枯山水庭院' },
        { time: '晚上', description: '漫步花见小路，体验京都夜色的静谧与优雅' }
      ]
    },
    {
      day: 'Day 2',
      title: '清水寺与二年坂',
      spots: [
        { time: '清晨', description: '六点起床前往清水寺，避开游客大军，欣赏晨光中的红叶' },
        { time: '上午', description: '漫步二年坂石板路，拍摄传统町家建筑' },
        { time: '下午', description: '在茶室品尝抹茶，体验日本茶道文化' }
      ]
    },
    {
      day: 'Day 3',
      title: '岚山竹林',
      spots: [
        { time: '上午', description: '穿越岚山竹林小径，感受天然绿色隧道的神秘' },
        { time: '中午', description: '在岚山よしむら品尝手工荞麦面' },
        { time: '下午', description: '漫步渡月桥，在% Arabica咖啡店欣赏河景' }
      ]
    }
  ],
  2: [
    {
      day: '第一站',
      title: '冒椒火辣',
      spots: [
        { time: '探店', description: '藏在奎星楼街深处的网红串串店，秘制牛油锅底麻辣鲜香' },
        { time: '必点', description: '牛肉串腌制入味，毛肚七上八下口感脆爽，脑花入口即化' }
      ]
    },
    {
      day: '第二站',
      title: '洞子口张老二凉粉',
      spots: [
        { time: '探店', description: '开了三十多年的老字号，成都人从小吃到大的味道' },
        { time: '必点', description: '黄凉粉和白凉粉各有千秋，配上特制红油辣椒让人欲罢不能' }
      ]
    },
    {
      day: '第三站',
      title: '陈麻婆豆腐',
      spots: [
        { time: '探店', description: '麻婆豆腐的发源地，教科书级别的正宗味道' },
        { time: '必点', description: '豆腐嫩滑，肉末酥香，花椒的麻与辣椒的辣完美融合' }
      ]
    },
    {
      day: '第四站',
      title: '贺记蛋烘糕',
      spots: [
        { time: '探店', description: '成都传统小吃的佼佼者，现点现做' },
        { time: '必点', description: '外皮金黄酥脆，内里松软香甜，是成都人的童年回忆' }
      ]
    }
  ],
  3: [
    {
      day: 'Day 1-2',
      title: '雷克雅未克',
      spots: [
        { time: '上午', description: '抵达世界上最北的首都，感受这座12万人口城市的艺术气息' },
        { time: '下午', description: '登顶哈尔格林姆教堂，俯瞰雷克雅未克全城' },
        { time: '傍晚', description: '在太阳航海者雕塑前欣赏海边日落，感受维京人的探索精神' }
      ]
    },
    {
      day: 'Day 3-4',
      title: '黄金圈',
      spots: [
        { time: '上午', description: '辛格维利尔国家公园，欧亚板块和北美板块的分界线' },
        { time: '中午', description: '等待间歇泉喷发，水柱高达30米的壮观景象' },
        { time: '下午', description: '黄金瀑布，感受冰岛最壮观的瀑布之一' }
      ]
    },
    {
      day: 'Day 5-7',
      title: '南岸风光',
      spots: [
        { time: '上午', description: '维克黑沙滩，黑色火山沙与白色海浪的强烈对比' },
        { time: '下午', description: '参加冰川徒步团，穿上冰爪在千年冰川上行走' },
        { time: '晚上', description: '寻找极光的最佳观测点，等待绿色光带在夜空舞动' }
      ]
    },
    {
      day: 'Day 8-14',
      title: '冰河湖与极光',
      spots: [
        { time: '上午', description: '杰古沙龙冰河湖，蓝色浮冰漂浮在湖面上的绝美景象' },
        { time: '下午', description: '钻石沙滩，冰块散落在黑沙滩上如钻石般闪耀' },
        { time: '深夜', description: '终于等到极光爆发，绿色光带在夜空中舞动，像上天的馈赠' }
      ]
    }
  ]
}

// 解析行程数据 - 优先使用API返回的itinerary数据
const parsedItinerary = computed(() => {
  // 优先使用从API获取的itinerary数据
  if (diary.value.itinerary && diary.value.itinerary.length > 0) {
    // 转换API数据格式为组件需要的格式
    return diary.value.itinerary.map((day, index) => {
      // 处理 activities 或 spots 字段
      const activities = day.activities || day.spots || []
      return {
        day: typeof day.day === 'number' ? `Day ${day.day}` : (day.day || `Day ${index + 1}`),
        title: day.theme || day.title || '精彩一天',
        spots: activities.map(activity => ({
          time: activity.time || '09:00',
          description: activity.title || activity.description || activity.insight || ''
        }))
      }
    })
  }
  // 如果是精美日记(1-3)，使用mock数据
  if (diaryId.value >= 1 && diaryId.value <= 3 && mockDiaries[diaryId.value]) {
    return mockItineraries[diaryId.value] || []
  }
  return []
})

// 解析视频数据 - 从diary.videos字段获取
const parsedVideos = computed(() => {
  if (!diary.value.videos) return []
  
  // 如果是字符串，尝试解析JSON
  let videos = []
  if (typeof diary.value.videos === 'string') {
    try {
      videos = JSON.parse(diary.value.videos)
    } catch {
      return []
    }
  } else if (Array.isArray(diary.value.videos)) {
    videos = diary.value.videos
  } else {
    return []
  }
  
  // 将相对路径转换为完整URL
  return videos.map(video => {
    if (typeof video === 'string' && video.startsWith('/')) {
      return `${window.location.origin}${video}`
    }
    return video
  })
})

// 获取视频封面图（使用日记图片作为封面）
const getVideoPoster = (index) => {
  if (!diary.value.images || diary.value.images.length === 0) return ''
  // 使用封面图或轮播图片作为视频封面
  return diary.value.images[index % diary.value.images.length] || ''
}

// Mock 数据
const mockDiaries = {
  1: {
    id: 1,
    title: 'Kyoto 京都：千年古都的秋日私语',
    content: `京都，这座承载着日本千年历史的古都，每一个角落都散发着独特的魅力。这次秋日的京都之行，让我深深沉醉在红叶与古寺的交织中。

清晨从大阪关西机场出发，乘坐Haruka特急列车，约75分钟便抵达京都站。一出车站，就能感受到这座城市特有的宁静与庄重。

🏨 住宿推荐：
选择了位于祇园附近的传统日式旅馆"花见小路庵"。推开木质拉门，榻榻米的气息扑面而来，窗外是精致的枯山水庭院。

清晨六点起床，赶在游客大军到来之前前往清水寺。晨光中的清水舞台被红叶环绕，那种美让人屏息。

📸 拍照Tips：
- 清水舞台正面是经典机位，但人太多
- 推荐绕到舞台侧面，可以拍到红叶与建筑的层次感
- 二年坂的清晨几乎没有游客，石板路与传统町家建筑相得益彰

岚山的竹林小径是此行最期待的景点之一。高耸入云的竹子形成天然的绿色隧道，阳光透过竹叶洒下斑驳光影。

🍜 美食推荐：
- 岚山よしむら：手工荞麦面，窗外就是渡月桥
- % Arabica：网红咖啡店，但景色确实值得

金阁寺的倒影在镜湖池中完美呈现，这座被金箔覆盖的楼阁在阳光下熠熠生辉。

龙安寺的枯山水庭院则是另一种美。十五块石头精心布置在白砂之中，坐在廊下静静凝视，内心逐渐平静。

🚇 交通：购买京都巴士一日券（700日元），基本可以覆盖所有景点
💰 预算：4天3夜约8万日元（含住宿、餐饮、交通）
📅 最佳季节：11月中旬至12月上旬（红叶季）

京都的美，在于它的克制与留白。无论是枯山水的禅意，还是町家建筑的素雅，都在诉说着一种"少即是多"的美学理念。这座城市值得慢慢品味，而不是匆匆打卡。`,
    username: '旅行摄影师小林',
    created_at: '2024-11-15T08:30:00',
    view_count: 3280,
    avg_rating: 4.9,
    rating_count: 156,
    budget: '¥4,000',
    companion: '独自',
    images: [
      'https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=1200&q=80',
      'https://images.unsplash.com/photo-1528360983277-13d401cdc186?w=800&q=80',
      'https://images.unsplash.com/photo-1545569341-9eb8b30979d9?w=800&q=80',
      'https://images.unsplash.com/photo-1524413840807-0c3cb6fa808d?w=800&q=80'
    ],
    diary_type: 'travel'
  },
  2: {
    id: 2,
    title: '成都美食探店：藏在巷子里的烟火气',
    content: `成都是一座来了就不想走的城市，而让我留恋的，正是那些藏在巷子深处的美食。这次用三天时间，深度探索了本地人最爱的几家小店。

【第一站：冒椒火辣】
这家串串店藏在奎星楼街的深处，店面不大，但总是排着长队。他们的秘制牛油锅底是灵魂，麻辣鲜香，回味悠长。

🍢 必点推荐：
- 牛肉串：腌制入味，涮烫后嫩滑多汁
- 毛肚：七上八下，口感脆爽
- 脑花：处理得很干净，入口即化

【第二站：洞子口张老二凉粉】
开了三十多年的老字号，是成都人从小吃到大的味道。黄凉粉和白凉粉各有千秋，配上特制的红油辣椒，简单却让人欲罢不能。

【第三站：陈麻婆豆腐】
麻婆豆腐的发源地，这里的麻婆豆腐堪称教科书级别。豆腐嫩滑，肉末酥香，花椒的麻与辣椒的辣完美融合。

【第四站：贺记蛋烘糕】
蛋烘糕是成都的传统小吃，贺记是其中的佼佼者。现点现做，外皮金黄酥脆，内里松软香甜。

成都的美食，不在于装修有多豪华，而在于那份烟火气和人情味。老板会热情地跟你聊天，推荐今天的新鲜食材。这种氛围，是连锁餐厅永远给不了的。`,
    username: '吃货小王',
    created_at: '2024-12-01T14:20:00',
    view_count: 2156,
    avg_rating: 4.8,
    rating_count: 89,
    budget: '¥800',
    companion: '朋友',
    images: [
      'https://images.unsplash.com/photo-1563245372-f21724e3856d?w=1200&q=80',
      'https://images.unsplash.com/photo-1541696432-82c6da8ce7bf?w=800&q=80',
      'https://images.unsplash.com/photo-1594007654729-407eedc4be65?w=800&q=80'
    ],
    diary_type: 'food'
  },
  3: {
    id: 3,
    title: '冰岛环岛自驾：追逐极光的14天',
    content: `冰岛，这个被称为"火与冰之国"的地方，一直是我旅行清单上的必去之地。经过半年的筹备，终于踏上了这片神奇的土地。

【Day 1-2 雷克雅未克】
首都雷克雅未克是世界上最北的首都，人口只有12万，却充满了艺术气息。

📍 必去景点：
- 哈尔格林姆教堂：雷克雅未克地标，登顶可俯瞰全城
- 太阳航海者雕塑：海边的不锈钢雕塑，象征着维京人的探索精神

【Day 3-4 黄金圈】
黄金圈是冰岛最经典的路线，包含三个主要景点。

🌊 辛格维利尔国家公园：
欧亚板块和北美板块的分界线就在这里，可以清晰地看到板块漂移形成的裂缝。

⛲ 间歇泉：
每隔5-10分钟喷发一次，水柱高达30米。等待喷发的那一刻，所有人都屏住呼吸。

【Day 5-7 南岸风光】
南岸是冰岛景观最丰富的地区，瀑布、黑沙滩、冰川应有尽有。

🖤 维克黑沙滩：
黑色的火山沙与白色的海浪形成强烈对比，玄武岩柱群更是拍照的绝佳背景。

🏔️ 瓦特纳冰川：
参加了冰川徒步团，穿上冰爪，在千年冰川上行走，那种震撼难以言表。

【Day 8-10 冰河湖】
杰古沙龙冰河湖是此行的高潮。蓝色的浮冰漂浮在湖面上，像是大自然雕刻的艺术品。

【Day 11-14 极光之夜】
在环岛的最后几晚，终于等来了极光。绿色的光带在夜空中舞动，像是上天的馈赠。

冰岛教会我敬畏自然。在这片土地上，人类是如此渺小，而自然是如此伟大。`,
    username: '极地探险者',
    created_at: '2024-10-20T10:00:00',
    view_count: 5620,
    avg_rating: 5.0,
    rating_count: 234,
    budget: '¥35,000',
    companion: '情侣',
    images: [
      'https://images.unsplash.com/photo-1531366936337-7c912a4589a7?w=1200&q=80',
      'https://images.unsplash.com/photo-1520769945061-0a448c463865?w=800&q=80',
      'https://images.unsplash.com/photo-1476610182048-b716b8518aae?w=800&q=80',
      'https://images.unsplash.com/photo-1518182170546-0766bc6f9213?w=800&q=80'
    ],
    diary_type: 'travel'
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const renderContent = (content) => {
  if (!content) return ''
  let html = content
    .replace(/\n/g, '<br/>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
  
  // 为表情符号添加样式
  html = html.replace(/(📍|⏰|💰|🍢|🍲|🥞|🌶️|⚠️|🚇|🏨|📸|🍜|🚗|✈️|🏔️|🌊|⛲|🌈|💦|🖤|🦭|🌋|♨️|⛰️|🌌|📷|🎨|🌡️|👕|⛽)/g, '<span class="content-icon">$1</span>')
  
  return html
}

const loadDiary = async () => {
  try {
    const response = await fetch(`/api/diaries/${diaryId.value}`)
    if (response.ok) {
      const data = await response.json()
      console.log('[DiaryDetail] API返回数据:', data)
      console.log('[DiaryDetail] images字段:', data.images, '长度:', data.images?.length)
      // 检查返回的数据是否有效（有id和title）
      if (data && data.id && data.title) {
        diary.value = { ...diary.value, ...data }
        // 数据加载完成后立即初始化背景和区块检测
        setTimeout(() => {
          initBackground()
          updateContentSections()
        }, 100)
        return
      }
    }
    // API请求失败或返回无效数据，尝试使用mock数据
    console.warn('API加载日记失败，尝试使用mock数据')
    fallbackToMock()
  } catch (error) {
    console.error('加载日记失败:', error)
    fallbackToMock()
  }
}

// 回退到mock数据
const fallbackToMock = () => {
  if (diaryId.value >= 1 && diaryId.value <= 3 && mockDiaries[diaryId.value]) {
    diary.value = { ...mockDiaries[diaryId.value] }
  } else {
    diary.value = {
      id: diaryId.value,
      title: '日记加载失败',
      content: '无法加载该日记内容，请稍后重试。',
      username: '',
      created_at: new Date().toISOString(),
      view_count: 0,
      avg_rating: 0,
      rating_count: 0,
      images: [],
      budget: '',
      companion: ''
    }
  }
}

onMounted(() => {
  loadDiary()
})

// 为时间轴节点分配图片 - 按顺序将日记图片分配给各个时间节点
const getSpotImage = (dayLabel, spotIndex) => {
  if (!diary.value.images || diary.value.images.length <= 1) return null
  
  // 计算在所有天数中的累计索引
  let globalIndex = 0
  for (const day of parsedItinerary.value) {
    if (day.day === dayLabel) {
      globalIndex += spotIndex
      break
    }
    globalIndex += day.spots.length
  }
  
  // 从第二张图片开始分配（第一张是封面）
  const imageIndex = globalIndex % (diary.value.images.length - 1)
  return diary.value.images[imageIndex + 1] || null
}

// 图片预览
const previewImage = ref('')
const showPreview = ref(false)

// AIGC 动画相关
const animationUrl = ref('')
const isGenerating = ref(false)
const generatingProgress = ref('')

const openImagePreview = (src) => {
  previewImage.value = src
  showPreview.value = true
}

const closeImagePreview = () => {
  showPreview.value = false
  previewImage.value = ''
}

// 生成 AI 动画
const generateAnimation = async () => {
  isGenerating.value = true
  generatingProgress.value = '正在初始化 AI 模型...'
  
  try {
    const userId = localStorage.getItem('userId') || 1
    
    generatingProgress.value = '正在上传图片到 AI 模型...'
    const response = await fetch(`/api/diaries/${diaryId.value}/generate-animation?user_id=${userId}`, {
      method: 'POST'
    })
    
    if (response.ok) {
      const data = await response.json()
      if (data.success) {
        animationUrl.value = data.animation_url
        generatingProgress.value = '动画生成成功！'
        setTimeout(() => { generatingProgress.value = '' }, 3000)
      } else {
        generatingProgress.value = `生成失败: ${data.message}`
      }
    } else {
      generatingProgress.value = '生成失败，请稍后重试'
    }
  } catch (error) {
    console.error('AI 动画生成失败:', error)
    generatingProgress.value = '网络异常，请稍后重试'
  } finally {
    isGenerating.value = false
  }
}

// 查询动画状态
const checkAnimationStatus = async () => {
  try {
    const userId = localStorage.getItem('userId') || 1
    const response = await fetch(`/api/diaries/${diaryId.value}/animation-status?user_id=${userId}`)
    if (response.ok) {
      const data = await response.json()
      if (data.has_animation) {
        animationUrl.value = data.animation_url
      }
    }
  } catch (error) {
    console.error('查询动画状态失败:', error)
  }
}

// 滚动背景相关
// 当前背景图片
const currentBgImage = ref('')
const currentBgIndex = ref(0)

// 默认背景图（当没有上传图片时使用）
const DEFAULT_BG_IMAGE = '/default-diary-bg.jpg'

// 获取所有可用作背景的图片
const backgroundImages = computed(() => {
  if (!diary.value.images || diary.value.images.length === 0) {
    // 没有上传图片时，返回默认背景图
    return [DEFAULT_BG_IMAGE]
  }
  // 使用所有图片作为背景候选（包括封面）
  return diary.value.images
})

// 计算每个内容区块的位置用于滚动切换
const contentSections = ref([])

const updateContentSections = () => {
  // 获取所有主要内容区块
  const sections = []
  
  // Hero区域
  const hero = document.querySelector('.hero-section, .title-section')
  if (hero) sections.push({ el: hero, type: 'hero' })
  
  // 时间轴节点
  const timelineItems = document.querySelectorAll('.timeline-item')
  timelineItems.forEach((item, index) => {
    sections.push({ el: item, type: 'timeline', index })
  })
  
  // 画廊图片
  const galleryItems = document.querySelectorAll('.gallery-item')
  galleryItems.forEach((item, index) => {
    sections.push({ el: item, type: 'gallery', index })
  })
  
  contentSections.value = sections
}

// 滚动监听 - 切换背景图片
const handleScroll = () => {
  if (backgroundImages.value.length === 0) return
  
  const scrollY = window.scrollY
  const windowHeight = window.innerHeight
  const triggerLine = scrollY + windowHeight * 0.4 // 触发线位于视口40%位置
  
  // 找到当前位于触发线附近的内容区块
  let activeIndex = 0
  let minDistance = Infinity
  
  contentSections.value.forEach((section, index) => {
    if (section.el) {
      const rect = section.el.getBoundingClientRect()
      const sectionCenter = rect.top + rect.height / 2 + scrollY
      const distance = Math.abs(sectionCenter - triggerLine)
      
      if (distance < minDistance) {
        minDistance = distance
        activeIndex = index
      }
    }
  })
  
  // 切换背景图片（循环使用可用图片）
  const newIndex = activeIndex % backgroundImages.value.length
  if (newIndex !== currentBgIndex.value) {
    currentBgIndex.value = newIndex
    currentBgImage.value = backgroundImages.value[newIndex]
  }
}

// 初始化背景
const initBackground = () => {
  if (backgroundImages.value.length > 0) {
    currentBgImage.value = backgroundImages.value[0]
    currentBgIndex.value = 0
  }
}

onMounted(() => {
  loadDiary()
  // 滚动监听
  window.addEventListener('scroll', handleScroll)
  // 检查是否已有 AI 动画
  setTimeout(() => checkAnimationStatus(), 2000)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<style scoped>
/* 大背景层 */
.page-background {
  position: fixed;
  inset: 0;
  z-index: -2;
  overflow: hidden;
}

.bg-image {
  position: absolute;
  inset: 0;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  transition: opacity 0.6s ease-in-out;
}

.bg-white {
  position: absolute;
  inset: 0;
  background: #f8f9fc;
}

.bg-dim-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.15);
  transition: opacity 0.3s ease;
}

/* 背景切换动画 */
.bg-switch-enter-active,
.bg-switch-leave-active {
  transition: opacity 0.6s ease-in-out;
}

.bg-switch-enter-from,
.bg-switch-leave-to {
  opacity: 0;
}

/* 日记详情页 */
.diary-detail-page {
  min-height: 100vh;
  position: relative;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  padding-top: 80px;
}

.mesh-gradient-bg {
  position: fixed;
  inset: 0;
  z-index: -1;
  background: linear-gradient(180deg, #F8F9FC 0%, #FFFFFF 50%, #F8F9FC 100%);
}

.blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.4;
}

.blob-1 {
  width: 400px;
  height: 400px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  top: -100px;
  left: -100px;
}

.blob-2 {
  width: 300px;
  height: 300px;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  top: 40%;
  right: -50px;
}

.blob-3 {
  width: 350px;
  height: 350px;
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  bottom: -100px;
  left: 30%;
}

.page-content {
  padding: 100px 20px 60px;
  max-width: 800px;
  margin: 0 auto;
}

.detail-container {
  position: relative;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 12px;
  cursor: pointer;
  margin-bottom: 24px;
  transition: all 0.3s ease;
  font-size: 14px;
  color: #333;
}

.back-btn:hover {
  background: rgba(255, 255, 255, 1);
  transform: translateX(-4px);
}

.diary-card {
  background: rgba(255, 255, 255, 0.62);
  backdrop-filter: blur(14px) saturate(120%);
  border-radius: 24px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

/* 玻璃拟态卡片增强效果 */
.glass-card {
  position: relative;
}

.glass-card::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(
    135deg,
    rgba(255, 255, 255, 0.4) 0%,
    rgba(255, 255, 255, 0.1) 100%
  );
  border-radius: 24px;
  pointer-events: none;
}

/* 旅行视频区域 */
.travel-video-section {
  margin-top: 2rem;
}

.video-grid {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin-top: 1.5rem;
}

.video-item {
  width: 100%;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.video-aspect-ratio {
  position: relative;
  width: 100%;
  padding-top: 56.25%; /* 16:9 */
  background: #000;
}

.video-player {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: contain;
  border-radius: 16px;
}

.video-player::-webkit-media-controls-panel {
  background: linear-gradient(to top, rgba(0, 0, 0, 0.7), transparent);
}

.video-player::cue {
  background: rgba(0, 0, 0, 0.8);
  color: #fff;
  font-size: 14px;
}

/* Hero区域 */
.hero-section {
  position: relative;
}

.hero-image-wrapper {
  position: relative;
  height: 400px;
  overflow: hidden;
}

.hero-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.hero-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.7) 0%, transparent 60%);
}

.hero-content {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 40px;
  color: white;
}

.diary-title {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 12px;
  line-height: 1.3;
}

.hero-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  opacity: 0.9;
}

.separator {
  opacity: 0.5;
}

.title-section {
  padding: 40px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.metadata-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  padding: 24px 40px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.pill {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: rgba(0, 0, 0, 0.03);
  border-radius: 50px;
  font-size: 14px;
}

.pill-icon {
  width: 18px;
  height: 18px;
  color: #667eea;
}

.pill-label {
  color: #666;
}

.pill-value {
  font-weight: 600;
  color: #333;
}

.content-section {
  padding: 40px;
}

.section-title {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 24px;
  color: #333;
}

/* 时间轴样式 */
.timeline-section {
  margin-bottom: 40px;
  padding: 24px;
  background: rgba(102, 126, 234, 0.05);
  border-radius: 16px;
}

.timeline-day {
  margin-bottom: 32px;
}

.timeline-day:last-child {
  margin-bottom: 0;
}

.timeline-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.day-badge {
  padding: 6px 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.day-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.timeline-content {
  position: relative;
  padding-left: 24px;
}

.timeline-item {
  position: relative;
  padding-bottom: 20px;
}

.timeline-dot {
  position: absolute;
  left: -24px;
  top: 4px;
  width: 12px;
  height: 12px;
  background: #667eea;
  border-radius: 50%;
  border: 3px solid white;
  box-shadow: 0 0 0 2px #667eea;
}

.timeline-line {
  position: absolute;
  left: -19px;
  top: 16px;
  width: 2px;
  height: calc(100% - 4px);
  background: linear-gradient(to bottom, #667eea, transparent);
}

.timeline-item-body {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding-left: 16px;
}

.timeline-item-content {
  flex: 1;
  min-width: 0;
}

.time-marker {
  display: inline-block;
  padding: 4px 10px;
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  margin-bottom: 8px;
}

.spot-description {
  font-size: 15px;
  line-height: 1.6;
  color: #555;
  margin-bottom: 6px;
}

.spot-location {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #888;
  font-weight: 500;
}

.timeline-item-image {
  width: 120px;
  height: 90px;
  border-radius: 10px;
  overflow: hidden;
  flex-shrink: 0;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.timeline-item-image:hover {
  transform: scale(1.05);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.timeline-item-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 图片预览弹窗 */
.image-preview-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 40px;
  animation: fadeIn 0.3s ease;
}

.image-preview-container {
  position: relative;
  max-width: 90vw;
  max-height: 90vh;
}

.image-preview-container img {
  max-width: 100%;
  max-height: 90vh;
  border-radius: 12px;
  object-fit: contain;
}

.preview-close-btn {
  position: absolute;
  top: -16px;
  right: -16px;
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.preview-close-btn:hover {
  background: rgba(255, 71, 87, 0.8);
  border-color: rgba(255, 71, 87, 0.5);
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.diary-body {
  font-size: 16px;
  line-height: 1.8;
  color: #444;
}

.diary-body :deep(br) {
  margin-bottom: 12px;
}

.content-icon {
  font-size: 1.2em;
  margin-right: 4px;
}

.gallery-section {
  padding: 0 40px 40px;
}

.gallery-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.gallery-item {
  border-radius: 12px;
  overflow: hidden;
  aspect-ratio: 4/3;
}

.gallery-item.large {
  grid-column: span 2;
  aspect-ratio: 16/9;
}

.gallery-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.gallery-item:hover img {
  transform: scale(1.05);
}

/* 视频区域样式 */
.video-section {
  padding: 0 40px 40px;
}

.video-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 24px;
}

.video-item {
  border-radius: 16px;
  overflow: hidden;
  background: #000;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  transition: all 0.3s ease;
}

.video-item:hover {
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.18);
  transform: translateY(-2px);
}

.video-player {
  width: 100%;
  display: block;
  max-height: 500px;
  object-fit: contain;
  background: #000;
}

.video-player::-webkit-media-controls-panel {
  background: linear-gradient(to top, rgba(0, 0, 0, 0.7), transparent);
}

.video-player::cue {
  background: rgba(0, 0, 0, 0.8);
  color: #fff;
  font-size: 14px;
}

.interaction-section {
  margin-top: 40px;
}

/* AIGC 动画区域 */
.aigc-animation-section {
  padding: 32px 40px 40px;
  border-top: 1px solid rgba(0, 0, 0, 0.05);
}

.aigc-header {
  margin-bottom: 24px;
}

.aigc-header .section-title {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.aigc-icon {
  width: 24px;
  height: 24px;
  color: #667eea;
}

.aigc-desc {
  font-size: 14px;
  color: #888;
  margin: 0;
}

/* 已生成动画播放器 */
.aigc-video-wrapper {
  position: relative;
  border-radius: 16px;
  overflow: hidden;
  background: #000;
  box-shadow: 0 12px 32px rgba(102, 126, 234, 0.2);
}

.aigc-video-player {
  width: 100%;
  display: block;
  max-height: 450px;
  object-fit: contain;
  background: #000;
}

.aigc-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  padding: 6px 12px;
  background: rgba(102, 126, 234, 0.85);
  backdrop-filter: blur(10px);
  color: white;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

/* 未生成：预览网格 */
.aigc-generate-area {
  text-align: center;
}

.aigc-preview-grid {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
  margin-bottom: 24px;
  padding: 24px;
  background: rgba(102, 126, 234, 0.05);
  border-radius: 16px;
}

.aigc-preview-item {
  width: 140px;
  height: 100px;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.aigc-preview-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.aigc-arrow {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #667eea;
}

.aigc-arrow svg {
  width: 100%;
  height: 100%;
}

.aigc-preview-placeholder {
  width: 140px;
  height: 100px;
  border-radius: 10px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
  gap: 8px;
}

.aigc-preview-placeholder svg {
  width: 32px;
  height: 32px;
  opacity: 0.8;
}

.aigc-preview-placeholder span {
  font-size: 13px;
  font-weight: 600;
}

/* 生成按钮 */
.aigc-generate-btn {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 14px 32px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 50px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
}

.aigc-generate-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 12px 32px rgba(102, 126, 234, 0.4);
}

.aigc-generate-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.aigc-generate-btn svg {
  width: 20px;
  height: 20px;
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.generating-tip {
  margin-top: 12px;
  font-size: 14px;
  color: #667eea;
  font-style: italic;
}

@media (max-width: 640px) {
  .aigc-animation-section {
    padding: 24px;
  }
  
  .aigc-preview-grid {
    flex-direction: column;
    gap: 12px;
  }
  
  .aigc-arrow {
    transform: rotate(90deg);
  }
  
  .aigc-generate-btn {
    width: 100%;
    justify-content: center;
  }
}

@media (max-width: 640px) {
  .page-content {
    padding: 80px 16px 40px;
  }
  
  .hero-image-wrapper {
    height: 280px;
  }
  
  .hero-content,
  .title-section,
  .metadata-pills,
  .content-section {
    padding: 24px;
  }
  
  .diary-title {
    font-size: 24px;
  }
  
  .metadata-pills {
    gap: 8px;
  }
  
  .pill {
    padding: 8px 12px;
    font-size: 12px;
  }
  
  .gallery-grid {
    grid-template-columns: 1fr;
  }
  
  .gallery-item.large {
    grid-column: span 1;
  }
  
  .timeline-item-body {
    flex-direction: column;
    gap: 12px;
  }
  
  .timeline-item-image {
    width: 100%;
    height: 160px;
  }
  
  .video-section {
    padding: 0 24px 24px;
  }
  
  .video-player {
    max-height: 300px;
  }
}
</style>
