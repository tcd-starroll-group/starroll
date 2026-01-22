<script setup lang="ts">
import { ref, onUnmounted } from 'vue'
import { sensorManager, SensorManager, type SensorData, type CameraOrientation } from '../utils/sensor'

// 状态管理
const permissionState = ref<string>('未请求')
const isListening = ref(false)
const sensorData = ref<SensorData | null>(null)
const cameraOrientation = ref<CameraOrientation | null>(null)
const error = ref<string>('')

// 用户点击按钮请求权限
// ⚠️ 这是iOS 13+的关键要求：必须由用户手势触发
async function handleRequestPermission() {
  error.value = ''
  
  try {
    const result = await sensorManager.requestPermission()
    
    switch (result) {
      case 'granted':
        permissionState.value = '✅ 已授权'
        // 权限获取后自动开始监听
        startListening()
        break
      case 'denied':
        permissionState.value = '❌ 已拒绝'
        error.value = '传感器权限被拒绝。请在设置中允许访问动作与方向。'
        break
      case 'not-required':
        permissionState.value = '✅ 无需权限'
        // Android设备直接开始监听
        startListening()
        break
      default:
        permissionState.value = '❓ 未知状态'
    }
  } catch (err) {
    error.value = `请求权限失败: ${err}`
    console.error(err)
  }
}

// 开始监听传感器
function startListening() {
  try {
    // 添加数据监听器
    sensorManager.addListener(handleSensorData)
    
    // 开始监听
    sensorManager.startListening()
    isListening.value = true
    
  } catch (err) {
    error.value = `启动监听失败: ${err}`
    console.error(err)
  }
}

// 停止监听传感器
function stopListening() {
  sensorManager.removeListener(handleSensorData)
  sensorManager.stopListening()
  isListening.value = false
}

// 处理传感器数据回调
function handleSensorData(data: SensorData) {
  sensorData.value = data
  
  // 计算相机朝向
  const orientation = sensorManager.getCameraOrientation(data)
  cameraOrientation.value = orientation
}

// 组件卸载时清理
onUnmounted(() => {
  if (isListening.value) {
    stopListening()
  }
})

// 检测设备信息
const deviceInfo = ref({
  isSupported: SensorManager.isSupported(),
  needsPermission: SensorManager.needsPermission(),
  userAgent: navigator.userAgent,
  isIOS: /iPhone|iPad|iPod/.test(navigator.userAgent),
  isAndroid: /Android/.test(navigator.userAgent),
  isHTTPS: window.location.protocol === 'https:'
})

// 辅助函数：根据方位角获取方向
function getCompassDirection(azimuth: number): string {
  const directions: string[] = [
    '正北 N', '东北偏北 NNE', '东北 NE', '东北偏东 ENE',
    '正东 E', '东南偏东 ESE', '东南 SE', '东南偏南 SSE',
    '正南 S', '西南偏南 SSW', '西南 SW', '西南偏西 WSW',
    '正西 W', '西北偏西 WNW', '西北 NW', '西北偏北 NNW'
  ]
  
  const index = Math.round(azimuth / 22.5) % 16
  return directions[index] ?? '正北 N'
}
</script>

