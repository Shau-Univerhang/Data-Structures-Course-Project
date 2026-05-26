<template>
  <div class="persona-stage" :class="`persona-${config.id}`">
    <div class="dialogue">{{ config.catchphrase }}</div>
    <svg viewBox="0 0 400 520" class="persona-svg">
      <defs>
        <linearGradient :id="`shirt-${config.id}`" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" :stop-color="config.colors.secondary" />
          <stop offset="100%" :stop-color="shadeColor(config.colors.secondary, -10)" />
        </linearGradient>
      </defs>
      <g class="shadow-group">
        <polygon :points="shadowPoints" :fill="config.colors.primary" opacity="0.15" />
      </g>
      <g class="body-breathe">
        <g v-for="(part, index) in config.svgParts" :key="index" :class="part.group">
          <polygon :points="part.points" :fill="part.fill || getPartColor(part.group, config)" />
        </g>
      </g>
    </svg>
  </div>
</template>

<script setup>
const props = defineProps({
  config: Object
})

function shadeColor(color, percent) {
  const num = parseInt(color.replace('#', ''), 16)
  const amt = Math.round(2.55 * percent)
  const R = Math.min(255, Math.max(0, (num >> 16) + amt))
  const G = Math.min(255, Math.max(0, ((num >> 8) & 0x00FF) + amt))
  const B = Math.min(255, Math.max(0, (num & 0x0000FF) + amt))
  return '#' + (0x1000000 + R * 0x10000 + G * 0x100 + B).toString(16).slice(1)
}

function getPartColor(group, config) {
  const colorMap = {
    legs: config.colors.primary,
    torso: `url(#shirt-${config.id})`,
    arm: config.colors.skin,
    armRight: config.colors.skin,
    armLeft: config.colors.skin,
    neck: config.colors.skin,
    head: config.colors.skin,
    hair: config.colors.hair,
    prop: config.colors.prop,
    accent: config.colors.accent
  }
  return colorMap[group] || config.colors.primary
}

const shadowPoints = '120,480 280,480 300,495 100,495'
</script>

<style scoped>
.persona-stage {
  position: relative;
  display: inline-block;
  width: 400px;
  height: 520px;
}

.persona-svg {
  width: 100%;
  height: 100%;
  overflow: visible;
}

.dialogue {
  position: absolute;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  padding: 10px 20px;
  font-size: 14px;
  font-weight: 600;
  color: #333;
  white-space: nowrap;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  opacity: 0;
  animation: dialogueFloat 4s ease-in-out infinite;
  pointer-events: none;
  z-index: 10;
}

.dialogue::after {
  content: '';
  position: absolute;
  bottom: -8px;
  left: 50%;
  transform: translateX(-50%);
  border-left: 8px solid transparent;
  border-right: 8px solid transparent;
  border-top: 8px solid rgba(255, 255, 255, 0.95);
}

.body-breathe {
  animation: breathe 3s ease-in-out infinite;
  transform-origin: center 400px;
}

@keyframes breathe {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-3px); }
}

@keyframes dialogueFloat {
  0%, 100% { opacity: 0; transform: translateX(-50%) translateY(5px); }
  20%, 80% { opacity: 1; transform: translateX(-50%) translateY(0); }
}
</style>
