<script setup lang="ts">
import BaseButton from '../components/BaseButton.vue'
import StarBackground from '@/components/StarBackground.vue'
import { ref, reactive } from 'vue'

// TypeScript interfaces for type safety
interface LoginState {
  email: string;
  pass: string;
  rememberMe: boolean;
}

// Reactive form state
const form = reactive<LoginState>({
  email: '',
  pass: '',
  rememberMe: false
});

const isLoading = ref(false);
const errorMessage = ref('');

// Handle Login Logic
const handleLogin = async () => {
  if (!form.email || !form.pass) {
    errorMessage.value = "Please fill in all cosmic coordinates (fields).";
    return;
  }

  isLoading.value = true;
  errorMessage.value = '';

  try {
    // Simulate API Call
    await new Promise((resolve) => setTimeout(resolve, 1500));
    console.log("Logged in successfully:", form.email);
  } catch (err) {
    errorMessage.value = "Unauthorized. Check your Star ID.";
  } finally {
    isLoading.value = false;
  }
};
</script>

<template>
  <StarBackground>
  <div class="login-page">
    <div class="stars"></div>

    <div class="login-card glass-panel">
      <div class="header">
        <h1 class="title">STARROLL</h1>
        <p class="subtitle">Enter the cosmic gateway</p>
      </div>

      <form @submit.prevent="handleLogin" class="form">
        <div class="input-group">
          <label>Star ID / Email</label>
          <input 
            v-model="form.email" 
            type="email" 
            placeholder="pilot@starroll.com" 
            :disabled="isLoading"
          />
        </div>

        <div class="input-group">
          <label>Access Key</label>
          <input 
            v-model="form.pass" 
            type="password" 
            placeholder="••••••••" 
            :disabled="isLoading"
          />
        </div>

        <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>

        <BaseButton 
          type="submit" 
          :is-loading="isLoading"
          variant="primary"
        >
          Initiate Roll
        </BaseButton>
      </form>

      <div class="footer-links">
        <a href="/password-reset">Forgot Coordinates?</a>
        <span>|</span>
        <a href="/register">Join the Fleet</a>
      </div>
    </div>
  </div>
  </StarBackground>
</template>

<style scoped>
/* REMOVED: background colors, fonts, and button styles 
   inherited from main.css and BaseButton.vue 
*/

.login-page {
  min-height: 70vh;
  display: flex;
  align-items: center;
  justify-content: center;
  /* Use variable from main.css */
  background: radial-gradient(circle at center, #1b2735 0%, var(--color-bg-deep) 100%);
  overflow: hidden;
  position: relative;
}

.login-card {
  padding: 3rem;
  border-radius: 24px;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
  z-index: 10;
  /* glass-panel properties now come from main.css */
}

.title {
  color: var(--color-text-main);
  letter-spacing: 4px;
  font-weight: 800;
  margin: 0;
  text-align: center;
}

.subtitle {
  color: var(--color-text-muted);
  text-align: center;
  font-size: 0.9rem;
  margin-bottom: 2rem;
}

.input-group {
  margin-bottom: 1.5rem;
}

.input-group label {
  display: block;
  color: var(--color-star-primary);
  font-size: 0.8rem;
  margin-bottom: 0.5rem;
  text-transform: uppercase;
  font-weight: bold;
}

.input-group input {
  width: 100%;
  padding: 12px 16px;
  background: rgba(0, 0, 0, 0.3);
  border: var(--glass-border);
  border-radius: 8px;
  color: white;
  transition: all 0.3s ease;
}

.input-group input:focus {
  outline: none;
  border-color: var(--color-star-primary);
  background: rgba(0, 0, 0, 0.5);
}

.error-text {
  color: var(--color-error);
  font-size: 0.85rem;
  margin-bottom: 1rem;
  text-align: center;
}

.footer-links {
  margin-top: 2rem;
  display: flex;
  justify-content: center;
  gap: 10px;
  font-size: 0.8rem;
}

.footer-links a {
  color: var(--color-star-primary);
  text-decoration: none;
}
</style>