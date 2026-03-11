<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import StarBackground from '@/components/StarBackground.vue';
import BottomBar from '@/components/BottomBar.vue';

// 引入全局通用样式
import '../assets/styles/common.css';
import '../assets/styles/main.css';

const router = useRouter();

// 搜索框状态
const searchQuery = ref('');

// 模拟的博客列表数据 (后续可替换为通过 defaultApi 获取的后端数据)
const blogs = ref([
  {
    id: '1',
    title: 'Dublin 凤凰公园的完美观星夜',
    excerpt: '昨晚都柏林难得放晴，我带上设备去了凤凰公园。避开了市中心的严重光污染，猎户座的腰带清晰可见。我还尝试使用了 StarRoll 的 AR 模式...',
    author: 'Kehan',
    date: '2026-03-08',
    likes: 128,
    comments: 32
  },
  {
    id: '2',
    title: '如何拍摄清晰的星轨？新手入门指南',
    excerpt: '拍摄星轨并不需要极其昂贵的设备，一台支持手动模式（M档）的微单和一根三脚架就足够了。今天我们来聊聊快门速度、ISO和光圈的黄金搭配组合。',
    author: 'AstroPhotog',
    date: '2026-03-05',
    likes: 345,
    comments: 89
  },
  {
    id: '3',
    title: '韦伯望远镜最新传回的深空图像解析',
    excerpt: 'NASA 昨天释出了最新的创生之柱红外波段图像。与哈勃时期相比，韦伯极其强大的红外穿透能力让我们看到了隐藏在星际尘埃背后的新生恒星...',
    author: 'DeepSpace',
    date: '2026-03-01',
    likes: 892,
    comments: 156
  },
  {
    id: '4',
    title: '记录一次失败的流星雨观测',
    excerpt: '满心期待的双子座流星雨，结果遇到了大面积的云层覆盖，在寒风中冻了三个小时只看到了一颗暗淡的流星划过。不过这才是天文观测的常态吧。',
    author: 'CloudyNight',
    date: '2025-12-15',
    likes: 45,
    comments: 12
  }
]);

// 根据搜索关键词动态过滤博客
const filteredBlogs = computed(() => {
  if (!searchQuery.value) return blogs.value;
  const q = searchQuery.value.toLowerCase();
  return blogs.value.filter(blog => 
    blog.title.toLowerCase().includes(q) || 
    blog.excerpt.toLowerCase().includes(q) ||
    blog.author.toLowerCase().includes(q)
  );
});

// 路由跳转
const goToAddBlog = () => {
  router.push('/add-blog');
};

const goToBlogDetail = (id: string) => {
  // TODO: 后续可以跳转到具体的博客详情页，如 router.push(`/blog/${id}`)
  console.log('Navigate to blog details:', id);
};
</script>

<template>
  <StarBackground>
    <div class="blog-index-container">
      
      <header class="header">
        <h1 class="title">StarLog</h1>
        <button class="write-btn" @click="goToAddBlog">
          <svg viewBox="0 0 24 24" width="20" height="20">
            <path fill="currentColor" d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/>
          </svg>
          <span>Write</span>
        </button>
      </header>

      <div class="search-section">
        <div class="search-bar glass-panel">
          <svg class="search-icon" viewBox="0 0 24 24" width="20" height="20">
            <path fill="currentColor" d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
          </svg>
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="Search logs, authors, or galaxies..." 
            class="search-input"
          />
        </div>
      </div>

      <div class="blog-list">
        <transition-group name="list">
          <div 
            v-for="blog in filteredBlogs" 
            :key="blog.id" 
            class="blog-card glass-panel"
            @click="goToBlogDetail(blog.id)"
          >
            <h2 class="blog-title">{{ blog.title }}</h2>
            <p class="blog-excerpt">{{ blog.excerpt }}</p>
            
            <div class="blog-meta">
              <div class="meta-left">
                <span class="author">@{{ blog.author }}</span>
                <span class="dot">•</span>
                <span class="date">{{ blog.date }}</span>
              </div>
              <div class="meta-right">
                <div class="stat">
                  <svg viewBox="0 0 24 24" width="14" height="14">
                    <path fill="currentColor" d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
                  </svg>
                  <span>{{ blog.likes }}</span>
                </div>
                <div class="stat">
                  <svg viewBox="0 0 24 24" width="14" height="14">
                    <path fill="currentColor" d="M21.99 4c0-1.1-.89-2-1.99-2H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h14l4 4-.01-18zM18 14H6v-2h12v2zm0-3H6V9h12v2zm0-3H6V6h12v2z"/>
                  </svg>
                  <span>{{ blog.comments }}</span>
                </div>
              </div>
            </div>
          </div>
        </transition-group>

        <div v-if="filteredBlogs.length === 0" class="empty-state">
          <p>No starlight found matching your query.</p>
        </div>
      </div>

    </div>

    <BottomBar />
  </StarBackground>
