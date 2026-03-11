<script setup lang="ts">
import { useRouter } from 'vue-router';
import StarBackground from '@/components/StarBackground.vue';
import '../assets/styles/common.css';
import '../assets/styles/main.css';

const router = useRouter();

// 核心功能列表数据
const features = [
  {
    id: 'ar',
    title: 'AR Stargaze',
    desc: '开启摄像头，通过增强现实技术实时探索并识别你头顶的浩瀚星空与星座。',
    path: '/',
    icon: 'M12 4C7 4 2.73 7.11 1 11.5 2.73 15.89 7 19 12 19s9.27-3.11 11-7.5C21.27 7.11 17 4 12 4zm0 12.5c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z'
  },
  {
    id: 'startrail',
    title: 'Star Trail',
    desc: '模拟或记录恒星随着时间推移的运动轨迹，生成令人惊叹的星轨视觉体验。',
    path: '/star-trail',
    icon: 'M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z'
  },
  {
    id: 'recognizer',
    title: 'Recognizer',
    desc: '上传你拍摄的星空照片，智能引擎将为你分析并匹配出对应的星体与星座信息。',
    path: '/recognizer',
    icon: 'M3 5v4h2V5h4V3H5c-1.1 0-2 .9-2 2zm2 10H3v4c0 1.1.9 2 2 2h4v-2H5v-4zm14 4h-4v2h4c1.1 0 2-.9 2-2v-4h-2v4zm0-16h-4v2h4v4h2V5c0-1.1-.9-2-2-2z'
  },
  {
    id: 'chats',
    title: 'Chats',
    desc: '接入星际通讯频道，与全球各地的天文爱好者实时交流观测心得。',
    path: '/chats',
    icon: 'M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z'
  },
  {
    id: 'blog',
    title: 'Blog',
    desc: '撰写你的私人星空日志，记录每一次仰望星空的瞬间，分享宇宙的浪漫。',
    path: '/add-blog',
    icon: 'M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z'
  },
  {
    id: 'search',
    title: 'Search',
    desc: '检索庞大的天体数据库，输入名字或坐标，精准定位你想寻找的任何星辰。',
    path: '/search',
    icon: 'M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z'
  }
];

const navigateTo = (path: string) => {
  router.push(path);
};
</script>

<template>
  <StarBackground>
    <div class="navigation-container">
      
      <header class="header">
        <h1 class="title">Explore</h1>
        <p class="subtitle">Select a module to begin</p>
      </header>

      <div class="features-list">
        <div 
          v-for="feat in features" 
          :key="feat.id" 
          class="feature-card glass-panel"
          @click="navigateTo(feat.path)"
        >
          <div class="icon-box">
            <svg viewBox="0 0 24 24" width="28" height="28">
              <path fill="currentColor" :d="feat.icon" />
            </svg>
          </div>
          
          <div class="text-box">
            <h2 class="feat-title">{{ feat.title }}</h2>
            <p class="feat-desc">{{ feat.desc }}</p>
          </div>

          <div class="arrow-box">
            <svg viewBox="0 0 24 24" width="24" height="24">
              <path fill="currentColor" d="M10 6L8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z"/>
            </svg>
          </div>
        </div>
      </div>

    </div>
  </StarBackground>
</template>


<style scoped>
.navigation-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  padding: 40px 24px;
  color: var(--color-text-main);
  overflow-y: auto;
  /* 隐藏滚动条 */
  scrollbar-width: none; 
}

.navigation-container::-webkit-scrollbar {
  display: none;
}

/* 顶部标题栏 */
.header {
  margin-bottom: 32px;
}
.title {
  font-size: 36px;
  font-weight: 800;
  letter-spacing: 2px;
  color: #fff;
  text-shadow: var(--shadow-glow);
}
.subtitle {
  font-size: 14px;
  color: var(--color-text-muted);
  margin-top: 8px;
  letter-spacing: 1px;
}

/* 功能列表容器 */
.features-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding-bottom: 40px;
}

/* 单个功能卡片 (玻璃拟态 + Flex 布局) */
.feature-card {
  display: flex;
  align-items: center;
  padding: 20px 16px;
  border-radius: 20px;
  cursor: pointer;
  background: var(--color-bg-surface);
  border: 1px solid rgba(255, 255, 255, 0.08);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* 交互动效：悬停时轻微放大并加深边框光晕 */
.feature-card:hover {
  transform: translateX(6px) scale(1.01);
  background: rgba(88, 166, 255, 0.1);
  border-color: rgba(88, 166, 255, 0.4);
  box-shadow: var(--shadow-glow);
}

/* 左侧图标容器 */
.icon-box {
  flex-shrink: 0;
  width: 56px;
  height: 56px;
  border-radius: 16px;
  background: linear-gradient(135deg, rgba(88, 166, 255, 0.2), rgba(147, 51, 234, 0.2));
  display: flex;
  justify-content: center;
  align-items: center;
  color: var(--color-star-primary);
  margin-right: 16px;
  border: 1px solid rgba(88, 166, 255, 0.2);
  transition: color 0.3s, background 0.3s;
}

.feature-card:hover .icon-box {
  color: #fff;
  background: var(--color-star-primary);
  box-shadow: 0 0 15px var(--color-star-primary);
}

/* 中间文字容器 */
.text-box {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.feat-title {
  font-size: 18px;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.95);
  margin-bottom: 6px;
  letter-spacing: 0.5px;
}

.feat-desc {
  font-size: 13px;
  line-height: 1.5;
  color: var(--color-text-muted);
  /* 限制介绍文字最多显示两行，多余显示省略号 */
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* 右侧箭头指示器 */
.arrow-box {
  flex-shrink: 0;
  margin-left: 12px;
  color: rgba(255, 255, 255, 0.2);
  transition: color 0.3s, transform 0.3s;
}

.feature-card:hover .arrow-box {
  color: var(--color-star-primary);
  transform: translateX(4px);
}
</style>