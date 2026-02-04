import { ref, shallowRef } from 'vue';
import { StarWalk2Renderer } from '@/core/renderer/StarWalk2Renderer';

// 全局状态
const rendererInstance = shallowRef<StarWalk2Renderer | null>(null);
const arModeEnabled = ref(false);
const stats = ref({
    totalStars: 0,
    visibleStars: 0,
    currentMagLimit: 0,
    currentZoom: 1.0,
    observerLocation: '',
    azimuth: 0,
    altitude: 0,
    arMode: false
});

/**
 * StarWalk2 级别组合式函数
 */
export function useStarWalk2() {
    
    const init = (container: HTMLElement) => {
        if (rendererInstance.value) return;
        
        console.log('🚀 启动 StarWalk2 级别渲染器');
        console.log('📐 完整分层架构 + 望远镜缩放 + 星密度变化');
        
        rendererInstance.value = new StarWalk2Renderer(container);
        
        setTimeout(() => {
            refreshStats();
        }, 3000);
    };
    
    const enableARMode = async () => {
        if (!rendererInstance.value) return false;
        
        const success = await rendererInstance.value.enableARMode();
        arModeEnabled.value = success;
        
        return success;
    };
    
    const disableARMode = () => {
        if (rendererInstance.value) {
            rendererInstance.value.disableARMode();
            arModeEnabled.value = false;
        }
    };
    
    const refreshStats = () => {
        if (rendererInstance.value) {
            stats.value = rendererInstance.value.getStats();
            console.log('📊 StarWalk2 统计:', stats.value);
        }
    };
    
    const setConstellationLinesVisible = (visible: boolean) => {
        if (rendererInstance.value) {
            rendererInstance.value.setConstellationLinesVisible(visible);
        }
    };
    
    return {
        init,
        renderer: rendererInstance,
        arModeEnabled,
        enableARMode,
        disableARMode,
        stats,
        refreshStats,
        setConstellationLinesVisible
    };
}
