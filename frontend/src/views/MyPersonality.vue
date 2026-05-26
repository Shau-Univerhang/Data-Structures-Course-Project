<template>
  <div class="my-personality-page">
    <Navbar />

    <div class="page-container">
      <!-- 未测试状态 -->
      <div v-if="!hasResult && !loading" class="empty-state">
        <div class="empty-icon">🫥</div>
        <h2>你的人格还是一片空白</h2>
        <p>20道灵魂拷问，测出你的真实旅行人格</p>
        <p class="empty-hint">是Excel成精还是风的方向盘？来，面对真实的自己</p>
        <button class="test-btn" @click="goTest">去测试</button>
      </div>

      <!-- 已测试状态 -->
      <div v-else-if="hasResult && result" class="result-display">
        <div class="result-header">
          <div class="character-wrapper" v-if="personaConfig">
            <PersonaSVG :config="personaConfig" />
          </div>
          <div class="result-code">{{ result.type_code }}</div>
          <h1 class="result-name">{{ result.name }}</h1>
          <p class="result-tagline">"{{ result.tagline }}"</p>
          <div class="result-style">{{ result.travel_style }}</div>
        </div>

        <div class="result-card">
          <div class="dimension-section">
            <h3>四维解析</h3>
            <div class="dimension-list">
              <div
                v-for="(dim, key) in result.dimension_scores"
                :key="key"
                class="dimension-item"
              >
                <div class="dim-info">
                  <span class="dim-name">{{ dim.name }}</span>
                  <span class="dim-tendency">{{ dim.tendency }}</span>
                </div>
                <div class="dim-bar-bg">
                  <div class="dim-bar-fill" :style="{ width: dim.strength + '%' }"></div>
                </div>
                <div class="dim-scale">
                  <span>{{ key === 'P' ? 'P人' : key === 'E' ? '咸鱼' : key === 'S' ? 'i人' : '貔貅' }}</span>
                  <span class="dim-score">{{ dim.score }}分</span>
                  <span>{{ key === 'P' ? 'J人' : key === 'E' ? '肝帝' : key === 'S' ? 'e人' : '蝗虫' }}</span>
                </div>
              </div>
            </div>
          </div>

          <div class="description-section">
            <h3>人格画像</h3>
            <p>{{ result.description }}</p>
          </div>

          <div class="traits-section">
            <div class="trait-box">
              <h4>天赋技能</h4>
              <div class="trait-list">
                <span v-for="(s, i) in result.strengths" :key="i" class="trait-pill good">{{ s }}</span>
              </div>
            </div>
            <div class="trait-box">
              <h4>弱点暴露</h4>
              <div class="trait-list">
                <span v-for="(w, i) in result.weaknesses" :key="i" class="trait-pill bad">{{ w }}</span>
              </div>
            </div>
          </div>

          <div class="spots-section">
            <h3>为你推荐的景点</h3>
            <div class="spots-list">
              <div
                v-for="(spot, i) in result.recommend_spots"
                :key="i"
                class="spot-item"
              >
                <span class="spot-icon">📍</span>
                <span class="spot-text">{{ spot }}</span>
              </div>
            </div>
          </div>

          <div class="actions">
            <button class="action-btn retest" @click="goTest">重新测试</button>
            <button class="action-btn share" @click="shareResult">分享结果</button>
          </div>
        </div>
      </div>

      <!-- 加载中 -->
      <div v-else class="loading-state">
        <div class="loading-spinner"></div>
        <p>加载中...</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import Navbar from '../components/Navbar.vue'
import PersonaSVG from '../components/personas/PersonaSVG.vue'
import { API } from '../api'
import { getPersonaById } from '../components/personas/config.js'

const router = useRouter()
const hasResult = ref(false)
const result = ref(null)
const loading = ref(true)

const personaConfig = computed(() => {
  if (!result.value?.type_code) return null
  return getPersonaById(result.value.type_code)
})

onMounted(async () => {
  await loadResult()
})

const loadResult = async () => {
  const userId = localStorage.getItem('userId')
  if (!userId) {
    loading.value = false
    return
  }

  try {
    const data = await API.personality.getMyResult(parseInt(userId))
    result.value = data
    hasResult.value = true
  } catch (e) {
    if (e.message && e.message.includes('404')) {
      hasResult.value = false
    } else {
      console.error('获取人格结果失败:', e)
    }
  } finally {
    loading.value = false
  }
}

const goTest = () => {
  router.push('/personality-test')
}

