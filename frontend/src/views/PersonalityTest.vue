<template>
  <div class="personality-test-page">
    <Navbar />

    <div class="test-container">
      <!-- 开始页面 -->
      <div v-if="step === 'intro'" class="intro-section">
        <div class="intro-icon">🧭</div>
        <h1 class="intro-title">TBTI 旅行人格测试</h1>
        <p class="intro-subtitle">Travel Behavioral Type Indicator</p>
        <p class="intro-desc">
          20道灵魂拷问，测出你的真实旅行人格<br>
          是Excel成精还是风的方向盘？<br>
          来，面对真实的自己
        </p>
        <div class="intro-features">
          <div class="feature-item">
            <span class="feature-num">4</span>
            <span class="feature-text">个维度</span>
          </div>
          <div class="feature-item">
            <span class="feature-num">16</span>
            <span class="feature-text">种人格</span>
          </div>
          <div class="feature-item">
            <span class="feature-num">20</span>
            <span class="feature-text">道题目</span>
          </div>
        </div>
        <button class="start-btn" @click="startTest">开始测试</button>
      </div>

      <!-- 答题页面 -->
      <div v-else-if="step === 'testing'" class="testing-section">
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: progressPercent + '%' }"></div>
        </div>
        <div class="progress-text">{{ currentIndex + 1 }} / {{ questions.length }}</div>

        <div class="question-card" v-if="currentQuestion">
          <h2 class="question-text">{{ currentQuestion.text }}</h2>
          <div class="options-list">
            <button
              v-for="(option, idx) in currentQuestion.options"
              :key="idx"
              class="option-btn"
              :class="{ selected: answers[currentIndex] === idx + 1 }"
              @click="selectAnswer(idx + 1)"
            >
              <span class="option-label">{{ ['非常不同意', '不同意', '中立', '同意', '非常同意'][idx] }}</span>
              <span class="option-text">{{ option }}</span>
            </button>
          </div>
        </div>

        <div class="nav-buttons">
          <button
            v-if="currentIndex > 0"
            class="nav-btn prev"
            @click="prevQuestion"
          >
            ← 上一题
          </button>
          <button
            v-if="currentIndex < questions.length - 1"
            class="nav-btn next"
            :disabled="!answers[currentIndex]"
            @click="nextQuestion"
          >
            下一题 →
          </button>
          <button
            v-else
            class="nav-btn submit"
            :disabled="!answers[currentIndex]"
            @click="submitTest"
          >
            查看结果
          </button>
        </div>
      </div>

      <!-- 结果页面 -->
      <div v-else-if="step === 'result' && result" class="result-section">
        <div class="result-card">
          <div class="character-wrapper">
            <PersonalityCharacter :type-code="result.type_code" />
          </div>
          <div class="result-code">{{ result.type_code }}</div>
          <h1 class="result-name">{{ result.name }}</h1>
          <p class="result-tagline">"{{ result.tagline }}"</p>

          <div class="dimension-radar">
            <div
              v-for="(dim, key) in result.dimension_details"
              :key="key"
              class="dimension-item"
            >
              <div class="dim-header">
                <span class="dim-name">{{ dim.name }}</span>
                <span class="dim-tendency">{{ dim.tendency }}</span>
              </div>
              <div class="dim-bar">
                <div class="dim-fill" :style="{ width: dim.strength + '%' }"></div>
              </div>
              <div class="dim-labels">
                <span>{{ key === 'P' ? 'P人' : key === 'E' ? '咸鱼' : key === 'S' ? 'i人' : '貔貅' }}</span>
                <span>{{ key === 'P' ? 'J人' : key === 'E' ? '肝帝' : key === 'S' ? 'e人' : '蝗虫' }}</span>
              </div>
            </div>
          </div>

          <div class="result-description">
            <h3>人格画像</h3>
            <p>{{ result.description }}</p>
          </div>

          <div class="result-traits">
            <div class="trait-section">
              <h4>✅ 天赋技能</h4>
              <div class="trait-tags">
                <span v-for="(s, i) in result.strengths" :key="i" class="trait-tag good">{{ s }}</span>
              </div>
            </div>
            <div class="trait-section">
              <h4>⚠️ 弱点暴露</h4>
              <div class="trait-tags">
                <span v-for="(w, i) in result.weaknesses" :key="i" class="trait-tag bad">{{ w }}</span>
              </div>
            </div>
          </div>

          <div class="result-spots">
            <h3>🎯 为你推荐的景点</h3>
            <div class="spots-grid">
              <div
                v-for="(spot, i) in result.recommend_spots.slice(0, 8)"
                :key="i"
                class="spot-card"
              >
                {{ spot }}
              </div>
            </div>
          </div>

          <div class="result-actions">
            <button class="action-btn save" @click="saveResult">保存到我的人格</button>
            <button class="action-btn retry" @click="retakeTest">重新测试</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import Navbar from '../components/Navbar.vue'
