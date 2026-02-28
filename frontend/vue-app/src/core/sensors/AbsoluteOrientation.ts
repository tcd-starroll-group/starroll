import * as THREE from 'three'

export interface AbsoluteOrientationData {
  quaternion: THREE.Quaternion
}

export type SensorCallback = (data: AbsoluteOrientationData) => void

class AbsoluteOrientationManager {
  private listeners: Set<SensorCallback> = new Set()
  private isListening: boolean = false
  private sensor: any = null // AbsoluteOrientationSensor
  private deviceOrientationHandler: ((e: DeviceOrientationEvent) => void) | null = null
  private compassHeadingHandler: ((e: DeviceOrientationEvent) => void) | null = null
  private lastCompassHeading: number | null = null
  private compassOffset: number | null = null // CompassHeading 与 alpha 之间的差距
  private lastDeviceOrientationEvent: DeviceOrientationEvent | null = null
  private polling: boolean = false
  private rafId: number | null = null

  // Three.js 内部复用对象，避免频繁垃圾回收
  private readonly tempEuler = new THREE.Euler()
  private readonly tempQuaternion = new THREE.Quaternion()
  private readonly worldQuaternion = new THREE.Quaternion(-Math.sqrt(0.5), 0, 0, Math.sqrt(0.5)) // -90deg X 修正

  startListening(): void {
    if (this.isListening) return

    // 1. 优先尝试现代 Sensor API
    if (typeof (window as any).AbsoluteOrientationSensor !== 'undefined') {
      this.setupModernSensor()
    } else {
      // 2. 回退到 DeviceOrientation 事件
      this.setupDeviceOrientation()
    }

    this.isListening = true
  }

  private setupModernSensor() {
    this.sensor = new (window as any).AbsoluteOrientationSensor({ frequency: 60 })
    this.sensor.addEventListener('reading', () => {
      // Sensor API 返回的是直接的四元数数组 [x, y, z, w]
      this.tempQuaternion.fromArray(this.sensor.quaternion)
      this.notify(this.tempQuaternion)
    })
    this.sensor.start()
  }

  private setupDeviceOrientation() {
    // deviceorientation handler: store latest event and let the RAF loop process it
    this.deviceOrientationHandler = (event: DeviceOrientationEvent) => {
      this.lastDeviceOrientationEvent = event
    }

    // main deviceorientation listener for orientation data
    window.addEventListener('deviceorientation', this.deviceOrientationHandler, true)

    // separate listener solely to capture webkitCompassHeading when present
    this.compassHeadingHandler = (event: DeviceOrientationEvent) => {
      const eAny = event as any
      if (typeof eAny.webkitCompassHeading === 'number') {
        this.lastCompassHeading = eAny.webkitCompassHeading
      }
    }
    window.addEventListener('deviceorientation', this.compassHeadingHandler, true)

    // start a RAF polling loop to process the most recent deviceorientation at display rate (~60Hz)
    this.startPollLoop()
  }

  private processDeviceOrientationEvent(event: DeviceOrientationEvent) {
    let { alpha, beta, gamma } = event

    if (alpha === null || beta === null || gamma === null) return

    const fmt = (v: number | null | undefined) => (v == null ? null : Number(v.toFixed(2)))

    // choose heading: prefer lastCompassHeading (from separate listener),
    // otherwise use absolute alpha when event.absolute === true, else fallback to relative alpha
    let usedHeadingSource = 'relative alpha (fallback)'
    let heading: number | null = null
    if (this.lastCompassHeading != null && this.compassOffset == null) {
      // alpha 是逆时针正，this.lastCompassHeading 是顺时针正
      heading = 360 - this.lastCompassHeading
      this.compassOffset = heading - alpha
      usedHeadingSource = 'stored webkitCompassHeading'
    } else {
      // no compass heading available; if event.absolute is true and alpha present, use it
      const eAny = event as any
      if (eAny && eAny.absolute && typeof alpha === 'number') {
        heading = alpha
        usedHeadingSource = 'event.absolute alpha'
      }
    }

    // Debug log: raw deviceorientation values (rounded to 2 decimals)
    console.debug('deviceorientation (processed):', {
      alpha: fmt(alpha),
      beta: fmt(beta),
      gamma: fmt(gamma),
      heading: fmt(heading),
      usedHeadingSource,
    })

    const degToRad = Math.PI / 180
    const zRad = (alpha + this.compassOffset!) * degToRad
    // Map: heading -> Z, beta -> X, gamma -> Y; order 'ZXY'
    this.tempEuler.set(beta * degToRad, gamma * degToRad, zRad, 'ZXY')
    this.tempQuaternion.setFromEuler(this.tempEuler)
    this.notify(this.tempQuaternion)
  }

  private startPollLoop() {
    if (this.polling) return
    this.polling = true
    const loop = () => {
      if (!this.polling) return
      if (this.lastDeviceOrientationEvent) {
        this.processDeviceOrientationEvent(this.lastDeviceOrientationEvent)
      }
      this.rafId = requestAnimationFrame(loop)
    }
    this.rafId = requestAnimationFrame(loop)
  }

  private stopPollLoop() {
    this.polling = false
    if (this.rafId != null) {
      cancelAnimationFrame(this.rafId)
      this.rafId = null
    }
    this.lastDeviceOrientationEvent = null
  }

  private notify(quaternion: THREE.Quaternion) {
    const data: AbsoluteOrientationData = {
      // 复制一份，防止外部修改影响内部状态
      quaternion: quaternion.clone(),
    }
    this.listeners.forEach((cb) => cb(data))
  }

  stopListening() {
    if (this.sensor) this.sensor.stop()
    if (this.deviceOrientationHandler) {
      window.removeEventListener('deviceorientation', this.deviceOrientationHandler, true)
      this.deviceOrientationHandler = null
    }
    if (this.compassHeadingHandler) {
      window.removeEventListener('deviceorientation', this.compassHeadingHandler, true)
      this.compassHeadingHandler = null
      this.lastCompassHeading = null
    }
    this.isListening = false
  }

  addListener(callback: SensorCallback) {
    this.listeners.add(callback)
  }
}

export const absoluteOrientationManager = new AbsoluteOrientationManager()
