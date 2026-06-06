<template>
  <div class="spot-page">
    <!-- 顶部迷你导航栏（滚动后显示） -->
    <header class="mini-header" :class="{ visible: showMiniHeader }">
      <button class="icon-btn back-icon" @click="goBack">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <polyline points="15 18 9 12 15 6"></polyline>
        </svg>
      </button>
      <h1 class="mini-title">{{ spot.name }}</h1>
      <button class="icon-btn share-icon" @click="handleShare">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"></path>
          <polyline points="16 6 12 2 8 6"></polyline>
          <line x1="12" y1="2" x2="12" y2="15"></line>
        </svg>
      </button>
    </header>

    <!-- 大屏布局容器 -->
    <div class="desktop-layout">
      <!-- 左侧：大图区域（大屏固定） -->
      <aside class="left-panel">
        <!-- 返回按钮 -->
        <button class="floating-back-btn" @click="goBack">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <polyline points="15 18 9 12 15 6"></polyline>
          </svg>
        </button>

        <!-- ① 沉浸式 Hero 图集 -->
        <section class="spot-hero">
          <div class="hero-slider" ref="heroSlider" @touchstart="handleTouchStart" @touchend="handleTouchEnd">
            <div
              class="hero-track"
              :style="{ transform: `translateX(-${currentImageIndex * 100}%)` }"
            >
              <div
                v-for="(img, idx) in spotImages"
                :key="idx"
                class="hero-slide"
                @click="openLightbox(idx)"
              >
                <img :src="getFullImageUrl(img)" :alt="spot.name" class="hero-image" />
              </div>
            </div>
          </div>
          <div class="hero-overlay"></div>

          <!-- 图片指示器 -->
          <div class="hero-dots" v-if="spotImages.length > 1">
            <span
              v-for="(_, idx) in spotImages"
              :key="idx"
              class="dot"
              :class="{ active: currentImageIndex === idx }"
              @click="goToSlide(idx)"
            ></span>
          </div>

          <!-- 图片计数器 -->
          <div class="image-counter" v-if="spotImages.length > 1">
            {{ currentImageIndex + 1 }} / {{ spotImages.length }}
          </div>

          <!-- Hero 底部信息叠加 -->
          <div class="hero-info">
            <div class="hero-info-left">
              <h2 class="hero-name">{{ spot.name }}</h2>
              <div class="hero-city">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
                  <circle cx="12" cy="10" r="3"></circle>
                </svg>
                {{ spot.city }}
              </div>
            </div>
            <div class="hero-info-right" v-if="spot.rating > 0">
              <div class="hero-rating">
                <span class="hero-star">★</span>
                <span class="hero-score">{{ spot.rating.toFixed(1) }}</span>
              </div>
              <div class="hero-favorites">
                <span class="hero-heart">♥</span>
                {{ formatNumber(spot.favorites_count || 0) }}
              </div>
            </div>
          </div>
        </section>
      </aside>

      <!-- 右侧：内容区域（大屏可滚动） -->
      <main class="right-panel" ref="rightPanel">
        <!-- ② 快捷操作栏 -->
        <section class="action-bar">
          <button class="action-item" :class="{ active: isCollected }" @click="toggleCollect">
            <span class="action-icon">{{ isCollected ? '❤️' : '🤍' }}</span>
            <span class="action-label">{{ isCollected ? '已收藏' : '收藏' }}</span>
          </button>
          <button class="action-item" @click="handleShare">
            <span class="action-icon">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"></path>
                <polyline points="16 6 12 2 8 6"></polyline>
                <line x1="12" y1="2" x2="12" y2="15"></line>
              </svg>
            </span>
            <span class="action-label">分享</span>
          </button>
          <button class="action-item" v-if="hasInternalMap" @click="goInternalNav">
            <span class="action-icon">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polygon points="1 6 1 22 8 18 16 22 21 18 21 2 16 6 8 2 1 6"></polygon>
                <line x1="8" y1="2" x2="8" y2="18"></line>
                <line x1="16" y1="6" x2="16" y2="22"></line>
              </svg>
            </span>
            <span class="action-label">导航</span>
          </button>
          <button class="action-item tour-guide-btn" @click="openTourGuide">
            <span class="action-icon">🎧</span>
            <span class="action-label">AI导游</span>
          </button>
        </section>

        <!-- ③ 核心信息卡片 -->
        <section class="info-card">
          <!-- 标签云 -->
          <div class="tags-scroll" v-if="filteredTags.length > 0">
            <span v-for="tag in filteredTags" :key="tag" class="tag">{{ tag }}</span>
          </div>

          <!-- 简介 -->
          <div class="desc-wrapper">
            <p class="spot-desc" :class="{ expanded: descExpanded }">{{ spot.description || '暂无描述' }}</p>
            <button v-if="showExpandBtn" class="expand-btn" @click="descExpanded = !descExpanded">
              {{ descExpanded ? '收起' : '展开全部' }}
            </button>
          </div>

          <!-- 信息网格 -->
          <div class="info-grid">
            <div class="info-item">
              <div class="info-icon">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"></circle>
                  <polyline points="12 6 12 12 16 14"></polyline>
                </svg>
              </div>
              <div class="info-content">
                <span class="info-label">开放时间</span>
                <span class="info-value">{{ spot.open_time || '全天开放' }}</span>
              </div>
            </div>
            <div class="info-item">
              <div class="info-icon">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="2" y="6" width="20" height="12" rx="2"></rect>
                  <circle cx="12" cy="12" r="2"></circle>
                  <path d="M6 12h.01M18 12h.01"></path>
                </svg>
              </div>
              <div class="info-content">
                <span class="info-label">门票</span>
                <span class="info-value">{{ spot.ticket_price || '免费' }}</span>
              </div>
            </div>
            <div class="info-item">
              <div class="info-icon">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
                </svg>
              </div>
              <div class="info-content">
                <span class="info-label">建议时长</span>
                <span class="info-value">{{ spot.suggested_duration || '2-3小时' }}</span>
              </div>
            </div>
            <div class="info-item">
              <div class="info-icon">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                  <circle cx="9" cy="7" r="4"></circle>
                  <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
                  <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
                </svg>
              </div>
              <div class="info-content">
                <span class="info-label">最佳季节</span>
                <span class="info-value">{{ spot.best_season || '四季皆宜' }}</span>
              </div>
            </div>
          </div>
        </section>

        <!-- ④ 地图位置区域（仅内部导航景点显示） -->
        <section class="map-section" v-if="hasInternalMap">
          <div class="section-title-bar">
            <div class="title-accent"></div>
            <h3>位置信息</h3>
          </div>
          <div class="map-container-wrapper">
            <div ref="miniMap" class="mini-map"></div>
            <button class="map-nav-btn" @click="goInternalNav">
              <span class="map-nav-icon">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polygon points="3 11 22 2 13 21 11 13 3 11"></polygon>
                </svg>
              </span>
              <span>{{ internalNavTitle }}</span>
            </button>
          </div>
        </section>

        <!-- ⑤ 拍照点位画廊（横向滚动） -->
        <section class="photo-section">
          <div class="section-title-bar">
            <div class="title-accent"></div>
            <h3>拍照点位</h3>
            <span class="photo-count">{{ photoSpots.length }}个</span>
            <button class="add-photo-btn" @click="showAddPhoto = true" v-if="userId">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <line x1="12" y1="5" x2="12" y2="19"></line>
                <line x1="5" y1="12" x2="19" y2="12"></line>
              </svg>
              上传
            </button>
          </div>
          <div class="photo-scroll" v-if="photoSpots.length > 0">
            <div
              v-for="ps in photoSpots"
              :key="ps.id"
              class="photo-card"
              @click="openPhotoLightbox(ps)"
            >
              <div class="photo-image-wrapper">
                <img :src="getFullImageUrl(ps.image)" :alt="ps.name" />
              </div>
              <div class="photo-card-info">
                <h4>{{ ps.name }}</h4>
                <p>{{ ps.description }}</p>
              </div>
            </div>
          </div>
          <div v-else class="empty-photo-spots">
            <p>暂无拍照点位，快来上传第一个吧！</p>
            <button class="empty-action-btn" @click="showAddPhoto = true" v-if="userId">上传拍照点位</button>
          </div>
        </section>

        <!-- ⑥ 评价区域 -->
        <section class="reviews-section">
          <div class="section-title-bar">
            <div class="title-accent"></div>
            <h3>用户评价</h3>
            <span class="review-count">{{ reviews.length }}条</span>
            <button class="add-review-btn" @click="showAddReview = true" v-if="!hasReviewed && userId">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <line x1="12" y1="5" x2="12" y2="19"></line>
                <line x1="5" y1="12" x2="19" y2="12"></line>
              </svg>
              写评价
            </button>
          </div>

          <!-- 评分统计 -->
          <div class="rating-stats" v-if="reviews.length > 0">
            <div class="rating-big">
              <span class="rating-number">{{ spot.rating?.toFixed(1) || '0.0' }}</span>
              <div class="rating-stars">
                <span v-for="i in 5" :key="i" :class="['star', { filled: i <= Math.round(spot.rating || 0) }]">★</span>
              </div>
            </div>
            <div class="rating-bars">
              <div v-for="n in 5" :key="n" class="rating-bar-row">
                <span class="bar-label">{{ 6 - n }}星</span>
                <div class="bar-track">
                  <div class="bar-fill" :style="{ width: getRatingPercent(6 - n) + '%' }"></div>
                </div>
                <span class="bar-count">{{ getRatingCount(6 - n) }}</span>
              </div>
            </div>
          </div>

          <!-- 评价列表 -->
          <div class="reviews-list" v-if="reviews.length > 0">
            <div v-for="review in reviews" :key="review.id" class="review-card">
              <div class="review-header">
                <div class="review-avatar">{{ review.username?.[0] || '用' }}</div>
                <div class="review-meta">
                  <span class="review-user">{{ review.username || '用户' }}</span>
                  <div class="review-rating">
                    <span v-for="i in 5" :key="i" :class="['star', { filled: i <= review.rating }]">★</span>
                  </div>
                </div>
                <div class="review-right">
                  <span class="review-date">{{ formatDate(review.created_at) }}</span>
                  <button
                    v-if="review.user_id == userId"
                    class="delete-review-btn"
                    @click="deleteReview(review.id)"
                  >
                    删除
                  </button>
                </div>
              </div>
              <p class="review-content">{{ review.content }}</p>
              <div class="review-images-scroll" v-if="review.images?.length">
                <img v-for="(img, idx) in review.images" :key="idx" :src="getFullImageUrl(img)" @click="openLightboxFromReview(review.images, idx)" />
              </div>
            </div>
          </div>

          <!-- 空状态 -->
          <div v-else class="empty-reviews">
            <div class="empty-icon">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
              </svg>
            </div>
            <p>暂无评价，快来发表第一条评价吧！</p>
            <button class="empty-action-btn" @click="showAddReview = true" v-if="userId">写评价</button>
          </div>
        </section>

        <!-- 底部安全区 -->
        <div class="bottom-safe-area"></div>
      </main>
    </div>

    <!-- 上传拍照点位弹窗 -->
    <div v-if="showAddPhoto" class="modal-overlay" @click.self="showAddPhoto = false">
      <div class="modal-content">
        <h3>上传拍照点位</h3>
        <input type="text" class="tech-input" placeholder="点位名称" v-model="newPhoto.name" />
        <textarea class="tech-input" placeholder="点位描述" v-model="newPhoto.description" rows="3"></textarea>
        <div class="file-input-wrapper">
          <input type="file" class="file-input" @change="handlePhotoUpload" accept="image/*" id="photo-upload" />
          <label for="photo-upload" class="file-label">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
              <polyline points="17 8 12 3 7 8"></polyline>
              <line x1="12" y1="3" x2="12" y2="15"></line>
            </svg>
            {{ photoFile ? photoFile.name : '选择图片' }}
          </label>
        </div>
        <div v-if="newPhoto.image" class="photo-preview">
          <img :src="newPhoto.image" alt="预览" />
        </div>
        <div class="modal-actions">
          <button class="btn-cancel" @click="showAddPhoto = false">取消</button>
          <button class="btn-confirm" @click="submitPhoto" :disabled="!newPhoto.name || !photoFile">提交</button>
        </div>
      </div>
    </div>

    <!-- 写评价弹窗 -->
    <div v-if="showAddReview" class="modal-overlay" @click.self="showAddReview = false">
      <div class="modal-content">
        <h3>写评价</h3>
        <div class="rating-input">
          <span class="rating-label">评分：</span>
          <div class="star-input">
            <span
              v-for="i in 5"
              :key="i"
              :class="['star', { filled: i <= newReview.rating }]"
              @click="newReview.rating = i"
            >★</span>
          </div>
          <span class="rating-text">{{ newReview.rating }}分</span>
        </div>
        <textarea class="tech-input" placeholder="分享您的游玩体验..." v-model="newReview.content" rows="4"></textarea>
        <div class="modal-actions">
          <button class="btn-cancel" @click="showAddReview = false">取消</button>
          <button class="btn-confirm" @click="submitReview" :disabled="newReview.rating === 0">提交</button>
        </div>
      </div>
    </div>

    <!-- 图片 Lightbox -->
    <div v-if="lightboxOpen" class="lightbox-overlay" @click.self="closeLightbox">
      <button class="lightbox-close" @click="closeLightbox">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <line x1="18" y1="6" x2="6" y2="18"></line>
          <line x1="6" y1="6" x2="18" y2="18"></line>
        </svg>
      </button>
      <button class="lightbox-nav prev" v-if="lightboxImages.length > 1" @click="prevLightboxImage">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <polyline points="15 18 9 12 15 6"></polyline>
        </svg>
      </button>
      <img :src="getFullImageUrl(lightboxImages[lightboxIndex])" class="lightbox-image" />
      <button class="lightbox-nav next" v-if="lightboxImages.length > 1" @click="nextLightboxImage">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <polyline points="9 18 15 12 9 6"></polyline>
        </svg>
      </button>
      <div class="lightbox-counter" v-if="lightboxImages.length > 1">
        {{ lightboxIndex + 1 }} / {{ lightboxImages.length }}
      </div>
    </div>

    <!-- 分享提示 -->
    <div v-if="showShareTip" class="share-toast">链接已复制到剪贴板</div>

    <!-- AI语音导游面板 -->
    <div v-if="showTourGuide" class="tour-guide-panel" :class="{ loading: tourGuideLoading }">
      <div class="tg-header">
        <div class="tg-title-row">
          <span class="tg-icon">🎧</span>
          <span class="tg-title">AI语音导游 · {{ spot.name }}</span>
        </div>
        <button class="tg-close" @click="closeTourGuide">✕</button>
      </div>

      <!-- 风格选择 -->
      <div class="tg-styles">
        <button
          v-for="s in tourGuideStyles"
          :key="s.key"
          class="tg-style-btn"
          :class="{ active: tourGuideStyle === s.key }"
          :disabled="tourGuideLoading"
          @click="switchTourStyle(s.key)"
        >
          <span class="style-emoji">{{ s.emoji }}</span>
          <span>{{ s.label }}</span>
        </button>
      </div>

      <!-- 加载状态 -->
      <div v-if="tourGuideLoading" class="tg-loading">
        <div class="tg-spinner"></div>
        <p>AI正在生成导游词...</p>
      </div>

      <!-- 导游内容 -->
      <div v-else-if="tourGuideText" class="tg-content">
        <!-- 音频播放器 -->
        <div v-if="tourGuideAudio" class="tg-player">
          <button class="tg-play-btn" :class="{ playing: isPlaying }" @click="toggleAudio">
            <span>{{ isPlaying ? '⏸' : '▶' }}</span>
          </button>
          <div class="tg-progress-bar" @click="seekAudio">
            <div class="tg-progress-fill" :style="{ width: audioProgress + '%' }"></div>
          </div>
          <span class="tg-time">{{ formatAudioTime(audioCurrentTime) }} / {{ formatAudioTime(audioDuration) }}</span>
        </div>
        <div v-else class="tg-no-audio">
          <span>🔇</span> 语音合成暂不可用，以下是文字版导游词
        </div>

        <!-- 导游词文本 -->
        <div class="tg-text">{{ tourGuideText }}</div>

        <button class="tg-generate-btn tg-regenerate-btn" @click="generateTourGuide">
          <span>🔄</span>
          <span>重新生成</span>
        </button>
      </div>

      <!-- 空状态 -->
      <div v-else class="tg-empty">
        <p>选择上方风格后，点击下方按钮生成导游词</p>
        <button class="tg-generate-btn" @click="generateTourGuide">
          <span>🎙️</span>
          <span>生成导游词</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()

