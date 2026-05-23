<template>
  <div class="persona-wrap">
    <div class="bubble">{{ catchphrase }}</div>
    <svg viewBox="0 0 400 520" class="persona-svg">
      <g class="shadow">
        <polygon points="100,512 300,512 280,525 120,525" fill="rgba(0,0,0,0.15)"/>
      </g>

      <g class="legs">
        <polygon points="170,400 195,400 192,512 167,512" fill="#9D4EDD"/>
        <polygon points="167,512 192,512 188,525 163,525" fill="#7B2CBF"/>
        <polygon points="160,400 170,400 167,512 160,512" fill="#7B2CBF"/>
        <polygon points="205,400 230,400 227,512 202,512" fill="#7B2CBF"/>
        <polygon points="202,512 227,512 223,525 198,525" fill="#5A189A"/>
        <polygon points="230,400 240,400 237,512 227,512" fill="#5A189A"/>
      </g>

      <g class="torso breathe">
        <polygon points="150,390 250,390 245,400 155,400" fill="#7209B7"/>
        <polygon points="150,250 200,250 200,330 155,390 145,390" fill="#F72585"/>
        <polygon points="200,250 250,250 255,390 245,390 200,330" fill="#B5179E"/>
        <polygon points="190,250 210,250 205,330 195,330" fill="#7209B7"/>
        <polygon points="180,250 200,250 195,270 185,265" fill="#F72585"/>
        <polygon points="200,250 220,250 215,265 205,270" fill="#B5179E"/>
        <polygon points="155,290 175,288 173,308 153,310" fill="#3A0CA3"/>
        <polygon points="225,340 245,338 247,358 227,360" fill="#7209B7"/>
      </g>

      <g class="arm-left sway">
        <polygon points="150,255 130,270 125,320 140,330" fill="#F72585"/>
        <polygon points="130,270 120,280 115,330 125,320" fill="#B5179E"/>
        <polygon points="120,280 110,300 112,340 115,330" fill="#7209B7"/>
        <polygon points="112,340 118,345 125,340 120,335" fill="#F72585"/>
        <polygon points="110,345 125,345 122,355 112,355" fill="#B5179E"/>
        <polygon points="112,355 122,355 120,365 114,365" fill="#E0C5AE"/>
      </g>

      <g class="arm-right shutter">
        <polygon points="250,255 270,275 280,325 265,335" fill="#B5179E"/>
        <polygon points="270,275 285,285 295,335 280,325" fill="#F72585"/>
        <polygon points="285,285 300,305 305,345 295,335" fill="#7209B7"/>
        <polygon points="305,345 298,352 288,345 295,338" fill="#B5179E"/>
        <polygon points="307,350 292,350 295,360 305,360" fill="#F72585"/>
        <polygon points="305,360 295,360 297,370 303,370" fill="#E0C5AE"/>
        <polygon points="280,280 320,275 325,315 285,320" fill="#1A1A1A"/>
        <polygon points="285,285 315,281 318,310 288,314" fill="#2A2A2A"/>
        <circle cx="302" cy="298" r="10" fill="#4A4A4A"/>
        <circle cx="302" cy="298" r="6" fill="#2A2A2A"/>
        <circle cx="302" cy="298" r="3" fill="#1A1A1A"/>
        <polygon points="260,255 280,280 278,282 258,257" fill="#3A0CA3"/>
        <polygon points="290,270 330,265 335,285 295,290" fill="#FFFFFF" class="shutter-flash" opacity="0"/>
      </g>

      <g class="neck freeze">
        <polygon points="185,220 215,220 212,250 188,250" fill="#D0B59E"/>
        <polygon points="185,220 195,220 193,250 188,250" fill="#E0C5AE"/>
        <polygon points="205,220 215,220 212,250 207,250" fill="#C0A58E"/>
      </g>

      <g class="head freeze">
        <polygon points="170,155 230,155 228,200 225,220 200,225 175,220 172,200" fill="#E0C5AE"/>
        <polygon points="170,155 185,155 183,200 172,200" fill="#D0B59E"/>
        <polygon points="215,155 230,155 228,200 217,200" fill="#C0A58E"/>
        <polygon points="175,220 200,225 225,220 222,232 200,238 178,232" fill="#D0B59E"/>

        <polygon points="148,128 252,128 260,172 140,172" fill="#3A0CA3"/>
        <polygon points="140,138 200,48 260,138 252,158 148,158" fill="#7209B7"/>
        <polygon points="135,132 168,62 195,148 185,198" fill="#560BAD"/>
        <polygon points="265,132 245,58 218,148 228,198" fill="#560BAD"/>
        <polygon points="135,132 122,162 132,228 158,202" fill="#3A0CA3"/>
        <polygon points="265,132 278,162 268,228 242,202" fill="#2A0A82"/>
        <polygon points="168,148 210,88 248,148 235,178 182,178" fill="#7209B7"/>

        <path d="M 182,188 Q 188,192 192,188" stroke="#1A1A1A" stroke-width="1.5" fill="none"/>
        <path d="M 208,188 Q 212,192 218,188" stroke="#1A1A1A" stroke-width="1.5" fill="none"/>
        <path d="M 192,218 Q 200,224 208,218" stroke="#B09070" stroke-width="1.5" fill="none"/>
        <polygon points="200,198 203,205 197,205" fill="#C0A58E"/>
      </g>
    </svg>
  </div>
</template>

<script setup>
const catchphrase = '等一下，这光绝了'
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

.freeze {
  animation: freeze 4s ease-in-out infinite;
  transform-origin: 200px 235px;
}

.sway {
  animation: sway 4s ease-in-out infinite;
  transform-origin: 150px 250px;
}

.shutter {
  animation: shutter 4s ease-in-out infinite;
  transform-origin: 250px 250px;
}

.shutter-flash {
  animation: shutter-flash 4s ease-in-out infinite;
}

@keyframes breathe {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-3px); }
}

@keyframes freeze {
  0%, 20% { transform: translateX(0); }
  25% { transform: translateX(5px); }
  30% { transform: translateX(0); }
  100% { transform: translateX(0); }
}

@keyframes sway {
  0%, 100% { transform: rotate(0deg); }
  50% { transform: rotate(2deg); }
}

@keyframes shutter {
  0%, 100% { transform: rotate(0deg) translateY(0); }
  30% { transform: rotate(-15deg) translateY(-5px); }
  40% { transform: rotate(-15deg) translateY(-5px); }
  70% { transform: rotate(0deg) translateY(0); }
}

@keyframes shutter-flash {
  0%, 35% { opacity: 0; }
  40% { opacity: 1; }
  45% { opacity: 0; }
  100% { opacity: 0; }
}

@keyframes bubble-in {
  0%, 20% { opacity: 0; transform: translateX(-50%) translateY(10px); }
  30%, 70% { opacity: 1; transform: translateX(-50%) translateY(0); }
  80%, 100% { opacity: 0; transform: translateX(-50%) translateY(-5px); }
}
</style>
