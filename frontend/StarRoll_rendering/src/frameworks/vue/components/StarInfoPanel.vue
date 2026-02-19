<script setup lang="ts">
import { ref, computed } from 'vue';
import type { StarClickInfo } from '@/core/renderer/GroundObserverRenderer';

const props = defineProps<{
    starInfo: StarClickInfo | null;
}>();

const emit = defineEmits<{
    close: [];
}>();

// 格式化星等
const formattedMagnitude = computed(() => {
    if (!props.starInfo) return '';
    return props.starInfo.magnitude.toFixed(2);
});

// 格式化B-V色指数
const formattedBV = computed(() => {
    if (!props.starInfo) return '';
    return props.starInfo.bvColor.toFixed(3);
});

// 格式化距离
const formattedDistance = computed(() => {
    if (!props.starInfo || !props.starInfo.distance) return '未知';
    const distance = props.starInfo.distance;
    if (distance < 1000) {
        return `${distance.toFixed(1)} 光年`;
    } else {
        return `${(distance / 1000).toFixed(2)} 千光年`;
    }
});

// 格式化赤经
const formattedRA = computed(() => {
    if (!props.starInfo) return '';
    const ra = props.starInfo.rightAscension;
    const hours = Math.floor(ra / 15);
    const minutes = Math.floor((ra / 15 - hours) * 60);
    const seconds = Math.floor(((ra / 15 - hours) * 60 - minutes) * 60);
    return `${hours}h ${minutes}m ${seconds}s`;
});

// 格式化赤纬
const formattedDec = computed(() => {
    if (!props.starInfo) return '';
    const dec = props.starInfo.declination;
    const sign = dec >= 0 ? '+' : '-';
    const absDec = Math.abs(dec);
    const degrees = Math.floor(absDec);
    const minutes = Math.floor((absDec - degrees) * 60);
    const seconds = Math.floor(((absDec - degrees) * 60 - minutes) * 60);
    return `${sign}${degrees}° ${minutes}' ${seconds}"`;
});

// 星星颜色类别
const colorCategory = computed(() => {
    if (!props.starInfo) return { name: '', color: '#ffffff' };
    const bv = props.starInfo.bvColor;
    
    if (bv < -0.3) return { name: '蓝色', color: '#A8C0FF' };
    if (bv < 0) return { name: '蓝白色', color: '#C8D8FF' };
    if (bv < 0.3) return { name: '白色', color: '#FFFFFF' };
    if (bv < 0.6) return { name: '黄白色', color: '#FFF8E0' };
    if (bv < 1.0) return { name: '黄色', color: '#FFEB99' };
    if (bv < 1.5) return { name: '橙色', color: '#FFCC66' };
    return { name: '红色', color: '#FFB366' };
});

// 亮度等级描述
const brightnessLevel = computed(() => {
    if (!props.starInfo) return '';
    const mag = props.starInfo.magnitude;
    
    if (mag < 0) return '极亮星（负星等）';
    if (mag < 1) return '一等星';
    if (mag < 2) return '二等星';
    if (mag < 3) return '三等星';
    if (mag < 4) return '四等星';
    if (mag < 5) return '五等星';
    if (mag < 6) return '六等星';
    return '暗星';
});

const handleClose = () => {
    emit('close');
};
</script>

<template>
  <Transition name="slide-up">
    <div v-if="starInfo" class="star-info-panel">
      <div class="panel-header">
        <div class="star-title">
          <h2 class="star-name">{{ starInfo.name }}</h2>
          <p v-if="starInfo.englishName" class="star-english">{{ starInfo.englishName }}</p>
        </div>
        <button @click="handleClose" class="close-btn">✕</button>
      </div>
      
      <div class="panel-content">
        <!-- 基本信息 -->
        <div class="info-section">
          <div class="section-title">基本信息</div>
          <div class="info-grid">
            <div class="info-item">
              <span class="label">所属星座</span>
              <span class="value">{{ starInfo.constellation }}</span>
            </div>
            <div class="info-item">
              <span class="label">HIP编号</span>
              <span class="value">{{ starInfo.hip }}</span>
            </div>
            <div class="info-item">
              <span class="label">视星等</span>
              <span class="value">{{ formattedMagnitude }} <span class="sub-text">({{ brightnessLevel }})</span></span>
            </div>
            <div class="info-item">
              <span class="label">距离</span>
              <span class="value">{{ formattedDistance }}</span>
            </div>
          </div>
        </div>
        
        <!-- 颜色信息 -->
        <div class="info-section">
          <div class="section-title">颜色特征</div>
          <div class="color-info">
            <div class="color-sample" :style="{ backgroundColor: colorCategory.color }"></div>
            <div class="color-details">
              <div class="color-name">{{ colorCategory.name }}</div>
              <div class="color-bv">B-V色指数: {{ formattedBV }}</div>
            </div>
          </div>
        </div>
        
        <!-- 天球坐标 -->
        <div class="info-section">
          <div class="section-title">天球坐标</div>
          <div class="info-grid">
            <div class="info-item">
              <span class="label">赤经 (RA)</span>
              <span class="value mono">{{ formattedRA }}</span>
            </div>
            <div class="info-item">
              <span class="label">赤纬 (Dec)</span>
              <span class="value mono">{{ formattedDec }}</span>
            </div>
          </div>
        </div>
        
        <!-- 地平坐标 -->
        <div class="info-section">
          <div class="section-title">当前位置</div>
          <div class="info-grid">
            <div class="info-item">
              <span class="label">方位角</span>
              <span class="value">{{ starInfo.azimuth.toFixed(1) }}°</span>
            </div>
            <div class="info-item">
              <span class="label">高度角</span>
              <span class="value">{{ starInfo.altitude.toFixed(1) }}°</span>
            </div>
          </div>
        </div>
      </div>
      
      <div class="panel-footer">
        <div class="hint-text">💡 点击画面空白处或关闭按钮关闭信息面板</div>
      </div>
    </div>
  </Transition>
  
  <!-- 背景遮罩 -->
  <Transition name="fade">
    <div v-if="starInfo" class="overlay" @click="handleClose"></div>
  </Transition>
