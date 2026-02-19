<script setup lang="ts">
import { useStarRoll } from '../composables/useStarRoll';
import { computed } from 'vue';

const { selectedObject } = useStarRoll();

// 类型守卫辅助
const isPlanet = (obj: any): boolean => !!obj.radius;
const isConstellation = (obj: any): boolean => !!obj.shapeId;

const info = computed(() => {
    if (!selectedObject.value) return null;
    const obj = selectedObject.value;
    
    if (isPlanet(obj)) {
        const p = obj as any;
        return {
            title: p.name,
            subtitle: 'SOLAR SYSTEM PLANET',
            desc: `Orbit: ${p.orbitRadius} AU | Period: ${p.orbitPeriod} Yr`,
            details: [
                { label: 'Radius', value: p.radius + ' Earths' },
                { label: 'Day Length', value: p.rotationPeriod + ' Days' },
                { label: 'Type', value: p.type.toUpperCase() }
            ]
        };
    } else if (isConstellation(obj)) {
        const c = obj as any;
        return {
            title: c.name.zh,
            subtitle: c.name.en.toUpperCase(),
            desc: c.description || 'No description available.',
            details: [
                { label: 'Shape', value: c.shapeId.toUpperCase() },
                { label: 'Stars', value: c.stars.length },
                { label: 'RA/Dec', value: `${c.center.ra}° / ${c.center.dec}°` }
            ]
        };
    }
    return null;
});
</script>

<template>
  <Transition name="fade-slide">
    <div v-if="info" class="info-panel sr-glass-panel">
      <div class="header">
        <div class="subtitle">{{ info.subtitle }}</div>
        <div class="title">{{ info.title }}</div>
      </div>
      
      <div class="divider"></div>
      
      <div class="description">
        {{ info.desc }}
      </div>
      
      <div class="details-grid">
        <div v-for="(item, idx) in info.details" :key="idx" class="detail-item">
          <div class="label">{{ item.label }}</div>
          <div class="value">{{ item.value }}</div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.info-panel {
  position: absolute;
  top: 50%;
  right: 24px;
  transform: translateY(-50%);
  width: 280px;
  padding: 24px;
  z-index: 10;
}

.header {
    margin-bottom: 16px;
}
.subtitle {
    font-size: 10px;
    letter-spacing: 2px;
    color: var(--sr-accent-color);
    margin-bottom: 4px;
}
.title {
    font-size: 32px;
    font-weight: 300;
}

.divider {
    height: 1px;
    background: var(--sr-border-glass);
    margin: 16px 0;
}

.description {
    font-size: 13px;
    line-height: 1.6;
    color: var(--sr-text-secondary);
    margin-bottom: 24px;
}

.details-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
}

.label {
    font-size: 10px;
    color: var(--sr-text-secondary);
    text-transform: uppercase;
}
.value {
    font-size: 14px;
    font-weight: 500;
    margin-top: 2px;
}

/* Transition */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

.fade-slide-enter-from,
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-40%);
}
</style>

