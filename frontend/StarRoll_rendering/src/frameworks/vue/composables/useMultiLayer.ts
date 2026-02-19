import { ref, shallowRef } from 'vue';
import { MultiLayerRenderer } from '@/core/renderer/MultiLayerRenderer';
import { PlanetConfig } from '@/types/planet';

// 全局状态
const rendererInstance = shallowRef<MultiLayerRenderer | null>(null);
const currentMode = ref<'overview' | 'explore'>('overview');
const selectedPlanet = ref<PlanetConfig | null>(null);
const selectedConstellation = ref<string | null>(null);
const showConstellations = ref(true);
const isPaused = ref(false);
const timeScale = ref(0.1);
const stats = ref({ totalStars: 0, visibleStars: 0, constellations: 0, models: 0 });

/**
 * 多层渲染系统组合式函数
 * StarWalk2 级别的架构
 */
export function useMultiLayer() {
    
    /**
     * 初始化
     */
    const init = (container: HTMLElement) => {
        if (rendererInstance.value) return;
        
        console.log('🚀 初始化 StarWalk2 级别多层渲染系统');
        console.log('📐 架构: Sky Layer → Deep Space Layer → Planet Surface Layer → UI Overlay');
        
        rendererInstance.value = new MultiLayerRenderer(container);
        
        // 延迟获取统计
        setTimeout(() => {
            refreshStats();
        }, 3000);
    };
    
    /**
     * 选择行星（进入探索模式）
     */
    const selectPlanet = async (planet: PlanetConfig) => {
        if (!rendererInstance.value || currentMode.value === 'explore') return;
        
        selectedPlanet.value = planet;
        selectedConstellation.value = null;
        
        console.log(`🪐 选择行星: ${planet.name}`);
        
        await rendererInstance.value.switchToExplore(planet);
        currentMode.value = 'explore';
    };
    
    /**
     * 返回概览
     */
    const backToOverview = async () => {
        if (!rendererInstance.value || currentMode.value === 'overview') return;
        
        console.log('🔙 返回概览');
        
        selectedPlanet.value = null;
        
        await rendererInstance.value.switchToOverview();
        currentMode.value = 'overview';
    };
    
    /**
     * 切换星座显示
     */
    const toggleConstellations = () => {
        showConstellations.value = !showConstellations.value;
        if (rendererInstance.value) {
            rendererInstance.value.setConstellationsVisible(showConstellations.value);
        }
    };
    
    /**
     * 暂停/恢复
     */
    const togglePause = () => {
        isPaused.value = !isPaused.value;
        if (rendererInstance.value) {
            const planetSystem = rendererInstance.value.getPlanetSystem();
            if (isPaused.value) planetSystem.pause();
            else planetSystem.resume();
        }
    };
    
    /**
     * 设置时间速度
     */
    const setSpeed = (speed: number) => {
        timeScale.value = speed;
        if (rendererInstance.value) {
            rendererInstance.value.getPlanetSystem().setTimeScale(speed);
        }
    };
    
    /**
     * 刷新统计
     */
    const refreshStats = () => {
        if (rendererInstance.value) {
            stats.value = rendererInstance.value.getStats();
            console.log('📊 渲染统计:', stats.value);
        }
    };
    
    return {
        init,
        renderer: rendererInstance,
        currentMode,
        selectedPlanet,
        selectedConstellation,
        selectPlanet,
        backToOverview,
        showConstellations,
        toggleConstellations,
        isPaused,
        togglePause,
        timeScale,
        setSpeed,
        stats,
        refreshStats
    };
}
