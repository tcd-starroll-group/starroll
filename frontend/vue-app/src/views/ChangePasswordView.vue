<script setup lang="ts">
import { ref, reactive } from 'vue'
import BaseButton from '../components/BaseButton.vue'
import { changePasswordApi } from '@/api/auth' 
import '../assets/styles/input.css'

// 定义组件事件：用于点击“返回”或“成功后关闭”
const emit = defineEmits(['back', 'success'])

// 1. 响应式表单状态，读取 oldPassword 和 newPassword
const form = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: '' // 增加确认密码以提升安全性
})

const isLoading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

// 2. 处理修改密码逻辑
const handleChangePassword = async () => {
  // 基础校验
  if (!form.oldPassword || !form.newPassword || !form.confirmPassword) {
    errorMessage.value = "Please fill in all required fields."
    return
  }
  
  if (form.newPassword !== form.confirmPassword) {
    errorMessage.value = "New password and confirmation do not match."
    return
  }

  isLoading.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    // 调用 API。由于 requests.ts 拦截器已配置，请求会自动携带 Token
    const response = await changePasswordApi({
      oldPassword: form.oldPassword,
      newPassword: form.newPassword
    })

    if (response.status === 200) {
      successMessage.value = "密钥修改成功，正在同步..."
      console.log("Password updated successfully")
      
      // 延迟关闭或跳转，让用户看清成功提示
      setTimeout(() => {
        emit('success')
      }, 1500)
    }
  } catch (err: any) {
    // 依据之前讨论的报错逻辑提取错误信息
    errorMessage.value = err.response?.data?.message || "密钥修改失败，请检查旧密钥。"
    console.error("Update failed:", err)
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="change-password-card glass-panel">
    <div class="header">
      <h2 class="title">SECURITY</h2>
      <p class="subtitle">Update your cosmic access keys</p>
    </div>

    <form @submit.prevent="handleChangePassword" class="form">
      <div class="input-group">
        <label>Current Access Key (Old)</label>
        <input 
          v-model="form.oldPassword" 
          type="password" 
          placeholder="••••••••" 
          :disabled="isLoading"
        />
      </div>

      <div class="input-group">
        <label>New Access Key</label>
        <input 
          v-model="form.newPassword" 
          type="password" 
          placeholder="••••••••" 
          :disabled="isLoading"
        />
      </div>

      <div class="input-group">
        <label>Confirm New Key</label>
        <input 
          v-model="form.confirmPassword" 
          type="password" 
          placeholder="••••••••" 
          :disabled="isLoading"
        />
      </div>

      <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>
      <p v-if="successMessage" class="success-text">{{ successMessage }}</p>

      <div class="actions">
        <BaseButton 
          type="submit" 
          :is-loading="isLoading"
          variant="primary"
        >
          Update Key
        </BaseButton>
        
        <BaseButton 
          type="button" 
          variant="outline" 
          @click="$emit('back')"
          :disabled="isLoading"
        >
          Back to Settings
        </BaseButton>
      </div>
    </form>
  </div>
</template>

<style scoped>
.change-password-card {
  padding: 30px;
  width: 100%;
  max-width: 400px;
  margin: 0 auto;
}

.title {
  font-size: 1.5rem;
  letter-spacing: 2px;
  margin-bottom: 4px;
}

.subtitle {
  color: var(--color-text-muted);
  font-size: 0.85rem;
  margin-bottom: 24px;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 20px;
  text-align: left;
}

.actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 10px;
}

.success-text {
  color: #00ff88;
  font-size: 0.85rem;
  margin: 0;
}

.error-text {
  color: #ff4d4d;
  font-size: 0.85rem;
  margin: 0;
}
</style>