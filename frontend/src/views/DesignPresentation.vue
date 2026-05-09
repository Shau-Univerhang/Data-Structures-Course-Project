<template>
  <div class="presentation-page">
    <div class="hero-background">
      <img :src="backgroundImage" alt="presentation background" class="bg-image" />
      <div class="bg-overlay"></div>
      <div class="grid-overlay"></div>
    </div>

    <Navbar />

    <main class="presentation-content">
      <!-- Hero Section -->
      <section class="hero-section">
        <div class="hero-text">
          <div class="hero-tags">
            <span class="tech-tag">中期验收</span>
            <span class="tech-tag">OpenClaw + MiniMax</span>
            <span class="tech-tag">3分钟PPT + 功能演示</span>
          </div>
          <h1>邮游世界中期验收方案</h1>
          <p class="hero-desc">
            基于大语言模型和自研算法的个性化旅游规划系统。展示创新需求、智能体开发、系统架构与核心算法的完整落地情况。
          </p>
          <div class="hero-actions">
            <button class="tech-button" @click="scrollToSection('innovation')">开始讲解</button>
            <button class="ghost-button" @click="scrollToSection('demo')">查看演示入口</button>
          </div>
        </div>

        <div class="hero-panel tech-card">
          <div class="panel-title">讲解主线</div>
          <div class="storyline-list">
            <div v-for="(item, index) in storyline" :key="item.title" class="storyline-item">
              <span class="storyline-index">{{ index + 1 }}</span>
              <div>
                <div class="storyline-title">{{ item.title }}</div>
                <div class="storyline-desc">{{ item.desc }}</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Section 01: 创新需求与亮点 -->
      <section id="innovation" class="content-section">
        <div class="section-header">
          <span class="section-kicker">01 / 创新需求与亮点</span>
          <h2>四大核心创新，超越传统旅游系统</h2>
          <p>不仅做景点推荐，更把出行前规划、游玩中导航、社交互动和内容沉淀串成完整链路。</p>
        </div>

        <div class="innovation-grid">
          <article v-for="item in innovations" :key="item.title" class="tech-card innovation-card" :class="item.highlight ? 'highlight-card' : ''">
            <div class="innovation-header">
              <span class="innovation-icon">{{ item.icon }}</span>
              <span v-if="item.star" class="star-badge">⭐ 核心</span>
            </div>
            <h3>{{ item.title }}</h3>
            <p>{{ item.desc }}</p>
            <div class="tech-stack-tags">
              <span v-for="tag in item.tags" :key="tag" class="stack-tag">{{ tag }}</span>
            </div>
          </article>
        </div>
      </section>

      <!-- Section 02: 智能体开发环境 -->
      <section class="content-section">
        <div class="section-header">
          <span class="section-kicker">02 / 智能体开发环境</span>
          <h2>OpenClaw + MiniMax 三智能体协作</h2>
          <p>基于 OpenClaw 智能体编排框架，接入 MiniMax API，构建三个专业身份定位的智能体。</p>
        </div>

        <div class="agent-env-card tech-card">
          <div class="env-header">
            <div class="env-item">
              <span class="env-label">开发平台</span>
              <span class="env-value">OpenClaw</span>
            </div>
            <div class="env-divider"></div>
            <div class="env-item">
              <span class="env-label">底层模型</span>
              <span class="env-value">MiniMax M2.5 / abab6.5s-chat</span>
            </div>
            <div class="env-divider"></div>
            <div class="env-item">
              <span class="env-label">开发方式</span>
              <span class="env-value">Prompt Engineering + JSON 结构化输出</span>
            </div>
          </div>
        </div>

        <div class="agent-grid">
          <article v-for="(agent, index) in agents" :key="agent.name" class="tech-card agent-card">
            <div class="agent-number">0{{ index + 1 }}</div>
            <div class="agent-icon">{{ agent.icon }}</div>
            <h3>{{ agent.name }}</h3>
            <p class="agent-role">{{ agent.role }}</p>
            <ul class="agent-duties">
              <li v-for="duty in agent.duties" :key="duty">{{ duty }}</li>
            </ul>
          </article>
        </div>

        <div class="tech-card agent-collab-card">
          <h3>智能体协作关系</h3>
          <div class="collab-flow">
            <div class="collab-step">
              <div class="collab-box">用户/项目经理</div>
            </div>
            <div class="collab-arrow">↓</div>
            <div class="collab-row">
              <div class="collab-box agent-box">代码架构师<br/><small>开发助手</small></div>
              <div class="collab-box agent-box">项目协调官<br/><small>分工助手</small></div>
              <div class="collab-box agent-box">文档工程师<br/><small>进度追踪官</small></div>
            </div>
            <div class="collab-arrow">↓</div>
            <div class="collab-step">
              <div class="collab-box platform-box">OpenClaw + MiniMax API</div>
            </div>
          </div>
        </div>
      </section>

      <!-- Section 03: 系统架构 -->
      <section class="content-section">
        <div class="section-header">
          <span class="section-kicker">03 / 系统整体架构</span>
          <h2>前后端分层设计与业务模块划分</h2>
          <p>围绕"探索发现 → 行程生成 → 路线优化 → 内部导航 → 旅行日记沉淀"构建完整闭环。</p>
        </div>

        <div class="architecture-diagram tech-card">
          <div class="arch-layer arch-frontend">
            <div class="arch-label">前端层</div>
            <div class="arch-content">
              <span class="arch-item">Vue 3 + Element Plus</span>
              <span class="arch-arrow">→</span>
              <span class="arch-item">20+ 页面组件</span>
            </div>
          </div>
          <div class="arch-connector">↓</div>
          <div class="arch-layer arch-backend">
            <div class="arch-label">后端层</div>
            <div class="arch-content">
              <span class="arch-item">FastAPI</span>
              <span class="arch-arrow">→</span>
              <span class="arch-item">Routers / Algorithms / Models</span>
            </div>
          </div>
          <div class="arch-connector">↓</div>
          <div class="arch-layer arch-data">
            <div class="arch-label">数据层</div>
            <div class="arch-content">
              <span class="arch-item">SQLite</span>
              <span class="arch-arrow">+</span>
              <span class="arch-item">MiniMax API</span>
            </div>
          </div>
        </div>

        <div class="module-status-grid">
          <div v-for="mod in modules" :key="mod.name" class="tech-card module-card">
            <div class="module-header">
              <span class="module-icon">{{ mod.icon }}</span>
              <span class="module-status" :class="mod.status === '完成' ? 'status-done' : 'status-progress'">{{ mod.status }}</span>
            </div>
            <div class="module-name">{{ mod.name }}</div>
            <div class="module-progress">
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: mod.progress + '%' }"></div>
              </div>
              <span class="progress-text">{{ mod.progress }}%</span>
            </div>
          </div>
        </div>
      </section>

      <!-- Section 04: 核心算法详解 -->
      <section class="content-section">
        <div class="section-header">
          <span class="section-kicker">04 / 核心算法详解</span>
          <h2>算法与业务场景一一对应</h2>
          <p>每种算法都解决一个明确问题：推荐效率、单目标寻路、多目标优化、模糊搜索、数据压缩。</p>
        </div>

        <div class="algo-timeline">
          <div v-for="(algo, index) in algorithms" :key="algo.name" class="algo-timeline-item">
            <div class="algo-timeline-left">
              <div class="algo-index">{{ String(index + 1).padStart(2, '0') }}</div>
              <div class="algo-connector" v-if="index < algorithms.length - 1"></div>
            </div>
            <div class="tech-card algo-detail-card">
              <div class="algo-detail-header">
                <div>
                  <span class="algo-badge">{{ algo.tag }}</span>
                  <h3>{{ algo.name }}</h3>
                </div>
                <span class="algo-complexity">{{ algo.complexity }}</span>
              </div>
              <div class="algo-detail-body">
                <div class="algo-detail-row">
                  <span class="detail-label">解决问题</span>
                  <p>{{ algo.problem }}</p>
                </div>
                <div class="algo-detail-row">
                  <span class="detail-label">为什么选它</span>
                  <p>{{ algo.reason }}</p>
                </div>
                <div class="algo-detail-row">
                  <span class="detail-label">落地位置</span>
                  <code class="file-code">{{ algo.file }}</code>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Section 05: 人格驱动推荐公式 -->
      <section class="content-section">
        <div class="section-header">
          <span class="section-kicker">05 / 创新算法：人格驱动推荐</span>
          <h2>TBTI 旅行人格 × 推荐算法</h2>
          <p>16种人格类型，每种都有独特的景点推荐列表，推荐时人格匹配景点额外加分。</p>
        </div>

        <div class="formula-card tech-card">
          <div class="formula-title">推荐评分公式</div>
          <div class="formula">
            <span class="formula-part">score</span>
            <span class="formula-eq">=</span>
            <span class="formula-part formula-pref">偏好匹配 × 1000</span>
            <span class="formula-op">+</span>
            <span class="formula-part formula-fav">收藏数 × 0.1</span>
            <span class="formula-op">+</span>
            <span class="formula-part formula-rating">评分 × 10</span>
            <span class="formula-op">+</span>
            <span class="formula-part formula-person">人格匹配 × 500</span>
          </div>
        </div>

        <div class="personality-dims">
          <div v-for="dim in personalityDims" :key="dim.name" class="tech-card dim-card">
            <div class="dim-icon">{{ dim.icon }}</div>
            <div class="dim-name">{{ dim.name }}</div>
            <div class="dim-vs">
              <span class="dim-a">{{ dim.a }}</span>
              <span class="dim-vs-text">VS</span>
              <span class="dim-b">{{ dim.b }}</span>
            </div>
          </div>
        </div>
      </section>

      <!-- Section 06: 开发进度 -->
      <section class="content-section">
        <div class="section-header">
          <span class="section-kicker">06 / 开发进度</span>
          <h2>整体进度远超 50% 中期要求</h2>
          <p>11个核心模块全部完成，数据规模达到课程设计要求。</p>
        </div>

        <div class="progress-overview tech-card">
          <div class="progress-circle-wrap">
            <svg class="progress-circle" viewBox="0 0 120 120">
              <circle class="progress-circle-bg" cx="60" cy="60" r="54" />
              <circle class="progress-circle-fill" cx="60" cy="60" r="54" />
            </svg>
            <div class="progress-circle-text">
              <span class="progress-percent">~100%</span>
              <span class="progress-label">整体完成度</span>
            </div>
          </div>
          <div class="progress-stats">
            <div class="stat-item">
              <span class="stat-number">277+</span>
              <span class="stat-label">景点数量</span>
            </div>
            <div class="stat-item">
              <span class="stat-number">20+</span>
              <span class="stat-label">覆盖城市</span>
            </div>
            <div class="stat-item">
              <span class="stat-number">16</span>
              <span class="stat-label">人格类型</span>
            </div>
            <div class="stat-item">
              <span class="stat-number">5</span>
              <span class="stat-label">核心算法</span>
            </div>
          </div>
        </div>
      </section>

      <!-- Section 07: 演示入口 -->
      <section id="demo" class="content-section summary-section">
        <div class="section-header">
          <span class="section-kicker">07 / 功能演示入口</span>
          <h2>点击跳转，直接体验核心功能</h2>
          <p>从讲解页直接跳转到各功能模块进行演示。</p>
        </div>

        <div class="demo-grid">
          <div v-for="demo in demos" :key="demo.name" class="tech-card demo-card-item" @click="router.push(demo.path)">
            <div class="demo-icon">{{ demo.icon }}</div>
            <h4>{{ demo.name }}</h4>
            <p>{{ demo.desc }}</p>
            <span class="demo-link">立即体验 →</span>
          </div>
        </div>
      </section>
    </main>

    <!-- Hidden SVG for gradient definition -->
    <svg width="0" height="0" style="position: absolute; visibility: hidden;">
      <defs>
        <linearGradient id="progressGradient" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stop-color="#00d4ff"></stop>
          <stop offset="100%" stop-color="#7b2cbf"></stop>
        </linearGradient>
      </defs>
    </svg>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import Navbar from '../components/Navbar.vue'

