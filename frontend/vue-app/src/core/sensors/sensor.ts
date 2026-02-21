/**
 * 传感器数据管理模块
 * 用于读取iOS和Android设备的陀螺仪和方向传感器数据
 * 包含横竖屏自动适配逻辑
 */

export interface SensorData {
  alpha: number | null  // Z轴旋转角度 (0-360度)
  beta: number | null   // X轴旋转角度 (-180到180度)
  gamma: number | null  // Y轴旋转角度 (-90到90度)
  webkitCompassHeading?: number | null // iOS 专用真实指南针方向
  screenOrientation: number // [新增] 屏幕旋转角度
  absolute: boolean     // 是否为绝对方向
  timestamp: number     // 时间戳
}

export interface CameraOrientation {
  azimuth: number    // 方位角 (0-360度，正北为0)
  altitude: number   // 仰角 (-90到90度)
}

export type SensorCallback = (data: SensorData) => void
export type PermissionState = 'granted' | 'denied' | 'prompt' | 'not-required'

/**
 * 获取当前屏幕旋转角度
 * 兼容性处理：优先使用 screen.orientation, 降级使用 window.orientation
 */
function getScreenOrientation(): number {
  // 1. 现代浏览器标准 API
  if (window.screen && window.screen.orientation && window.screen.orientation.angle !== undefined) {
    return window.screen.orientation.angle;
  }
  // 2. iOS Safari 和旧版浏览器 (部分返回 90, -90)
  if (typeof window.orientation === 'number') {
    return window.orientation;
  }
  // 3. 默认竖屏
  return 0;
}

class SensorManager {
  private listeners: Set<SensorCallback> = new Set()
  private isListening: boolean = false
  private permissionState: PermissionState = 'prompt'
  private lastData: SensorData | null = null

  /**
   * 请求传感器权限（仅iOS 13+需要）
   * ⚠️ 必须由用户手势触发（如按钮点击）
   */
  async requestPermission(): Promise<PermissionState> {
    // 检查是否需要权限API（iOS 13+）
    if (typeof DeviceOrientationEvent !== 'undefined' &&
        typeof (DeviceOrientationEvent as unknown as { requestPermission: () => Promise<string> }).requestPermission === 'function') {
      try {
        const permission = await (DeviceOrientationEvent as unknown as { requestPermission: () => Promise<string> }).requestPermission()
        
        if (permission === 'granted') {
          this.permissionState = 'granted'
          console.log('✅ 传感器权限已授予')
        } else {
          this.permissionState = 'denied'
          console.warn('❌ 传感器权限被拒绝')
        }
        
        return this.permissionState
      } catch (error) {
        console.error('请求传感器权限失败:', error)
        this.permissionState = 'denied'
        return 'denied'
      }
    } else {
      // Android或旧版iOS，无需权限
      this.permissionState = 'not-required'
      console.log('✅ 设备无需请求权限，可直接使用传感器')
      return 'not-required'
    }
  }

  /**
   * 检查当前权限状态
   */
  getPermissionState(): PermissionState {
    return this.permissionState
  }

  /**
   * 开始监听传感器数据
   */
  startListening(): void {
    if (this.isListening) {
      console.warn('传感器已在监听中')
      return
    }

    if (this.permissionState === 'denied') {
      throw new Error('传感器权限被拒绝，无法启动监听')
    }

    window.addEventListener('deviceorientation', this.handleOrientation, true)
    
    // [新增] 监听屏幕旋转，以便立即更新数据
    window.addEventListener('orientationchange', this.handleScreenRotation, true);
    
    this.isListening = true
    console.log('📡 开始监听传感器数据')
  }

  /**
   * 停止监听传感器数据
   */
  stopListening(): void {
    if (!this.isListening) {
      return
    }

    window.removeEventListener('deviceorientation', this.handleOrientation, true)
    window.removeEventListener('orientationchange', this.handleScreenRotation, true);
    this.isListening = false
    console.log('🛑 停止监听传感器数据')
  }

  /**
   * 处理屏幕旋转事件
   */
  private handleScreenRotation = (): void => {
      // 屏幕旋转时，如果没有新的传感器数据进来，也需要触发一次更新，
      // 否则渲染器里的 screenOrientation 还是旧的
      if (this.lastData) {
          // 复制一份旧数据，更新屏幕方向
          const updatedData = { ...this.lastData, screenOrientation: getScreenOrientation() };
          this.lastData = updatedData;
          this.listeners.forEach(callback => { try { callback(updatedData) } catch (e) {} });
      }
  }

  /**
   * 处理设备方向事件
   */
  private handleOrientation = (event: DeviceOrientationEvent): void => {
    // 获取 iOS 特有的 webkitCompassHeading
    const eventiOS = event as any;
    const webkitCompassHeading = typeof eventiOS.webkitCompassHeading === 'number' 
      ? eventiOS.webkitCompassHeading 
      : null;
    
    // 获取当前屏幕方向
    const screenOrientation = getScreenOrientation();

    const data: SensorData = {
      alpha: event.alpha,
      beta: event.beta,
      gamma: event.gamma,
      webkitCompassHeading: webkitCompassHeading, 
      screenOrientation: screenOrientation, // [新增] 传递这个值给渲染器
      absolute: event.absolute,
      timestamp: Date.now()
    }

    this.lastData = data

    // 通知所有监听器
    this.listeners.forEach(callback => {
      try {
        callback(data)
      } catch (error) {
        console.error('传感器回调函数执行失败:', error)
      }
    })
  }

  /**
   * 添加数据监听器
   */
  addListener(callback: SensorCallback): void {
    this.listeners.add(callback)
  }

  /**
   * 移除数据监听器
   */
  removeListener(callback: SensorCallback): void {
    this.listeners.delete(callback)
  }

  /**
   * 移除所有监听器
   */
  removeAllListeners(): void {
    this.listeners.clear()
  }

  /**
   * 获取最后一次传感器数据
   */
  getLastData(): SensorData | null {
    return this.lastData
  }

  /**
   * 计算相机朝向（用于 UI 显示的估算值）
   * 注意：在 AR 模式下，Renderer 会使用更精确的四元数计算，
   * 建议直接调用 renderer.getCameraOrientation() 获取最准确的显示值。
   */
  getCameraOrientation(data: SensorData): CameraOrientation | null {
    if (data.alpha === null || data.beta === null || data.gamma === null) {
      return null
    }

    // 简单估算，仅用于 UI 降级显示
    // 真实的 AR 计算逻辑已移至 GroundObserverRenderer.ts
    
    let azimuth = data.alpha || 0;
    if (typeof data.webkitCompassHeading === 'number') {
        azimuth = data.webkitCompassHeading;
    }
    
    // 加上屏幕旋转补偿
    azimuth += data.screenOrientation;
    
    // 归一化
    azimuth = ((azimuth % 360) + 360) % 360;
    
    return {
      azimuth,
      altitude: 0 // 这里不再进行复杂的仰角计算，交给 Renderer
    }
  }

  /**
   * 检查设备是否支持传感器
   */
  static isSupported(): boolean {
    return 'DeviceOrientationEvent' in window
  }

  /**
   * 检查是否需要请求权限
   */
  static needsPermission(): boolean {
    return typeof DeviceOrientationEvent !== 'undefined' &&
           typeof (DeviceOrientationEvent as unknown as { requestPermission?: () => Promise<string> }).requestPermission === 'function'
  }
}

// 导出单例实例
export const sensorManager = new SensorManager()

// 导出类以便测试
export { SensorManager }