/**
 * 传感器数据管理模块
 * 用于读取iOS和Android设备的陀螺仪和方向传感器数据
 */

export interface SensorData {
  alpha: number | null  // Z轴旋转角度 (0-360度)
  beta: number | null   // X轴旋转角度 (-180到180度)
  gamma: number | null  // Y轴旋转角度 (-90到90度)
  absolute: boolean     // 是否为绝对方向
  timestamp: number     // 时间戳
}

export interface CameraOrientation {
  azimuth: number    // 方位角 (0-360度，正北为0)
  altitude: number   // 仰角 (-90到90度)
}

export type SensorCallback = (data: SensorData) => void
export type PermissionState = 'granted' | 'denied' | 'prompt' | 'not-required'

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
    this.isListening = false
    console.log('🛑 停止监听传感器数据')
  }

  /**
   * 处理设备方向事件
   */
  private handleOrientation = (event: DeviceOrientationEvent): void => {
    const data: SensorData = {
      alpha: event.alpha,
      beta: event.beta,
      gamma: event.gamma,
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
   * 计算相机朝向（方位角和仰角）
   * 将传感器的欧拉角转换为天文学中的水平坐标系统
   */
  getCameraOrientation(data: SensorData): CameraOrientation | null {
    if (data.alpha === null || data.beta === null || data.gamma === null) {
      return null
    }

    // iOS和Android的坐标系统可能不同
    // 这里需要根据实际测试调整
    const isIOS = /iPhone|iPad|iPod/.test(navigator.userAgent)
    
    let azimuth: number
    let altitude: number

    if (isIOS) {
      // iOS设备方向事件定义：
      // - alpha (0-360): 设备绕Z轴旋转，指南针方向
      // - beta (-180到180): 设备绕X轴旋转（前后倾斜）
      // - gamma (-90到90): 设备绕Y轴旋转（左右倾斜）
      
      // 当手机竖直握持（屏幕朝向你）：
      // - beta = 0°: 竖直
      // - beta = -90°: 平躺屏幕朝上（看天空）
      // - beta = 90°: 平躺屏幕朝下（看地面）
      
      // 方位角计算（指南针方向）
      azimuth = data.alpha
      
      // 仰角计算：需要从beta转换为天文学的仰角
      // 当手机平躺屏幕朝上看天空时：beta = -90, altitude = 90（天顶）
      // 当手机竖直时：beta = 0, altitude = 0（地平线）
      // 当手机平躺屏幕朝下时：beta = 90, altitude = -90（天底）
      altitude = data.beta - 90
      
    } else {
      // Android: 通常与iOS相似
      azimuth = data.alpha
      altitude = data.beta - 90
    }

    // 归一化角度范围
    azimuth = ((azimuth % 360) + 360) % 360  // 0-360
    altitude = Math.max(-90, Math.min(90, altitude))  // -90到90

    return {
      azimuth,
      altitude
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

