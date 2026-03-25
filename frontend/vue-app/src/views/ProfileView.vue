<script setup lang="ts">
import { reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import StarBackground from '@/components/StarBackground.vue'
import BaseButton from '@/components/BaseButton.vue'
import { defaultApi } from '@/api/defaultApi'

// 1. TypeScript Interfaces for the Pilot
interface PilotStats {
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

// 2. Mock Data (This would eventually come from your Pinia store or API)
const pilot = reactive({
  name: 'Loading...',
  email: '',
  avatar: '',
  stats: {
    starsDiscovered: 0,
    totalScans: 0,
    rank: '---',
    joinDate: ''
  } as PilotStats,
  recentDiscoveries: [] as Discovery[]
})

onMounted(async () => {
  try {
    const token = localStorage.getItem('token') || ''
    const response = await defaultApi.apiVerifyUserTokenPost({
      apiVerifyUserTokenPostRequest: { token },
    })

    pilot.name = response.username || 'Loading...'
    console.log("档案同步成功:", pilot.name)
  } catch (err) {
    console.error("无法获取飞行员档案，请检查 Token 是否有效");
  }

  try {
    const statsResponse = await defaultApi.apiGetProfileStatsPost({ body: {} })
    pilot.stats.starsDiscovered = statsResponse.starsDiscovered ?? 0
    pilot.stats.totalScans = statsResponse.totalScans ?? 0
    pilot.stats.rank = statsResponse.rank ?? '---'
    pilot.stats.joinDate = statsResponse.joinDate ?? ''
    console.log("Profile stats loaded:", pilot.stats)
  } catch (err) {
    console.error("Failed to load profile stats:", err)
  }
})
const router = useRouter()
const handleLogout = () => {
  console.log("Logging out pilot...")
  localStorage.removeItem('token')
  // router.push('/login')
}
const goToDetails = () => {
  router.push({ name: 'UserDetails' }) // This matches the "name" in your router file
}
</script>

<template>
  <StarBackground>
    <div class="profile-container">
      
      <section class="profile-header glass-panel">
        <div class="avatar-wrapper">
          <img :src="pilot.avatar" alt="Pilot Avatar" class="avatar" />
          <div class="status-indicator"></div>
        </div>
        <div class="pilot-info">
          <h1 class="pilot-name">{{ pilot.name }}</h1>
          <p class="pilot-rank">{{ pilot.stats.rank }}</p>
          <div class="badge-row">
            <span class="badge">Fleet Member</span>
            <span class="badge">Vanguard</span>
          </div>
        </div>
        <div class="header-actions">
          <BaseButton variant="primary" @click="goToDetails" class="details-btn">
            User Details
          </BaseButton>
          <BaseButton variant="outline" @click="handleLogout">Log Out</BaseButton>
        </div>
      </section>

      <div class="stats-grid">
        <div class="stat-card glass-panel">
          <span class="stat-label">Stars Discovered</span>
          <span class="stat-value">{{ pilot.stats.starsDiscovered }}</span>
        </div>
        <div class="stat-card glass-panel">
          <span class="stat-label">Total Scans</span>
          <span class="stat-value">{{ pilot.stats.totalScans }}</span>
        </div>
        <div class="stat-card glass-panel">
          <span class="stat-label">Stellar Rank</span>
          <span class="stat-value">{{ pilot.stats.rank }}</span>
        </div>
      </div>

      <section class="discoveries-section glass-panel">
        <h2 class="section-title">Recent Transmissions</h2>
        <div class="discovery-list">
          <div v-for="item in pilot.recentDiscoveries" :key="item.id" class="discovery-item">
            <div class="discovery-info">
              <span class="discovery-name">{{ item.name }}</span>
              <span class="discovery-type">{{ item.type }}</span>
            </div>
            <span class="discovery-date">{{ item.date }}</span>
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
  max-width: 800px;
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: 40px 20px;
  text-align: center;
}                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                

/* Header Styles */
.profile-header {
  display: flex;
  align-items: center;
  gap: 30px;
  padding: 30px;
  border-radius: 24px;
}

.avatar-wrapper {
  position: relative;
}

.avatar {
  width: 100px;
  height: 100px;
  background: rgba(0, 0, 0, 0.4);
  border-radius: 50%;
  border: 2px solid var(--color-star-primary);
  padding: 10px;
}

.status-indicator {
  position: absolute;
  bottom: 5px;
  right: 5px;
  width: 18px;
  height: 18px;
  background: #00ff88;
  border: 3px solid var(--color-bg-deep);
  border-radius: 50%;
  box-shadow: 0 0 10px #00ff88;
}

.pilot-name {
  font-size: 1.8rem;
  letter-spacing: 1px;
  margin-bottom: 4px;
}

.pilot-rank {
  color: var(--color-star-primary);
  text-transform: uppercase;
  font-weight: 700;
  font-size: 0.85rem;
  letter-spacing: 2px;
}

.badge-row {
  display: flex;
  gap: 8px;
  margin-top: 12px;
}

.badge {
  font-size: 0.7rem;
  padding: 4px 10px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 100px;
  color: var(--color-text-muted);
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.stat-card {
  padding: 24px;
  text-align: center;
  border-radius: 20px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stat-label {
  font-size: 0.75rem;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 1px;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--color-star-primary);
}

/* Discoveries List */
.discoveries-section {
  padding: 30px;
  border-radius: 24px;
}

.section-title {
  font-size: 1.2rem;
  margin-bottom: 20px;
  color: var(--color-text-main);
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
  align-items: center;
  padding: 16px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
  transition: background 0.3s ease;
}

.discovery-item:hover {
  background: rgba(255, 255, 255, 0.07);
}

.discovery-info {
  display: flex;
  flex-direction: column;
}

.discovery-name {
  font-weight: 600;
  color: var(--color-text-main);
}

.discovery-type {
  font-size: 0.8rem;
  color: var(--color-text-muted);
}

.discovery-date {
  font-size: 0.8rem;
  color: var(--color-star-secondary);
}

.view-all-btn {
  width: 100%;
}

.header-actions {
  display: flex;
  flex-direction: row; /* Aligns buttons horizontally */
  gap: 12px;           /* Adjust this value (e.g., 16px, 20px) for more/less space */
  align-items: center;
}

@media (max-width: 600px) {
  .stats-grid { grid-template-columns: 1fr; }
  .profile-header { flex-direction: column; text-align: center; }
  .badge-row { justify-content: center; }
  .header-actions {
    flex-direction: column;
    width: 100%;
  }
  
  .header-actions > button {
    width: 100%; /* Makes buttons full-width on mobile */
  }
}
</style>