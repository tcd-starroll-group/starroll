<script setup lang="ts">
import { onMounted, ref, watch } from 'vue';
import { GroundObserver } from '../utils/useGroundObserver';
import StarPopupPanel from '../components/StarPopup.vue';
import type { StarClickInfo } from '@/core/renderer/GroundObserverRenderer';

const containerRef = ref<HTMLElement | null>(null);
let groundObserver: GroundObserver | null = null;

const clickedStarInfo = ref<StarClickInfo | null>(null);


// click stars
let selectedStar = ref<StarClickInfo | null>(null);
const closeStarInfo = () => {
    // clear the local mirror first so the UI panel hides reliably
    clickedStarInfo.value = null;
    // also clear the renderer's selected ref if available
    if (groundObserver?.selectedStar) groundObserver.selectedStar.value = null;
    if (selectedStar) selectedStar.value = null;
};

onMounted(async () => {
    if (containerRef.value) {
        groundObserver = new GroundObserver(containerRef.value);
        // bind the selectedStar ref from the GroundObserver instance
        selectedStar = groundObserver.selectedStar;
        watch(selectedStar, (val) => {
            clickedStarInfo.value = val
        })
        try {
            await groundObserver.enableARMode();
            groundObserver.testTimeFlash();
        } catch (error) {
            console.error('Error enabling AR mode:', error);
        }
    }else{
        console.error('containerRef.value is null')
    }
});


</script>

<template>
  <div class="starroll-app" @click.self="">
    <div ref="containerRef" class="canvas-container" @click.self=""></div>
    
    <div class="ui-layer">        
        <div class="horizon-line">
          <div class="horizon-label">Horizon</div>
        </div>
        
        <StarPopupPanel 
            :starInfo="clickedStarInfo"
            @close="closeStarInfo"
        />
    </div>
  </div>
</template>

<style>
/* Global Reset for this App */
.starroll-app {
    width: 100vw;
    height: 100vh;
    background: #000;
    overflow: hidden;
    position: relative;
    font-family: var(--sr-font-family);
    color: white;
}

.canvas-container {
    width: 100%;
    height: 100%;
    position: absolute;
    top: 0;
    left: 0;
    z-index: 1;
}

.ui-layer {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 10;
    pointer-events: none; /* Let clicks pass through to canvas */
}

/* Re-enable pointer events for UI elements */
.ui-layer > * {
    pointer-events: auto;
}

/* [Added] Real compass display panel */
.real-compass-display {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 200px;
    height: 200px;
    background: rgba(0, 0, 10, 0.8);
    border-radius: 50%;
    border: 2px solid rgba(255, 255, 255, 0.3);
    backdrop-filter: blur(10px);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    z-index: 100;
    pointer-events: none;
    box-shadow: 0 0 50px rgba(0, 0, 0, 0.5);
}

.compass-ring {
    position: absolute;
    width: 100%;
    height: 100%;
    border-radius: 50%;
    transition: transform 0.1s linear; /* Smooth rotation */
}

.mark-n, .mark-e, .mark-s, .mark-w {
    position: absolute;
    font-weight: bold;
    font-size: 14px;
}

