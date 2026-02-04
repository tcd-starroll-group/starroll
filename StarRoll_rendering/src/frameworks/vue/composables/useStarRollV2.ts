import { ref, onMounted, onUnmounted, shallowRef } from 'vue';
import { StarrollRendererV2 } from '@/core/renderer/StarrollRendererV2';
import { PlanetConfig } from '@/types/planet';
import { NebulaType } from '@/core/renderer/background/NebulaVariants';

// 全局单例状态
const rendererInstance = shallowRef<StarrollRendererV2 | null>(null);
const currentMode = ref<'system' | 'starry'>('starry'); // 默认星空模式
const isPaused = ref(false);
const timeScale = ref(0.1);
const selectedObject = ref<PlanetConfig | null>(null);
const currentNebula = ref<NebulaType>('spiral');
const showConstellationLines = ref(true);
const starCatalogStats = ref({ totalStars: 0, visibleStars: 0, constellations: 0 });

/**
 * StarRoll V2 组合式函数
 * 支持真实星表数据渲染
 */
export function useStarRollV2() {
    
    const init = (container: HTMLElement) => {
        if (rendererInstance.value) return;
        
        console.log('Initializing StarRoll V2 with real star catalog...');
        rendererInstance.value = new StarrollRendererV2(container);
        
        // 延迟获取统计信息（等待星表加载）
        setTimeout(() => {
            if (rendererInstance.value) {
                starCatalogStats.value = rendererInstance.value.getStarCatalogStats();
                console.log('Star catalog stats:', starCatalogStats.value);
            }
        }, 2000);
    };

    const setMode = (mode: 'system' | 'starry') => {
        currentMode.value = mode;
        if (rendererInstance.value) {
            rendererInstance.value.setMode(mode);
        }
    };

    const togglePause = () => {
        isPaused.value = !isPaused.value;
        if (rendererInstance.value) {
            if (isPaused.value) rendererInstance.value.planets.pause();
            else rendererInstance.value.planets.resume();
        }
    };

    const setSpeed = (speed: number) => {
        timeScale.value = speed;
        if (rendererInstance.value) {
            rendererInstance.value.planets.setTimeScale(speed);
        }
    };
    
    const focusTarget = (target: PlanetConfig) => {
        selectedObject.value = target;
        if (rendererInstance.value) {
            const planetData = rendererInstance.value.planets.getPlanet(target.id);
            if (planetData) {
                rendererInstance.value.cameraDirector.focus(planetData.mesh);
            }
        }
    };

    const setNebula = (type: NebulaType) => {
        currentNebula.value = type;
        if (rendererInstance.value) {
            rendererInstance.value.galaxyRenderer.setNebulaType(type);
        }
    };

    /**
     * 切换星座连线显示
     */
    const toggleConstellationLines = () => {
        showConstellationLines.value = !showConstellationLines.value;
        if (rendererInstance.value) {
            rendererInstance.value.setConstellationLinesVisible(showConstellationLines.value);
        }
    };

    /**
     * 设置特定星座的可见性
     */
    const setConstellationVisible = (id: string, visible: boolean) => {
        if (rendererInstance.value) {
            rendererInstance.value.setConstellationVisible(id, visible);
        }
    };

    /**
     * 刷新星表统计信息
     */
    const refreshStats = () => {
        if (rendererInstance.value) {
            starCatalogStats.value = rendererInstance.value.getStarCatalogStats();
        }
    };

    return {
        init,
        renderer: rendererInstance,
        currentMode,
        setMode,
        isPaused,
        togglePause,
        timeScale,
        setSpeed,
        selectedObject,
        focusTarget,
        currentNebula,
        setNebula,
        showConstellationLines,
        toggleConstellationLines,
        setConstellationVisible,
        starCatalogStats,
        refreshStats
    };
}
