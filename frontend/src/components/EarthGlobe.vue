<template>
  <div class="earth-globe-container" :class="{ 'mini-mode': mini }">
    <div ref="canvasContainer" class="canvas-wrapper"></div>

    <button v-if="showClose" class="earth-close-btn" @click="emit('close')">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M18 6L6 18M6 6l12 12"/>
      </svg>
    </button>

    <template v-if="!mini">
      <!-- 搜索与城市列表面板 -->
      <div class="search-panel" :class="{ 'collapsed': isListCollapsed }">
        <div class="search-header">
          <div class="search-box">
            <svg class="search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/>
            </svg>
            <input 
              v-model="searchQuery" 
              placeholder="搜索城市..." 
              class="search-input"
              @focus="isListCollapsed = false"
            />
          </div>
          <button class="collapse-toggle" @click="isListCollapsed = !isListCollapsed">
            <svg :style="{ transform: isListCollapsed ? 'rotate(180deg)' : 'none' }" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M15 18l-6-6 6-6"/>
            </svg>
          </button>
        </div>

        <div v-if="!isListCollapsed" class="city-list-wrapper">
          <div v-if="filteredTraces.length === 0" class="empty-result">
            未找到足迹
          </div>
          <div v-else class="city-items">
            <button 
              v-for="city in filteredTraces" 
              :key="city.name" 
              class="city-item"
              :class="{ 'active': selectedCity?.name === city.name }"
              @click="flyToCity(city)"
            >
              <div class="city-item-info">
                <span class="city-item-name">{{ city.name }}</span>
                <span class="city-item-detail">{{ city.province || city.country }}</span>
              </div>
              <span class="city-item-count">{{ city.visitCount }}</span>
            </button>
          </div>
        </div>
      </div>

      <div v-if="hoveredCity && !selectedCity" class="hover-tooltip" :style="{ left: tooltipPos.x + 'px', top: tooltipPos.y + 'px' }">
        <div class="tooltip-city-name">{{ hoveredCity.name }}</div>
        <div v-if="hoveredCity.province" class="tooltip-province">{{ hoveredCity.province }}, {{ hoveredCity.country }}</div>
        <div v-if="hoveredCity.visitCount" class="tooltip-visits">到访 {{ hoveredCity.visitCount }} 次</div>
      </div>

      <transition name="hologram">
        <div v-if="selectedCity" class="hologram-panel">
          <!-- 背景装饰：扫描线与数字阵列 -->
          <div class="hologram-bg-decor"></div>
          
          <div class="panel-inner">
            <div class="panel-header">
              <div class="panel-glitch-title" :data-text="selectedCity.name">{{ selectedCity.name }}</div>
              <div class="panel-sub-info">
                <span class="location-tag">{{ selectedCity.province }}, {{ selectedCity.country }}</span>
                <span class="coord-tag">{{ selectedCity.lat.toFixed(2) }}°N, {{ selectedCity.lng.toFixed(2) }}°E</span>
              </div>
              <button class="panel-close-btn" @click="closeCityPanel">
                <div class="close-ring"></div>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                  <path d="M18 6L6 18M6 6l12 12"/>
                </svg>
              </button>
            </div>

            <div class="panel-body">
              <div class="data-scanner">
                <div class="scanner-line"></div>
                <div class="stats-group">
                  <div class="stat-item">
                    <div class="stat-val">{{ selectedCity.visitCount }}</div>
                    <div class="stat-lbl">VISITS</div>
                  </div>
                  <div class="stat-divider"></div>
                  <div class="stat-item">
                    <div class="stat-val">{{ selectedCity.diaries?.length || 0 }}</div>
                    <div class="stat-lbl">RECORDS</div>
                  </div>
                </div>
              </div>

              <div class="memory-fragments">
                <div class="fragment-header">MEMORY FRAGMENTS</div>
                <div class="fragment-list">
                  <div 
                    v-for="(diary, index) in selectedCity.diaries" 
                    :key="diary.id" 
                    class="fragment-card"
                    :style="{ '--delay': index * 0.1 + 's' }"
                    @click="viewDiary(diary.id)"
                  >
                    <div class="card-edge"></div>
                    <img v-if="diary.cover" :src="diary.cover" class="card-img" />
                    <div v-else class="card-img-placeholder"></div>
                    <div class="card-info">
                      <div class="card-date">{{ formatDate(diary.created_at) }}</div>
                      <div class="card-title">{{ diary.title }}</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </transition>

      <div class="hint-text">
        <span>滚轮缩放 · 点击城市探索足迹</span>
      </div>

      <div class="stats-bar">
        <div class="stat">
          <span class="stat-num">{{ visitedCitiesCount }}</span>
          <span class="stat-label">到访城市</span>
        </div>
        <div class="stat-divider"></div>
        <div class="stat">
          <span class="stat-num">{{ totalDiaryCount }}</span>
          <span class="stat-label">旅行日记</span>
        </div>
        <div class="stat-divider"></div>
        <div class="stat">
          <span class="stat-num">{{ countriesCount }}</span>
          <span class="stat-label">国家/地区</span>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'

const props = defineProps({
  traces: { type: Array, default: () => [] },
  mini: { type: Boolean, default: false },
  showClose: { type: Boolean, default: false }
})

const emit = defineEmits(['close'])

const router = useRouter()
const canvasContainer = ref(null)
const hoveredCity = ref(null)
const selectedCity = ref(null)
const searchQuery = ref('')
const isListCollapsed = ref(false)
const tooltipPos = reactive({ x: 0, y: 0 })

let scene, camera, renderer, controls
let earthMesh, atmosphereMesh, starField
let sunLight, cityMarkers = []
let raycaster, mouse
let animationId, time = 0
let lastFrameTime = 0
let isDragging = false, dragTimeout

const visitedCitiesCount = computed(() => props.traces.length)
const totalDiaryCount = computed(() => props.traces.reduce((sum, c) => sum + (c.diaries?.length || 0), 0))
const countriesCount = computed(() => new Set(props.traces.map(c => c.country || '未知')).size)

const filteredTraces = computed(() => {
  if (!searchQuery.value) return props.traces
  const q = searchQuery.value.toLowerCase()
  return props.traces.filter(c => 
    c.name.toLowerCase().includes(q) || 
    (c.province && c.province.toLowerCase().includes(q)) ||
    (c.country && c.country.toLowerCase().includes(q))
  )
})

