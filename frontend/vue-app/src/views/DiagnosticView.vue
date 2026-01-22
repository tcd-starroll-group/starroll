<script setup lang="ts">
import { ref, onMounted } from 'vue'

const isRunning = ref(false)

interface DiagnosticItem {
  title: string
  status: 'checking' | 'success' | 'warning' | 'error'
  message: string
  details?: string
}

const tests = ref<DiagnosticItem[]>([])

onMounted(() => {
  runDiagnostics()
})

async function runDiagnostics() {
  isRunning.value = true
  tests.value = []

  // 1. 检测设备类型
  await addTest({
    title: '1️⃣ 设备类型检测',
    check: () => {
      const ua = navigator.userAgent
      const isMobile = /iPhone|iPad|iPod|Android|Mobile/.test(ua)
      const isIOS = /iPhone|iPad|iPod/.test(ua)
      const isAndroid = /Android/.test(ua)
      
      if (!isMobile) {
        return {
          status: 'error',
          message: '❌ 这是桌面设备，传感器不可用',
          details: '请在移动设备（iPhone、iPad或Android手机）上打开此页面'
        }
      }
      
      if (isIOS) {
        return {
          status: 'success',
          message: '✅ iOS设备',
          details: 'iPhone/iPad检测成功'
        }
      }
      
      if (isAndroid) {
        return {
          status: 'success',
          message: '✅ Android设备',
          details: 'Android手机检测成功'
        }
      }
      
      return {
        status: 'warning',
        message: '⚠️ 未知移动设备',
        details: ua
      }
    }
  })

  // 2. 检测浏览器
  await addTest({
    title: '2️⃣ 浏览器检测',
    check: () => {
      const ua = navigator.userAgent
      const isIOS = /iPhone|iPad|iPod/.test(ua)
      const isSafari = /Safari/.test(ua) && !/Chrome|CriOS|FxiOS/.test(ua)
      const isChrome = /Chrome|CriOS/.test(ua)
      const isFirefox = /Firefox|FxiOS/.test(ua)
      
      if (isIOS && !isSafari) {
        return {
          status: 'error',
          message: '❌ iOS必须使用Safari浏览器',
          details: '检测到非Safari浏览器，传感器可能不工作。请在Safari中打开此页面。'
        }
      }
      
      if (isIOS && isSafari) {
        return {
          status: 'success',
          message: '✅ Safari浏览器（正确）',
          details: 'iOS设备正在使用Safari浏览器'
        }
      }
      
      if (isChrome || isFirefox) {
        return {
          status: 'success',
          message: '✅ 现代浏览器',
          details: 'Android设备浏览器正常'
        }
      }
      
      return {
        status: 'warning',
        message: '⚠️ 未知浏览器',
        details: ua
      }
    }
  })

  // 3. 检测HTTPS
  await addTest({
    title: '3️⃣ HTTPS连接检测',
    check: () => {
      const isHTTPS = window.location.protocol === 'https:'
      const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
      
      if (isHTTPS) {
        return {
          status: 'success',
          message: '✅ 正在使用HTTPS',
          details: `当前地址: ${window.location.href}`
        }
      }
      
      if (isLocalhost) {
        return {
          status: 'warning',
          message: '⚠️ localhost不需要HTTPS',
          details: '本地开发环境，但在iOS设备上可能需要HTTPS'
        }
      }
      
      return {
        status: 'warning',
        message: '⚠️ 未使用HTTPS',
        details: `当前地址: ${window.location.href}\n建议使用ngrok获取HTTPS连接`
      }
    }
  })

  // 4. 检测DeviceOrientationEvent
  await addTest({
    title: '4️⃣ DeviceOrientation API支持',
    check: () => {
      if (!('DeviceOrientationEvent' in window)) {
        return {
          status: 'error',
          message: '❌ 不支持DeviceOrientationEvent',
          details: '浏览器不支持设备方向API'
        }
      }
      
      return {
        status: 'success',
        message: '✅ 支持DeviceOrientationEvent',
        details: 'DeviceOrientationEvent API可用'
      }
    }
  })

  // 5. 检测权限API
  await addTest({
    title: '5️⃣ 权限API检测',
    check: () => {
      const hasPermissionAPI = typeof (DeviceOrientationEvent as unknown as { requestPermission?: () => Promise<string> }).requestPermission === 'function'
      
      if (hasPermissionAPI) {
        return {
          status: 'success',
          message: '✅ 需要请求权限（iOS 13+）',
          details: '检测到权限API，需要用户授权'
        }
      }
      
      return {
        status: 'success',
        message: '✅ 无需请求权限',
        details: 'Android设备或旧版iOS，可直接使用传感器'
      }
    }
  })

  // 6. 检测DeviceMotionEvent
  await addTest({
    title: '6️⃣ DeviceMotion API支持（备用）',
    check: () => {
      if (!('DeviceMotionEvent' in window)) {
        return {
          status: 'warning',
          message: '⚠️ 不支持DeviceMotionEvent',
          details: '备用传感器不可用，但不影响主要功能'
        }
      }
      
      return {
        status: 'success',
        message: '✅ 支持DeviceMotionEvent',
        details: '备用传感器API可用'
      }
    }
  })

  // 7. 测试实际传感器数据
  await addTest({
    title: '7️⃣ 传感器数据测试',
    check: () => {
      return new Promise((resolve) => {
        let eventReceived = false
        let eventData: { alpha: number | null; beta: number | null; gamma: number | null } | null = null
        
        const handler = (event: DeviceOrientationEvent) => {
          eventReceived = true
          eventData = {
            alpha: event.alpha,
            beta: event.beta,
            gamma: event.gamma
          }
        }
        
        window.addEventListener('deviceorientation', handler, true)
        
        setTimeout(() => {
          window.removeEventListener('deviceorientation', handler, true)
          
          if (!eventReceived || !eventData) {
            resolve({
              status: 'warning',
              message: '⚠️ 未收到传感器事件',
              details: '2秒内未收到事件。可能需要授权或传感器被禁用。'
            })
          } else if (eventData.alpha === null && eventData.beta === null && eventData.gamma === null) {
            resolve({
              status: 'warning',
              message: '⚠️ 收到空数据',
              details: '传感器返回null值，可能未授权或传感器未就绪'
            })
          } else {
            resolve({
              status: 'success',
              message: '✅ 传感器数据正常',
              details: `alpha: ${eventData.alpha?.toFixed(2) ?? 'null'}, beta: ${eventData.beta?.toFixed(2) ?? 'null'}, gamma: ${eventData.gamma?.toFixed(2) ?? 'null'}`
            })
          }
        }, 2000)
      })
    }
  })

  isRunning.value = false
}

