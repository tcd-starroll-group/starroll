import { ref, shallowRef } from 'vue'
import { GroundObserverRenderer, type StarClickInfo } from '@/core/renderer/GroundObserverRenderer'

// 全局状态
const rendererInstance = shallowRef<GroundObserverRenderer | null>(null)
const currentTime = ref<Date>(new Date())
const arModeEnabled = ref(false)
const cameraOrientation = ref({ azimuth: 0, altitude: 0 })
const showConstellationLines = ref(true)
const showStarLabels = ref(true)
const selectedStar = ref<StarClickInfo | null>(null)
const isRequestingLocation = ref(false)

/**
 * 地面观测者组合式函数
 * 模拟从地球表面观测星空
 */
export function useGroundObserver() {
  /**
   * 初始化
   */
  const init = (container: HTMLElement) => {
    if (rendererInstance.value) return

    rendererInstance.value = new GroundObserverRenderer(container)

    // 设置星星点击回调
    rendererInstance.value.setOnStarClick((starInfo) => {
      selectedStar.value = starInfo
    })
  }

  /**
   * 启用 AR 模式
   */
  const enableARMode = async () => {
    if (!rendererInstance.value) {
      console.error('渲染器未初始化')
      return false
    }

    const success = await rendererInstance.value.enableARMode()
    arModeEnabled.value = success

    return success
  }

  /**
   * 禁用 AR 模式
   */
  const disableARMode = () => {
    if (rendererInstance.value) {
      rendererInstance.value.disableARMode()
      arModeEnabled.value = false
    }
  }

  // ... 其他方法保持不变 ...
  const toggleConstellationLines = () => {
    showConstellationLines.value = !showConstellationLines.value
    if (rendererInstance.value)
      rendererInstance.value.setConstellationLinesVisible(showConstellationLines.value)
  }

  const closeStarInfo = () => {
    selectedStar.value = null
  }

  return {
    init,
    renderer: rendererInstance,
    currentTime,
    arModeEnabled,
    enableARMode,
    disableARMode,
    cameraOrientation,
    showConstellationLines,
    toggleConstellationLines,
    showStarLabels,
    selectedStar,
    closeStarInfo,
    isRequestingLocation,
  }
}
