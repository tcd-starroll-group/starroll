<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import StarBackground from '@/components/StarBackground.vue'
import BaseButton from '@/components/BaseButton.vue'
import { getProfileApi } from '@/api/auth';

const router = useRouter()
const isEditing = ref(false)

// 1. Mock Data / Form State
const pilotForm = reactive({
  name: '',
  email: '',
  dob: '',
  place: '',
  avatar: ''
})

onMounted(async () => {
  try {
    const response = await getProfileApi();
    if (response.status === 200) {
      // Pre-fill the form with the user's current data
      Object.assign(pilotForm, response.data);
    }
  } catch (err) {
    console.error("Transmission Interrupted: Could not fetch detailed logs.");
  }
})

const handleToggleEdit = () => {
  if (isEditing.value) {
    // Here you would call your update API: await updateProfileApi(pilotForm)
    console.log("Saving updated pilot data...", pilotForm)
  }
  isEditing.value = !isEditing.value
}
</script>

<template>
  <StarBackground>
    <div class="details-container">
      
      <section class="details-card glass-panel">
        <div class="details-header">
          <h2 class="section-title">
            {{ isEditing ? 'Modify Personnel File' : 'Personnel Credentials' }}
          </h2>
          <div class="id-line"></div>
        </div>

        <div class="info-grid">
          <div class="field">
            <label>Full Name / Callsign</label>
            <div v-if="!isEditing" class="view-mode">{{ pilotForm.name }}</div>
            <input v-else v-model="pilotForm.name" type="text" class="edit-input" />
          </div>

          <div class="field">
            <label>Comm-Link (Email)</label>
            <div v-if="!isEditing" class="view-mode">{{ pilotForm.email }}</div>
            <input v-else v-model="pilotForm.email" type="email" class="edit-input" />
          </div>

          <div class="field">
            <label>Origin Date (DOB)</label>
            <div v-if="!isEditing" class="view-mode">{{ pilotForm.dob || 'Not Recorded' }}</div>
            <input v-else v-model="pilotForm.dob" type="date" class="edit-input" />
          </div>

          <div class="field">
            <label>Home Base (Location)</label>
            <div v-if="!isEditing" class="view-mode">{{ pilotForm.place || 'Deep Space' }}</div>
            <input v-else v-model="pilotForm.place" type="text" class="edit-input" />
          </div>
        </div>

        <div class="details-actions">
          <BaseButton variant="outline" @click="router.back()">Back to Bridge</BaseButton>
          <BaseButton :variant="isEditing ? 'primary' : 'outline'" @click="handleToggleEdit">
            {{ isEditing ? 'Sync Changes' : 'Edit Credentials' }}
          </BaseButton>
        </div>
      </section>

    </div>
  </StarBackground>
</template>

<style scoped>
.details-container {
  width: 100%;
  max-width: 600px;
  padding: 60px 20px;
  margin: 0 auto;
}

.details-card {
  padding: 40px;
  border-radius: 24px;
  text-align: left;
}

.details-header {
  margin-bottom: 30px;
}

.section-title {
  font-size: 1.5rem;
  color: var(--color-text-main);
  margin-bottom: 8px;
}

.id-line {
  height: 2px;
  width: 50px;
  background: var(--color-star-primary);
}

.info-grid {
  display: flex;
  flex-direction: column;
  gap: 24px;
  margin-bottom: 40px;
}

.field label {
  font-size: 0.75rem;
  color: var(--color-star-primary);
  text-transform: uppercase;
  letter-spacing: 1.5px;
  display: block;
  margin-bottom: 8px;
}

.view-mode {
  font-size: 1.1rem;
  color: #fff;
  padding: 8px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.edit-input {
  width: 100%;
  padding: 12px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: white;
  transition: border-color 0.3s ease;
}

.edit-input:focus {
  outline: none;
  border-color: var(--color-star-primary);
  background: rgba(255, 255, 255, 0.08);
}

.details-actions {
  display: flex;
  justify-content: flex-end;
  gap: 16px;
}

@media (max-width: 600px) {
  .details-actions {
    flex-direction: column;
  }
  .details-actions > button {
    width: 100%;
  }
}
</style>