// ========== 精确经纬度转换 ==========
const EARTH_RADIUS = 1.05

const latLngToVec3 = (lat, lng, radius) => {
  const phi = (90 - lat) * (Math.PI / 180)
  const theta = (lng + 180) * (Math.PI / 180)
  const x = -(radius * Math.sin(phi) * Math.cos(theta))
  const y = radius * Math.cos(phi)
  const z = radius * Math.sin(phi) * Math.sin(theta)
  return new THREE.Vector3(x, y, z)
}

// ========== 纹理加载 ==========
const TEXTURE_URLS = {
  day: 'https://unpkg.com/three-globe@2.31.1/example/img/earth-blue-marble.jpg',
  bump: 'https://unpkg.com/three-globe@2.31.1/example/img/earth-topology.png',
  water: 'https://unpkg.com/three-globe@2.31.1/example/img/earth-water.png',
  night: 'https://unpkg.com/three-globe@2.31.1/example/img/earth-night.jpg'
}

const loadTexture = (url) => {
  return new Promise((resolve, reject) => {
    const loader = new THREE.TextureLoader()
    loader.load(url, resolve, undefined, reject)
  })
}

const loadAllTextures = async () => {
  try {
    const [dayMap, bumpMap, waterMap, nightMap] = await Promise.all([
      loadTexture(TEXTURE_URLS.day),
      loadTexture(TEXTURE_URLS.bump),
      loadTexture(TEXTURE_URLS.water),
      loadTexture(TEXTURE_URLS.night)
    ])
    dayMap.colorSpace = THREE.SRGBColorSpace
    nightMap.colorSpace = THREE.SRGBColorSpace
    return { dayMap, bumpMap, waterMap, nightMap }
  } catch (e) {
    console.warn('纹理加载失败，使用备用方案', e)
    return createFallbackTextures()
  }
}

const createFallbackTextures = () => {
  const size = 2048
  const canvas = document.createElement('canvas')
  canvas.width = size
  canvas.height = size / 2
  const ctx = canvas.getContext('2d')

  const grad = ctx.createLinearGradient(0, 0, 0, canvas.height)
  grad.addColorStop(0, '#0d2137')
  grad.addColorStop(0.5, '#153a6a')
  grad.addColorStop(1, '#0d2137')
  ctx.fillStyle = grad
  ctx.fillRect(0, 0, canvas.width, canvas.height)

  ctx.strokeStyle = 'rgba(100, 180, 255, 0.12)'
  ctx.lineWidth = 1
  for (let lat = -80; lat <= 80; lat += 10) {
    const y = ((90 - lat) / 180) * canvas.height
    ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(canvas.width, y); ctx.stroke()
  }
  for (let lng = -180; lng <= 180; lng += 10) {
    const x = ((lng + 180) / 360) * canvas.width
    ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, canvas.height); ctx.stroke()
  }

  const tex = new THREE.CanvasTexture(canvas)
  tex.colorSpace = THREE.SRGBColorSpace
  return { dayMap: tex, bumpMap: null, waterMap: null }
}

// ========== 数字化地球Shader ==========
const createDigitalEarthShader = (textures) => {
  const dayMap = textures.dayMap || new THREE.DataTexture(new Uint8Array([0,0,0,255]), 1, 1)
  const bumpMap = textures.bumpMap || dayMap
  const waterMap = textures.waterMap || dayMap
  const nightMap = textures.nightMap || dayMap
  
  return new THREE.ShaderMaterial({
    uniforms: {
      uMap: { value: dayMap },
      uBumpMap: { value: bumpMap },
      uWaterMap: { value: waterMap },
      uNightMap: { value: nightMap },
      uTime: { value: 0 },
      uColor: { value: new THREE.Color(0x050d1a) }, // 极深海蓝
      uLandColor: { value: new THREE.Color(0x00d4ff) } // 赛博亮蓝
    },
    vertexShader: `
      varying vec2 vUv;
      varying vec3 vNormal;
      varying vec3 vPosition;
      void main() {
        vUv = uv;
        vNormal = normalize(normalMatrix * normal);
        vPosition = position;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `,
    fragmentShader: `
      uniform sampler2D uMap;
      uniform sampler2D uBumpMap;
      uniform sampler2D uWaterMap;
      uniform sampler2D uNightMap;
      uniform float uTime;
      uniform vec3 uColor;
      uniform vec3 uLandColor;
      varying vec2 vUv;
      varying vec3 vNormal;

      void main() {
        vec4 tex = texture2D(uMap, vUv);
        vec4 night = texture2D(uNightMap, vUv);
        
        // 1. 精准陆地提取
        float waterIntensity = texture2D(uWaterMap, vUv).r;
        float landMask = 1.0 - smoothstep(0.4, 0.6, waterIntensity);
        
        // 2. 地形起伏 (Bump)
        float bump = texture2D(uBumpMap, vUv).r;
        
        // 3. 生态颜色深度分析
        float greenness = clamp(tex.g * 1.5 - tex.r - tex.b, 0.0, 1.0); 
        float brownness = clamp(tex.r * 1.2 - tex.b, 0.0, 1.0) * (1.0 - greenness);
        float whiteness = smoothstep(0.7, 1.0, (tex.r + tex.g + tex.b) / 3.0);
        
        vec3 forestBlue = vec3(0.0, 0.4, 0.7);
        vec3 desertBlue = vec3(0.1, 0.3, 0.5);
        vec3 iceWhite = vec3(0.7, 0.9, 1.0);
        
        vec3 landBase = mix(uLandColor * 0.6, forestBlue, greenness);
        landBase = mix(landBase, desertBlue, brownness);
        landBase = mix(landBase, iceWhite, whiteness);
        
        // 4. 城市夜景灯光 (Night Lights) - 极具细节感的体现
        float lights = pow(night.r, 2.0) * 1.5;
        vec3 lightColor = vec3(1.0, 0.8, 0.4); // 暖橙色灯光
        landBase += lightColor * lights * (sin(uTime * 1.5 + vUv.x * 10.0) * 0.2 + 0.8);

        // 5. 数字化点阵与电子网格 (Cyber Grid)
        // 增加双层网格，更有精密感
        float grid1 = sin(vUv.x * 1500.0) * sin(vUv.y * 750.0);
        grid1 = smoothstep(0.98, 1.0, grid1);
        
        float grid2 = sin(vUv.x * 3000.0) * sin(vUv.y * 1500.0);
        grid2 = smoothstep(0.99, 1.0, grid2);
        
        landBase += uLandColor * (grid1 * 0.2 + grid2 * 0.15) * landMask;

        // 6. 最终颜色混合
        vec3 color = mix(uColor, landBase, landMask);
        
        // 7. 海洋镜面高光 (Liquid Digital Ocean)
        vec3 normal = normalize(vNormal);
        float spec = pow(max(dot(normal, vec3(0, 0, 1.0)), 0.0), 32.0);
        color += vec3(0.1, 0.4, 1.0) * spec * (1.0 - landMask) * 0.3;

        // 8. 扫描线细节
        float scanline = sin(vUv.y * 800.0 - uTime * 3.0) * 0.03 + 0.97;
        color *= scanline;
        
        // 9. 全息边缘强光
        float fresnel = pow(1.0 - abs(normal.z), 2.0);
        color += vec3(0.0, 0.6, 1.0) * fresnel * 0.9;
        
        // 叠加地形立体细节
        if (landMask > 0.5) {
          color += (bump - 0.5) * 0.25; 
        }

        gl_FragColor = vec4(color, 1.0);
      }
    `,
    transparent: false,
    depthWrite: true,
    depthTest: true
  })
}

