<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import StarBackground from '@/components/StarBackground.vue';
import '../assets/styles/common.css';
import '../assets/styles/main.css';

const router = useRouter();

const hipInput = ref('');
const isLoading = ref(false);
const errorMessage = ref('');
const starData = ref<any>(null);

const parseHipNumber = (input: string): number | null => {
  const cleaned = input.trim().replace(/^hip\s*/i, '');
  const n = parseInt(cleaned, 10);
  return isNaN(n) || n <= 0 ? null : n;
};

const radToDeg = (rad: number) => (rad * 180) / Math.PI;

const formatRA = (rad: number) => {
  const totalDeg = ((rad * 180) / Math.PI + 360) % 360;
  const hours = totalDeg / 15;
  const h = Math.floor(hours);
  const minRaw = (hours - h) * 60;
  const m = Math.floor(minRaw);
  const s = ((minRaw - m) * 60).toFixed(2);
  return `${String(h).padStart(2, '0')}h ${String(m).padStart(2, '0')}m ${s}s`;
};

const formatDec = (deg: number) => {
  const sign = deg < 0 ? '-' : '+';
  const abs = Math.abs(deg);
  const d = Math.floor(abs);
  const minRaw = (abs - d) * 60;
  const m = Math.floor(minRaw);
  const s = ((minRaw - m) * 60).toFixed(1);
  return `${sign}${String(d).padStart(2, '0')}° ${String(m).padStart(2, '0')}′ ${s}″`;
};

const formatPM = (radPerYr: number) => {
  const masPerYr = radPerYr * (180 / Math.PI) * 3600 * 1000;
  return `${masPerYr.toFixed(3)} mas/yr`;
};

const searchStar = async () => {
  const hip = parseHipNumber(hipInput.value);
  if (hip === null) {
    errorMessage.value = 'Please enter a valid HIP number (e.g. 88 or HIP 88).';
    return;
  }

  isLoading.value = true;
  errorMessage.value = '';
  starData.value = null;

  const baseUrl = import.meta.env?.BASE_URL || '/';
  const cleanBase = baseUrl.endsWith('/') ? baseUrl.slice(0, -1) : baseUrl;

  try {
    const response = await fetch(`${cleanBase}/data/stars-data/HIP_${hip}.json`);
    if (!response.ok) {
      if (response.status === 404) {
        errorMessage.value = `No data found for HIP ${hip}. The star may not be in the catalogue.`;
      } else {
        errorMessage.value = `Request failed (HTTP ${response.status}). Please try again.`;
      }
      return;
    }
    const contentType = response.headers.get('content-type') || '';
    if (!contentType.includes('application/json')) {
      errorMessage.value = `HIP ${hip} is not yet in the Starroll catalogue. Only stars with relatively high brightness are currently included.`;
      return;
    }
    let data: any;
    try {
      data = await response.json();
    } catch {
      errorMessage.value = `HIP ${hip} is not yet in the Starroll catalogue. Only stars with relatively high brightness are currently included.`;
      return;
    }
    starData.value = data;
  } catch (err) {
    console.error('Search star error:', err);
    errorMessage.value = 'A network error occurred. Please check your connection and try again.';
  } finally {
    isLoading.value = false;
  }
};

const handleKeydown = (e: KeyboardEvent) => {
  if (e.key === 'Enter') searchStar();
};


const navigateToAR = (hip: number) => {
  // Hard-navigate with a full page reload so Chrome starts fresh —
  // this clears any leftover zoom / shrunken-viewport state caused by
  // the soft keyboard that was open on this page.
  const base = import.meta.env.BASE_URL?.replace(/\/$/, '') ?? '';
  window.location.href = `${base}/?find_hip=${hip}`;
};
</script>

