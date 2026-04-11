<template>
  <div class="presentation-page">
    <div class="hero-background">
      <img :src="backgroundImage" alt="presentation background" class="bg-image" />
      <div class="bg-overlay"></div>
      <div class="grid-overlay"></div>
    </div>

    <Navbar />

    <main class="presentation-content">
      <section class="hero-section">
        <div class="hero-text">
          <div class="hero-tags">
            <span class="tech-tag">5-10分钟讲解</span>
            <span class="tech-tag">龙虾 + 大模型 + 智能体</span>
            <span class="tech-tag">旅游 + 内部导航</span>
          </div>
          <h1>智慧旅游与内部导航系统设计方案</h1>
          <p class="hero-desc">
            以真实地图、智能规划和多目标路线优化为核心，讲清我们如何从需求分析到架构落地，完成一个可演示、可交互、可扩展的系统。
          </p>
          <div class="hero-actions">
            <button class="tech-button" @click="scrollToSection('needs')">开始讲解</button>
            <button class="ghost-button" @click="scrollToSection('summary')">查看演示入口</button>
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

      <section id="needs" class="content-section">
        <div class="section-header">
          <span class="section-kicker">01 / 系统创新需求</span>
          <h2>为什么这个系统值得做</h2>
          <p>不是只做“景点推荐”，而是把出行前规划、游玩中导航和多目标优化串成一条完整链路。</p>
        </div>
        <div class="grid four-cols">
          <article v-for="item in needs" :key="item.title" class="tech-card info-card">
            <div class="card-icon">{{ item.icon }}</div>
            <h3>{{ item.title }}</h3>
            <p>{{ item.desc }}</p>
          </article>
        </div>
      </section>

      <section class="content-section">
        <div class="section-header">
          <span class="section-kicker">02 / 协同开发方式</span>
          <h2>龙虾、大模型、智能体如何分工</h2>
          <p>把“想法形成”“内容组织”“代码落地”拆开，让每一类能力都发挥到最合适的位置。</p>
        </div>

        <div class="workflow-grid">
          <article v-for="role in collaboration" :key="role.title" class="tech-card workflow-card">
            <div class="workflow-head">
              <span class="workflow-icon">{{ role.icon }}</span>
              <h3>{{ role.title }}</h3>
            </div>
            <p class="workflow-summary">{{ role.summary }}</p>
            <ul>
              <li v-for="point in role.points" :key="point">{{ point }}</li>
            </ul>
          </article>
        </div>

        <div class="flow-strip tech-card">
          <div v-for="(step, index) in flowSteps" :key="step.title" class="flow-step">
            <div class="flow-node">{{ index + 1 }}</div>
            <div>
              <div class="flow-title">{{ step.title }}</div>
              <div class="flow-desc">{{ step.desc }}</div>
            </div>
          </div>
        </div>
      </section>

      <section class="content-section architecture-section">
        <div class="section-header">
          <span class="section-kicker">03 / 整体技术架构</span>
          <h2>前后端分层设计与业务链路打通</h2>
          <p>我们不是单独做一个前端页面或一个算法 demo，而是围绕“探索发现 → 行程生成 → 路线优化 → 内部导航 → 旅行日记沉淀”构建完整的课程项目闭环。</p>
        </div>

        <div class="architecture-overview-grid">
          <div class="tech-card overview-card">
            <h3>前端架构</h3>
            <div class="overview-list">
              <div v-for="item in frontendArchitecture" :key="item.title" class="overview-item">
                <strong>{{ item.title }}</strong>
                <p>{{ item.desc }}</p>
                <span class="overview-file">{{ item.file }}</span>
              </div>
            </div>
          </div>

          <div class="tech-card overview-card">
            <h3>后端架构</h3>
            <div class="overview-list">
              <div v-for="item in backendArchitecture" :key="item.title" class="overview-item">
                <strong>{{ item.title }}</strong>
                <p>{{ item.desc }}</p>
                <span class="overview-file">{{ item.file }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="architecture-layout">
          <div class="architecture-left tech-card">
            <h3>系统分层</h3>
            <div class="architecture-stack">
              <div v-for="layer in architecture" :key="layer.title" class="arch-layer">
                <div class="arch-title-row">
                  <span class="arch-title">{{ layer.title }}</span>
                  <span class="arch-file">{{ layer.file }}</span>
                </div>
                <p>{{ layer.desc }}</p>
              </div>
            </div>
          </div>

          <div class="architecture-right">
            <div class="tech-card architecture-card large">
              <h3>业务闭环亮点</h3>
              <div class="capability-list">
                <div v-for="item in capabilities" :key="item.title" class="capability-item">
                  <span>{{ item.icon }}</span>
                  <div>
                    <strong>{{ item.title }}</strong>
                    <p>{{ item.desc }}</p>
                  </div>
                </div>
              </div>
            </div>
            <div class="mini-grid">
              <div class="tech-card mini-card" v-for="item in architectureNotes" :key="item.title">
                <h4>{{ item.title }}</h4>
                <p>{{ item.desc }}</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section class="content-section">
        <div class="section-header">
          <span class="section-kicker">04 / 功能打通亮点</span>
          <h2>旅游规划、路径导航、AI助手与日记系统形成闭环</h2>
          <p>相比单点功能，我们更强调系统之间的联动：从用户提出需求，到生成行程、优化路线、导航执行，再到游后内容沉淀，形成完整产品链路。</p>
        </div>

        <div class="linkage-grid">
          <article v-for="item in linkageHighlights" :key="item.title" class="tech-card linkage-card">
            <div class="card-icon">{{ item.icon }}</div>
            <h3>{{ item.title }}</h3>
            <p>{{ item.desc }}</p>
          </article>
        </div>

        <div class="tech-card journey-card">
          <h3>用户完整旅程</h3>
          <div class="journey-steps">
            <div v-for="(step, index) in journeySteps" :key="step.title" class="journey-step">
              <div class="journey-index">{{ index + 1 }}</div>
              <div>
                <div class="journey-title">{{ step.title }}</div>
                <div class="journey-desc">{{ step.desc }}</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section class="content-section">
        <div class="section-header">
          <span class="section-kicker">05 / 算法选择</span>
          <h2>算法不是堆砌，而是和业务场景一一对应</h2>
          <p>每种算法都对应一个明确问题：推荐效率、单目标寻路、多目标游览优化。</p>
        </div>

        <div class="grid three-cols">
          <article v-for="algo in algorithms" :key="algo.name" class="tech-card algorithm-card">
            <div class="algo-top">
              <span class="algo-badge">{{ algo.tag }}</span>
              <span class="algo-complexity">{{ algo.complexity }}</span>
            </div>
            <h3>{{ algo.name }}</h3>
            <div class="algo-block">
              <span class="algo-label">解决问题</span>
              <p>{{ algo.problem }}</p>
            </div>
            <div class="algo-block">
              <span class="algo-label">为什么选它</span>
              <p>{{ algo.reason }}</p>
            </div>
            <div class="algo-block">
              <span class="algo-label">落地位置</span>
              <p>{{ algo.file }}</p>
            </div>
          </article>
        </div>
      </section>

      <section class="content-section">
        <div class="section-header">
          <span class="section-kicker">06 / 开发中的问题与解决方案</span>
          <h2>以问题为导向推动系统落地</h2>
          <p>在项目开发过程中，我们不仅关注“AI 能不能生成代码”，更关注“AI 生成的内容是否可控、可解释、可维护”。因此我们把问题拆开，再逐项设计解决方案。</p>
        </div>

        <div class="issues-list detailed">
          <article v-for="issue in issues" :key="issue.title" class="tech-card issue-card detailed-issue-card">
            <div class="issue-head">
              <span class="issue-tag">{{ issue.tag }}</span>
              <h3>{{ issue.title }}</h3>
            </div>
            <p class="issue-problem"><strong>问题现象：</strong>{{ issue.problem }}</p>
            <p class="issue-impact"><strong>带来的后果：</strong>{{ issue.impact }}</p>
            <div class="solution-block">
              <strong>解决方案：</strong>
              <ul>
                <li v-for="solution in issue.solutions" :key="solution">{{ solution }}</li>
              </ul>
            </div>
          </article>
        </div>
      </section>

      <section id="summary" class="content-section summary-section">
        <div class="section-header">
          <span class="section-kicker">07 / 最终成果与课程价值</span>
          <h2>课程项目最终展示版总结</h2>
          <p>最终我们完成的不是单一页面或单个算法实验，而是一个以智慧旅游为核心、以真实导航为特色、以 AI 协同开发为方法的综合课程项目。</p>
        </div>

        <div class="summary-grid final-version">
          <div class="tech-card summary-card">
            <h3>最终成果</h3>
            <div class="timeline">
              <div v-for="item in results" :key="item.title" class="timeline-item">
                <span class="timeline-dot"></span>
                <div>
                  <strong>{{ item.title }}</strong>
                  <p>{{ item.desc }}</p>
                </div>
              </div>
            </div>
          </div>

          <div class="tech-card demo-card">
            <h3>课程项目价值</h3>
            <div class="course-value-list">
              <div v-for="item in courseValues" :key="item.title" class="course-value-item">
                <strong>{{ item.title }}</strong>
                <p>{{ item.desc }}</p>
              </div>
            </div>
            <div class="demo-actions">
              <button class="tech-button" @click="router.push('/explore')">探索发现</button>
              <button class="ghost-button" @click="router.push('/ai')">AI助手</button>
              <button class="ghost-button" @click="router.push('/diary')">旅行日记</button>
              <button class="ghost-button" @click="router.push('/internal-nav?id=9')">清华内部导航</button>
            </div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import Navbar from '../components/Navbar.vue'

const router = useRouter()

const backgroundImage = '/images/background/test01.jpg'

const storyline = [
  { title: '系统创新需求', desc: '为什么必须把旅游规划和内部导航整合起来' },
  { title: '协同开发方式', desc: '龙虾、大模型、智能体分别负责什么' },
  { title: '整体架构与算法', desc: '前后端、地图与算法层如何联动' },
  { title: '难点与成果', desc: '遇到了什么问题，最后完成了哪些能力' }
]

const needs = [
  { icon: '🧭', title: '路线要真实可走', desc: '不能只连景点坐标，必须基于真实道路与内部路网做路径规划。' },
  { icon: '🎯', title: '游览要支持多目标', desc: '用户不是只去一个点，而是希望一次规划多个建筑、设施或景点。' },
  { icon: '🚲', title: '交通方式要可切换', desc: '步行、骑行、电瓶车等模式会改变可达边和最优路径。' },
  { icon: '🤖', title: '方案要能快速迭代', desc: '需要借助大模型与智能体，把需求整理、页面表达和代码实现打通。' }
]

const collaboration = [
  {
    icon: '🦞',
    title: '龙虾',
    summary: '负责把需求说清楚、结构讲清楚。',
    points: ['梳理讲解逻辑与页面节奏', '整理功能卖点与展示重点', '把技术内容转成适合汇报的表达']
  },
  {
    icon: '🧠',
    title: '大模型',
    summary: '负责快速生成内容草稿与设计思路。',
    points: ['生成架构说明与方案文案', '对算法选择给出讲解框架', '归纳开发问题与解决思路']
  },
  {
    icon: '🛠️',
    title: '智能体',
    summary: '负责进入代码库，把方案落实成真实页面。',
    points: ['读取现有前后端实现', '新增讲解页并接入路由', '复用已有页面风格并完成验证']
  }
]

const flowSteps = [
  { title: '需求拆解', desc: '先确定讲什么、给谁讲、讲多久。' },
  { title: '内容组织', desc: '把创新点、架构、算法和问题整理成 section。' },
  { title: '代码落地', desc: '在现有 Vue 项目中新增单页滚动展示页。' },
  { title: '功能联动', desc: '从讲解页直接跳到 Explore、AI、InternalNav 进行演示。' }
]

const architecture = [
  { title: '前端入口与路由层', file: 'frontend/src/main.js', desc: '负责应用启动、页面注册、路由守卫与公开页面控制。' },
  { title: '探索与内容展示层', file: 'frontend/src/views/Explore.vue', desc: '负责景点、美食与城市内容的发现式浏览。' },
  { title: 'AI 行程交互层', file: 'frontend/src/views/AIAssistant.vue', desc: '负责自然语言交互、行程草案生成与会话内行程承接。' },
  { title: '行程规划与路线层', file: 'frontend/src/views/TripDetail.vue', desc: '负责景点排序、地图联动、交通方式切换与路径优化。' },
  { title: '内部导航层', file: 'frontend/src/views/InternalNav.vue', desc: '负责校园/景区内部路网的节点选择、路径计算与可视化。' },
  { title: '日记沉淀层', file: 'frontend/src/views/Diary.vue', desc: '负责游后内容生成、分类管理和旅行数据沉淀。' },
  { title: '接口聚合层', file: 'backend/main.py', desc: '统一挂载景点、行程、路线、日记、AI 等业务接口。' },
  { title: '算法引擎层', file: 'backend/algorithms/core.py', desc: '负责 Top-K 排序、Dijkstra 寻路、TSP 路线优化等核心计算。' }
]

const frontendArchitecture = [
  { title: 'Vue 3 + Vite 单页应用', desc: '采用 Vue 3 组织页面，Vite 提供快速开发和打包能力，适合课程项目快速迭代。', file: 'frontend/src/main.js' },
  { title: 'Vue Router 路由组织', desc: '把首页、探索、AI 助手、行程详情、内部导航、日记等功能页统一纳入单页路由管理。', file: 'frontend/src/main.js' },
  { title: 'Pinia 状态管理', desc: '用于前端状态组织，便于后续扩展跨页面数据共享。', file: 'frontend/src/main.js' },
  { title: 'Element Plus 组件体系', desc: '作为现成组件基础，支持弹窗、按钮、输入框等交互控件快速搭建。', file: 'frontend/package.json' },
  { title: '高德地图可视化接入', desc: '通过地图组件承载外部路线和内部导航结果，提升系统的空间表达能力。', file: 'frontend/src/views/TripDetail.vue' }
]

const backendArchitecture = [
  { title: 'FastAPI 后端服务', desc: '使用 FastAPI 组织 REST API，开发效率高，适合快速验证智慧旅游场景。', file: 'backend/main.py' },
  { title: '多业务 Router 拆分', desc: '按 spots、trips、route、diary、ai 等模块拆分接口，保证结构清晰。', file: 'backend/main.py' },
  { title: 'SQLite 数据持久化', desc: '使用轻量数据库保存景点、行程、内部路网、日记等业务数据。', file: 'backend/travel.db' },
  { title: '算法服务化封装', desc: '把排序、最短路、多目标优化封装成可调用函数，再由接口层对外暴露。', file: 'backend/algorithms/core.py' },
  { title: '静态资源统一挂载', desc: '后端统一提供图片等静态资源访问，支撑前端景点和日记展示。', file: 'backend/main.py' }
]

const capabilities = [
  { icon: '📍', title: '探索发现', desc: '用户先从城市、景点、美食内容进入系统，完成兴趣发现。' },
  { icon: '🤖', title: 'AI助手生成行程', desc: 'AI 助手根据用户描述生成初步行程，并支持会话内保存和承接。' },
  { icon: '🗺️', title: '旅游规划与路径优化', desc: 'TripDetail 页面支持景点排序、交通方式切换和最优游览顺序计算。' },
  { icon: '🏫', title: '内部导航打通', desc: '当前已完成清华大学内部路网导航，可从旅游规划继续进入校园真实道路导航。' },
  { icon: '📒', title: '旅行日记沉淀', desc: '游后体验可以继续沉淀为日记内容，形成旅游内容资产闭环。' }
]

const architectureNotes = [
  { title: '真实地图', desc: '基于高德地图承载外部路径展示与内部导航可视化。' },
  { title: '真实业务闭环', desc: '从推荐、规划、导航到日记沉淀，形成连续的用户旅程。' },
  { title: 'AI 协同开发', desc: '将大模型与智能体用于需求拆解、页面生成和代码调整，提升开发效率。' }
]

const linkageHighlights = [
  { icon: '🤖', title: 'AI助手 → 行程生成', desc: '用户可以通过自然语言输入旅行需求，由 AI 助手生成可继续编辑的行程草案。' },
  { icon: '🧭', title: '行程规划 → 路径优化', desc: '生成的行程不仅是景点列表，还能进一步进入地图视图进行排序和路径优化。' },
  { icon: '🏫', title: '外部规划 → 内部导航', desc: '当前已打通到清华大学内部地图：当游览进入校园内部后，系统可继续切换到清华大学真实内部路网导航，不在入口处中断。' },
  { icon: '📒', title: '游玩结束 → 日记沉淀', desc: '用户游后可继续在日记模块记录行程、摄影、美食与随笔，形成长期内容积累。' }
]

const journeySteps = [
  { title: '发现阶段', desc: '用户在 Explore 页面浏览城市、景点与美食，建立旅游兴趣。' },
  { title: '规划阶段', desc: '用户通过 AI 助手或手动方式生成多日行程。' },
  { title: '优化阶段', desc: '在 TripDetail 中调整景点顺序，并根据交通方式生成更合理路线。' },
  { title: '执行阶段', desc: '进入 InternalNav 页面后，目前可以在清华大学校园内部完成真实道路导航。' },
  { title: '沉淀阶段', desc: '最终在 Diary 页面记录旅程内容，实现从工具到内容社区的延伸。' }
]

const issues = [
  {
    tag: '需求表达',
    title: '需求提得不够颗粒化，AI 无法生成理想效果',
    problem: '当我们只对 AI 说“帮我写一个美观的旅游日记页面”时，AI 往往只能产出最基础的白底黑字列表，无法理解我们的视觉规范、组件库使用方式和复杂布局关系。',
    impact: '生成出来的页面样式简陋，和现有项目风格不统一，导致返工成本很高。',
    solutions: [
      '给 AI 提前投喂项目的视觉锚点，例如技术栈、主色调、圆角规范和组件库。',
      '用原子化的布局语言替代“美观”“高级感”这类模糊形容词，例如明确写出 Flex、左右分栏、hover 阴影、边框和间距规则。',
      '采用组件化拆解方式，不一次让 AI 生成整页，而是先写按钮、输入框、卡片，再逐步组合。',
      '如果已有成熟页面，就把已有样式或结构作为代码参照物提供给 AI，降低偏差。'
    ]
  },
  {
    tag: '可控性',
    title: '自己实操少，AI 修改过程像黑箱操作',
    problem: '当我们直接把一整段代码交给 AI 修 Bug 时，AI 虽然可能修复了表面问题，但也可能偷偷改了变量名、删除了核心逻辑或引入新的隐患。',
    impact: '我们无法判断修改是否安全，后续继续开发时容易和已有逻辑冲突。',
    solutions: [
      '要求 AI 在修改前先做逻辑审计，明确说明改动了哪些函数、为什么这么改。',
      '使用 IDE 对比视图逐行检查 AI 的改动，不直接全盘接收。',
      '让 AI 同时补充测试用例或最小验证步骤，确保不是只修了表面问题。'
    ]
  },
  {
    tag: '代码维护',
    title: '重构时 AI 没有删除多余代码，后续修改容易出错',
    problem: '在旧页面改造成新页面时，AI 往往把新代码直接叠加上去，但旧变量、旧函数和废弃样式并没有同步删除。',
    impact: '代码会越来越臃肿，后续开发时难以判断哪部分是真正在生效的逻辑，维护成本迅速上升。',
    solutions: [
      '采用原子化重写策略，明确要求 AI 完整重写某个模块，而不是在旧代码上无限叠加。',
      '单独开启“代码断舍离”清理轮次，让 AI 专门找出未使用的变量、引用和样式并删除。'
    ]
  },
  {
    tag: '上下文',
    title: 'AI 上下文污染后容易出现幻觉和逻辑混乱',
    problem: '当对话过长、主题过多时，AI 容易忘记最初的命名规范和项目约束，甚至会混入无关技术栈的代码。',
    impact: '生成结果前后不一致，增加了沟通成本，也会拉低整体开发效率。',
    solutions: [
      '建立一份精简的“核心存档”，包含数据库字段、核心算法、API 命名和项目规范，在新对话中反复作为基准输入。',
      '按模块分频道交流，例如算法逻辑、前端 UI、数据处理分别在不同窗口中进行，减少上下文互相干扰。'
    ]
  }
]

const results = [
  { title: '形成完整业务闭环', desc: '项目打通了探索发现、AI 行程生成、旅游规划、路径导航、清华大学内部导航和旅行日记沉淀。' },
  { title: '实现真实导航能力', desc: '当前已完成清华大学校园内部基于真实路网的导航，其他景点内部地图仍在持续扩展中。' },
  { title: '体现算法与业务结合', desc: 'Top-K、Dijkstra、TSP 不再停留在课本层面，而是真正服务于推荐、规划和导航场景。' },
  { title: '验证 AI 协同开发方法', desc: '项目实践了龙虾、大模型与智能体协同开发流程，提升了方案设计和实现效率。' }
]

const courseValues = [
  { title: '工程价值', desc: '项目具备较完整的前后端结构，体现了从需求分析到系统落地的工程化能力。' },
  { title: '算法价值', desc: '将数据结构与算法课程中的排序、图最短路、路径优化与真实业务问题结合起来。' },
  { title: '创新价值', desc: '把 AI 助手、内部导航和旅行日记纳入同一系统，形成了区别于传统旅游规划系统的特色。' },
  { title: '展示价值', desc: '最终系统既可作为课程项目答辩作品，也具备继续扩展为完整产品原型的潜力。' }
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
    complexity: 'O((V+E)logV)',
    problem: '当用户已经确定起点和终点时，要快速求出最短时间或最短距离路径。',
    reason: '适合带权图最短路问题，和内部道路网络建模天然匹配。',
    file: 'backend/algorithms/core.py'
  },
  {
    tag: '多目标优化',
    name: 'TSP 贪心 + 2-opt',
    complexity: 'O(n²)',
    problem: '当用户希望一次游览多个点位时，需要给出更优访问顺序。',
    reason: '比暴力枚举更适合实际交互场景，能在效果和效率之间取得平衡。',
    file: 'backend/algorithms/core.py'
  }
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

.hero-section {
  min-height: calc(100vh - 120px);
  display: grid;
  grid-template-columns: minmax(0, 1.3fr) minmax(320px, 460px);
  gap: 32px;
  align-items: center;
}

.hero-text h1 {
  font-size: 58px;
  line-height: 1.15;
  margin: 20px 0 24px;
  max-width: 760px;
}

.hero-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
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
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  font-weight: 700;
  flex-shrink: 0;
}

