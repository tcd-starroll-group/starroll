import { ref, shallowRef } from 'vue';
import { StarrollRendererV3 } from '@/core/renderer/StarrollRendererV3';
import { PlanetConfig } from '@/types/planet';
import { NebulaType } from '@/core/renderer/background/NebulaVariants';

// 全局单例状态
const rendererInstance = shallowRef<StarrollRendererV3 | null>(null);
const currentMode = ref<'system' | 'starry'>('starry');
const isPaused = ref(false);
const timeScale = ref(0.1);
const selectedObject = ref<PlanetConfig | null>(null);
const currentNebula = ref<NebulaType>('spiral');
const showConstellationLines = ref(true);
const showConstellationModels = ref(true);
const stats = ref({ totalStars: 0, visibleStars: 0, constellations: 0, models: 0 });

/**
 * StarRoll V3 组合式函数
 * 支持真实星表 + 星座 3D 模型
 */
export function useStarRollV3() {
    
    const init = (container: HTMLElement) => {
        if (rendererInstance.value) return;
        
        console.log('🚀 初始化 StarRoll V3 - 真实星表 + 3D 模型渲染');
        rendererInstance.value = new StarrollRendererV3(container);
        
        // 延迟获取统计信息
        setTimeout(() => {
            if (rendererInstance.value) {
                stats.value = rendererInstance.value.getStats();
                console.log('📊 最终统计:', stats.value);
            }
        }, 3000);
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
     * 切换星座连线
     */
    const toggleConstellationLines = () => {
        showConstellationLines.value = !showConstellationLines.value;
        if (rendererInstance.value) {
            rendererInstance.value.setConstellationLinesVisible(showConstellationLines.value);
        }
    };

    /**
     * 切换星座 3D 模型
     */
    const toggleConstellationModels = () => {
        showConstellationModels.value = !showConstellationModels.value;
        if (rendererInstance.value) {
            rendererInstance.value.setConstellationModelsVisible(showConstellationModels.value);
        }
    };

    /**
     * 设置特定星座可见性
     */
    const setConstellationVisible = (id: string, visible: boolean) => {
        if (rendererInstance.value) {
            rendererInstance.value.setConstellationVisible(id, visible);
        }
    };

    /**
     * 刷新统计信息
     */
    const refreshStats = () => {
        if (rendererInstance.value) {
            stats.value = rendererInstance.value.getStats();
        }
    };

    /**
     * 聚焦到指定星座
     */
    const focusConstellation = (id: string) => {
        if (rendererInstance.value) {
            rendererInstance.value.focusConstellation(id);
        }
    };

    /**
     * 获取所有星座列表
     */
    const getConstellations = () => {
        if (rendererInstance.value) {
            return rendererInstance.value.getConstellations();
        }
        return [];
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
        showConstellationModels,
        toggleConstellationModels,
        setConstellationVisible,
        stats,
        refreshStats,
        focusConstellation,
        getConstellations
    };
}
