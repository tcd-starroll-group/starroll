<script setup lang="ts">
import { useMultiLayer } from '../composables/useMultiLayer';
import { solarSystemData } from '@/core/data/planets';
import { constellationModels } from '@/core/data/constellation-models';
import { computed, ref } from 'vue';

const { 
    currentMode,
    selectPlanet,
    backToOverview,
    selectedPlanet,
    selectedConstellation,
    showConstellations,
    toggleConstellations
} = useMultiLayer();

// 视图模式（PLANETS / STARS）
const currentTab = ref<'system' | 'starry'>('system');

// 当前显示的列表
const currentList = computed(() => {
    if (currentTab.value === 'system') {
        return solarSystemData;
    }
    return constellationModels;
});

const selectItem = (item: any) => {
    if (currentMode.value === 'explore') {
        // 探索模式下点击返回概览
        backToOverview();
        return;
    }
    
    if (currentTab.value === 'system') {
        // 行星模式 - 进入探索模式
        selectPlanet(item);
    } else {
        // 星空模式 - 选中星座
        selectedConstellation.value = item.id;
        console.log(`✨ 选中星座: ${item.name}`);
    }
};
</script>

<template>
  <div class="side-nav-container">
    <!-- Top Navigation Panel -->
    <div class="nav-panel sr-glass-panel">
      <!-- 模式指示器 (探索模式) -->
      <div v-if="currentMode === 'explore'" class="mode-indicator">
        <div class="indicator-badge">🔍 EXPLORE MODE</div>
        <button class="back-button" @click="backToOverview">
          ← 返回概览
        </button>
      </div>
      
      <!-- Mode Tabs (概览模式) -->
      <div v-if="currentMode === 'overview'" class="mode-tabs">
        <div 
          class="tab" 
          :class="{ active: currentTab === 'system' }"
          @click="currentTab = 'system'"
        >
          PLANETS
        </div>
        <div 
          class="tab" 
          :class="{ active: currentTab === 'starry' }"
          @click="currentTab = 'starry'"
        >
          STARS
        </div>
      </div>

      <!-- Scrollable List -->
      <div class="list-container sr-scroll">
        <!-- 探索模式提示 -->
        <div v-if="currentMode === 'explore' && selectedPlanet" class="explore-info">
          <div class="explore-title">{{ selectedPlanet.name }}</div>
          <div class="explore-hint">查看行星详细信息</div>
        </div>
        
        <!-- 概览模式列表 -->
        <template v-else>
          <!-- 行星列表 -->
          <template v-if="currentTab === 'system'">
            <div 
              v-for="item in currentList" 
              :key="item.id"
              class="list-item planet-item"
              :class="{ active: selectedPlanet && selectedPlanet.id === item.id }"
              @click="selectItem(item)"
            >
              <div class="planet-icon">🪐</div>
              <div class="item-content">
                <div class="item-name">{{ (item as any).name }}</div>
                <div class="item-id">{{ item.id }}</div>
              </div>
              <div class="explore-arrow">→</div>
            </div>
          </template>
          
          <!-- 星座列表 -->
          <template v-else>
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
        </template>
      </div>
    </div>

    <!-- Bottom Settings Panel (概览模式) -->
    <div v-if="currentMode === 'overview'" class="settings-panel sr-glass-panel">
      <div class="panel-title">显示设置</div>
      <div class="setting-item">
        <span class="setting-label">星座模型</span>
        <label class="toggle-switch">
          <input type="checkbox" :checked="showConstellations" @change="toggleConstellations">
          <span class="slider"></span>
        </label>
      </div>
    </div>
    
    <!-- Stats Panel (探索模式) -->
    <div v-if="currentMode === 'explore'" class="stats-panel sr-glass-panel">
      <div class="panel-title">详细信息</div>
      <div v-if="selectedPlanet" class="planet-details">
        <div class="detail-row">
          <span class="label">名称:</span>
          <span class="value">{{ selectedPlanet.name }}</span>
        </div>
        <div class="detail-row">
          <span class="label">半径:</span>
          <span class="value">{{ selectedPlanet.radius }} km</span>
        </div>
        <div class="detail-row">
          <span class="label">轨道:</span>
          <span class="value">{{ selectedPlanet.orbitRadius }} AU</span>
        </div>
        <div class="detail-row">
          <span class="label">周期:</span>
          <span class="value">{{ selectedPlanet.orbitPeriod }} 天</span>
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

