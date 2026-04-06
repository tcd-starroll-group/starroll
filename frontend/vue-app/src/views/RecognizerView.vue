<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted, watch, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import StarBackground from '@/components/StarBackground.vue';
import { defaultApi } from '@/api/defaultApi';
import type { IdentifyStarsJob, IdentifyStarsJobResult } from '../../../../gen/ts';

import '../assets/styles/common.css';
import '../assets/styles/main.css';

const router = useRouter();

const fileInputRef = ref<HTMLInputElement | null>(null);
const imagePreview = ref<string | null>(null);
const base64Data = ref<string>('');
const isAnalyzing = ref(false);
const jobId = ref<string | null>(null);
const errorMessage = ref<string>('');

const recognitionResult = ref<IdentifyStarsJobResult | null>(null);
const pollingTimer = ref<ReturnType<typeof setInterval> | null>(null);

const historyList = ref<IdentifyStarsJob[]>([]);
const isFetchingHistory = ref(false);

const recognitionImageKey = computed(() => recognitionResult.value?.oriImageUrl ?? '');
const previewImageSrc = computed(() => imagePreview.value || recognitionImageKey.value);
const shouldShowPreviewImage = computed(() => !recognitionResult.value && Boolean(previewImageSrc.value));

// 🌟 新增：用于在图片上绘制星星的 Canvas 引用
const resultCanvasRef = ref<HTMLCanvasElement | null>(null);

// 🌟 标记开关：控制是否显示绘制标记
const showMarkers = ref(true);

// 🌟 选中的星星索引（null 表示未选中任何星星）
const selectedStarIndex = ref<number | null>(null);

// 🌟 星星列表容器 ref，用于自动滚动
const starsListRef = ref<HTMLElement | null>(null);
const starItemRefs = ref<HTMLElement[]>([]);

const stopPolling = () => {
  if (pollingTimer.value) {
    clearInterval(pollingTimer.value);
    pollingTimer.value = null;
  }
};

// 🌟 核心绘图引擎：在图片上绘制标记
const drawStarsOnCanvas = () => {
  if (!resultCanvasRef.value || !recognitionResult.value) return;

  const canvas = resultCanvasRef.value;
  const ctx = canvas.getContext('2d');
  if (!ctx) return;

  // 决定图片来源（本地预览 或 云端历史图片）
  const imgSrc = imagePreview.value || recognitionResult.value.oriImageUrl;
  if (!imgSrc) return;

  const img = new Image();
  img.onload = () => {
    // 1. 将画布尺寸严格对齐图片的原始像素尺寸
    canvas.width = img.width;
    canvas.height = img.height;

    // 2. 绘制原始底图
    ctx.drawImage(img, 0, 0);

    // 3. 若标记开关关闭，仅显示原图
    if (!showMarkers.value) return;

    // 4. 遍历星星数据，绘制瞄准圈和文字
    const stars = recognitionResult.value?.identifiedStars || [];
    const hasSelection = selectedStarIndex.value !== null;

    stars.forEach((star, index) => {
      // 必须有有效的 x, y 坐标才绘制
      if (star.pixelX == null || star.pixelY == null) return;

      const x = star.pixelX;
      const y = star.pixelY;
      const isSelected = selectedStarIndex.value === index;
      const isDimmed = hasSelection && !isSelected;

      // 根据状态设置颜色和尺寸
      const color = isDimmed ? 'rgba(46, 204, 113, 0.12)' : '#2ecc71';
      const outerRadius = isSelected ? 26 : 20;
      const lineWidth = isSelected ? 4 : (isDimmed ? 1.5 : 2.5);

      // 选中状态绘制双圈
      if (isSelected) {
        ctx.beginPath();
        ctx.arc(x, y, 36, 0, 2 * Math.PI);
        ctx.strokeStyle = 'rgba(46, 204, 113, 0.4)';
        ctx.lineWidth = 1.5;
        ctx.setLineDash([4, 4]);
        ctx.stroke();
        ctx.setLineDash([]);
      }

      // 绘制锁定外圈
      ctx.beginPath();
      ctx.arc(x, y, outerRadius, 0, 2 * Math.PI);
      ctx.strokeStyle = color;
      ctx.lineWidth = lineWidth;
      ctx.stroke();

      // 获取最好的显示名称
      let label = 'Unknown';
      if (star.names && star.names.length > 0) {
        label = star.names[0];
      } else if (star.hIP) {
        label = `HIP ${star.hIP}`;
      }

      // 绘制文字
      ctx.font = isSelected ? 'bold 26px monospace' : '22px monospace';
      ctx.fillStyle = color;
      ctx.shadowColor = isDimmed ? 'transparent' : 'black';
      ctx.shadowBlur = isDimmed ? 0 : 6;
      ctx.fillText(label, x + outerRadius + 6, y - 8);
      ctx.shadowBlur = 0;
    });
  };
  img.src = imgSrc;
};