const spot = ref({})
const reviews = ref([])
const photoSpots = ref([])
const showAddReview = ref(false)
const showAddPhoto = ref(false)
const isCollected = ref(false)
const hasReviewed = ref(false)
const hasInternalMap = ref(false)
const userId = computed(() => localStorage.getItem('userId'))
const internalNavTitle = computed(() => spot.value?.type === 'campus' ? '校园内导航' : '景区内部导航')

// Hero 图片轮播
const currentImageIndex = ref(0)
const spotImages = computed(() => {
  if (spot.value.images && spot.value.images.length > 0) return spot.value.images
  if (spot.value.image) return [spot.value.image]
  return [defaultImage]
})

// 触摸滑动
let touchStartX = 0
const handleTouchStart = (e) => {
  touchStartX = e.touches[0].clientX
}
const handleTouchEnd = (e) => {
  stopAutoPlay()
  const diff = touchStartX - e.changedTouches[0].clientX
  if (Math.abs(diff) > 30) {
    if (diff > 0 && currentImageIndex.value < spotImages.value.length - 1) {
      currentImageIndex.value++
    } else if (diff < 0 && currentImageIndex.value > 0) {
      currentImageIndex.value--
    }
  }
  startAutoPlay()
}

// 自动轮播
let autoPlayTimer = null
const startAutoPlay = () => {
  stopAutoPlay()
  if (spotImages.value.length > 1) {
    autoPlayTimer = setInterval(() => {
      currentImageIndex.value = (currentImageIndex.value + 1) % spotImages.value.length
    }, 3000)
  }
}
const stopAutoPlay = () => {
  if (autoPlayTimer) {
    clearInterval(autoPlayTimer)
    autoPlayTimer = null
  }
}

