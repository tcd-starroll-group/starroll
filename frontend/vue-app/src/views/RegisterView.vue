<script setup lang="ts">
import { ref, reactive } from 'vue'
import BaseButton from '@/components/BaseButton.vue'
import StarBackground from '@/components/StarBackground.vue'

// 1. TypeScript interface for Registration
interface RegisterState {
  username: string;
  email: string;
  pass: string;
  confirmPass: string;
}

// 2. Reactive form state
const form = reactive<RegisterState>({
  username: '',
  email: '',
  pass: '',
  confirmPass: ''
});

const isLoading = ref(false);
const errorMessage = ref('');

// 3. Handle Registration Logic
const handleRegister = async () => {
  // Basic Validations
  if (!form.username || !form.email || !form.pass || !form.confirmPass) {
    errorMessage.value = "All cosmic coordinates are required.";
    return;
  }

  if (form.pass !== form.confirmPass) {
    errorMessage.value = "Access keys do not match.";
    return;
  }

  isLoading.value = true;
  errorMessage.value = '';

  try {
    // Simulate API Call to create user
    await new Promise((resolve) => setTimeout(resolve, 2000));
    console.log("Registered new pilot:", form.username);
    // Redirect logic: router.push('/login')
  } catch (err) {
    errorMessage.value = "Signal interference. Try a different Star ID.";
  } finally {
    isLoading.value = false;
  }
};
</script>

<template>
  <StarBackground>
  <div class="register-page">
    <div class="stars"></div>

    <div class="register-card glass-panel">
      <div class="header">
        <h1 class="title">JOIN THE FLEET</h1>
        <p class="subtitle">Create your unique Star Identity</p>
      </div>

      <form @submit.prevent="handleRegister" class="form">
        <div class="input-group">
          <label>Pilot Name</label>
          <input 
            v-model="form.username" 
            type="text" 
            placeholder="e.g. StarLord77" 
            :disabled="isLoading"
          />
        </div>

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
            placeholder="Create password" 
            :disabled="isLoading"
          />
        </div>

        <div class="input-group">
          <label>Confirm Key</label>
          <input 
            v-model="form.confirmPass" 
            type="password" 
            placeholder="Repeat password" 
            :disabled="isLoading"
          />
        </div>

        <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>

        <BaseButton 
          type="submit" 
          :is-loading="isLoading"
          variant="primary"
        >
          Authorize Vessel
        </BaseButton>
      </form>

      <div class="footer-links">
        <span>Already in the fleet?</span>
        <a href="/login">Login here</a>
      </div>
    </div>
  </div>
  </StarBackground>
</template>

<style scoped>
/* Inheriting structural layout from main.css */

.register-page {
  min-height: 70vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: radial-gradient(circle at center, #1b2735 0%, var(--color-bg-deep) 100%);
  overflow: hidden;
  position: relative;
}

.register-card {
  padding: 2.5rem 3rem;
  border-radius: 24px;
  width: 100%;
  max-width: 450px; /* Slightly wider for form clarity */
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
  z-index: 10;
}

.title {
  color: var(--color-text-main);
  letter-spacing: 2px;
  font-weight: 800;
  text-align: center;
}

.subtitle {
  color: var(--color-text-muted);
  text-align: center;
  font-size: 0.9rem;
  margin-bottom: 1.5rem;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
}

.input-group label {
  display: block;
  color: var(--color-star-primary);
  font-size: 0.75rem;
  margin-bottom: 0.4rem;
  text-transform: uppercase;
  font-weight: bold;
  letter-spacing: 1px;
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
  text-align: center;
}

.footer-links {
  margin-top: 1.5rem;
  text-align: center;
  font-size: 0.85rem;
  color: var(--color-text-muted);
}

.footer-links a {
  color: var(--color-star-primary);
  text-decoration: none;
  margin-left: 5px;
  font-weight: bold;
}

</style>