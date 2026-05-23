<template>
  <div class="persona-wrap">
    <div class="bubble">{{ catchphrase }}</div>
    <svg viewBox="0 0 400 520" class="persona-svg">
      <g class="shadow">
        <polygon points="100,512 300,512 280,525 120,525" fill="rgba(0,0,0,0.15)"/>
      </g>

      <g class="legs">
        <polygon points="170,400 195,400 192,512 167,512" fill="#1A1A1A"/>
        <polygon points="167,512 192,512 188,525 163,525" fill="#0A0A0A"/>
        <polygon points="160,400 170,400 167,512 160,512" fill="#0A0A0A"/>
        <polygon points="205,400 230,400 227,512 202,512" fill="#0A0A0A"/>
        <polygon points="202,512 227,512 223,525 198,525" fill="#000000"/>
        <polygon points="230,400 240,400 237,512 227,512" fill="#000000"/>
      </g>

      <g class="torso breathe">
        <polygon points="150,390 250,390 245,400 155,400" fill="#0A0A0A"/>
        <polygon points="150,250 200,250 200,330 155,390 145,390" fill="#2A2A2A"/>
        <polygon points="200,250 250,250 255,390 245,390 200,330" fill="#1A1A1A"/>
        <polygon points="190,250 210,250 205,330 195,330" fill="#0A0A0A"/>
        <polygon points="180,250 200,250 195,270 185,265" fill="#2A2A2A"/>
        <polygon points="200,250 220,250 215,265 205,270" fill="#1A1A1A"/>
        <polygon points="150,300 170,300 168,340 148,340" fill="#0A0A0A"/>
        <polygon points="230,300 250,300 252,340 232,340" fill="#000000"/>
      </g>

      <g class="arm-left sway">
        <polygon points="150,255 130,270 125,320 140,330" fill="#2A2A2A"/>
        <polygon points="130,270 120,280 115,330 125,320" fill="#1A1A1A"/>
        <polygon points="120,280 110,300 112,340 115,330" fill="#0A0A0A"/>
        <polygon points="112,340 118,345 125,340 120,335" fill="#2A2A2A"/>
        <polygon points="110,345 125,345 122,355 112,355" fill="#1A1A1A"/>
        <polygon points="112,355 122,355 120,365 114,365" fill="#E0D0C0"/>
      </g>

      <g class="arm-right tool-pull">
        <polygon points="250,255 275,275 285,325 265,335" fill="#1A1A1A"/>
        <polygon points="275,275 290,285 300,335 285,325" fill="#0A0A0A"/>
        <polygon points="290,285 305,305 310,345 300,335" fill="#000000"/>
        <polygon points="310,345 302,352 292,345 300,338" fill="#1A1A1A"/>
        <polygon points="312,350 295,350 298,360 310,360" fill="#0A0A0A"/>
        <polygon points="310,360 298,360 300,370 308,370" fill="#E0D0C0"/>
        <polygon points="300,340 330,335 335,350 305,355" fill="#C0C0C0"/>
        <polygon points="305,355 335,350 338,358 308,363" fill="#A0A0A0"/>
      </g>

      <g class="neck head-tilt">
        <polygon points="185,220 215,220 212,250 188,250" fill="#D0C0B0"/>
        <polygon points="185,220 195,220 193,250 188,250" fill="#E0D0C0"/>
        <polygon points="205,220 215,220 212,250 207,250" fill="#C0B0A0"/>
      </g>

      <g class="head head-tilt">
        <polygon points="170,155 230,155 228,200 225,220 200,225 175,220 172,200" fill="#E0D0C0"/>
        <polygon points="170,155 185,155 183,200 172,200" fill="#D0C0B0"/>
        <polygon points="215,155 230,155 228,200 217,200" fill="#C0B0A0"/>
        <polygon points="175,220 200,225 225,220 222,232 200,238 178,232" fill="#D0C0B0"/>

        <polygon points="158,138 242,138 248,178 152,178" fill="#707070"/>
        <polygon points="152,148 200,78 248,148 242,162 158,162" fill="#B0B0B0"/>
        <polygon points="148,142 172,88 190,148 182,182" fill="#909090"/>
        <polygon points="252,142 232,82 212,148 222,186" fill="#909090"/>
        <polygon points="148,142 135,168 142,212 162,192" fill="#707070"/>
        <polygon points="252,142 265,168 258,212 238,192" fill="#606060"/>
        <polygon points="172,148 205,108 238,148 228,168 182,168" fill="#A0A0A0"/>

        <circle cx="188" cy="188" r="1.5" fill="#1A1A1A"/>
        <circle cx="212" cy="188" r="1.5" fill="#1A1A1A"/>
        <line x1="195" y1="218" x2="205" y2="218" stroke="#B0A090" stroke-width="1"/>
        <polygon points="200,198 202,203 198,203" fill="#C0B0A0"/>
      </g>
    </svg>
  </div>
</template>

<script setup>
const catchphrase = '正好能用'
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

.tool-pull {
  animation: tool-pull 4s ease-in-out infinite;
  transform-origin: 250px 250px;
}

@keyframes breathe {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-3px); }
}

@keyframes head-tilt {
  0%, 100% { transform: rotate(0deg) translateY(0); }
  50% { transform: rotate(-1deg) translateY(0); }
}

@keyframes sway {
  0%, 100% { transform: rotate(0deg); }
  50% { transform: rotate(2deg); }
}

@keyframes tool-pull {
  0%, 100% { transform: rotate(0deg) translateX(0); }
  25% { transform: rotate(-8deg) translateX(-5px); }
  50% { transform: rotate(-5deg) translateX(0); }
  75% { transform: rotate(-7deg) translateX(-3px); }
}

@keyframes bubble-in {
  0%, 20% { opacity: 0; transform: translateX(-50%) translateY(10px); }
  30%, 70% { opacity: 1; transform: translateX(-50%) translateY(0); }
  80%, 100% { opacity: 0; transform: translateX(-50%) translateY(-5px); }
}
</style>