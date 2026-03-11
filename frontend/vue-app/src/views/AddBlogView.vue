<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { QuillEditor } from '@vueup/vue-quill';
import '@vueup/vue-quill/dist/vue-quill.snow.css';

import BlotFormatter from 'quill-blot-formatter';

const router = useRouter();

const blogTitle = ref('');
const contentHtml = ref('');

const editorModules = [
  {
    name: 'blotFormatter',
    module: BlotFormatter,
    options: {}
  }
];

// Super versatile rich text toolbar configuration
const editorOptions = {
  placeholder: 'Record your star-gazing log, or share the romance of the universe...',
  theme: 'snow',
  modules: {
    toolbar: [
      // 1. Title, font family, font size
      [{ 'header': [1, 2, 3, 4, 5, 6, false] }],
      [{ 'font': [] }],
      [{ 'size': ['small', false, 'large', 'huge'] }],

      // 2. Basic text styles and superscript/subscript
      ['bold', 'italic', 'underline', 'strike'],
      [{ 'script': 'sub'}, { 'script': 'super' }],

      // 3. Font color and background color
      [{ 'color': [] }, { 'background': [] }],

      // 4. List and indent (including checklist)
      [{ 'list': 'ordered'}, { 'list': 'bullet' }, { 'list': 'check' }],
      [{ 'indent': '-1'}, { 'indent': '+1' }],

      // 5. Alignment and reading direction
      [{ 'align': [] }],
      [{ 'direction': 'rtl' }],

      // 6. Block elements: blockquote and code block
      ['blockquote', 'code-block'],

      // 7. Media and links: insert link, image, video
      ['link', 'image', 'video'],

      // 8. Ultimate button: clear all formats
      ['clean']
    ]
  }
};

const publishBlog = async () => {
  const cleanContent = contentHtml.value === '<p><br></p>' ? '' : contentHtml.value;

  if (!blogTitle.value.trim() && !cleanContent.trim()) {
    alert('Please fill in the content before publishing');
    return;
  }

  const blogData = {
    title: blogTitle.value,
    content: cleanContent
  };

  console.log('Publishing blog:', blogData);
  alert('Published successfully! (Frontend simulation)');
  router.back();
};
</script>

<template>
  <div class="starroll-app add-blog-container">
    <header class="sr-glass-panel top-bar">
      <button class="sr-glass-btn text-btn" @click="router.back()">Cancel</button>
      <div class="sr-title">Share the Starry Sky</div>
      <button class="sr-glass-btn primary-btn" @click="publishBlog">Publish</button>
    </header>

    <main class="editor-main sr-scroll">
      <input 
        v-model="blogTitle" 
        class="title-input" 
        type="text" 
        placeholder="Enter title (optional)..." 
      />

      <div class="quill-wrapper sr-glass-panel">
        <QuillEditor 
          v-model:content="contentHtml" 
          contentType="html"
          :toolbar="editorOptions.modules.toolbar"  :options="editorOptions"
          :modules="editorModules"
        />
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
  color: var(--sr-text-secondary);
}

.primary-btn {
  background: rgba(68, 170, 255, 0.2);
  border-color: var(--sr-accent-color);
  color: var(--sr-accent-color);
  font-weight: bold;
}

.editor-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 20px;
  gap: 16px;
  overflow-y: auto;
}

.title-input {
  background: transparent;
  border: none;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  color: var(--sr-text-primary);
  font-size: 24px;
  font-weight: 600;
  padding: 10px 0;
  outline: none;
  font-family: var(--sr-font-family);
  transition: border-color 0.3s;
  flex-shrink: 0;
}

.title-input:focus {
  border-bottom-color: var(--sr-accent-color);
}

.quill-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  border-radius: 8px;
  overflow: hidden;
  min-height: 400px;
}

/* =========================================
   Quill style dark/glass morphism override
   ========================================= */

:deep(.ql-toolbar.ql-snow) {
  background: rgba(255, 255, 255, 0.05);
  border: none;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px 8px 0 0;
  padding: 12px;
  /* Allow line wrapping for multiple toolbar items */
  display: flex;
  flex-wrap: wrap;
  gap: 4px; 
}

/* Adjust spacing between toolbar groups */
:deep(.ql-toolbar.ql-snow .ql-formats) {
  margin-right: 12px;
  margin-bottom: 4px;
}

:deep(.ql-container.ql-snow) {
  border: none;
  font-family: var(--sr-font-family);
  font-size: 16px;
  color: rgba(255, 255, 255, 0.9);
  flex: 1;
}

:deep(.ql-editor) {
  min-height: 300px;
}

:deep(.ql-editor.ql-blank::before) {
  color: rgba(255, 255, 255, 0.3);
  font-style: normal;
}

/* Adapt stroke and fill color for all new icons */
:deep(.ql-snow .ql-stroke) { stroke: rgba(255, 255, 255, 0.7); }
:deep(.ql-snow .ql-fill) { fill: rgba(255, 255, 255, 0.7); }
:deep(.ql-snow .ql-picker) { color: rgba(255, 255, 255, 0.7); }

:deep(.ql-snow .ql-toolbar button:hover .ql-stroke),
:deep(.ql-snow .ql-toolbar button.ql-active .ql-stroke),
:deep(.ql-snow .ql-toolbar .ql-picker-label:hover .ql-stroke),
:deep(.ql-snow .ql-toolbar .ql-picker-label.ql-active .ql-stroke) {
  stroke: var(--sr-accent-color);
}

:deep(.ql-snow .ql-toolbar button:hover .ql-fill),
:deep(.ql-snow .ql-toolbar button.ql-active .ql-fill),
:deep(.ql-snow .ql-toolbar .ql-picker-label:hover .ql-fill),
:deep(.ql-snow .ql-toolbar .ql-picker-label.ql-active .ql-fill) {
  fill: var(--sr-accent-color);
}

/* Dark mode adaptation for dropdown menu inner list (e.g. title, font, font size dropdown) */
:deep(.ql-snow .ql-picker-options) {
  background-color: var(--sr-bg-glass);
  backdrop-filter: blur(12px);
  border: 1px solid var(--sr-border-glass);
  color: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
}

/* Dark mode adaptation for code block and blockquote */
:deep(.ql-editor pre.ql-syntax) {
  background-color: rgba(0, 0, 0, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #a6e22e; /* Minimal fluorescent green color scheme */
  border-radius: 6px;
}

:deep(.ql-editor blockquote) {
  border-left: 4px solid var(--sr-accent-color);
  background-color: rgba(255, 255, 255, 0.05);
  padding: 8px 16px;
  border-radius: 0 6px 6px 0;
  color: rgba(255, 255, 255, 0.7);
  font-style: italic;
}

/* Dark mode adaptation for the alignment toolbar popped up by BlotFormatter when selecting images */
:deep(.blot-formatter__toolbar) {
  background-color: var(--sr-bg-glass) !important;
  backdrop-filter: blur(8px);
  border: 1px solid var(--sr-border-glass) !important;
  border-radius: 6px !important;
}
:deep(.blot-formatter__button) {
  filter: invert(1); 
}
</style>