<template>
  <StarBackground>
    <div class="search-container">

      <!-- Header -->
      <header class="search-header">
        <button class="back-btn" @click="router.back()" aria-label="Go back">
          <svg viewBox="0 0 24 24" width="22" height="22">
            <path fill="currentColor" d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z"/>
          </svg>
        </button>
        <div>
          <h1 class="title">Search Stars</h1>
          <p class="subtitle">Look up a star by its Hipparcos catalogue number</p>
        </div>
      </header>

      <!-- Search Input -->
      <div class="search-box glass-panel">
        <div class="input-row">
          <div class="input-wrapper">
            <svg class="input-icon" viewBox="0 0 24 24" width="18" height="18">
              <path fill="currentColor" d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
            </svg>
            <input
              v-model="hipInput"
              type="text"
              class="hip-input"
              placeholder="Enter HIP number  (e.g. 88 or HIP 88)"
              @keydown="handleKeydown"
              :disabled="isLoading"
            />
          </div>
          <button
            class="search-btn"
            @click="searchStar"
            :disabled="isLoading || !hipInput.trim()"
          >
            <span v-if="isLoading" class="spinner"></span>
            <span v-else>Search</span>
          </button>
        </div>
      </div>

      <!-- Error -->
      <div v-if="errorMessage" class="error-banner glass-panel">
        <svg viewBox="0 0 24 24" width="18" height="18" style="flex-shrink:0">
          <path fill="currentColor" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
        </svg>
        <span>{{ errorMessage }}</span>
      </div>

      <!-- Loading skeleton -->
      <div v-if="isLoading" class="result-card glass-panel skeleton-wrap">
        <div class="skeleton-title"></div>
        <div class="skeleton-line"></div>
        <div class="skeleton-line short"></div>
        <div class="skeleton-line"></div>
        <div class="skeleton-line short"></div>
      </div>

      <!-- Result Card -->
      <div v-if="starData && !isLoading" class="result-card glass-panel">

        <!-- Star name & HIP -->
        <div class="result-header">
          <div class="star-icon-wrap">
            <svg viewBox="0 0 24 24" width="28" height="28">
              <path fill="currentColor" d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/>
            </svg>
          </div>
          <div>
            <h2 class="star-name">{{ starData.name || `HIP ${starData.hip}` }}</h2>
            <span class="hip-badge">HIP {{ starData.hip }}</span>
          </div>
        </div>

        <!-- Description -->
        <p v-if="starData.description" class="star-description">{{ starData.description }}</p>

        <!-- Data grid -->
        <div class="data-grid">
          <div class="data-item">
            <span class="data-label">Right Ascension</span>
            <span class="data-value">{{ formatRA(starData.alpha) }}</span>
          </div>
          <div class="data-item">
            <span class="data-label">Declination</span>
            <span class="data-value">{{ formatDec(starData.delta) }}</span>
          </div>
          <div class="data-item">
            <span class="data-label">Magnitude</span>
            <span class="data-value">{{ starData.mag?.toFixed(2) }}</span>
          </div>
          <div class="data-item">
            <span class="data-label">Distance</span>
            <span class="data-value">{{ starData.distance?.toFixed(1) }} ly</span>
          </div>
          <div class="data-item">
            <span class="data-label">B-V Color Index</span>
            <span class="data-value">{{ starData.bvColor?.toFixed(3) }}</span>
          </div>
          <div class="data-item">
            <span class="data-label">Proper Motion (RA)</span>
            <span class="data-value">{{ formatPM(starData.pmRA) }}</span>
          </div>
          <div class="data-item">
            <span class="data-label">Proper Motion (Dec)</span>
            <span class="data-value">{{ formatPM(starData.pmDE) }}</span>
          </div>
        </div>

        <!-- Actions row -->
        <button class="find-ar-btn" @click="navigateToAR(starData.hip)">
          <svg viewBox="0 0 24 24" width="16" height="16">
            <path fill="currentColor" d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/>
          </svg>
          Find in AR
        </button>
      </div>

    </div>
  </StarBackground>
</template>

<style scoped>
.search-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  padding: 40px 24px 60px;
  color: var(--color-text-main);
  /* Let the browser/page scroll naturally — no inner overflow needed */
}

/* Header */
.search-header {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 32px;
}
.back-btn {
  flex-shrink: 0;
  margin-top: 4px;
  background: var(--color-bg-surface);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  color: var(--color-text-main);
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.2s, border-color 0.2s;
}
.back-btn:hover {
  background: rgba(88, 166, 255, 0.15);
  border-color: rgba(88, 166, 255, 0.4);
}
.title {
  font-size: 32px;
  font-weight: 800;
  letter-spacing: 1.5px;
  color: #fff;
  text-shadow: var(--shadow-glow);
  text-align: left;
  margin-bottom: 4px;
}
.subtitle {
  font-size: 13px;
  color: var(--color-text-muted);
  letter-spacing: 0.5px;
  text-align: left;
  margin-bottom: 0;
}

