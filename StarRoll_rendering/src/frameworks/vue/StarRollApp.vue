<script setup lang="ts">
import { onMounted, ref } from 'vue';
// 使用地面观测者模式（为 AR 准备）
import { useGroundObserver } from './composables/useGroundObserver';
import TopBar from './components/TopBar.vue';
import InfoPanel from './components/InfoPanel.vue';
import SensorDebugPanel from './components/SensorDebugPanel.vue';
import StarInfoPanel from './components/StarInfoPanel.vue';
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
    isRequestingLocation
} = useGroundObserver();

// 检测是否为移动设备
const isMobile = /Android|iPhone|iPad/i.test(navigator.userAgent);
const isIOS = /iPhone|iPad|iPod/i.test(navigator.userAgent);

onMounted(async () => {
    if (containerRef.value) {
        console.log('🌍 启动地面观测者模式');
        console.log('📐 视角: 地球表面观测者');
        console.log('🧭 坐标系: 地平坐标系');
        console.log('📱 为 AR 渲染准备');
        
        init(containerRef.value);
        
        // 延迟获取统计信息
        setTimeout(() => {
            refreshStats();
            console.log('📊 观测统计:', stats.value);
            console.log(`✨ 可见恒星: ${stats.value.visibleStars} 颗`);
            console.log(`🎭 可见星座: ${stats.value.visibleConstellations} 个`);
            console.log(`📍 观测地点: ${stats.value.observerLocation}`);
            console.log(`🕐 本地恒星时: ${stats.value.localSiderealTime}°`);
            console.log('');
            console.log('💡 提示: 拖动鼠标环顾天空');
            console.log('📱 提示: 在移动设备上会自动跟随设备方向');
        }, 3500);
        
        // 启动后自动尝试获取位置
        setTimeout(async () => {
            console.log('🌍 自动尝试获取当前位置...');
            const success = await useCurrentLocationAndTime();
            if (success) {
                console.log('✅ 已自动更新到当前位置');
                showLocationHint.value = false;
            } else {
                console.log('💡 使用默认位置（上海），可点击"使用当前位置"按钮更新');
            }
        }, 2000);
    }
});

// 点击反馈状态
const isRequesting = ref(false);

// 位置请求提示
const showLocationHint = ref(true);

// 测试按钮点击
const testButtonClick = () => {
    console.log('✅ 测试按钮被点击！');
    console.log('📱 设备类型:', isMobile ? '移动设备' : '桌面');
    console.log('🍎 是否 iOS:', isIOS);
    console.log('🌐 User Agent:', navigator.userAgent);
    
    // 触觉反馈
    if (navigator.vibrate) {
        navigator.vibrate([50, 100, 50]);
        console.log('📳 触觉反馈已触发');
    } else {
        console.log('📳 设备不支持触觉反馈');
    }
    
    alert(`✅ 按钮点击测试成功！

设备信息：
- 类型: ${isMobile ? '移动设备' : '桌面'}
- iOS: ${isIOS ? '是' : '否'}
- 传感器支持: ${typeof DeviceOrientationEvent !== 'undefined' ? '是' : '否'}

如果能看到这个对话框，说明按钮事件正常工作！

下一步：点击上方 "启用 AR" 按钮测试权限请求。`);
};

// 请求使用当前位置和时间
const handleUseCurrentLocation = async () => {
    console.log('📍 点击使用当前位置');
    
    // 触觉反馈
    if (navigator.vibrate) {
        navigator.vibrate(50);
    }
    
    try {
        const success = await useCurrentLocationAndTime();
        
        if (success) {
            console.log('✅ 已使用当前位置和时间');
            showLocationHint.value = false;
            
            // 提示用户
            alert(`✅ 位置获取成功！

当前位置: ${currentLocation.value.name}
纬度: ${currentLocation.value.latitude.toFixed(4)}°
经度: ${currentLocation.value.longitude.toFixed(4)}°

星空已更新为您当前位置的天空！`);
        } else {
            console.error('❌ 位置获取失败');
            
            alert(`⚠️ 位置获取失败

可能原因：
1. 您拒绝了位置权限
2. 设备不支持地理位置API
3. 位置服务未开启

解决方法：
1. 在浏览器设置中允许位置权限
2. 确保设备GPS已开启
3. 刷新页面重试`);
        }
    } catch (error) {
        console.error('❌ 获取位置时发生错误:', error);
        alert('发生错误：' + error);
    }
};

// 获取方向标签
const getDirectionLabel = (azimuth: number): string => {
    const directions = ['北', '东北', '东', '东南', '南', '西南', '西', '西北'];
    const index = Math.round(azimuth / 45) % 8;
    return directions[index];
};