<template>
  <div class="sensor-container">
    <h1>📱 手机传感器读取</h1>

    <!-- 设备信息 -->
    <div class="info-section">
      <h2>设备信息</h2>
      <div class="info-grid">
        <div class="info-item">
          <span class="label">传感器支持:</span>
          <span :class="{ 'status-ok': deviceInfo.isSupported, 'status-error': !deviceInfo.isSupported }">
            {{ deviceInfo.isSupported ? '✅ 支持' : '❌ 不支持' }}
          </span>
        </div>
        <div class="info-item">
          <span class="label">需要权限:</span>
          <span>{{ deviceInfo.needsPermission ? '是 (iOS 13+)' : '否 (Android)' }}</span>
        </div>
        <div class="info-item">
          <span class="label">设备类型:</span>
          <span>
            {{ deviceInfo.isIOS ? 'iOS' : deviceInfo.isAndroid ? 'Android' : '其他' }}
          </span>
        </div>
        <div class="info-item">
          <span class="label">HTTPS连接:</span>
          <span :class="{ 'status-ok': deviceInfo.isHTTPS, 'status-warning': !deviceInfo.isHTTPS }">
            {{ deviceInfo.isHTTPS ? '✅ 是' : '⚠️ 否' }}
          </span>
        </div>
      </div>
    </div>

    <!-- 权限状态 -->
    <div class="status-section">
      <h2>权限状态</h2>
      <div class="status-box">
        <p class="status-text">{{ permissionState }}</p>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="actions">
      <button 
        v-if="!isListening"
        @click="handleRequestPermission" 
        class="btn-primary btn-large"
        :disabled="!deviceInfo.isSupported"
      >
        🎯 授予权限并开始读取
      </button>

      <button 
        v-if="isListening"
        @click="stopListening" 
        class="btn-danger btn-large"
      >
        🛑 停止读取
      </button>

      <router-link to="/diagnostic" class="btn-secondary">
        🔍 运行诊断工具
      </router-link>
    </div>

    <!-- 错误信息 -->
    <div v-if="error" class="error-box">
      <h3>⚠️ 错误</h3>
      <p>{{ error }}</p>
    </div>

    <!-- 传感器数据显示 -->
    <div v-if="isListening" class="data-section">
      <h2>📡 实时传感器数据</h2>
      
      <div v-if="sensorData" class="data-grid">
        <!-- 原始传感器数据 -->
        <div class="data-card">
          <h3>原始方向数据</h3>
          <div class="data-item">
            <span class="data-label">Alpha (Z轴):</span>
            <span class="data-value">{{ sensorData.alpha?.toFixed(2) ?? 'null' }}°</span>
          </div>
          <div class="data-item">
            <span class="data-label">Beta (X轴):</span>
            <span class="data-value">{{ sensorData.beta?.toFixed(2) ?? 'null' }}°</span>
          </div>
          <div class="data-item">
            <span class="data-label">Gamma (Y轴):</span>
            <span class="data-value">{{ sensorData.gamma?.toFixed(2) ?? 'null' }}°</span>
          </div>
          <div class="data-item">
            <span class="data-label">绝对方向:</span>
            <span class="data-value">{{ sensorData.absolute ? '是' : '否' }}</span>
          </div>
        </div>

        <!-- 相机朝向数据 -->
        <div v-if="cameraOrientation" class="data-card camera-card">
          <h3>📷 相机朝向</h3>
          <div class="data-item">
            <span class="data-label">方位角 (Azimuth):</span>
            <span class="data-value highlight">{{ cameraOrientation.azimuth.toFixed(2) }}°</span>
          </div>
          <div class="data-item">
            <span class="data-label">仰角 (Altitude):</span>
            <span class="data-value highlight">{{ cameraOrientation.altitude.toFixed(2) }}°</span>
          </div>
          <div class="compass">
            <div class="compass-direction">
              {{ getCompassDirection(cameraOrientation.azimuth) }}
            </div>
          </div>
        </div>
      </div>

      <div v-else class="waiting-data">
        <p>等待传感器数据...</p>
        <p class="hint">请移动您的设备以触发传感器</p>
      </div>
    </div>

    <!-- 使用说明 -->
    <div class="instructions">
      <h2>📚 使用说明</h2>
      
      <div class="instruction-box">
        <h3>iOS设备（iPhone/iPad）:</h3>
        <ol>
          <li>必须使用Safari浏览器</li>
          <li>确保使用HTTPS连接（推荐使用ngrok）</li>
          <li>点击"授予权限并开始读取"按钮</li>
          <li>在弹出的对话框中选择"允许"</li>
          <li>如果没有弹出对话框，请检查设置 → Safari → 动作与方向访问</li>
        </ol>
      </div>

      <div class="instruction-box">
        <h3>Android设备:</h3>
        <ol>
          <li>使用Chrome或Firefox浏览器</li>
          <li>建议使用HTTPS连接</li>
          <li>点击"授予权限并开始读取"按钮</li>
          <li>无需额外权限，应该直接开始工作</li>
        </ol>
      </div>

      <div class="instruction-box">
        <h3>使用ngrok获取HTTPS连接:</h3>
        <ol>
          <li>在开发机器上运行: <code>npm run dev</code></li>
          <li>记录本地端口号（通常是5173）</li>
          <li>运行: <code>ngrok http 5173</code></li>
          <li>复制ngrok提供的HTTPS地址（如 https://xxxx.ngrok.io）</li>
          <li>在手机上访问该HTTPS地址</li>
        </ol>
      </div>
    </div>
  </div>
</template>

<style scoped>
.sensor-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