// ========== 城市标记Shader ==========
const createCityMarkerShader = (color, visitCount) => {
  return new THREE.ShaderMaterial({
    transparent: true,
    blending: THREE.AdditiveBlending,
    depthWrite: false,
    uniforms: {
      uTime: { value: 0 },
      uColor: { value: new THREE.Color(color) },
      uVisitIntensity: { value: Math.min(visitCount / 5, 1.0) },
      uHovered: { value: 0 }
    },
    vertexShader: `
      varying vec2 vUv;
      void main() {
        vUv = uv;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `,
    fragmentShader: `
      uniform float uTime;
      uniform vec3 uColor;
      uniform float uVisitIntensity;
      uniform float uHovered;
      varying vec2 vUv;

      void main() {
        vec2 uv = vUv - 0.5;
        float d = length(uv);
        
        // 1. 十字星芒核心算法 (极致尖锐)
        float cross = smoothstep(0.02, 0.0, abs(uv.x)) * smoothstep(0.5, 0.0, abs(uv.y)) +
                      smoothstep(0.02, 0.0, abs(uv.y)) * smoothstep(0.5, 0.0, abs(uv.x));
        
        // 2. 实心核心与外部辉光
        float core = smoothstep(0.18, 0.0, d);
        float innerCore = smoothstep(0.06, 0.0, d);
        float aura = exp(-d * 10.0) * 0.5; // 增加一层背景辉光
        
        // 3. 动态脉冲
        float t = uTime * 3.0; // 频率加快
        float pulse = sin(t) * 0.1 + 0.9;
        
        // 4. 组合形状
        float star = max(max(core, cross * 1.0), aura);
        
        // 5. 极致超亮处理 (Overexposure)
        // 使用更高的倍率触发 AdditiveBlending 的视觉溢出
        vec3 brightColor = uColor * 5.0; 
        vec3 whiteHot = vec3(2.0, 2.0, 1.8); // 极亮核心
        vec3 finalColor = mix(brightColor, whiteHot, innerCore * 0.9);
        
        // 悬浮态亮度奖励
        finalColor += uHovered * brightColor * 0.5;
        
        float alpha = star * (1.1 + uHovered * 0.3);
        alpha *= (1.0 + uVisitIntensity * 0.5);
        
        gl_FragColor = vec4(finalColor * pulse, alpha);
      }
    `
  })
}

// 柱状光束Shader
const createPillarShader = (color) => {
  return new THREE.ShaderMaterial({
    transparent: true,
    blending: THREE.AdditiveBlending,
    depthWrite: false,
    side: THREE.DoubleSide,
    uniforms: {
      uTime: { value: 0 },
      uColor: { value: new THREE.Color(color) }
    },
    vertexShader: `
      varying vec2 vUv;
      void main() {
        vUv = uv;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `,
    fragmentShader: `
      uniform float uTime;
      uniform vec3 uColor;
      varying vec2 vUv;
      void main() {
        float fade = pow(1.0 - vUv.y, 2.0);
        float sideFade = 1.0 - abs(vUv.x - 0.5) * 2.0;
        float scan = sin(vUv.y * 10.0 - uTime * 3.0) * 0.1 + 0.9;
        gl_FragColor = vec4(uColor, fade * sideFade * 0.5 * scan);
      }
    `
  })
}

const getMarkerColor = (count) => {
  // 统一使用橙色系，通过明度区分活跃度
  if (count >= 5) return '#ff6b35' // 亮橙色
  if (count >= 3) return '#ff9800' // 标准橙
  if (count >= 2) return '#ffb74d' // 浅橙
  return '#ffd95d' // 金黄色
}

const createCityMarker = (city) => {
  const visitCount = city.visitCount || city.diaries?.length || 1
  const color = getMarkerColor(visitCount)

  const group = new THREE.Group()
  group.userData = { city, isCityMarker: true }

  const r = EARTH_RADIUS + 0.008 + Math.min(visitCount * 0.001, 0.006)
  group.position.copy(latLngToVec3(city.lat, city.lng, r))

  const size = 0.08 // 基础尺寸翻倍 (从 0.045 提升)
  const baseSize = size + Math.min(visitCount * 0.005, 0.04)
  const geo = new THREE.PlaneGeometry(baseSize, baseSize)
  const mat = createCityMarkerShader(color, visitCount)
  const marker = new THREE.Mesh(geo, mat)
  marker.userData = { city, isMarkerMesh: true }
  group.add(marker)

  // 添加选中时的光柱
  const pillarGeo = new THREE.CylinderGeometry(baseSize*0.1, baseSize*0.1, 0.3, 8, 1, true)
  pillarGeo.translate(0, 0.15, 0)
  pillarGeo.rotateX(Math.PI / 2)
  const pillarMat = createPillarShader(color)
  const pillar = new THREE.Mesh(pillarGeo, pillarMat)
  pillar.visible = false
  pillar.name = 'selectionPillar'
  group.add(pillar)

  const hitGeo = new THREE.SphereGeometry(baseSize * 2, 8, 8)
  const hitMat = new THREE.MeshBasicMaterial({ visible: false })
  const hitArea = new THREE.Mesh(hitGeo, hitMat)
  hitArea.userData = { city, isHitArea: true }
  group.add(hitArea)

  return { group, marker, hitArea }
}

