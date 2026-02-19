<script setup lang="ts">
import { onMounted, ref, onUnmounted } from 'vue';
import { useGroundObserver } from './composables/useGroundObserver';
import { sensorManager, type SensorData } from '@/core/Tensors/sensor'; 
import TopBar from './components/TopBar.vue';
import InfoPanel from './components/InfoPanel.vue';
import SensorDebugPanel from './components/SensorDebugPanel.vue';
import StarInfoPanel from './components/StarInfoPanel.vue';
import StarPopup from './components/StarPopup.vue'; // [Added] Import new popup component
import type { StarClickInfo } from '@/core/renderer/GroundObserverRenderer'; // [Added] Import click info type
import './assets/starroll.css';

const containerRef = ref<HTMLElement | null>(null);
const showDebugPanel = ref(false);
const showWelcomeHint = ref(true);

const { 
    init, 
    stats, 
    refreshStats,
    currentLocation,
    arModeEnabled,
    enableARMode,
    disableARMode,
    cameraOrientation,
    showConstellationLines,
    toggleConstellationLines,
    showStarLabels,
    toggleStarLabels,
    selectedStar,
    closeStarInfo,
    requestUserLocation,
    useCurrentLocationAndTime,
    isRequestingLocation,
    renderer
} = useGroundObserver();

// Detect mobile device
const isMobile = /Android|iPhone|iPad/i.test(navigator.userAgent);
const isIOS = /iPhone|iPad|iPod/i.test(navigator.userAgent);

const clickedStarInfo = ref<StarClickInfo | null>(null);

// [Added] Method to close star popup
const closeStarPopup = () => {
    clickedStarInfo.value = null;
};

// [Added] Compass related state
const showCompass = ref(false);
const compassHeading = ref(0);
const compassDirection = ref('--');

/**
 * Get direction label from azimuth angle
 * @param azimuth - Azimuth angle in degrees (0-360)
 * @returns Cardinal direction label (N, NE, E, SE, S, SW, W, NW)
 */
const getDirectionLabel = (azimuth: number): string => {
    const directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'];
    const index = Math.round(azimuth / 45) % 8;
    return directions[index];
};

/**
 * Handle compass data updates from sensor manager
 * @param data - Sensor data containing orientation information
 */
const handleCompassUpdate = (data: SensorData) => {
    const orientation = sensorManager.getCameraOrientation(data);
    if (orientation) {
        compassHeading.value = orientation.azimuth;
        compassDirection.value = getDirectionLabel(orientation.azimuth);
    }
};

/**
 * Toggle compass functionality
 * Requests sensor permission if needed and manages sensor listeners
 */
const toggleCompass = async () => {
    if (showCompass.value) {
        // Disable compass
        showCompass.value = false;
        sensorManager.removeListener(handleCompassUpdate);
        // Stop sensor listening to save power if AR mode is not active
        if (!arModeEnabled.value) {
            sensorManager.stopListening();
        }
    } else {
        // Enable compass
        // 1. Request permission if needed
        if (sensorManager.getPermissionState() === 'prompt') {
            const result = await sensorManager.requestPermission();
            if (result === 'denied') {
                alert('Sensor permissions are required to display the compass');
                return;
            }
        }
        
        // 2. Start listening to sensor data
        sensorManager.addListener(handleCompassUpdate);
        sensorManager.startListening();
        showCompass.value = true;
    }
};

onMounted(async () => {
    if (containerRef.value) {
        console.log('Starting Ground Observer mode');
        console.log('View: Earth surface observer');
        console.log('Coordinate System: Horizon coordinates');
        console.log('Preparing for AR rendering');
        
        init(containerRef.value);
        if (renderer.value) {
            renderer.value.setOnStarClick((starInfo: StarClickInfo) => {
                clickedStarInfo.value = starInfo;
            });
        }
        
        // Get stats with delay to ensure data is loaded
        setTimeout(() => {
            refreshStats();
            console.log('Observation Statistics:', stats.value);
            console.log(`Visible Stars: ${stats.value.visibleStars}`);
            console.log(`Visible Constellations: ${stats.value.visibleConstellations}`);
            console.log(`Observation Location: ${stats.value.observerLocation}`);
            console.log(`Local Sidereal Time: ${stats.value.localSiderealTime}°`);
            console.log('');
            console.log('Tip: Drag mouse to look around the sky');
            console.log('Tip: On mobile devices, the view will follow device orientation automatically');
        }, 3500);
        
        // Auto attempt to get current location after startup
        setTimeout(async () => {
            console.log('Automatically attempting to get current location...');
            const success = await useCurrentLocationAndTime();
            if (success) {
                console.log('Successfully updated to current location');
                showLocationHint.value = false;
            } else {
                console.log('Using default location (Shanghai). Click "Use Current Location" button to update');
            }
        }, 2000);
    }
});

// Cleanup on component unmount
onUnmounted(() => {
    sensorManager.removeListener(handleCompassUpdate);
});

// Click request state
const isRequesting = ref(false);

// Location request hint
const showLocationHint = ref(true);

/**
 * Test button click handler
 * Provides device information and haptic feedback
 */