// 🌟 Canvas 点击处理：检测点击位置最近的星星
const handleCanvasClick = (event: MouseEvent) => {
  if (!recognitionResult.value || !resultCanvasRef.value || !showMarkers.value) return;

  const canvas = resultCanvasRef.value;
  const rect = canvas.getBoundingClientRect();
  // 将屏幕坐标映射回 Canvas 原始像素坐标
  const scaleX = canvas.width / rect.width;
  const scaleY = canvas.height / rect.height;
  const clickX = (event.clientX - rect.left) * scaleX;
  const clickY = (event.clientY - rect.top) * scaleY;

  const stars = recognitionResult.value.identifiedStars || [];
  let closestIndex: number | null = null;
  let closestDist = Infinity;
  const HIT_RADIUS = 40; // 点击容忍半径（原始像素）

  stars.forEach((star, index) => {
    if (star.pixelX == null || star.pixelY == null) return;
    const dx = clickX - star.pixelX;
    const dy = clickY - star.pixelY;
    const dist = Math.sqrt(dx * dx + dy * dy);
    if (dist <= HIT_RADIUS && dist < closestDist) {
      closestDist = dist;
      closestIndex = index;
    }
  });

  // 再次点击同一颗星则取消选中
  selectedStarIndex.value = closestIndex === selectedStarIndex.value ? null : closestIndex;
};

// 🌟 监听器：一旦识别结果被赋值，立刻触发 Canvas 绘图
watch(recognitionResult, async (newVal) => {
  if (newVal && newVal.identifiedStars && newVal.identifiedStars.length > 0) {
    selectedStarIndex.value = null; // 重置选中状态
    starItemRefs.value = [];        // 清空列表 ref 缓存
    await nextTick(); // 等待 <canvas> 元素挂载到 DOM
    drawStarsOnCanvas();
  }
});

// 🌟 监听标记开关：切换时立刻重绘
watch(showMarkers, () => {
  drawStarsOnCanvas();
});

