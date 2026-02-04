<script setup lang="ts">
import { useStarRoll } from '../composables/useStarRoll';
import { computed } from 'vue';

const { currentMode, isPaused, timeScale, togglePause, setSpeed } = useStarRoll();

// 格式化当前时间 (伪造一个基于真实时间 + 增量的显示)
const displayTime = computed(() => {
    const d = new Date();
    return d.toLocaleTimeString('en-US', { hour12: false });
});
const displayDate = computed(() => {
    const d = new Date();
    return d.toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' });
});
</script>

<template>
  <div class="top-bar sr-glass-panel">
    <div class="location-info">
      <div class="sr-title">LOCATION</div>
      <div class="sub-text">Shanghai, CN (31.2°N, 121.4°E)</div>
    </div>

    <div class="time-display">
      <div class="date">{{ displayDate }}</div>
      <div class="time sr-value">{{ displayTime }}</div>
    </div>

    <div class="controls">
      <button class="sr-glass-btn" @click="setSpeed(timeScale === 1 ? 100 : 1)">
        {{ timeScale > 1 ? '>> 100x' : '1x' }}
      </button>
      <button class="sr-glass-btn play-btn" @click="togglePause">
        {{ isPaused ? '▶' : '||' }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.top-bar {
  position: absolute;
  top: 24px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 48px;
  padding: 12px 32px;
  z-index: 10;
}

.location-info {
  text-align: right;
}
.sub-text {
    font-size: 12px;
    opacity: 0.8;
}

.time-display {
  text-align: center;
  min-width: 140px;
}
.date {
    font-size: 12px;
    opacity: 0.7;
    margin-bottom: 2px;
}

.controls {
    display: flex;
    gap: 12px;
}
.play-btn {
    width: 40px;
}
</style>

