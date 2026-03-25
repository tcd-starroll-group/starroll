<script setup lang="ts">
import type { StarClickInfo } from '@/core/renderer/GroundObserverRenderer';
import { useRouter } from 'vue-router';

// Define component props to receive star data
const props = defineProps<{
  starInfo: StarClickInfo | null;
}>();

// Define component events to emit close signal to parent component
const emit = defineEmits<{
  (e: 'close'): void;
}>();

const router = useRouter();

// 🌟 修改：跳转到特定星星的博客浏览列表页
const viewStarBlogs = () => {
  if (props.starInfo && props.starInfo.hip) {
    router.push({
      path: '/star-blogs', // ⚠️ 这里填你未来要创建的浏览页面的路由
      query: { 
        hip: props.starInfo.hip, 
        name: props.starInfo.originalName || props.starInfo.name // 顺便把名字带过去，方便目标页面渲染标题
      }
    });
  }
};
</script>

<template>
  <div v-if="starInfo" 
       class="star-popup" 
       @click.stop> 
       <button class="close-btn" @click.stop="emit('close')">×</button>
      
      <div class="star-header">
          <div class="star-name">{{ starInfo.originalName || starInfo.name }}</div>
          <div class="star-hip">HIP {{ starInfo.hip }}</div>
      </div>
      
      <div class="star-content">
          <div v-if="starInfo.description" class="star-desc">
              {{ starInfo.description }}
          </div>

          <div class="data-row">
              <span class="label">Constellation:</span>
              <span class="value">{{ starInfo.constellation }}</span>
          </div>
          <div class="data-row">
              <span class="label">Apparent Magnitude:</span>
              <span class="value">{{ starInfo.magnitude.toFixed(2) }}</span>
          </div>
          <div class="data-row">
              <span class="label">Distance:</span>
              <span class="value">{{ starInfo.distance ? starInfo.distance.toFixed(1) + ' ly' : '--' }}</span>
          </div>

          <button class="blog-btn" @click.stop="viewStarBlogs">
            🔭 Explore Star Logs
          </button>
      </div>
  </div>
</template>

<style scoped>
/* 原有样式保持不变 */
@keyframes popupFadeIn {
    from { opacity: 0; transform: scale(0.8) translateY(10px); }
    to { opacity: 1; transform: scale(1) translateY(0); }
}

.star-popup {
    position: absolute;
    background: rgba(15, 20, 30, 0.85);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(100, 150, 255, 0.2);
    border-radius: 12px;
    padding: 16px;
    min-width: 240px;
    max-width: 300px;
    color: white;
    font-family: var(--sr-font-family, 'Inter', sans-serif);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6),
                inset 0 0 0 1px rgba(255, 255, 255, 0.1);
    transform: translate(-50%, -100%);
    margin-top: -15px;
    pointer-events: auto;
    animation: popupFadeIn 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
    z-index: 200;
}

.star-popup::after {
    content: '';
    position: absolute;
    bottom: -8px;
    left: 50%;
    transform: translateX(-50%);
    border-width: 8px 8px 0;
    border-style: solid;
    border-color: rgba(15, 20, 30, 0.85) transparent transparent transparent;
    filter: drop-shadow(0 1px 1px rgba(100, 150, 255, 0.2));
}

.close-btn {
    position: absolute;
    top: 5px;
    right: 8px;
    background: transparent;
    border: none;
    color: rgba(255,255,255,0.6);
    font-size: 24px;
    line-height: 1;
    cursor: pointer;
    z-index: 201;
    transition: color 0.2s;
}

.close-btn:hover {
    color: white;
}

.star-header {
    border-bottom: 1px solid rgba(255,255,255,0.15);
    padding-bottom: 8px;
    margin-bottom: 10px;
    padding-right: 20px;
}

.star-name {
    font-size: 16px;
    font-weight: bold;
    color: #66ccff;
    text-shadow: 0 0 10px rgba(102, 204, 255, 0.5);
    line-height: 1.3;
}

.star-hip {
    font-size: 11px;
    color: #8899aa;
    margin-top: 2px;
}

.star-content {
    font-size: 13px;
    line-height: 1.5;
}

.star-desc {
    font-size: 12px;
    color: #aaccff;
    margin-bottom: 12px;
    font-style: italic;
    background: rgba(100, 150, 255, 0.1);
    padding: 6px 10px;
    border-radius: 6px;
    border-left: 3px solid #66ccff;
}

.data-row {
    display: flex;
    justify-content: space-between;
    margin-bottom: 6px;
    border-bottom: 1px dashed rgba(255,255,255,0.05);
    padding-bottom: 4px;
}

.data-row:last-of-type {
    border-bottom: none;
    margin-bottom: 0;
    padding-bottom: 0;
}

.label {
    color: #8899aa;
}

.value {
    font-weight: 500;
    color: #ffffff;
}

/* 🌟 按钮专属样式 */
.blog-btn {
    width: 100%;
    margin-top: 16px;
    padding: 10px 0;
    background: rgba(68, 170, 255, 0.15);
    border: 1px solid rgba(68, 170, 255, 0.4);
    color: #66ccff;
    border-radius: 6px;
    cursor: pointer;
    font-size: 14px;
    font-weight: 600;
    transition: all 0.3s ease;
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 8px;
    font-family: var(--sr-font-family);
}

.blog-btn:hover {
    background: rgba(68, 170, 255, 0.3);
    border-color: #66ccff;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(68, 170, 255, 0.2);
    color: #ffffff;
}

.blog-btn:active {
    transform: translateY(0);
}
</style>