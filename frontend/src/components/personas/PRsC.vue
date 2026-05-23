<template>
  <div class="persona-wrap">
    <div class="bubble">{{ catchphrase }}</div>
    <svg viewBox="0 0 400 520" class="persona-svg">
      <g class="shadow">
        <polygon points="100,512 300,512 280,525 120,525" fill="rgba(0,0,0,0.15)"/>
      </g>

      <g class="legs">
        <polygon points="170,400 195,400 192,512 167,512" fill="#2D1B4E"/>
        <polygon points="167,512 192,512 188,525 163,525" fill="#1A0A2E"/>
        <polygon points="160,400 170,400 167,512 160,512" fill="#1A0A2E"/>
        <polygon points="205,400 230,400 227,512 202,512" fill="#1A0A2E"/>
        <polygon points="202,512 227,512 223,525 198,525" fill="#0F0F18"/>
        <polygon points="230,400 240,400 237,512 227,512" fill="#0F0F18"/>
      </g>

      <g class="torso breathe">
        <polygon points="150,390 250,390 245,400 155,400" fill="#1A0A2E"/>
        <polygon points="150,250 200,250 200,330 155,390 145,390" fill="#2D1B4E"/>
        <polygon points="200,250 250,250 255,390 245,390 200,330" fill="#4A0E4E"/>
        <polygon points="190,250 210,250 205,330 195,330" fill="#1A0A2E"/>
        <polygon points="180,250 200,250 195,270 185,265" fill="#2D1B4E"/>
        <polygon points="200,250 220,250 215,265 205,270" fill="#4A0E4E"/>
        <polygon points="192,265 208,265 205,275 195,275" fill="#1A1A1A"/>
        <polygon points="195,275 205,275 202,285 198,285" fill="#0A0A0A"/>
      </g>

      <g class="arm-left sway">
        <polygon points="150,255 130,270 125,320 140,330" fill="#2D1B4E"/>
        <polygon points="130,270 120,280 115,330 125,320" fill="#4A0E4E"/>
        <polygon points="120,280 110,300 112,340 115,330" fill="#1A0A2E"/>
        <polygon points="112,340 118,345 125,340 120,335" fill="#2D1B4E"/>
        <polygon points="110,345 125,345 122,355 112,355" fill="#4A0E4E"/>
        <polygon points="112,355 122,355 120,365 114,365" fill="#F0D5BE"/>
        <polygon points="108,300 120,298 122,312 110,314" fill="#FFD700"/>
        <circle cx="115" cy="306" r="4" fill="#1A1A1A"/>
        <line x1="115" y1="306" x2="115" y2="303" stroke="#FFD700" stroke-width="1"/>
      </g>

      <g class="arm-right present-card">
        <polygon points="250,255 275,275 285,325 265,335" fill="#4A0E4E"/>
        <polygon points="275,275 290,285 300,335 285,325" fill="#2D1B4E"/>
        <polygon points="290,285 305,305 310,345 300,335" fill="#1A0A2E"/>
        <polygon points="310,345 302,352 292,345 300,338" fill="#4A0E4E"/>
        <polygon points="312,350 295,350 298,360 310,360" fill="#2D1B4E"/>
        <polygon points="310,360 298,360 300,370 308,370" fill="#F0D5BE"/>
        <polygon points="305,335 345,325 350,345 310,355" fill="#0A0A0A"/>
        <polygon points="310,355 350,345 352,355 312,365" fill="#000000"/>
        <polygon points="308,340 340,332 341,336 309,344" fill="#FFD700"/>
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

        <polygon points="158,138 242,138 248,178 152,178" fill="#4B0082"/>
        <polygon points="152,148 200,82 248,148 242,162 158,162" fill="#6A0DAD"/>
        <polygon points="148,142 172,88 190,148 182,185" fill="#8A2BE2"/>
        <polygon points="252,142 238,88 218,148 222,185" fill="#7B1FA2"/>
        <polygon points="148,142 138,168 145,212 162,192" fill="#4B0082"/>
        <polygon points="252,142 262,168 255,212 238,192" fill="#3A0066"/>
        <polygon points="172,148 210,118 242,148 230,168 185,168" fill="#7A1DBD"/>

        <circle cx="188" cy="188" r="2" fill="#1A1A1A"/>
        <circle cx="212" cy="188" r="2" fill="#1A1A1A"/>
        <path d="M 192,215 Q 200,220 208,215" stroke="#C0A58E" stroke-width="1.5" fill="none"/>
        <polygon points="200,198 203,205 197,205" fill="#D0B59E"/>
      </g>
    </svg>
  </div>
</template>

<script setup>
const catchphrase = '刷卡，不用密码'
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

.sway {
  animation: sway 4s ease-in-out infinite;
  transform-origin: 150px 250px;
}

.present-card {
  animation: present-card 3s ease-in-out infinite;
  transform-origin: 250px 250px;
}

@keyframes breathe {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-3px); }
}

@keyframes head-tilt {
  0%, 100% { transform: rotate(0deg) translateY(0); }
  50% { transform: rotate(2deg) translateY(-1px); }
}

@keyframes sway {
  0%, 100% { transform: rotate(0deg); }
  50% { transform: rotate(2deg); }
}

@keyframes present-card {
  0%, 100% { transform: rotate(0deg) translateX(0); }
  50% { transform: rotate(-5deg) translateX(20px); }
}

@keyframes bubble-in {
  0%, 20% { opacity: 0; transform: translateX(-50%) translateY(10px); }
  30%, 70% { opacity: 1; transform: translateX(-50%) translateY(0); }
  80%, 100% { opacity: 0; transform: translateX(-50%) translateY(-5px); }
}
</style>