const router = useRouter()

const backgroundImage = '/images/background/test01.jpg'

const storyline = [
  { title: '创新需求与亮点', desc: '小红书导入、旅行人格、日记社区、拍照点位四大创新' },
  { title: '智能体开发环境', desc: 'OpenClaw + MiniMax 三智能体协作开发' },
  { title: '系统架构与算法', desc: '前后端分层、五大核心算法、人格驱动推荐' },
  { title: '开发进度与演示', desc: '100%完成度、数据规模、功能演示入口' }
]

const innovations = [
  {
    icon: '📕',
    title: '小红书行程智能导入',
    desc: '粘贴小红书笔记内容，AI自动解析提取景点、天数、美食，生成结构化行程。支持别名映射、模糊匹配、分隔符拆分。',
    tags: ['MiniMax AI', 'NLP解析', '智能匹配'],
    star: true,
    highlight: true
  },
  {
    icon: '🧠',
    title: '旅行人格测试（TBTI）',
    desc: '20道题、4个维度、16种人格类型。每种人格有独特景点推荐列表，推荐算法中人格匹配额外+500分权重。',
    tags: ['P/E/S/C四维度', '16型人格', '推荐联动'],
    star: true,
    highlight: true
  },
  {
    icon: '📰',
    title: '旅游日记社区',
    desc: '公开日记库、城市游记索引、评分评论系统（支持楼中楼回复）、评论点赞、软删除。形成内容社区闭环。',
    tags: ['公开日记', '评论互动', '城市索引']
  },
  {
    icon: '📸',
    title: '拍照点位与相册系统',
    desc: '为景点上传最佳拍照位置，旅行相册按行程分组，支持时间轴/行程视图切换，照片统计与管理。',
    tags: ['Photo Spot', '相册管理', '时间轴']
  },
  {
    icon: '🤖',
    title: 'AI旅行助手"邮邮"',
    desc: '多轮对话上下文记忆，自动识别目的地和天数，生成可保存的结构化行程（含daySpots按天分配）。',
    tags: ['多轮对话', '上下文记忆', '行程生成']
  },
  {
    icon: '✍️',
    title: '智能日记生成（AIGC）',
    desc: '一句话灵感生成完整旅行日记，5种写作风格（治愈/幽默/纪实/诗意/简洁），支持图片AI分析、内容润色。',
    tags: ['AIGC', '多模态', '风格切换']
  }
]

