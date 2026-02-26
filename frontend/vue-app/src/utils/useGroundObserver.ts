import { GroundObserverRenderer, type StarClickInfo } from '@/core/renderer/GroundObserverRenderer'
import * as model from '../../../../gen/ts/models/index'
import { ref } from 'vue'

export class GroundObserver {
  private rendererInstance: GroundObserverRenderer | null = null
  public selectedStar = ref<StarClickInfo | null>(null)

  constructor(container: HTMLElement) {
    this.rendererInstance = new GroundObserverRenderer(container)
    this.rendererInstance.setOnStarClick((starInfo) => {
      this.selectedStar.value = starInfo
    })
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
