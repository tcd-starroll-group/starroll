<script setup lang="ts">
import BaseButton from '../components/BaseButton.vue'
import StarBackground from '@/components/StarBackground.vue'
import { ref, reactive } from 'vue'
import '../assets/styles/common.css'
import '../assets/styles/input.css'
import { defaultApi } from '@/api/defaultApi'
import { ResponseError } from '../../../../gen/ts/runtime'
import { useRouter } from 'vue-router';

// TypeScript interfaces for type safety
interface LoginState {
  username: string;
  password: string;
  rememberMe: boolean;
}

// Reactive form state
const form = reactive<LoginState>({
  username: '',
  password: '',
  rememberMe: false
});

const isLoading = ref(false);
const errorMessage = ref('');
const router = useRouter();

// Handle Login Logic
const handleLogin = async () => {
  if (!form.username || !form.password) {
    errorMessage.value = "Please fill in all cosmic coordinates (fields).";
    return;
  }

  isLoading.value = true;
  errorMessage.value = '';

  try {
    const response = await defaultApi.apiUserLoginPost({
      userAuth: {
        username: form.username,
        password: form.password,
      },
    });

    console.log("Logged in successfully:", form.username);

    console.log("Logged in successfully:", form.username);

    if (response.token) {
      localStorage.setItem('token', response.token);
    }
    
    if (response.userID) {
      localStorage.setItem('userID', String(response.userID));
      console.log("UserID saved from response:", response.userID);
    }
    
    localStorage.setItem('username', form.username);
    console.log("login! success");

    router.push('/profile');

  } catch (err: unknown) {
    if (err instanceof ResponseError && (err.response.status === 401 || err.response.status === 404)) {
      errorMessage.value = "Invalid username or password.";
    } else {
      errorMessage.value = "" + err;
    }
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
          <label>Star ID / username</label>
          <input 
            v-model="form.username" 
            type="username" 
            placeholder="pilot@starroll.com" 
            :disabled="isLoading"
          />
        </div>

        <div class="input-group">
          <label>Access Key</label>
          <input 
            v-model="form.password" 
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