const goToSlide = (idx) => {
  stopAutoPlay()
  currentImageIndex.value = idx
  startAutoPlay()
}

// 简介展开
const descExpanded = ref(false)
const showExpandBtn = ref(false)

// 滚动迷你导航栏
const showMiniHeader = ref(false)

// Lightbox
const lightboxOpen = ref(false)
const lightboxImages = ref([])
const lightboxIndex = ref(0)

// 分享
const showShareTip = ref(false)

// AI语音导游
const showTourGuide = ref(false)
const tourGuideLoading = ref(false)
const tourGuideStyle = ref('rational')
const tourGuideText = ref('')
const tourGuideAudio = ref(null)
const isPlaying = ref(false)
let audioContext = null
let audioElement = null
const audioProgress = ref(0)
const audioCurrentTime = ref(0)
const audioDuration = ref(0)
let audioTimer = null

const tourGuideStyles = [
  { key: 'rational', label: '理性派', emoji: '📐', voice: '小何2.0' },
  { key: 'emotional', label: '感性派', emoji: '📖', voice: '娇喘女声' },
  { key: 'foodie', label: '吃货派', emoji: '🍜', voice: '猪八戒' }
]

// 高德地图
const miniMap = ref(null)
let mapInstance = null

// 允许的tag列表
const ALLOWED_TAGS = [
  '必玩景点',
  '历史文化',
  '地标建筑',
  '非遗体验',
  '风景名胜',
  '逛吃逛喝',
  '博物展览',
  'citywalk',
  '拍照出片',
  '市井烟火',
  '休闲娱乐'
]

// 过滤后的tags
const filteredTags = computed(() => {
  if (!spot.value.tags || !Array.isArray(spot.value.tags)) return []
  return spot.value.tags.filter(tag => ALLOWED_TAGS.includes(tag))
})

const newReview = ref({ rating: 0, content: '' })
const newPhoto = ref({ name: '', description: '', image: '' })
const photoFile = ref(null)
const defaultImage = 'https://images.unsplash.com/photo-1599571234909-29ed5d1321d6?w=800'
const API_BASE_URL = 'http://localhost:8000'

// 获取完整图片URL
const getFullImageUrl = (url) => {
  if (!url) return ''
  if (url.startsWith('http')) return url
  return `${API_BASE_URL}${url}`
}

onMounted(async () => {
  const spotId = route.query.id
  if (spotId) {
    await loadSpot(spotId)
    await loadReviews(spotId)
    await checkIfReviewed(spotId)
    await loadPhotoSpots(spotId)
    await checkInternalMap(spotId)

    // 检查简介是否需要展开按钮
    nextTick(() => {
      const descEl = document.querySelector('.spot-desc')
      if (descEl && descEl.scrollHeight > descEl.clientHeight) {
        showExpandBtn.value = true
      }
    })

    // 启动自动轮播
    nextTick(() => {
      startAutoPlay()
    })

    // 滚动监听
    window.addEventListener('scroll', handleScroll)
  }
})