import PersonalityCharacter from '../components/PersonalityCharacter.vue'
import { API } from '../api'

const router = useRouter()
const step = ref('intro')
const questions = ref([])
const answers = ref([])
const currentIndex = ref(0)
const result = ref(null)
const loading = ref(false)

const currentQuestion = computed(() => {
  return questions.value[currentIndex.value] || null
})

const progressPercent = computed(() => {
  return ((currentIndex.value + 1) / questions.value.length) * 100
})

onMounted(async () => {
  try {
    const data = await API.personality.getQuestions()
    questions.value = data.questions || []
    answers.value = new Array(questions.value.length).fill(null)
  } catch (e) {
    console.error('获取题目失败:', e)
  }
})

const startTest = () => {
  step.value = 'testing'
  currentIndex.value = 0
  answers.value = new Array(questions.value.length).fill(null)
}

const selectAnswer = (value) => {
  answers.value[currentIndex.value] = value
  // 自动下一题
  if (currentIndex.value < questions.value.length - 1) {
    setTimeout(() => {
      nextQuestion()
    }, 300)
  }
}

const nextQuestion = () => {
  if (currentIndex.value < questions.value.length - 1) {
    currentIndex.value++
  }
}

const prevQuestion = () => {
  if (currentIndex.value > 0) {
    currentIndex.value--
  }
}

const submitTest = async () => {
  // 检查是否全部作答
  if (answers.value.some(a => a === null)) {
    alert('还有题目未作答哦')
    return
  }

  loading.value = true
  try {
    const data = await API.personality.submitTest(answers.value)
    result.value = data
    step.value = 'result'
  } catch (e) {
    console.error('提交测试失败:', e)
    alert('测试提交失败，请重试')
  } finally {
    loading.value = false
  }
}

const saveResult = async () => {
  const userId = localStorage.getItem('userId')
  if (!userId) {
    alert('请先登录')
    router.push('/login')
    return
  }

  try {
    await API.personality.saveResult(answers.value, parseInt(userId))
    alert('保存成功！')
    router.push('/my-personality')
  } catch (e) {
    console.error('保存失败:', e)
    alert('保存失败，请重试')
  }
}

const retakeTest = () => {
  step.value = 'intro'
  result.value = null
  currentIndex.value = 0
  answers.value = new Array(questions.value.length).fill(null)
}
</script>

<style scoped>
.personality-test-page {
  min-height: 100vh;
  background: #0a0a1a;
  color: #fff;
  padding-top: 80px;
}

.test-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

/* 开始页面 */
.intro-section {
  text-align: center;
  padding: 60px 20px;
  animation: fadeIn 0.6s ease;
}

.intro-icon {
  font-size: 80px;
  margin-bottom: 20px;
}

.intro-title {
  font-size: 36px;
  font-weight: 700;
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 10px;
}

.intro-subtitle {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 30px;
  letter-spacing: 2px;
}

.intro-desc {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.7);
  line-height: 2;
  margin-bottom: 40px;
}

.intro-features {
  display: flex;
  justify-content: center;
  gap: 40px;
  margin-bottom: 50px;
}

.feature-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.feature-num {
  font-size: 36px;
  font-weight: 700;
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.feature-text {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.5);
}

.start-btn {
  padding: 16px 60px;
  font-size: 18px;
  font-weight: 600;
  border: none;
  border-radius: 50px;
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  color: #fff;
  cursor: pointer;
  transition: all 0.3s ease;
}

.start-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 30px rgba(0, 212, 255, 0.3);
}