const testButtonClick = () => {
    console.log('Test button clicked!');
    console.log('Device Type:', isMobile ? 'Mobile' : 'Desktop');
    console.log('Is iOS:', isIOS);
    console.log('User Agent:', navigator.userAgent);
    
    // Haptic feedback if supported
    if (navigator.vibrate) {
        navigator.vibrate([50, 100, 50]);
        console.log('Haptic feedback triggered');
    } else {
        console.log('Device does not support haptic feedback');
    }
    
    alert(`Button click test successful!

Device Information:
- Type: ${isMobile ? 'Mobile' : 'Desktop'}
- iOS: ${isIOS ? 'Yes' : 'No'}
- Sensor Support: ${typeof DeviceOrientationEvent !== 'undefined' ? 'Yes' : 'No'}

If you can see this dialog, button events are working correctly!

Next step: Click the "Enable AR" button above to test permission requests.`);
};

/**
 * Handle request for current location and time
 * Updates star map to user's current geographic position
 */
const handleUseCurrentLocation = async () => {
    console.log('Clicked to use current location');
    
    // Haptic feedback
    if (navigator.vibrate) {
        navigator.vibrate(50);
    }
    
    try {
        const success = await useCurrentLocationAndTime();
        
        if (success) {
            console.log('Successfully using current location and time');
            showLocationHint.value = false;
            
            // User notification
            alert(`Location retrieved successfully!

Current Location: ${currentLocation.value.name}
Latitude: ${currentLocation.value.latitude.toFixed(4)}°
Longitude: ${currentLocation.value.longitude.toFixed(4)}°

The star map has been updated to the sky at your current location!`);
        } else {
            console.error('Failed to retrieve location');
            
            alert(`Location retrieval failed

Possible reasons:
1. You denied location permissions
2. Device does not support Geolocation API
3. Location services are disabled

Solutions:
1. Allow location permissions in browser settings
2. Ensure device GPS is enabled
3. Refresh the page and try again`);
        }
    } catch (error) {
        console.error('Error retrieving location:', error);
        alert('Error occurred: ' + error);
    }
};

/**
 * Toggle AR mode
 * Handles permission requests and AR mode activation/deactivation
 */
const toggleARMode = async () => {
    console.log('AR button clicked');
    
    // Haptic feedback (if supported)
    if (navigator.vibrate) {
        navigator.vibrate(50);
    }
    
    if (arModeEnabled.value) {
        disableARMode();
        console.log('AR mode disabled');
        return;
    }
    
    // Show requesting state
    isRequesting.value = true;
    
    try {
        console.log('Requesting sensor permissions...');
        console.log('Waiting for user response to iOS permission dialog...');
        
        const success = await enableARMode();
        
        if (success) {
            console.log('AR mode enabled');
            console.log('Rotate your device to move the star map');
            showWelcomeHint.value = false;
        } else {
            console.error('Failed to enable AR mode');
            
            if (isIOS) {
                alert(`iOS permission request failed

Possible reasons:
1. You denied permissions
2. HTTPS connection is required
3. Safari browser settings issues

Solutions:
1. Use Safari browser (not Chrome)
2. Create an HTTPS tunnel with ngrok
3. Refresh the page and try again
4. Check Safari Settings → Privacy → Motion & Orientation

Is HTTPS required? Check console for detailed information.`);
            } else {
                alert('Unable to enable AR mode\n\nPlease check if your device supports orientation sensors');
            }
        }
    } catch (error) {
        console.error('Error enabling AR mode:', error);
        alert('Error occurred: ' + error);
    } finally {
        isRequesting.value = false;
    }
};
</script>