</template>

<style scoped>
.blog-index-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  /* 顶部留白，底部留出 100px 空间防止被 BottomBar 挡住内容 */
  padding: 40px 20px 100px 20px; 
  color: var(--color-text-main);
  overflow-y: auto;
  scrollbar-width: none; 
}
.blog-index-container::-webkit-scrollbar {
  display: none;
}

/* Header 区域 */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}
.title {
  font-size: 32px;
  font-weight: 800;
  letter-spacing: 1px;
  text-shadow: var(--shadow-glow);
}

/* 霓虹发光的 Write 按钮 */
.write-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  background: rgba(88, 166, 255, 0.15);
  border: 1px solid rgba(88, 166, 255, 0.4);
  color: var(--color-star-primary);
  padding: 8px 16px;
  border-radius: 20px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 0 10px rgba(88, 166, 255, 0.2);
}
.write-btn:hover {
  background: var(--color-star-primary);
  color: #fff;
  box-shadow: 0 0 20px rgba(88, 166, 255, 0.6);
  transform: translateY(-2px);
}

/* 搜索栏 */
.search-section {
  margin-bottom: 24px;
}
.search-bar {
  display: flex;
  align-items: center;
  padding: 0 16px;
  height: 48px;
  border-radius: 12px;
  transition: border-color 0.3s, box-shadow 0.3s;
}
.search-bar:focus-within {
  border-color: var(--color-star-primary);
  box-shadow: 0 0 15px rgba(88, 166, 255, 0.2);
}
.search-icon {
  color: var(--color-text-muted);
  margin-right: 12px;
}
.search-input {
  flex: 1;
  background: transparent;
  border: none;
  color: var(--color-text-main);
  font-size: 15px;
  outline: none;
}
.search-input::placeholder {
  color: var(--color-text-muted);
}

/* 博客列表 */
.blog-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 博客卡片 */
.blog-card {
  padding: 20px;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.blog-card:hover {
  transform: translateY(-4px);
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(88, 166, 255, 0.3);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
}

.blog-title {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 8px;
  color: rgba(255, 255, 255, 0.95);
  line-height: 1.4;
}

.blog-excerpt {
  font-size: 14px;
  color: var(--color-text-muted);
  line-height: 1.6;
  margin-bottom: 16px;
  /* 限制最多显示两行，超出显示省略号 */
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* 卡片底部元数据 */
.blog-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
}
.meta-left {
  display: flex;
  align-items: center;
  gap: 8px;
}
.author {
  color: var(--color-star-primary);
  font-weight: 500;
}
.meta-right {
  display: flex;
  gap: 12px;
}
.stat {
  display: flex;
  align-items: center;
  gap: 4px;
}

/* 搜索无结果时的空状态 */
.empty-state {
  text-align: center;
  padding: 40px 0;
  color: var(--color-text-muted);
  font-style: italic;
}

/* Vue 的列表动画过渡效果 */
.list-enter-active,
.list-leave-active {
  transition: all 0.4s ease;
}
.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateY(20px);
}
</style>