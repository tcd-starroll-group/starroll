<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue';

// 实时更新的当前时间
const currentTime = ref(new Date());

// 定时更新时间
let timer: number | null = null;

onMounted(() => {
    timer = window.setInterval(() => {
        currentTime.value = new Date();
    }, 1000);
});

onUnmounted(() => {
    if (timer) {
        clearInterval(timer);
    }
});

// 格式化当前时间
const displayTime = computed(() => {
    return currentTime.value.toLocaleTimeString('zh-CN', { hour12: false });
});

const displayDate = computed(() => {
    return currentTime.value.toLocaleDateString('zh-CN', { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
    });
});
</script>

<template>
  <div class="top-bar sr-glass-panel">
    <div class="time-display">
      <div class="date">{{ displayDate }}</div>
      <div class="time sr-value">{{ displayTime }}</div>
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
  justify-content: center;
  padding: 12px 24px;
  z-index: 10;
}

.time-display {
  text-align: center;
  min-width: 180px;
}

.date {
    font-size: 13px;
    opacity: 0.7;
    margin-bottom: 4px;
    color: rgba(255, 255, 255, 0.8);
}

.time {
    font-size: 18px;
    font-weight: 600;
    color: #fff;
    font-family: 'Courier New', monospace;
}
</style>

