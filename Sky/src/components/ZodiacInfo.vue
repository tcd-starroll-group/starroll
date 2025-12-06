<script setup lang="ts">
import { defineProps, defineEmits } from 'vue';
import type { Constellation } from '../data/zodiac';

defineProps<{
  data: Constellation | null;
  visible: boolean;
}>();

const emit = defineEmits(['close']);
</script>

<template>
  <transition name="fade-scale">
    <div v-if="visible && data" class="zodiac-overlay" @click.self="emit('close')">
      <div class="info-card">
        <button class="close-btn" @click="emit('close')">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
        
        <div class="header">
          <div class="symbol">{{ data.symbol }}</div>
          <div class="names">
            <h1>{{ data.name }}</h1>
            <span class="latin">{{ data.latinName }}</span>
          </div>
        </div>

        <div class="meta-row">
          <div class="meta-item">
            <span class="label">DATE</span>
            <span class="value">{{ data.dates }}</span>
          </div>
          <div class="meta-item">
            <span class="label">ELEMENT</span>
            <span class="value">{{ data.element }}</span>
          </div>
        </div>

        <div class="divider"></div>

        <p class="description">{{ data.description }}</p>
      </div>
    </div>
  </transition>
</template>

<style scoped>
/* Font Import assumed in global CSS */

.zodiac-overlay {
  position: fixed;
  top: 0; left: 0;
  width: 100%; height: 100%;
  background: rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(4px);
  z-index: 9999;
  display: flex;
  justify-content: center;
  align-items: center;
  perspective: 1000px;
}

.info-card {
  position: relative;
  width: 85%;
  max-width: 380px;
  background: rgba(20, 24, 35, 0.65);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  box-shadow: 
    0 20px 50px rgba(0, 0, 0, 0.5),
    inset 0 0 0 1px rgba(255, 255, 255, 0.05);
  border-radius: 24px;
  padding: 2rem;
  color: white;
  overflow: hidden;
  transform-style: preserve-3d;
}

/* Subtle Glow Background inside card */
.info-card::before {
  content: '';
  position: absolute;
  top: -50%; left: -50%;
  width: 200%; height: 200%;
  background: radial-gradient(circle at 50% 50%, rgba(100, 150, 255, 0.1), transparent 60%);
  pointer-events: none;
  z-index: -1;
}

.close-btn {
  position: absolute;
  top: 1.2rem; right: 1.2rem;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 50%;
  width: 36px; height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: rotate(90deg);
}

.header {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.symbol {
  font-size: 3.5rem;
  background: linear-gradient(135deg, #fff, #88aaff);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  filter: drop-shadow(0 0 15px rgba(136, 170, 255, 0.5));
}

.names {
  display: flex;
  flex-direction: column;
}

.names h1 {
  margin: 0;
  font-family: 'Cinzel', serif;
  font-weight: 400;
  font-size: 1.8rem;
  letter-spacing: 2px;
  text-shadow: 0 0 10px rgba(255,255,255,0.3);
}

.names .latin {
  font-family: sans-serif;
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.5);
  text-transform: uppercase;
  letter-spacing: 4px;
  margin-top: 4px;
}

.meta-row {
  display: flex;
  gap: 2rem;
  margin-bottom: 1.5rem;
}

.meta-item {
  display: flex;
  flex-direction: column;
}

.label {
  font-size: 0.7rem;
  color: rgba(136, 170, 255, 0.8);
  letter-spacing: 1px;
  margin-bottom: 4px;
}

.value {
  font-family: 'Cinzel', serif;
  font-size: 1rem;
}

.divider {
  height: 1px;
  background: linear-gradient(to right, rgba(255,255,255,0), rgba(255,255,255,0.3), rgba(255,255,255,0));
  margin-bottom: 1.5rem;
}

.description {
  line-height: 1.6;
  font-weight: 300;
  font-size: 0.95rem;
  color: rgba(255, 255, 255, 0.9);
  text-align: justify;
}

/* Animations */
.fade-scale-enter-active,
.fade-scale-leave-active {
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

.fade-scale-enter-from,
.fade-scale-leave-to {
  opacity: 0;
  transform: scale(0.9) translateY(20px);
}
</style>