// 切换 AR 模式
const toggleARMode = async () => {
    console.log('🔘 AR 按钮被点击');
    
    // 触觉反馈（如果支持）
    if (navigator.vibrate) {
        navigator.vibrate(50);
    }
    
    if (arModeEnabled.value) {
        disableARMode();
        console.log('🛑 AR 模式已禁用');
        return;
    }
    
    // 显示请求中状态
    isRequesting.value = true;
    
    try {
        console.log('📱 正在请求传感器权限...');
        console.log('⏳ 等待用户响应 iOS 权限对话框...');
        
        const success = await enableARMode();
        
        if (success) {
            console.log('✅ AR 模式已启用');
            console.log('📱 现在转动您的设备，星空会跟随移动');
            showWelcomeHint.value = false;
        } else {
            console.error('❌ AR 模式启用失败');
            
            if (isIOS) {
                alert(`⚠️ iOS 权限请求失败

可能原因：
1. 您拒绝了权限
2. 需要使用 HTTPS 连接
3. Safari 浏览器设置问题

解决方法：
1. 使用 Safari 浏览器（不是 Chrome）
2. 使用 ngrok 创建 HTTPS 隧道
3. 刷新页面重试
4. 检查 Safari 设置 → 隐私 → 动作与方向

是否需要使用 HTTPS？请在控制台查看详细信息。`);
            } else {
                alert('⚠️ 无法启用 AR 模式\n\n请检查设备是否支持方向传感器');
            }
        }
    } catch (error) {
        console.error('❌ 启用 AR 时发生错误:', error);
        alert('发生错误：' + error);
    } finally {
        isRequesting.value = false;
    }
};
</script>

<template>
  <div class="starroll-app">
    <!-- 3D Canvas Container -->
    <div ref="containerRef" class="canvas-container"></div>
    
    <!-- UI Overlay -->
    <div class="ui-layer">
        <!-- AR模式下只显示最简洁的UI -->
        <TopBar v-if="!arModeEnabled" />
        <InfoPanel v-if="!arModeEnabled" />
        
        <!-- 观测者信息（AR模式下隐藏） -->
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
            {{ isRequestingLocation ? '⏳ 获取中...' : '📍 使用当前位置' }}
          </button>
          <button @click="showDebugPanel = true" class="debug-btn">
            🔧 传感器调试
          </button>
        </div>
        
        <!-- iOS 欢迎提示（首次访问） -->
        <div v-if="showWelcomeHint && isMobile" class="welcome-hint" @click="showWelcomeHint = false">
          <div class="hint-content">
            <div class="hint-icon">📱</div>
            <div class="hint-title">欢迎使用 AR 星空</div>
            <div class="hint-text-large">
              {{ isIOS ? '👇 点击下方 "启用 AR 模式" 按钮' : '👇 点击下方按钮启用 AR' }}
            </div>
            <div class="hint-text-small" v-if="isIOS">
              iOS 需要您手动授予传感器权限
            </div>
            <div class="hint-dismiss">点击任意处关闭提示</div>
          </div>
        </div>
        
        <!-- AR 控制面板 -->
        <div class="ar-panel" :class="{ 'highlight': showWelcomeHint && isMobile }">
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
                isRequesting ? '请求权限中...' :
                arModeEnabled ? 'AR 模式已启用' : 
                (isIOS ? '点击启用 AR (iOS)' : '启用 AR 模式') 
              }}
            </span>
          </button>
          
          <!-- 点击测试按钮 -->
          <button @click="testButtonClick" class="test-button" v-if="!arModeEnabled">
            🔍 测试按钮点击
          </button>
          <div class="hint-text">{{ arModeEnabled ? '转动设备环顾星空' : '点击按钮获取传感器权限' }}</div>
          
          <!-- AR模式下默认隐藏控制，保持画面简洁 -->
          <div class="display-controls" v-if="!arModeEnabled">
            <div class="control-item">
              <span class="control-label">星座连线</span>
              <label class="toggle-switch">
                <input type="checkbox" :checked="showConstellationLines" @change="toggleConstellationLines">
                <span class="slider"></span>
              </label>
            </div>
            <div class="control-item">
              <span class="control-label">星星标签</span>
              <label class="toggle-switch">
                <input type="checkbox" :checked="showStarLabels" @change="toggleStarLabels">
                <span class="slider"></span>
              </label>
            </div>
          </div>
          
          <!-- 简洁的方向指示（AR模式） -->
          <div v-if="arModeEnabled" class="ar-compass">
            <div class="compass-value">{{ Math.round(cameraOrientation.azimuth) }}°</div>
            <div class="compass-label">{{ getDirectionLabel(cameraOrientation.azimuth) }}</div>
          </div>
        </div>
        
        <!-- Bottom Horizon Line -->
        <div class="horizon-line">
          <div class="horizon-label">地平线</div>
        </div>
        
        <!-- 传感器调试面板 -->
        <SensorDebugPanel 
          v-if="showDebugPanel" 
          @close="showDebugPanel = false"
        />
        
        <!-- 星星信息面板 -->
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

/* 观测者信息 */
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

/* 欢迎提示 */
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

/* AR 控制面板 */
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

/* 测试按钮 */
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

/* 调试信息 */
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

/* 显示控制 */
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

/* 地平线 */
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

/* AR罗盘指示 */
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
</style>