// ========== 大气层 ==========
const createAtmosphere = () => {
  return new THREE.ShaderMaterial({
    transparent: true,
    side: THREE.BackSide,
    blending: THREE.AdditiveBlending,
    depthWrite: false,
    uniforms: {
      uTime: { value: 0 },
      uGlowColor: { value: new THREE.Color(0x4a9eff) }
    },
    vertexShader: `
      varying vec3 vNormal;
      varying vec3 vPosition;
      void main() {
        vNormal = normalize(normalMatrix * normal);
        vPosition = position;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `,
    fragmentShader: `
      uniform float uTime;
      uniform vec3 uGlowColor;
      uniform float uMorph;
      varying vec3 vNormal;
      varying vec3 vPosition;
      void main() {
        // 这里的公式创造边缘辉光感，避开硬边 plastic 感
        float intensity = pow(0.65 - dot(vNormal, vec3(0, 0, 1.0)), 3.0);
        float breath = sin(uTime * 0.8) * 0.05 + 0.95;
        gl_FragColor = vec4(uGlowColor, intensity * 0.6 * breath);
      }
    `
  })
}

// ========== 星空 ==========
const createStars = (count = 5000) => {
  const pos = new Float32Array(count * 3)
  const sizes = new Float32Array(count)
  const phases = new Float32Array(count)

  for (let i = 0; i < count; i++) {
    const r = 80 + Math.random() * 500
    const theta = Math.random() * Math.PI * 2
    const phi = Math.acos(2 * Math.random() - 1)
    pos[i * 3] = r * Math.sin(phi) * Math.cos(theta)
    pos[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta)
    pos[i * 3 + 2] = r * Math.cos(phi)
    sizes[i] = 0.4 + Math.random() * 1.6
    phases[i] = Math.random() * Math.PI * 2
  }

  const geo = new THREE.BufferGeometry()
  geo.setAttribute('position', new THREE.BufferAttribute(pos, 3))
  geo.setAttribute('size', new THREE.BufferAttribute(sizes, 1))
  geo.setAttribute('phase', new THREE.BufferAttribute(phases, 1))

  return new THREE.Points(geo, new THREE.ShaderMaterial({
    uniforms: { uTime: { value: 0 } },
    vertexShader: `
      attribute float size;
      attribute float phase;
      varying float vA;
      uniform float uTime;
      void main() {
        vA = 0.4 + sin(uTime * 1.5 + phase) * 0.35;
        vec4 mv = modelViewMatrix * vec4(position, 1.0);
        gl_PointSize = size * (250.0 / -mv.z);
        gl_Position = projectionMatrix * mv;
      }
    `,
    fragmentShader: `
      varying float vA;
      void main() {
        float d = length(gl_PointCoord - vec2(0.5));
        if (d > 0.5) discard;
        float a = 1.0 - smoothstep(0.0, 0.5, d);
        gl_FragColor = vec4(0.85, 0.88, 1.0, a * vA);
      }
    `,
    transparent: true,
    blending: THREE.AdditiveBlending,
    depthWrite: false
  }))
}

// ========== 场景初始化 ==========
const initScene = async () => {
  try {
    const container = canvasContainer.value
    if (!container) return

    const w = container.clientWidth
    const h = container.clientHeight
    console.log(`初始化场景: ${w}x${h}, mini=${props.mini}`)

    scene = new THREE.Scene()
    scene.background = new THREE.Color(0x050d1a)

    camera = new THREE.PerspectiveCamera(60, w / h, 0.1, 2000)
    camera.position.set(0, 0, 2.5)

    const canvas = document.createElement('canvas')
    canvas.style.cssText = 'width:100%;height:100%;display:block'
    container.appendChild(canvas)

    renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, powerPreference: 'high-performance' })
    renderer.setSize(w, h)
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
    renderer.toneMapping = THREE.ACESFilmicToneMapping
    renderer.toneMappingExposure = 1.1

    controls = new OrbitControls(camera, renderer.domElement)
    controls.enableDamping = true
    controls.dampingFactor = 0.06
    controls.enableZoom = !props.mini
    controls.minDistance = 1.25
    controls.maxDistance = 10
    controls.autoRotate = true
    controls.autoRotateSpeed = props.mini ? 0.5 : 0.35 
    controls.enablePan = false
    
    if (props.mini) {
      controls.enabled = false 
    }

    controls.addEventListener('start', () => { isDragging = true; controls.autoRotate = false })
    controls.addEventListener('end', () => {
      isDragging = false
      clearTimeout(dragTimeout)
      dragTimeout = setTimeout(() => { controls.autoRotate = true }, 3000)
    })

    const textures = await loadAllTextures()

    // 地球球体
    const segments = props.mini ? 64 : 256
    const earthGeo = new THREE.SphereGeometry(EARTH_RADIUS, segments, segments)
    const earthShader = createDigitalEarthShader(textures)
    earthMesh = new THREE.Mesh(earthGeo, earthShader)
    earthMesh.renderOrder = 1 // 确保在地表层
    scene.add(earthMesh)

    // 大气层
    const atmoSegments = props.mini ? 32 : 128
    const atmoGeo = new THREE.SphereGeometry(1.055, atmoSegments, atmoSegments)
    const atmoMat = createAtmosphere()
    atmosphereMesh = new THREE.Mesh(atmoGeo, atmoMat)
    scene.add(atmosphereMesh)

    // 星空
    const starCount = props.mini ? 1000 : 5000
    starField = createStars(starCount)
    scene.add(starField)

    // 动态光源
    const ambient = new THREE.AmbientLight(0x2a2a4a, 0.3)
    scene.add(ambient)
    sunLight = new THREE.DirectionalLight(0xffffff, 2.0)
    scene.add(sunLight)
    const rimLight = new THREE.DirectionalLight(0x3a6aff, 0.12)
    rimLight.position.set(0, 0, -5)
    scene.add(rimLight)

    if (!props.mini) {
      raycaster = new THREE.Raycaster()
      mouse = new THREE.Vector2()
      renderer.domElement.addEventListener('click', onCanvasClick)
      renderer.domElement.addEventListener('mousemove', onCanvasMouseMove)
    }
    
    window.addEventListener('resize', onWindowResize)
  } catch (err) {
    console.error('Three.js 初始化失败:', err)
  }
}

