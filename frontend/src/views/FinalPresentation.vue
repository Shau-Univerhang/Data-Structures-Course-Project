<template>
  <div class="final-page">
    <Navbar />

    <!-- 粒子背景 -->
    <canvas ref="particleCanvas" class="particle-canvas"></canvas>

    <!-- 固定导航锚点 -->
    <nav class="fp-nav">
      <div class="fp-nav-sections">
        <a v-for="s in navSections" :key="s.id" :href="'#' + s.id" :class="{ active: currentSection === s.id }">
          <span class="nav-dot"></span>
          <span class="nav-label">{{ s.label }}</span>
        </a>
      </div>
    </nav>

    <!-- S1: Hero -->
    <section id="hero" class="fp-section fp-hero">
      <div class="fp-hero-bg"></div>
      <div class="fp-hero-content">
        <div class="fp-hero-badge">
          <span class="badge-pulse"></span>
          最终验收演示
        </div>
        <h1 class="fp-hero-title">
          <span class="title-line">邮游世界</span>
          <span class="title-sub">个性化旅游推荐系统</span>
        </h1>
        <p class="fp-hero-desc">
          融合<em>16种旅行人格</em> × <em>10大核心算法</em> × <em>AI全链路生成</em>的智能旅游平台<br />
          从人格测试到行程规划，从路线导航到VLOG生成，从日记沉淀到3D地球足迹——一站式闭环体验
        </p>
        <div class="fp-hero-stats">
          <div class="hero-stat">
            <span class="stat-num">287</span>
            <span class="stat-lbl">景区/校园</span>
          </div>
          <div class="hero-stat">
            <span class="stat-num">2,575</span>
            <span class="stat-lbl">道路边数</span>
          </div>
          <div class="hero-stat">
            <span class="stat-num">10+</span>
            <span class="stat-lbl">核心算法</span>
          </div>
          <div class="hero-stat">
            <span class="stat-num">16</span>
            <span class="stat-lbl">旅行人格</span>
          </div>
          <div class="hero-stat">
            <span class="stat-num">20+</span>
            <span class="stat-lbl">页面组件</span>
          </div>
        </div>
        <div class="fp-hero-actions">
          <a href="#innovation" class="fp-btn-primary">开始讲解</a>
          <a href="#demo" class="fp-btn-ghost">直接体验 →</a>
        </div>
      </div>
      <div class="fp-scroll-hint">
        <span>滚动探索</span>
        <div class="scroll-arrow">↓</div>
      </div>
    </section>

    <!-- S2: 创新亮点 -->
    <section id="innovation" class="fp-section fp-dark">
      <div class="fp-section-inner">
        <div class="fp-section-head">
          <span class="fp-section-num">01</span>
          <h2>九大创新亮点<span class="accent">.</span></h2>
          <p>将 AI 深度融入旅游全链路——从人格洞察到内容创作，从地理探索到社交互动</p>
        </div>
        <div class="fp-innovation-grid">
          <div v-for="(item, i) in innovations" :key="i" class="fp-innovation-card" :style="{ animationDelay: `${i * 0.1}s` }">
            <div class="fp-inn-icon">{{ item.icon }}</div>
            <div class="fp-inn-tag">{{ item.tag }}</div>
            <h3>{{ item.title }}</h3>
            <p>{{ item.desc }}</p>
            <div class="fp-inn-tech">
              <span v-for="t in item.tech" :key="t">{{ t }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- S3: 智能体开发 -->
    <section id="agent" class="fp-section fp-dark-alt">
      <div class="fp-section-inner">
        <div class="fp-section-head">
          <span class="fp-section-num">02</span>
          <h2>智能体辅助开发体系<span class="accent">.</span></h2>
          <p>Trae IDE + Claude Code + 三个定制 OpenClaw 智能体协同工作</p>
        </div>

        <div class="fp-env-bar">
          <div class="fp-env-item">
            <span class="fp-env-icon">🖥</span>
            <div>
              <div class="fp-env-label">AI IDE</div>
              <div class="fp-env-val">Trae (Claude 4.0)</div>
            </div>
          </div>
          <div class="fp-env-div"></div>
          <div class="fp-env-item">
            <span class="fp-env-icon">⌨</span>
            <div>
              <div class="fp-env-label">辅助工具</div>
              <div class="fp-env-val">Claude Code (CLI)</div>
            </div>
          </div>
          <div class="fp-env-div"></div>
          <div class="fp-env-item">
            <span class="fp-env-icon">🤖</span>
            <div>
              <div class="fp-env-label">智能体框架</div>
              <div class="fp-env-val">OpenClaw 三智能体</div>
            </div>
          </div>
          <div class="fp-env-div"></div>
          <div class="fp-env-item">
            <span class="fp-env-icon">🧩</span>
            <div>
              <div class="fp-env-label">开发模式</div>
              <div class="fp-env-val">Vibecoding</div>
            </div>
          </div>
        </div>

        <div class="fp-agent-grid">
          <div class="fp-agent-card" v-for="(a, i) in agents" :key="i">
            <div class="fp-agent-num">{{ String(i + 1).padStart(2, '0') }}</div>
            <div class="fp-agent-avatar">{{ a.icon }}</div>
            <h3>{{ a.name }}</h3>
            <p class="fp-agent-role">{{ a.role }}</p>
            <ul>
              <li v-for="d in a.duties" :key="d">{{ d }}</li>
            </ul>
          </div>
        </div>

        <div class="fp-flow-card">
          <div class="fp-flow-title">智能体协作流程</div>
          <div class="fp-flow">
            <div class="fp-flow-node">👤 用户需求</div>
            <div class="fp-flow-arrow">→</div>
            <div class="fp-flow-node active">📋 项目协调官<br /><small>任务拆解 · 分工</small></div>
            <div class="fp-flow-arrow">→</div>
            <div class="fp-flow-node active">💻 代码架构师<br /><small>分析代码 · 开发</small></div>
            <div class="fp-flow-arrow">→</div>
            <div class="fp-flow-node active">📚 文档追踪官<br /><small>文档 · 进度 · 周报</small></div>
            <div class="fp-flow-arrow">→</div>
            <div class="fp-flow-node">✅ 交付验收</div>
          </div>
        </div>
      </div>
    </section>

    <!-- S4: 系统架构 -->
    <section id="arch" class="fp-section fp-dark">
      <div class="fp-section-inner">
        <div class="fp-section-head">
          <span class="fp-section-num">03</span>
          <h2>系统整体架构<span class="accent">.</span></h2>
          <p>Vue 3 + FastAPI + SQLite，前后端分离，12个路由模块，14张数据表</p>
        </div>

        <div class="fp-arch">
          <div class="fp-arch-layer frontend">
            <div class="fp-arch-lbl">表现层</div>
            <div class="fp-arch-items">
              <span>Vue 3 + Vite</span><span>Element Plus</span><span>高德地图 2.0</span>
              <span>Pinia 状态管理</span><span>Vue Router</span><span>20+ 页面组件</span>
            </div>
          </div>
          <div class="fp-arch-conn"></div>
          <div class="fp-arch-layer api">
            <div class="fp-arch-lbl">API 网关</div>
            <div class="fp-arch-items">
              <span>FastAPI</span><span>CORS</span><span>JWT 认证</span>
              <span>文件上传</span><span>静态资源</span>
            </div>
          </div>
          <div class="fp-arch-conn"></div>
          <div class="fp-arch-layer logic">
            <div class="fp-arch-lbl">业务层 — 12个路由模块</div>
            <div class="fp-arch-items small">
              <span>spots</span><span>route</span><span>diary</span><span>ai</span>
              <span>trips</span><span>food</span><span>xiaohongshu</span><span>personality</span>
              <span>auth</span><span>collection</span><span>photo</span><span>photo_spot</span>
            </div>
          </div>
          <div class="fp-arch-conn"></div>
          <div class="fp-arch-layer algo">
            <div class="fp-arch-lbl">算法层 — 3个算法模块</div>
            <div class="fp-arch-items small">
              <span>core.py<br /><small>8大算法</small></span>
              <span>diary_recommend.py<br /><small>推荐引擎</small></span>
              <span>personality_algorithm.py<br /><small>16人格</small></span>
            </div>
          </div>
          <div class="fp-arch-conn"></div>
          <div class="fp-arch-layer data">
            <div class="fp-arch-lbl">数据层</div>
            <div class="fp-arch-items small">
              <span>SQLite</span><span>FTS5 全文索引</span><span>DeepSeek API</span>
              <span>Seedance VLOG</span><span>火山引擎 TTS</span><span>MiniMax AIGC</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- S5: 核心算法 -->
    <section id="algo" class="fp-section fp-dark-alt">
      <div class="fp-section-inner">
        <div class="fp-section-head">
          <span class="fp-section-num">04</span>
          <h2>核心算法全景<span class="accent">.</span></h2>
          <p>10+ 种核心算法，每种都有明确的业务场景、选择依据和性能分析</p>
        </div>

        <div class="fp-algo-grid">
          <div class="fp-algo-card" v-for="algo in algorithms" :key="algo.name">
            <div class="fp-algo-tag">{{ algo.tag }}</div>
            <h3>{{ algo.name }}</h3>
            <div class="fp-algo-meta">
              <span class="fp-algo-complexity">T: {{ algo.complexity }}</span>
              <span class="fp-algo-space" v-if="algo.space">S: {{ algo.space }}</span>
            </div>
            <p class="fp-algo-problem">{{ algo.problem }}</p>
            <div class="fp-algo-reason">
              <span class="reason-label">为什么选它</span>
              <p>{{ algo.reason }}</p>
            </div>
            <div class="fp-algo-location">{{ algo.location }}</div>
          </div>
        </div>
      </div>
    </section>

    <!-- S6: 数据规模 -->
    <section id="data" class="fp-section fp-dark">
      <div class="fp-section-inner">
        <div class="fp-section-head">
          <span class="fp-section-num">05</span>
          <h2>数据规模验证<span class="accent">.</span></h2>
          <p>所有数据指标均达到或超过课程设计要求</p>
        </div>

        <div class="fp-data-grid">
          <div class="fp-data-card highlight">
            <div class="fp-data-icon">🏔</div>
            <div class="fp-data-num">287</div>
            <div class="fp-data-label">景区/校园数</div>
            <div class="fp-data-req">要求 ≥ 200 · 超额 43.5%</div>
          </div>
          <div class="fp-data-card highlight">
            <div class="fp-data-icon">🏗</div>
            <div class="fp-data-num">90</div>
            <div class="fp-data-label">建筑物数</div>
            <div class="fp-data-req">要求 ≥ 20/景区</div>
          </div>
          <div class="fp-data-card highlight">
            <div class="fp-data-icon">🔗</div>
            <div class="fp-data-num">2,575</div>
            <div class="fp-data-label">道路边数</div>
            <div class="fp-data-req">要求 ≥ 200 · 超额 1187%</div>
          </div>
          <div class="fp-data-card">
            <div class="fp-data-icon">🏪</div>
            <div class="fp-data-num">152</div>
            <div class="fp-data-label">服务设施</div>
            <div class="fp-data-req">13种 · 要求 ≥ 10种</div>
          </div>
          <div class="fp-data-card">
            <div class="fp-data-icon">🚏</div>
            <div class="fp-data-num">1,653</div>
            <div class="fp-data-label">道路节点</div>
            <div class="fp-data-req">覆盖步行/骑行/电瓶车道</div>
          </div>
          <div class="fp-data-card">
            <div class="fp-data-icon">📔</div>
            <div class="fp-data-num">11</div>
            <div class="fp-data-label">旅游日记</div>
            <div class="fp-data-req">含3篇高质量示例</div>
          </div>
        </div>
      </div>
    </section>

    <!-- S7: AI 开发模式 -->
    <section id="devmode" class="fp-section fp-dark-alt">
      <div class="fp-section-inner">
        <div class="fp-section-head">
          <span class="fp-section-num">06</span>
          <h2>AI 开发模式<span class="accent">.</span></h2>
          <p>Vibecoding 模式 + 人机协作，贯穿系统设计、开发、测试全过程</p>
        </div>

        <div class="fp-dev-flow">
          <div class="fp-dev-step" v-for="(step, i) in devSteps" :key="i">
            <div class="fp-dev-step-num">{{ i + 1 }}</div>
            <div class="fp-dev-step-content">
              <h4>{{ step.title }}</h4>
              <p>{{ step.desc }}</p>
            </div>
          </div>
        </div>

        <div class="fp-role-card">
          <h3>人机协作分工</h3>
          <div class="fp-role-row">
            <div class="fp-role-box ai">
              <div class="fp-role-icon">🤖</div>
              <h4>AI 负责</h4>
              <p>代码生成 · 算法实现 · UI 布局 · Bug 修复建议 · 文档生成 · 代码审查</p>
            </div>
            <div class="fp-role-vs">⇄</div>
            <div class="fp-role-box human">
              <div class="fp-role-icon">👤</div>
              <h4>人类负责</h4>
              <p>需求定义 · 架构决策 · 代码审查 · 联调测试 · 答辩准备 · 最终质量把控</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- S8: 实践反思 -->
    <section id="reflect" class="fp-section fp-dark">
      <div class="fp-section-inner">
        <div class="fp-section-head">
          <span class="fp-section-num">07</span>
          <h2>实践反思与成长<span class="accent">.</span></h2>
          <p>通过一学期的 AI 辅助开发实践，对 AI 开发模式的深刻思考</p>
        </div>

        <div class="fp-reflect-grid">
          <div class="fp-reflect-card good">
            <h3>✅ AI 赋能带来的提升</h3>
            <ul>
              <li>复杂算法（Held-Karp DP、MaxHeap）借助 AI 快速完成正确实现</li>
              <li>从想法到可运行系统的周期大幅缩短，功能模块 30 分钟即可落地</li>
              <li>Vue 3、FastAPI、Python 多技术栈无缝切换，降低全栈开发门槛</li>
              <li>AI 辅助代码审查，及时发现潜在 Bug 和性能问题</li>
            </ul>
          </div>
          <div class="fp-reflect-card warn">
            <h3>⚠️ 遇到的问题与应对</h3>
            <ul>
              <li><strong>AI 幻觉</strong>：生成不存在的 API 参数 → 必须结合官方文档验证</li>
              <li><strong>代码风格不一致</strong>：多轮对话风格漂移 → 为 AI 设定明确的代码规范</li>
              <li><strong>Git 合并冲突</strong>：多人协作 AI 代码冲突 → 建立分支管理策略</li>
              <li><strong>数据库未迁移</strong>：模型变更无迁移脚本 → 添加 startup_migrations()</li>
            </ul>
          </div>
          <div class="fp-reflect-card insight">
            <h3>💡 核心洞察</h3>
            <ul>
              <li>AI 是生产力倍增器，但不是替代品——核心算法必须自己理解透彻</li>
              <li>提示词工程（Prompt Engineering）是新一代编程核心技能</li>
              <li>应要求 AI 先输出方案再编码，避免盲目修改</li>
              <li>重要逻辑需在 AI 辅助下手写一遍加深理解</li>
            </ul>
          </div>
        </div>
      </div>
    </section>

    <!-- S9: 功能演示入口 -->
    <section id="demo" class="fp-section fp-dark-alt">
      <div class="fp-section-inner">
        <div class="fp-section-head">
          <span class="fp-section-num">08</span>
          <h2>功能演示入口<span class="accent">.</span></h2>
          <p>点击下方卡片，直接跳转各功能模块进行演示</p>
        </div>

        <div class="fp-demo-grid">
          <div v-for="d in demos" :key="d.path" class="fp-demo-card" @click="$router.push(d.path)">
            <div class="fp-demo-top">
              <span class="fp-demo-icon">{{ d.icon }}</span>
              <span class="fp-demo-badge" v-if="d.highlight">⭐ 创新</span>
            </div>
            <h4>{{ d.name }}</h4>
            <p>{{ d.desc }}</p>
            <span class="fp-demo-link">立即体验 →</span>
          </div>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="fp-footer">
      <p>邮游世界 · 数据结构课程设计最终验收 | 北京邮电大学 2025-2026</p>
      <p class="fp-footer-sub">Powered by Vue 3 + FastAPI + Trae AI · Vibecoding 开发模式</p>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import Navbar from '../components/Navbar.vue'

const router = useRouter()
const particleCanvas = ref(null)
const currentSection = ref('hero')

// ---- 粒子背景 ----
let animFrame = null

function initParticles() {
  const canvas = particleCanvas.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  const dpr = window.devicePixelRatio || 1

  function resize() {
    canvas.width = window.innerWidth * dpr
    canvas.height = window.innerHeight * dpr
    canvas.style.width = window.innerWidth + 'px'
    canvas.style.height = window.innerHeight + 'px'
    ctx.scale(dpr, dpr)
  }
  resize()
  window.addEventListener('resize', resize)

  const particles = Array.from({ length: 80 }, () => ({
    x: Math.random() * window.innerWidth,
    y: Math.random() * window.innerHeight,
    vx: (Math.random() - 0.5) * 0.6,
    vy: (Math.random() - 0.5) * 0.6,
    r: Math.random() * 1.5 + 0.5,
    alpha: Math.random() * 0.5 + 0.15
  }))

  function draw() {
    ctx.clearRect(0, 0, window.innerWidth, window.innerHeight)
    particles.forEach((p, i) => {
      p.x += p.vx
      p.y += p.vy
      if (p.x < 0) p.x = window.innerWidth
      if (p.x > window.innerWidth) p.x = 0
      if (p.y < 0) p.y = window.innerHeight
      if (p.y > window.innerHeight) p.y = 0

      // 连线
      for (let j = i + 1; j < particles.length; j++) {
        const dx = p.x - particles[j].x
        const dy = p.y - particles[j].y
        const dist = Math.sqrt(dx * dx + dy * dy)
        if (dist < 120) {
          ctx.beginPath()
          ctx.moveTo(p.x, p.y)
          ctx.lineTo(particles[j].x, particles[j].y)
          ctx.strokeStyle = `rgba(0, 212, 255, ${0.06 * (1 - dist / 120)})`
          ctx.lineWidth = 0.5
          ctx.stroke()
        }
      }

      ctx.beginPath()
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2)
      ctx.fillStyle = `rgba(0, 212, 255, ${p.alpha})`
      ctx.fill()
    })
    animFrame = requestAnimationFrame(draw)
  }
  draw()
}

