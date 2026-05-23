<template>
  <div class="persona-wrap">
    <div class="bubble">{{ catchphrase }}</div>
    <svg viewBox="0 0 400 520" class="persona-svg">
      <g class="shadow">
        <polygon points="100,512 300,512 280,525 120,525" fill="rgba(0,0,0,0.15)"/>
      </g>

      <g class="legs">
        <polygon points="170,400 195,400 192,460 167,460" fill="#8B6914"/>
        <polygon points="167,460 192,460 188,525 163,525" fill="#6B5010"/>
        <polygon points="160,400 170,400 167,460 160,460" fill="#6B5010"/>
        <polygon points="205,400 230,400 227,460 202,460" fill="#6B5010"/>
        <polygon points="202,460 227,460 223,525 198,525" fill="#4A3508"/>
        <polygon points="230,400 240,400 237,460 227,460" fill="#4A3508"/>
      </g>

      <g class="torso breathe">
        <polygon points="150,390 250,390 245,400 155,400" fill="#4A4A4A"/>
        <polygon points="150,250 200,250 200,330 155,390 145,390" fill="#6B705C"/>
        <polygon points="200,250 250,250 255,390 245,390 200,330" fill="#8A8A7A"/>
        <polygon points="190,250 210,250 205,330 195,330" fill="#4A4A4A"/>
        <polygon points="180,250 200,250 195,270 185,265" fill="#6B705C"/>
        <polygon points="200,250 220,250 215,265 205,270" fill="#8A8A7A"/>
        <polygon points="155,280 175,278 173,300 153,302" fill="#7A7A6A"/>
        <polygon points="225,310 245,308 247,330 227,332" fill="#5A5A5A"/>
      </g>

      <g class="arm-left spread-left">
        <polygon points="150,255 120,240 90,280 110,300" fill="#6B705C"/>
        <polygon points="120,240 95,225 60,265 85,280" fill="#8A8A7A"/>
        <polygon points="95,225 70,210 35,250 60,265" fill="#4A4A4A"/>
        <polygon points="35,250 42,258 52,255 45,247" fill="#6B705C"/>
        <polygon points="42,258 48,265 58,262 52,255" fill="#8A8A7A"/>
        <polygon points="48,265 50,272 60,270 58,262" fill="#8B6914"/>
      </g>

      <g class="arm-right spread-right">
        <polygon points="250,255 280,240 310,280 290,300" fill="#8A8A7A"/>
        <polygon points="280,240 305,225 340,265 315,280" fill="#6B705C"/>
        <polygon points="305,225 330,210 365,250 340,265" fill="#4A4A4A"/>
        <polygon points="365,250 358,258 348,255 355,247" fill="#8A8A7A"/>
        <polygon points="358,258 352,265 342,262 348,255" fill="#6B705C"/>
        <polygon points="352,265 350,272 340,270 342,262" fill="#8B6914"/>
      </g>

      <g class="neck head-tilt-back">
        <polygon points="185,220 215,220 212,250 188,250" fill="#6B5010"/>
        <polygon points="185,220 195,220 193,250 188,250" fill="#8B6914"/>
        <polygon points="205,220 215,220 212,250 207,250" fill="#4A3508"/>
      </g>

      <g class="head head-tilt-back">
        <polygon points="170,155 230,155 228,200 225,220 200,225 175,220 172,200" fill="#8B6914"/>
        <polygon points="170,155 185,155 183,200 172,200" fill="#6B5010"/>
        <polygon points="215,155 230,155 228,200 217,200" fill="#4A3508"/>
        <polygon points="175,220 200,225 225,220 222,232 200,238 178,232" fill="#6B5010"/>

        <polygon points="148,128 252,128 260,172 140,172" fill="#1B4332"/>
        <polygon points="140,138 200,55 260,138 252,158 148,158" fill="#2D6A4F"/>
        <polygon points="135,132 165,68 195,148 185,198" fill="#40916C"/>
        <polygon points="265,132 245,65 218,148 222,198" fill="#40916C"/>
        <polygon points="135,132 122,162 132,222 158,202" fill="#1B4332"/>
        <polygon points="265,132 278,162 268,222 242,202" fill="#0F3322"/>
        <polygon points="168,148 210,95 248,148 235,178 182,178" fill="#52B788"/>

        <path d="M 182,188 Q 188,192 192,188" stroke="#1A1A1A" stroke-width="1.5" fill="none"/>
        <path d="M 208,188 Q 212,192 218,188" stroke="#1A1A1A" stroke-width="1.5" fill="none"/>
        <path d="M 192,218 Q 200,224 208,218" stroke="#4A3508" stroke-width="1.5" fill="none"/>
        <polygon points="200,198 203,205 197,205" fill="#4A3508"/>
      </g>
    </svg>
  </div>
</template>

<script setup>
const catchphrase = '这里没有信号，真好'
</script>

<style scoped>
.persona-wrap {
  position: relative;
  width: 320px;
  height: 416px;
}

.bubble {
  position: absolute;
  top: 10px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(255,255,255,0.15);
  backdrop-filter: blur(10px);
  padding: 10px 20px;
  border-radius: 20px;
  color: white;
  font-size: 14px;
  border: 1px solid rgba(255,255,255,0.2);
  opacity: 0;
  animation: bubble-in 4s ease-in-out infinite;
  white-space: nowrap;
  z-index: 10;
}

.persona-svg {
  width: 100%;
  height: 100%;
  filter: drop-shadow(0 10px 20px rgba(0,0,0,0.3));
}

.breathe {
  animation: breathe 3s ease-in-out infinite;
}

.head-tilt-back {
  animation: head-tilt-back 4s ease-in-out infinite;
  transform-origin: 200px 235px;
}

.spread-left {
  animation: spread-left 4s ease-in-out infinite;
  transform-origin: 150px 250px;
}

.spread-right {
  animation: spread-right 4s ease-in-out infinite;
  transform-origin: 250px 250px;
}

@keyframes breathe {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-3px); }
}

@keyframes head-tilt-back {
  0%, 20% { transform: rotate(0deg) translateY(0); }
  30%, 70% { transform: rotate(-15deg) translateY(-2px); }
  80%, 100% { transform: rotate(0deg) translateY(0); }
}

@keyframes spread-left {
  0%, 20% { transform: rotate(0deg); }
  30%, 70% { transform: rotate(-80deg); }
  80%, 100% { transform: rotate(0deg); }
}

@keyframes spread-right {
  0%, 20% { transform: rotate(0deg); }
  30%, 70% { transform: rotate(80deg); }
  80%, 100% { transform: rotate(0deg); }
}

@keyframes bubble-in {
  0%, 20% { opacity: 0; transform: translateX(-50%) translateY(10px); }
  30%, 70% { opacity: 1; transform: translateX(-50%) translateY(0); }
  80%, 100% { opacity: 0; transform: translateX(-50%) translateY(-5px); }
}
</style>