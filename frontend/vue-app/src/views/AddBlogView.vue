<script setup lang="ts">
import { ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { QuillEditor } from '@vueup/vue-quill';
import '@vueup/vue-quill/dist/vue-quill.snow.css';
import BlotFormatter from 'quill-blot-formatter';

const router = useRouter();
const route = useRoute();

const blogTitle = ref('');
const contentHtml = ref('');

// Register Quill plugin
const editorModules = [
  {
    name: 'blotFormatter',
    module: BlotFormatter,
    options: {}
  }
];

// Rich text editor configuration, explicitly includes the 'image' button here
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
      ['link', 'image', 'video'], // 🌟 Image upload button is here
      ['clean']
    ]
  }
};

// 🌟 Native fetch sends requests to resolve 401 errors
const publishBlog = async () => {
  const cleanContent = contentHtml.value === '<p><br></p>' ? '' : contentHtml.value;

  if (!blogTitle.value.trim()) {
    alert('Please enter a title for your log');
    return;
  }
  if (!cleanContent.trim()) {
    alert('Please fill in the content before publishing');
    return;
  }

  const token = localStorage.getItem('token');
  const userID = localStorage.getItem('userID');

  if (!token || !userID) {
    alert('You need to log in first to share the starry sky!');
    router.push('/login'); 
    return;
  }

  const hipId = Number(route.query.hip);
  if (!hipId) {
    alert('Error: Missing star identification (HIP number).');
    return;
  }

  try {
    const response = await fetch('/api/createBlog', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}` 
      },
      body: JSON.stringify({
        userCredentials: {
          token: token,
          userID: userID
        },
        HIP: String(hipId), 
        hIP: String(hipId), 
        title: blogTitle.value,
        content: cleanContent,
        imageURLList: [] // Rich text images will be converted to Base64 and stored in content, pass empty array for this field
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
    console.log('Blog published successfully!', data);
    alert('Published successfully!');
    
    router.back();

  // 🌟 Removed error: any, perfectly resolved the Unexpected any red line error
  } catch (error) { 
    console.error('Failed to publish blog:', error);
    alert('Failed to publish. Check console for details.');
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
            :toolbar="editorOptions.modules.toolbar"  :options="editorOptions"
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

/* 🌟 Quill Editor deep adaptation for dark space theme */
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