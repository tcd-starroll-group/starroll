<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';

const router = useRouter();
const route = useRoute();

// 从路由参数中获取博客 ID
const blogID = (route.query.id as string) || '';

const isLoading = ref(true);
const errorMessage = ref('');

// 博客全量数据状态
const blogData = ref<any>(null);
const isLiked = ref(false); // 本地乐观更新的状态

// 评论交互状态
const commentDraft = ref('');
const isSubmittingComment = ref(false);

// 1. 获取博客详情
const fetchBlogDetail = async () => {
  if (!blogID) {
    errorMessage.value = 'Invalid Blog ID.';
    isLoading.value = false;
    return;
  }

  const token = localStorage.getItem('token');
  try {
    const response = await fetch('/api/viewBlog', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}` 
      },
      // 兼容两种可能的大小写，防止 422 报错
      body: JSON.stringify({ blogID: blogID, blog_id: blogID })
    });

    if (!response.ok) throw new Error('Failed to load blog detail');

    const data = await response.json();
    blogData.value = data;

  } catch (error) {
    console.error('Fetch detail error:', error);
    errorMessage.value = 'The signal was lost. Failed to load the log.';
  } finally {
    isLoading.value = false;
  }
};

// 2. 点赞博客
const handleLike = async () => {
  if (!blogData.value || !blogID) return;
  
  const token = localStorage.getItem('token');
  
  // 乐观更新 UI
  isLiked.value = !isLiked.value;
  const countKey = blogData.value.likeNumber !== undefined ? 'likeNumber' : 'like_count';
  blogData.value[countKey] = (blogData.value[countKey] || 0) + (isLiked.value ? 1 : -1);

  try {
    const response = await fetch('/api/likeBlog', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ blogID: blogID, blog_id: blogID })
    });

    if (!response.ok) throw new Error('Like failed');
    
    // 使用后端返回的真实数量修正本地数量
    const data = await response.json();
    if (data.likeNumber !== undefined) {
      blogData.value[countKey] = data.likeNumber;
      isLiked.value = true; // 根据后端的返回，此时一定是 true
    }
  } catch (error) {
    console.error('Like error:', error);
    // 失败则回滚
    isLiked.value = !isLiked.value;
    blogData.value[countKey] += isLiked.value ? 1 : -1;
  }
};

// 3. 提交评论
const submitComment = async () => {
  if (!commentDraft.value.trim() || !blogID) return;

  const token = localStorage.getItem('token');
  const userID = localStorage.getItem('userID');
  isSubmittingComment.value = true;

  try {
    const response = await fetch('/api/commentBlog', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ 
        blogID: blogID, 
        blog_id: blogID,
        commentText: commentDraft.value,
        comment_text: commentDraft.value
      })
    });

    if (!response.ok) throw new Error('Comment failed');

    // 提交成功，本地追加评论，体验更丝滑
    const countKey = blogData.value.commentNumber !== undefined ? 'commentNumber' : 'comment_count';
    blogData.value[countKey] = (blogData.value[countKey] || 0) + 1;
    
    if (!blogData.value.commentList) blogData.value.commentList = [];
    
    // 把自己的评论加到列表最前面
    blogData.value.commentList.unshift({
      commentID: 'temp-' + Date.now(),
      commentText: commentDraft.value,
      userID: userID || 'You',
      time: new Date().toISOString()
    });

    commentDraft.value = ''; // 清空草稿

  } catch (error) {
    console.error('Comment error:', error);
    alert('Failed to post comment. Space dust interference.');
  } finally {
    isSubmittingComment.value = false;
  }
};

// 格式化时间辅助函数
const formatTime = (timeStr?: string) => {
  if (!timeStr) return 'Just now';
  return new Date(timeStr).toLocaleString(undefined, {
    month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
  });
};

onMounted(() => {
  fetchBlogDetail();
});
</script>

<template>
  <div class="starroll-app blog-detail-container">
    <header class="sr-glass-panel top-bar">
      <button class="sr-glass-btn text-btn" @click="router.back()">← Back</button>
      <div class="sr-title">Star Log Detail</div>
      <div style="width: 60px"></div> </header>

    <main class="detail-main sr-scroll">
      
      <div v-if="isLoading" class="status-message">
        <div class="loading-spinner"></div>
        <p>Receiving signal...</p>
      </div>

      <div v-else-if="errorMessage" class="status-message empty-state">
        <div class="empty-icon">⚠️</div>
        <p class="error-text">{{ errorMessage }}</p>
      </div>

      <div v-else-if="blogData" class="blog-content-wrapper">
        <div class="blog-header">
          <h1 class="blog-title">{{ blogData.title || 'Untitled Log' }}</h1>
        </div>

        <div v-if="blogData.imageURLList && blogData.imageURLList.length > 0" class="blog-images sr-glass-panel">
          <img v-for="(img, idx) in blogData.imageURLList" :key="idx" :src="img" alt="Blog Image" />
        </div>

        <div class="blog-text sr-glass-panel ql-editor-custom">
          <div v-if="blogData.content" v-html="blogData.content"></div>
          <p v-else class="empty-content">No content written for this log.</p>
        </div>

        <div class="interaction-bar sr-glass-panel">
          <button 
            class="action-btn like-btn" 
            :class="{ 'is-liked': isLiked }" 
            @click="handleLike"
          >
            <svg viewBox="0 0 24 24" width="24" height="24">
              <path v-if="!isLiked" fill="currentColor" d="M12.1 18.55L12 18.65L11.89 18.55C7.14 14.24 4 11.39 4 8.5C4 6.5 5.5 5 7.5 5C9.04 5 10.54 6 11.07 7.36H12.93C13.46 6 14.96 5 16.5 5C18.5 5 20 6.5 20 8.5C20 11.39 16.86 14.24 12.1 18.55ZM16.5 3C14.76 3 13.09 3.81 12 5.08C10.91 3.81 9.24 3 7.5 3C4.42 3 2 5.41 2 8.5C2 12.27 5.4 15.36 10.55 20.03L12 21.35L13.45 20.03C18.6 15.36 22 12.27 22 8.5C22 5.41 19.58 3 16.5 3Z"/>
              <path v-else fill="currentColor" d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
            </svg>
            <span>{{ blogData.likeNumber || blogData.like_count || 0 }} Likes</span>
          </button>
          
          <div class="stat-info">
            <span>💬 {{ blogData.commentNumber || blogData.comment_count || 0 }} Comments</span>
          </div>
        </div>

        <div class="comments-section sr-glass-panel">
          <h3 class="section-title">Log Communications</h3>
          
          <div class="comment-input-area">
            <textarea 
              v-model="commentDraft" 
              class="sr-input comment-textarea" 
              placeholder="Leave your message here..."
              rows="3"
            ></textarea>
            <button 
              class="sr-glass-btn primary-btn submit-btn" 
              :disabled="!commentDraft.trim() || isSubmittingComment"
              @click="submitComment"
            >
              {{ isSubmittingComment ? 'Sending...' : 'Send Message' }}
            </button>
          </div>

          <div class="comment-list">
            <div v-if="!blogData.commentList || blogData.commentList.length === 0" class="no-comments">
              Space is silent. Be the first to speak.
            </div>
            
            <div v-else v-for="comment in blogData.commentList" :key="comment.commentID" class="comment-item">
              <div class="comment-user">Astronaut #{{ String(comment.userID || 'Unknown').substring(0,4) }}</div>
              <div class="comment-text">{{ comment.commentText }}</div>
              <div class="comment-time">{{ formatTime(comment.time) }}</div>
            </div>
          </div>
        </div>

      </div>
    </main>
  </div>
</template>

<style scoped>
.blog-detail-container {
  display: flex;
  flex-direction: column;
  background-image: radial-gradient(circle at 50% 0%, #1a1a2e 0%, #000000 100%);
  height: 100vh;
  color: white;
}

.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  border-radius: 0;
  border-top: none;
  border-left: none;
  border-right: none;
  z-index: 10;
}

.text-btn { background: transparent; border: none; padding: 4px 8px; color: var(--sr-text-secondary); cursor: pointer; }
.primary-btn { background: rgba(68, 170, 255, 0.2); border-color: var(--sr-accent-color); color: var(--sr-accent-color); font-weight: bold; cursor: pointer; }

.detail-main {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  max-width: 800px;
  width: 100%;
  margin: 0 auto;
}

.status-message { display: flex; flex-direction: column; justify-content: center; align-items: center; height: 50vh; color: rgba(255, 255, 255, 0.6); }
.empty-icon { font-size: 48px; margin-bottom: 16px; }
.error-text { color: #ff4757; }

.blog-content-wrapper { display: flex; flex-direction: column; gap: 20px; padding-bottom: 40px; }

.blog-title { font-size: 28px; color: #66ccff; margin: 0; font-weight: 700; text-shadow: 0 0 10px rgba(102, 204, 255, 0.3); }

.blog-images { padding: 16px; border-radius: 12px; display: flex; flex-direction: column; gap: 12px; }
.blog-images img { width: 100%; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.5); }

/* 🌟 富文本展示的专属样式，完美还原 Quill 的排版 */
.ql-editor-custom { 
  padding: 24px; 
  border-radius: 12px; 
  line-height: 1.8; 
  font-size: 16px; 
  letter-spacing: 0.5px; 
  color: rgba(255, 255, 255, 0.9);
}
/* 因为 v-html 是动态注入的，Vue 会把 scoped 样式隔离开，为了作用到 v-html 内部，我们需要使用 :deep() */
.ql-editor-custom :deep(h1) { font-size: 2em; margin-bottom: 0.5em; border-bottom: 1px solid rgba(255, 255, 255, 0.1); padding-bottom: 0.3em; }
.ql-editor-custom :deep(h2) { font-size: 1.5em; margin-bottom: 0.5em; color: #66ccff; }
.ql-editor-custom :deep(p) { margin-bottom: 1em; }
.ql-editor-custom :deep(ul), .ql-editor-custom :deep(ol) { margin-left: 2em; margin-bottom: 1em; }
.ql-editor-custom :deep(li) { margin-bottom: 0.5em; }
.ql-editor-custom :deep(blockquote) { border-left: 4px solid #66ccff; padding-left: 16px; margin-left: 0; color: rgba(255, 255, 255, 0.6); font-style: italic; background: rgba(102, 204, 255, 0.05); padding: 12px 16px; border-radius: 0 8px 8px 0; }
.ql-editor-custom :deep(img) { max-width: 100%; border-radius: 8px; margin: 16px 0; }
.ql-editor-custom :deep(strong) { font-weight: bold; color: white; }
.ql-editor-custom :deep(a) { color: #66ccff; text-decoration: none; }
.ql-editor-custom :deep(a:hover) { text-decoration: underline; }

.empty-content { color: rgba(255, 255, 255, 0.4); font-style: italic; }

.interaction-bar { display: flex; justify-content: space-between; align-items: center; padding: 16px 24px; border-radius: 12px; }
.action-btn { display: flex; align-items: center; gap: 8px; background: transparent; border: none; color: rgba(255, 255, 255, 0.8); font-size: 16px; cursor: pointer; font-weight: bold; transition: all 0.2s; }
.like-btn:hover { color: #ff4757; transform: scale(1.05); }
.like-btn.is-liked { color: #ff4757; }
.stat-info { color: rgba(255, 255, 255, 0.6); font-size: 14px; }

.comments-section { padding: 24px; border-radius: 12px; }
.section-title { font-size: 18px; color: #66ccff; margin-bottom: 16px; border-bottom: 1px dashed rgba(255,255,255,0.1); padding-bottom: 8px; }

.comment-input-area { display: flex; flex-direction: column; gap: 12px; margin-bottom: 32px; }
.comment-textarea { width: 100%; background: rgba(0, 0, 0, 0.2); border: 1px solid rgba(255, 255, 255, 0.1); color: white; padding: 12px; border-radius: 8px; resize: vertical; font-family: inherit; }
.comment-textarea:focus { outline: none; border-color: #66ccff; box-shadow: 0 0 8px rgba(102, 204, 255, 0.2); }
.submit-btn { align-self: flex-end; padding: 8px 24px; }
.submit-btn:disabled { opacity: 0.5; cursor: not-allowed; }

.comment-list { display: flex; flex-direction: column; gap: 16px; }
.no-comments { text-align: center; color: rgba(255, 255, 255, 0.4); padding: 20px 0; font-style: italic; }
.comment-item { background: rgba(0, 0, 0, 0.2); padding: 16px; border-radius: 8px; border-left: 3px solid #66ccff; }
.comment-user { font-size: 12px; color: #66ccff; font-weight: bold; margin-bottom: 6px; }
.comment-text { font-size: 14px; line-height: 1.5; color: rgba(255, 255, 255, 0.9); margin-bottom: 8px; white-space: pre-wrap; }
.comment-time { font-size: 11px; color: rgba(255, 255, 255, 0.4); }

.loading-spinner { width: 40px; height: 40px; border: 3px solid rgba(100, 150, 255, 0.2); border-top-color: #66ccff; border-radius: 50%; animation: spin 1s linear infinite; margin-bottom: 20px; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>