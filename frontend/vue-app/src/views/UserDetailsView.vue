<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import StarBackground from '@/components/StarBackground.vue'
import BaseButton from '@/components/BaseButton.vue'
import { defaultApi } from '@/api/defaultApi'

const router = useRouter()
const isEditing = ref(false)

// 1. Mock Data / Form State
const pilotForm = reactive({
  name: '',
  email: '',
  dob: '',
  place: ''
})

onMounted(async () => {
  try {
    const token = localStorage.getItem('token') || ''
    const username = localStorage.getItem('username') || ''
    
    if (!token) {
      router.push('/login')
      return
    }

    // Lock the name to the strict login username
    pilotForm.name = username

    // Fetch the rest of the profile data
    const statsResponse = await defaultApi.apiGetProfileStatsPost({ 
      body: {} 
    }) as any
    
    if (statsResponse) {
      pilotForm.email = statsResponse.email || ''
      if (statsResponse.profile) {
        pilotForm.dob = statsResponse.profile.dob || ''
        pilotForm.place = statsResponse.profile.place || ''
      }
    }
  } catch (err) {
    console.error("Transmission Interrupted: Could not fetch detailed logs.", err);
  }
})

const handleToggleEdit = async () => {
  if (isEditing.value) {
    console.log("Saving updated pilot data...", pilotForm)
    
    try {
      const username = localStorage.getItem('username') || ''
      const token = localStorage.getItem('token') || ''

      // Call the edit profile API - sending ONLY what we want to update
      await defaultApi.apiEditProfilePost({
        profileAndToken: {
          username: username,
          token: token,
          profile: { 
            email: pilotForm.email,
            dob: pilotForm.dob,
            place: pilotForm.place
          }
        }
      })
      
      // Update local storage email
      if (pilotForm.email) {
        localStorage.setItem('pilot_email', pilotForm.email)
      }
      
      alert("Credentials Synced Successfully!")
    } catch (err) {
      console.error("Failed to sync credentials:", err)
      alert("Failed to sync changes. Please check your connection.")
      return // Stop here so it doesn't exit edit mode if it failed
    }
  }
  
  // Toggle the edit mode state
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
            <input v-else v-model="pilotForm.name" type="text" class="edit-input disabled-input" disabled title="Callsigns cannot be altered" />
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
            <input v-else v-model="pilotForm.place" type="text" class="edit-input" placeholder="e.g., Earth, Mars Colony 4" />
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

.disabled-input {
  opacity: 0.5;
  cursor: not-allowed;
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