onUnmounted(() => {
  stopAutoPlay()
  window.removeEventListener('scroll', handleScroll)
})

const handleScroll = () => {
  showMiniHeader.value = window.scrollY > 300
}

const loadSpot = async (id) => {
  try {
    const response = await fetch(`http://localhost:8000/api/spots/${id}`)
    const data = await response.json()
    spot.value = {
      ...data,
      image: data.images?.[0] || defaultImage,
      rating: data.rating || 0,
      favorites_count: data.favorites_count || 0
    }

    // 检查是否已收藏
    if (userId.value) {
      const checkRes = await fetch(`http://localhost:8000/api/collections/check/${id}?user_id=${userId.value}`)
      if (checkRes.ok) {
        const checkData = await checkRes.json()
        isCollected.value = checkData.is_collected
      }
    }
  } catch (error) {
    console.error('加载景点失败:', error)
    spot.value = {
      id: id,
      name: '景点详情',
      city: route.query.city || '北京',
      rating: 0,
      favorites_count: 0,
      description: '景点描述加载中...',
      tags: ['必玩景点'],
      open_time: '08:00-18:00',
      ticket_price: '¥60'
    }
  }
}

const loadReviews = async (spotId) => {
  try {
    const response = await fetch(`http://localhost:8000/api/collections/spot-reviews/${spotId}`)
    if (response.ok) {
      const data = await response.json()
      reviews.value = data
    }
  } catch (error) {
    console.error('加载评价失败:', error)
    reviews.value = []
  }
}

const checkIfReviewed = async (spotId) => {
  if (!userId.value) return
  try {
    const response = await fetch(`http://localhost:8000/api/collections/spot-reviews/check/${spotId}?user_id=${userId.value}`)
    if (response.ok) {
      const data = await response.json()
      hasReviewed.value = data.has_reviewed
    }
  } catch (error) {
    console.error('检查评价状态失败:', error)
  }
}

const loadPhotoSpots = async (spotId) => {
  try {
    const response = await fetch(`http://localhost:8000/api/photo-spots/${spotId}`)
    if (response.ok) {
      const data = await response.json()
      photoSpots.value = data
    }
  } catch (error) {
    console.error('加载拍照点位失败:', error)
    photoSpots.value = []
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}

const formatNumber = (num) => {
  if (num >= 10000) return (num / 10000).toFixed(1) + 'w'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'k'
  return num.toString()
}

const goBack = () => router.back()

const checkInternalMap = async (spotId) => {
  try {
    const res = await fetch(`http://localhost:8000/api/route/nodes/${spotId}`)
    if (res.ok) {
      const data = await res.json()
      hasInternalMap.value = (data.nodes || []).length > 0

      // 如果有内部地图，初始化高德地图
      if (hasInternalMap.value) {
        nextTick(() => {
          initMiniMap()
        })
      }
    }
  } catch {
    hasInternalMap.value = false
  }
}

const initMiniMap = async () => {
  if (!miniMap.value) return
  try {
    const AMapLoader = (await import('@amap/amap-jsapi-loader')).default
    const AMAP_KEY = import.meta.env.VITE_AMAP_KEY || ''
    const AMAP_SECURITY_KEY = import.meta.env.VITE_AMAP_SECURITY_KEY || ''

    if (AMAP_SECURITY_KEY) {
      window._AMapSecurityConfig = { securityJsCode: AMAP_SECURITY_KEY }
    }

    const AMap = await AMapLoader.load({
      key: AMAP_KEY,
      version: '2.0',
      plugins: ['AMap.Marker', 'AMap.Scale']
    })

    // 使用景点坐标或默认北京
    const center = spot.value.longitude && spot.value.latitude
      ? [spot.value.longitude, spot.value.latitude]
      : [116.397428, 39.90923]

    mapInstance = new AMap.Map(miniMap.value, {
      zoom: 14,
      center: center,
      viewMode: '2D'
    })

    // 添加标记
    new AMap.Marker({
      position: center,
      title: spot.value.name || '景点位置'
    }).setMap(mapInstance)
  } catch (error) {
    console.error('迷你地图初始化失败:', error)
  }
}

const goInternalNav = () => {
  router.push({ path: '/internal-nav', query: { id: spot.value.id } })
}

const toggleCollect = async () => {
  if (!userId.value) {
    router.push('/login')
    return
  }

  try {
    if (isCollected.value) {
      const response = await fetch(`http://localhost:8000/api/collections/${spot.value.id}?user_id=${userId.value}`, {
        method: 'DELETE'
      })
      if (response.ok) {
        isCollected.value = false
        spot.value.favorites_count = Math.max(0, (spot.value.favorites_count || 0) - 1)
        ElMessage.success('已取消收藏')
      }
    } else {
      const response = await fetch(`http://localhost:8000/api/collections?user_id=${userId.value}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ spot_id: spot.value.id })
      })
      if (response.ok) {
        isCollected.value = true
        spot.value.favorites_count = (spot.value.favorites_count || 0) + 1
        ElMessage.success('收藏成功')
      }
    }
  } catch (error) {
    console.error('操作失败:', error)
    ElMessage.error('操作失败')
  }
}

const handleShare = () => {
  const url = window.location.href
  navigator.clipboard?.writeText(url).then(() => {
    showShareTip.value = true
    setTimeout(() => showShareTip.value = false, 2000)
  }).catch(() => {
    ElMessage.info('分享链接: ' + url)
  })
}

// Lightbox 操作
const openLightbox = (index) => {
  lightboxImages.value = spotImages.value
  lightboxIndex.value = index
  lightboxOpen.value = true
  document.body.style.overflow = 'hidden'
}

const openPhotoLightbox = (ps) => {
  lightboxImages.value = [getFullImageUrl(ps.image)]
  lightboxIndex.value = 0
  lightboxOpen.value = true
  document.body.style.overflow = 'hidden'
}

const openLightboxFromReview = (images, index) => {
  lightboxImages.value = images
  lightboxIndex.value = index
  lightboxOpen.value = true
  document.body.style.overflow = 'hidden'
}

const closeLightbox = () => {
  lightboxOpen.value = false
  document.body.style.overflow = ''
}

const prevLightboxImage = () => {
  if (lightboxIndex.value > 0) lightboxIndex.value--
}

const nextLightboxImage = () => {
  if (lightboxIndex.value < lightboxImages.value.length - 1) lightboxIndex.value++
}

// 评分统计
const getRatingCount = (star) => {
  return reviews.value.filter(r => r.rating === star).length
}

const getRatingPercent = (star) => {
  if (reviews.value.length === 0) return 0
  return (getRatingCount(star) / reviews.value.length) * 100
}

const submitReview = async () => {
  if (!userId.value) {
    router.push('/login')
    return
  }

  if (newReview.value.rating === 0) {
    ElMessage.warning('请选择评分')
    return
  }

  try {
    const response = await fetch(`http://localhost:8000/api/collections/spot-reviews?user_id=${userId.value}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        spot_id: spot.value.id,
        rating: newReview.value.rating,
        content: newReview.value.content
      })
    })

    if (response.ok) {
      const data = await response.json()
      reviews.value.unshift(data)
      hasReviewed.value = true
      showAddReview.value = false
      newReview.value = { rating: 0, content: '' }

      spot.value.rating = data.new_rating || spot.value.rating
      spot.value.review_count = (spot.value.review_count || 0) + 1

      ElMessage.success('评价提交成功')
      await loadReviews(spot.value.id)
    } else {
      const error = await response.json()
      ElMessage.error(error.detail || '评价失败')
    }
  } catch (error) {
    console.error('提交评价失败:', error)
    ElMessage.error('提交失败')
  }
}

