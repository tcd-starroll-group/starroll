import { GroundObserverRenderer, type StarClickInfo } from '@/core/renderer/GroundObserverRenderer'
import * as model from '../../../../gen/ts/models/index'
import { ref } from 'vue'

export class GroundObserver {
  private rendererInstance: GroundObserverRenderer | null = null
  public selectedStar = ref<StarClickInfo | null>(null)
  // Time control
  public enumTimeMode = {
    FIXED: 'FIXED',
    REALTIME: 'REALTIME',
    ACCELERATED: 'ACCELERATED',
  } as const
  public typeOfTimeMode = typeof this.enumTimeMode
  private timeMode: keyof typeof this.enumTimeMode = 'REALTIME'
  private fixedTimestamp: number | null = null
  private accelerationMultiplier = 2000
  private tickIntervalMs = 1000
  private timerId: ReturnType<typeof setInterval> | null = null
  private accelTimestamp: number | null = null

  constructor(container: HTMLElement) {
    this.rendererInstance = new GroundObserverRenderer(container)
    this.rendererInstance.setOnStarClick((starInfo) => {
      this.selectedStar.value = starInfo
    })
    // default: realtime mode; start time loop applying current UTC timestamp
    this.startTimeLoop()
  }

  public async enableARMode(): Promise<boolean> {
    return this.rendererInstance!.enableARMode()
  }

  public disableARMode() {
    this.rendererInstance!.disableARMode()
  }

  public setTimestamp(timestamp: number) {
    this.rendererInstance!.timestamp = timestamp
  }

  // Public API: set time mode
  public setTimeMode(mode: keyof typeof this.enumTimeMode) {
    if (this.timeMode === mode) return
    this.timeMode = mode
    if (mode === 'FIXED' && this.fixedTimestamp == null) this.fixedTimestamp = Date.now()
    if (mode === 'ACCELERATED') {
      // initialize accelerated timestamp from renderer or now
      this.accelTimestamp = this.rendererInstance?.timestamp ?? Date.now()
      // when accelerating we tick faster for smoothness
      this.setTickInterval(50)
    } else {
      // restore default 1s tick for FIXED/REALTIME
      this.setTickInterval(1000)
    }
  }

  public setFixedTimestamp(timestamp: number) {
    this.fixedTimestamp = timestamp
  }

  public setAcceleration(multiplier: number) {
    this.accelerationMultiplier = multiplier
  }

  public setTickInterval(ms: number) {
    this.tickIntervalMs = ms
    // restart the loop with new interval
    if (this.timerId) {
      this.stopTimeLoop()
      this.startTimeLoop()
    }
  }

  private startTimeLoop() {
    if (this.timerId) return
    this.timerId = setInterval(() => {
      if (!this.rendererInstance) return
      switch (this.timeMode) {
        case 'FIXED':
          // use the fixed timestamp (doesn't change but still applied every tick)
          if (this.fixedTimestamp == null) this.fixedTimestamp = Date.now()
          this.rendererInstance.timestamp = this.fixedTimestamp
          break
        case 'REALTIME':
          this.rendererInstance.timestamp = Date.now()
          break
        case 'ACCELERATED':
          if (this.accelTimestamp == null)
            this.accelTimestamp = this.rendererInstance.timestamp ?? Date.now()
          this.accelTimestamp += this.tickIntervalMs * this.accelerationMultiplier
          this.rendererInstance.timestamp = this.accelTimestamp
          break
      }
    }, this.tickIntervalMs)
  }

  private stopTimeLoop() {
    if (!this.timerId) return
    clearInterval(this.timerId)
    this.timerId = null
  }

  public setLocation(location: model.GPS) {
    this.rendererInstance!.location = location
  }

  public async testTimeFlash() {
    const start_time = 1772034664175
    let timestamp = start_time
    if (!this.rendererInstance) return
    this.rendererInstance.timestamp = timestamp

    const multiplier = 2000
    const intervalMs = 50
    const incrementMs = intervalMs * multiplier // simulated ms per tick

    while (true) {
      await new Promise((resolve) => setTimeout(resolve, intervalMs))
      timestamp += incrementMs
      this.rendererInstance.timestamp = timestamp
    }
  }
}