.mark-n { top: 10px; left: 50%; transform: translateX(-50%); color: #ff4444; }
.mark-e { right: 10px; top: 50%; transform: translateY(-50%); color: white; }
.mark-s { bottom: 10px; left: 50%; transform: translateX(-50%); color: white; }
.mark-w { left: 10px; top: 50%; transform: translateY(-50%); color: white; }

/* Fixed compass pointer */
.compass-pointer {
    position: absolute;
    top: -10px;
    left: 50%;
    transform: translateX(-50%);
    width: 0; 
    height: 0; 
    border-left: 8px solid transparent;
    border-right: 8px solid transparent;
    border-bottom: 15px solid #FFD700;
    z-index: 101;
}

.compass-text {
    text-align: center;
    z-index: 102;
}

.compass-value {
    font-size: 32px;
    font-weight: 700;
    color: #FFD700;
    font-family: monospace;
}

.compass-label {
    font-size: 12px;
    color: #aaa;
}

.horizon-line {
    position: absolute;
    bottom: 40px;
    left: 0;
    width: 100%;
    height: 1px;
    background: linear-gradient(90deg, 
        transparent 0%, 
        rgba(255,255,255,0.1) 20%, 
        rgba(255,255,255,0.3) 50%, 
        rgba(255,255,255,0.1) 80%, 
        transparent 100%
    );
    pointer-events: none;
}

/* Observer information panel */
.observer-info {
    position: absolute;
    top: 80px;
    left: 24px;
    padding: 12px 16px;
    background: rgba(0, 0, 0, 0.6);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 8px;
    backdrop-filter: blur(10px);
}

.info-row {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 13px;
    color: var(--sr-text-primary);
    margin-bottom: 4px;
}

.info-row.small {
    font-size: 10px;
    color: var(--sr-text-secondary);
    margin-bottom: 0;
}

.info-row .icon {
    font-size: 14px;
}

.location-btn {
    width: 100%;
    margin-top: 8px;
    padding: 8px 12px;
    background: rgba(68, 170, 255, 0.15);
    border: 1px solid rgba(68, 170, 255, 0.3);
    border-radius: 6px;
    color: rgba(68, 170, 255, 0.9);
    font-size: 11px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
}

.location-btn:hover {
    background: rgba(68, 170, 255, 0.25);
    color: #44aaff;
}

.location-btn:disabled {
    opacity: 0.5;
    cursor: wait;
}

.location-btn:active:not(:disabled) {
    transform: scale(0.98);
}

.debug-btn {
    width: 100%;
    margin-top: 8px;
    padding: 6px 12px;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 4px;
    color: var(--sr-text-secondary);
    font-size: 10px;
    cursor: pointer;
    transition: all 0.2s;
}

.debug-btn:hover {
    background: rgba(255,255,255,0.1);
    color: var(--sr-text-primary);
}

/* AR control panel */
.ar-panel {
    position: absolute;
    bottom: 80px;
    right: 24px;
    padding: 16px;
    background: rgba(0, 0, 0, 0.7);
    border: 1px solid rgba(68, 170, 255, 0.3);
    border-radius: 12px;
    backdrop-filter: blur(10px);
    min-width: 220px;
    transition: all 0.3s;
}

.ar-panel.highlight {
    border-color: rgba(255, 215, 0, 0.6);
    box-shadow: 0 0 30px rgba(255, 215, 0, 0.4);
    animation: highlight-pulse 2s infinite;
}

@keyframes highlight-pulse {
    0%, 100% {
        box-shadow: 0 0 20px rgba(255, 215, 0, 0.4);
    }
    50% {
        box-shadow: 0 0 40px rgba(255, 215, 0, 0.6);
    }
}

.ar-button {
    width: 100%;
    padding: 14px 20px;
    background: rgba(68, 170, 255, 0.25);
    border: 2px solid rgba(68, 170, 255, 0.5);
    border-radius: 10px;
    color: white;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s;
    text-align: center;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
}

.ar-button:active {
    transform: scale(0.98);
}

.ar-button:hover {
    background: rgba(68, 170, 255, 0.35);
    box-shadow: 0 0 20px rgba(68, 170, 255, 0.6);
}

.ar-button.pulse-animation {
    animation: pulse-button 1.5s infinite;
}

@keyframes pulse-button {
    0%, 100% {
        transform: scale(1);
        box-shadow: 0 0 15px rgba(68, 170, 255, 0.5);
    }
    50% {
        transform: scale(1.05);
        box-shadow: 0 0 25px rgba(68, 170, 255, 0.8);
    }
}

.ar-button.requesting {
    background: rgba(255, 165, 0, 0.3);
    border-color: rgba(255, 165, 0, 0.6);
    color: #FFA500;
    cursor: wait;
}

.ar-button.requesting .button-icon {
    animation: spin 1s linear infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

.ar-button.active {
    background: rgba(76, 175, 80, 0.35);
    border-color: rgba(76, 175, 80, 0.6);
    color: #4CAF50;
    animation: pulse-ar 2s infinite;
}

@keyframes pulse-ar {
    0%, 100% {
        box-shadow: 0 0 15px rgba(76, 175, 80, 0.5);
    }
    50% {
        box-shadow: 0 0 25px rgba(76, 175, 80, 0.8);
    }
}

.ar-button:disabled {
    opacity: 0.7;
    cursor: wait;
}

.button-icon {
    font-size: 18px;
}

.button-text {
    flex: 1;
}

/* Test button */
.test-button {
    width: 100%;
    margin-top: 8px;
    padding: 8px;
    background: rgba(255, 165, 0, 0.2);
    border: 1px solid rgba(255, 165, 0, 0.4);
    border-radius: 6px;
    color: #FFA500;
    font-size: 11px;
    cursor: pointer;
    transition: all 0.2s;
}

.test-button:active {
    transform: scale(0.95);
    background: rgba(255, 165, 0, 0.3);
}

.hint-text {
    font-size: 10px;
    color: var(--sr-text-secondary);
    margin-top: 8px;
    text-align: center;
    opacity: 0.8;
}

/* Debug information */
.debug-info {
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid rgba(255,255,255,0.1);
}

.debug-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 6px;
    font-size: 11px;
}

.debug-row .label {
    color: var(--sr-text-secondary);
}

.debug-row .value {
    color: var(--sr-accent-color);
    font-weight: 600;
    font-family: 'Courier New', monospace;
}

/* Display controls */
.display-controls {
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid rgba(255,255,255,0.1);
}

.control-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
}