// ---- 滚动监听 ----
function onScroll() {
  const sections = document.querySelectorAll('.fp-section')
  let current = 'hero'
  sections.forEach(sec => {
    const rect = sec.getBoundingClientRect()
    if (rect.top <= window.innerHeight * 0.4) {
      current = sec.id
    }
  })
  currentSection.value = current
}

// ---- 数据 ----
const navSections = [
  { id: 'hero', label: '首页' },
  { id: 'innovation', label: '创新' },
  { id: 'agent', label: '智能体' },
  { id: 'arch', label: '架构' },
  { id: 'algo', label: '算法' },
  { id: 'data', label: '数据' },
  { id: 'devmode', label: 'AI模式' },
  { id: 'reflect', label: '反思' },
  { id: 'demo', label: '演示' }
]

const innovations = [
  {
    icon: '🧠', tag: '核心创新',
    title: 'TBTI 16种旅行人格系统',
    desc: '20题心理测试 → 4维人格计算 → 16型低多边形SVG动画形象。人格匹配权重直接嵌入推荐排序算法，实现「千人千面」的智能推荐，已支持测试结果持久化与人格驱动力推荐联动。',
    tech: ['SVG动画', '人格算法', '推荐联动', '16型形象']
  },
  {
    icon: '�', tag: '核心创新',
    title: '3D数字地球旅行足迹',
    desc: '基于 Three.js 自研数字化赛博地球——自定义 WebGL Shader 实现赛博陆地着色、电子网格、夜景灯光、海洋镜面高光。城市星芒标记 + 真实边界线 + 全息信息面板，一键点击飞向城市，以沉浸式3D体验回望旅行足迹。',
    tech: ['Three.js', 'WebGL Shader', 'GeoJSON', '3D边界线']
  },
  {
    icon: '🎬', tag: '核心创新',
    title: 'AI 旅行 VLOG 一键成片',
    desc: 'AI 自动编写分镜脚本 → Seedance 图生视频/文生视频 API → FFmpeg 多片段拼接合成。行程照片可自动转为动漫风格旅行视频，支持实时进度追踪与历史 VLOG 管理，真正实现「一键生成旅行电影」。',
    tech: ['Seedance', '分镜脚本', 'FFmpeg拼接', '进度追踪']
  },
  {
    icon: '🎙', tag: 'AI驱动',
    title: 'AI 多风格语音导游',
    desc: 'DeepSeek 大模型生成个性化导游词 × 火山引擎 TTS 语音合成。支持「理性派」「感性派」「吃货派」三种风格，自动缓存加速重复访问，带给用户真正沉浸式AI音频导游体验。',
    tech: ['LLM生成', 'TTS合成', '3种风格', '智能缓存']
  },
  {
    icon: '📕', tag: 'AI驱动',
    title: '小红书智能行程导入',
    desc: '粘贴或输入小红书笔记内容 → LLM 自动解析目的地/天数/景点按天分配/美食推荐 → 别名映射模糊匹配数据库景点 → 一键创建结构化行程。解决传统手动创建行程的繁琐痛点。',
    tech: ['DeepSeek', 'NLP解析', '别名映射', '智能匹配']
  },
  {
    icon: '✨', tag: 'AI驱动',
    title: 'AIGC 日记动画生成',
    desc: '基于日记配图调用图生视频 API，自动生成 5-6 秒旅游动画嵌入日记。支持 H.265 视频压缩上传，日记内容 Gzip 无损压缩 + FTS5 全文检索——存储与检索的双重优化。',
    tech: ['AIGC动画', 'H.265压缩', 'Gzip压缩', 'FTS5搜索']
  },
  {
    icon: '📸', tag: '社交互动',
    title: '旅行相册与拍照点位',
    desc: '按行程分组的云端相册系统，支持时间轴/行程视图切换。独创「拍照点位」功能——用户可为景点上传最佳拍照位置（含样片+描述），帮助后来者找到绝佳取景角度，形成 UGC 拍照指南生态。',
    tech: ['云端相册', 'Photo Spot', 'UGC生态', '行程分组']
  },
  {
    icon: '🏫', tag: '导航创新',
    title: '室内外一体化导航',
    desc: '基于北邮主楼真实 3 层结构建模，支持大门→电梯→楼层的室内跨楼层导航 + 室外 Dijkstra 路径规划。采用图距离（非直线距离）计算设施可达性，完美契合课程加分要求。',
    tech: ['3层建模', '电梯导航', '图距离', '跨楼层']
  },
  {
    icon: '❤️', tag: '社交互动',
    title: '旅行收藏与人格社区',
    desc: '一键收藏心仪景点，个人收藏夹集中管理。旅行人格结果可视化展示 + 人格类型详情页，16种人格各配专属低多边形 SVG 动画形象，形成差异化人格社区氛围，增强用户粘性。',
    tech: ['收藏系统', '人格形象', 'SVG动画', '社区氛围']
  }
]

