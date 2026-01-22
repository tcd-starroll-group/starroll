<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { sensorManager, type SensorData } from '@/core/sensors/sensor';

const isSupported = ref(false);
const needsPermission = ref(false);
const permissionState = ref('prompt');
const isListening = ref(false);
const sensorData = ref<SensorData | null>(null);
const cameraOrientation = ref<{ azimuth: number, altitude: number } | null>(null);

// 检查设备支持
onMounted(() => {
    // 直接检查 DeviceOrientationEvent API
    isSupported.value = typeof DeviceOrientationEvent !== 'undefined';
    
    // 检查是否需要权限（iOS 13+）
    needsPermission.value = typeof DeviceOrientationEvent !== 'undefined' && 
        typeof (DeviceOrientationEvent as any).requestPermission === 'function';
    
    permissionState.value = sensorManager.getPermissionState();
    
    console.log('📱 传感器调试面板已加载');
    console.log('设备支持:', isSupported.value);
    console.log('需要权限:', needsPermission.value);
});

// 请求权限
const requestPermission = async () => {
    const result = await sensorManager.requestPermission();
    permissionState.value = result;
};

// 开始测试
const startTest = () => {
    if (permissionState.value === 'denied') {
        alert('传感器权限被拒绝，请在设置中允许');
        return;
    }
    
    // 添加监听器
    sensorManager.addListener(handleSensorUpdate);
    sensorManager.startListening();
    isListening.value = true;
    
    console.log('📡 传感器测试已启动');
};

// 停止测试
const stopTest = () => {
    sensorManager.removeListener(handleSensorUpdate);
    sensorManager.stopListening();
    isListening.value = false;
    
    console.log('🛑 传感器测试已停止');
};

// 处理传感器数据
const handleSensorUpdate = (data: SensorData) => {
    sensorData.value = data;
    
    // 计算相机朝向
    const orientation = sensorManager.getCameraOrientation(data);
    cameraOrientation.value = orientation;
};

// 清理
onUnmounted(() => {
    if (isListening.value) {
        stopTest();
    }
});
</script>

