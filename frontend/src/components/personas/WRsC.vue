<template>
  <div class="persona-wrap">
    <div class="bubble">{{ catchphrase }}</div>
    <svg viewBox="0 0 400 520" class="persona-svg">
      <!-- 阴影 -->
      <g class="shadow">
        <polygon points="100,512 300,512 280,525 120,525" fill="rgba(0,0,0,0.15)"/>
      </g>

      <!-- 腿部（6片）卡其裤 -->
      <g class="legs">
        <polygon points="170,400 195,400 192,512 167,512" fill="#606C38"/>
        <polygon points="167,512 192,512 188,525 163,525" fill="#7B8C4A"/>
        <polygon points="160,400 170,400 167,512 160,512" fill="#7B8C4A"/>
        <polygon points="205,400 230,400 227,512 202,512" fill="#7B8C4A"/>
        <polygon points="202,512 227,512 223,525 198,525" fill="#8B9D5E"/>
        <polygon points="230,400 240,400 237,512 227,512" fill="#8B9D5E"/>
      </g>

      <!-- 躯干（6片）旧毛衣 -->
      <g class="torso breathe">
        <polygon points="150,390 250,390 245,400 155,400" fill="#BC6C25"/>
        <polygon points="150,250 200,250 200,330 155,390 145,390" fill="#DDA15E"/>
        <polygon points="200,250 250,250 255,390 245,390 200,330" fill="#E9C46A"/>
        <polygon points="190,250 210,250 205,330 195,330" fill="#BC6C25"/>
        <polygon points="180,250 200,250 195,270 185,265" fill="#DDA15E"/>
        <polygon points="200,250 220,250 215,265 205,270" fill="#E9C46A"/>
        <!-- 起球 -->
        <polygon points="165,300 170,298 172,303 167,305" fill="#F4A261"/>
        <polygon points="225,320 230,318 232,323 227,325" fill="#BC6C25"/>
      </g>

      <!-- 左臂（6片）提菜篮 -->
      <g class="arm-left basket-hold">
        <polygon points="150,255 125,275 115,325 135,335" fill="#DDA15E"/>
        <polygon points="125,275 110,285 100,335 115,325" fill="#E9C46A"/>
        <polygon points="110,285 95,305 90,345 100,335" fill="#BC6C25"/>
        <polygon points="90,345 98,352 108,345 100,338" fill="#DDA15E"/>
        <polygon points="88,350 105,350 102,360 90,360" fill="#E9C46A"/>
        <polygon points="90,360 102,360 100,370 92,370" fill="#E0C097"/>
        <!-- 菜篮子 -->
        <polygon points="80,360 115,355 120,395 85,400" fill="#8B4513"/>
        <polygon points="85,365 110,361 113,390 88,394" fill="#A0522D"/>
        <polygon points="85,370 90,369 92,375 87,376" fill="#90EE90"/>
        <polygon points="100,368 105,367 107,373 102,374" fill="#FF6347"/>
      </g>

      <!-- 右臂（6片）摆手 -->
      <g class="arm-right wave-hand">
        <polygon points="250,255 275,275 285,325 265,335" fill="#E9C46A"/>
        <polygon points="275,275 290,285 300,335 285,325" fill="#DDA15E"/>
        <polygon points="290,285 305,305 310,345 300,335" fill="#BC6C25"/>
        <polygon points="310,345 302,352 292,345 300,338" fill="#E9C46A"/>
        <polygon points="312,350 295,350 298,360 310,360" fill="#DDA15E"/>
        <polygon points="310,360 298,360 300,370 308,370" fill="#E0C097"/>
      </g>

      <!-- 后背大包 -->
      <g class="prop-bag">
        <polygon points="120,260 155,252 162,340 127,348" fill="#6B705C"/>
        <polygon points="127,348 162,340 168,365 133,373" fill="#5A5F4B"/>
        <polygon points="130,280 150,276 155,330 135,334" fill="#7A7A6A"/>
      </g>

      <!-- 脖子（3片） -->
      <g class="neck head-tilt">
        <polygon points="185,220 215,220 212,250 188,250" fill="#D0B088"/>
        <polygon points="185,220 195,220 193,250 188,250" fill="#E0C097"/>
        <polygon points="205,220 215,220 212,250 207,250" fill="#C0A078"/>
      </g>

      <!-- 头部 -->
      <g class="head head-tilt">
        <!-- 面部（4片） -->
        <polygon points="170,155 230,155 228,200 225,220 200,225 175,220 172,200" fill="#E0C097"/>
        <polygon points="170,155 185,155 183,200 172,200" fill="#D0B088"/>
        <polygon points="215,155 230,155 228,200 217,200" fill="#C0A078"/>
        <polygon points="175,220 200,225 225,220 222,232 200,238 178,232" fill="#D0B088"/>

        <!-- 头发（7片）驼色短发自然卷 -->
        <polygon points="155,135 245,135 252,175 148,175" fill="#A67B5B"/>
        <polygon points="150,145 200,72 250,145 243,162 152,162" fill="#BC6C25"/>
        <polygon points="145,140 170,82 192,148 182,188" fill="#DDA15E"/>
        <polygon points="255,140 240,78 218,148 222,188" fill="#DDA15E"/>
        <polygon points="145,140 132,168 140,215 158,195" fill="#A67B5B"/>
        <polygon points="255,140 268,168 260,215 242,195" fill="#966B4B"/>
        <polygon points="168,148 208,108 248,148 235,172 182,172" fill="#E9C46A"/>

        <!-- 五官（朴实微笑） -->
        <circle cx="188" cy="188" r="2" fill="#1A1A1A"/>
        <circle cx="212" cy="188" r="2" fill="#1A1A1A"/>
        <path d="M 192,218 Q 200,224 208,218" stroke="#B09068" stroke-width="1.5" fill="none"/>
        <polygon points="200,198 203,205 197,205" fill="#C0A078"/>
      </g>
    </svg>
  </div>
</template>

<script setup>
const catchphrase = '老板，便宜两块'
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

.basket-hold {
  animation: basket-hold 3s ease-in-out infinite;
  transform-origin: 150px 250px;
}

.wave-hand {
  animation: wave-hand 2s ease-in-out infinite;
  transform-origin: 250px 250px;
}

@keyframes breathe {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-3px); }
}

@keyframes head-tilt {
  0%, 100% { transform: rotate(0deg) translateY(0); }
  50% { transform: rotate(-2deg) translateY(-1px); }
}

@keyframes basket-hold {
  0%, 100% { transform: rotate(0deg); }
  50% { transform: rotate(3deg); }
}

@keyframes wave-hand {
  0%, 100% { transform: rotate(0deg); }
  25% { transform: rotate(10deg); }
  75% { transform: rotate(-5deg); }
}

@keyframes bubble-in {
  0%, 20% { opacity: 0; transform: translateX(-50%) translateY(10px); }
  30%, 70% { opacity: 1; transform: translateX(-50%) translateY(0); }
  80%, 100% { opacity: 0; transform: translateX(-50%) translateY(-5px); }
}
</style>