const agents = [
  {
    icon: '💻',
    name: '代码架构师',
    role: '技术开发助手',
    duties: ['必须先分析已有代码再给出方案', '帮助修复 Bug、优化算法性能', '基于现有风格给出开发建议', '输出：分析摘要→方案→代码→验证']
  },
  {
    icon: '📋',
    name: '项目协调官',
    role: '团队分工助手',
    duties: ['根据3人能力特长合理分配任务', '制定每周工作计划与里程碑', '识别任务依赖，避免阻塞', '输出：进度评估→分工表→优先级→预警']
  },
  {
    icon: '📚',
    name: '文档与进度追踪官',
    role: '内容创作与追踪',
    duties: ['撰写全部课程设计文档', '制作答辩PPT', '每周代码变更对比分析', 'GitHub提交统计与贡献分析']
  }
]

const algorithms = [
  {
    tag: '排序', name: 'TopK 堆排序', complexity: 'O(N log K)', space: 'O(K)',
    problem: '景点/美食/日记量大时需高效取前K个最优，不经过完全排序',
    reason: '维护大小为K的小顶堆/大顶堆，仅对K个结果排序。当K=10时几乎为O(N)，远优于全排序O(N log N)',
    location: 'core.py / diary_recommend.py / heapTopK.js'
  },
  {
    tag: '图论', name: 'Dijkstra 最短路径', complexity: 'O((V+E) log V)', space: 'O(V)',
    problem: '景区/校园内部导航，从起点到终点的最短时间/距离路径',
    reason: '优先队列优化版，支持道路类型过滤、拥挤度加权（真实速度=拥挤度×理想速度），天然适配路网建模',
    location: 'core.py → dijkstra()'
  },
  {
    tag: 'NP-hard', name: 'TSP 自适应求解器', complexity: 'O(n²·2ⁿ) / O(n²)', space: 'O(n·2ⁿ)',
    problem: '多点巡游场景，规划访问多个景点的最优顺序和路径',
    reason: 'n≤12使用Held-Karp DP精确解（保证全局最优），n>12使用贪心+2-opt启发式（兼顾效率），自适应策略业界先进',
    location: 'core.py → _choose_tsp_solver()'
  },
  {
    tag: '搜索', name: 'FTS5 BM25 全文检索', complexity: 'O(log N)', space: 'O(N)',
    problem: '日记数量大且变化快时的内容搜索，需高效相关性排序',
    reason: 'SQLite FTS5虚拟表+BM25算法，支持中文分词、高亮摘要。三阶段搜索：精确MATCH→拆字OR组合→LIKE降级',
    location: 'utils/diary_fts.py'
  },
  {
    tag: '搜索', name: 'Levenshtein 模糊匹配', complexity: 'O(n·m)', space: 'O(m)',
    problem: '用户输入可能存在错别字、拼音首字母、通配符等，需要容错搜索',
    reason: '支持完全匹配/前缀/子串/编辑距离四级优先级分层，结合中文子串匹配实现多字段联合搜索',
    location: 'core.py → fuzzy_search()'
  },
  {
    tag: '压缩', name: 'Gzip 无损压缩', complexity: 'O(N)', space: 'O(N)',
    problem: '长篇日记内容占用大量存储空间，需要高效压缩',
    reason: 'compresslevel=6平衡压缩率与速度。创新点：压缩前保留content_plain纯文本副本供FTS索引，解决压缩与检索矛盾',
    location: 'core.py → compress_diary()'
  },
  {
    tag: '推荐', name: '多因子加权融合', complexity: 'O(N)', space: 'O(1)',
    problem: '日记推荐需综合热度、评分、用户兴趣多个维度',
    reason: 'score=0.4×热度(log归一化)+0.3×评分(置信度调整)+0.3×兴趣(Jaccard相似度)，权重可配置支持A/B测试',
    location: 'diary_recommend.py → RecommendScorer'
  },
  {
    tag: '排序', name: '多路归并排序', complexity: 'O(N log N)', space: 'O(N)',
    problem: '多来源日记（FTS搜索+兴趣推荐+热门）合并去重排序',
    reason: '使用最小堆进行多路归并，同时去重，适合流式数据和增量更新场景',
    location: 'diary_recommend.py → MergeSorter'
  },
  {
    tag: '模拟', name: '哈希拥挤度模拟', complexity: 'O(E)', space: 'O(E)',
    problem: '最短时间策略需要差异化拥挤度，且同一条边每次计算结果需一致',
    reason: '基于Edge ID的MD5确定性哈希+道路类型范围约束+入口/食堂热点惩罚，确保可复现的差异化模拟',
    location: 'core.py → simulate_campus_congestion()'
  },
  {
    tag: '哈希', name: '标题SHA256精确查找', complexity: 'O(1)', space: 'O(1)',
    problem: '日记标题精确查询需高效，日记量大且变化快',
    reason: '预计算normalized_title + SHA256哈希，利用数据库哈希索引实现O(1)精确匹配',
    location: 'utils/diary_fts.py → search_by_exact_title()'
  }
]

