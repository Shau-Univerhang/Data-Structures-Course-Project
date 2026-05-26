<template>
  <div class="persona-showcase">
    <div class="showcase-header">
      <h1 class="showcase-title">16 种旅行人格</h1>
      <p class="showcase-subtitle">每一种都是独特的旅行灵魂</p>
    </div>

    <div class="persona-grid">
      <div class="persona-card" style="background-color: #2D6A4F;">
        <PRsC />
        <div class="card-info">
          <h3 class="card-name">断网疗愈体</h3>
          <span class="card-code">PRsC</span>
        </div>
      </div>

      <div class="persona-card" style="background-color: #2A2A35;">
        <PESC />
        <div class="card-info">
          <h3 class="card-name">Excel成精</h3>
          <span class="card-code">PESC</span>
        </div>
      </div>

      <div class="persona-card" style="background-color: #D4A017;">
        <PEScKPI />
        <div class="card-info">
          <h3 class="card-name">人间KPI</h3>
          <span class="card-code">PESc</span>
        </div>
      </div>

      <div class="persona-card" style="background-color: #6B705C;">
        <PEsCWifi />
        <div class="card-info">
          <h3 class="card-name">电子流浪猫</h3>
          <span class="card-code">PEsC</span>
        </div>
      </div>

      <div class="persona-card" style="background-color: #1A1A1A;">
        <PEscTool />
        <div class="card-info">
          <h3 class="card-name">瑞士军刀成精</h3>
          <span class="card-code">PEsc</span>
        </div>
      </div>

      <div class="persona-card" style="background-color: #A0522D;">
        <PReC />
        <div class="card-info">
          <h3 class="card-name">躺平项目经理</h3>
          <span class="card-code">PReC</span>
        </div>
      </div>

      <div class="persona-card" style="background-color: #FF69B4;">
        <PRec />
        <div class="card-info">
          <h3 class="card-name">朋友圈精修师</h3>
          <span class="card-code">PRec</span>
        </div>
      </div>

      <div class="persona-card" style="background-color: #4A0E4E;">
        <PRscMoney />
        <div class="card-info">
          <h3 class="card-name">人民币蒸发器</h3>
          <span class="card-code">PRsc</span>
        </div>
      </div>

      <div class="persona-card" style="background-color: #E85D04;">
        <WESCGPS />
        <div class="card-info">
          <h3 class="card-name">野生GPS</h3>
          <span class="card-code">WESC</span>
        </div>
      </div>

      <div class="persona-card" style="background-color: #8B4513;">
        <WESc />
        <div class="card-info">
          <h3 class="card-name">故事拾荒者</h3>
          <span class="card-code">WESc</span>
        </div>
      </div>

      <div class="persona-card" style="background-color: #1B4332;">
        <WEsCSignal />
        <div class="card-info">
          <h3 class="card-name">信号绝缘体</h3>
          <span class="card-code">WEsC</span>
        </div>
      </div>

      <div class="persona-card" style="background-color: #0077B6;">
        <WEsc />
        <div class="card-info">
          <h3 class="card-name">风的方向盘</h3>
          <span class="card-code">WEsc</span>
        </div>
      </div>

      <div class="persona-card" style="background-color: #9D0208;">
        <WReC />
        <div class="card-info">
          <h3 class="card-name">夜间经济贡献者</h3>
          <span class="card-code">WReC</span>
        </div>
      </div>

      <div class="persona-card" style="background-color: #7209B7;">
        <WRec />
        <div class="card-info">
          <h3 class="card-name">氛围感炼丹师</h3>
          <span class="card-code">WRec</span>
        </div>
      </div>

      <div class="persona-card" style="background-color: #495057;">
        <WRsC />
        <div class="card-info">
          <h3 class="card-name">人类观察样本</h3>
          <span class="card-code">WRsC</span>
        </div>
      </div>

      <div class="persona-card" style="background-color: #BC6C25;">
        <WRsc />
        <div class="card-info">
          <h3 class="card-name">城市游牧民</h3>
          <span class="card-code">WRsc</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import PRsC from './PRsC.vue'
import PESC from './PESC.vue'
import PEScKPI from './PESc-KPI.vue'
import PEsCWifi from './PEsC-Wifi.vue'
import PEscTool from './PEsc-Tool.vue'
import PReC from './PReC.vue'
import PRec from './PRec.vue'
import PRscMoney from './PRsc-Money.vue'
import WESCGPS from './WESC-GPS.vue'
import WESc from './WESc.vue'
import WEsCSignal from './WEsC-Signal.vue'
import WEsc from './WEsc.vue'
import WReC from './WReC.vue'
import WRec from './WRec.vue'
import WRsC from './WRsC.vue'
import WRsc from './WRsc.vue'
</script>

<style scoped lang="scss">
.persona-showcase {
  padding: 40px 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.showcase-header {
  text-align: center;
  margin-bottom: 48px;
}

.showcase-title {
  font-size: 36px;
  font-weight: 700;
  color: #1a1a2e;
  margin: 0 0 12px;
  letter-spacing: -0.5px;
}

.showcase-subtitle {
  font-size: 16px;
  color: #666;
  margin: 0;
}

.persona-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 24px;
}

.persona-card {
  position: relative;
  border-radius: 20px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.2);
  }
}

.card-info {
  margin-top: 12px;
  padding: 12px 20px;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  width: 100%;
  max-width: 280px;
}

.card-name {
  font-size: 15px;
  font-weight: 600;
  color: #fff;
  margin: 0;
  text-shadow: 0 1px 2px rgba(0,0,0,0.3);
}

.card-code {
  font-size: 12px;
  font-weight: 500;
  color: rgba(255,255,255,0.8);
  font-family: monospace;
  padding: 4px 8px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 4px;
}

@media (max-width: 768px) {
  .persona-grid {
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 16px;
  }

  .showcase-title {
    font-size: 28px;
  }
}
</style>