const deleteReview = async (reviewId) => {
  if (!confirm('确定要删除这条评价吗？')) return

  try {
    const url = `http://localhost:8000/api/collections/reviews/delete/${reviewId}?user_id=${userId.value}`
    const response = await fetch(url, { method: 'DELETE' })

    if (response.ok) {
      ElMessage.success('评价已删除')
      await loadReviews(spot.value.id)
      hasReviewed.value = false
      await loadSpot(spot.value.id)
    } else {
      const errorText = await response.text()
      try {
        const error = JSON.parse(errorText)
        ElMessage.error(error.detail || '删除失败')
      } catch {
        ElMessage.error(`删除失败: ${response.status}`)
      }
    }
  } catch (error) {
    console.error('删除评价异常:', error)
    ElMessage.error('删除失败')
  }
}

const handlePhotoUpload = (e) => {
  const file = e.target.files[0]
  if (file) {
    photoFile.value = file
    newPhoto.value.image = URL.createObjectURL(file)
  }
}

const submitPhoto = async () => {
  if (!userId.value) {
    router.push('/login')
    return
  }

  if (newPhoto.value.name && photoFile.value) {
    try {
      const formData = new FormData()
      formData.append('spot_id', spot.value.id)
      formData.append('name', newPhoto.value.name)
      formData.append('description', newPhoto.value.description || '')
      formData.append('image', photoFile.value)

      const response = await fetch(`http://localhost:8000/api/photo-spots/?user_id=${userId.value}`, {
        method: 'POST',
        body: formData
      })

      if (response.ok) {
        const data = await response.json()
        photoSpots.value.unshift(data)
        showAddPhoto.value = false
        newPhoto.value = { name: '', description: '', image: '' }
        photoFile.value = null
        ElMessage.success('拍照点位已上传！')
      } else {
        const error = await response.json()
        ElMessage.error(error.detail || '上传失败')
      }
    } catch (error) {
      console.error('上传拍照点位失败:', error)
      ElMessage.error('上传失败')
    }
  } else {
    ElMessage.warning('请填写名称并选择图片')
  }
}

// ==================== AI语音导游 ====================

const openTourGuide = () => {
  showTourGuide.value = true
  loadCachedGuides()
}

const closeTourGuide = () => {
  stopAudio()
  showTourGuide.value = false
}

const cachedGuides = ref({})  // { rational: {text, audio_base64}, ... }

const loadCachedGuides = async () => {
  const spotId = route.query.id
  if (!spotId) return
  try {
    const resp = await fetch(`http://localhost:8000/api/ai/tour-guide/${spotId}`)
    const data = await resp.json()
    if (data && Object.keys(data).length > 0) {
      cachedGuides.value = data
      const defaultStyle = tourGuideStyle.value
      if (data[defaultStyle]) {
        tourGuideText.value = data[defaultStyle].text
        loadAudioFromBase64(data[defaultStyle].audio_base64)
      }
    }
  } catch (e) {
    cachedGuides.value = {}
  }
}

const switchTourStyle = (style) => {
  tourGuideStyle.value = style
  stopAudio()
  destroyAudio()
  if (cachedGuides.value[style]) {
    tourGuideText.value = cachedGuides.value[style].text
    loadAudioFromBase64(cachedGuides.value[style].audio_base64)
  } else {
    tourGuideText.value = ''
    tourGuideAudio.value = null
  }
}

const loadAudioFromBase64 = (b64) => {
  if (!b64) {
    tourGuideAudio.value = null
    return
  }
  const binaryStr = atob(b64)
  const bytes = new Uint8Array(binaryStr.length)
  for (let i = 0; i < binaryStr.length; i++) {
    bytes[i] = binaryStr.charCodeAt(i)
  }
  tourGuideAudio.value = URL.createObjectURL(new Blob([bytes], { type: 'audio/mpeg' }))
}

const generateTourGuide = async () => {
  tourGuideLoading.value = true
  tourGuideText.value = ''
  tourGuideAudio.value = null
  stopAudio()

  try {
    const spotId = route.query.id
    const response = await fetch(`http://localhost:8000/api/ai/tour-guide`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ spot_id: parseInt(spotId), style: tourGuideStyle.value })
    })
    const data = await response.json()

    if (data.text) {
      tourGuideText.value = data.text
      cachedGuides.value[tourGuideStyle.value] = {
        text: data.text,
        audio_base64: data.audio_base64
      }
    }
    if (data.audio_base64) {
      loadAudioFromBase64(data.audio_base64)
    }
  } catch (error) {
    console.error('生成导游词失败:', error)
    tourGuideText.value = '生成失败，请稍后重试'
  } finally {
    tourGuideLoading.value = false
  }
}

const toggleAudio = () => {
  if (!tourGuideAudio.value) return
  if (isPlaying.value) {
    pauseAudio()
  } else {
    playAudio()
  }
}

const playAudio = () => {
  if (!tourGuideAudio.value) return
  if (!audioElement || audioElement.src !== tourGuideAudio.value) {
    destroyAudio()
    audioElement = new Audio(tourGuideAudio.value)
    audioElement.addEventListener('timeupdate', () => {
      audioCurrentTime.value = audioElement.currentTime
      audioDuration.value = audioElement.duration || 0
      if (audioElement.duration) {
        audioProgress.value = (audioElement.currentTime / audioElement.duration) * 100
      }
    })
    audioElement.addEventListener('ended', () => {
      isPlaying.value = false
      audioProgress.value = 0
      audioCurrentTime.value = 0
    })
    audioElement.addEventListener('loadedmetadata', () => {
      audioDuration.value = audioElement.duration
    })
  }
  audioElement.play().catch(console.error)
  isPlaying.value = true
}

const destroyAudio = () => {
  if (audioElement) {
    audioElement.pause()
    audioElement.src = ''
    audioElement = null
  }
}

const pauseAudio = () => {
  if (audioElement) {
    audioElement.pause()
  }
  isPlaying.value = false
}

const stopAudio = () => {
  if (audioElement) {
    audioElement.pause()
    audioElement.currentTime = 0
  }
  isPlaying.value = false
  audioProgress.value = 0
  audioCurrentTime.value = 0
}

const seekAudio = (e) => {
  if (!audioElement || !audioElement.duration) return
  const rect = e.currentTarget.getBoundingClientRect()
  const ratio = (e.clientX - rect.left) / rect.width
  audioElement.currentTime = ratio * audioElement.duration
}

const formatAudioTime = (seconds) => {
  if (!seconds || isNaN(seconds)) return '0:00'
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  return `${m}:${s.toString().padStart(2, '0')}`
}
</script>

<style scoped>
.spot-page {
  min-height: 100vh;
  background: #0a0a1a;
  color: #fff;
  position: relative;
}

/* 大屏左右分栏布局 */
.desktop-layout {
  display: flex;
  min-height: 100vh;
}