const agents = [
  {
    icon: '💻',
    name: '代码架构师与开发助手',
    role: '专注于代码架构与开发实现',
    duties: [
      '分析项目已有代码（core.py、routers、前端组件）',
      '基于现有代码风格给出开发建议',
      '修复Bug、优化算法性能、重构代码',
      '协助完成数据结构课程算法实现'
    ]
  },
  {
    icon: '📋',
    name: '项目协调官与分工助手',
    role: '专注于团队协调与任务分配',
    duties: [
      '根据3人团队能力特长合理分配任务',
      '制定每周工作计划与里程碑',
      '识别任务依赖关系，避免阻塞',
      '协调前后端API接口对接'
    ]
  },
  {
    icon: '📚',
    name: '文档工程师与进度追踪官',
    role: '专注于文档创作与进度追踪',
    duties: [
      '撰写课程设计文档（需求/设计/算法/测试）',
      '制作答辩PPT，突出算法应用与创新',
      '执行代码全景扫描与每周进度追踪',
      '分析GitHub提交历史，生成贡献统计'
    ]
  }
]

const modules = [
  { name: '首页轮播', icon: '🏠', status: '完成', progress: 100 },
  { name: '景点推荐', icon: '📍', status: '完成', progress: 100 },
  { name: '路线规划', icon: '🗺️', status: '完成', progress: 100 },
  { name: '室内导航', icon: '🏫', status: '完成', progress: 100 },
  { name: '场所查询', icon: '🔍', status: '完成', progress: 100 },
  { name: '旅游日记', icon: '📒', status: '完成', progress: 100 },
  { name: '美食推荐', icon: '🍜', status: '完成', progress: 100 },
  { name: 'AI助手', icon: '🤖', status: '完成', progress: 100 },
  { name: '小红书导入', icon: '📕', status: '完成', progress: 100 },
  { name: '旅行人格', icon: '🧠', status: '完成', progress: 100 },
  { name: '拍照/相册', icon: '📸', status: '完成', progress: 100 }
]

