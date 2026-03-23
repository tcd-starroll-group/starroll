<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import StarBackground from '@/components/StarBackground.vue';
import BottomBar from '@/components/BottomBar.vue';
import { defaultApi } from '@/api/defaultApi';

// Import global common styles
import '../assets/styles/common.css';
import '../assets/styles/main.css';

const router = useRouter();

// State management
const fileInputRef = ref<HTMLInputElement | null>(null);
const imagePreview = ref<string | null>(null);
const base64Data = ref<string>('');
const isAnalyzing = ref(false);
const jobId = ref<string | null>(null);
const errorMessage = ref<string>('');

// Trigger file selection
const triggerUpload = () => {
  fileInputRef.value?.click();
};

// Handle image selection and Base64 encoding
const handleImageSelected = (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (target.files && target.files.length > 0) {
    const file = target.files[0];
    errorMessage.value = '';
    jobId.value = null;
    
    // Generate local preview URL
    imagePreview.value = URL.createObjectURL(file);

    // Convert image to Base64
    const reader = new FileReader();
    reader.onload = (e) => {
      if (e.target?.result) {
        const resultString = e.target.result as string;
        // Remove prefix like "data:image/jpeg;base64,", backend only needs pure encoding
        base64Data.value = resultString.split(',')[1]; 
      }
    };
    reader.readAsDataURL(file);
  }
};

// Call API to submit recognition task
const startAnalysis = async () => {
  if (!base64Data.value) {
    errorMessage.value = 'Please upload a starry sky image first';
    return;
  }

  const token = localStorage.getItem('token');
  const userId = localStorage.getItem('userID') || '2';

  if (!token ) {
    errorMessage.value = 'Identity credentials expired, redirecting to login page...';
    // Use window.location.href to force browser redirect to online environment
    setTimeout(() => {
      window.location.href = 'https://starroll.ie/userlogin';
    }, 2000);
    return;
  }

  isAnalyzing.value = true;
  errorMessage.value = '';

  try {
    // 🚀 Use encapsulated defaultApi to send request
    const response = await defaultApi.apiCreateIdentifyStarsJobPost({
      apiCreateIdentifyStarsJobPostRequest: {
        image: base64Data.value,
        userID: userId,
        // According to openapiv3.yaml definition, token still needs to be passed in body even if included in request header
        token: token 
      }
    });

    console.log('Job created successfully:', response);
    
    // API automatically parses JSON response, read properties directly
    jobId.value = response.jobID || null;
    
    if (jobId.value) {
      console.log('Preparing to poll Job:', jobId.value);
      // TODO: Polling logic will be added here in next step
    }

  } catch (error: unknown) {
    console.error('Failed to create identify job:', error);
    errorMessage.value = 'Failed to upload starry sky data, check network or re-login.';
  } finally {
    isAnalyzing.value = false;
  }
};

// Reselect image
const resetUploader = () => {
  imagePreview.value = null;
  base64Data.value = '';
  jobId.value = null;
  errorMessage.value = '';
  if (fileInputRef.value) {
    fileInputRef.value.value = '';
  }
};
</script>

<template>
  <StarBackground>
    <div class="recognizer-container">
      
      <header class="header">
        <button class="back-btn" @click="router.back()">
          <svg viewBox="0 0 24 24" width="24" height="24">
            <path fill="currentColor" d="M15.41 16.59L10.83 12l4.58-4.59L14 6l-6 6 6 6 1.41-1.41z"/>
          </svg>
        </button>
        <h1 class="title">Recognizer</h1>
        <div class="spacer"></div>
      </header>

      <main class="main-content">
        <p class="subtitle">Upload your starry sky photography, and the engine will mark constellations and celestial bodies for you.</p>

        <div 
          v-if="!imagePreview" 
          class="upload-box glass-panel" 
          @click="triggerUpload"
        >
          <div class="upload-icon-wrapper">
            <svg viewBox="0 0 24 24" width="48" height="48">
              <path fill="currentColor" d="M19.35 10.04C18.67 6.59 15.64 4 12 4 9.11 4 6.6 5.64 5.35 8.04 2.34 8.36 0 10.91 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96zM14 13v4h-4v-4H7l5-5 5 5h-3z"/>
            </svg>
          </div>
          <p class="upload-text">Click to select a starry sky photo</p>
          <p class="upload-hint">Supports JPG, PNG formats</p>
        </div>

        <div v-else class="preview-section">
          <div class="image-wrapper glass-panel">
            <img :src="imagePreview" alt="Star map preview" class="preview-img" />
            <div v-if="isAnalyzing" class="scan-line"></div>
          </div>

          <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>

          <div class="action-group">
            <template v-if="!jobId">
              <button 
                class="sr-glass-btn secondary-btn" 
                @click="resetUploader" 
                :disabled="isAnalyzing"
              >
                Reselect Image
              </button>
              <button 
                class="sr-glass-btn primary-btn" 
                @click="startAnalysis"
                :disabled="isAnalyzing"
              >
                <span v-if="isAnalyzing" class="spinner"></span>
                {{ isAnalyzing ? 'Uploading to processing center...' : 'Start Starry Sky Analysis' }}
              </button>
            </template>
            
            <template v-else>
              <div class="success-panel glass-panel">
                <svg class="success-icon" viewBox="0 0 24 24" width="24" height="24">
                  <path fill="currentColor" d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z"/>
                </svg>
                <div class="success-text">
                  <h3>Task Created</h3>
                  <p>Job ID: {{ jobId }}</p>
                  <p class="small-text">Engine is processing, please wait...</p>
                </div>
              </div>
              <button class="sr-glass-btn secondary-btn w-full mt-4" @click="resetUploader">
                Analyze Next Image
              </button>
            </template>
          </div>
        </div>

        <input 
          type="file" 
          ref="fileInputRef" 
          accept="image/*" 
          style="display: none;" 
          @change="handleImageSelected"
        />
      </main>

    </div>

    <BottomBar />
  </StarBackground>