/* 答题页面 */
.testing-section {
  animation: fadeIn 0.4s ease;
}

.progress-bar {
  height: 4px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
  margin-bottom: 10px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #00d4ff, #7b2cbf);
  border-radius: 2px;
  transition: width 0.3s ease;
}

.progress-text {
  text-align: center;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 30px;
}

.question-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 20px;
  padding: 40px;
  margin-bottom: 30px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.question-text {
  font-size: 22px;
  font-weight: 600;
  margin-bottom: 30px;
  line-height: 1.6;
}

.options-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.option-btn {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 16px 20px;
  background: rgba(255, 255, 255, 0.05);
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  color: #fff;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: left;
}

.option-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(0, 212, 255, 0.5);
}

.option-btn.selected {
  background: rgba(0, 212, 255, 0.15);
  border-color: #00d4ff;
}

.option-label {
  font-size: 13px;
  font-weight: 600;
  color: #00d4ff;
  min-width: 80px;
  flex-shrink: 0;
}

.option-text {
  font-size: 15px;
  color: rgba(255, 255, 255, 0.8);
}

.nav-buttons {
  display: flex;
  justify-content: space-between;
  gap: 15px;
}

.nav-btn {
  padding: 14px 30px;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
}

.nav-btn.prev {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}

.nav-btn.next,
.nav-btn.submit {
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  color: #fff;
  margin-left: auto;
}

.nav-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.nav-btn:not(:disabled):hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 20px rgba(0, 212, 255, 0.3);
}

/* 结果页面 */
.result-section {
  animation: fadeIn 0.6s ease;
}

.result-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 24px;
  padding: 40px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.character-wrapper {
  margin-bottom: 16px;
  display: flex;
  justify-content: center;
}

.result-code {
  font-size: 48px;
  font-weight: 800;
  text-align: center;
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 10px;
  letter-spacing: 4px;
}

.result-name {
  font-size: 32px;
  font-weight: 700;
  text-align: center;
  margin-bottom: 10px;
}

.result-tagline {
  font-size: 18px;
  text-align: center;
  color: rgba(255, 255, 255, 0.6);
  font-style: italic;
  margin-bottom: 40px;
}

.dimension-radar {
  margin-bottom: 40px;
}

.dimension-item {
  margin-bottom: 20px;
}

.dim-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.dim-name {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
}

.dim-tendency {
  font-size: 13px;
  color: #00d4ff;
  font-weight: 600;
}

.dim-bar {
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 5px;
}

.dim-fill {
  height: 100%;
  background: linear-gradient(90deg, #00d4ff, #7b2cbf);
  border-radius: 4px;
  transition: width 1s ease;
}

.dim-labels {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
}

.result-description {
  margin-bottom: 30px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 16px;
}

.result-description h3 {
  font-size: 18px;
  margin-bottom: 12px;
  color: #00d4ff;
}

.result-description p {
  font-size: 15px;
  line-height: 1.8;
  color: rgba(255, 255, 255, 0.7);
}

.result-traits {
  margin-bottom: 30px;
}

.trait-section {
  margin-bottom: 20px;
}

.trait-section h4 {
  font-size: 16px;
  margin-bottom: 12px;
}

.trait-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.trait-tag {
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
}

.trait-tag.good {
  background: rgba(0, 212, 255, 0.15);
  color: #00d4ff;
  border: 1px solid rgba(0, 212, 255, 0.3);
}

.trait-tag.bad {
  background: rgba(255, 100, 100, 0.15);
  color: #ff6464;
  border: 1px solid rgba(255, 100, 100, 0.3);
}

.result-spots {
  margin-bottom: 30px;
}

.result-spots h3 {
  font-size: 18px;
  margin-bottom: 16px;
}

.spots-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.spot-card {
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.result-actions {
  display: flex;
  gap: 15px;
}

.action-btn {
  flex: 1;
  padding: 16px;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
}

.action-btn.save {
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  color: #fff;
}

.action-btn.retry {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 20px rgba(0, 212, 255, 0.2);
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 600px) {
  .intro-title { font-size: 28px; }
  .result-code { font-size: 36px; }
  .result-name { font-size: 24px; }
  .spots-grid { grid-template-columns: 1fr; }
  .result-actions { flex-direction: column; }
}
</style>
