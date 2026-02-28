<script setup lang="ts">
import { ref, reactive } from 'vue'
import BaseButton from '@/components/BaseButton.vue'
import StarBackground from '@/components/StarBackground.vue'
import '../assets/styles/common.css'
import '../assets/styles/input.css'
import { registerApi } from '@/api/auth';
import { useRouter } from 'vue-router';

// 1. TypeScript interface for Registration
interface RegisterState {
  username: string;
  email: string;
  password: string;
  confirmPass: string;
}

// 2. Reactive form state
const form = reactive<RegisterState>({
  username: '',
  email: '',
  password: '',
  confirmPass: ''
});

const isLoading = ref(false);
const errorMessage = ref('');
const router = useRouter();

// 3. Handle Registration Logic
const handleRegister = async () => {
  // Basic Validations
  if (!form.username || !form.email || !form.password || !form.confirmPass) {
    errorMessage.value = "All cosmic coordinates are required.";
    return;
  }

  if (form.password !== form.confirmPass) {
    errorMessage.value = "Access keys do not match.";
    return;
  }

  isLoading.value = true;
  errorMessage.value = '';

  try {
    const response = await registerApi({
    username: form.username,
    password: form.password,
    email: form.email
    });

    localStorage.setItem('token', response.data.token);
    console.log("Registration successful:", form.username);

    if (response.status === 201) {
      console.log("login! success");
      router.push('/profile'); 
    }
    else if (response.status === 409) {
      errorMessage.value = "Username taken.";
    }


  } catch (err) {
    errorMessage.value = "Signal interference. Try a different Star ID.";
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
            v-model="form.password" 
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
        <a href="/userLogin">Login here</a>
      </div>
    </div>
  </StarBackground>
</template>

<style scoped>

.form {
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
}

</style>