<template>
  <div class="sensor-debug-panel">
    <div class="panel-header">
      <h3>📱 传感器调试面板</h3>
      <button @click="$emit('close')" class="close-btn">✕</button>
    </div>
    
    <div class="panel-content">
      <!-- 设备信息 -->
      <div class="section">
        <div class="section-title">设备信息</div>
        <div class="info-row">
          <span class="label">传感器支持:</span>
          <span class="value" :class="isSupported ? 'success' : 'error'">
            {{ isSupported ? '✅ 支持' : '❌ 不支持' }}
          </span>
        </div>
        <div class="info-row">
          <span class="label">需要权限:</span>
          <span class="value">{{ needsPermission ? '是 (iOS)' : '否' }}</span>
        </div>
        <div class="info-row">
          <span class="label">权限状态:</span>
          <span class="value" :class="{
            'success': permissionState === 'granted' || permissionState === 'not-required',
            'error': permissionState === 'denied'
          }">
            {{ 
              permissionState === 'granted' ? '✅ 已授予' :
              permissionState === 'denied' ? '❌ 已拒绝' :
              permissionState === 'not-required' ? '✅ 无需权限' :
              '⏸️ 待请求'
            }}
          </span>
        </div>
      </div>
      
      <!-- 权限请求 -->
      <div v-if="needsPermission && permissionState === 'prompt'" class="section">
        <button @click="requestPermission" class="primary-btn">
          🔐 请求传感器权限
        </button>
      </div>
      
      <!-- 测试控制 -->
      <div class="section">
        <div class="section-title">测试控制</div>
        <button 
          v-if="!isListening" 
          @click="startTest" 
          class="primary-btn"
          :disabled="!isSupported || permissionState === 'denied'"
        >
          ▶️ 开始测试
        </button>
        <button 
          v-else 
          @click="stopTest" 
          class="danger-btn"
        >
          ⏸️ 停止测试
        </button>
      </div>
      
      <!-- 传感器数据 -->
      <div v-if="sensorData" class="section">
        <div class="section-title">传感器原始数据</div>
        <div class="data-grid">
          <div class="data-item">
            <div class="data-label">Alpha (Z轴)</div>
            <div class="data-value">{{ sensorData.alpha?.toFixed(2) }}°</div>
          </div>
          <div class="data-item">
            <div class="data-label">Beta (X轴)</div>
            <div class="data-value">{{ sensorData.beta?.toFixed(2) }}°</div>
          </div>
          <div class="data-item">
            <div class="data-label">Gamma (Y轴)</div>
            <div class="data-value">{{ sensorData.gamma?.toFixed(2) }}°</div>
          </div>
        </div>
        <div class="info-row">
          <span class="label">绝对方向:</span>
          <span class="value">{{ sensorData.absolute ? '是' : '否' }}</span>
        </div>
      </div>
      
      <!-- 相机朝向 -->
      <div v-if="cameraOrientation" class="section highlight">
        <div class="section-title">⭐ 相机朝向（天文坐标）</div>
        <div class="orientation-display">
          <div class="orientation-item">
            <div class="orientation-icon">🧭</div>
            <div class="orientation-info">
              <div class="orientation-label">方位角</div>
              <div class="orientation-value">{{ cameraOrientation.azimuth.toFixed(1) }}°</div>
              <div class="orientation-dir">{{ getDirectionName(cameraOrientation.azimuth) }}</div>
            </div>
          </div>
          <div class="orientation-item">
            <div class="orientation-icon">📐</div>
            <div class="orientation-info">
              <div class="orientation-label">仰角</div>
              <div class="orientation-value">{{ cameraOrientation.altitude.toFixed(1) }}°</div>
              <div class="orientation-dir">{{ getAltitudeDesc(cameraOrientation.altitude) }}</div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 使用说明 -->
      <div class="section">
        <div class="section-title">📖 使用说明</div>
        <ol class="instructions">
          <li>点击 "请求传感器权限"（仅 iOS）</li>
          <li>点击 "开始测试"</li>
          <li>转动设备，观察数据变化</li>
          <li>方位角 0° = 北，90° = 东</li>
          <li>仰角 0° = 地平线，90° = 天顶</li>
        </ol>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
// 辅助函数
function getDirectionName(azimuth: number): string {
  if (azimuth >= 337.5 || azimuth < 22.5) return '正北 ⬆️';
  if (azimuth >= 22.5 && azimuth < 67.5) return '东北 ↗️';
  if (azimuth >= 67.5 && azimuth < 112.5) return '正东 ➡️';
  if (azimuth >= 112.5 && azimuth < 157.5) return '东南 ↘️';
  if (azimuth >= 157.5 && azimuth < 202.5) return '正南 ⬇️';
  if (azimuth >= 202.5 && azimuth < 247.5) return '西南 ↙️';
  if (azimuth >= 247.5 && azimuth < 292.5) return '正西 ⬅️';
  return '西北 ↖️';
}

function getAltitudeDesc(altitude: number): string {
  if (altitude >= 80) return '接近天顶';
  if (altitude >= 45) return '高空';
  if (altitude >= 20) return '中高度';
  if (altitude >= 5) return '低空';
  if (altitude >= 0) return '接近地平线';
  return '地平线以下';
}

export { getDirectionName, getAltitudeDesc };
</script>

<style scoped>
.sensor-debug-panel {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 90%;
    max-width: 400px;
    max-height: 80vh;
    background: rgba(0, 0, 10, 0.95);
    border: 2px solid rgba(68, 170, 255, 0.5);
    border-radius: 16px;
    backdrop-filter: blur(20px);
    z-index: 1000;
    overflow: hidden;
    box-shadow: 0 0 40px rgba(68, 170, 255, 0.3);
}