</template>

<style scoped>
.recognizer-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  padding: 24px 20px 100px 20px;
  color: var(--color-text-main);
  overflow-y: auto;
  scrollbar-width: none;
}
.recognizer-container::-webkit-scrollbar {
  display: none;
}

/* Header */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}
.back-btn {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--glass-border);
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  justify-content: center;
  align-items: center;
  color: white;
  cursor: pointer;
}
.title {
  font-size: 24px;
  font-weight: 700;
  text-shadow: var(--shadow-glow);
}
.spacer {
  width: 40px;
}

.subtitle {
  text-align: center;
  color: var(--color-text-muted);
  font-size: 14px;
  margin-bottom: 32px;
  line-height: 1.5;
}

/* Upload dashed box */
.upload-box {
  border: 2px dashed rgba(88, 166, 255, 0.4);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 300px;
  cursor: pointer;
  transition: all 0.3s;
}
.upload-box:hover {
  background: rgba(88, 166, 255, 0.1);
  border-color: var(--color-star-primary);
  box-shadow: 0 0 20px rgba(88, 166, 255, 0.2);
}
.upload-icon-wrapper {
  color: var(--color-star-primary);
  margin-bottom: 16px;
  filter: drop-shadow(0 0 8px rgba(88, 166, 255, 0.6));
}
.upload-text {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 8px;
}
.upload-hint {
  font-size: 12px;
  color: var(--color-text-muted);
}

/* Preview area */
.preview-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.image-wrapper {
  position: relative;
  width: 100%;
  aspect-ratio: 4/3;
  border-radius: 16px;
  overflow: hidden;
  padding: 0;
  border: 1px solid var(--color-star-primary);
  box-shadow: 0 0 30px rgba(88, 166, 255, 0.15);
}
.preview-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  background: #000;
}

/* Sci-fi scan line animation */
.scan-line {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 4px;
  background: var(--color-star-primary);
  box-shadow: 0 0 15px 2px var(--color-star-primary);
  animation: scan 2s linear infinite;
  opacity: 0.8;
}

@keyframes scan {
  0% { top: 0; }
  50% { top: 100%; }
  100% { top: 0; }
}

/* Button group */
.action-group {
  display: flex;
  gap: 16px;
}
.sr-glass-btn {
  flex: 1;
  padding: 14px;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  transition: all 0.3s;
}
.secondary-btn {
  background: rgba(255, 255, 255, 0.05);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.2);
}
.primary-btn {
  background: rgba(88, 166, 255, 0.2);
  color: var(--color-star-primary);
  border: 1px solid var(--color-star-primary);
}
.primary-btn:hover:not(:disabled) {
  background: var(--color-star-primary);
  color: white;
  box-shadow: 0 0 20px rgba(88, 166, 255, 0.5);
}
.sr-glass-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Success panel */
.success-panel {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: rgba(46, 204, 113, 0.1);
  border-color: rgba(46, 204, 113, 0.4);
  border-radius: 12px;
  width: 100%;
}
.success-icon {
  color: #2ecc71;
  filter: drop-shadow(0 0 8px rgba(46, 204, 113, 0.6));
}
.success-text h3 {
  font-size: 16px;
  color: #2ecc71;
  margin-bottom: 4px;
}
.success-text p {
  font-size: 14px;
  font-family: monospace;
  color: rgba(255, 255, 255, 0.8);
}
.success-text .small-text {
  font-size: 12px;
  color: var(--color-text-muted);
  margin-top: 4px;
}
.w-full { width: 100%; }
.mt-4 { margin-top: 16px; }

/* Error text */
.error-text {
  color: var(--color-error, #ff4444);
  text-align: center;
  font-size: 14px;
}

/* Loading spin animation */
.spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>