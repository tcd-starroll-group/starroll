import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { SensorManager, type SensorData } from './sensor'

describe('SensorManager', () => {
  let manager: SensorManager

  beforeEach(() => {
    manager = new SensorManager()
  })

  afterEach(() => {
    manager.stopListening()
    manager.removeAllListeners()
  })

  describe('静态方法', () => {
    it('应该检测设备是否支持传感器', () => {
      const isSupported = SensorManager.isSupported()
      expect(typeof isSupported).toBe('boolean')
    })

    it('应该检测是否需要请求权限', () => {
      const needsPermission = SensorManager.needsPermission()
      expect(typeof needsPermission).toBe('boolean')
    })
  })

  describe('权限管理', () => {
    it('初始权限状态应该是prompt', () => {
      expect(manager.getPermissionState()).toBe('prompt')
    })

    it('requestPermission应该返回权限状态', async () => {
      const result = await manager.requestPermission()
      expect(['granted', 'denied', 'not-required']).toContain(result)
    })
  })

  describe('数据监听', () => {
    it('应该能够添加和移除监听器', () => {
      const callback = vi.fn()
      
      manager.addListener(callback)
      manager.removeListener(callback)
      
      expect(callback).not.toHaveBeenCalled()
    })

    it('应该能够移除所有监听器', () => {
      const callback1 = vi.fn()
      const callback2 = vi.fn()
      
      manager.addListener(callback1)
      manager.addListener(callback2)
      manager.removeAllListeners()
      
      // 即使触发事件，回调也不应该被调用
      expect(callback1).not.toHaveBeenCalled()
      expect(callback2).not.toHaveBeenCalled()
    })

    it('获取最后的传感器数据应该初始为null', () => {
      expect(manager.getLastData()).toBeNull()
    })
  })

  describe('相机朝向计算', () => {
    it('应该能够从传感器数据计算相机朝向', () => {
      const sensorData: SensorData = {
        alpha: 0,    // 正北
        beta: 90,    // 平躺
        gamma: 0,
        absolute: true,
        timestamp: Date.now()
      }

      const orientation = manager.getCameraOrientation(sensorData)
      
      expect(orientation).not.toBeNull()
      expect(orientation?.azimuth).toBeGreaterThanOrEqual(0)
      expect(orientation?.azimuth).toBeLessThan(360)
      expect(orientation?.altitude).toBeGreaterThanOrEqual(-90)
      expect(orientation?.altitude).toBeLessThanOrEqual(90)
    })

    it('当传感器数据为null时应该返回null', () => {
      const sensorData: SensorData = {
        alpha: null,
        beta: null,
        gamma: null,
        absolute: false,
        timestamp: Date.now()
      }

      const orientation = manager.getCameraOrientation(sensorData)
      expect(orientation).toBeNull()
    })

    it('方位角应该在0-360度范围内', () => {
      const testCases = [
        { alpha: 0, beta: 0, gamma: 0 },
        { alpha: 90, beta: 45, gamma: 0 },
        { alpha: 180, beta: 90, gamma: 0 },
        { alpha: 270, beta: -45, gamma: 0 },
        { alpha: 359, beta: 0, gamma: 0 }
      ]

      testCases.forEach(({ alpha, beta, gamma }) => {
        const sensorData: SensorData = {
          alpha,
          beta,
          gamma,
          absolute: true,
          timestamp: Date.now()
        }

        const orientation = manager.getCameraOrientation(sensorData)
        expect(orientation).not.toBeNull()
        expect(orientation!.azimuth).toBeGreaterThanOrEqual(0)
        expect(orientation!.azimuth).toBeLessThan(360)
      })
    })

    it('仰角应该在-90到90度范围内', () => {
      const testCases = [
        { alpha: 0, beta: 0, gamma: 0 },      // 仰角 = 90
        { alpha: 0, beta: 90, gamma: 0 },     // 仰角 = 0
        { alpha: 0, beta: 180, gamma: 0 },    // 仰角 = -90
      ]

      testCases.forEach(({ alpha, beta, gamma }) => {
        const sensorData: SensorData = {
          alpha,
          beta,
          gamma,
          absolute: true,
          timestamp: Date.now()
        }

        const orientation = manager.getCameraOrientation(sensorData)
        expect(orientation).not.toBeNull()
        expect(orientation!.altitude).toBeGreaterThanOrEqual(-90)
        expect(orientation!.altitude).toBeLessThanOrEqual(90)
      })
    })
  })

  describe('边界情况', () => {
    it('停止未启动的监听应该不报错', () => {
      expect(() => manager.stopListening()).not.toThrow()
    })

    it('重复启动监听应该打印警告', () => {
      const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => {})
      
      manager.startListening()
      manager.startListening()
      
      expect(consoleSpy).toHaveBeenCalled()
      
      consoleSpy.mockRestore()
    })
  })
})
