<template>
  <div class="permission-request sr-glass-panel" style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;z-index:200;pointer-events:auto;">
    <div style="max-width:420px;padding:20px;text-align:center;">
      <h3 class="sr-title">Camera & Sensor Permissions Required</h3>
      <p class="sr-value" style="font-size:13px;margin:8px 0 16px;">Allow access to the camera and device orientation sensors to enable the AR experience.</p>
      <button class="sr-glass-btn" @click="requestAll" :disabled="requesting">
        {{ requesting ? 'Requesting...' : 'Grant permission & continue' }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
const emit = defineEmits<{
  (e: 'granted'): void
}>();

const requesting = ref(false);

type IOSPermissionState = 'granted' | 'denied';

async function requestDeviceOrientationPermission(): Promise<IOSPermissionState | 'not-required'> {
  const deviceOrientation = (window as any).DeviceOrientationEvent;
  if (!deviceOrientation || typeof deviceOrientation.requestPermission !== 'function') {
    return 'not-required';
  }

  try {
    const permission = await deviceOrientation.requestPermission();
    return permission === 'granted' ? 'granted' : 'denied';
  } catch {
    return 'denied';
  }
}

async function trySensorGrant() {
  if (!(window as any).AbsoluteOrientationSensor) return;
  try {
    const SensorClass = (window as any).AbsoluteOrientationSensor;
    const s = new SensorClass({ frequency: 10 });
    // start/stop to trigger permission prompt
    s.start();
    await new Promise((r) => setTimeout(r, 500));
    s.stop();
  } catch {
    // ignore
  }
}

async function requestAll() {
  requesting.value = true;
  let orientationPermission: IOSPermissionState | 'not-required' = 'not-required';

  try {
    // iOS Safari: must be called in user gesture context
    orientationPermission = await requestDeviceOrientationPermission();

    // request camera
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      await navigator.mediaDevices.getUserMedia({ video: true });
    }
  } catch {
    // user denied or unavailable
  }
  try {
    await trySensorGrant();
  } catch {}

  requesting.value = false;
  if (orientationPermission !== 'denied') {
    emit('granted');
  }
}
</script>

<style scoped>
.permission-request { pointer-events: auto; }
</style>