.control-label {
    font-size: 11px;
    color: var(--sr-text-primary);
}

/* Toggle Switch */
.toggle-switch {
    position: relative;
    width: 40px;
    height: 20px;
    display: inline-block;
}

.toggle-switch input {
    opacity: 0;
    width: 0;
    height: 0;
}

.slider {
    position: absolute;
    cursor: pointer;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(255,255,255,0.1);
    border-radius: 20px;
    transition: .3s;
    border: 1px solid rgba(255,255,255,0.2);
}

.slider:before {
    position: absolute;
    content: "";
    height: 14px;
    width: 14px;
    left: 2px;
    bottom: 2px;
    background-color: white;
    border-radius: 50%;
    transition: .3s;
}

input:checked + .slider {
    background-color: var(--sr-accent-color);
    border-color: var(--sr-accent-color);
}

input:checked + .slider:before {
    transform: translateX(20px);
}

/* Horizon line */
.horizon-line {
    position: absolute;
    bottom: 40px;
    left: 0;
    width: 100%;
    height: 2px;
    background: linear-gradient(90deg, 
        transparent 0%, 
        rgba(68, 170, 255, 0.3) 20%, 
        rgba(68, 170, 255, 0.6) 50%, 
        rgba(68, 170, 255, 0.3) 80%, 
        transparent 100%
    );
    pointer-events: none;
}

.horizon-label {
    position: absolute;
    left: 50%;
    transform: translateX(-50%);
    bottom: 8px;
    font-size: 10px;
    color: rgba(68, 170, 255, 0.6);
    letter-spacing: 2px;
    text-transform: uppercase;
}

/* AR compass display */
.ar-compass {
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid rgba(255,255,255,0.1);
    text-align: center;
}

.compass-value {
    font-size: 24px;
    font-weight: 700;
    color: var(--sr-accent-color);
    font-family: 'Courier New', monospace;
    margin-bottom: 4px;
}

.compass-label {
    font-size: 14px;
    color: var(--sr-text-primary);
    letter-spacing: 2px;
}
.ui-layer {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 10;
    pointer-events: none; /* Let clicks pass through to canvas */
}

/* Re-enable pointer events for UI elements */
.ui-layer > * {
    pointer-events: auto;
}
/* 极简宇宙风格全局样式 */
:root {
  --sr-bg-glass: rgba(10, 15, 30, 0.65);
  --sr-border-glass: rgba(255, 255, 255, 0.12);
  --sr-text-primary: #ffffff;
  --sr-text-secondary: rgba(255, 255, 255, 0.6);
  --sr-accent-color: #44aaff;
  --sr-font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

.sr-glass-panel {
  background: var(--sr-bg-glass);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid var(--sr-border-glass);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  border-radius: 12px;
  color: var(--sr-text-primary);
  font-family: var(--sr-font-family);
}

.sr-glass-btn {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--sr-border-glass);
  color: var(--sr-text-primary);
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.sr-glass-btn:hover {
  background: rgba(255, 255, 255, 0.15);
  border-color: var(--sr-accent-color);
  text-shadow: 0 0 8px var(--sr-accent-color);
}

.sr-title {
  font-size: 14px;
  font-weight: 600;
  letter-spacing: 1px;
  text-transform: uppercase;
  color: var(--sr-text-secondary);
  margin-bottom: 8px;
}

.sr-value {
  font-size: 24px;
  font-weight: 300;
  letter-spacing: -0.5px;
}

/* 滚动条隐藏但可滚动 */
.sr-scroll::-webkit-scrollbar {
  width: 4px;
}
.sr-scroll::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 2px;
}



</style>