interface TestResult {
  status: 'checking' | 'success' | 'warning' | 'error'
  message: string
  details?: string
}

async function addTest(test: { title: string; check: () => TestResult | Promise<TestResult> }) {
  const item: DiagnosticItem = {
    title: test.title,
    status: 'checking',
    message: '检测中...',
  }
  
  tests.value.push(item)
  
  await new Promise(resolve => setTimeout(resolve, 200))
  
  try {
    const result = await test.check()
    item.status = result.status
    item.message = result.message
    item.details = result.details
  } catch (error) {
    item.status = 'error'
    item.message = '❌ 检测失败'
    item.details = String(error)
  }
}

function getStatusColor(status: string) {
  switch (status) {
    case 'success': return '#28a745'
    case 'warning': return '#ffc107'
    case 'error': return '#dc3545'
    default: return '#6c757d'
  }
}

function getStatusIcon(status: string) {
  switch (status) {
    case 'checking': return '🔄'
    case 'success': return '✅'
    case 'warning': return '⚠️'
    case 'error': return '❌'
    default: return '❓'
  }
}

function copyResults() {
  const text = tests.value.map(t => 
    `${t.title}\n${t.message}\n${t.details || ''}\n`
  ).join('\n')
  
  navigator.clipboard.writeText(text).then(() => {
    alert('诊断结果已复制到剪贴板！')
  }).catch(() => {
    console.log(text)
    alert('复制失败，请查看控制台')
  })
}
</script>