.left-panel {
  flex: 0 0 55%;
  position: sticky;
  top: 0;
  height: 100vh;
  overflow: hidden;
}

.right-panel {
  flex: 1;
  min-width: 0;
  overflow-y: auto;
  padding: 24px 32px 0;
}

/* 左侧大图区域 */
.left-panel .spot-hero {
  height: 100vh;
  min-height: unset;
  max-height: unset;
}

.left-panel .hero-name {
  font-size: 36px;
}

.left-panel .hero-info {
  padding: 0 32px 32px;
}

.left-panel .hero-dots {
  bottom: 120px;
}

.left-panel .floating-back-btn {
  top: 24px;
  left: 24px;
}

/* 右侧内容区调整 */
.right-panel .action-bar {
  margin: 0 0 24px;
}

.right-panel .info-card {
  margin: 0 0 24px;
}

.right-panel .map-section {
  margin: 0 0 24px;
}

.right-panel .photo-section {
  margin: 0 0 24px;
}

.right-panel .photo-section .section-title-bar {
  padding: 0;
}

.right-panel .photo-scroll {
  padding: 0;
}

.right-panel .empty-photo-spots {
  margin: 0;
}

.right-panel .reviews-section {
  margin: 0 0 24px;
}

/* 迷你导航栏 */
.mini-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: rgba(10, 10, 26, 0.95);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(0, 212, 255, 0.1);
  z-index: 100;
  transform: translateY(-100%);
  transition: transform 0.3s ease;
}

.mini-header.visible {
  transform: translateY(0);
}

.mini-title {
  font-size: 17px;
  font-weight: 600;
  background: linear-gradient(135deg, #00d4ff, #fff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.icon-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 1px solid rgba(0, 212, 255, 0.3);
  background: rgba(0, 0, 0, 0.3);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s;
}

.icon-btn:hover {
  background: rgba(0, 212, 255, 0.15);
  border-color: rgba(0, 212, 255, 0.6);
}

/* 浮动返回按钮 */
.floating-back-btn {
  position: fixed;
  top: 16px;
  left: 16px;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(10px);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 50;
  transition: all 0.3s;
}

.floating-back-btn:hover {
  background: rgba(0, 212, 255, 0.2);
  border-color: rgba(0, 212, 255, 0.5);
}

/* Hero 区域 */
.spot-hero {
  position: relative;
  height: 45vh;
  min-height: 320px;
  max-height: 500px;
  overflow: hidden;
}

.hero-slider {
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.hero-track {
  display: flex;
  height: 100%;
  transition: transform 0.2s ease;
}

.hero-slide {
  flex: 0 0 100%;
  height: 100%;
  cursor: pointer;
}

.hero-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.hero-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to bottom, rgba(10, 10, 26, 0.1) 0%, rgba(10, 10, 26, 0.3) 50%, #0a0a1a 100%);
  pointer-events: none;
}

.hero-dots {
  position: absolute;
  bottom: 80px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 8px;
  z-index: 5;
}

.dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.4);
  cursor: pointer;
  transition: all 0.3s;
}

.dot.active {
  width: 20px;
  border-radius: 3px;
  background: #00d4ff;
}

.image-counter {
  position: absolute;
  top: 20px;
  right: 20px;
  padding: 4px 12px;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.8);
  z-index: 5;
}

/* Hero 底部信息 */
.hero-info {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 0 20px 20px;
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  z-index: 5;
}

.hero-name {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 6px;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
}

.hero-city {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
}

.hero-info-right {
  text-align: right;
}

.hero-rating {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-bottom: 4px;
}

.hero-star {
  color: #ffd700;
  font-size: 16px;
}

.hero-score {
  font-size: 20px;
  font-weight: 700;
  color: #ffd700;
}

.hero-favorites {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
}

.hero-heart {
  color: #ff6b6b;
  margin-right: 2px;
}

/* 快捷操作栏 */
.action-bar {
  display: flex;
  gap: 12px;
  padding: 16px 20px;
  margin: -24px 16px 0;
  background: rgba(20, 20, 40, 0.9);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  border: 1px solid rgba(0, 212, 255, 0.15);
  position: relative;
  z-index: 10;
}

.action-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 12px 8px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.03);
  color: #fff;
  cursor: pointer;
  transition: all 0.3s;
}

.action-item:hover {
  background: rgba(0, 212, 255, 0.1);
  border-color: rgba(0, 212, 255, 0.3);
}

.action-item.active {
  background: rgba(255, 107, 107, 0.1);
  border-color: rgba(255, 107, 107, 0.3);
  color: #ff6b6b;
}

.action-icon {
  font-size: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.action-icon svg {
  stroke: currentColor;
}

.action-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
}

.action-item.active .action-label {
  color: #ff6b6b;
}

/* 核心信息卡片 */
.info-card {
  margin: 24px 16px 0;
  padding: 24px;
  background: rgba(20, 20, 40, 0.6);
  border: 1px solid rgba(0, 212, 255, 0.1);
  border-radius: 20px;
  backdrop-filter: blur(10px);
}

