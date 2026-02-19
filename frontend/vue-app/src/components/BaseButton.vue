<script setup lang="ts">
// Define what "inputs" this button can take
interface Props {
  type?: 'button' | 'submit' | 'reset';
  variant?: 'primary' | 'secondary' | 'outline';
  isLoading?: boolean;
  disabled?: boolean;
}

// Set default values for the props
withDefaults(defineProps<Props>(), {
  type: 'button',
  variant: 'primary',
  isLoading: false,
  disabled: false
});
</script>

<template>
  <button 
    :type="type" 
    :disabled="disabled || isLoading"
    class="base-button"
    :class="[variant, { 'is-loading': isLoading }]"
  >
    <span v-if="isLoading" class="loader"></span>
    <slot v-else></slot>
  </button>
</template>

<style scoped>
.base-button {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 12px 24px;
  font-size: 1rem;
  font-weight: 600;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
  color: white;
  width: 100%; /* Default to full width for mobile-first auth */
}

/* Variant Styles */
.primary {
  background: linear-gradient(45deg, var(--color-star-primary), var(--color-star-secondary));
}

.primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: var(--shadow-glow);
}

.outline {
  background: transparent;
  border: 1px solid var(--color-star-primary);
  color: var(--color-star-primary);
}

/* Loading/Disabled States */
.base-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  filter: grayscale(0.5);
}

.loader {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: #fff;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>