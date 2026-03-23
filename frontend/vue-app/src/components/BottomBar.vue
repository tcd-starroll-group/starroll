<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router';
import { computed } from 'vue';
import '../assets/styles/common.css';
import '../assets/styles/main.css';

const router = useRouter();
const route = useRoute();

// Define bottom navigation modules
const navItems = [
  { 
    id: 'ar', 
    name: 'AR', 
    path: '/', 
    // Planet/AR icon
    icon: 'M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z' 
  },
  { 
    id: 'explore', 
    name: 'Explore', 
    // Assume your feature list page route is /explore
    path: '/explore', 
    // Compass/Discover icon
    icon: 'M12 10.9c-.61 0-1.1.49-1.1 1.1s.49 1.1 1.1 1.1c.61 0 1.1-.49 1.1-1.1s-.49-1.1-1.1-1.1zM12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm2.19 12.19L6 18l3.81-8.19L18 6l-3.81 8.19z' 
  },
  { 
    id: 'chats', 
    name: 'Chats', 
    path: '/chats', 
    // Chat bubble icon
    icon: 'M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z' 
  },
  { 
    id: 'profile', 
    name: 'Profile', 
    path: '/profile', 
    // Profile icon
    icon: 'M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z' 
  }
];

// Calculate the currently active navigation item
const activeNav = computed(() => {
  return route.path;
});

const navigateTo = (path: string) => {
  if (route.path !== path) {
    router.push(path);
  }
};
</script>

<template>
  <nav class="bottom-bar glass-panel">
    <div 
      v-for="nav in navItems" 
      :key="nav.id"
      class="nav-item"
      :class="{ active: activeNav === nav.path }"
      @click="navigateTo(nav.path)"
      :aria-label="nav.name"
    >
      <div class="icon-wrapper">
        <svg viewBox="0 0 24 24" width="26" height="26">
          <path fill="currentColor" :d="nav.icon" />
        </svg>
      </div>
      <div v-if="activeNav === nav.path" class="nav-indicator"></div>
    </div>
  </nav>
</template>

<style scoped>
.bottom-bar {
  position: fixed;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  /* Adapt to mobile, limit max width on desktop */
  width: calc(100% - 48px);
  max-width: 400px; 
  height: 68px;
  border-radius: 34px; /* Capsule shape */
  display: flex;
  justify-content: space-around;
  align-items: center;
  padding: 0 16px;
  z-index: 999; /* Ensure floating above all content */
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4), inset 0 0 0 1px rgba(255, 255, 255, 0.05);
}

.nav-item {
  position: relative;
  width: 56px;
  height: 56px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: var(--color-text-muted); /* Default gray */
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Active state: icon turns blue, slightly enlarged and glowing */
.nav-item.active {
  color: var(--color-star-primary);
}

.icon-wrapper {
  transition: transform 0.3s;
}

.nav-item:hover .icon-wrapper {
  transform: translateY(-2px);
  color: rgba(255, 255, 255, 0.9);
}

.nav-item.active .icon-wrapper {
  transform: translateY(-4px);
  filter: drop-shadow(0 0 8px rgba(88, 166, 255, 0.6));
}

/* Bottom glowing dot */
.nav-indicator {
  position: absolute;
  bottom: 6px;
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background-color: var(--color-star-primary);
  box-shadow: 0 0 10px 2px var(--color-star-primary);
  animation: popIn 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
}

@keyframes popIn {
  0% { transform: scale(0); opacity: 0; }
  100% { transform: scale(1); opacity: 1; }
}
</style>