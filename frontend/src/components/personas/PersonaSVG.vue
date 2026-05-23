<template>
  <div class="persona-wrap" :class="`id-${config.id}`">
    <div class="bubble">{{ config.catchphrase }}</div>
    <svg viewBox="0 0 400 520" class="persona-svg">
      <g v-for="part in config.parts" :key="part.id" :class="part.animClass">
        <polygon v-if="part.type==='polygon'" :points="part.points" :fill="part.fill"/>
        <circle v-if="part.type==='circle'" :cx="part.cx" :cy="part.cy" :r="part.r" :fill="part.fill"/>
        <line v-if="part.type==='line'" :x1="part.x1" :y1="part.y1" :x2="part.x2" :y2="part.y2" :stroke="part.stroke" :stroke-width="part.width"/>
      </g>
    </svg>
  </div>
</template>

<script setup>
defineProps({ config: Object })
</script>

<style scoped>
.persona-wrap {
  position: relative;
  width: 320px;
  height: 416px;
}

.bubble {
  position: absolute;
  top: 20px;
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

.sway-reverse {
  animation: sway 4s ease-in-out infinite reverse;
  transform-origin: 250px 250px;
}

.led-blink {
  animation: blink 3s ease-in-out infinite;
}

@keyframes breathe {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-3px); }
}

@keyframes head-tilt {
  0%, 100% { transform: rotate(0deg) translateY(0); }
  50% { transform: rotate(-3deg) translateY(-2px); }
}

@keyframes sway {
  0%, 100% { transform: rotate(0deg); }
  50% { transform: rotate(2deg); }
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

@keyframes bubble-in {
  0%, 20% { opacity: 0; transform: translateX(-50%) translateY(10px); }
  30%, 70% { opacity: 1; transform: translateX(-50%) translateY(0); }
  80%, 100% { opacity: 0; transform: translateX(-50%) translateY(-5px); }
}
</style>
