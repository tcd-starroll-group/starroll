<script setup lang="ts">
import BaseButton from '../components/BaseButton.vue'
import StarBackground from '@/components/StarBackground.vue'
import { ref, reactive } from 'vue'
import '../assets/styles/common.css'
import '../assets/styles/input.css'

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
  
  </StarBackground>
</template>

<style scoped>

</style>