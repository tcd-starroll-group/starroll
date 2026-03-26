<template>
  <div v-if="shouldShowDialog" class="permission-request sr-glass-panel" style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;z-index:200;pointer-events:auto;">
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
import { onMounted, ref } from 'vue';
const emit = defineEmits<{
  (e: 'granted'): void
}>();

const requesting = ref(false);
const shouldShowDialog = ref(false);

type IOSPermissionState = 'granted' | 'denied';
type PermissionStatusState = 'granted' | 'denied' | 'prompt' | 'unknown' | 'not-required';

async function checkCameraPermission(): Promise<PermissionStatusState> {
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    return 'not-required';
  }

  const permissionsApi = navigator.permissions;
  if (!permissionsApi || typeof permissionsApi.query !== 'function') {
    return 'unknown';
  }

  try {
    const status = await permissionsApi.query({ name: 'camera' as PermissionName });
    return status.state;
  } catch {
    return 'unknown';
  }
}

async function checkDeviceOrientationPermission(): Promise<PermissionStatusState> {
  const deviceOrientation = (window as any).DeviceOrientationEvent;
  if (!deviceOrientation) {
    return 'not-required';
  }

  if (typeof deviceOrientation.requestPermission !== 'function') {
    return 'granted';
  }

  return new Promise((resolve) => {
    let settled = false;
    const done = (value: PermissionStatusState) => {
      if (settled) return;
      settled = true;
      window.removeEventListener('deviceorientation', onOrientation);
      resolve(value);
    };

    const timer = window.setTimeout(() => {
      done('unknown');
    }, 600);

    const onOrientation = (event: DeviceOrientationEvent) => {
      if (
        event.alpha !== null ||
        event.beta !== null ||
        event.gamma !== null
      ) {
        window.clearTimeout(timer);
        done('granted');
      }
    };

    window.addEventListener('deviceorientation', onOrientation, { once: true });
  });
}

async function precheckPermissions() {
  const [cameraPermission, orientationPermission] = await Promise.all([
    checkCameraPermission(),
    checkDeviceOrientationPermission(),
  ]);

  const cameraReady = cameraPermission === 'granted' || cameraPermission === 'not-required';
  const orientationReady = orientationPermission === 'granted' || orientationPermission === 'not-required';

  if (cameraReady && orientationReady) {
    emit('granted');
    return;
  }

  shouldShowDialog.value = true;
}

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

onMounted(() => {
  void precheckPermissions();
});
</script>

<style scoped>
.permission-request { pointer-events: auto; }
</style>