.settings-panel, .stats-panel {
  width: 240px;
  padding: 16px;
}

/* 模式指示器 */
.mode-indicator {
  padding: 12px 16px;
  border-bottom: 1px solid var(--sr-border-glass);
}

.indicator-badge {
  font-size: 10px;
  color: var(--sr-accent-color);
  letter-spacing: 1.5px;
  font-weight: 600;
  margin-bottom: 8px;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

.back-button {
  width: 100%;
  padding: 8px;
  background: rgba(68, 170, 255, 0.1);
  border: 1px solid rgba(68, 170, 255, 0.3);
  border-radius: 4px;
  color: var(--sr-accent-color);
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s;
}

.back-button:hover {
  background: rgba(68, 170, 255, 0.2);
  box-shadow: 0 0 8px rgba(68, 170, 255, 0.3);
}

/* 探索模式信息 */
.explore-info {
  padding: 24px;
  text-align: center;
}

.explore-title {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 12px;
  color: var(--sr-text-primary);
}

.explore-hint {
  font-size: 11px;
  color: var(--sr-text-secondary);
  opacity: 0.7;
}

/* Mode Tabs */
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

/* List Container */
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
  display: flex;
  align-items: center;
  gap: 12px;
}

.list-item:hover {
  background: rgba(255,255,255,0.08);
  transform: translateX(4px);
}

.list-item.active {
  background: rgba(255, 215, 0, 0.15);
  border: 1px solid rgba(255, 215, 0, 0.3);
  box-shadow: 0 0 12px rgba(255, 215, 0, 0.2);
}

/* 行星列表 */
.planet-item .planet-icon {
  font-size: 20px;
  flex-shrink: 0;
}

.planet-item .explore-arrow {
  margin-left: auto;
  color: var(--sr-accent-color);
  opacity: 0;
  transition: opacity 0.2s;
  font-size: 16px;
}

.planet-item:hover .explore-arrow {
  opacity: 1;
  animation: bounce-right 1s infinite;
}

@keyframes bounce-right {
  0%, 100% { transform: translateX(0); }
  50% { transform: translateX(4px); }
}

/* 星座列表 */
.constellation-item {
  display: flex;
  align-items: center;
}

.constellation-icon {
  font-size: 18px;
  flex-shrink: 0;
}

.item-content {
  flex: 1;
  min-width: 0;
}

.item-name {
  font-size: 14px;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.item-id {
  font-size: 10px;
  text-transform: uppercase;
  color: var(--sr-text-secondary);
  margin-top: 2px;
}

.constellation-item.active .constellation-icon {
  animation: sparkle 1.5s infinite;
}

@keyframes sparkle {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.6; transform: scale(1.2); }
}

/* Settings Panel */
.panel-title {
  font-size: 10px;
  color: var(--sr-text-secondary);
  letter-spacing: 1px;
  margin-bottom: 12px;
  font-weight: 600;
  text-transform: uppercase;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid rgba(255,255,255,0.05);
}

.setting-label {
  font-size: 12px;
  color: var(--sr-text-primary);
}

/* Toggle Switch */
.toggle-switch {
  position: relative;
  width: 44px;
  height: 24px;
  display: inline-block;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255,255,255,0.1);
  border-radius: 24px;
  transition: .3s;
  border: 1px solid rgba(255,255,255,0.1);
}

.slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 2px;
  background-color: white;
  border-radius: 50%;
  transition: .3s;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

input:checked + .slider {
  background-color: var(--sr-accent-color);
  border-color: var(--sr-accent-color);
}

input:checked + .slider:before {
  transform: translateX(20px);
}

.slider:hover {
  background-color: rgba(255,255,255,0.15);
}

input:checked + .slider:hover {
  background-color: rgba(68, 170, 255, 0.8);
}

/* Stats Panel */
.planet-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid rgba(255,255,255,0.05);
}

.detail-row:last-child {
  border-bottom: none;
}

.detail-row .label {
  font-size: 11px;
  color: var(--sr-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.detail-row .value {
  font-size: 13px;
  color: var(--sr-text-primary);
  font-weight: 500;
}
</style>
