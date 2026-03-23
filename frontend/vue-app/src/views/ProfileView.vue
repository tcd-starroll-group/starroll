<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import StarBackground from '@/components/StarBackground.vue'
import BaseButton from '@/components/BaseButton.vue'
import { defaultApi } from '@/api/defaultApi'

<<<<<<< HEAD
// 1. TypeScript Interfaces for the Pilot
interface UserStats {
=======
// 1. TypeScript Interfaces
interface PilotStats {
>>>>>>> bb4e51d (wip)
  starsDiscovered: number;
  totalScans: number;
  rank: string;
  joinDate: string;
}

interface Discovery {
  id: string;
  name: string;
  type: string;
  date: string;
}

<<<<<<< HEAD
// 2. Mock Data (This would eventually come from your Pinia store or API)
const user = reactive({
  name: 'Loading...',
  email: '',
=======
// 2. Reactive State
const newAvatarUrl = ref('')
const pilot = reactive({
  name: localStorage.getItem('username') || 'Pilot Loading...',
  email: '', // Added email tracking
>>>>>>> bb4e51d (wip)
  avatar: '',
  stats: {
    starsDiscovered: 0,
    totalScans: 0,
    rank: '---',
    joinDate: ''
  } as UserStats,
  recentDiscoveries: [] as Discovery[]
})

// 3. Logic Functions (Unified Save)
const saveProfileChanges = async () => {
  const username = localStorage.getItem('username') || ''
  const token = localStorage.getItem('token') || ''

  // Determine which avatar to save (new one if typed, otherwise keep existing)
  const avatarToSave = newAvatarUrl.value ? newAvatarUrl.value : pilot.avatar

  try {
    // Send both the avatar and email in the JSON payload
    await defaultApi.apiEditProfilePost({
      profileAndToken: {
        username: username,
        token: token,
        profile: { 
          avatar: avatarToSave,
          email: pilot.email 
        }
      }
    })
<<<<<<< HEAD
    pilot.name = userResponse.username || 'Unknown Pilot'

    // 2. Get Profile Stats (Rank/Scans/Discoveries)
    // The middleware automatically adds the token header, so we just pass an empty object {}
    const statsResponse = await defaultApi.apiGetProfileStatsPost({
      profileStatsRequest: {} 
    })
    
    // Update the UI
    pilot.stats = {
      starsDiscovered: statsResponse.starsDiscovered || 0,
      totalScans: statsResponse.totalScans || 0,
      rank: statsResponse.rank || 'Novice',
      joinDate: statsResponse.joinDate || '---'
    }

    console.log("Telemetry Sync Complete!")
  } catch (err) {
    console.error("Link Failure: Could not sync pilot profile.", err);
=======
    
    // Update local UI
    pilot.avatar = avatarToSave
    newAvatarUrl.value = '' // Clear the input field after saving
    
    // Sync with localStorage
    localStorage.setItem('pilot_avatar', avatarToSave)
    if (pilot.email) {
      localStorage.setItem('pilot_email', pilot.email)
    }
    
    alert("Profile synchronized with StarRoll servers!")
  } catch (err) {
    console.error("Database sync failed:", err)
    alert("Failed to save to database. Check if your session is still valid.")
>>>>>>> bb4e51d (wip)
  }
}

onMounted(async () => {
  const token = localStorage.getItem('token') || ''
  const username = localStorage.getItem('username') || 'Pilot'
  
  // PRE-LOAD from localStorage for instant UI
  pilot.name = username
  pilot.email = localStorage.getItem('pilot_email') || ''
  pilot.avatar = localStorage.getItem('pilot_avatar') || 
                 `https://api.dicebear.com/7.x/avataaars/svg?seed=${username}`

  try {
    // Fetch persisted data from the Backend
    const statsResponse = await defaultApi.apiGetProfileStatsPost({ body: {} }) as any
    
    if (statsResponse.profile) {
      // Sync Avatar
      if (statsResponse.profile.avatar) {
        pilot.avatar = statsResponse.profile.avatar
        localStorage.setItem('pilot_avatar', statsResponse.profile.avatar)
      }
      // Sync Email (if backend returns it inside the profile JSON)
      if (statsResponse.profile.email) {
        pilot.email = statsResponse.profile.email
        localStorage.setItem('pilot_email', statsResponse.profile.email)
      }
    }
    
    pilot.stats.starsDiscovered = statsResponse.starsDiscovered ?? 0
    pilot.stats.totalScans = statsResponse.totalScans ?? 0
    pilot.stats.rank = statsResponse.rank ?? '---'
  } catch (err) {
    console.error("Could not fetch persisted profile:", err)
  }
})

const router = useRouter()
const handleLogout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('username')
  localStorage.removeItem('pilot_avatar')
  localStorage.removeItem('pilot_email')
  router.push('/login')
}

const goToDetails = () => {
  router.push({ name: 'UserDetails' })
}
</script>

<template>
  <StarBackground>
    <div class="profile-container">
      
      <section class="profile-header glass-panel">
<<<<<<< HEAD
        <div class="avatar-wrapper">
          <img :src="user.avatar" alt="Pilot Avatar" class="avatar" />
          <div class="status-indicator"></div>
=======
        
        <div class="avatar-section">
          <div class="avatar-wrapper">
            <img :src="pilot.avatar" alt="Pilot Avatar" class="avatar" />
            <div class="status-indicator"></div>
          </div>
          
          <div class="avatar-edit-controls">
            <input 
              v-model="newAvatarUrl" 
              placeholder="Paste new image URL..." 
              class="url-input"
            />
          </div>
>>>>>>> bb4e51d (wip)
        </div>

        <div class="pilot-info">
<<<<<<< HEAD
          <h1 class="pilot-name">{{ user.name }}</h1>
          <p class="pilot-rank">{{ user.stats.rank }}</p>
=======
          <h1 class="pilot-name">{{ pilot.name }}</h1>
          
          <input 
            v-model="pilot.email" 
            placeholder="pilot@starroll.com" 
            class="email-input"
            type="email"
          />

          <p class="pilot-rank">{{ pilot.stats.rank }}</p>
>>>>>>> bb4e51d (wip)
          <div class="badge-row">
            <span class="badge">Fleet Member</span>
            <span class="badge">Vanguard</span>
          </div>
        </div>

        <div class="header-actions">
          <BaseButton variant="primary" size="small" @click="saveProfileChanges" class="save-btn">
            Save Changes
          </BaseButton>
          <BaseButton variant="outline" size="small" @click="goToDetails" class="details-btn">
            User Details
          </BaseButton>
          <BaseButton variant="outline" size="small" @click="handleLogout">
            Log Out
          </BaseButton>
        </div>
      </section>

      <div class="stats-grid">
        <div class="stat-card glass-panel">
          <span class="stat-label">Stars Discovered</span>
          <span class="stat-value">{{ user.stats.starsDiscovered }}</span>
        </div>
        <div class="stat-card glass-panel">
          <span class="stat-label">Total Scans</span>
          <span class="stat-value">{{ user.stats.totalScans }}</span>
        </div>
        <div class="stat-card glass-panel">
          <span class="stat-label">Stellar Rank</span>
          <span class="stat-value">{{ pilot.stats.rank }}</span>
        </div>
      </div>

      <section class="discoveries-section glass-panel">
        <h2 class="section-title">Recent Transmissions</h2>
        <div class="discovery-list">
          <div v-for="item in user.recentDiscoveries" :key="item.id" class="discovery-item">
            <div class="discovery-info">
              <span class="discovery-name">{{ item.name }}</span>
              <span class="discovery-type">{{ item.type }}</span>
            </div>
            <span class="discovery-date">{{ item.date }}</span>
          </div>
          <div v-if="pilot.recentDiscoveries.length === 0" class="empty-state">
            No recent transmissions found.
          </div>
        </div>
        <BaseButton variant="outline" class="view-all-btn">View Full Catalog</BaseButton>
      </section>

    </div>
  </StarBackground>
</template>

<style scoped>
.profile-container {
  width: 100%;
  max-width: 900px;
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: 40px 20px;
}

.profile-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 30px;
  padding: 30px;
  border-radius: 24px;
  text-align: left;
}

/* Avatar Section Styles */
.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.avatar-wrapper {
  position: relative;
}

.avatar {
  width: 110px;
  height: 110px;
  background: rgba(0, 0, 0, 0.4);
  border-radius: 50%;
  border: 2px solid var(--color-star-primary);
  object-fit: cover;
}

.status-indicator {
  position: absolute;
  bottom: 8px;
  right: 8px;
  width: 16px;
  height: 16px;
  background: #00ff88;
  border: 2px solid #000;
  border-radius: 50%;
  box-shadow: 0 0 10px #00ff88;
}

/* Input Styles */
.avatar-edit-controls {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.url-input, .email-input {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  color: white;
  padding: 6px 10px;
  outline: none;
  transition: border-color 0.3s ease;
}

.url-input {
  font-size: 11px;
  width: 140px;
  text-align: center;
}

.email-input {
  font-size: 0.9rem;
  width: 100%;
  max-width: 250px;
  margin-bottom: 8px;
  color: var(--color-star-secondary);
}

.url-input:focus, .email-input:focus {
  border-color: var(--color-star-primary);
  background: rgba(255, 255, 255, 0.1);
}

/* Info and Stats */
.pilot-info { 
  flex-grow: 1; 
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.pilot-name { font-size: 1.8rem; margin-bottom: 4px; }

.pilot-rank {
  color: var(--color-star-primary);
  text-transform: uppercase;
  font-weight: 700;
  font-size: 0.85rem;
  letter-spacing: 2px;
}

.badge-row { display: flex; gap: 8px; margin-top: 12px; }

.badge {
  font-size: 0.7rem;
  padding: 4px 10px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 100px;
  color: var(--color-text-muted);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.stat-card {
  padding: 24px;
  text-align: center;
  border-radius: 20px;
}

.stat-label {
  font-size: 0.75rem;
  color: var(--color-text-muted);
  text-transform: uppercase;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--color-star-primary);
}

.discoveries-section {
  padding: 30px;
  border-radius: 24px;
}

.discovery-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 20px;
}

.discovery-item {
  display: flex;
  justify-content: space-between;
  padding: 16px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
}

.header-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-width: 140px;
}

.save-btn {
  box-shadow: 0 0 10px rgba(0, 255, 136, 0.2);
}

.empty-state {
  color: var(--color-text-muted);
  padding: 20px;
  font-style: italic;
}

@media (max-width: 768px) {
  .profile-header { flex-direction: column; text-align: center; }
  .pilot-info { align-items: center; }
  .stats-grid { grid-template-columns: 1fr; }
  .header-actions { width: 100%; }
}
</style>