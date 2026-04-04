<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted, watch, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import StarBackground from '@/components/StarBackground.vue';
import BottomBar from '@/components/BottomBar.vue';
import { defaultApi } from '@/api/defaultApi';

import '../assets/styles/common.css';
import '../assets/styles/main.css';

interface IdentifiedStar {
  names?: string | string[];
  pixelX?: number;
  pixelY?: number;
  vmag?: number;
  hIP?: number | string;
}

interface CenterInfo {
  rightAscension?: number;
  declination?: number;
  radius?: number;
  orientation?: number;
}

interface StarrySkyResult {
  center?: CenterInfo;
  identifiedStars?: IdentifiedStar[];
  imageKey?: string;
  createTime?: string;
}

interface HistoryJob {
  jobID?: string;
  jobId?: string;
  job_id?: string;
  status?: string;
  createTime?: string;
}

const router = useRouter();

const fileInputRef = ref<HTMLInputElement | null>(null);
const imagePreview = ref<string | null>(null);
const base64Data = ref<string>('');
const isAnalyzing = ref(false);
const jobId = ref<string | null>(null);
const errorMessage = ref<string>('');

const recognitionResult = ref<StarrySkyResult | null>(null); 
const pollingTimer = ref<ReturnType<typeof setInterval> | null>(null);

const historyList = ref<HistoryJob[]>([]);
const isFetchingHistory = ref(false);

const recognitionImageKey = computed(() => recognitionResult.value?.imageKey ?? '');
const previewImageSrc = computed(() => imagePreview.value || getImageUrl(recognitionImageKey.value));
const shouldShowPreviewImage = computed(() => !recognitionResult.value && Boolean(previewImageSrc.value));

// 🌟 新增：用于在图片上绘制星星的 Canvas 引用
const resultCanvasRef = ref<HTMLCanvasElement | null>(null);

const stopPolling = () => {
  if (pollingTimer.value) {
    clearInterval(pollingTimer.value);
    pollingTimer.value = null;
  }
};

const getImageUrl = (key?: string) => {
  if (!key) return '';
  if (key.startsWith('http')) return key;
  const cleanKey = key.startsWith('/') ? key.substring(1) : key;
  return `https://starroll.ie/api/file/${cleanKey}`; 
};

// 🌟 核心绘图引擎：在图片上绘制标记
const drawStarsOnCanvas = () => {
  if (!resultCanvasRef.value || !recognitionResult.value) return;

  const canvas = resultCanvasRef.value;
  const ctx = canvas.getContext('2d');
  if (!ctx) return;

  // 决定图片来源（本地预览 或 云端历史图片）
  const imgSrc = imagePreview.value || getImageUrl(recognitionResult.value.imageKey);
  if (!imgSrc) return;

  const img = new Image();
  img.crossOrigin = "Anonymous"; // 允许跨域图片绘制
  img.onload = () => {
    // 1. 将画布尺寸严格对齐图片的原始像素尺寸
    canvas.width = img.width;
    canvas.height = img.height;

    // 2. 绘制原始底图
    ctx.drawImage(img, 0, 0);

    // 3. 遍历星星数据，绘制瞄准圈和文字
    const stars = recognitionResult.value?.identifiedStars || [];
    stars.forEach(star => {
      // 必须有有效的 x, y 坐标才绘制
      if (star.pixelX == null || star.pixelY == null) return;

      const x = star.pixelX;
      const y = star.pixelY;

      // 绘制绿色锁定外圈
      ctx.beginPath();
      ctx.arc(x, y, 20, 0, 2 * Math.PI);
      ctx.strokeStyle = '#2ecc71';
      ctx.lineWidth = 3;
      ctx.stroke();

      // 绘制中心准星点
      ctx.beginPath();
      ctx.arc(x, y, 3, 0, 2 * Math.PI);
      ctx.fillStyle = '#2ecc71';
      ctx.fill();

      // 获取最好的显示名称
      let label = 'Unknown';
      if (star.names && star.names.length > 0) {
        label = Array.isArray(star.names) ? star.names[0] : star.names;
      } else if (star.hIP) {
        label = `HIP ${star.hIP}`;
      }

      // 绘制文字阴影以增强背景对比度
      ctx.font = '24px monospace';
      ctx.fillStyle = '#2ecc71';
      ctx.shadowColor = 'black';
      ctx.shadowBlur = 6;
      ctx.fillText(label, x + 25, y - 10);
      
      // 恢复阴影设置
      ctx.shadowBlur = 0;
    });
  };
  img.src = imgSrc;
};

