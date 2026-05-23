<template>
  <div class="persona-wrap">
    <div class="bubble">{{ catchphrase }}</div>
    <svg viewBox="0 0 400 520" class="persona-svg">
      <g class="shadow">
        <polygon points="100,512 300,512 280,525 120,525" fill="rgba(0,0,0,0.15)"/>
      </g>

      <g class="prop-moto">
        <polygon points="260,380 340,380 335,420 265,420" fill="#2A2A2A"/>
        <polygon points="265,420 335,420 330,440 270,440" fill="#1A1A1A"/>
        <polygon points="280,360 320,360 315,380 285,380" fill="#3A3A3A"/>
        <polygon points="310,400 325,395 330,430 315,435" fill="#4A4A4A"/>
        <polygon points="315,405 322,402 325,425 318,428" fill="#2A2A2A"/>
        <polygon points="270,400 285,395 290,430 275,435" fill="#4A4A4A"/>
        <polygon points="275,405 282,402 285,425 278,428" fill="#2A2A2A"/>
        <polygon points="290,340 310,335 312,345 292,350" fill="#C0C0C0"/>
        <polygon points="305,335 325,330 327,340 307,345" fill="#A0A0A0"/>
      </g>

      <g class="legs">
        <polygon points="170,400 195,400 192,512 167,512" fill="#4A90E2"/>
        <polygon points="167,512 192,512 188,525 163,525" fill="#357ABD"/>
        <polygon points="160,400 170,400 167,512 160,512" fill="#357ABD"/>
        <polygon points="205,400 230,400 227,460 202,460" fill="#357ABD"/>
        <polygon points="202,460 227,460 223,525 198,525" fill="#2E6DA4"/>
        <polygon points="230,400 240,400 237,460 227,460" fill="#2E6DA4"/>
      </g>

      <g class="torso breathe">
        <polygon points="150,390 250,390 245,400 155,400" fill="#0A0A0A"/>
        <polygon points="150,250 200,250 200,330 155,390 145,390" fill="#1A1A1A"/>
        <polygon points="200,250 250,250 255,390 245,390 200,330" fill="#2A2A2A"/>
        <polygon points="190,250 210,250 205,330 195,330" fill="#0A0A0A"/>
        <polygon points="180,250 200,250 195,270 185,265" fill="#1A1A1A"/>
        <polygon points="200,250 220,250 215,265 205,270" fill="#2A2A2A"/>
        <polygon points="198,250 202,250 201,330 199,330" fill="#C0C0C0"/>
      </g>

      <g class="arm-left sway">
        <polygon points="150,255 130,270 125,320 140,330" fill="#1A1A1A"/>
        <polygon points="130,270 120,280 115,330 125,320" fill="#2A2A2A"/>
        <polygon points="120,280 110,300 112,340 115,330" fill="#0A0A0A"/>
        <polygon points="112,340 118,345 125,340 120,335" fill="#1A1A1A"/>
        <polygon points="110,345 125,345 122,355 112,355" fill="#2A2A2A"/>
        <polygon points="112,355 122,355 120,365 114,365" fill="#E0D0C0"/>
      </g>

      <g class="arm-right throttle">
        <polygon points="250,255 275,240 295,280 280,300" fill="#2A2A2A"/>
        <polygon points="275,240 290,225 315,265 295,280" fill="#1A1A1A"/>
        <polygon points="290,225 305,210 330,250 315,265" fill="#0A0A0A"/>
        <polygon points="330,250 325,258 315,255 320,247" fill="#2A2A2A"/>
        <polygon points="325,258 320,265 310,262 315,255" fill="#1A1A1A"/>
        <polygon points="320,265 318,272 308,270 310,262" fill="#E0D0C0"/>
      </g>

      <g class="neck head-turn">
        <polygon points="185,220 215,220 212,250 188,250" fill="#D0C0B0"/>
        <polygon points="185,220 195,220 193,250 188,250" fill="#E0D0C0"/>
        <polygon points="205,220 215,220 212,250 207,250" fill="#C0B0A0"/>
      </g>

      <g class="head head-turn">
        <polygon points="170,155 230,155 228,200 225,220 200,225 175,220 172,200" fill="#E0D0C0"/>
        <polygon points="170,155 185,155 183,200 172,200" fill="#D0C0B0"/>
        <polygon points="215,155 230,155 228,200 217,200" fill="#C0B0A0"/>
        <polygon points="175,220 200,225 225,220 222,232 200,238 178,232" fill="#D0C0B0"/>

        <polygon points="155,135 245,135 252,175 148,175" fill="#00B4D8"/>
        <polygon points="150,145 208,62 255,145 248,162 152,162" fill="#48CAE4"/>
        <polygon points="145,140 172,72 192,148 182,192" fill="#90E0EF"/>
        <polygon points="255,140 248,68 218,148 228,192" fill="#90E0EF"/>
        <polygon points="145,140 132,168 140,215 158,195" fill="#00B4D8"/>
        <polygon points="255,140 268,168 260,215 242,195" fill="#0096C7"/>
        <polygon points="168,148 210,102 248,148 235,172 182,172" fill="#48CAE4"/>

        <circle cx="188" cy="188" r="2.5" fill="#1A1A1A"/>
        <circle cx="212" cy="188" r="2.5" fill="#1A1A1A"/>
        <path d="M 192,215 Q 200,222 208,215" stroke="#B0A090" stroke-width="1.5" fill="none"/>
        <polygon points="200,198 203,205 197,205" fill="#C0B0A0"/>
      </g>
    </svg>
  </div>
</template>

<script setup>
const catchphrase = '风是自由的，我也是'
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

.head-turn {
  animation: head-turn 4s ease-in-out infinite;
  transform-origin: 200px 235px;
}

.sway {
  animation: sway 4s ease-in-out infinite;
  transform-origin: 150px 250px;
}

.throttle {
  animation: throttle 3s ease-in-out infinite;
  transform-origin: 250px 250px;
}

@keyframes breathe {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-3px); }
}

@keyframes head-turn {
  0%, 100% { transform: rotate(0deg) translateY(0); }
  50% { transform: rotate(10deg) translateY(-1px); }
}

@keyframes sway {
  0%, 100% { transform: rotate(0deg); }
  50% { transform: rotate(2deg); }
}

@keyframes throttle {
  0%, 100% { transform: rotate(0deg) translateY(0); }
  50% { transform: rotate(-20deg) translateY(-2px); }
}

@keyframes bubble-in {
  0%, 20% { opacity: 0; transform: translateX(-50%) translateY(10px); }
  30%, 70% { opacity: 1; transform: translateX(-50%) translateY(0); }
  80%, 100% { opacity: 0; transform: translateX(-50%) translateY(-5px); }
}
</style>