h1 {
  text-align: center;
  color: #2c3e50;
  margin-bottom: 30px;
  font-size: 32px;
}

h2 {
  color: #34495e;
  border-bottom: 2px solid #3498db;
  padding-bottom: 10px;
  margin: 30px 0 20px 0;
}

h3 {
  color: #555;
  margin-top: 0;
  font-size: 18px;
}

/* 信息区域 */
.info-section {
  background-color: #f8f9fa;
  padding: 20px;
  border-radius: 10px;
  margin-bottom: 20px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  background-color: white;
  border-radius: 5px;
}

.label {
  font-weight: 600;
  color: #555;
}

.status-ok {
  color: #28a745;
  font-weight: 600;
}

.status-error {
  color: #dc3545;
  font-weight: 600;
}

.status-warning {
  color: #ffc107;
  font-weight: 600;
}

/* 状态区域 */
.status-section {
  margin-bottom: 20px;
}

.status-box {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  border-radius: 10px;
  text-align: center;
}

.status-text {
  color: white;
  font-size: 24px;
  font-weight: 600;
  margin: 0;
}

/* 操作按钮 */
.actions {
  display: flex;
  gap: 15px;
  justify-content: center;
  margin: 30px 0;
  flex-wrap: wrap;
}

.btn-large {
  font-size: 18px;
  padding: 15px 40px;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 12px 30px;
  font-size: 16px;
  border-radius: 8px;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  text-decoration: none;
  display: inline-block;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}

.btn-primary:disabled {
  background: #95a5a6;
  cursor: not-allowed;
  transform: none;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
  border: none;
  padding: 12px 30px;
  font-size: 16px;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.3s;
  text-decoration: none;
  display: inline-block;
}

.btn-secondary:hover {
  background-color: #5a6268;
}

.btn-danger {
  background-color: #dc3545;
  color: white;
  border: none;
  padding: 12px 30px;
  font-size: 16px;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.btn-danger:hover {
  background-color: #c82333;
}

/* 错误信息 */
.error-box {
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  color: #721c24;
  padding: 20px;
  border-radius: 8px;
  margin: 20px 0;
}

.error-box h3 {
  margin-top: 0;
  color: #721c24;
}

/* 数据显示 */
.data-section {
  margin-top: 30px;
}

.data-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.data-card {
  background: white;
  border: 2px solid #e0e0e0;
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.camera-card {
  border-color: #667eea;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.data-item {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
}

.data-item:last-child {
  border-bottom: none;
}

.data-label {
  font-weight: 600;
  color: #555;
}

.data-value {
  font-family: 'Courier New', monospace;
  font-size: 18px;
  color: #2c3e50;
}

.data-value.highlight {
  color: #667eea;
  font-weight: 700;
  font-size: 22px;
}

.compass {
  margin-top: 20px;
  text-align: center;
}

.compass-direction {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-size: 24px;
  font-weight: 700;
  padding: 15px;
  border-radius: 50px;
  display: inline-block;
  min-width: 100px;
}

.waiting-data {
  text-align: center;
  padding: 40px;
  background-color: #f8f9fa;
  border-radius: 10px;
  margin-top: 20px;
}

.waiting-data p {
  font-size: 18px;
  color: #666;
  margin: 10px 0;
}

.hint {
  font-size: 14px !important;
  color: #999 !important;
}

/* 使用说明 */
.instructions {
  margin-top: 40px;
}

.instruction-box {
  background-color: #e8f4f8;
  border-left: 4px solid #3498db;
  padding: 20px;
  border-radius: 5px;
  margin-bottom: 20px;
}

.instruction-box h3 {
  color: #2c3e50;
  margin-top: 0;
}

.instruction-box ol {
  margin: 10px 0 0 20px;
  padding: 0;
}

.instruction-box li {
  margin-bottom: 10px;
  color: #555;
  line-height: 1.6;
}

.instruction-box code {
  background-color: #fff;
  padding: 2px 8px;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
  color: #e83e8c;
  font-size: 14px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .sensor-container {
    padding: 10px;
  }

  h1 {
    font-size: 24px;
  }

  .actions {
    flex-direction: column;
  }

  .btn-primary,
  .btn-secondary,
  .btn-danger {
    width: 100%;
  }

  .data-grid {
    grid-template-columns: 1fr;
  }

  .info-grid {
    grid-template-columns: 1fr;
  }
}
</style>