<template>
  <div class="starroll-app" @click.self="closeStarPopup">
    <div ref="containerRef" class="canvas-container" @click.self="closeStarPopup"></div>
    
    <div class="ui-layer">
        <TopBar v-if="!arModeEnabled" />
        <InfoPanel v-if="!arModeEnabled" />
        <StarPopup 
            :star-info="clickedStarInfo" 
            @close="closeStarPopup" 
        />

        <div v-if="showCompass" class="real-compass-display">
            <div class="compass-ring" :style="{ transform: `rotate(${-compassHeading}deg)` }">
                <span class="mark-n">N</span>
                <span class="mark-e">E</span>
                <span class="mark-s">S</span>
                <span class="mark-w">W</span>
                <div class="compass-pointer"></div>
            </div>
            <div class="compass-text">
                <div class="compass-value">{{ compassHeading.toFixed(0) }}°</div>
                <div class="compass-label">{{ compassDirection }} (Magnetic North)</div>
            </div>
        </div>

        <div class="observer-info" v-if="!arModeEnabled">
          <div class="info-row">
            <span class="icon">📍</span>
            <span class="text">{{ currentLocation.name }}</span>
          </div>
          <div class="info-row small">
            <span>{{ currentLocation.latitude.toFixed(2) }}°N, {{ currentLocation.longitude.toFixed(2) }}°E</span>
          </div>
          <button 
            @click="handleUseCurrentLocation" 
            class="location-btn"
            :disabled="isRequestingLocation"
          >
            {{ isRequestingLocation ? 'Retrieving...' : 'Use Current Location' }}
          </button>
          <button @click="showDebugPanel = true" class="debug-btn">
            Sensor Debug
          </button>
        </div>
        
        <div v-if="showWelcomeHint && isMobile" class="welcome-hint" @click="showWelcomeHint = false">
          <div class="hint-content">
            <div class="hint-icon">📱</div>
            <div class="hint-title">Welcome to AR Star Map</div>
            <div class="hint-text-large">
              {{ isIOS ? 'Tap the "Enable AR Mode" button below' : 'Tap the button below to enable AR' }}
            </div>
            <div class="hint-text-small" v-if="isIOS">
              iOS requires you to manually grant sensor permissions
            </div>
            <div class="hint-dismiss">Tap anywhere to close this hint</div>
          </div>
        </div>
        
        <div class="ar-panel" :class="{ 'highlight': showWelcomeHint && isMobile }">
          
          <button @click="toggleCompass" class="compass-toggle-btn" :class="{ active: showCompass }">
              {{ showCompass ? 'Disable Compass' : 'Enable Real Compass' }}
          </button>

          <button 
            @click="toggleARMode" 
            class="ar-button" 
            :class="{ 
              active: arModeEnabled,
              requesting: isRequesting,
              'pulse-animation': showWelcomeHint && isMobile && !arModeEnabled
            }"
            :disabled="isRequesting"
          >
            <span class="button-icon">
              {{ isRequesting ? '⏳' : (arModeEnabled ? '✅' : '📱') }}
            </span>
            <span class="button-text">
              {{ 
                isRequesting ? 'Requesting Permissions...' :
                arModeEnabled ? 'AR Mode Enabled' : 
                (isIOS ? 'Tap to Enable AR (iOS)' : 'Enable AR Mode') 
              }}
            </span>
          </button>
          
          <button @click="testButtonClick" class="test-button" v-if="!arModeEnabled">
            Test Button Click
          </button>
          <div class="hint-text">{{ arModeEnabled ? 'Rotate device to view stars' : 'Tap button to get sensor permissions' }}</div>
          
          <div class="display-controls" v-if="!arModeEnabled">
            <div class="control-item">
              <span class="control-label">Constellation Lines</span>
              <label class="toggle-switch">
                <input type="checkbox" :checked="showConstellationLines" @change="toggleConstellationLines">
                <span class="slider"></span>
              </label>
            </div>
            <div class="control-item">
              <span class="control-label">Star Labels</span>
              <label class="toggle-switch">
                <input type="checkbox" :checked="showStarLabels" @change="toggleStarLabels">
                <span class="slider"></span>
              </label>
            </div>
          </div>
          
          <div v-if="arModeEnabled" class="ar-compass">
            <div class="compass-value">{{ Math.round(cameraOrientation.azimuth) }}°</div>
            <div class="compass-label">{{ getDirectionLabel(cameraOrientation.azimuth) }}</div>
          </div>
        </div>
        
        <div class="horizon-line">
          <div class="horizon-label">Horizon</div>
        </div>
        
        <SensorDebugPanel 
          v-if="showDebugPanel" 
          @close="showDebugPanel = false"
        />
        
        <StarInfoPanel 
          :star-info="selectedStar"
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

/* [Added] Compass toggle button styles */
.compass-toggle-btn {
    width: 100%;
    margin-bottom: 10px;
    padding: 10px;
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 8px;
    color: white;
    font-size: 12px;
    cursor: pointer;
    transition: all 0.3s;
}

.compass-toggle-btn.active {
    background: rgba(255, 215, 0, 0.2);
    border-color: rgba(255, 215, 0, 0.5);
    color: #FFD700;
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

/* Welcome hint panel */
.welcome-hint {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 90%;
    max-width: 350px;
    padding: 24px;
    background: rgba(0, 0, 0, 0.95);
    border: 2px solid rgba(68, 170, 255, 0.6);
    border-radius: 16px;
    backdrop-filter: blur(20px);
    z-index: 999;
    animation: fadeIn 0.5s ease-out;
    box-shadow: 0 0 40px rgba(68, 170, 255, 0.4);
}

@keyframes fadeIn {
    from { opacity: 0; transform: translate(-50%, -45%); }
    to { opacity: 1; transform: translate(-50%, -50%); }
}

.hint-content {
    text-align: center;
}

.hint-icon {
    font-size: 48px;
    margin-bottom: 16px;
    animation: bounce 2s infinite;
}

@keyframes bounce {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-10px); }
}

.hint-title {
    font-size: 18px;
    font-weight: 600;
    color: var(--sr-text-primary);
    margin-bottom: 12px;
}

.hint-text-large {
    font-size: 14px;
    color: var(--sr-accent-color);
    margin-bottom: 8px;
    font-weight: 500;
}

.hint-text-small {
    font-size: 11px;
    color: var(--sr-text-secondary);
    margin-bottom: 16px;
}

.hint-dismiss {
    font-size: 10px;
    color: var(--sr-text-secondary);
    opacity: 0.6;
    margin-top: 16px;
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
</style>