const devSteps = [
  { title: '需求表达', desc: '用自然语言向 AI（Trae / Claude Code）描述功能需求、设计目标和现有代码背景' },
  { title: '代码分析', desc: 'AI 先读取项目已有代码（core.py、routers、前端组件），理解现有风格和命名规范' },
  { title: '方案输出', desc: 'AI 输出结构化修改方案：分析摘要 → 问题诊断 → 修改方案（含代码片段）→ 验证建议' },
  { title: '人工审查', desc: '开发者审查代码正确性、风格一致性、算法逻辑、边界条件处理' },
  { title: '迭代优化', desc: '发现问题后自然语言反馈，AI 修正，循环至满意。每次迭代通过 Git 提交' },
  { title: '测试验证', desc: '运行单元测试、集成测试，在真实环境验证功能可用性和性能指标' }
]

const demos = [
  { icon: '🌍', name: '3D地球足迹', desc: '赛博地球 · 城市星芒 · 全息面板', path: '/diary-library', highlight: true },
  { icon: '🧠', name: '旅行人格测试', desc: '20题发现你的16型旅行人格', path: '/personality-test', highlight: true },
  { icon: '🗺', name: '路线规划', desc: 'Dijkstra + TSP 智能路径规划', path: '/trips', highlight: true },
  { icon: '🤖', name: 'AI 旅行助手', desc: '多轮对话 · VLOG生成 · 语音导游', path: '/ai', highlight: true },
  { icon: '📸', name: '旅行相册', desc: '行程分组 · 拍照点位 · 时间轴', path: '/photos', highlight: false },
  { icon: '📒', name: '旅游日记', desc: 'FTS5搜索 + Gzip + AIGC动画', path: '/diary', highlight: false },
  { icon: '🍜', name: '美食推荐', desc: '堆排序 TopK + 多字段模糊搜索', path: '/food', highlight: false },
  { icon: '🏫', name: '室内导航', desc: '北邮主楼3层 · 跨楼层导航', path: '/indoor', highlight: true },
  { icon: '📍', name: '景点推荐', desc: '人格驱动的个性化排序推荐', path: '/spot-recommend', highlight: false },
  { icon: '📕', name: '小红书导入', desc: 'LLM智能解析 · 一键创建', path: '/create-trip', highlight: true },
  { icon: '❤️', name: '我的收藏', desc: '景点收藏 · 人格形象展示', path: '/collection', highlight: false },
  { icon: '🔍', name: '场所查询', desc: '图距离设施查询 + 类别过滤', path: '/internal-nav', highlight: false }
]

