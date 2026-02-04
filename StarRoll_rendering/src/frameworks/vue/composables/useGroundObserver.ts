import { ref, shallowRef } from 'vue';
import { GroundObserverRenderer } from '@/core/renderer/GroundObserverRenderer';
import { ObserverLocation, OBSERVER_LOCATIONS } from '@/core/astronomy/HorizonCoordinates';

// 全局状态
const rendererInstance = shallowRef<GroundObserverRenderer | null>(null);
const currentLocation = ref<ObserverLocation>(OBSERVER_LOCATIONS.SHANGHAI);
const currentTime = ref<Date>(new Date());
const arModeEnabled = ref(false);
const cameraOrientation = ref({ azimuth: 0, altitude: 0 });
const showConstellationLines = ref(true);
const showStarLabels = ref(true);
const stats = ref({ 
    visibleStars: 0, 
    visibleConstellations: 0, 
    observerLocation: '', 
    localSiderealTime: '',
    arMode: false,
    sensorPermission: 'prompt' as any
});

/**
 * 地面观测者组合式函数
 * 模拟从地球表面观测星空
 */
export function useGroundObserver() {
    
    /**
     * 初始化
     */
    const init = (container: HTMLElement) => {
        if (rendererInstance.value) return;
        
        console.log('🌍 初始化地面观测模式');
        console.log('视角: 地球表面观测者');
        console.log('坐标系: 地平坐标系');
        
        rendererInstance.value = new GroundObserverRenderer(container);
        
        // 延迟获取统计
        setTimeout(() => {
            refreshStats();
        }, 3000);
    };
    
    /**
     * 设置观测地点
     */
    const setLocation = (location: ObserverLocation) => {
        currentLocation.value = location;
        if (rendererInstance.value) {
            rendererInstance.value.setObserverLocation(location);
        }
    };
    
    /**
     * 设置观测时间
     */
    const setTime = (time: Date) => {
        currentTime.value = time;
        if (rendererInstance.value) {
            rendererInstance.value.setObservationTime(time);
        }
    };
    
    /**
     * 刷新统计
     */
    const refreshStats = () => {
        if (rendererInstance.value) {
            stats.value = rendererInstance.value.getStats();
            console.log('📊 地面观测统计:', stats.value);
        }
    };
    
    /**
     * 启用 AR 模式
     */
    const enableARMode = async () => {
        if (!rendererInstance.value) {
            console.error('渲染器未初始化');
            return false;
        }
        
        const success = await rendererInstance.value.enableARMode();
        arModeEnabled.value = success;
        
        if (success) {
            // 启动相机朝向更新循环
            startOrientationTracking();
        }
        
        return success;
    };
    
    /**
     * 禁用 AR 模式
     */
    const disableARMode = () => {
        if (rendererInstance.value) {
            rendererInstance.value.disableARMode();
            arModeEnabled.value = false;
        }
    };
    
    /**
     * 获取当前相机朝向（调试用）
     */
    const startOrientationTracking = () => {
        const update = () => {
            if (!arModeEnabled.value || !rendererInstance.value) return;
            
            const orientation = rendererInstance.value.getCameraOrientation();
            cameraOrientation.value = orientation;
            
            requestAnimationFrame(update);
        };
        update();
    };
    
    /**
     * 切换星座连线
     */
    const toggleConstellationLines = () => {
        showConstellationLines.value = !showConstellationLines.value;
        if (rendererInstance.value) {
            rendererInstance.value.setConstellationLinesVisible(showConstellationLines.value);
        }
    };
    
    /**
     * 切换星星标签
     */
    const toggleStarLabels = () => {
        showStarLabels.value = !showStarLabels.value;
        if (rendererInstance.value) {
            rendererInstance.value.setStarLabelsVisible(showStarLabels.value);
        }
    };
    
    return {
        init,
        renderer: rendererInstance,
        currentLocation,
        setLocation,
        currentTime,
        setTime,
        stats,
        refreshStats,
        arModeEnabled,
        enableARMode,
        disableARMode,
        cameraOrientation,
        showConstellationLines,
        toggleConstellationLines,
        showStarLabels,
        toggleStarLabels,
        availableLocations: OBSERVER_LOCATIONS
    };
}
