<script setup lang="ts">
import { useStarRollV3 } from '../composables/useStarRollV3';
import { solarSystemData } from '@/core/data/planets';
import { NebulaType } from '@/core/renderer/background/NebulaVariants';
import { computed, ref, onMounted } from 'vue';

const { 
    currentMode, 
    setMode, 
    focusTarget, 
    selectedObject, 
    currentNebula, 
    setNebula,
    focusConstellation,
    getConstellations
} = useStarRollV3();

// 星座列表
const constellations = ref<Array<{ id: string; name: string }>>([]);
const selectedConstellation = ref<string | null>(null);

// 当前显示的列表
const currentList = computed(() => {
    if (currentMode.value === 'system') {
        return solarSystemData;
    }
    return constellations.value;
});

const selectItem = (item: any) => {
    if (currentMode.value === 'system') {
        // 行星模式
        focusTarget(item);
    } else {
        // 星空模式 - 聚焦到星座
        selectedConstellation.value = item.id;
        focusConstellation(item.id);
        console.log(`✨ 选中星座: ${item.name}`);
    }
};

// 加载星座列表
onMounted(() => {
    setTimeout(() => {
        constellations.value = getConstellations();
        console.log('📋 星座列表已加载:', constellations.value);
    }, 3500); // 等待模型加载完成
});

const nebulaOptions: { label: string; value: NebulaType }[] = [
    { label: 'Spiral', value: 'spiral' },
    { label: 'Filament', value: 'filament' },
    { label: 'Explosive', value: 'explosive' },
    { label: 'Layered', value: 'layered' },
    { label: 'Dark', value: 'dark' },
    { label: 'Purple Mist', value: 'purple' },
    { label: 'Deep Grid', value: 'deepspace' }
];
</script>

<template>
  <div class="side-nav-container">
    <!-- Top Navigation Panel -->
    <div class="nav-panel sr-glass-panel">
      <!-- Mode Switcher -->
      <div class="mode-tabs">
        <div 
          class="tab" 
          :class="{ active: currentMode === 'system' }"
          @click="setMode('system')"
        >
          PLANETS
        </div>
        <div 
          class="tab" 
          :class="{ active: currentMode === 'starry' }"
          @click="setMode('starry')"
        >
          STARS
        </div>
      </div>

      <!-- Scrollable List -->
      <div class="list-container sr-scroll">
        <!-- 行星模式 -->
        <template v-if="currentMode === 'system'">
          <div 
            v-for="item in currentList" 
            :key="item.id"
            class="list-item"
            :class="{ active: selectedObject && selectedObject.id === item.id }"
            @click="selectItem(item)"
          >
            <div class="item-name">{{ (item as any).name || item.id }}</div>
            <div class="item-id">{{ item.id }}</div>
          </div>
        </template>
        
        <!-- 星空模式 - 星座列表 -->
        <template v-else>
          <div v-if="constellations.length === 0" class="loading-hint">
            <div class="loading-spinner"></div>
            <div class="loading-text">加载星座模型中...</div>
          </div>
          <div 
            v-for="item in currentList" 
            :key="item.id"
            class="list-item constellation-item"
            :class="{ active: selectedConstellation === item.id }"
            @click="selectItem(item)"
          >
            <div class="constellation-icon">✨</div>
            <div class="item-content">
              <div class="item-name">{{ item.name }}</div>
              <div class="item-id">{{ item.id }}</div>
            </div>
          </div>
        </template>
      </div>
    </div>

    <!-- Bottom Nebula Settings -->
    <div class="nebula-panel sr-glass-panel">
      <div class="panel-title">NEBULA STYLE</div>
      <div class="nebula-grid">
        <div 
          v-for="opt in nebulaOptions" 
          :key="opt.value"
          class="nebula-chip"
          :class="{ active: currentNebula === opt.value }"
          @click="setNebula(opt.value)"
        >
          {{ opt.label }}
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.side-nav-container {
  position: absolute;
  top: 50%;
  left: 24px;
  transform: translateY(-50%);
  display: flex;
  flex-direction: column;
  gap: 16px;
  z-index: 10;
}

.nav-panel {
  width: 240px;
  height: 50vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.nebula-panel {
  width: 240px;
  padding: 16px;
}

.panel-title {
  font-size: 10px;
  color: var(--sr-text-secondary);
  letter-spacing: 1px;
  margin-bottom: 12px;
  font-weight: 600;
}

.nebula-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.nebula-chip {
  font-size: 11px;
  padding: 6px 10px;
  border-radius: 4px;
  background: rgba(255,255,255,0.05);
  border: 1px solid transparent;
  cursor: pointer;
  transition: all 0.2s;
  color: var(--sr-text-secondary);
}

.nebula-chip:hover {
  background: rgba(255,255,255,0.1);
  color: var(--sr-text-primary);
}

.nebula-chip.active {
  background: rgba(68, 170, 255, 0.15);
  border-color: var(--sr-accent-color);
  color: var(--sr-accent-color);
  box-shadow: 0 0 8px rgba(68, 170, 255, 0.2);
}

/* Existing styles */
.mode-tabs {
  display: flex;
  border-bottom: 1px solid var(--sr-border-glass);
}

.tab {
  flex: 1;
  text-align: center;
  padding: 16px 0;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 1px;
  cursor: pointer;
  color: var(--sr-text-secondary);
  transition: all 0.3s;
}

.tab:hover {
  color: var(--sr-text-primary);
  background: rgba(255,255,255,0.05);
}

.tab.active {
  color: var(--sr-accent-color);
  background: rgba(68, 170, 255, 0.1);
  box-shadow: inset 0 -2px 0 var(--sr-accent-color);
}

.list-container {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

.list-item {
  padding: 12px 16px;
  border-radius: 6px;
  cursor: pointer;
  margin-bottom: 4px;
  transition: all 0.2s;
}

.list-item:hover {
  background: rgba(255,255,255,0.08);
}

.list-item.active {
  background: rgba(68, 170, 255, 0.2);
  border: 1px solid rgba(68, 170, 255, 0.3);
}

.item-name {
  font-size: 14px;
  font-weight: 500;
}

.item-id {
  font-size: 10px;
  text-transform: uppercase;
  color: var(--sr-text-secondary);
  margin-top: 2px;
}

/* 星座列表样式 */
.constellation-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.constellation-icon {
  font-size: 18px;
  flex-shrink: 0;
}

.item-content {
  flex: 1;
  min-width: 0;
}

.constellation-item .item-name {
  font-size: 13px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.constellation-item.active {
  background: rgba(255, 215, 0, 0.15);
  border: 1px solid rgba(255, 215, 0, 0.3);
  box-shadow: 0 0 12px rgba(255, 215, 0, 0.2);
}

.constellation-item.active .constellation-icon {
  animation: sparkle 1.5s infinite;
}

@keyframes sparkle {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.6; transform: scale(1.2); }
}

/* 加载提示 */
.loading-hint {
  padding: 24px;
  text-align: center;
  color: var(--sr-text-secondary);
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid rgba(255,255,255,0.1);
  border-top-color: var(--sr-accent-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 12px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  font-size: 12px;
  color: var(--sr-text-secondary);
}
</style>