.tags-scroll {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.tag {
  padding: 6px 14px;
  background: rgba(0, 212, 255, 0.08);
  border: 1px solid rgba(0, 212, 255, 0.2);
  border-radius: 20px;
  font-size: 13px;
  color: #00d4ff;
  transition: all 0.3s;
}

.tag:hover {
  background: rgba(0, 212, 255, 0.15);
  border-color: rgba(0, 212, 255, 0.4);
}

.desc-wrapper {
  margin-bottom: 20px;
}

.spot-desc {
  font-size: 15px;
  line-height: 1.7;
  color: rgba(255, 255, 255, 0.75);
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  transition: all 0.3s;
}

.spot-desc.expanded {
  -webkit-line-clamp: unset;
  display: block;
}

.expand-btn {
  margin-top: 8px;
  background: none;
  border: none;
  color: #00d4ff;
  font-size: 13px;
  cursor: pointer;
  padding: 0;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.info-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.info-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: rgba(0, 212, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #00d4ff;
  flex-shrink: 0;
}

.info-content {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.info-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

.info-value {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
}

/* 模块标题栏 */
.section-title-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
}

.title-accent {
  width: 4px;
  height: 20px;
  background: linear-gradient(to bottom, #00d4ff, #7b2cbf);
  border-radius: 2px;
}

.section-title-bar h3 {
  font-size: 18px;
  font-weight: 600;
  flex: 1;
}

.photo-count,
.review-count {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
}

/* 地图区域 */
.map-section {
  margin: 32px 16px 0;
}

.map-container-wrapper {
  position: relative;
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid rgba(0, 212, 255, 0.15);
}

.mini-map {
  width: 100%;
  height: 200px;
  background: #1a1a2e;
}

.map-nav-btn {
  position: absolute;
  bottom: 12px;
  right: 12px;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  background: rgba(10, 10, 26, 0.9);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(0, 212, 255, 0.3);
  border-radius: 20px;
  color: #00d4ff;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s;
}

.map-nav-btn:hover {
  background: rgba(0, 212, 255, 0.15);
}

/* 拍照点位 */
.photo-section {
  margin: 32px 0 0;
}

.photo-section .section-title-bar {
  padding: 0 16px;
}

.photo-scroll {
  display: flex;
  gap: 12px;
  padding: 0 16px;
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  scrollbar-width: none;
}

.photo-scroll::-webkit-scrollbar {
  display: none;
}

.photo-card {
  flex: 0 0 280px;
  scroll-snap-align: start;
  background: rgba(20, 20, 40, 0.6);
  border: 1px solid rgba(0, 212, 255, 0.1);
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s;
}

.photo-card:hover {
  border-color: rgba(0, 212, 255, 0.3);
  transform: translateY(-4px);
}

.photo-image-wrapper {
  width: 100%;
  aspect-ratio: 16 / 10;
  overflow: hidden;
}

.photo-image-wrapper img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.photo-card:hover .photo-image-wrapper img {
  transform: scale(1.05);
}

.photo-card-info {
  padding: 12px 14px;
}

.photo-card-info h4 {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 4px;
}

.photo-card-info p {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* 评价区域 */
.reviews-section {
  margin: 32px 16px 0;
}

.add-review-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 14px;
  background: rgba(0, 212, 255, 0.1);
  border: 1px solid rgba(0, 212, 255, 0.3);
  border-radius: 20px;
  color: #00d4ff;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s;
}

.add-review-btn:hover {
  background: rgba(0, 212, 255, 0.2);
}

.add-photo-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 14px;
  background: rgba(0, 212, 255, 0.1);
  border: 1px solid rgba(0, 212, 255, 0.3);
  border-radius: 20px;
  color: #00d4ff;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s;
}

.add-photo-btn:hover {
  background: rgba(0, 212, 255, 0.2);
}

.empty-photo-spots {
  text-align: center;
  padding: 40px 20px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  margin: 0 16px;
}

.empty-photo-spots p {
  color: rgba(255, 255, 255, 0.5);
  font-size: 14px;
  margin-bottom: 16px;
}

/* 评分统计 */
.rating-stats {
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 16px;
  margin-bottom: 20px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.rating-big {
  text-align: center;
  min-width: 80px;
}

.rating-number {
  font-size: 42px;
  font-weight: 700;
  color: #ffd700;
  line-height: 1;
}

.rating-stars {
  margin-top: 6px;
}

.rating-stars .star {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.2);
}

.rating-stars .star.filled {
  color: #ffd700;
}

.rating-bars {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.rating-bar-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.bar-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  width: 28px;
  text-align: right;
}

.bar-track {
  flex: 1;
  height: 4px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 2px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  background: linear-gradient(to right, #ffd700, #ffaa00);
  border-radius: 2px;
  transition: width 0.5s ease;
}

.bar-count {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
  width: 20px;
  text-align: left;
}

/* 评价卡片 */
.review-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 16px;
  padding: 18px;
  margin-bottom: 12px;
  transition: all 0.3s;
}

.review-card:hover {
  border-color: rgba(0, 212, 255, 0.15);
  background: rgba(255, 255, 255, 0.04);
}

.review-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.review-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 15px;
  flex-shrink: 0;
}

.review-meta {
  flex: 1;
  min-width: 0;
}

.review-user {
  font-size: 15px;
  font-weight: 500;
  display: block;
  margin-bottom: 2px;
}

.review-rating .star {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.2);
}

.review-rating .star.filled {
  color: #ffd700;
}

.review-right {
  text-align: right;
  flex-shrink: 0;
}

.review-date {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
  display: block;
  margin-bottom: 4px;
}

.delete-review-btn {
  background: none;
  border: 1px solid rgba(255, 107, 107, 0.4);
  color: #ff6b6b;
  padding: 3px 10px;
  border-radius: 8px;
  font-size: 11px;
  cursor: pointer;
  transition: all 0.3s;
}

.delete-review-btn:hover {
  background: rgba(255, 107, 107, 0.1);
}

.review-content {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.6;
  margin-bottom: 12px;
}

.review-images-scroll {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  scrollbar-width: none;
}

.review-images-scroll::-webkit-scrollbar {
  display: none;
}

.review-images-scroll img {
  width: 100px;
  height: 100px;
  object-fit: cover;
  border-radius: 10px;
  cursor: pointer;
  transition: transform 0.3s;
}

.review-images-scroll img:hover {
  transform: scale(1.05);
}

/* 空状态 */
.empty-reviews {
  text-align: center;
  padding: 48px 20px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.empty-icon {
  color: rgba(255, 255, 255, 0.2);
  margin-bottom: 12px;
}

.empty-reviews p {
  color: rgba(255, 255, 255, 0.5);
  font-size: 14px;
  margin-bottom: 16px;
}

.empty-action-btn {
  padding: 10px 28px;
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  border: none;
  border-radius: 20px;
  color: #fff;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.empty-action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
}

/* 底部安全区 */
.bottom-safe-area {
  height: 40px;
}

/* 弹窗 */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  background: #1a1a2e;
  border: 1px solid rgba(0, 212, 255, 0.2);
  border-radius: 20px;
  padding: 25px;
  width: 100%;
  max-width: 400px;
}

.modal-content h3 {
  margin-bottom: 20px;
  font-size: 18px;
}

.tech-input {
  width: 100%;
  padding: 12px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(0, 212, 255, 0.2);
  border-radius: 10px;
  color: #fff;
  margin-bottom: 15px;
  font-family: inherit;
}

.tech-input::placeholder {
  color: rgba(255, 255, 255, 0.3);
}

textarea.tech-input {
  min-height: 80px;
  resize: vertical;
}

.rating-input {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
}

.rating-label {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
}

.star-input {
  display: flex;
  gap: 5px;
}

.star-input .star {
  font-size: 24px;
  color: rgba(255, 255, 255, 0.2);
  cursor: pointer;
  transition: color 0.2s;
}

.star-input .star.filled {
  color: #ffd700;
}

.rating-text {
  font-size: 14px;
  color: #ffd700;
  margin-left: 10px;
}

.modal-actions {
  display: flex;
  gap: 15px;
  margin-top: 15px;
}

.btn-cancel, .btn-confirm {
  flex: 1;
  padding: 12px;
  border-radius: 10px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.btn-cancel {
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #fff;
}

.btn-cancel:hover {
  background: rgba(255, 255, 255, 0.05);
}

.btn-confirm {
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  border: none;
  color: #fff;
}

.btn-confirm:hover {
  transform: translateY(-1px);
  box-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
}

.btn-confirm:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

/* 文件上传 */
.file-input-wrapper {
  margin-bottom: 15px;
}

.file-input {
  display: none;
}

.file-label {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 14px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px dashed rgba(0, 212, 255, 0.3);
  border-radius: 10px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.file-label:hover {
  background: rgba(0, 212, 255, 0.05);
  border-color: rgba(0, 212, 255, 0.5);
}

.photo-preview {
  margin-bottom: 15px;
  border-radius: 10px;
  overflow: hidden;
  border: 1px solid rgba(0, 212, 255, 0.2);
}

.photo-preview img {
  width: 100%;
  max-height: 200px;
  object-fit: cover;
  display: block;
}

/* Lightbox */
.lightbox-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.95);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.lightbox-close {
  position: absolute;
  top: 20px;
  right: 20px;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: rgba(0, 0, 0, 0.5);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 10;
  transition: all 0.3s;
}

.lightbox-close:hover {
  background: rgba(255, 255, 255, 0.1);
}

.lightbox-image {
  max-width: 90vw;
  max-height: 85vh;
  object-fit: contain;
  border-radius: 8px;
}

.lightbox-nav {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 48px;
  height: 48px;
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: rgba(0, 0, 0, 0.5);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s;
  z-index: 10;
}

.lightbox-nav:hover {
  background: rgba(255, 255, 255, 0.1);
}

.lightbox-nav.prev {
  left: 16px;
}

.lightbox-nav.next {
  right: 16px;
}

.lightbox-counter {
  position: absolute;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  padding: 6px 16px;
  background: rgba(0, 0, 0, 0.6);
  border-radius: 12px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.8);
}