onMounted(() => {
  nextTick(() => initParticles())
  window.addEventListener('scroll', onScroll, { passive: true })
})

onUnmounted(() => {
  cancelAnimationFrame(animFrame)
  window.removeEventListener('scroll', onScroll)
})
</script>

<style scoped>
/* ============ 全局 ============ */
.final-page {
  background: #070b16;
  color: #e8ecf1;
  font-family: 'Noto Sans SC', -apple-system, sans-serif;
  overflow-x: hidden;
}

.particle-canvas {
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;
}

/* ============ 侧边导航 ============ */
.fp-nav {
  position: fixed;
  right: 28px;
  top: 50%;
  transform: translateY(-50%);
  z-index: 100;
  display: flex;
  flex-direction: column;
  gap: 18px;
}
.fp-nav a {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  color: rgba(255,255,255,0.4);
  transition: all 0.3s ease;
  justify-content: flex-end;
}
.fp-nav a:hover,
.fp-nav a.active {
  color: #00d4ff;
}
.nav-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
  transition: all 0.3s ease;
}
.fp-nav a.active .nav-dot {
  width: 10px;
  height: 10px;
  box-shadow: 0 0 10px #00d4ff;
}
.nav-label {
  font-size: 11px;
  letter-spacing: 0.1em;
  opacity: 0;
  transform: translateX(10px);
  transition: all 0.3s ease;
  white-space: nowrap;
}
.fp-nav a:hover .nav-label,
.fp-nav a.active .nav-label {
  opacity: 1;
  transform: translateX(0);
}

