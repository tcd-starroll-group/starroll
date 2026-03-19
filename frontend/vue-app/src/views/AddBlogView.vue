<script setup lang="ts">
import { ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { QuillEditor } from '@vueup/vue-quill';
import '@vueup/vue-quill/dist/vue-quill.snow.css';
import BlotFormatter from 'quill-blot-formatter';

// 🌟 引入生成的 API 客户端
import { DefaultApi } from '@/gen/ts/apis/DefaultApi';
import { Configuration } from '@/gen/ts/runtime';

const router = useRouter();
const route = useRoute(); // 实例化 route 以获取 URL 中的 hip

const blogTitle = ref('');
const contentHtml = ref('');

// 注册 Quill 插件
const editorModules = [
  {
    name: 'blotFormatter',
    module: BlotFormatter,
    options: {}
  }
];

// 富文本编辑器配置
const editorOptions = {
  placeholder: 'Record your star-gazing log, or share the romance of the universe...',
  theme: 'snow',
  modules: {
    toolbar: [
      [{ 'header': [1, 2, 3, 4, 5, 6, false] }],
      [{ 'font': [] }],
      [{ 'size': ['small', false, 'large', 'huge'] }],
      ['bold', 'italic', 'underline', 'strike'],
      [{ 'script': 'sub'}, { 'script': 'super' }],
      [{ 'color': [] }, { 'background': [] }],
      [{ 'list': 'ordered'}, { 'list': 'bullet' }, { 'list': 'check' }],
      [{ 'indent': '-1'}, { 'indent': '+1' }],
      [{ 'align': [] }],
      [{ 'direction': 'rtl' }],
      ['blockquote', 'code-block'],
      ['link', 'image', 'video'],
      ['clean']
    ]
  }
};

// 🌟 真实的发布博客联调函数
const publishBlog = async () => {
  const cleanContent = contentHtml.value === '<p><br></p>' ? '' : contentHtml.value;

  // 1. 校验前端必填项
  if (!blogTitle.value.trim()) {
    alert('Please enter a title for your log');
    return;
  }
  if (!cleanContent.trim()) {
    alert('Please fill in the content before publishing');
    return;
  }

  // 2. 提取用户身份凭证
  const token = localStorage.getItem('token');
  const userID = localStorage.getItem('userID');

  if (!token || !userID) {
    alert('You need to log in first to share the starry sky!');
    return;
  }

  // 3. 提取 HIP 编号 (从 URL query 解析)
  const hipId = Number(route.query.hip);
  if (!hipId) {
    alert('Error: Missing star identification (HIP number).');
    return;
  }

  // 4. 初始化 API
  const api = new DefaultApi(new Configuration({ basePath: '/api' }));

  try {
    // 发送创建博客请求
    const response = await api.apiCreateBlogPost({
      apiCreateBlogPostRequest: {
        userCredentials: {
          token: token,
          userID: userID // 如果生成器生成的是 userID（大写D），请自行修改
        },
        hIP: String(hipId), // 强制转为 String，以匹配后端模型
        title: blogTitle.value,
        content: cleanContent,
        imageURLList: []    // 暂时没有图片上传功能，传空数组
      }
    });

    console.log('Blog published successfully! ID:', response.blogID);
    alert('Published successfully!');
    
    // 发布成功后，退回到星空日记浏览页
    router.back();
  } catch (error) {
    console.error('Failed to publish blog:', error);
    alert('Failed to publish. Check console for details. (Maybe Token expired?)');
  }
};
</script>

<template>
  <div class="starroll-app add-blog-container">
    <header class="sr-glass-panel top-bar">
      <button class="sr-glass-btn text-btn" @click="router.back()">← Back</button>
      <div class="sr-title">New Star Log</div>
      <button class="sr-glass-btn primary-btn" @click="publishBlog">Publish</button>
    </header>

    <main class="editor-main sr-scroll">
      <div class="editor-wrapper sr-glass-panel">
        <input 
          v-model="blogTitle" 
          type="text" 
          class="title-input" 
          placeholder="Enter your log title here..." 
        />
        
        <div class="quill-container">
          <QuillEditor 
            v-model:content="contentHtml" 
            contentType="html" 
            :options="editorOptions" 
            :modules="editorModules" 
          />
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.add-blog-container {
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

.text-btn {
  background: transparent;
  border: none;
  padding: 4px 8px;
  color: var(--sr-text-secondary, #8899aa);
  cursor: pointer;
}

.primary-btn {
  background: rgba(68, 170, 255, 0.2);
  border-color: var(--sr-accent-color, #66ccff);
  color: var(--sr-accent-color, #66ccff);
  font-weight: bold;
  cursor: pointer;
  padding: 6px 16px;
  border-radius: 6px;
}

.primary-btn:hover {
  background: rgba(68, 170, 255, 0.3);
}

.editor-main {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.editor-wrapper {
  width: 100%;
  max-width: 900px;
  display: flex;
  flex-direction: column;
  border-radius: 12px;
  background: rgba(25, 30, 45, 0.6);
  border: 1px solid rgba(100, 150, 255, 0.15);
  overflow: hidden;
}

.title-input {
  width: 100%;
  padding: 20px;
  font-size: 24px;
  font-weight: bold;
  background: transparent;
  border: none;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  color: white;
  outline: none;
  font-family: var(--sr-font-family);
}

.title-input::placeholder {
  color: rgba(255, 255, 255, 0.3);
}

.quill-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: rgba(255, 255, 255, 0.02);
  min-height: 400px;
}

/* 🌟 Quill Editor 深度适配深色太空主题 */
:deep(.ql-toolbar.ql-snow) {
  border: none;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.05);
  padding: 12px;
}

:deep(.ql-container.ql-snow) {
  border: none;
  font-family: var(--sr-font-family);
  font-size: 16px;
  color: white;
}

:deep(.ql-editor) {
  min-height: 400px;
  padding: 20px;
  line-height: 1.6;
}

:deep(.ql-editor.ql-blank::before) {
  color: rgba(255, 255, 255, 0.3);
  font-style: italic;
}

:deep(.ql-snow .ql-stroke) {
  stroke: rgba(255, 255, 255, 0.7);
}

:deep(.ql-snow .ql-fill) {
  fill: rgba(255, 255, 255, 0.7);
}

:deep(.ql-snow .ql-picker) {
  color: rgba(255, 255, 255, 0.7);
}

:deep(.ql-snow .ql-toolbar button:hover .ql-stroke),
:deep(.ql-snow .ql-toolbar button.ql-active .ql-stroke),
:deep(.ql-snow .ql-toolbar .ql-picker-label:hover .ql-stroke),
:deep(.ql-snow .ql-toolbar .ql-picker-label.ql-active .ql-stroke) {
  stroke: var(--sr-accent-color, #66ccff);
}

:deep(.ql-snow .ql-toolbar button:hover .ql-fill),
:deep(.ql-snow .ql-toolbar button.ql-active .ql-fill),
:deep(.ql-snow .ql-toolbar .ql-picker-label:hover .ql-fill),
:deep(.ql-snow .ql-toolbar .ql-picker-label.ql-active .ql-fill) {
  fill: var(--sr-accent-color, #66ccff);
}

:deep(.ql-snow .ql-picker-options) {
  background-color: var(--sr-bg-glass, rgba(30, 35, 55, 0.95));
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
}

:deep(.ql-editor pre.ql-syntax) {
  background-color: rgba(0, 0, 0, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #a6e22e;
  border-radius: 6px;
}

:deep(.ql-editor blockquote) {
  border-left: 4px solid var(--sr-accent-color, #66ccff);
  color: rgba(255, 255, 255, 0.8);
  background: rgba(255, 255, 255, 0.05);
  padding: 10px 15px;
  border-radius: 0 6px 6px 0;
  margin: 10px 0;
}
</style>