// 🌟 监听器：一旦识别结果被赋值，立刻触发 Canvas 绘图
watch(recognitionResult, async (newVal) => {
  if (newVal && newVal.identifiedStars && newVal.identifiedStars.length > 0) {
    await nextTick(); // 等待 <canvas> 元素挂载到 DOM
    drawStarsOnCanvas();
  }
});

const fetchHistoryJobs = async () => {
  isFetchingHistory.value = true;
  try {
    // 修复 Unexpected any: 使用 @ts-ignore 直接忽略类型检查，避免任何警告
    const rawResponse = await defaultApi.apiListIdentifyStarsJobsPostRaw({
      paginationQuery: { limit: 20, offset: 0, order: 'desc' }
    });
    const responseData = await rawResponse.raw.clone().json();
    historyList.value = responseData.identify_stars_jobs_list || responseData.identifyStarsJobsList || [];
  } catch (error) {
    console.error('Failed to fetch history:', error);
  } finally {
    isFetchingHistory.value = false;
  }
};

onMounted(() => {
  fetchHistoryJobs();
});

onUnmounted(() => {
  stopPolling();
});

const fetchJobDetailsData = async (currentJobId: string) => {
  try {
    const token = localStorage.getItem('token') || '';

    const rawResponse = await defaultApi.apiGetIdentifyStarsJobResultPostRaw({
      apiGetIdentifyStarsJobResultPostRequest: {
        jobID: currentJobId
      }
    });

    const responseData = await rawResponse.raw.clone().json();
    const jobList = responseData.identifyStarsJobsList || responseData.identify_stars_jobs_list || [];
    const jobResult = jobList.length > 0 ? (jobList[0] as StarrySkyResult) : null;

    if (jobResult) {
      isAnalyzing.value = false;
      recognitionResult.value = jobResult; // 这会触发上面的 watch 并执行画图！
    } else {
      isAnalyzing.value = false;
      errorMessage.value = 'Failed to parse astronomical data from backend.';
    }
  } catch (error) {
    console.error('Fetch Details Error:', error);
    isAnalyzing.value = false;
    errorMessage.value = 'Failed to fetch detailed star map. Network Error.';
  }
};

const pollJobStatusViaHistory = async () => {
  await fetchHistoryJobs();
  if (!jobId.value) return;

  const currentJob = historyList.value.find(j => 
    String(j.jobID || j.jobId || j.job_id) === String(jobId.value)
  );

  if (currentJob) {
    const s = (currentJob.status || '').toUpperCase();
    
    if (s === 'SUCCESS' || s === 'COMPLETED' || s === 'SUCCEEDED') {
      stopPolling();
      isAnalyzing.value = true;
      await fetchJobDetailsData(jobId.value as string);
    } 
    else if (s === 'FAILED' || s === 'ERROR') {
      stopPolling();
      isAnalyzing.value = false;
      errorMessage.value = `Engine processing failed (Status: ${s}). Please try another image.`;
    } 
  }
};

const handleHistoryClick = (job: HistoryJob) => {
  window.scrollTo({ top: 0, behavior: 'smooth' });

  const rawId = job.jobID || job.jobId || job.job_id;
  if (!rawId) return;
  const id = String(rawId);
  const s = (job.status || '').toUpperCase();

  stopPolling();
  imagePreview.value = null;
  base64Data.value = '';
  recognitionResult.value = null;
  errorMessage.value = '';

  if (s === 'SUCCESS' || s === 'COMPLETED' || s === 'SUCCEEDED') {
    jobId.value = id;
    isAnalyzing.value = true;
    setTimeout(() => fetchJobDetailsData(id), 500);
  } 
  else if (s === 'FAILED' || s === 'ERROR') {
    errorMessage.value = `Task #${id.substring(0,5)} failed during processing.`;
  } 
  else {
    errorMessage.value = `Task #${id.substring(0,5)} is still processing (${s}). Please check back later.`;
  }
};