/* ============ 通用 Section ============ */
.fp-section {
  position: relative;
  z-index: 1;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 100px 60px;
}
.fp-dark { background: linear-gradient(180deg, #070b16, #0d1225); }
.fp-dark-alt { background: linear-gradient(180deg, #0d1225, #070b16); }

.fp-section-inner {
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
}

.fp-section-head {
  text-align: center;
  margin-bottom: 64px;
}
.fp-section-num {
  display: inline-block;
  font-size: 13px;
  font-weight: 700;
  color: #00d4ff;
  letter-spacing: 0.15em;
  margin-bottom: 12px;
  padding: 4px 14px;
  border: 1px solid rgba(0,212,255,0.25);
  border-radius: 20px;
}
.fp-section-head h2 {
  font-size: 42px;
  font-weight: 800;
  margin: 12px 0 14px;
  color: #fff;
}
.accent { color: #00d4ff; }
.fp-section-head p {
  font-size: 17px;
  color: rgba(255,255,255,0.55);
  max-width: 700px;
  margin: 0 auto;
  line-height: 1.7;
}

/* ============ S1: Hero ============ */
.fp-hero {
  flex-direction: column;
  text-align: center;
  padding-top: 140px;
  min-height: 100vh;
  position: relative;
}
.fp-hero-bg {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse at 50% 0%, rgba(0,212,255,0.12) 0%, transparent 60%),
    radial-gradient(ellipse at 80% 80%, rgba(123,44,191,0.08) 0%, transparent 50%);
}
.fp-hero-content { position: relative; z-index: 1; }
.fp-hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 8px 22px;
  border-radius: 30px;
  background: rgba(0,212,255,0.08);
  border: 1px solid rgba(0,212,255,0.3);
  font-size: 14px;
  color: #00d4ff;
  letter-spacing: 0.1em;
  margin-bottom: 36px;
}
.badge-pulse {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #00d4ff;
  animation: pulse 2s ease-in-out infinite;
}
@keyframes pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(0,212,255,0.6); }
  50% { box-shadow: 0 0 0 12px rgba(0,212,255,0); }
}
.fp-hero-title {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 28px;
}
.title-line {
  font-size: 72px;
  font-weight: 900;
  background: linear-gradient(135deg, #fff 0%, #00d4ff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  line-height: 1.1;
}
.title-sub {
  font-size: 28px;
  font-weight: 300;
  color: rgba(255,255,255,0.7);
  letter-spacing: 0.15em;
}
.fp-hero-desc {
  font-size: 17px;
  color: rgba(255,255,255,0.6);
  line-height: 2;
  margin-bottom: 40px;
  max-width: 700px;
  margin-left: auto;
  margin-right: auto;
}
.fp-hero-desc em {
  color: #00d4ff;
  font-style: normal;
  font-weight: 700;
}
.fp-hero-stats {
  display: flex;
  justify-content: center;
  gap: 48px;
  margin-bottom: 44px;
  flex-wrap: wrap;
}
.hero-stat {
  text-align: center;
}
.stat-num {
  display: block;
  font-size: 40px;
  font-weight: 900;
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.stat-lbl {
  font-size: 13px;
  color: rgba(255,255,255,0.45);
  margin-top: 4px;
  display: block;
}
.fp-hero-actions {
  display: flex;
  justify-content: center;
  gap: 18px;
  flex-wrap: wrap;
}
.fp-btn-primary {
  padding: 16px 40px;
  border-radius: 30px;
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  color: #fff;
  font-size: 16px;
  font-weight: 700;
  text-decoration: none;
  transition: all 0.3s ease;
  border: none;
  cursor: pointer;
}
.fp-btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(0,212,255,0.4);
}
.fp-btn-ghost {
  padding: 16px 36px;
  border-radius: 30px;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.2);
  color: #fff;
  font-size: 16px;
  text-decoration: none;
  transition: all 0.3s ease;
}
.fp-btn-ghost:hover {
  border-color: rgba(0,212,255,0.4);
  background: rgba(0,212,255,0.08);
}
.fp-scroll-hint {
  position: absolute;
  bottom: 40px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: rgba(255,255,255,0.3);
  font-size: 12px;
  letter-spacing: 0.1em;
  animation: float 2s ease-in-out infinite;
}
@keyframes float {
  0%, 100% { transform: translateX(-50%) translateY(0); }
  50% { transform: translateX(-50%) translateY(-8px); }
}

/* ============ S2: 创新亮点 ============ */
.fp-innovation-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}
.fp-innovation-card {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 20px;
  padding: 32px 28px;
  transition: all 0.4s ease;
  position: relative;
  overflow: hidden;
}
.fp-innovation-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, #00d4ff, #7b2cbf, transparent);
  opacity: 0;
  transition: opacity 0.4s ease;
}
.fp-innovation-card:hover {
  border-color: rgba(0,212,255,0.25);
  transform: translateY(-6px);
  box-shadow: 0 20px 60px rgba(0,0,0,0.4);
}
.fp-innovation-card:hover::before { opacity: 1; }
.fp-inn-icon { font-size: 42px; margin-bottom: 14px; }
.fp-inn-tag {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 6px;
  background: rgba(0,212,255,0.1);
  color: #00d4ff;
  font-size: 11px;
  font-weight: 600;
  margin-bottom: 12px;
}
.fp-innovation-card h3 {
  font-size: 19px;
  font-weight: 700;
  margin-bottom: 10px;
  color: #fff;
}
.fp-innovation-card p {
  font-size: 14px;
  color: rgba(255,255,255,0.6);
  line-height: 1.75;
  margin-bottom: 18px;
}
.fp-inn-tech {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.fp-inn-tech span {
  padding: 4px 10px;
  border-radius: 6px;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.08);
  font-size: 12px;
  color: rgba(255,255,255,0.55);
}