const algorithms = [
  {
    tag: '推荐效率',
    name: 'Top-K 部分排序',
    complexity: 'O(n log k)',
    problem: '景点和餐厅很多时，需要高效给出前若干个最值得推荐的结果。',
    reason: '不需要对全部数据完整排序，只保留最有价值的前 k 项，效率更高。',
    file: 'backend/algorithms/core.py'
  },
  {
    tag: '单目标寻路',
    name: 'Dijkstra 最短路径',
    complexity: 'O((V+E) log V)',
    problem: '当用户确定起点和终点时，快速求出最短时间或最短距离路径。',
    reason: '适合带权图最短路问题，和内部道路网络建模天然匹配。',
    file: 'backend/algorithms/core.py'
  },
  {
    tag: '多目标优化',
    name: 'TSP 贪心 + 2-opt',
    complexity: 'O(n²)',
    problem: '当用户希望一次游览多个点位时，给出更优访问顺序。',
    reason: '比暴力枚举更适合实际交互场景，在效果和效率间取得平衡。',
    file: 'backend/algorithms/core.py'
  },
  {
    tag: '模糊搜索',
    name: 'Levenshtein 编辑距离',
    complexity: 'O(n × m)',
    problem: '用户输入可能有错别字或拼音首字母，需要容错搜索。',
    reason: '支持子串匹配、编辑距离相似度计算，提升搜索体验。',
    file: 'backend/algorithms/core.py'
  },
  {
    tag: '数据压缩',
    name: 'Gzip 无损压缩',
    complexity: '-',
    problem: '日记内容较长，需要节省数据库存储空间。',
    reason: 'gzip压缩率高且解压快，适合文本类内容存储优化。',
    file: 'backend/algorithms/core.py'
  }
]