/* 分享提示 */
.share-toast {
  position: fixed;
  bottom: 40px;
  left: 50%;
  transform: translateX(-50%);
  padding: 12px 24px;
  background: rgba(20, 20, 40, 0.95);
  border: 1px solid rgba(0, 212, 255, 0.3);
  border-radius: 24px;
  color: #00d4ff;
  font-size: 14px;
  z-index: 3000;
  animation: toastIn 0.3s ease;
}

@keyframes toastIn {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}

/* 响应式 */
@media (max-width: 1023px) {
  .desktop-layout {
    display: block;
  }

  .left-panel {
    position: relative;
    height: auto;
    flex: none;
  }

  .left-panel .spot-hero {
    height: 45vh;
    min-height: 320px;
    max-height: 500px;
  }

  .left-panel .hero-name {
    font-size: 28px;
  }

  .left-panel .hero-info {
    padding: 0 20px 20px;
  }

  .left-panel .hero-dots {
    bottom: 80px;
  }

  .left-panel .floating-back-btn {
    top: 16px;
    left: 16px;
  }

  .right-panel {
    padding: 0;
    overflow-y: visible;
  }

  .right-panel .action-bar {
    margin: -24px 16px 0;
  }

  .right-panel .info-card {
    margin: 24px 16px 0;
  }

  .right-panel .map-section {
    margin: 32px 16px 0;
  }

  .right-panel .photo-section {
    margin: 32px 0 0;
  }

  .right-panel .photo-section .section-title-bar {
    padding: 0 16px;
  }

  .right-panel .photo-scroll {
    padding: 0 16px;
  }

  .right-panel .empty-photo-spots {
    margin: 0 16px;
  }

  .right-panel .reviews-section {
    margin: 32px 16px 0;
  }
}

@media (min-width: 1024px) and (max-width: 1439px) {
  .left-panel {
    flex: 0 0 50%;
  }
}

@media (min-width: 1440px) {
  .left-panel {
    flex: 0 0 55%;
  }
}

@media (max-width: 480px) {
  .info-grid {
    grid-template-columns: 1fr;
  }

  .hero-name {
    font-size: 24px;
  }

  .rating-stats {
    flex-direction: column;
    gap: 16px;
  }
}

/* ==================== AI语音导游面板 ==================== */
.tour-guide-panel {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  background: rgba(10, 10, 26, 0.97);
  backdrop-filter: blur(30px);
  border-top: 1px solid rgba(0, 212, 255, 0.2);
  border-radius: 20px 20px 0 0;
  padding: 20px 24px 30px;
  max-height: 55vh;
  overflow-y: auto;
  animation: tgSlideUp 0.35s ease;
  box-shadow: 0 -10px 50px rgba(0, 0, 0, 0.5);
}

@keyframes tgSlideUp {
  from { transform: translateY(100%); }
  to { transform: translateY(0); }
}

.tg-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.tg-title-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.tg-icon {
  font-size: 22px;
}

.tg-title {
  font-size: 17px;
  font-weight: 700;
  color: #fff;
}

.tg-close {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: rgba(255, 255, 255, 0.6);
  width: 32px;
  height: 32px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.tg-close:hover {
  background: rgba(255, 80, 80, 0.2);
  border-color: rgba(255, 80, 80, 0.5);
  color: #ff6b6b;
}

.tg-styles {
  display: flex;
  gap: 10px;
  margin-bottom: 18px;
}

.tg-style-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 10px 12px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(255, 255, 255, 0.04);
  color: rgba(255, 255, 255, 0.7);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s;
}

.tg-style-btn:hover {
  background: rgba(0, 212, 255, 0.08);
  border-color: rgba(0, 212, 255, 0.3);
}

.tg-style-btn.active {
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.2), rgba(123, 44, 191, 0.2));
  border-color: rgba(0, 212, 255, 0.5);
  color: #00d4ff;
  font-weight: 600;
}

.tg-style-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.style-emoji {
  font-size: 16px;
}

.tg-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 30px 0;
  gap: 14px;
}

.tg-spinner {
  width: 36px;
  height: 36px;
  border: 3px solid rgba(0, 212, 255, 0.15);
  border-top-color: #00d4ff;
  border-radius: 50%;
  animation: tgSpin 0.8s linear infinite;
}

@keyframes tgSpin {
  to { transform: rotate(360deg); }
}

.tg-loading p {
  color: rgba(255, 255, 255, 0.5);
  font-size: 14px;
}

.tg-content {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.tg-player {
  display: flex;
  align-items: center;
  gap: 12px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 14px;
  padding: 12px 16px;
}

.tg-play-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: none;
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  color: #fff;
  font-size: 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: transform 0.2s, box-shadow 0.2s;
}

.tg-play-btn:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 20px rgba(0, 212, 255, 0.4);
}

.tg-progress-bar {
  flex: 1;
  height: 5px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
  cursor: pointer;
  overflow: hidden;
}

.tg-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #00d4ff, #7b2cbf);
  border-radius: 3px;
  transition: width 0.1s linear;
}

.tg-time {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  font-variant-numeric: tabular-nums;
  flex-shrink: 0;
  min-width: 70px;
  text-align: right;
}

.tg-no-audio {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  border-radius: 10px;
  background: rgba(255, 180, 50, 0.08);
  border: 1px solid rgba(255, 180, 50, 0.2);
  color: rgba(255, 180, 50, 0.9);
  font-size: 13px;
}

.tg-text {
  font-size: 14px;
  line-height: 1.8;
  color: rgba(255, 255, 255, 0.85);
  white-space: pre-wrap;
  max-height: 200px;
  overflow-y: auto;
  padding-right: 4px;
}

.tg-text::-webkit-scrollbar {
  width: 3px;
}

.tg-text::-webkit-scrollbar-thumb {
  background: rgba(0, 212, 255, 0.3);
  border-radius: 3px;
}

.tg-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 24px 0;
  gap: 16px;
}

.tg-empty p {
  color: rgba(255, 255, 255, 0.35);
  font-size: 14px;
}

.tg-generate-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 32px;
  border-radius: 14px;
  border: none;
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.tg-generate-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 30px rgba(0, 212, 255, 0.5);
}

.tg-regenerate-btn {
  margin-top: 4px;
  align-self: center;
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.3), rgba(123, 44, 191, 0.3));
  border: 1px solid rgba(0, 212, 255, 0.3);
  font-size: 14px;
  padding: 10px 24px;
}
</style>
