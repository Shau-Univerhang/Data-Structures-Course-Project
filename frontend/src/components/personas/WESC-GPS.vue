<template>
  <div class="persona-wrap">
    <div class="bubble">{{ catchphrase }}</div>
    <svg viewBox="0 0 400 520" class="persona-svg">
      <g class="shadow">
        <polygon points="100,512 300,512 280,525 120,525" fill="rgba(0,0,0,0.15)"/>
      </g>

      <g class="legs">
        <polygon points="170,400 195,400 192,512 167,512" fill="#004E89"/>
        <polygon points="167,512 192,512 188,525 163,525" fill="#003F7F"/>
        <polygon points="160,400 170,400 167,512 160,512" fill="#003F7F"/>
        <polygon points="205,400 230,400 227,512 202,512" fill="#003F7F"/>
        <polygon points="202,512 227,512 223,525 198,525" fill="#002F5F"/>
        <polygon points="230,400 240,400 237,512 227,512" fill="#002F5F"/>
      </g>

      <g class="torso breathe">
        <polygon points="150,390 250,390 245,400 155,400" fill="#E85D04"/>
        <polygon points="150,250 200,250 200,330 155,390 145,390" fill="#FF6B35"/>
        <polygon points="200,250 250,250 255,390 245,390 200,330" fill="#FF8C42"/>
        <polygon points="190,250 210,250 205,330 195,330" fill="#E85D04"/>
        <polygon points="180,250 200,250 195,270 185,265" fill="#FF6B35"/>
        <polygon points="200,250 220,250 215,265 205,270" fill="#FF8C42"/>
        <polygon points="170,240 200,235 230,240 225,255 200,250 175,255" fill="#FF6B35"/>
        <polygon points="175,245 200,240 225,245 220,250 200,248 180,250" fill="#E85D04"/>
      </g>

      <g class="arm-left wave-left">
        <polygon points="150,255 125,240 105,280 120,300" fill="#FF6B35"/>
        <polygon points="125,240 110,225 85,265 105,280" fill="#FF8C42"/>
        <polygon points="110,225 95,210 70,250 85,265" fill="#E85D04"/>
        <polygon points="70,250 75,258 85,255 80,247" fill="#FF6B35"/>
        <polygon points="75,258 80,265 90,262 85,255" fill="#FF8C42"/>
        <polygon points="80,265 82,272 92,270 90,262" fill="#E8C4A0"/>
      </g>

      <g class="arm-right wave-right">
        <polygon points="250,255 280,230 300,270 280,295" fill="#FF8C42"/>
        <polygon points="280,230 300,210 325,250 305,270" fill="#FF6B35"/>
        <polygon points="300,210 320,190 345,230 325,250" fill="#E85D04"/>
        <polygon points="345,230 338,238 328,235 335,227" fill="#FF8C42"/>
        <polygon points="338,238 332,245 322,242 328,235" fill="#FF6B35"/>
        <polygon points="332,245 328,252 318,250 322,242" fill="#E8C4A0"/>
      </g>

      <g class="neck head-tilt">
        <polygon points="185,220 215,220 212,250 188,250" fill="#D8B490"/>
        <polygon points="185,220 195,220 193,250 188,250" fill="#E8C4A0"/>
        <polygon points="205,220 215,220 212,250 207,250" fill="#C8A480"/>
      </g>

      <g class="head head-tilt">
        <polygon points="170,155 230,155 228,200 225,220 200,225 175,220 172,200" fill="#E8C4A0"/>
        <polygon points="170,155 185,155 183,200 172,200" fill="#D8B490"/>
        <polygon points="215,155 230,155 228,200 217,200" fill="#C8A480"/>
        <polygon points="175,220 200,225 225,220 222,232 200,238 178,232" fill="#D8B490"/>

        <polygon points="152,132 248,132 255,172 145,172" fill="#E85D04"/>
        <polygon points="145,142 200,58 255,142 248,158 152,158" fill="#FF6B35"/>
        <polygon points="140,138 172,78 195,148 185,188" fill="#FF8C42"/>
        <polygon points="260,138 245,72 220,148 225,188" fill="#FF8C42"/>
        <polygon points="140,138 128,162 138,208 158,192" fill="#E85D04"/>
        <polygon points="260,138 272,162 262,208 242,192" fill="#D04A00"/>
        <polygon points="168,148 208,108 248,148 235,172 182,172" fill="#FFA06B"/>

        <circle cx="188" cy="188" r="3" fill="#1A1A1A"/>
        <circle cx="212" cy="188" r="3" fill="#1A1A1A"/>
        <path d="M 192,215 Q 200,222 208,215" stroke="#B89470" stroke-width="1.5" fill="none"/>
        <polygon points="200,198 203,205 197,205" fill="#C8A480"/>
      </g>

      <g class="prop-compass">
        <polygon points="185,260 215,260 218,290 182,290" fill="#C0C0C0"/>
        <polygon points="188,265 212,265 214,285 186,285" fill="#E0E0E0"/>
        <polygon points="198,270 202,270 200,280" fill="#D00000"/>
        <polygon points="200,275 205,275 202,282" fill="#1A1A1A"/>
      </g>

      <g class="prop-whistle">
        <polygon points="165,270 175,268 178,278 168,280" fill="#FFD700"/>
        <polygon points="168,273 173,272 174,276 169,277" fill="#FFA500"/>
      </g>
    </svg>
  </div>
</template>

<script setup>
const catchphrase = '跟我走，这边近'
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

.head-tilt {
  animation: head-tilt 4s ease-in-out infinite;
  transform-origin: 200px 235px;
}

.wave-left {
  animation: wave-left 3s ease-in-out infinite;
  transform-origin: 150px 250px;
}

.wave-right {
  animation: wave-right 3s ease-in-out infinite;
  transform-origin: 250px 250px;
}

@keyframes breathe {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-3px); }
}

@keyframes head-tilt {
  0%, 100% { transform: rotate(0deg) translateY(0); }
  50% { transform: rotate(5deg) translateY(-1px); }
}

@keyframes wave-left {
  0%, 100% { transform: rotate(0deg); }
  50% { transform: rotate(30deg); }
}

@keyframes wave-right {
  0%, 100% { transform: rotate(0deg); }
  50% { transform: rotate(-45deg); }
}

@keyframes bubble-in {
  0%, 20% { opacity: 0; transform: translateX(-50%) translateY(10px); }
  30%, 70% { opacity: 1; transform: translateX(-50%) translateY(0); }
  80%, 100% { opacity: 0; transform: translateX(-50%) translateY(-5px); }
}
</style>