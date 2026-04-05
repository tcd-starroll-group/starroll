<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';

const router = useRouter();
const route = useRoute();

const starName = ref((route.query.name as string) || 'Unknown Star');
const hipId = Number(route.query.hip);

const isLoading = ref(true);
const blogs = ref<any[]>([]); // 使用 any 或你之前定义的 BlogPreview 均可

const fetchStarBlogs = async () => {
  if (!hipId) {
    alert('Missing star identification (HIP number).');
    isLoading.value = false;
    return;
  }

  const token = localStorage.getItem('token');
  const userID = localStorage.getItem('userID');

  if (!token || !userID) {
    alert('You need to log in to view star logs.');
    router.push('/login'); 
    return;
  }
  
  try {
    isLoading.value = true;
    const response = await fetch('/api/listStarBlogs', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}` 
      },
      body: JSON.stringify({
        userCredentials: { token, userID },
        HIP: String(hipId), 
        hIP: String(hipId) 
      })
    });

    if (!response.ok) {
      if (response.status === 401) {
        alert('Your session has expired. Please log in again.');
        localStorage.removeItem('token');
        router.push('/login');
        return;
      }
      throw new Error(`Server error: ${response.status}`);
    }

    const data = await response.json();
    blogs.value = data.blogsList || data.blogs_list || [];
  } catch (error) {
    console.error('Failed to fetch blogs for this star:', error);
  } finally {
    isLoading.value = false;
  }
};

const goToWriteBlog = () => {
  router.push({ path: '/add-blog', query: { hip: hipId } });
};

// 🌟 核心：点击跳转到详情页
const goToBlogDetail = (blogID: string) => {
  router.push({ 
    path: '/blog-detail', 
    query: { id: blogID } 
  });
};

onMounted(() => {
  fetchStarBlogs();
});
</script>

<template>
  <div class="starroll-app star-blogs-container">
    <header class="sr-glass-panel top-bar">
      <button class="sr-glass-btn text-btn" @click="router.back()">← Back</button>
      <div class="sr-title">Star Logs: {{ starName }}</div>
      <button class="sr-glass-btn primary-btn" @click="goToWriteBlog">Write Log</button>
    </header>

    <main class="blogs-main sr-scroll">
      <div v-if="isLoading" class="status-message">
        <div class="loading-spinner"></div>
        <p>Scanning the universe for logs...</p>
      </div>

      <div v-else-if="blogs.length === 0" class="status-message empty-state">
        <div class="empty-icon">✨</div>
        <p>No one has left a log for {{ starName }} yet.</p>
        <p class="sub-text">Be the first to share your starry sky!</p>
        <button class="sr-glass-btn primary-btn mt-4" @click="goToWriteBlog">Write the First Log</button>
      </div>

      <div v-else class="blog-cards">
        <div v-for="blog in blogs" :key="blog.blogID" class="blog-card sr-glass-panel" @click="goToBlogDetail(blog.blogID)">
          <h3 class="blog-title">{{ blog.title || 'Untitled Log' }}</h3>
          
          <div v-if="blog.imageURL" class="blog-image-preview">
            <img :src="blog.imageURL" alt="Star Log Cover" />
          </div>
          
          <div class="blog-footer">
            <div class="stats">
              <span class="stat-item">Blog ID: {{ blog.blogID }}</span>
            </div>
            <button class="sr-glass-btn text-btn read-more-btn">Read Details →</button>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.star-blogs-container { display: flex; flex-direction: column; background-image: radial-gradient(circle at 50% 0%, #1a1a2e 0%, #000000 100%); height: 100vh; color: white; }
.top-bar { display: flex; justify-content: space-between; align-items: center; padding: 12px 20px; border-radius: 0; border-top: none; border-left: none; border-right: none; z-index: 10; }
.text-btn { background: transparent; border: none; padding: 4px 8px; color: var(--sr-text-secondary); cursor: pointer; }
.primary-btn { background: rgba(68, 170, 255, 0.2); border-color: var(--sr-accent-color); color: var(--sr-accent-color); font-weight: bold; cursor: pointer; }
.blogs-main { flex: 1; padding: 20px; overflow-y: auto; display: flex; flex-direction: column; }
.status-message { flex: 1; display: flex; flex-direction: column; justify-content: center; align-items: center; color: rgba(255, 255, 255, 0.6); text-align: center; }
.empty-icon { font-size: 48px; margin-bottom: 16px; opacity: 0.8; }
.sub-text { font-size: 14px; margin-top: 8px; color: rgba(255, 255, 255, 0.4); }
.mt-4 { margin-top: 16px; }
.blog-cards { display: flex; flex-direction: column; gap: 16px; padding-bottom: 40px; }

.blog-card {
  padding: 20px;
  border-radius: 12px;
  background: rgba(25, 30, 45, 0.6);
  border: 1px solid rgba(100, 150, 255, 0.15);
  transition: transform 0.2s, border-color 0.2s;
  cursor: pointer; /* 增加鼠标手型 */
}
.blog-card:hover {
  transform: translateY(-2px);
  border-color: rgba(100, 150, 255, 0.4);
  background: rgba(30, 35, 55, 0.8);
}
.blog-title { margin: 0 0 12px 0; font-size: 18px; color: #66ccff; font-weight: 600; }
.blog-image-preview { margin-bottom: 16px; border-radius: 8px; overflow: hidden; max-height: 150px; }
.blog-image-preview img { width: 100%; height: auto; object-fit: cover; display: block; }
.blog-footer { display: flex; justify-content: space-between; align-items: center; border-top: 1px dashed rgba(255, 255, 255, 0.1); padding-top: 12px; }
.stats { display: flex; gap: 16px; }
.stat-item { font-size: 12px; color: rgba(255, 255, 255, 0.4); font-family: monospace; }
.read-more-btn { font-size: 13px; color: #66ccff; padding: 0; pointer-events: none; }
.loading-spinner { width: 40px; height: 40px; border: 3px solid rgba(100, 150, 255, 0.2); border-top-color: #66ccff; border-radius: 50%; animation: spin 1s linear infinite; margin-bottom: 20px; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>