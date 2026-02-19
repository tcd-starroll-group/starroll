<script setup lang="ts">
import type { StarClickInfo } from '@/core/renderer/GroundObserverRenderer';

// Define component props to receive star data
const props = defineProps<{
  starInfo: StarClickInfo | null;
}>();

// Define component events to emit close signal to parent component
const emit = defineEmits<{
  (e: 'close'): void;
}>();

/**
 * Calculate popup position with boundary detection
 * Ensures the popup stays within viewport bounds
 * @param star - Star data containing screen position coordinates
 * @returns CSS style object with top/left positions
 */
const getPopupStyle = (star: StarClickInfo) => {
    const width = 240;
    const padding = 15;
    
    // Initial position offset from star click position
    let left = star.screenX + 15;
    let top = star.screenY - 15;

    // Boundary detection - prevent overflow on right side
    if (left + width > window.innerWidth) {
        left = star.screenX - width - 15;
    }
    
    // Boundary detection - prevent overflow on bottom side
    if (top + 300 > window.innerHeight) {
        top = star.screenY - 300;
    }
    
    // Boundary detection - prevent overflow on top side
    if (top < padding) top = padding;

    return {
        top: `${top}px`,
        left: `${left}px`
    };
};
</script>

<template>
  <div v-if="starInfo" 
       class="star-popup" 
       :style="getPopupStyle(starInfo)"
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
          
          <div v-if="starInfo.url" class="data-row link-row">
              <a :href="starInfo.url" target="_blank" class="star-link">
                  Simbad Details ↗
              </a>
          </div>

          <div class="separator"></div>
          <div class="data-row">
              <span class="label">Azimuth:</span>
              <span class="value">{{ starInfo.azimuth.toFixed(1) }}°</span>
          </div>
          <div class="data-row">
              <span class="label">Altitude:</span>
              <span class="value">{{ starInfo.altitude.toFixed(1) }}°</span>
          </div>
           <div class="data-row">
              <span class="label">B-V Color Index:</span>
              <span class="value">{{ starInfo.bvColor.toFixed(2) }}</span>
          </div>
      </div>
  </div>
</template>

<style scoped>
.star-popup {
    position: absolute;
    width: 240px;
    background: rgba(15, 20, 35, 0.95);
    border: 1px solid rgba(100, 200, 255, 0.4);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.6);
    border-radius: 12px;
    padding: 16px;
    color: white;
    z-index: 200;
    backdrop-filter: blur(10px);
    pointer-events: auto; /* Critical: Enable click events */
    animation: popupFadeIn 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

/* Popup fade-in animation */
@keyframes popupFadeIn {
    from { opacity: 0; transform: scale(0.8) translateY(10px); }
    to { opacity: 1; transform: scale(1) translateY(0); }
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
    color: #ccc;
    margin-bottom: 8px;
    font-style: italic;
    line-height: 1.4;
    max-height: 80px;
    overflow-y: auto;
}

.link-row {
    margin-top: 8px;
    justify-content: flex-end;
}

.star-link {
    color: #44aaff;
    text-decoration: none;
    font-size: 12px;
    border-bottom: 1px dashed #44aaff;
}

.star-link:hover {
    color: #fff;
    border-bottom-style: solid;
}

.data-row {
    display: flex;
    justify-content: space-between;
    margin-bottom: 4px;
}

.label {
    color: #8899aa;
}

.value {
    color: #ddeeff;
    font-family: monospace;
    font-weight: 600;
}

.separator {
    height: 1px;
    background: rgba(255,255,255,0.1);
    margin: 8px 0;
}
</style>