const personalityDims = [
  { icon: '📅', name: '规划性 (P)', a: 'J人计划控', b: 'P人随性派' },
  { icon: '🎯', name: '体验重心 (E)', a: '肝帝探索型', b: '咸鱼享受型' },
  { icon: '👥', name: '社交模式 (S)', a: 'e人社交狂', b: 'i人独行者' },
  { icon: '💰', name: '消费态度 (C)', a: '蝗虫集邮党', b: '貔貅品质控' }
]

const demos = [
  { name: '旅行人格测试', icon: '🧠', desc: '20题测试，发现你的旅行人格', path: '/personality-test' },
  { name: 'AI助手', icon: '🤖', desc: '与邮邮对话，生成专属行程', path: '/ai' },
  { name: '探索发现', icon: '🌍', desc: '浏览景点、美食与城市', path: '/explore' },
  { name: '旅行日记', icon: '📒', desc: '记录旅程，分享故事', path: '/diary' },
  { name: '路线规划', icon: '🗺️', desc: 'Dijkstra + TSP 智能规划', path: '/trips' },
  { name: '景点推荐', icon: '📍', desc: '人格驱动的个性化推荐', path: '/spot-recommend' }
]

function scrollToSection(id) {
  const element = document.getElementById(id)
  element?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}
</script>

<style scoped>
.presentation-page {
  min-height: 100vh;
  position: relative;
  overflow-x: hidden;
}

.hero-background {
  position: fixed;
  inset: 0;
  z-index: 0;
}

.bg-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.bg-overlay {
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at top right, rgba(0, 212, 255, 0.18), transparent 30%),
    linear-gradient(180deg, rgba(5, 10, 24, 0.72) 0%, rgba(8, 12, 28, 0.88) 45%, rgba(10, 10, 26, 0.96) 100%);
}

.grid-overlay {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.04) 1px, transparent 1px);
  background-size: 42px 42px;
  mask-image: linear-gradient(to bottom, rgba(0, 0, 0, 0.5), transparent 90%);
}

.presentation-content {
  position: relative;
  z-index: 1;
  padding: 110px 60px 80px;
}

/* Hero */
.hero-section {
  min-height: calc(100vh - 120px);
  display: grid;
  grid-template-columns: minmax(0, 1.3fr) minmax(320px, 460px);
  gap: 32px;
  align-items: center;
}