<template>
  <div class="diagnostic-container">
    <h1>🔍 传感器诊断工具</h1>
    
    <div class="description">
      <p>此工具将自动检测您的设备和浏览器配置，帮助诊断传感器权限问题。</p>
    </div>

    <div class="actions">
      <button @click="runDiagnostics" :disabled="isRunning" class="btn-primary">
        🔄 重新诊断
      </button>
      <button @click="copyResults" class="btn-secondary">
        📋 复制结果
      </button>
    </div>

    <div class="tests-container">
      <div 
        v-for="(test, index) in tests" 
        :key="index"
        class="test-item"
        :class="test.status"
      >
        <div class="test-header">
          <span class="test-icon">{{ getStatusIcon(test.status) }}</span>
          <h3>{{ test.title }}</h3>
        </div>
        <div class="test-message" :style="{ color: getStatusColor(test.status) }">
          {{ test.message }}
        </div>
        <div v-if="test.details" class="test-details">
          {{ test.details }}
        </div>
      </div>
    </div>

    <div class="recommendations">
      <h2>💡 根据诊断结果的建议</h2>
      
      <div class="recommendation-box">
        <h3>如果看到错误（❌）：</h3>
        <ul>
          <li>设备类型错误 → 请在移动设备上打开此页面</li>
          <li>浏览器错误 → iOS请使用Safari，Android请使用Chrome</li>
          <li>API不支持 → 浏览器版本太旧，请更新</li>
        </ul>
      </div>

      <div class="recommendation-box">
        <h3>如果看到警告（⚠️）：</h3>
        <ul>
          <li>未使用HTTPS → 使用ngrok获取HTTPS连接</li>
          <li>未收到传感器事件 → 需要授权或检查系统设置</li>
          <li>收到空数据 → 检查iOS设置中的"动作与方向访问"</li>
        </ul>
      </div>

      <div class="recommendation-box success-box">
        <h3>如果全部是✅：</h3>
        <p>
          恭喜！您的设备和浏览器配置正确。<br>
          请返回主页面点击"授予权限"按钮。
        </p>
        <router-link to="/" class="btn-primary">返回主页面</router-link>
      </div>
    </div>

    <div class="help-section">
      <h2>📚 详细帮助文档</h2>
      <p>请查看项目中的 <code>权限诊断指南.md</code> 文件获取完整的故障排查步骤。</p>
    </div>
  </div>
</template>

<style scoped>
.diagnostic-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

h1 {
  text-align: center;
  color: #2c3e50;
  margin-bottom: 20px;
}

h2 {
  color: #34495e;
  border-bottom: 2px solid #3498db;
  padding-bottom: 10px;
  margin: 30px 0 20px 0;
}

.description {
  background-color: #e8f4f8;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
  border-left: 4px solid #3498db;
}

.description p {
  margin: 0;
  color: #555;
}

.actions {
  display: flex;
  gap: 10px;
  justify-content: center;
  margin-bottom: 30px;
  flex-wrap: wrap;
}

.btn-primary {
  background-color: #3498db;
  color: white;
  border: none;
  padding: 12px 30px;
  font-size: 16px;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s;
  text-decoration: none;
  display: inline-block;
}

.btn-primary:hover:not(:disabled) {
  background-color: #2980b9;
}

.btn-primary:disabled {
  background-color: #95a5a6;
  cursor: not-allowed;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
  border: none;
  padding: 12px 30px;
  font-size: 16px;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.btn-secondary:hover {
  background-color: #5a6268;
}

.tests-container {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.test-item {
  background-color: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s;
}

.test-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.test-item.success {
  border-left: 4px solid #28a745;
}

.test-item.warning {
  border-left: 4px solid #ffc107;
}

.test-item.error {
  border-left: 4px solid #dc3545;
}

.test-item.checking {
  border-left: 4px solid #6c757d;
}

.test-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.test-icon {
  font-size: 24px;
}

.test-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 18px;
}

.test-message {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 8px;
}

.test-details {
  font-size: 14px;
  color: #666;
  background-color: #fff;
  padding: 10px;
  border-radius: 5px;
  font-family: 'Courier New', monospace;
  white-space: pre-wrap;
  word-break: break-word;
}

.recommendations {
  margin-top: 40px;
}

.recommendation-box {
  background-color: #fff3cd;
  border: 1px solid #ffc107;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 15px;
}

.recommendation-box.success-box {
  background-color: #d4edda;
  border-color: #28a745;
}

.recommendation-box h3 {
  margin-top: 0;
  color: #856404;
  font-size: 16px;
}

.recommendation-box.success-box h3 {
  color: #155724;
}

.recommendation-box ul {
  margin: 10px 0 0 0;
  padding-left: 20px;
}

.recommendation-box li {
  margin-bottom: 8px;
  color: #555;
}

.recommendation-box p {
  margin: 10px 0;
  color: #155724;
}

.help-section {
  background-color: #e8f4f8;
  border-radius: 8px;
  padding: 20px;
  margin-top: 30px;
  border-left: 4px solid #3498db;
}

.help-section p {
  margin: 0;
  color: #555;
}

.help-section code {
  background-color: #fff;
  padding: 2px 8px;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
  color: #e83e8c;
}

@media (max-width: 600px) {
  .diagnostic-container {
    padding: 10px;
  }

  .actions {
    flex-direction: column;
  }

  .btn-primary,
  .btn-secondary {
    width: 100%;
  }

  .test-header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>

