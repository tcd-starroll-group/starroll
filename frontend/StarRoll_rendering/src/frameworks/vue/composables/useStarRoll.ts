import { ref, onMounted, onUnmounted, shallowRef } from 'vue';
import { StarrollRenderer } from '@/core/renderer/StarrollRenderer';
import { PlanetConfig } from '@/types/planet';
import { ConstellationData } from '@/types/constellation';
import { NebulaType } from '@/core/renderer/background/NebulaVariants';

// 全局单例状态 (简单实现)
const rendererInstance = shallowRef<StarrollRenderer | null>(null);
const currentMode = ref<'system' | 'starry'>('system');
const isPaused = ref(false);
const timeScale = ref(1.0);
const selectedObject = ref<PlanetConfig | ConstellationData | null>(null);
const currentNebula = ref<NebulaType>('spiral');

export function useStarRoll() {
    
    const init = (container: HTMLElement) => {
        if (rendererInstance.value) return;
        rendererInstance.value = new StarrollRenderer(container);
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
    
    const focusTarget = (target: PlanetConfig | ConstellationData) => {
        selectedObject.value = target;
        if (rendererInstance.value) {
            rendererInstance.value.focus(target);
        }
    };

    const setNebula = (type: NebulaType) => {
        currentNebula.value = type;
        if (rendererInstance.value) {
            rendererInstance.value.galaxyRenderer.setNebulaType(type);
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
        setNebula
    };
}