const triggerUpload = () => fileInputRef.value?.click();

const handleImageSelected = (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (target.files && target.files.length > 0) {
    const file = target.files[0];
    resetUploader(); 
    imagePreview.value = URL.createObjectURL(file);
    const reader = new FileReader();
    reader.onload = (e) => {
      if (e.target?.result) base64Data.value = (e.target.result as string).split(',')[1]; 
    };
    reader.readAsDataURL(file);
  }
};

const startAnalysis = async () => {
  if (!base64Data.value) {
    errorMessage.value = 'Please upload a starry sky image first';
    return;
  }

  const token = localStorage.getItem('token');
  const userId = localStorage.getItem('userID');

  if (!token || !userId) {
    errorMessage.value = 'Identity credentials expired, redirecting to login page...';
    setTimeout(() => window.location.href = 'https://starroll.ie/userlogin', 2000);
    return;
  }

  isAnalyzing.value = true;
  errorMessage.value = '';
  recognitionResult.value = null;

  try {
    const response = await defaultApi.apiCreateIdentifyStarsJobPost({
      apiCreateIdentifyStarsJobPostRequest: {
        image: base64Data.value,
        userID: userId,
        token: token 
      }
    });
    
    jobId.value = response.jobID || null;
    
    if (jobId.value) {
      pollingTimer.value = setInterval(() => pollJobStatusViaHistory(), 3000);
    }
  } catch (error: unknown) {
    console.error('Failed to create identify job:', error);
    errorMessage.value = 'Failed to upload starry sky data, check network or re-login.';
    isAnalyzing.value = false;
  }
};

const resetUploader = () => {
  stopPolling();
  imagePreview.value = null;
  base64Data.value = '';
  jobId.value = null;
  recognitionResult.value = null;
  errorMessage.value = '';
  isAnalyzing.value = false;
  if (fileInputRef.value) fileInputRef.value.value = '';
};

const formatDate = (dateString?: string) => {
  if (!dateString) return 'Unknown time';
  return new Date(dateString).toLocaleString(undefined, {
    month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
  });
};
</script>