// ========== 标记管理 ==========
const updateCityMarkers = () => {
  cityMarkers.forEach(m => scene.remove(m.group))
  cityMarkers = []
  if (!props.traces?.length) return
  props.traces.forEach(city => {
    const m = createCityMarker(city, false)
    scene.add(m.group)
    cityMarkers.push(m)
  })
}

// ========== 边界线渲染Shader ==========
const createBoundaryShader = (color, opacity, speed = 1.0, isCity = false) => {
  return new THREE.ShaderMaterial({
    transparent: true,
    blending: THREE.AdditiveBlending,
    depthWrite: false,
    uniforms: {
      uTime: { value: 0 },
      uColor: { value: new THREE.Color(color) },
      uOpacity: { value: opacity },
      uSpeed: { value: speed },
      uIsCity: { value: isCity ? 1.0 : 0.0 }
    },
    vertexShader: `
      varying vec3 vPosition;
      void main() {
        vPosition = position;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `,
    fragmentShader: `
      uniform float uTime;
      uniform vec3 uColor;
      uniform float uOpacity;
      uniform float uSpeed;
      uniform float uIsCity;
      varying vec3 vPosition;

      void main() {
        // 极高亮度的测试 Shader
        float flow = sin(vPosition.x * 15.0 + vPosition.y * 15.0 + vPosition.z * 15.0 - uTime * uSpeed * 2.5);
        flow = flow * 0.5 + 0.5; 
        
        float alpha = uOpacity * (0.5 + flow * 0.5);
        vec3 color = uColor;
        
        // 让城市线极其显眼
        if (uIsCity > 0.5) {
          color = mix(uColor, vec3(1.0, 1.0, 1.0), flow * 0.5);
          alpha = uOpacity * (0.8 + flow * 0.2);
        }

        gl_FragColor = vec4(color, alpha);
      }
    `
  })
}

let countryBoundaries = null
let chinaProvincialBoundaries = null

// ========== 边界线加载 ==========
const loadBoundaries = async () => {
  const processGeometry = (geometry, points, radius) => {
    if (geometry.type === 'Polygon') {
      geometry.coordinates.forEach(ring => {
        ring.forEach((coord, i) => {
          if (i < ring.length - 1) {
            points.push(latLngToVec3(coord[1], coord[0], radius), latLngToVec3(ring[i+1][1], ring[i+1][0], radius))
          }
        })
      })
    } else if (geometry.type === 'MultiPolygon') {
      geometry.coordinates.forEach(polygon => {
        polygon.forEach(ring => {
          ring.forEach((coord, i) => {
            if (i < ring.length - 1) {
              points.push(latLngToVec3(coord[1], coord[0], radius), latLngToVec3(ring[i+1][1], ring[i+1][0], radius))
            }
          })
        })
      })
    } else if (geometry.type === 'LineString') {
      geometry.coordinates.forEach((coord, i) => {
        if (i < geometry.coordinates.length - 1) {
          points.push(latLngToVec3(coord[1], coord[0], radius), latLngToVec3(geometry.coordinates[i+1][1], geometry.coordinates[i+1][0], radius))
        }
      })
    } else if (geometry.type === 'MultiLineString') {
      geometry.coordinates.forEach(line => {
        line.forEach((coord, i) => {
          if (i < line.length - 1) {
            points.push(latLngToVec3(coord[1], coord[0], radius), latLngToVec3(line[i+1][1], line[i+1][0], radius))
          }
        })
      })
    }
  }

  // 1. 加载全球国界
  try {
    // 使用 jsdelivr CDN 提高稳定性
    const response = await fetch('https://cdn.jsdelivr.net/gh/nvkelso/natural-earth-vector@master/geojson/ne_110m_admin_0_countries.geojson')
    if (response.ok) {
      const data = await response.json()
      const points = []
      data.features.forEach(f => {
        // 排除中国，因为我们有更高精度的中国省界/国界组合
        if (f.properties && (f.properties.SOV_A3 === 'CHN' || f.properties.ADM0_A3 === 'CHN' || f.properties.NAME === 'China')) {
          return
        }
        processGeometry(f.geometry, points, 1.06)
      })
      const geo = new THREE.BufferGeometry().setFromPoints(points)
      // 统一亮度：使用和中国线条一致的颜色 (0x00d4ff) 和高透明度 (0.9)
      const mat = createBoundaryShader(0x00d4ff, 0.9, 1.0, true) 
      countryBoundaries = new THREE.LineSegments(geo, mat)
      countryBoundaries.renderOrder = 10
      scene.add(countryBoundaries)
    }
  } catch (e) { console.error('国界加载失败', e) }

  // 2. 加载中国省界 (使用更稳定的CDN) - 预览模式下跳过以节省性能和带宽
  if (props.mini) return

  try {
    const response = await fetch('https://geo.datav.aliyun.com/areas_v3/bound/100000_full.json')
    if (response.ok) {
      const data = await response.json()
      const points = []
      data.features.forEach(f => processGeometry(f.geometry, points, 1.061))
      const geo = new THREE.BufferGeometry().setFromPoints(points)
      // 保持一致的高亮度
      const mat = createBoundaryShader(0x00d4ff, 0.9, 1.2, true) 
      chinaProvincialBoundaries = new THREE.LineSegments(geo, mat)
      chinaProvincialBoundaries.renderOrder = 11
      scene.add(chinaProvincialBoundaries)
    }
  } catch (e) { console.error('中国省界加载失败', e) }
}