.hero-text h1 {
  font-size: 52px;
  line-height: 1.15;
  margin: 20px 0 24px;
  max-width: 760px;
  background: linear-gradient(135deg, #fff 0%, #00d4ff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hero-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.tech-tag {
  padding: 6px 16px;
  border-radius: 20px;
  background: rgba(0, 212, 255, 0.12);
  border: 1px solid rgba(0, 212, 255, 0.3);
  color: #00d4ff;
  font-size: 13px;
}

.hero-desc {
  max-width: 760px;
  font-size: 18px;
  line-height: 1.8;
  color: rgba(255, 255, 255, 0.86);
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-top: 30px;
}

.tech-button {
  padding: 14px 32px;
  border-radius: 30px;
  border: none;
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  color: #fff;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.tech-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(0, 212, 255, 0.35);
}

.ghost-button {
  border: 1px solid rgba(255, 255, 255, 0.28);
  background: rgba(255, 255, 255, 0.08);
  color: #fff;
  border-radius: 25px;
  padding: 12px 28px;
  font-size: 15px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.ghost-button:hover {
  transform: translateY(-2px);
  border-color: rgba(255, 255, 255, 0.5);
  background: rgba(255, 255, 255, 0.14);
}

.hero-panel {
  padding: 28px;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
}

.panel-title {
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 18px;
}

.storyline-list {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.storyline-item {
  display: flex;
  gap: 14px;
  align-items: flex-start;
}

.storyline-index {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  font-weight: 700;
  flex-shrink: 0;
  font-size: 14px;
}

.storyline-title {
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 4px;
}

.storyline-desc {
  color: rgba(255, 255, 255, 0.65);
  line-height: 1.6;
  font-size: 14px;
}

/* Sections */
.content-section {
  margin-top: 80px;
}

.section-header {
  max-width: 860px;
  margin-bottom: 32px;
}

.section-kicker {
  display: inline-block;
  margin-bottom: 12px;
  color: #00d4ff;
  font-size: 14px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.section-header h2 {
  font-size: 36px;
  margin-bottom: 14px;
  font-weight: 700;
}

.section-header p {
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.8;
  font-size: 17px;
}

/* Tech Card Base */
.tech-card {
  background: rgba(255, 255, 255, 0.04);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  padding: 28px;
  transition: all 0.3s ease;
}

.tech-card:hover {
  border-color: rgba(0, 212, 255, 0.25);
  transform: translateY(-3px);
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
}

/* Innovation Grid */
.innovation-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.innovation-card {
  position: relative;
  overflow: hidden;
}

.innovation-card.highlight-card {
  border-color: rgba(0, 212, 255, 0.3);
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.06), rgba(123, 44, 191, 0.06));
}

.innovation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
}

.innovation-icon {
  font-size: 32px;
}

.star-badge {
  padding: 4px 10px;
  border-radius: 12px;
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  color: #fff;
  font-size: 12px;
  font-weight: 600;
}

.innovation-card h3 {
  font-size: 20px;
  margin-bottom: 10px;
  font-weight: 700;
}

.innovation-card p {
  color: rgba(255, 255, 255, 0.72);
  line-height: 1.7;
  font-size: 14px;
  margin-bottom: 16px;
}

.tech-stack-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.stack-tag {
  padding: 4px 10px;
  border-radius: 8px;
  background: rgba(0, 212, 255, 0.1);
  border: 1px solid rgba(0, 212, 255, 0.2);
  color: #00d4ff;
  font-size: 12px;
}

/* Agent Environment */
.agent-env-card {
  margin-bottom: 24px;
  padding: 20px 28px;
}

.env-header {
  display: flex;
  align-items: center;
  gap: 24px;
  flex-wrap: wrap;
}

.env-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.env-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.env-value {
  font-size: 16px;
  font-weight: 600;
  color: #00d4ff;
}

.env-divider {
  width: 1px;
  height: 40px;
  background: rgba(255, 255, 255, 0.1);
}

/* Agent Grid */
.agent-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.agent-card {
  position: relative;
  padding-top: 50px;
}

.agent-number {
  position: absolute;
  top: 16px;
  right: 20px;
  font-size: 48px;
  font-weight: 800;
  color: rgba(0, 212, 255, 0.1);
  line-height: 1;
}

.agent-icon {
  font-size: 36px;
  margin-bottom: 12px;
}

.agent-card h3 {
  font-size: 18px;
  margin-bottom: 6px;
  font-weight: 700;
}

.agent-role {
  color: #00d4ff;
  font-size: 14px;
  margin-bottom: 14px;
}

.agent-duties {
  list-style: none;
  padding: 0;
  margin: 0;
}

.agent-duties li {
  padding: 6px 0;
  padding-left: 18px;
  position: relative;
  color: rgba(255, 255, 255, 0.7);
  font-size: 13px;
  line-height: 1.6;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.agent-duties li::before {
  content: '▸';
  position: absolute;
  left: 0;
  color: #00d4ff;
}

/* Agent Collab */
.agent-collab-card h3 {
  margin-bottom: 24px;
  font-size: 20px;
}

.collab-flow {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.collab-step, .collab-row {
  width: 100%;
  display: flex;
  justify-content: center;
}

.collab-row {
  gap: 16px;
  flex-wrap: wrap;
}

.collab-box {
  padding: 16px 24px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  text-align: center;
  font-weight: 600;
  min-width: 140px;
}

.collab-box small {
  display: block;
  margin-top: 4px;
  font-weight: 400;
  color: rgba(255, 255, 255, 0.6);
  font-size: 13px;
}

.agent-box {
  border-color: rgba(0, 212, 255, 0.3);
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.08), rgba(123, 44, 191, 0.08));
}

.platform-box {
  border-color: rgba(123, 44, 191, 0.4);
  background: linear-gradient(135deg, rgba(123, 44, 191, 0.1), rgba(0, 212, 255, 0.1));
}

.collab-arrow {
  font-size: 24px;
  color: #00d4ff;
  font-weight: 700;
}

/* Architecture Diagram */
.architecture-diagram {
  display: flex;
  flex-direction: column;
  gap: 0;
  padding: 32px;
  margin-bottom: 24px;
}

.arch-layer {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 20px 24px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.arch-frontend { border-left: 4px solid #00d4ff; }
.arch-backend { border-left: 4px solid #7b2cbf; }
.arch-data { border-left: 4px solid #00ff88; }

.arch-label {
  font-weight: 700;
  font-size: 14px;
  min-width: 80px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.arch-frontend .arch-label { color: #00d4ff; }
.arch-backend .arch-label { color: #a855f7; }
.arch-data .arch-label { color: #00ff88; }

.arch-content {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.arch-item {
  padding: 8px 16px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.06);
  font-size: 14px;
}

.arch-arrow {
  color: rgba(255, 255, 255, 0.4);
}

.arch-connector {
  text-align: center;
  color: rgba(255, 255, 255, 0.3);
  font-size: 20px;
  padding: 8px 0;
}

/* Module Status */
.module-status-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.module-card {
  padding: 20px;
}

.module-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.module-icon {
  font-size: 24px;
}

.module-status {
  padding: 3px 10px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 600;
}

.status-done {
  background: rgba(0, 255, 136, 0.15);
  color: #00ff88;
  border: 1px solid rgba(0, 255, 136, 0.3);
}

.status-progress {
  background: rgba(255, 193, 7, 0.15);
  color: #ffc107;
  border: 1px solid rgba(255, 193, 7, 0.3);
}

.module-name {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 12px;
}

.module-progress {
  display: flex;
  align-items: center;
  gap: 10px;
}

.progress-bar {
  flex: 1;
  height: 6px;
  border-radius: 3px;
  background: rgba(255, 255, 255, 0.08);
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 3px;
  background: linear-gradient(90deg, #00d4ff, #7b2cbf);
  transition: width 1s ease;
}

.progress-text {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  min-width: 36px;
}

/* Algorithm Timeline */
.algo-timeline {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.algo-timeline-item {
  display: flex;
  gap: 20px;
}

.algo-timeline-left {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 60px;
  flex-shrink: 0;
}

.algo-index {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  font-weight: 800;
  font-size: 18px;
  color: #fff;
}

.algo-connector {
  width: 2px;
  flex: 1;
  background: linear-gradient(180deg, rgba(0, 212, 255, 0.4), rgba(123, 44, 191, 0.4));
  margin: 8px 0;
}

.algo-detail-card {
  flex: 1;
  margin-bottom: 24px;
}

.algo-detail-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 10px;
}

.algo-detail-header h3 {
  font-size: 22px;
  margin-top: 8px;
  font-weight: 700;
}

.algo-badge {
  display: inline-flex;
  padding: 4px 12px;
  border-radius: 20px;
  background: rgba(0, 212, 255, 0.12);
  border: 1px solid rgba(0, 212, 255, 0.28);
  color: #00d4ff;
  font-size: 12px;
  font-weight: 600;
  margin-bottom: 8px;
}

.algo-complexity {
  padding: 6px 14px;
  border-radius: 10px;
  background: rgba(123, 44, 191, 0.15);
  border: 1px solid rgba(123, 44, 191, 0.3);
  color: #a855f7;
  font-size: 14px;
  font-weight: 700;
  font-family: 'Courier New', monospace;
}

.algo-detail-row {
  padding: 10px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.algo-detail-row:last-child {
  border-bottom: none;
}

.detail-label {
  display: block;
  font-weight: 700;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 4px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.algo-detail-row p {
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.6;
  font-size: 14px;
}

.file-code {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 6px;
  background: rgba(0, 212, 255, 0.1);
  color: #00d4ff;
  font-size: 13px;
  font-family: 'Courier New', monospace;
}

/* Formula Card */
.formula-card {
  text-align: center;
  padding: 40px;
  margin-bottom: 24px;
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.06), rgba(123, 44, 191, 0.06));
  border-color: rgba(0, 212, 255, 0.2);
}

.formula-title {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.5);
  text-transform: uppercase;
  letter-spacing: 0.15em;
  margin-bottom: 20px;
}

.formula {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  align-items: center;
  gap: 8px;
  font-size: 18px;
}

.formula-part {
  padding: 8px 16px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.06);
  font-weight: 600;
}

.formula-eq {
  font-weight: 800;
  color: #00d4ff;
}

.formula-op {
  color: rgba(255, 255, 255, 0.5);
  font-weight: 700;
}

.formula-pref { border-bottom: 2px solid #00d4ff; }
.formula-fav { border-bottom: 2px solid #a855f7; }
.formula-rating { border-bottom: 2px solid #00ff88; }
.formula-person { border-bottom: 2px solid #ff6b6b; }

/* Personality Dims */
.personality-dims {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.dim-card {
  text-align: center;
  padding: 28px 20px;
}

.dim-icon {
  font-size: 32px;
  margin-bottom: 10px;
}

.dim-name {
  font-weight: 700;
  font-size: 16px;
  margin-bottom: 14px;
}

.dim-vs {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.dim-a, .dim-b {
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
}

.dim-a {
  background: rgba(0, 212, 255, 0.12);
  color: #00d4ff;
}

.dim-b {
  background: rgba(123, 44, 191, 0.12);
  color: #a855f7;
}

.dim-vs-text {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
  font-weight: 700;
}

/* Progress Overview */
.progress-overview {
  display: flex;
  align-items: center;
  gap: 60px;
  padding: 40px;
}

.progress-circle-wrap {
  position: relative;
  width: 180px;
  height: 180px;
  flex-shrink: 0;
}

.progress-circle {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}

.progress-circle-bg {
  fill: none;
  stroke: rgba(255, 255, 255, 0.08);
  stroke-width: 8;
}

.progress-circle-fill {
  fill: none;
  stroke: url(#progressGradient);
  stroke-width: 8;
  stroke-linecap: round;
  stroke-dasharray: 339.292;
  stroke-dashoffset: 0;
  animation: progressAnimation 2s ease-out forwards;
}

.progress-circle-text {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.progress-percent {
  font-size: 36px;
  font-weight: 800;
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.progress-label {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
  margin-top: 4px;
}

.progress-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
  flex: 1;
}

.stat-item {
  padding: 20px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  text-align: center;
}

.stat-number {
  display: block;
  font-size: 32px;
  font-weight: 800;
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 6px;
}

.stat-label {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
}

/* Demo Grid */
.demo-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.demo-card-item {
  cursor: pointer;
  text-align: center;
  padding: 32px 24px;
  transition: all 0.3s ease;
}

.demo-card-item:hover {
  transform: translateY(-5px);
  border-color: rgba(0, 212, 255, 0.4);
  box-shadow: 0 15px 50px rgba(0, 212, 255, 0.15);
}

.demo-icon {
  font-size: 40px;
  margin-bottom: 14px;
}

.demo-card-item h4 {
  font-size: 18px;
  margin-bottom: 8px;
  font-weight: 700;
}

.demo-card-item p {
  color: rgba(255, 255, 255, 0.65);
  font-size: 14px;
  margin-bottom: 16px;
  line-height: 1.5;
}

.demo-link {
  color: #00d4ff;
  font-size: 14px;
  font-weight: 600;
}

/* SVG Gradient Definition - needs to be in HTML */
/* We'll add this via a hidden SVG in the template if needed */

/* Animations */
@keyframes progressAnimation {
  from { stroke-dashoffset: 339.292; }
  to { stroke-dashoffset: 0; }
}

/* Responsive */
@media (max-width: 1200px) {
  .presentation-content {
    padding: 100px 28px 60px;
  }

  .hero-section {
    grid-template-columns: 1fr;
  }

  .hero-text h1 {
    font-size: 40px;
  }

  .innovation-grid,
  .agent-grid,
  .module-status-grid,
  .personality-dims,
  .demo-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .progress-overview {
    flex-direction: column;
    gap: 32px;
  }

  .formula {
    font-size: 15px;
  }
}

@media (max-width: 768px) {
  .presentation-content {
    padding: 92px 18px 50px;
  }

  .hero-text h1 {
    font-size: 32px;
  }

  .section-header h2 {
    font-size: 28px;
  }

  .innovation-grid,
  .agent-grid,
  .module-status-grid,
  .personality-dims,
  .demo-grid,
  .collab-row {
    grid-template-columns: 1fr;
  }

  .env-header {
    flex-direction: column;
    gap: 12px;
  }

  .env-divider {
    width: 100%;
    height: 1px;
  }

  .formula {
    flex-direction: column;
    gap: 6px;
  }

  .progress-stats {
    grid-template-columns: 1fr;
  }

  .algo-timeline-item {
    flex-direction: column;
  }

  .algo-timeline-left {
    flex-direction: row;
    width: 100%;
  }

  .algo-connector {
    display: none;
  }
}
</style>