/* Search box */
.search-box {
  padding: 20px;
  margin-bottom: 20px;
  border-radius: 20px;
}
.input-row {
  display: flex;
  gap: 12px;
  align-items: center;
}
.input-wrapper {
  flex: 1;
  position: relative;
  display: flex;
  align-items: center;
}
.input-icon {
  position: absolute;
  left: 14px;
  color: var(--color-text-muted);
  pointer-events: none;
}
.hip-input {
  width: 100%;
  padding: 12px 14px 12px 42px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 12px;
  color: var(--color-text-main);
  font-size: 16px; /* Must be ≥16px to prevent iOS Safari auto-zoom on focus */
  font-family: inherit;
  outline: none;
  transition: border-color 0.2s, background 0.2s;
}
.hip-input::placeholder {
  color: var(--color-text-muted);
  font-size: 13px;
}
.hip-input:focus {
  border-color: var(--color-star-primary);
  background: rgba(88, 166, 255, 0.06);
}
.hip-input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.search-btn {
  flex-shrink: 0;
  padding: 12px 24px;
  background: linear-gradient(135deg, var(--color-star-primary), var(--color-star-secondary));
  color: #fff;
  border: none;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  transition: opacity 0.2s, transform 0.15s;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 90px;
  height: 45px;
}
.search-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
.search-btn:not(:disabled):hover {
  opacity: 0.9;
  transform: translateY(-1px);
}
.search-btn:not(:disabled):active {
  transform: translateY(0);
}

/* Spinner */
.spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Error */
.error-banner {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 18px;
  border-radius: 14px;
  color: var(--color-error);
  border-color: rgba(255, 123, 114, 0.25) !important;
  background: rgba(255, 123, 114, 0.08) !important;
  margin-bottom: 16px;
  font-size: 14px;
  line-height: 1.5;
}

/* Skeleton */
.skeleton-wrap {
  padding: 24px;
  border-radius: 20px;
}
.skeleton-title,
.skeleton-line {
  background: linear-gradient(90deg, rgba(255,255,255,0.05) 25%, rgba(255,255,255,0.1) 50%, rgba(255,255,255,0.05) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.4s infinite;
  border-radius: 8px;
  margin-bottom: 14px;
}
.skeleton-title {
  height: 26px;
  width: 55%;
}
.skeleton-line {
  height: 16px;
  width: 80%;
}
.skeleton-line.short {
  width: 55%;
}
@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* Result card */
.result-card {
  padding: 24px;
  border-radius: 20px;
}

.result-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}

.star-icon-wrap {
  flex-shrink: 0;
  width: 56px;
  height: 56px;
  border-radius: 16px;
  background: linear-gradient(135deg, rgba(88, 166, 255, 0.2), rgba(147, 51, 234, 0.2));
  border: 1px solid rgba(88, 166, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-star-primary);
}

.star-name {
  font-size: 18px;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.95);
  margin-bottom: 6px;
  line-height: 1.3;
}

.hip-badge {
  display: inline-block;
  font-size: 12px;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 20px;
  background: rgba(88, 166, 255, 0.15);
  color: var(--color-star-primary);
  border: 1px solid rgba(88, 166, 255, 0.3);
  letter-spacing: 0.5px;
}

.star-description {
  font-size: 14px;
  color: var(--color-text-muted);
  line-height: 1.6;
  margin-bottom: 20px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 10px;
  border-left: 3px solid rgba(88, 166, 255, 0.4);
}

/* Data grid */
.data-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 24px;
}

.data-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 12px 14px;
  background: rgba(255, 255, 255, 0.04);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.data-label {
  font-size: 11px;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.8px;
  font-weight: 500;
}

.data-value {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  word-break: break-all;
}

/* Find in AR button */
.find-ar-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  width: 100%;
  font-size: 14px;
  font-weight: 600;
  color: #fff;
  padding: 13px 18px;
  border-radius: 12px;
  border: none;
  background: linear-gradient(135deg, var(--color-star-primary), var(--color-star-secondary));
  cursor: pointer;
  transition: opacity 0.2s, transform 0.15s;
  font-family: inherit;
}
.find-ar-btn:hover {
  opacity: 0.88;
  transform: translateY(-1px);
}
.find-ar-btn:active {
  transform: translateY(0);
}

/* Responsive: single column on narrow screens */
@media (max-width: 400px) {
  .data-grid {
    grid-template-columns: 1fr;
  }
  .input-row {
    flex-direction: column;
  }
  .search-btn {
    width: 100%;
  }
}
</style>