.panel-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 20px;
    background: rgba(68, 170, 255, 0.1);
    border-bottom: 1px solid rgba(68, 170, 255, 0.3);
}

.panel-header h3 {
    margin: 0;
    font-size: 16px;
    color: var(--sr-accent-color);
}

.close-btn {
    background: none;
    border: none;
    color: var(--sr-text-secondary);
    font-size: 20px;
    cursor: pointer;
    padding: 4px 8px;
    transition: all 0.2s;
}

.close-btn:hover {
    color: var(--sr-text-primary);
    transform: scale(1.2);
}

.panel-content {
    padding: 20px;
    max-height: calc(80vh - 60px);
    overflow-y: auto;
}

.section {
    margin-bottom: 20px;
    padding-bottom: 16px;
    border-bottom: 1px solid rgba(255,255,255,0.05);
}

.section:last-child {
    border-bottom: none;
}

.section.highlight {
    background: rgba(255, 215, 0, 0.05);
    padding: 16px;
    border-radius: 8px;
    border: 1px solid rgba(255, 215, 0, 0.2);
}

.section-title {
    font-size: 12px;
    color: var(--sr-text-secondary);
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 12px;
    font-weight: 600;
}

.info-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
    font-size: 13px;
}

.info-row .label {
    color: var(--sr-text-secondary);
}

.info-row .value {
    color: var(--sr-text-primary);
    font-weight: 500;
}

.info-row .value.success {
    color: #4CAF50;
}

.info-row .value.error {
    color: #f44336;
}

/* 按钮 */
.primary-btn, .danger-btn {
    width: 100%;
    padding: 12px;
    border: none;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s;
}

.primary-btn {
    background: rgba(68, 170, 255, 0.3);
    color: var(--sr-accent-color);
    border: 1px solid rgba(68, 170, 255, 0.5);
}

.primary-btn:hover:not(:disabled) {
    background: rgba(68, 170, 255, 0.4);
    box-shadow: 0 0 15px rgba(68, 170, 255, 0.5);
}

.primary-btn:disabled {
    opacity: 0.4;
    cursor: not-allowed;
}

.danger-btn {
    background: rgba(244, 67, 54, 0.3);
    color: #f44336;
    border: 1px solid rgba(244, 67, 54, 0.5);
}

.danger-btn:hover {
    background: rgba(244, 67, 54, 0.4);
}

/* 数据展示 */
.data-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
    margin-bottom: 12px;
}

.data-item {
    text-align: center;
    padding: 12px;
    background: rgba(255,255,255,0.03);
    border-radius: 6px;
    border: 1px solid rgba(255,255,255,0.05);
}

.data-label {
    font-size: 9px;
    color: var(--sr-text-secondary);
    margin-bottom: 6px;
    text-transform: uppercase;
}

.data-value {
    font-size: 16px;
    color: var(--sr-accent-color);
    font-weight: 600;
    font-family: 'Courier New', monospace;
}

/* 相机朝向显示 */
.orientation-display {
    display: flex;
    gap: 12px;
}

.orientation-item {
    flex: 1;
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px;
    background: rgba(255, 215, 0, 0.05);
    border-radius: 8px;
    border: 1px solid rgba(255, 215, 0, 0.2);
}

.orientation-icon {
    font-size: 24px;
}

.orientation-info {
    flex: 1;
}

.orientation-label {
    font-size: 10px;
    color: var(--sr-text-secondary);
    margin-bottom: 4px;
}

.orientation-value {
    font-size: 18px;
    color: #FFD700;
    font-weight: 700;
    font-family: 'Courier New', monospace;
}

.orientation-dir {
    font-size: 11px;
    color: var(--sr-text-secondary);
    margin-top: 2px;
}

/* 说明列表 */
.instructions {
    font-size: 12px;
    color: var(--sr-text-secondary);
    line-height: 1.8;
    padding-left: 20px;
}

.instructions li {
    margin-bottom: 6px;
}
</style>
