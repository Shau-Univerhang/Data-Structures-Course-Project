<template>
  <div class="persona-wrap">
    <div class="bubble">{{ catchphrase }}</div>
    <svg viewBox="0 0 400 520" class="persona-svg">
      <g class="shadow">
        <polygon points="100,512 300,512 280,525 120,525" fill="rgba(0,0,0,0.15)"/>
      </g>

      <g class="legs">
        <polygon points="170,400 195,400 192,512 167,512" fill="#4A4A4A"/>
        <polygon points="167,512 192,512 188,525 163,525" fill="#5A5A5A"/>
        <polygon points="160,400 170,400 167,512 160,512" fill="#5A5A5A"/>
        <polygon points="205,400 230,400 227,512 202,512" fill="#5A5A5A"/>
        <polygon points="202,512 227,512 223,525 198,525" fill="#3A3A3A"/>
        <polygon points="230,400 240,400 237,512 227,512" fill="#3A3A3A"/>
      </g>

      <g class="torso breathe">
        <polygon points="150,390 250,390 245,400 155,400" fill="#8A8A7A"/>
        <polygon points="150,250 200,250 200,330 155,390 145,390" fill="#6B705C"/>
        <polygon points="200,250 250,250 255,390 245,390 200,330" fill="#A5A58D"/>
        <polygon points="190,250 210,250 205,330 195,330" fill="#8A8A7A"/>
        <polygon points="180,250 200,250 195,270 185,265" fill="#6B705C"/>
        <polygon points="200,250 220,250 215,265 205,270" fill="#A5A58D"/>
        <polygon points="155,300 175,300 173,340 153,340" fill="#6B705C"/>
        <polygon points="225,300 245,300 247,340 227,340" fill="#5A5F4B"/>
      </g>

      <g class="arm-left point-map">
        <polygon points="150,255 130,270 125,320 140,330" fill="#6B705C"/>
        <polygon points="130,270 120,280 115,330 125,320" fill="#A5A58D"/>
        <polygon points="120,280 110,300 112,340 115,330" fill="#8A8A7A"/>
        <polygon points="112,340 118,345 125,340 120,335" fill="#6B705C"/>
        <polygon points="110,345 125,345 122,355 112,355" fill="#A5A58D"/>
        <polygon points="112,355 122,355 120,365 114,365" fill="#D0B59E"/>
      </g>

      <g class="arm-right reach-backpack">
        <polygon points="250,255 275,275 285,325 265,335" fill="#A5A58D"/>
        <polygon points="275,275 290,285 300,335 285,325" fill="#6B705C"/>
        <polygon points="290,285 305,305 310,345 300,335" fill="#8A8A7A"/>
        <polygon points="310,345 302,352 292,345 300,338" fill="#A5A58D"/>
        <polygon points="312,350 295,350 298,360 310,360" fill="#6B705C"/>
        <polygon points="310,360 298,360 300,370 308,370" fill="#D0B59E"/>
      </g>

      <g class="backpack">
        <polygon points="120,260 155,252 162,340 127,348" fill="#5A5A5A"/>
        <polygon points="127,348 162,340 168,365 133,373" fill="#4A4A4A"/>
        <polygon points="130,280 150,276 155,330 135,334" fill="#6B6B6B"/>
        <polygon points="125,250 150,245 155,260 130,265" fill="#7A7A7A"/>
        <polygon points="115,320 125,318 128,350 118,352" fill="#4682B4"/>
        <polygon points="155,320 165,318 168,350 158,352" fill="#D4AF37"/>
      </g>

      <g class="prop-map scroll-map">
        <polygon points="80,320 130,315 135,365 85,370" fill="#F5F0E0"/>
        <polygon points="85,370 135,365 140,375 90,380" fill="#E8E0D0"/>
        <polygon points="90,330 125,327 128,355 93,358" fill="#C4D4A0"/>
        <polygon points="95,340 115,338 117,348 97,350" fill="#8B7355"/>
      </g>

      <g class="neck head-tilt">
        <polygon points="185,220 215,220 212,250 188,250" fill="#D0B59E"/>
        <polygon points="185,220 195,220 193,250 188,250" fill="#E0C5AE"/>
        <polygon points="205,220 215,220 212,250 207,250" fill="#C0A58E"/>
      </g>

      <g class="head head-tilt">
        <polygon points="170,155 230,155 228,200 225,220 200,225 175,220 172,200" fill="#E0C5AE"/>
        <polygon points="170,155 185,155 183,200 172,200" fill="#D0B59E"/>
        <polygon points="215,155 230,155 228,200 217,200" fill="#C0A58E"/>
        <polygon points="175,220 200,225 225,220 222,232 200,238 178,232" fill="#D0B59E"/>

        <polygon points="152,132 248,132 255,172 145,172" fill="#6B6B6B"/>
        <polygon points="145,142 200,68 255,142 248,158 152,158" fill="#8A8A8A"/>
        <polygon points="140,138 172,78 195,148 185,188" fill="#A0A0A0"/>
        <polygon points="260,138 245,72 220,148 225,188" fill="#A0A0A0"/>
        <polygon points="140,138 128,162 138,208 158,192" fill="#6B6B6B"/>
        <polygon points="260,138 272,162 262,208 242,192" fill="#5A5A5A"/>
        <polygon points="168,148 208,108 248,148 235,172 182,172" fill="#9A9A9A"/>

        <circle cx="188" cy="188" r="2" fill="#1A1A1A"/>
        <path d="M 208,186 Q 212,190 218,186" stroke="#1A1A1A" stroke-width="1.5" fill="none"/>
        <path d="M 192,218 Q 200,224 208,218" stroke="#B09070" stroke-width="1.5" fill="none"/>
        <polygon points="200,198 203,205 197,205" fill="#C0A58E"/>
      </g>
    </svg>
  </div>
</template>

<script setup>
const catchphrase = '前面应该有WiFi'
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

.reach-backpack {
  animation: reach-backpack 4s ease-in-out infinite;
  transform-origin: 250px 250px;
}

.point-map {
  animation: point-map 4s ease-in-out infinite;
  transform-origin: 150px 250px;
}

.scroll-map {
  animation: scroll-map 4s ease-in-out infinite;
  transform-origin: 110px 340px;
}

@keyframes breathe {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-3px); }
}

@keyframes head-tilt {
  0%, 100% { transform: rotate(0deg) translateY(0); }
  50% { transform: rotate(-2deg) translateY(-1px); }
}

@keyframes reach-backpack {
  0%, 100% { transform: rotate(0deg); }
  25% { transform: rotate(-20deg); }
  50% { transform: rotate(-15deg); }
  75% { transform: rotate(-18deg); }
}

@keyframes point-map {
  0%, 100% { transform: rotate(0deg); }
  25% { transform: rotate(5deg); }
  50% { transform: rotate(10deg); }
  75% { transform: rotate(8deg); }
}

@keyframes scroll-map {
  0%, 20% { transform: scale(0); opacity: 0; }
  30% { transform: scale(1); opacity: 1; }
  70% { transform: scale(1); opacity: 1; }
  80%, 100% { transform: scale(0); opacity: 0; }
}

@keyframes bubble-in {
  0%, 20% { opacity: 0; transform: translateX(-50%) translateY(10px); }
  30%, 70% { opacity: 1; transform: translateX(-50%) translateY(0); }
  80%, 100% { opacity: 0; transform: translateX(-50%) translateY(-5px); }
}
</style>