</template>

<style scoped>
.star-info-panel {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    max-height: 70vh;
    background: rgba(10, 10, 20, 0.98);
    border-top-left-radius: 24px;
    border-top-right-radius: 24px;
    backdrop-filter: blur(20px);
    box-shadow: 0 -8px 32px rgba(0, 0, 0, 0.5);
    z-index: 1000;
    overflow-y: auto;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.panel-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    padding: 24px 20px 16px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    position: sticky;
    top: 0;
    background: rgba(10, 10, 20, 0.95);
    backdrop-filter: blur(20px);
    z-index: 1;
}

.star-title {
    flex: 1;
}

.star-name {
    font-size: 24px;
    font-weight: 700;
    color: #fff;
    margin: 0 0 4px 0;
    text-shadow: 0 2px 8px rgba(68, 170, 255, 0.3);
}

.star-english {
    font-size: 14px;
    color: rgba(255, 255, 255, 0.6);
    margin: 0;
    font-style: italic;
}

.close-btn {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: rgba(255, 255, 255, 0.7);
    font-size: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.2s;
    flex-shrink: 0;
}

.close-btn:hover {
    background: rgba(255, 255, 255, 0.1);
    color: #fff;
}

.close-btn:active {
    transform: scale(0.95);
}

.panel-content {
    padding: 20px;
}

.info-section {
    margin-bottom: 24px;
}

.info-section:last-child {
    margin-bottom: 0;
}

.section-title {
    font-size: 12px;
    font-weight: 600;
    color: rgba(68, 170, 255, 0.9);
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 12px;
}

.info-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
}

.info-item {
    display: flex;
    flex-direction: column;
    gap: 4px;
    padding: 12px;
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 8px;
}

.label {
    font-size: 10px;
    color: rgba(255, 255, 255, 0.5);
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.value {
    font-size: 15px;
    color: #fff;
    font-weight: 600;
}

.value.mono {
    font-family: 'Courier New', monospace;
    font-size: 13px;
}

.sub-text {
    font-size: 11px;
    color: rgba(255, 255, 255, 0.5);
    font-weight: 400;
}

/* 颜色信息 */
.color-info {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 12px;
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 8px;
}

.color-sample {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    box-shadow: 0 0 20px currentColor;
    flex-shrink: 0;
}

.color-details {
    flex: 1;
}

.color-name {
    font-size: 16px;
    font-weight: 600;
    color: #fff;
    margin-bottom: 4px;
}

.color-bv {
    font-size: 12px;
    color: rgba(255, 255, 255, 0.5);
    font-family: 'Courier New', monospace;
}

.panel-footer {
    padding: 16px 20px;
    border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.hint-text {
    font-size: 11px;
    color: rgba(255, 255, 255, 0.4);
    text-align: center;
}

/* 背景遮罩 */
.overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.4);
    z-index: 999;
}

/* 动画 */
.slide-up-enter-active,
.slide-up-leave-active {
    transition: transform 0.3s ease-out;
}

.slide-up-enter-from {
    transform: translateY(100%);
}

.slide-up-leave-to {
    transform: translateY(100%);
}

.fade-enter-active,
.fade-leave-active {
    transition: opacity 0.3s;
}

.fade-enter-from,
.fade-leave-to {
    opacity: 0;
}

/* 响应式 */
@media (min-width: 768px) {
    .star-info-panel {
        left: 50%;
        transform: translateX(-50%);
        max-width: 500px;
        border-radius: 24px;
        bottom: 40px;
        max-height: 600px;
    }
    
    .slide-up-enter-from {
        transform: translateX(-50%) translateY(100%);
    }
    
    .slide-up-leave-to {
        transform: translateX(-50%) translateY(100%);
    }
}

/* 滚动条样式 */
.star-info-panel::-webkit-scrollbar {
    width: 6px;
}

.star-info-panel::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.02);
}

.star-info-panel::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 3px;
}

.star-info-panel::-webkit-scrollbar-thumb:hover {
    background: rgba(255, 255, 255, 0.2);
}
</style>
