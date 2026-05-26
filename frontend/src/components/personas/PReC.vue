<template>
  <div class="persona-wrap">
    <div class="bubble">{{ catchphrase }}</div>
    <svg viewBox="0 0 400 520" class="persona-svg">
      <g class="shadow">
        <polygon points="100,512 300,512 280,525 120,525" fill="rgba(0,0,0,0.15)"/>
      </g>

      <g class="legs">
        <polygon points="170,400 195,400 192,512 167,512" fill="#FFFFFF"/>
        <polygon points="167,512 192,512 188,525 163,525" fill="#F0F0F0"/>
        <polygon points="160,400 170,400 167,512 160,512" fill="#F0F0F0"/>
        <polygon points="205,400 230,400 227,512 202,512" fill="#F0F0F0"/>
        <polygon points="202,512 227,512 223,525 198,525" fill="#E0E0E0"/>
        <polygon points="230,400 240,400 237,512 227,512" fill="#E0E0E0"/>
      </g>

      <g class="torso breathe">
        <polygon points="150,390 250,390 245,400 155,400" fill="#FF69B4"/>
        <polygon points="150,250 200,250 200,330 155,390 145,390" fill="#FFB6C1"/>
        <polygon points="200,250 250,250 255,390 245,390 200,330" fill="#FFC0CB"/>
        <polygon points="190,250 210,250 205,330 195,330" fill="#FF69B4"/>
        <polygon points="180,250 200,250 195,270 185,265" fill="#FFB6C1"/>
        <polygon points="200,250 220,250 215,265 205,270" fill="#FFC0CB"/>
      </g>

      <g class="arm-left camera-hold">
        <polygon points="150,255 125,240 105,280 120,300" fill="#FFB6C1"/>
        <polygon points="125,240 110,225 85,265 105,280" fill="#FFC0CB"/>
        <polygon points="110,225 95,210 70,250 85,265" fill="#FF69B4"/>
        <polygon points="70,250 75,258 85,255 80,247" fill="#FFB6C1"/>
        <polygon points="75,258 80,265 90,262 85,255" fill="#FFC0CB"/>
        <polygon points="80,265 82,272 92,270 90,262" fill="#FFD1DC"/>
      </g>

      <g class="arm-right camera-hold">
        <polygon points="250,255 275,240 295,280 280,300" fill="#FFC0CB"/>
        <polygon points="275,240 290,225 315,265 295,280" fill="#FF69B4"/>
        <polygon points="290,225 305,210 330,250 315,265" fill="#FFB6C1"/>
        <polygon points="330,250 325,258 315,255 320,247" fill="#FFC0CB"/>
        <polygon points="325,258 320,265 310,262 315,255" fill="#FF69B4"/>
        <polygon points="320,265 318,272 308,270 310,262" fill="#FFD1DC"/>
        <polygon points="60,230 100,225 105,255 65,260" fill="#1A1A1A"/>
        <polygon points="65,235 95,231 98,250 68,254" fill="#333333"/>
        <circle cx="82" cy="242" r="8" fill="#4A4A4A"/>
        <circle cx="82" cy="242" r="5" fill="#2A2A2A"/>
        <circle cx="82" cy="242" r="2" fill="#1A1A1A"/>
        <polygon points="75,228 80,227 81,232 76,233" fill="#FFFFFF" class="flash-blink"/>
      </g>

      <g class="neck head-tilt">
        <polygon points="185,220 215,220 212,250 188,250" fill="#FFC0CB"/>
        <polygon points="185,220 195,220 193,250 188,250" fill="#FFD1DC"/>
        <polygon points="205,220 215,220 212,250 207,250" fill="#F0B0BB"/>
      </g>

      <g class="head head-tilt">
        <polygon points="170,155 230,155 228,200 225,220 200,225 175,220 172,200" fill="#FFD1DC"/>
        <polygon points="170,155 185,155 183,200 172,200" fill="#FFC0CB"/>
        <polygon points="215,155 230,155 228,200 217,200" fill="#F0B0BB"/>
        <polygon points="175,220 200,225 225,220 222,232 200,238 178,232" fill="#FFC0CB"/>

        <polygon points="155,135 245,135 252,175 148,175" fill="#FF1493"/>
        <polygon points="150,145 205,72 255,145 248,162 152,162" fill="#FF69B4"/>
        <polygon points="145,140 168,82 190,148 182,188" fill="#FF85C1"/>
        <polygon points="255,140 240,78 218,148 225,188" fill="#FF85C1"/>
        <polygon points="145,140 132,168 140,215 158,195" fill="#FF1493"/>
        <polygon points="255,140 268,168 260,215 242,195" fill="#E01090"/>
        <polygon points="168,148 205,112 242,148 230,170 180,170" fill="#FF99CC"/>

        <circle cx="188" cy="188" r="2.5" fill="#1A1A1A"/>
        <circle cx="212" cy="188" r="2.5" fill="#1A1A1A"/>
        <path d="M 192,215 Q 200,220 208,215" stroke="#E0A0A0" stroke-width="1.5" fill="none"/>
        <polygon points="200,198 203,205 197,205" fill="#F0B0BB"/>
      </g>
    </svg>
  </div>
</template>

<script setup>
const catchphrase = '光线不对，往左一点'
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

.camera-hold {
  animation: camera-hold 3s ease-in-out infinite;
  transform-origin: 250px 250px;
}

.flash-blink {
  animation: flash 2s ease-in-out infinite;
}

@keyframes breathe {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-3px); }
}

@keyframes head-tilt {
  0%, 100% { transform: rotate(0deg) translateY(0); }
  50% { transform: rotate(-2deg) translateY(-1px); }
}

@keyframes camera-hold {
  0%, 100% { transform: rotate(0deg) translateY(0); }
  50% { transform: rotate(-5deg) translateY(-15px); }
}

@keyframes flash {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.2; }
}

@keyframes bubble-in {
  0%, 20% { opacity: 0; transform: translateX(-50%) translateY(10px); }
  30%, 70% { opacity: 1; transform: translateX(-50%) translateY(0); }
  80%, 100% { opacity: 0; transform: translateX(-50%) translateY(-5px); }
}
</style>
