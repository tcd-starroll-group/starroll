import { ref, shallowRef } from 'vue';
import { DualSceneRenderer, SceneMode, ViewTarget } from '@/core/renderer/DualSceneRenderer';
import { PlanetConfig } from '@/types/planet';
import { NebulaType } from '@/core/renderer/background/NebulaVariants';

// 全局状态
const rendererInstance = shallowRef<DualSceneRenderer | null>(null);
const currentMode = ref<SceneMode>('overview');
const currentTarget = ref<ViewTarget>('system');
const selectedPlanet = ref<PlanetConfig | null>(null);
const selectedConstellation = ref<string | null>(null);
const isPaused = ref(false);
const timeScale = ref(0.1);
const currentNebula = ref<NebulaType>('spiral');
const stats = ref({ totalStars: 0, visibleStars: 0, constellations: 0, models: 0 });

/**
 * 双场景组合式函数
 * 支持 Overview / Explore 模式切换
 */
export function useDualScene() {
    
    /**
     * 初始化渲染器
     */
    const init = (container: HTMLElement) => {
        if (rendererInstance.value) return;
        
        console.log('🎬 初始化双场景渲染系统');
        rendererInstance.value = new DualSceneRenderer(container);
        
        // 延迟获取统计
        setTimeout(() => {
            if (rendererInstance.value) {
                stats.value = rendererInstance.value.getStarCatalogRenderer().getStats();
                console.log('📊 统计信息:', stats.value);
            }
        }, 3000);
    };
    
    /**
     * 设置视图目标（太阳系 / 星空）
     */
    const setViewTarget = (target: ViewTarget) => {
        currentTarget.value = target;
        if (rendererInstance.value) {
            rendererInstance.value.setViewTarget(target);
        }
    };
    
    /**
     * 选择行星（进入探索模式）
     */
    const selectPlanet = async (planet: PlanetConfig) => {
        if (!rendererInstance.value) return;
        
        selectedPlanet.value = planet;
        selectedConstellation.value = null;
        
        console.log(`🌍 选择行星: ${planet.name}`);
        
        // 切换到探索模式
        await rendererInstance.value.switchToExplore(planet);
        currentMode.value = 'explore';
    };
    
    /**
     * 选择星座
     */
    const selectConstellation = (id: string, name: string) => {
        if (!rendererInstance.value || currentMode.value !== 'overview') return;
        
        selectedConstellation.value = id;
        selectedPlanet.value = null;
        
        console.log(`✨ 选择星座: ${name}`);
        
        // 在 Overview 模式下聚焦星座
        // TODO: 实现星座聚焦
    };
    
    /**
     * 返回概览模式
     */
    const backToOverview = async () => {
        if (!rendererInstance.value) return;
        
        console.log('🔙 返回概览模式');
        
        selectedPlanet.value = null;
        selectedConstellation.value = null;
        
        await rendererInstance.value.switchToOverview();
        currentMode.value = 'overview';
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
     * 设置星云类型
     */
    const setNebula = (type: NebulaType) => {
        currentNebula.value = type;
        if (rendererInstance.value) {
            // TODO: 实现星云切换
        }
    };
    
    /**
     * 获取可用的星座列表
     */
    const getConstellations = () => {
        // TODO: 从 constellation-models 获取
        return [];
    };
    
    /**
     * 刷新统计
     */
    const refreshStats = () => {
        if (rendererInstance.value) {
            stats.value = rendererInstance.value.getStarCatalogRenderer().getStats();
        }
    };
    
    return {
        init,
        renderer: rendererInstance,
        currentMode,
        currentTarget,
        setViewTarget,
        selectedPlanet,
        selectedConstellation,
        selectPlanet,
        selectConstellation,
        backToOverview,
        isPaused,
        togglePause,
        timeScale,
        setSpeed,
        currentNebula,
        setNebula,
        stats,
        refreshStats,
        getConstellations
    };
}