<template>
  <StarBackground>
    <div class="recognizer-container">
      
      <header class="header">
        <button class="back-btn" @click="router.back()">
          <svg viewBox="0 0 24 24" width="24" height="24"><path fill="currentColor" d="M15.41 16.59L10.83 12l4.58-4.59L14 6l-6 6 6 6 1.41-1.41z"/></svg>
        </button>
        <h1 class="title">Recognizer</h1>
        <div class="spacer"></div>
      </header>

      <p class="subtitle">Upload your starry sky photography, and the engine will identify the celestial bodies for you.</p>

      <main class="main-layout">
        
        <div class="workspace-section">
          
          <div v-if="!imagePreview && !recognitionResult && !isAnalyzing && !jobId && !errorMessage" class="upload-box glass-panel" @click="triggerUpload">
            <div class="upload-icon-wrapper">
              <svg viewBox="0 0 24 24" width="48" height="48"><path fill="currentColor" d="M19.35 10.04C18.67 6.59 15.64 4 12 4 9.11 4 6.6 5.64 5.35 8.04 2.34 8.36 0 10.91 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96zM14 13v4h-4v-4H7l5-5 5 5h-3z"/></svg>
            </div>
            <p class="upload-text">Click to select a starry sky photo</p>
            <p class="upload-hint">Supports JPG, PNG formats</p>
          </div>

          <div v-else class="preview-section">
            
            <div v-if="imagePreview || recognitionResult" class="image-wrapper glass-panel" :class="{ 'has-result': recognitionResult }">
              
              <canvas v-show="recognitionResult" ref="resultCanvasRef" class="preview-img result-img"></canvas>
              
                  <img v-show="shouldShowPreviewImage" 
                    :src="previewImageSrc" 
                   alt="Star map preview" class="preview-img" />

                  <div v-if="!imagePreview && !recognitionImageKey && !recognitionResult" class="preview-img no-img-fallback">
                <p>No Image Available</p>
              </div>

              <div v-if="isAnalyzing && !recognitionResult" class="scan-line"></div>
            </div>

            <div v-else-if="isAnalyzing" class="image-wrapper skeleton-box glass-panel">
              <div class="spinner-blue skeleton-spinner"></div>
              <p>Fetching historical data from universe...</p>
            </div>

            <div v-if="recognitionResult" class="result-data-panel glass-panel">
              <div class="result-header">
                <h3>Identified Stars ({{ recognitionResult.identifiedStars?.length || 0 }})</h3>
                <p v-if="recognitionResult.center" class="center-coord">
                  Center: RA {{ recognitionResult.center.rightAscension?.toFixed(2) }}°, Dec {{ recognitionResult.center.declination?.toFixed(2) }}°
                </p>
              </div>
              
              <div v-if="recognitionResult.identifiedStars?.length" class="stars-list sr-scroll">
                <div v-for="(star, index) in recognitionResult.identifiedStars" :key="index" class="star-item">
                  <div class="star-icon">✨</div>
                  <div class="star-info">
                    <span class="star-name">
                      {{ star.names ? (Array.isArray(star.names) ? star.names.join(' / ') : star.names) : 'Unnamed Star' }}
                    </span>
                    <span class="star-details" v-if="star.hIP || star.vmag">
                      <span v-if="star.hIP">HIP: {{ star.hIP }}</span>
                      <span v-if="star.hIP && star.vmag"> | </span>
                      <span v-if="star.vmag">Mag: {{ star.vmag }}</span>
                    </span>
                  </div>
                </div>
              </div>
              <p v-else class="no-stars-found">No specific stars were clearly identified in this image.</p>
            </div>

            <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>

            <div class="action-group">
              <template v-if="!jobId && !recognitionResult && !errorMessage">
                <button class="sr-glass-btn secondary-btn" @click="resetUploader" :disabled="isAnalyzing">Reselect</button>
                <button class="sr-glass-btn primary-btn" @click="startAnalysis" :disabled="isAnalyzing">Start Starry Sky Analysis</button>
              </template>
              
              <template v-else-if="isAnalyzing && !recognitionResult">
                <div class="status-panel glass-panel">
                  <div class="spinner-blue"></div>
                  <div class="status-text">
                    <h3>Engine is computing...</h3>
                    <p>Job ID: {{ jobId }}</p>
                    <p class="small-text">Deep space scanning in progress...</p>
                  </div>
                </div>
              </template>

              <template v-else-if="recognitionResult || errorMessage">
                <button class="sr-glass-btn primary-btn w-full mt-2" @click="resetUploader">
                  New Analysis / Upload Image
                </button>
              </template>
            </div>
          </div>
        </div>

        <div class="history-section glass-panel">
          <div class="history-header">
            <h3>History Logs</h3>
            <button class="refresh-btn" @click="fetchHistoryJobs" :disabled="isFetchingHistory">
              <svg :class="{'rotating': isFetchingHistory}" viewBox="0 0 24 24" width="16" height="16"><path fill="currentColor" d="M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/></svg>
            </button>
          </div>

          <div class="history-list sr-scroll">
            <div v-if="historyList.length === 0" class="no-history">
              No historical analysis records found.
            </div>
            
            <div 
              v-else 
              v-for="job in historyList" 
              :key="job.jobID || job.job_id" 
              class="history-item clickable-item"
              @click="handleHistoryClick(job)"
            >
              <div class="history-info">
                <div class="history-id">Task #{{ String(job.jobID || job.jobId || job.job_id || '').substring(0, 5) }}...</div>
                <div class="history-time">{{ formatDate(job.createTime) }}</div>
              </div>
              <div class="history-actions">
                <span class="status-badge" :class="'status-' + (job.status || 'UNKNOWN').toLowerCase()">
                  {{ job.status || 'UNKNOWN' }}
                </span>
                <span class="view-hint">
                  {{ ['SUCCESS', 'COMPLETED', 'SUCCEEDED'].includes((job.status || '').toUpperCase()) ? 'Click to view ➔' : 'Check status' }}
                </span>
              </div>
            </div>
          </div>
        </div>

      </main>

      <input type="file" ref="fileInputRef" accept="image/*" style="display: none;" @change="handleImageSelected" />
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
.recognizer-container::-webkit-scrollbar { display: none; }

