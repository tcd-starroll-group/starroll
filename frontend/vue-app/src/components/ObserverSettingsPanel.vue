<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue';

type ObserverSettings = {
  utcTimestampMs: number;
  lat: number;
  lon: number;
};

const emit = defineEmits<{
  (e: 'apply', payload: ObserverSettings): void;
}>();

const utcTimestampMs = ref<number>(Date.now());
const lat = ref<number>(53.3498);
const lon = ref<number>(-6.2603);
const panelVisible = ref(false);
const sliderValue = ref(0);
const lastSliderValue = ref(0);
const sliderStepSeconds = 60;
const timeMultiplier = ref(1);
let timerId: number | null = null;

const pad = (value: number) => String(value).padStart(2, '0');

const clamp = (value: number, min: number, max: number) => Math.min(max, Math.max(min, value));

const localDateTimeInput = computed({
  get: () => {
    const date = new Date(utcTimestampMs.value);
    const year = date.getFullYear();
    const month = pad(date.getMonth() + 1);
    const day = pad(date.getDate());
    const hour = pad(date.getHours());
    const minute = pad(date.getMinutes());
    const second = pad(date.getSeconds());
    return `${year}-${month}-${day}T${hour}:${minute}:${second}`;
  },
  set: (value: string) => {
    const parsed = new Date(value).getTime();
    if (!Number.isNaN(parsed)) {
      utcTimestampMs.value = parsed;
      onApply();
    }
  },
});

const onLocationInput = () => {
  const latitude = Number(lat.value);
  const longitude = Number(lon.value);
  if (Number.isFinite(latitude) && Number.isFinite(longitude)) {
    onApply();
  }
};

const applyTimeOffset = (offsetSeconds: number) => {
  utcTimestampMs.value += offsetSeconds * 1000;
  onApply();
};

const onTimeSliderInput = () => {
  const current = clamp(Number(sliderValue.value), -120, 120);
  const delta = current - lastSliderValue.value;
  if (delta !== 0) {
    applyTimeOffset(delta * sliderStepSeconds);
    lastSliderValue.value = current;
  }
};

const onTimeSliderChange = () => {
  sliderValue.value = 0;
  lastSliderValue.value = 0;
};

const stopAutoTick = () => {
  if (timerId !== null) {
    clearInterval(timerId);
    timerId = null;
  }
};

const startAutoTick = () => {
  stopAutoTick();
  const multiplier = clamp(Number(timeMultiplier.value) || 1, 1, 10000);
  timeMultiplier.value = multiplier;

  const intervalMs = multiplier === 1 ? 1000 : 50;
  const advanceMsPerTick = intervalMs * multiplier;

  timerId = window.setInterval(() => {
    utcTimestampMs.value += advanceMsPerTick;
    onApply();
  }, intervalMs);
};

const onMultiplierInput = () => {
  timeMultiplier.value = clamp(Number(timeMultiplier.value) || 1, 1, 10000);
  startAutoTick();
};

const onApply = () => {
  emit('apply', {
    utcTimestampMs: utcTimestampMs.value,
    lat: Number(lat.value),
    lon: Number(lon.value),
  });
};

const useCurrentTimeAndLocation = async () => {
  utcTimestampMs.value = Date.now();

  if (navigator.geolocation) {
    try {
      const position = await new Promise<GeolocationPosition>((resolve, reject) => {
        navigator.geolocation.getCurrentPosition(resolve, reject, {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 0,
        });
      });
      lat.value = position.coords.latitude;
      lon.value = position.coords.longitude;
    } catch (error) {
      console.warn('Failed to get current location, keeping existing coordinates.', error);
    }
  }

  onApply();
};

onMounted(async () => {
  await useCurrentTimeAndLocation();
  startAutoTick();
});

watch(timeMultiplier, () => {
  startAutoTick();
});

onUnmounted(() => {
  stopAutoTick();
});
</script>

<template>
  <button class="settings-toggle" @click="panelVisible = !panelVisible">
    <img src="/images/time_and_location.png" alt="Time and location settings" />
  </button>

  <div v-if="panelVisible" class="settings-panel sr-glass-panel">
    <div class="header-row">
      <div class="sr-title">Observer Settings</div>
      <button class="close-btn" @click="panelVisible = false">×</button>
    </div>

    <label>
      Time
      <input v-model="localDateTimeInput" type="datetime-local" step="1" />
    </label>

    <label>
      Slide to adjust time
      <div class="time-gear-control">
        <input
          v-model.number="sliderValue"
          class="gear-slider"
          type="range"
          min="-120"
          max="120"
          step="1"
          @input="onTimeSliderInput"
          @change="onTimeSliderChange"
        />
      </div>
    </label>

    <label>
      Time multiplier (1-10000)
      <input
        v-model.number="timeMultiplier"
        type="number"
        min="1"
        max="10000"
        step="1"
        @input="onMultiplierInput"
      />
    </label>

    <label>
      Latitude
      <input v-model.number="lat" type="number" step="0.000001" min="-90" max="90" @input="onLocationInput" />
    </label>

    <label>
      Longitude
      <input v-model.number="lon" type="number" step="0.000001" min="-180" max="180" @input="onLocationInput" />
    </label>

    <button class="sr-glass-btn" @click="useCurrentTimeAndLocation">Use current time and location</button>

    <div class="utc-ms">UTC ms: {{ utcTimestampMs }}</div>
  </div>
</template>

<style scoped>
.settings-panel {
  position: absolute;
  top: 68px;
  right: 76px;
  z-index: 20;
  padding: 12px;
  display: grid;
  gap: 8px;
  width: 260px;
}

.settings-toggle {
  position: absolute;
  top: 20px;
  right: 76px;
  z-index: 21;
  width: 40px;
  height: 40px;
  border: none;
  border-radius: 10px;
  background: transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  /* backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px); */
}

.settings-toggle img {
  width: 24px;
  height: 24px;
}

.header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.close-btn {
  border: 1px solid var(--sr-border-glass);
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.05);
  color: var(--sr-text-primary);
  width: 24px;
  height: 24px;
  line-height: 20px;
  cursor: pointer;
}
label {
  display: grid;
  gap: 4px;
  font-size: 12px;
}
input {
  width: 100%;
}

.time-gear-control {
  display: grid;
  gap: 8px;
}

.gear-slider {
  accent-color: var(--sr-text-primary);
}

.utc-ms {
  font-size: 11px;
  color: var(--sr-text-secondary);
  word-break: break-all;
}
</style>