// ========== 交互 ==========
const getIntersectedCity = (event) => {
  const rect = renderer.domElement.getBoundingClientRect()
  mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1
  mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1
  raycaster.setFromCamera(mouse, camera)
  const intersects = raycaster.intersectObjects(cityMarkers.map(c => c.group), true)
  if (intersects.length === 0) return null
  let obj = intersects[0].object
  while (obj && !obj.userData?.city) obj = obj.parent
  return obj?.userData?.city || null
}

const onCanvasClick = (e) => {
  const city = getIntersectedCity(e)
  city ? selectCity(city) : selectedCity.value = null
}

const onCanvasMouseMove = (e) => {
  const city = getIntersectedCity(e)
  const rect = renderer.domElement.getBoundingClientRect()
  renderer.domElement.style.cursor = city ? 'pointer' : 'default'

  if (city) {
    hoveredCity.value = city
    tooltipPos.x = e.clientX - rect.left + 15
    tooltipPos.y = e.clientY - rect.top - 40
  } else {
    hoveredCity.value = null
  }

  cityMarkers.forEach(m => {
    if (m.marker.material.uniforms) {
      m.marker.material.uniforms.uHovered.value = city && m.group.userData.city === city ? 1 : 0
    }
  })
}

let cityBoundaryLine = null

const fetchCityBoundary = async (cityName) => {
  if (cityBoundaryLine) {
    scene.remove(cityBoundaryLine)
    cityBoundaryLine.geometry.dispose()
    cityBoundaryLine.material.dispose()
    cityBoundaryLine = null
  }

  try {
    // 使用 Overpass API 获取城市边界 (行政级别4通常是地级市/直辖市)
    const query = `[out:json];relation["name"="${cityName}"]["boundary"="administrative"]["admin_level"~"4|2"];out geom;`
    const response = await fetch(`https://overpass-api.de/api/interpreter?data=${encodeURIComponent(query)}`)
    const data = await response.json()
    
    if (!data.elements || data.elements.length === 0) return

    const points = []
    data.elements.forEach(element => {
      if (element.members) {
        element.members.forEach(member => {
          if (member.type === 'way' && member.geometry) {
            member.geometry.forEach((coord, i) => {
              if (i < member.geometry.length - 1) {
                const p1 = latLngToVec3(coord.lat, coord.lon, 1.062)
                const p2 = latLngToVec3(member.geometry[i+1].lat, member.geometry[i+1].lon, 1.062)
                points.push(p1, p2)
              }
            })
          }
        })
      }
    })

    if (points.length > 0) {
      const geometry = new THREE.BufferGeometry().setFromPoints(points)
      const material = createBoundaryShader(0x00d4ff, 0.9, 2.5, true) // 选中城市：极亮，极快
      cityBoundaryLine = new THREE.LineSegments(geometry, material)
      cityBoundaryLine.renderOrder = 12
      scene.add(cityBoundaryLine)
    }
  } catch (e) {
    console.warn('城市边界加载失败', e)
  }
}

const flyToCity = (city) => {
  selectCity(city)
  // 如果在小屏下，点击列表后收起列表
  if (window.innerWidth < 1024) {
    isListCollapsed.value = true
  }
}

const selectCity = (city) => {
  selectedCity.value = city
  controls.autoRotate = false
  
  // 异步加载真实城市边界
  fetchCityBoundary(city.name)

  // 显示选中标记的光柱
  cityMarkers.forEach(m => {
    const pillar = m.group.getObjectByName('selectionPillar')
    if (pillar) pillar.visible = m.group.userData.city === city
  })

  const target = latLngToVec3(city.lat, city.lng, 0)

  const camDist = 2.2
  const camTarget = (() => { const p = latLngToVec3(city.lat, city.lng, EARTH_RADIUS); return new THREE.Vector3().copy(p).normalize().multiplyScalar(camDist) })()

  const startCam = camera.position.clone()
  const startTgt = controls.target.clone()
  const dur = 1000
  const start = Date.now()

  const anim = () => {
    const t = Math.min((Date.now() - start) / dur, 1)
    const ease = t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2
    camera.position.lerpVectors(startCam, camTarget, ease)
    controls.target.lerpVectors(startTgt, target, ease)
    controls.update()
    if (t < 1) requestAnimationFrame(anim)
  }
  anim()
}

const closeCityPanel = () => {
  selectedCity.value = null
  
  if (cityBoundaryLine) {
    scene.remove(cityBoundaryLine)
    cityBoundaryLine.geometry.dispose()
    cityBoundaryLine.material.dispose()
    cityBoundaryLine = null
  }

  cityMarkers.forEach(m => {
    const pillar = m.group.getObjectByName('selectionPillar')
    if (pillar) pillar.visible = false
  })
  controls.autoRotate = true
}

const viewDiary = (id) => router.push(`/diary/${id}`)

const onWindowResize = () => {
  const c = canvasContainer.value
  if (!c || !camera || !renderer) return
  const w = c.clientWidth, h = c.clientHeight
  camera.aspect = w / h
  camera.updateProjectionMatrix()
  renderer.setSize(w, h)
}

const animate = () => {
  animationId = requestAnimationFrame(animate)
  
  const now = Date.now()
  const delta = now - lastFrameTime
  
  // 预览模式限制为 30fps，探索模式保持 60fps
  const fpsLimit = props.mini ? 33 : 16
  if (delta < fpsLimit) return
  
  lastFrameTime = now
  time += 0.016 * (props.mini ? 2 : 1) 

  if (earthMesh?.material.uniforms) earthMesh.material.uniforms.uTime.value = time
  if (atmosphereMesh?.material.uniforms) atmosphereMesh.material.uniforms.uTime.value = time
   if (starField) starField.material.uniforms.uTime.value = time
  
  if (countryBoundaries?.material.uniforms) countryBoundaries.material.uniforms.uTime.value = time
  if (chinaProvincialBoundaries?.material.uniforms) chinaProvincialBoundaries.material.uniforms.uTime.value = time
  if (cityBoundaryLine?.material.uniforms) cityBoundaryLine.material.uniforms.uTime.value = time

  cityMarkers.forEach(({ marker, group }) => {
    if (marker.material.uniforms) marker.material.uniforms.uTime.value = time
    const pillar = group.getObjectByName('selectionPillar')
    if (pillar && pillar.material.uniforms) pillar.material.uniforms.uTime.value = time
    marker.lookAt(camera.position)
  })

  controls.update()

  if (sunLight) {
    sunLight.position.copy(camera.position).normalize().multiplyScalar(5)
  }

  renderer.render(scene, camera)
}

