<template>
  <div class="persona-wrap">
    <div class="bubble">{{ catchphrase }}</div>
    <svg viewBox="0 0 400 520" class="persona-svg">
      <g class="shadow">
        <polygon points="100,512 300,512 280,525 120,525" fill="rgba(0,0,0,0.15)"/>
      </g>

      <g class="legs">
        <polygon points="170,400 195,400 192,512 167,512" fill="#4A90E2"/>
        <polygon points="167,512 192,512 188,525 163,525" fill="#357ABD"/>
        <polygon points="160,400 170,400 167,512 160,512" fill="#357ABD"/>
        <polygon points="205,400 230,400 227,512 202,512" fill="#357ABD"/>
        <polygon points="202,512 227,512 223,525 198,525" fill="#2E6DA4"/>
        <polygon points="230,400 240,400 237,512 227,512" fill="#2E6DA4"/>
      </g>

      <g class="torso breathe">
        <polygon points="150,390 250,390 245,400 155,400" fill="#F4D03F"/>
        <polygon points="150,250 200,250 200,330 155,390 145,390" fill="#FFD93D"/>
        <polygon points="200,250 250,250 255,390 245,390 200,330" fill="#FFE066"/>
        <polygon points="190,250 210,250 205,330 195,330" fill="#F4D03F"/>
        <polygon points="180,250 200,250 195,270 185,265" fill="#FFD93D"/>
        <polygon points="200,250 220,250 215,265 205,270" fill="#FFE066"/>
        <polygon points="160,300 180,300 178,330 158,330" fill="#FFD93D"/>
        <polygon points="220,300 240,300 242,330 222,330" fill="#FFE066"/>
      </g>

      <g class="arm-left sway">
        <polygon points="150,255 130,270 125,320 140,330" fill="#FFD93D"/>
        <polygon points="130,270 120,280 115,330 125,320" fill="#FFE066"/>
        <polygon points="120,280 110,300 112,340 115,330" fill="#F4D03F"/>
        <polygon points="112,340 118,345 125,340 120,335" fill="#FFD93D"/>
        <polygon points="110,345 125,345 122,355 112,355" fill="#FFE066"/>
        <polygon points="112,355 122,355 120,365 114,365" fill="#F0D5BE"/>
      </g>

      <g class="arm-right selfie">
        <polygon points="250,255 275,240 295,280 280,300" fill="#FFE066"/>
        <polygon points="275,240 290,225 315,265 295,280" fill="#FFD93D"/>
        <polygon points="290,225 305,210 330,250 315,265" fill="#F4D03F"/>
        <polygon points="330,250 325,258 315,255 320,247" fill="#FFE066"/>
        <polygon points="325,258 320,265 310,262 315,255" fill="#FFD93D"/>
        <polygon points="320,265 318,272 308,270 310,262" fill="#F0D5BE"/>
        <polygon points="305,200 340,195 345,235 310,240" fill="#1A1A1A"/>
        <polygon points="310,205 335,201 338,230 313,234" fill="#333333"/>
        <polygon points="315,210 325,208 327,218 317,220" fill="#FFFFFF" class="screen-flash"/>
      </g>

      <g class="neck head-tilt">
        <polygon points="185,220 215,220 212,250 188,250" fill="#E0C5AE"/>
        <polygon points="185,220 195,220 193,250 188,250" fill="#F0D5BE"/>
        <polygon points="205,220 215,220 212,250 207,250" fill="#D0B59E"/>
      </g>

      <g class="head head-tilt">
        <polygon points="170,155 230,155 228,200 225,220 200,225 175,220 172,200" fill="#F0D5BE"/>
        <polygon points="170,155 185,155 183,200 172,200" fill="#E0C5AE"/>
        <polygon points="215,155 230,155 228,200 217,200" fill="#D0B59E"/>
        <polygon points="175,220 200,225 225,220 222,232 200,238 178,232" fill="#E0C5AE"/>

        <polygon points="155,135 245,135 252,175 148,175" fill="#C49400"/>
        <polygon points="150,145 200,72 250,145 243,162 152,162" fill="#E8C547"/>
        <polygon points="145,140 170,82 192,148 182,188" fill="#D4A017"/>
        <polygon points="255,140 240,78 218,148 222,188" fill="#D4A017"/>
        <polygon points="145,140 132,168 140,215 158,195" fill="#C49400"/>
        <polygon points="255,140 268,168 260,215 242,195" fill="#B08400"/>
        <polygon points="168,148 208,108 248,148 235,172 182,172" fill="#E8C547"/>

        <path d="M 182,185 Q 188,180 192,185" stroke="#1A1A1A" stroke-width="1.5" fill="none"/>
        <path d="M 208,185 Q 212,180 218,185" stroke="#1A1A1A" stroke-width="1.5" fill="none"/>
        <polygon points="192,210 200,225 208,210" fill="#8B0000"/>
        <polygon points="200,198 203,205 197,205" fill="#D0B59E"/>
      </g>

      <g class="headphones">
        <polygon points="165,210 175,200 225,200 235,210" fill="none" stroke="#FF6B6B" stroke-width="3"/>
        <polygon points="165,210 175,205 175,225 165,230" fill="#FF6B6B"/>
        <polygon points="225,205 235,210 235,230 225,225" fill="#FF6B6B"/>
      </g>
    </svg>
  </div>
</template>

<script setup>
const catchphrase = '这个角度显腿长'
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
  animation: head-shake 4s ease-in-out infinite;
  transform-origin: 200px 235px;
}

.sway {
  animation: sway 4s ease-in-out infinite;
  transform-origin: 150px 250px;
}

.selfie {
  animation: selfie 3s ease-in-out infinite;
  transform-origin: 250px 250px;
}

.screen-flash {
  animation: screen-flash 3s ease-in-out infinite;
}

@keyframes breathe {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-3px); }
}

@keyframes head-shake {
  0%, 100% { transform: rotate(0deg) translateY(0); }
  25% { transform: rotate(-3deg) translateY(-2px); }
  75% { transform: rotate(3deg) translateY(-2px); }
}

@keyframes sway {
  0%, 100% { transform: rotate(0deg); }
  50% { transform: rotate(2deg); }
}

@keyframes selfie {
  0%, 100% { transform: rotate(0deg) translateX(0) translateY(0); }
  50% { transform: rotate(-15deg) translateX(25px) translateY(-5px); }
}

@keyframes screen-flash {
  0%, 40% { opacity: 0.3; }
  45% { opacity: 1; }
  50%, 100% { opacity: 0.3; }
}

@keyframes bubble-in {
  0%, 20% { opacity: 0; transform: translateX(-50%) translateY(10px); }
  30%, 70% { opacity: 1; transform: translateX(-50%) translateY(0); }
  80%, 100% { opacity: 0; transform: translateX(-50%) translateY(-5px); }
}
</style>