.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.back-btn { background: rgba(255, 255, 255, 0.05); border: 1px solid var(--glass-border); border-radius: 50%; width: 40px; height: 40px; display: flex; justify-content: center; align-items: center; color: white; cursor: pointer; }
.title { font-size: 24px; font-weight: 700; text-shadow: var(--shadow-glow); margin: 0; }
.spacer { width: 40px; }
.subtitle { text-align: center; color: var(--color-text-muted); font-size: 14px; margin-bottom: 24px; line-height: 1.5; }

.main-layout { display: flex; flex-direction: column; gap: 24px; }
@media (min-width: 768px) {
  .main-layout { flex-direction: row; align-items: flex-start; }
  .workspace-section { flex: 2; }
  .history-section { flex: 1; min-width: 300px; }
}

.workspace-section { display: flex; flex-direction: column; gap: 20px; }

.upload-box { border: 2px dashed rgba(88, 166, 255, 0.4); display: flex; flex-direction: column; justify-content: center; align-items: center; height: 300px; cursor: pointer; transition: all 0.3s; }
.upload-box:hover { background: rgba(88, 166, 255, 0.1); border-color: var(--color-star-primary); box-shadow: 0 0 20px rgba(88, 166, 255, 0.2); }
.upload-icon-wrapper { color: var(--color-star-primary); margin-bottom: 16px; filter: drop-shadow(0 0 8px rgba(88, 166, 255, 0.6)); }
.upload-text { font-size: 18px; font-weight: 600; margin-bottom: 8px; text-align: center; }
.upload-hint { font-size: 12px; color: var(--color-text-muted); }