const formatDate = (d) => d ? new Date(d).toLocaleDateString('zh-CN', { year: 'numeric', month: 'short', day: 'numeric' }) : ''

watch(() => props.traces, updateCityMarkers, { deep: true })

onMounted(async () => {
  await nextTick()
  await initScene()
  updateCityMarkers()
  loadBoundaries()
  animate()
})

onUnmounted(() => {
  if (animationId) cancelAnimationFrame(animationId)
  if (renderer) {
    renderer.domElement.removeEventListener('click', onCanvasClick)
    renderer.domElement.removeEventListener('mousemove', onCanvasMouseMove)
    window.removeEventListener('resize', onWindowResize)
    renderer.domElement.parentNode?.removeChild(renderer.domElement)
    renderer.dispose()
  }
  controls?.dispose()
  clearTimeout(dragTimeout)
})
</script>

<style scoped>
.earth-globe-container {
  position: relative;
  width: 100%;
  height: 100%;
  background: #050d1a;
  overflow: hidden;
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.mini-mode {
  cursor: pointer;
  border-radius: 12px;
}

.mini-mode:hover {
  box-shadow: 0 0 30px rgba(0, 212, 255, 0.15);
  transform: scale(1.02);
}

.mini-mode::after {
  content: '点击探索足迹';
  position: absolute;
  bottom: 12px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 11px;
  color: rgba(200, 220, 255, 0.5);
  background: rgba(10, 20, 40, 0.6);
  padding: 4px 10px;
  border-radius: 10px;
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
  white-space: nowrap;
}

.mini-mode:hover::after {
  opacity: 1;
}

.canvas-wrapper {
  width: 100%;
  height: 100%;
}

.canvas-wrapper canvas {
  display: block;
  width: 100%;
  height: 100%;
}

.earth-close-btn {
  position: fixed;
  top: 75px;
  right: 20px;
  width: 48px;
  height: 48px;
  background: rgba(10, 20, 40, 0.85);
  backdrop-filter: blur(15px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  color: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 9999;
  transition: all 0.3s ease;
}

.earth-close-btn:hover {
  background: rgba(255, 71, 87, 0.2);
  border-color: rgba(255, 71, 87, 0.3);
  color: #ff4757;
}

.hover-tooltip {
  position: absolute;
  z-index: 30;
  background: rgba(10, 20, 40, 0.92);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(74, 158, 255, 0.3);
  border-radius: 12px;
  padding: 12px 16px;
  pointer-events: none;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
}

.tooltip-city-name {
  color: #fff;
  font-size: 14px;
  font-weight: 600;
}

.tooltip-province {
  color: rgba(200, 220, 255, 0.7);
  font-size: 12px;
  margin-top: 4px;
}

.tooltip-visits {
  color: #00d4ff;
  font-size: 12px;
  margin-top: 4px;
  font-weight: 500;
}

.hologram-panel {
  position: absolute;
  top: 50%;
  right: 40px;
  transform: translateY(-50%);
  width: 360px;
  max-height: 80vh;
  background: rgba(10, 25, 50, 0.7);
  backdrop-filter: blur(25px);
  border: 1px solid rgba(0, 212, 255, 0.3);
  border-radius: 4px; /* 科幻感通常使用直角或微圆角 */
  clip-path: polygon(
    0 0, 
    calc(100% - 30px) 0, 100% 30px, 
    100% 100%, 
    30px 100%, 0 calc(100% - 30px)
  );
  z-index: 100;
  display: flex;
  flex-direction: column;
  box-shadow: 0 0 50px rgba(0, 0, 0, 0.5), inset 0 0 20px rgba(0, 212, 255, 0.1);
}

.hologram-bg-decor {
  position: absolute;
  inset: 0;
  background-image: 
    linear-gradient(rgba(0, 212, 255, 0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0, 212, 255, 0.05) 1px, transparent 1px);
  background-size: 20px 20px;
  pointer-events: none;
  opacity: 0.3;
}

.panel-inner {
  position: relative;
  padding: 30px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.panel-glitch-title {
  font-size: 28px;
  font-weight: 800;
  color: #fff;
  letter-spacing: 2px;
  position: relative;
  text-shadow: 0 0 15px rgba(0, 212, 255, 0.5);
}

.panel-sub-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-top: 8px;
}

.location-tag {
  font-size: 14px;
  color: rgba(0, 212, 255, 0.8);
  font-weight: 500;
}

.coord-tag {
  font-size: 11px;
  font-family: monospace;
  color: rgba(255, 255, 255, 0.4);
}

.panel-close-btn {
  position: absolute;
  top: 20px;
  right: 20px;
  background: none;
  border: none;
  color: #fff;
  cursor: pointer;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.close-ring {
  position: absolute;
  inset: 0;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  transition: all 0.3s ease;
}

.panel-close-btn:hover .close-ring {
  border-color: #ff4757;
  transform: scale(1.1);
  box-shadow: 0 0 10px rgba(255, 71, 87, 0.5);
}

.data-scanner {
  position: relative;
  padding: 20px;
  background: rgba(255, 255, 255, 0.03);
  border-left: 3px solid #00d4ff;
  overflow: hidden;
}

.scanner-line {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 2px;
  background: linear-gradient(90deg, transparent, #00d4ff, transparent);
  animation: scan 3s linear infinite;
}

@keyframes scan {
  0% { top: 0; }
  100% { top: 100%; }
}

.stats-group {
  display: flex;
  align-items: center;
  justify-content: space-around;
}

.stat-val {
  font-size: 24px;
  font-family: monospace;
  font-weight: bold;
  color: #fff;
}

.stat-lbl {
  font-size: 10px;
  color: rgba(0, 212, 255, 0.6);
  letter-spacing: 1px;
}

.memory-fragments {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.fragment-header {
  font-size: 12px;
  font-weight: bold;
  color: rgba(255, 255, 255, 0.3);
  letter-spacing: 2px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding-bottom: 5px;
}

.fragment-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  overflow-y: auto;
  max-height: 350px;
  padding-right: 10px;
}

.fragment-list::-webkit-scrollbar { width: 2px; }
.fragment-list::-webkit-scrollbar-thumb { background: rgba(0, 212, 255, 0.3); }

.fragment-card {
  position: relative;
  display: flex;
  gap: 12px;
  padding: 10px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.05);
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  animation: fragment-in 0.6s backwards;
  animation-delay: var(--delay);
}

@keyframes fragment-in {
  from { opacity: 0; transform: translateX(30px); }
  to { opacity: 1; transform: translateX(0); }
}

.fragment-card:hover {
  background: rgba(0, 212, 255, 0.08);
  border-color: rgba(0, 212, 255, 0.4);
  transform: translateX(-5px);
  box-shadow: -10px 0 20px rgba(0, 212, 255, 0.1);
}

.card-edge {
  position: absolute;
  top: -1px;
  left: -1px;
  width: 10px;
  height: 10px;
  border-top: 2px solid #00d4ff;
  border-left: 2px solid #00d4ff;
  opacity: 0;
  transition: opacity 0.3s;
}

.fragment-card:hover .card-edge { opacity: 1; }

.card-img {
  width: 60px;
  height: 60px;
  object-fit: cover;
  border-radius: 2px;
  filter: saturate(0.8) contrast(1.1);
}

.card-info {
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.card-title {
  color: #fff;
  font-size: 14px;
  font-weight: 500;
  margin-top: 2px;
}

.card-date {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.3);
  font-family: monospace;
}

/* 进场动画 */
.hologram-enter-active, .hologram-leave-active {
  transition: all 0.6s cubic-bezier(0.2, 1, 0.3, 1);
}

.hologram-enter-from, .hologram-leave-to {
  opacity: 0;
  transform: translateY(-50%) translateX(100px) skewX(-5deg);
  filter: blur(10px);
}

@media (max-width: 768px) {
  .hologram-panel {
    top: auto;
    bottom: 20px;
    right: 10px;
    left: 10px;
    width: auto;
    transform: none;
    max-height: 50vh;
  }
  .hologram-enter-from, .hologram-leave-to {
    transform: translateY(50px);
  }
}

.search-panel {
  position: absolute;
  top: 20px;
  left: 20px;
  width: 280px;
  max-height: calc(100% - 140px);
  background: rgba(10, 20, 40, 0.85);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(74, 158, 255, 0.2);
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  z-index: 20;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
}

.search-panel.collapsed {
  width: 50px;
  height: 50px;
  border-radius: 25px;
  overflow: hidden;
}

.search-header {
  display: flex;
  align-items: center;
  padding: 12px;
  gap: 8px;
}

.search-box {
  flex: 1;
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  padding: 0 10px;
  transition: all 0.3s ease;
}

.search-box:focus-within {
  border-color: rgba(74, 158, 255, 0.5);
  background: rgba(255, 255, 255, 0.08);
}

.search-icon {
  color: rgba(255, 255, 255, 0.4);
}

.search-input {
  width: 100%;
  height: 36px;
  background: none;
  border: none;
  color: #fff;
  font-size: 13px;
  padding-left: 8px;
  outline: none;
}

.search-input::placeholder {
  color: rgba(255, 255, 255, 0.3);
}

.collapse-toggle {
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.5);
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.collapse-toggle:hover {
  background: rgba(255, 255, 255, 0.05);
  color: #fff;
}

.city-list-wrapper {
  flex: 1;
  overflow-y: auto;
  padding: 0 8px 12px;
}

.city-items {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.city-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  background: none;
  border: 1px solid transparent;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: left;
  width: 100%;
}

.city-item:hover {
  background: rgba(74, 158, 255, 0.1);
}

.city-item.active {
  background: rgba(74, 158, 255, 0.15);
  border-color: rgba(74, 158, 255, 0.3);
}

.city-item-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.city-item-name {
  color: #fff;
  font-size: 14px;
  font-weight: 500;
}

.city-item-detail {
  color: rgba(255, 255, 255, 0.4);
  font-size: 11px;
}

.city-item-count {
  font-size: 11px;
  color: #00d4ff;
  background: rgba(0, 212, 255, 0.1);
  padding: 2px 8px;
  border-radius: 8px;
  border: 1px solid rgba(0, 212, 255, 0.2);
}

.empty-result {
  text-align: center;
  padding: 40px 0;
  color: rgba(255, 255, 255, 0.3);
  font-size: 13px;
}



.hint-text {
  position: absolute;
  top: 16px;
  left: 50%;
  transform: translateX(-50%);
  padding: 8px 16px;
  background: rgba(10, 20, 40, 0.8);
  border: 1px solid rgba(74, 158, 255, 0.2);
  border-radius: 20px;
  font-size: 13px;
  color: rgba(200, 220, 255, 0.7);
  z-index: 5;
}

.stats-bar {
  position: absolute;
  top: 16px;
  right: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 16px;
  background: rgba(10, 20, 40, 0.8);
  border: 1px solid rgba(74, 158, 255, 0.15);
  border-radius: 14px;
  z-index: 5;
}

.stat { text-align: center; }

.stat-num {
  display: block;
  font-size: 18px;
  font-weight: 700;
  color: #4a9eff;
}

.stat-label {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
}

.stat-divider {
  width: 1px;
  height: 20px;
  background: rgba(255, 255, 255, 0.1);
}

.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.slide-up-enter-active, .slide-up-leave-active {
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.slide-up-enter-from, .slide-up-leave-to { opacity: 0; transform: translateY(20px); }

@media (max-width: 1024px) {
  .search-panel {
    width: 240px;
    max-height: calc(100% - 200px);
  }

}

@media (max-width: 768px) {
  .earth-globe-container { height: 400px; }
  .search-panel {
    top: 10px;
    left: 10px;
    width: calc(100% - 20px);
    max-height: 200px;
  }
  .search-panel.collapsed {
    width: 40px;
    height: 40px;
  }

  .stats-bar { top: 50px; right: 10px; padding: 8px 12px; }
  .stat-num { font-size: 16px; }
  .hint-text { top: 50px; }
}
</style>
