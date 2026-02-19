<script setup lang="ts">
import { ref } from 'vue'
import BaseButton from '@/components/BaseButton.vue'
import StarBackground from '@/components/StarBackground.vue'
import '../assets/styles/common.css'
import '../assets/styles/input.css'

// 1. Logic State
const email = ref('')
const isLoading = ref(false)
const isSent = ref(false) // Toggles between the form and success message
const errorMessage = ref('')

// 2. Handle Reset Request
const handleResetRequest = async () => {
  if (!email.value) {
    errorMessage.value = "Please provide your Star ID coordinates (email)."
    return
  }

  isLoading.value = true
  errorMessage.value = ''

  try {
    // Simulate API Call to backend
    await new Promise((resolve) => setTimeout(resolve, 2000))
    console.log("Reset link transmitted to:", email.value)
    isSent.value = true
  } catch (err) {
    errorMessage.value = "Terminal error. Could not establish connection."
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <StarBackground>
    <div class="stars"></div>

    <div class="login-card glass-panel">
      <div v-if="!isSent">
        <div class="header">
          <h1 class="title">RECOVER ACCESS</h1>
          <p class="subtitle">Lost in the void? We'll send a recovery signal to your Star ID.</p>
        </div>

        <form @submit.prevent="handleResetRequest" class="form">
          <div class="input-group">
            <label>Star ID / Email</label>
            <input 
              v-model="email" 
              type="email" 
              placeholder="pilot@starroll.com" 
              :disabled="isLoading"
              required
            />
          </div>

          <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>

          <BaseButton 
            type="submit" 
            :is-loading="isLoading"
            variant="primary"
          >
            Transmit Signal
          </BaseButton>
        </form>
      </div>

      <div v-else class="success-state">
        <div class="icon-circle">
          <span class="icon">🛰️</span>
        </div>
        <h2 class="title">SIGNAL SENT</h2>
        <p class="subtitle">
          Check your communications relay for <strong>{{ email }}</strong> to reset your access key.
        </p>
        <BaseButton variant="outline" @click="isSent = false">
          Back to Terminal
        </BaseButton>
      </div>

      <div class="footer-links">
        <a href="/login">Return to Login</a>
      </div>
    </div>
  </StarBackground>
</template>

<style scoped>


/* Form Styles */
.form {
  text-align: left;
}

/* Success State Styles */
.success-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.icon-circle {
  width: 64px;
  height: 64px;
  background: rgba(88, 166, 255, 0.1);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1rem;
  border: 1px solid var(--color-star-primary);
}

.icon {
  font-size: 2rem;
}

</style>