const shareResult = () => {
  if (!result.value) return

  const text = `我的TBTI旅行人格是【${result.value.name}】(${result.value.type_code})\n"${result.value.tagline}"\n快来测测你的旅行人格吧！`

  if (navigator.share) {
    navigator.share({
      title: 'TBTI 旅行人格测试',
      text: text,
      url: window.location.origin + '/personality-test'
    })
  } else {
    // 复制到剪贴板
    navigator.clipboard.writeText(text).then(() => {
      alert('结果已复制到剪贴板！')
    }).catch(() => {
      alert(text)
    })
  }
}
</script>

<style scoped>
.my-personality-page {
  min-height: 100vh;
  background: #0a0a1a;
  color: #fff;
  padding-top: 80px;
}

.page-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

/* 未测试状态 */
.empty-state {
  text-align: center;
  padding: 80px 20px;
  animation: fadeIn 0.6s ease;
}

.empty-icon {
  font-size: 80px;
  margin-bottom: 20px;
}

.empty-state h2 {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 12px;
}

.empty-state p {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 8px;
}

.empty-hint {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.4);
  margin-bottom: 40px;
}

.test-btn {
  padding: 16px 50px;
  font-size: 17px;
  font-weight: 600;
  border: none;
  border-radius: 50px;
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  color: #fff;
  cursor: pointer;
  transition: all 0.3s ease;
}

.test-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 30px rgba(0, 212, 255, 0.3);
}

/* 已测试状态 */
.result-display {
  animation: fadeIn 0.6s ease;
}

.result-header {
  text-align: center;
  padding: 40px 20px;
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.1), rgba(123, 44, 191, 0.1));
  border-radius: 24px;
  margin-bottom: 20px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.character-wrapper {
  margin-bottom: 16px;
  display: flex;
  justify-content: center;
}

.result-code {
  font-size: 42px;
  font-weight: 800;
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: 4px;
  margin-bottom: 8px;
}

.result-name {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 8px;
}

.result-tagline {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.6);
  font-style: italic;
  margin-bottom: 12px;
}

.result-style {
  display: inline-block;
  padding: 6px 16px;
  background: rgba(0, 212, 255, 0.15);
  border: 1px solid rgba(0, 212, 255, 0.3);
  border-radius: 20px;
  font-size: 13px;
  color: #00d4ff;
}

.result-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 24px;
  padding: 30px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.dimension-section {
  margin-bottom: 30px;
}

.dimension-section h3 {
  font-size: 18px;
  margin-bottom: 20px;
  color: #00d4ff;
}

.dimension-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.dimension-item {
  padding: 16px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
}

.dim-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.dim-name {
  font-size: 15px;
  font-weight: 600;
}

.dim-tendency {
  font-size: 13px;
  color: #00d4ff;
  font-weight: 600;
}

.dim-bar-bg {
  height: 10px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 5px;
  overflow: hidden;
  margin-bottom: 8px;
}

.dim-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #00d4ff, #7b2cbf);
  border-radius: 5px;
  transition: width 1s ease;
}

.dim-scale {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
}

.dim-score {
  color: rgba(255, 255, 255, 0.7);
  font-weight: 600;
}

.description-section {
  margin-bottom: 30px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 16px;
}

.description-section h3 {
  font-size: 18px;
  margin-bottom: 12px;
  color: #00d4ff;
}

.description-section p {
  font-size: 15px;
  line-height: 1.8;
  color: rgba(255, 255, 255, 0.7);
}

.traits-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
  margin-bottom: 30px;
}

.trait-box {
  padding: 16px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
}

.trait-box h4 {
  font-size: 14px;
  margin-bottom: 12px;
}

.trait-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.trait-pill {
  padding: 6px 12px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 500;
}

.trait-pill.good {
  background: rgba(0, 212, 255, 0.15);
  color: #00d4ff;
  border: 1px solid rgba(0, 212, 255, 0.3);
}

.trait-pill.bad {
  background: rgba(255, 100, 100, 0.15);
  color: #ff6464;
  border: 1px solid rgba(255, 100, 100, 0.3);
}

.spots-section {
  margin-bottom: 30px;
}

.spots-section h3 {
  font-size: 18px;
  margin-bottom: 16px;
  color: #00d4ff;
}

.spots-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.spot-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.spot-icon {
  font-size: 16px;
}

.spot-text {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
}

.actions {
  display: flex;
  gap: 15px;
}

.action-btn {
  flex: 1;
  padding: 14px;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
  text-align: center;
}

.action-btn.retest {
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  color: #fff;
}

.action-btn.share {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 20px rgba(0, 212, 255, 0.2);
}

/* 加载中 */
.loading-state {
  text-align: center;
  padding: 100px 20px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(255, 255, 255, 0.1);
  border-top-color: #00d4ff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 600px) {
  .traits-section {
    grid-template-columns: 1fr;
  }
  .result-code { font-size: 32px; }
  .result-name { font-size: 22px; }
  .actions { flex-direction: column; }
}
</style>