/* ============ S3: 智能体 ============ */
.fp-env-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 24px;
  padding: 32px 40px;
  background: rgba(0,212,255,0.04);
  border: 1px solid rgba(0,212,255,0.1);
  border-radius: 18px;
  margin-bottom: 48px;
  flex-wrap: wrap;
}
.fp-env-item {
  display: flex;
  align-items: center;
  gap: 14px;
}
.fp-env-icon { font-size: 28px; }
.fp-env-label { font-size: 11px; color: rgba(255,255,255,0.4); letter-spacing: 0.1em; margin-bottom: 2px; }
.fp-env-val { font-size: 16px; font-weight: 700; color: #00d4ff; }
.fp-env-div { width: 1px; height: 44px; background: rgba(255,255,255,0.1); }

.fp-agent-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  margin-bottom: 32px;
}
.fp-agent-card {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 18px;
  padding: 40px 28px 28px;
  position: relative;
  transition: all 0.3s ease;
}
.fp-agent-card:hover {
  border-color: rgba(0,212,255,0.25);
  transform: translateY(-4px);
}
.fp-agent-num {
  position: absolute;
  top: 16px;
  right: 20px;
  font-size: 56px;
  font-weight: 900;
  color: rgba(0,212,255,0.06);
  line-height: 1;
}
.fp-agent-avatar { font-size: 42px; margin-bottom: 14px; }
.fp-agent-card h3 { font-size: 20px; font-weight: 700; margin-bottom: 6px; color: #fff; }
.fp-agent-role { color: #00d4ff; font-size: 13px; margin-bottom: 18px; font-weight: 600; }
.fp-agent-card ul {
  list-style: none;
  padding: 0;
  margin: 0;
}
.fp-agent-card li {
  padding: 8px 0;
  padding-left: 16px;
  position: relative;
  font-size: 13px;
  color: rgba(255,255,255,0.6);
  border-bottom: 1px solid rgba(255,255,255,0.04);
  line-height: 1.6;
}
.fp-agent-card li::before {
  content: '›';
  position: absolute;
  left: 0;
  color: #00d4ff;
  font-weight: 700;
}

.fp-flow-card {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 18px;
  padding: 32px;
  text-align: center;
}
.fp-flow-title { font-size: 16px; font-weight: 700; color: rgba(255,255,255,0.7); margin-bottom: 28px; }
.fp-flow {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  flex-wrap: wrap;
}
.fp-flow-node {
  padding: 16px 24px;
  border-radius: 14px;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.08);
  font-weight: 600;
  font-size: 14px;
  transition: all 0.3s ease;
}
.fp-flow-node.active {
  border-color: rgba(0,212,255,0.3);
  background: rgba(0,212,255,0.06);
}
.fp-flow-node small { display: block; margin-top: 3px; font-weight: 400; font-size: 11px; color: rgba(255,255,255,0.4); }
.fp-flow-arrow { color: #00d4ff; font-size: 20px; font-weight: 700; }

/* ============ S4: 架构 ============ */
.fp-arch {
  display: flex;
  flex-direction: column;
  gap: 0;
}
.fp-arch-layer {
  display: flex;
  align-items: flex-start;
  gap: 24px;
  padding: 24px 28px;
  border-radius: 16px;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.06);
  border-left: 4px solid transparent;
}
.fp-arch-layer.frontend { border-left-color: #00d4ff; }
.fp-arch-layer.api { border-left-color: #7b2cbf; }
.fp-arch-layer.logic { border-left-color: #00ff88; }
.fp-arch-layer.algo { border-left-color: #ff6b6b; }
.fp-arch-layer.data { border-left-color: #ffb347; }
.fp-arch-lbl {
  min-width: 100px;
  font-weight: 700;
  font-size: 14px;
  letter-spacing: 0.08em;
  padding-top: 2px;
}
.frontend .fp-arch-lbl { color: #00d4ff; }
.api .fp-arch-lbl { color: #a855f7; }
.logic .fp-arch-lbl { color: #00ff88; }
.algo .fp-arch-lbl { color: #ff6b6b; }
.data .fp-arch-lbl { color: #ffb347; }
.fp-arch-items {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  flex: 1;
}
.fp-arch-items span {
  padding: 8px 16px;
  border-radius: 10px;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.08);
  font-size: 13px;
  color: rgba(255,255,255,0.7);
}
.fp-arch-items.small span { font-size: 12px; padding: 6px 12px; }
.fp-arch-items span small { display: block; font-size: 10px; color: rgba(255,255,255,0.35); margin-top: 2px; }
.fp-arch-conn {
  text-align: center;
  color: rgba(255,255,255,0.2);
  font-size: 18px;
  padding: 6px 0;
}
.fp-arch-conn::after { content: '↓'; }

/* ============ S5: 算法 ============ */
.fp-algo-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}
.fp-algo-card {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 16px;
  padding: 28px;
  transition: all 0.3s ease;
}
.fp-algo-card:hover {
  border-color: rgba(0,212,255,0.2);
  box-shadow: 0 8px 30px rgba(0,0,0,0.3);
}
.fp-algo-tag {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 6px;
  background: rgba(0,212,255,0.1);
  color: #00d4ff;
  font-size: 11px;
  font-weight: 600;
  margin-bottom: 10px;
}
.fp-algo-card h3 {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 8px;
  color: #fff;
}
.fp-algo-meta {
  display: flex;
  gap: 12px;
  margin-bottom: 14px;
}
.fp-algo-complexity {
  padding: 4px 10px;
  border-radius: 6px;
  background: rgba(123,44,191,0.12);
  border: 1px solid rgba(123,44,191,0.25);
  color: #a855f7;
  font-size: 12px;
  font-family: 'Courier New', monospace;
  font-weight: 700;
}
.fp-algo-space {
  padding: 4px 10px;
  border-radius: 6px;
  background: rgba(0,255,136,0.1);
  border: 1px solid rgba(0,255,136,0.2);
  color: #00ff88;
  font-size: 12px;
  font-family: 'Courier New', monospace;
  font-weight: 700;
}
.fp-algo-problem {
  font-size: 13px;
  color: rgba(255,255,255,0.55);
  line-height: 1.7;
  margin-bottom: 14px;
}
.fp-algo-reason {
  padding: 14px;
  border-radius: 10px;
  background: rgba(255,255,255,0.03);
  margin-bottom: 12px;
}
.reason-label {
  font-size: 11px;
  color: rgba(255,255,255,0.35);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-bottom: 6px;
  display: block;
}
.fp-algo-reason p {
  font-size: 13px;
  color: rgba(255,255,255,0.65);
  line-height: 1.7;
}
.fp-algo-location {
  font-size: 11px;
  color: rgba(255,255,255,0.3);
  font-family: 'Courier New', monospace;
  padding: 6px 10px;
  border-radius: 6px;
  background: rgba(255,255,255,0.03);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* ============ S6: 数据 ============ */
.fp-data-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}
.fp-data-card {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 20px;
  padding: 36px 28px;
  text-align: center;
  transition: all 0.3s ease;
}
.fp-data-card:hover {
  border-color: rgba(0,212,255,0.2);
  transform: translateY(-4px);
}
.fp-data-card.highlight {
  border-color: rgba(0,212,255,0.2);
  background: linear-gradient(135deg, rgba(0,212,255,0.05), rgba(123,44,191,0.05));
}
.fp-data-icon { font-size: 36px; margin-bottom: 12px; }
.fp-data-num {
  font-size: 42px;
  font-weight: 900;
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 6px;
}
.fp-data-label { font-size: 16px; font-weight: 700; color: #fff; margin-bottom: 8px; }
.fp-data-req {
  font-size: 12px;
  color: rgba(255,255,255,0.4);
}

/* ============ S7: AI 开发模式 ============ */
.fp-dev-flow {
  display: flex;
  gap: 0;
  margin-bottom: 48px;
  flex-wrap: wrap;
}
.fp-dev-step {
  flex: 1;
  min-width: 150px;
  text-align: center;
  padding: 0 16px 40px;
  position: relative;
}
.fp-dev-step::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 16px;
  right: 16px;
  height: 2px;
  background: linear-gradient(90deg, #00d4ff, #7b2cbf);
  border-radius: 1px;
}
.fp-dev-step-num {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: 800;
  color: #fff;
  margin: 0 auto 18px;
}
.fp-dev-step-content h4 {
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 8px;
  color: #fff;
}
.fp-dev-step-content p {
  font-size: 13px;
  color: rgba(255,255,255,0.5);
  line-height: 1.7;
}

.fp-role-card {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 18px;
  padding: 36px;
  text-align: center;
}
.fp-role-card h3 { font-size: 20px; font-weight: 700; margin-bottom: 28px; color: #fff; }
.fp-role-row { display: flex; align-items: center; justify-content: center; gap: 20px; flex-wrap: wrap; }
.fp-role-box {
  flex: 1;
  min-width: 280px;
  max-width: 400px;
  padding: 28px;
  border-radius: 16px;
  border: 1px solid rgba(255,255,255,0.08);
}
.fp-role-box.ai { background: rgba(0,212,255,0.04); border-color: rgba(0,212,255,0.15); }
.fp-role-box.human { background: rgba(123,44,191,0.04); border-color: rgba(123,44,191,0.15); }
.fp-role-icon { font-size: 36px; margin-bottom: 12px; }
.fp-role-box h4 { font-size: 18px; font-weight: 700; margin-bottom: 10px; color: #fff; }
.fp-role-box p { font-size: 14px; color: rgba(255,255,255,0.55); line-height: 1.7; }
.fp-role-vs { font-size: 28px; color: #00d4ff; font-weight: 700; }

/* ============ S8: 反思 ============ */
.fp-reflect-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}
.fp-reflect-card {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 18px;
  padding: 32px 28px;
  border-left: 4px solid transparent;
}
.fp-reflect-card.good { border-left-color: #00ff88; }
.fp-reflect-card.warn { border-left-color: #ffb347; }
.fp-reflect-card.insight { border-left-color: #00d4ff; }
.fp-reflect-card h3 { font-size: 17px; font-weight: 700; margin-bottom: 18px; color: #fff; }
.fp-reflect-card ul { list-style: none; padding: 0; margin: 0; }
.fp-reflect-card li {
  padding: 8px 0;
  padding-left: 14px;
  position: relative;
  font-size: 13px;
  color: rgba(255,255,255,0.6);
  line-height: 1.7;
  border-bottom: 1px solid rgba(255,255,255,0.04);
}
.fp-reflect-card li::before {
  content: '';
  position: absolute;
  left: 0;
  top: 14px;
  width: 5px;
  height: 5px;
  border-radius: 50%;
}
.good li::before { background: #00ff88; }
.warn li::before { background: #ffb347; }
.insight li::before { background: #00d4ff; }

/* ============ S9: 演示入口 ============ */
.fp-demo-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}
.fp-demo-card {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 18px;
  padding: 32px 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.35s ease;
  position: relative;
  overflow: hidden;
}
.fp-demo-card::after {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 18px;
  background: radial-gradient(circle at var(--mx, 50%) var(--my, 50%), rgba(0,212,255,0.12) 0%, transparent 60%);
  opacity: 0;
  transition: opacity 0.35s ease;
}
.fp-demo-card:hover {
  transform: translateY(-6px);
  border-color: rgba(0,212,255,0.35);
  box-shadow: 0 18px 50px rgba(0,212,255,0.12);
}
.fp-demo-card:hover::after { opacity: 1; }
.fp-demo-top {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 12px;
  margin-bottom: 14px;
}
.fp-demo-icon { font-size: 38px; }
.fp-demo-badge {
  padding: 3px 10px;
  border-radius: 10px;
  background: linear-gradient(135deg, rgba(0,212,255,0.2), rgba(123,44,191,0.2));
  color: #00d4ff;
  font-size: 11px;
  font-weight: 600;
}
.fp-demo-card h4 {
  font-size: 17px;
  font-weight: 700;
  margin-bottom: 8px;
  color: #fff;
}
.fp-demo-card p {
  font-size: 13px;
  color: rgba(255,255,255,0.5);
  line-height: 1.6;
  margin-bottom: 16px;
}
.fp-demo-link { color: #00d4ff; font-size: 14px; font-weight: 600; }

/* ============ Footer ============ */
.fp-footer {
  position: relative;
  z-index: 1;
  text-align: center;
  padding: 48px 24px;
  background: #070b16;
  border-top: 1px solid rgba(255,255,255,0.05);
}
.fp-footer p { font-size: 14px; color: rgba(255,255,255,0.4); }
.fp-footer-sub { font-size: 12px !important; margin-top: 6px; color: rgba(255,255,255,0.25) !important; }

/* ============ 响应式 ============ */
@media (max-width: 1024px) {
  .fp-nav { display: none; }
  .fp-section { padding: 80px 32px; }
  .fp-hero { padding-top: 110px; }
  .title-line { font-size: 48px; }
  .title-sub { font-size: 22px; }
  .fp-section-head h2 { font-size: 32px; }
  .fp-innovation-grid,
  .fp-agent-grid,
  .fp-data-grid,
  .fp-reflect-grid,
  .fp-demo-grid { grid-template-columns: repeat(2, 1fr); }
  .fp-algo-grid { grid-template-columns: 1fr; }
  .fp-dev-flow { flex-direction: column; }
  .fp-dev-step { min-width: 100%; padding-bottom: 32px; }
  .fp-hero-stats { gap: 28px; }
  .stat-num { font-size: 30px; }
}

@media (max-width: 640px) {
  .fp-section { padding: 60px 18px; }
  .fp-hero { padding-top: 100px; }
  .title-line { font-size: 36px; }
  .title-sub { font-size: 18px; }
  .fp-hero-desc { font-size: 14px; }
  .fp-innovation-grid,
  .fp-agent-grid,
  .fp-data-grid,
  .fp-reflect-grid,
  .fp-demo-grid { grid-template-columns: 1fr; }
  .fp-env-bar { flex-direction: column; gap: 14px; padding: 24px; }
  .fp-env-div { width: 100%; height: 1px; }
  .fp-flow { gap: 8px; }
  .fp-flow-node { padding: 12px 16px; font-size: 12px; }
  .fp-flow-arrow { display: none; }
  .fp-hero-stats { gap: 20px; }
}
</style>