// 🌟 监听选中星星：重绘 Canvas，并将列表滚到对应项
watch(selectedStarIndex, async (newIndex) => {
  drawStarsOnCanvas();
  if (newIndex !== null) {
    await nextTick();
    const el = starItemRefs.value[newIndex];
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
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
    historyList.value = responseData.identifyStarsJobsList || [];
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
    const jobResult = await defaultApi.apiGetIdentifyStarsJobResultPost({
      apiGetIdentifyStarsJobResultPostRequest: {
        jobID: currentJobId
      }
    });

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
    String(j.jobID) === String(jobId.value)
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

const handleHistoryClick = (job: IdentifyStarsJob) => {
  window.scrollTo({ top: 0, behavior: 'smooth' });

  const rawId = job.jobID;
  if (!rawId) return;
  const id = String(rawId);
  const s = (job.status || '').toUpperCase();

  stopPolling();
  imagePreview.value = null;
  base64Data.value = '';
  recognitionResult.value = null;
  errorMessage.value = '';
  selectedStarIndex.value = null;
  starItemRefs.value = [];

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
  selectedStarIndex.value = null;
  starItemRefs.value = [];
  if (fileInputRef.value) fileInputRef.value.value = '';
};

const formatDate = (dateString?: string) => {
  if (!dateString) return 'Unknown time';
  return new Date(dateString).toLocaleString(undefined, {
    month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
  });
};

const navigateToAR = (hip: number) => {
  const base = import.meta.env.BASE_URL?.replace(/\/$/, '') ?? '';
  window.location.href = `${base}/?find_hip=${hip}`;
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

              <!-- 标记开关浮层 -->
              <div v-if="recognitionResult" class="canvas-controls">
                <button
                  class="marker-toggle-btn"
                  :class="{ active: showMarkers }"
                  @click.stop="showMarkers = !showMarkers"
                  :title="showMarkers ? 'Hide markers' : 'Show markers'"
                >
                  <svg viewBox="0 0 24 24" width="14" height="14">
                    <path fill="currentColor" d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/>
                  </svg>
                  {{ showMarkers ? 'Markers ON' : 'Markers OFF' }}
                </button>
              </div>

              <canvas
                v-show="recognitionResult"
                ref="resultCanvasRef"
                class="preview-img result-img"
                :style="{ cursor: showMarkers && recognitionResult ? 'crosshair' : 'default' }"
                @click="handleCanvasClick"
              ></canvas>
              
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
              
              <div v-if="recognitionResult.identifiedStars?.length" class="stars-list sr-scroll" ref="starsListRef">
                <div
                  v-for="(star, index) in recognitionResult.identifiedStars"
                  :key="index"
                  class="star-item"
                  :class="{ 'star-item-selected': selectedStarIndex === index }"
                  :ref="(el: any) => { if (el) starItemRefs[index] = el as HTMLElement }"
                  @click="selectedStarIndex = selectedStarIndex === index ? null : index"
                >
                  <div class="star-icon">✨</div>
                  <div class="star-info">
                    <span class="star-name">
                      {{ star.names?.length ? star.names.join(' / ') : 'Unnamed Star' }}
                    </span>
                    <span class="star-details" v-if="star.hIP || star.vmag">
                      <span v-if="star.hIP">HIP: {{ star.hIP }}</span>
                      <span v-if="star.hIP && star.vmag"> | </span>
                      <span v-if="star.vmag">Mag: {{ star.vmag }}</span>
                    </span>
                  </div>
                  <button v-if="star.hIP" class="find-ar-btn-inline" @click.stop="navigateToAR(star.hIP)">
                    <svg viewBox="0 0 24 24" width="12" height="12">
                      <path fill="currentColor" d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/>
                    </svg>
                    Find in AR
                  </button>
                </div>
              </div>
              <p v-else class="no-stars-found">No specific stars were clearly identified in this image.</p>
            </div>

            <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>

            <div class="action-group">
              <template v-if="!jobId && !recognitionResult && !errorMessage">
                <button class="sr-glass-btn secondary-btn" @click="resetUploader" :disabled="isAnalyzing">Reselect</button>
                <button class="sr-glass-btn primary-btn" @click="startAnalysis" :disabled="isAnalyzing">Start</button>
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
            <h3>History</h3>
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
              :key="job.jobID"
              class="history-item clickable-item"
              @click="handleHistoryClick(job)"
            >
              <div class="history-info">
                <div class="history-id">Task #{{ String(job.jobID || '').substring(0, 5) }}...</div>
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
.find-ar-btn-inline { flex-shrink: 0; display: flex; align-items: center; gap: 4px; padding: 5px 10px; border-radius: 8px; border: 1px solid rgba(88, 166, 255, 0.4); background: rgba(88, 166, 255, 0.1); color: var(--color-star-primary); font-size: 11px; font-weight: 600; font-family: inherit; cursor: pointer; transition: background 0.2s, transform 0.15s; white-space: nowrap; }
.find-ar-btn-inline:hover { background: rgba(88, 166, 255, 0.25); transform: translateY(-1px); }
.find-ar-btn-inline:active { transform: translateY(0); }

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

/* ---- Canvas 控制浮层 ---- */
.canvas-controls {
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 10;
  display: flex;
  gap: 8px;
}

.marker-toggle-btn {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 5px 10px;
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: rgba(0, 0, 0, 0.55);
  color: rgba(255, 255, 255, 0.5);
  font-size: 11px;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  backdrop-filter: blur(4px);
  transition: all 0.2s ease;
}
.marker-toggle-btn.active {
  border-color: #2ecc71;
  color: #2ecc71;
  background: rgba(46, 204, 113, 0.15);
}
.marker-toggle-btn:hover { opacity: 0.9; transform: scale(1.03); }

/* ---- 星星列表高亮 ---- */
.star-item { cursor: pointer; transition: all 0.2s ease; }
.star-item:hover { background: rgba(255, 255, 255, 0.08); }
.star-item-selected {
  background: rgba(46, 204, 113, 0.15) !important;
  border-color: rgba(46, 204, 113, 0.5) !important;
  box-shadow: 0 0 12px rgba(46, 204, 113, 0.2);
}
.star-item-selected .star-name { color: #2ecc71; }
</style>