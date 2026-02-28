<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import StarBackground from '@/components/StarBackground.vue'
import BaseButton from '@/components/BaseButton.vue'

const route = useRoute()
const router = useRouter()

// 1. TypeScript Interface for Star Data
interface StarDetail {
  id: string;
  name: string;
  constellation: string;
  distance: string; // e.g., "4.37 light years"
  magnitude: number;
  spectralClass: string;
  coordinates: { ra: string; dec: string };
  description: string;
}

// 2. Reactive State
const star = ref<StarDetail | null>(null)
const isLoading = ref(true)

// 3. Mock Fetching Logic
onMounted(async () => {
  const starId = route.params.id as string
  
  // In a real app, you would fetch from: `/data/star-catalog/${starId}.json`
  setTimeout(() => {
    star.value = {
      id: starId,
      name: starId === 'sirius' ? 'Sirius A' : 'Alpha Centauri',
      constellation: 'Canis Major',
      distance: '8.6 Ly',
      magnitude: -1.46,
      spectralClass: 'A1V',
      coordinates: { ra: '06h 45m 08s', dec: '-16° 42′ 58″' },
      description: 'The brightest star in the night sky. Its name is derived from the Greek word Seirios, meaning "glowing" or "scorching".'
    }
    isLoading.value = false
  }, 800)
})

const goBack = () => router.back()
</script>

<template>
  <StarBackground>
    <div v-if="star" class="detail-container">
      
      <div class="visual-section">
        <BaseButton variant="outline" class="back-btn" @click="goBack">
          ← Back to Catalog
        </BaseButton>
        
        <div class="star-core-wrapper">
          <div class="star-glow"></div>
          <div class="star-core"></div>
        </div>
        
        <div class="visual-footer">
          <h1 class="star-name">{{ star.name }}</h1>
          <p class="star-id">CATALOG ID: {{ star.id.toUpperCase() }}</p>
        </div>
      </div>

      <div class="data-section glass-panel">
        <div class="data-header">
          <span class="status-tag">SIGNAL LOCKED</span>
          <h2 class="section-title">Stellar Telemetry</h2>
        </div>

        <div class="specs-grid">
          <div class="spec-item">
            <span class="label">Distance</span>
            <span class="value">{{ star.distance }}</span>
          </div>
          <div class="spec-item">
            <span class="label">Spectral Class</span>
            <span class="value">{{ star.spectralClass }}</span>
          </div>
          <div class="spec-item">
            <span class="label">Magnitude</span>
            <span class="value">{{ star.magnitude }}</span>
          </div>
          <div class="spec-item">
            <span class="label">Constellation</span>
            <span class="value">{{ star.constellation }}</span>
          </div>
        </div>

        <div class="coordinates-box">
          <div class="coord">
            <span class="label">Right Ascension</span>
            <code>{{ star.coordinates.ra }}</code>
          </div>
          <div class="coord">
            <span class="label">Declination</span>
            <code>{{ star.coordinates.dec }}</code>
          </div>
        </div>

        <div class="description">
          <p>{{ star.description }}</p>
        </div>

        <div class="actions">
          <BaseButton variant="primary">Add to Favorites</BaseButton>
          <BaseButton variant="outline">Download Data</BaseButton>
        </div>
      </div>

    </div>

    <div v-else class="loading-state">
      <div class="scanner-line"></div>
      <p>CALIBRATING SENSORS...</p>
    </div>
  </StarBackground>
</template>

<style scoped>
.detail-container {
  display: grid;
  grid-template-columns: 1fr 450px;
  gap: 40px;
  width: 100%;
  max-width: 1200px;
  height: 80vh;
  align-items: center;
}

/* Visual Section Styles */
.visual-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  position: relative;
}

.back-btn {
  align-self: flex-start;
  width: auto;
}

.star-core-wrapper {
  position: relative;
  width: 300px;
  height: 300px;
}

.star-core {
  width: 100%;
  height: 100%;
  background: radial-gradient(circle, #fff 0%, var(--color-star-primary) 60%, transparent 100%);
  border-radius: 50%;
  box-shadow: 0 0 60px var(--color-star-primary);
  position: relative;
  z-index: 2;
}

.star-glow {
  position: absolute;
  top: -50%; left: -50%; width: 200%; height: 200%;
  background: radial-gradient(circle, var(--color-star-primary) 0%, transparent 70%);
  opacity: 0.2;
  animation: pulse 4s infinite ease-in-out;
}

.star-name {
  font-size: 3rem;
  letter-spacing: 4px;
  margin-bottom: 5px;
}

.star-id {
  color: var(--color-star-secondary);
  font-weight: bold;
  letter-spacing: 2px;
}

/* Data Section Styles */
.data-section {
  padding: 40px;
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 30px;
  overflow-y: auto;
}

.status-tag {
  font-size: 0.7rem;
  background: rgba(0, 255, 136, 0.1);
  color: #00ff88;
  padding: 4px 12px;
  border-radius: 4px;
  border: 1px solid #00ff88;
}

.specs-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.spec-item {
  display: flex;
  flex-direction: column;
}

.label {
  font-size: 0.7rem;
  text-transform: uppercase;
  color: var(--color-text-muted);
  margin-bottom: 4px;
}

.value {
  font-size: 1.2rem;
  font-weight: bold;
  color: var(--color-star-primary);
}

.coordinates-box {
  background: rgba(0, 0, 0, 0.3);
  padding: 20px;
  border-radius: 12px;
  display: flex;
  justify-content: space-between;
}

.description p {
  line-height: 1.6;
  color: var(--color-text-muted);
}

.actions {
  display: flex;
  gap: 15px;
  margin-top: auto;
}

/* Animations */
@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 0.2; }
  50% { transform: scale(1.1); opacity: 0.4; }
}

@media (max-width: 1024px) {
  .detail-container {
    grid-template-columns: 1fr;
    height: auto;
    overflow-y: visible;
  }
  .data-section { height: auto; }
}
</style>