.storyline-title {
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 4px;
}

.storyline-desc {
  color: var(--text-secondary);
  line-height: 1.6;
}

.content-section {
  margin-top: 72px;
}

.section-header {
  max-width: 860px;
  margin-bottom: 28px;
}

.section-kicker {
  display: inline-block;
  margin-bottom: 12px;
  color: var(--primary-color);
  font-size: 14px;
  letter-spacing: 0.12em;
}

.section-header h2 {
  font-size: 38px;
  margin-bottom: 14px;
}

.section-header p {
  color: rgba(255, 255, 255, 0.78);
  line-height: 1.8;
  font-size: 17px;
}

.grid {
  display: grid;
  gap: 20px;
}

.four-cols {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.three-cols {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.info-card,
.algorithm-card,
.issue-card,
.summary-card,
.demo-card,
.workflow-card,
.architecture-card,
.mini-card {
  height: 100%;
}

.card-icon,
.workflow-icon {
  font-size: 28px;
  margin-bottom: 14px;
}

.info-card h3,
.workflow-card h3,
.algorithm-card h3,
.issue-card h3,
.summary-card h3,
.demo-card h3,
.architecture-card h3 {
  font-size: 22px;
  margin-bottom: 12px;
}

.info-card p,
.workflow-summary,
.algorithm-card p,
.issue-card p,
.demo-card p,
.architecture-card p,
.mini-card p {
  color: rgba(255, 255, 255, 0.78);
  line-height: 1.8;
}

.workflow-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 20px;
}

.workflow-head {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.workflow-card ul {
  margin-top: 14px;
  padding-left: 18px;
  color: rgba(255, 255, 255, 0.82);
  line-height: 1.8;
}

.flow-strip {
  margin-top: 20px;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 18px;
}

.flow-step {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.flow-node,
.timeline-dot {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: rgba(0, 212, 255, 0.16);
  border: 1px solid rgba(0, 212, 255, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--primary-color);
  font-weight: 700;
  flex-shrink: 0;
}

.flow-title,
.arch-title,
.algo-label,
.issue-tag {
  font-weight: 700;
}

.flow-desc,
.arch-file {
  color: var(--text-secondary);
  line-height: 1.6;
}

.architecture-overview-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.overview-card {
  height: 100%;
}

.overview-list {
  display: grid;
  gap: 14px;
  margin-top: 18px;
}

.overview-item {
  padding: 14px 16px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.overview-item p {
  margin: 8px 0;
}

.overview-file {
  color: var(--primary-color);
  font-size: 13px;
}

.linkage-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 20px;
}

.linkage-card {
  height: 100%;
}

.journey-card {
  margin-top: 20px;
}

.journey-steps {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 16px;
  margin-top: 18px;
}

.journey-step {
  padding: 16px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.journey-index {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  font-weight: 700;
  margin-bottom: 12px;
}

.journey-title {
  font-weight: 700;
  margin-bottom: 6px;
}

.journey-desc,
.issue-impact {
  color: rgba(255, 255, 255, 0.78);
  line-height: 1.8;
}

.issues-list.detailed {
  gap: 20px;
}

.detailed-issue-card {
  padding: 24px;
}

.solution-block {
  margin-top: 14px;
}

.solution-block ul {
  margin-top: 10px;
  padding-left: 20px;
  color: rgba(255, 255, 255, 0.82);
  line-height: 1.9;
}

.summary-grid.final-version {
  grid-template-columns: minmax(0, 1fr) minmax(420px, 520px);
}

.course-value-list {
  display: grid;
  gap: 16px;
  margin-top: 16px;
}

.course-value-item {
  padding: 14px 16px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.course-value-item p {
  margin-top: 8px;
}


.architecture-stack {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-top: 18px;
}

.arch-layer {
  padding: 16px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.arch-title-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 8px;
  flex-wrap: wrap;
}

.arch-file {
  font-size: 13px;
}

.architecture-right {
  display: grid;
  gap: 20px;
}

.capability-list {
  display: grid;
  gap: 16px;
  margin-top: 16px;
}

.capability-item {
  display: grid;
  grid-template-columns: 28px 1fr;
  gap: 12px;
  align-items: start;
}

.capability-item span {
  font-size: 22px;
}

.capability-item p {
  margin-top: 6px;
}

.mini-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 20px;
}

.algo-top {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
  align-items: center;
  flex-wrap: wrap;
}

.algo-badge,
.algo-complexity,
.issue-tag {
  display: inline-flex;
  align-items: center;
  padding: 6px 12px;
  border-radius: 999px;
  background: rgba(0, 212, 255, 0.12);
  border: 1px solid rgba(0, 212, 255, 0.28);
  color: var(--primary-color);
  font-size: 13px;
}

.algo-block + .algo-block {
  margin-top: 12px;
}

.algo-label {
  display: block;
  margin-bottom: 4px;
  color: #fff;
}

.issues-list {
  display: grid;
  gap: 18px;
}

.issue-head {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
  margin-bottom: 12px;
}

.issue-problem,
.issue-solution {
  line-height: 1.8;
}

.summary-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(360px, 420px);
  gap: 20px;
}

.timeline {
  margin-top: 18px;
  display: grid;
  gap: 18px;
}

.timeline-item {
  display: flex;
  gap: 14px;
  align-items: flex-start;
}

.timeline-dot {
  width: 16px;
  height: 16px;
  margin-top: 4px;
}

.demo-actions {
  display: flex;
  flex-direction: column;
  gap: 14px;
  margin-top: 18px;
}

@media (max-width: 1200px) {
  .presentation-content {
    padding: 100px 28px 60px;
  }

  .hero-section,
  .architecture-overview-grid,
  .architecture-layout,
  .summary-grid,
  .workflow-grid,
  .four-cols,
  .three-cols,
  .flow-strip,
  .mini-grid,
  .linkage-grid,
  .journey-steps {
    grid-template-columns: 1fr;
  }

  .hero-text h1 {
    font-size: 44px;
  }
}

@media (max-width: 768px) {
  .presentation-content {
    padding: 92px 18px 50px;
  }

  .hero-section {
    min-height: auto;
  }

  .hero-text h1 {
    font-size: 34px;
  }

  .section-header h2 {
    font-size: 28px;
  }

  .hero-desc,
  .section-header p {
    font-size: 15px;
  }

  .hero-actions {
    flex-direction: column;
    align-items: stretch;
  }

  .tech-button,
  .ghost-button {
    width: 100%;
  }
}
</style>
