<script setup lang="ts">
/**
 * Pro Tip: Place your video file in 'frontend/vue-app/public/videos/star-bg.mp4'
 * This allows you to reference it with a simple absolute path.
 */
</script>

<template>
  <div class="star-container">
    <video 
      autoplay 
      muted 
      loop 
      playsinline 
      class="bg-video"
    >
      <source src="/videos/star_bg.mp4" type="video/mp4" />
      Your browser does not support the video tag.
    </video>

    <div class="video-overlay"></div>
    
    <div class="content-overlay">
      <slot></slot>
    </div>
  </div>
</template>

<style scoped>
.star-container {
  min-height: 100vh;
  width: 100%;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow-x: hidden; /* allow vertical growth/scroll; only clip horizontal */
  background-color: var(--color-bg-deep); /* Fallback color */
}

.bg-video {
  position: fixed; /* keep video anchored to viewport even when page scrolls */
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover; /* This ensures the video fills the screen without stretching */
  transform: none;
  z-index: 1;
}

.video-overlay {
  position: fixed; /* keep overlay anchored together with video */
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.4); /* Adjust opacity to make your forms pop */
  z-index: 2;
}

.content-overlay {
  position: relative;
  z-index: 10;
  width: 100%;
  display: flex;
  justify-content: center;
  padding: 20px;
}
</style>