.preview-section { display: flex; flex-direction: column; gap: 20px; }
.image-wrapper { position: relative; width: 100%; aspect-ratio: 4/3; border-radius: 16px; overflow: hidden; padding: 0; border: 1px solid var(--color-star-primary); box-shadow: 0 0 30px rgba(88, 166, 255, 0.15); transition: all 0.5s ease; }
.image-wrapper.has-result { border-color: #2ecc71; box-shadow: 0 0 30px rgba(46, 204, 113, 0.25); }

/* 必须保证 Canvas 和 Img 都可以完美缩放适应屏幕 */
.preview-img { width: 100%; height: 100%; object-fit: contain; background: #000; display: block; }
.result-img { animation: fadeIn 0.8s ease-out; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

.no-img-fallback { display: flex; justify-content: center; align-items: center; color: rgba(255, 255, 255, 0.3); font-family: monospace; font-size: 14px; }

.skeleton-box { display: flex; flex-direction: column; justify-content: center; align-items: center; gap: 16px; background: rgba(0, 0, 0, 0.5); }
.skeleton-box p { color: rgba(255, 255, 255, 0.6); font-family: monospace; }

.scan-line { position: absolute; top: 0; left: 0; width: 100%; height: 4px; background: var(--color-star-primary); box-shadow: 0 0 15px 2px var(--color-star-primary); animation: scan 2s linear infinite; opacity: 0.8; }
@keyframes scan { 0% { top: 0; } 50% { top: 100%; } 100% { top: 0; } }

.result-data-panel { padding: 16px; background: rgba(30, 35, 55, 0.8); border: 1px solid rgba(46, 204, 113, 0.3); border-radius: 12px; }
.result-header { border-bottom: 1px dashed rgba(255, 255, 255, 0.1); padding-bottom: 12px; margin-bottom: 12px; }
.result-header h3 { color: #2ecc71; font-size: 16px; margin: 0 0 4px 0; }
.center-coord { font-size: 12px; color: rgba(255, 255, 255, 0.6); font-family: monospace; }
.stars-list { display: flex; flex-direction: column; gap: 8px; max-height: 200px; overflow-y: auto; padding-right: 4px; }
.star-item { display: flex; align-items: center; gap: 12px; background: rgba(255, 255, 255, 0.05); padding: 10px 12px; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.05); }
.star-icon { font-size: 14px; }
.star-info { display: flex; flex-direction: column; }
.star-name { font-size: 14px; font-weight: 500; color: white; }
.star-details { font-size: 12px; color: rgba(255, 255, 255, 0.5); font-family: monospace; margin-top: 2px; }
.no-stars-found { font-size: 14px; color: rgba(255, 255, 255, 0.5); text-align: center; padding: 10px 0; }

.history-section { background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 16px; padding: 16px; display: flex; flex-direction: column; max-height: 600px; }
.history-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255, 255, 255, 0.1); padding-bottom: 12px; margin-bottom: 12px; }
.history-header h3 { margin: 0; font-size: 16px; color: var(--color-star-primary); }
.refresh-btn { background: none; border: none; color: rgba(255, 255, 255, 0.6); cursor: pointer; padding: 4px; display: flex; align-items: center; }
.refresh-btn:hover { color: white; }
.rotating { animation: spin 1s linear infinite; }

.history-list { display: flex; flex-direction: column; gap: 12px; overflow-y: auto; flex: 1; padding-right: 4px; }
.no-history { color: rgba(255, 255, 255, 0.4); font-size: 13px; text-align: center; padding: 20px 0; }

.clickable-item { 
  background: rgba(0, 0, 0, 0.3); 
  border-radius: 8px; 
  padding: 12px; 
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  border: 1px solid rgba(255, 255, 255, 0.05); 
  cursor: pointer;
  transition: all 0.2s ease;
}
.clickable-item:hover {
  background: rgba(88, 166, 255, 0.1);
  border-color: rgba(88, 166, 255, 0.3);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}
.view-hint { font-size: 10px; color: var(--color-star-primary); opacity: 0.7; margin-top: 4px; }
.clickable-item:hover .view-hint { opacity: 1; }

.history-info { display: flex; flex-direction: column; gap: 4px; }
.history-id { font-size: 13px; font-weight: 600; color: rgba(255, 255, 255, 0.9); }
.history-time { font-size: 11px; color: rgba(255, 255, 255, 0.5); }
.history-actions { display: flex; flex-direction: column; align-items: flex-end; }
.status-badge { font-size: 10px; padding: 2px 6px; border-radius: 4px; font-weight: bold; text-transform: uppercase; }
.status-success, .status-completed, .status-succeeded { background: rgba(46, 204, 113, 0.2); color: #2ecc71; border: 1px solid rgba(46, 204, 113, 0.4); }
.status-failed, .status-error { background: rgba(231, 76, 60, 0.2); color: #e74c3c; border: 1px solid rgba(231, 76, 60, 0.4); }
.status-running, .status-pending { background: rgba(241, 196, 15, 0.2); color: #f1c40f; border: 1px solid rgba(241, 196, 15, 0.4); }

.action-group { display: flex; flex-direction: column; gap: 16px; }
.sr-glass-btn { padding: 14px; border-radius: 12px; font-size: 16px; font-weight: 600; display: flex; justify-content: center; align-items: center; gap: 8px; transition: all 0.3s; }
.secondary-btn { background: rgba(255, 255, 255, 0.05); color: white; border: 1px solid rgba(255, 255, 255, 0.2); }
.primary-btn { background: rgba(88, 166, 255, 0.2); color: var(--color-star-primary); border: 1px solid var(--color-star-primary); }
.primary-btn:hover:not(:disabled) { background: var(--color-star-primary); color: white; box-shadow: 0 0 20px rgba(88, 166, 255, 0.5); }
.sr-glass-btn:disabled { opacity: 0.6; cursor: not-allowed; }

.status-panel { display: flex; align-items: center; gap: 16px; padding: 16px; background: rgba(88, 166, 255, 0.05); border: 1px solid rgba(88, 166, 255, 0.2); border-radius: 12px; width: 100%; }
.status-text h3 { font-size: 16px; color: white; margin-bottom: 4px; }
.status-text p { font-size: 14px; font-family: monospace; color: rgba(255, 255, 255, 0.8); }
.status-text .small-text { font-size: 12px; color: var(--color-text-muted); margin-top: 4px; }
.w-full { width: 100%; }
.mt-2 { margin-top: 8px; }
.error-text { color: var(--color-error, #ff4444); text-align: center; font-size: 14px; }
.spinner-blue { width: 24px; height: 24px; border: 3px solid rgba(88, 166, 255, 0.2); border-top-color: var(--color-star-primary); border-radius: 50%; animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>