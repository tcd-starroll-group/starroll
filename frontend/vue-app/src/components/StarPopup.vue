<script setup lang="ts">
import type { StarClickInfo } from '@/core/renderer/GroundObserverRenderer';
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { defaultApi } from '@/api/defaultApi';

// Define component props to receive star data
const props = defineProps<{
  starInfo: StarClickInfo | null;
    starMessageDisplay?: {
        id: string;
        from: string;
        message: string;
    } | null;
}>();

// Define component events to emit close signal to parent component
const emit = defineEmits<{
  (e: 'close'): void;
}>();

const router = useRouter();
const showCreateMessageModal = ref(false);
const messageFrom = ref('');
const messageContent = ref('');
const creatingMessage = ref(false);
const createMessageError = ref('');
const createdMessageId = ref('');
const copySuccess = ref(false);

async function ensureLoggedIn() {
    try {
        await defaultApi.apiCheckLoginStatusPost();
        return true;
    } catch {
        emit('close');
        await router.push({ name: 'Login' });
        return false;
    }
}

const viewStarBlogs = async () => {
  if (props.starInfo && props.starInfo.hip) {
        const isLoggedIn = await ensureLoggedIn();
        if (!isLoggedIn) return;

    router.push({
      path: '/star-blogs', 
      query: { 
        hip: props.starInfo.hip, 
        name: props.starInfo.originalName || props.starInfo.name // 顺便把名字带过去，方便目标页面渲染标题
      }
    });
  }
};

function resetCreateMessageState() {
    messageFrom.value = '';
    messageContent.value = '';
    creatingMessage.value = false;
    createMessageError.value = '';
    createdMessageId.value = '';
    copySuccess.value = false;
}

async function openCreateMessageModal() {
    if (!props.starInfo?.hip) return;
    const isLoggedIn = await ensureLoggedIn();
    if (!isLoggedIn) return;
    resetCreateMessageState();
    showCreateMessageModal.value = true;
}

function closeCreateMessageModal() {
    showCreateMessageModal.value = false;
}

async function submitCreateMessage() {
    if (!props.starInfo?.hip || creatingMessage.value) return;

    const fromValue = messageFrom.value.trim();
    const messageValue = messageContent.value.trim();

    if (!fromValue || !messageValue) {
        createMessageError.value = 'Please fill in both "from" and "message".';
        return;
    }

    createMessageError.value = '';
    copySuccess.value = false;
    creatingMessage.value = true;

    try {
        const result = await defaultApi.apiCreateStarMessagePost({
            starMessage: {
                hip: String(props.starInfo.hip),
                from: fromValue,
                message: messageValue,
            },
        });
        if (!result.id) {
            createMessageError.value = 'Star message created, but no ID was returned.';
            return;
        }
        createdMessageId.value = result.id;
    } catch {
        createMessageError.value = 'Failed to create star message. Please try again.';
    } finally {
        creatingMessage.value = false;
    }
}

async function copyCreatedId() {
    if (!createdMessageId.value) return;
    try {
        const shareUrl = `https://starroll.ie?star_message=${encodeURIComponent(createdMessageId.value)}`;
        await navigator.clipboard.writeText(shareUrl);
        copySuccess.value = true;
    } catch {
        copySuccess.value = false;
    }
}

function joinChatRoom() {
    if (!props.starInfo) return;
        ensureLoggedIn().then((isLoggedIn) => {
            if (!isLoggedIn) return;

            emit('close');
            router.push({ name: 'ChatRoom', params: { roomId: props.starInfo!.hip } });
        });
}
</script>

<template>
  <div v-if="starInfo" 
       class="star-popup" 
       @click.stop> 
       <button class="close-btn" @click.stop="emit('close')">×</button>
      
      <div class="star-header">
          <div class="star-name">{{ starInfo.originalName || starInfo.name }}</div>
          <div class="star-hip">HIP {{ starInfo.hip }}</div>
      </div>
      
      <div class="star-content">
          <div v-if="starMessageDisplay" class="star-message-panel">
              <div class="star-message-title">Star Message</div>
              <div class="star-message-row"><span class="label">From:</span><span class="value">{{ starMessageDisplay.from }}</span></div>
              <div class="star-message-text">{{ starMessageDisplay.message }}</div>
          </div>

          <div v-if="starInfo.description" class="star-desc">
              {{ starInfo.description }}
          </div>

          <div class="data-row">
              <span class="label">Constellation:</span>
              <span class="value">{{ starInfo.constellation }}</span>
          </div>
          <div class="data-row">
              <span class="label">Apparent Magnitude:</span>
              <span class="value">{{ starInfo.magnitude.toFixed(2) }}</span>
          </div>
          <div class="data-row">
              <span class="label">Distance:</span>
              <span class="value">{{ starInfo.distance ? starInfo.distance.toFixed(1) + ' ly' : '--' }}</span>
          </div>

          <button class="blog-btn" @click.stop="viewStarBlogs">
            Explore Star Logs
          </button>
          <button class="chat-btn" @click.stop="joinChatRoom">
            Enter Star Chat Room
          </button>
                    <button class="message-btn" @click.stop="openCreateMessageModal">
                        Create Star Message
                    </button>

          <div class="separator"></div>
          <div class="data-row">
              <span class="label">Right ascension:</span>
              <span class="value">{{ starInfo.rightAscension.toFixed(2) }}°</span>
          </div>
          <div class="data-row">
              <span class="label">Declination:</span>
              <span class="value">{{ starInfo.declination.toFixed(2) }}°</span>
          </div>
           <div class="data-row">
              <span class="label">B-V Color Index:</span>
              <span class="value">{{ starInfo.bvColor.toFixed(2) }}</span>
          </div>
      </div>
  </div>

    <div v-if="showCreateMessageModal" class="create-message-overlay" @click.self="closeCreateMessageModal">
        <div class="create-message-modal" @click.stop>
            <button class="close-btn create-message-close" @click="closeCreateMessageModal">×</button>
            <div class="create-message-title">Create Star Message</div>
            <div class="create-message-subtitle">HIP {{ starInfo?.hip }}</div>

            <label class="form-label" for="from-input">from</label>
            <input
                id="from-input"
                v-model="messageFrom"
                class="form-input"
                type="text"
                maxlength="64"
                placeholder="Your name"
            />

            <label class="form-label" for="message-input">message</label>
            <textarea
                id="message-input"
                v-model="messageContent"
                class="form-textarea"
                rows="4"
                maxlength="300"
                placeholder="Write your message to the stars"
            />

            <div v-if="createMessageError" class="form-error">{{ createMessageError }}</div>

            <button class="submit-btn" :disabled="creatingMessage" @click="submitCreateMessage">
                {{ creatingMessage ? 'Creating...' : 'Create' }}
            </button>

            <div v-if="createdMessageId" class="created-id-box">
                <div class="created-id-label">Generated ID</div>
                <div class="created-id-value">{{ createdMessageId }}</div>
                <button class="copy-btn" @click="copyCreatedId">Copy Share Link</button>
                <div v-if="copySuccess" class="copy-success">Copied</div>
            </div>
        </div>
    </div>
</template>

<style scoped>
/* 原有样式保持不变 */
@keyframes popupFadeIn {
    from { opacity: 0; transform: scale(0.8) translateY(10px); }
    to { opacity: 1; transform: scale(1) translateY(0); }
}

.star-popup {
    position: fixed;
    left: 50%;
    bottom: 24px;
    background: rgba(15, 20, 30, 0.85);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(100, 150, 255, 0.2);
    border-radius: 12px;
    padding: 16px;
    min-width: 240px;
    max-width: 300px;
    color: white;
    font-family: var(--sr-font-family, 'Inter', sans-serif);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6),
                inset 0 0 0 1px rgba(255, 255, 255, 0.1);
    transform: translateX(-50%);
    margin-top: 0;
    pointer-events: auto;
    z-index: 200;
}

.star-popup::after {
    content: '';
    position: absolute;
    bottom: -8px;
    left: 50%;
    transform: translateX(-50%);
    border-width: 8px 8px 0;
    border-style: solid;
    border-color: rgba(15, 20, 30, 0.85) transparent transparent transparent;
    filter: drop-shadow(0 1px 1px rgba(100, 150, 255, 0.2));
}

.close-btn {
    position: absolute;
    top: 5px;
    right: 8px;
    background: transparent;
    border: none;
    color: rgba(255,255,255,0.6);
    font-size: 24px;
    line-height: 1;
    cursor: pointer;
    z-index: 201;
    transition: color 0.2s;
}

.close-btn:hover {
    color: white;
}

.star-header {
    border-bottom: 1px solid rgba(255,255,255,0.15);
    padding-bottom: 8px;
    margin-bottom: 10px;
    padding-right: 20px;
}

.star-name {
    font-size: 16px;
    font-weight: bold;
    color: #66ccff;
    text-shadow: 0 0 10px rgba(102, 204, 255, 0.5);
    line-height: 1.3;
}

.star-hip {
    font-size: 11px;
    color: #8899aa;
    margin-top: 2px;
}

.star-content {
    font-size: 13px;
    line-height: 1.5;
}

.star-desc {
    font-size: 12px;
    color: #aaccff;
    margin-bottom: 12px;
    font-style: italic;
    background: rgba(100, 150, 255, 0.1);
    padding: 6px 10px;
    border-radius: 6px;
    border-left: 3px solid #66ccff;
    line-height: 1.4;
    max-height: 80px;
    overflow-y: auto;
}

.star-message-panel {
    margin-bottom: 12px;
    padding: 8px 10px;
    border-radius: 8px;
    border: 1px solid rgba(179, 146, 255, 0.42);
    background: rgba(132, 102, 255, 0.14);
}

.star-message-title {
    color: #dbcfff;
    font-size: 12px;
    font-weight: 700;
    margin-bottom: 6px;
}

.star-message-row {
    display: flex;
    justify-content: space-between;
    margin-bottom: 4px;
    font-size: 12px;
}

.star-message-text {
    margin-top: 6px;
    font-size: 12px;
    line-height: 1.45;
    color: #f3eeff;
    white-space: pre-wrap;
    word-break: break-word;
}

.link-row {
    margin-top: 8px;
    justify-content: flex-end;
}

.chat-btn {
    display: block;
    width: 100%;
    margin-top: 10px;
    padding: 7px 0;
    background: rgba(102, 204, 255, 0.12);
    border: 1px solid rgba(102, 204, 255, 0.35);
    border-radius: 8px;
    color: #66ccff;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    text-align: center;
    transition: background 0.2s;
    letter-spacing: 0.3px;
}
.chat-btn:hover {
    background: rgba(102, 204, 255, 0.25);
}

.message-btn {
    display: block;
    width: 100%;
    margin-top: 10px;
    padding: 7px 0;
    background: rgba(132, 102, 255, 0.16);
    border: 1px solid rgba(132, 102, 255, 0.38);
    border-radius: 8px;
    color: #c8b8ff;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    text-align: center;
    transition: background 0.2s;
    letter-spacing: 0.3px;
}

.message-btn:hover {
    background: rgba(132, 102, 255, 0.28);
}

.star-link {
    color: #44aaff;
    text-decoration: none;
    font-size: 12px;
    border-bottom: 1px dashed #44aaff;
}

.star-link:hover {
    color: #fff;
    border-bottom-style: solid;
}

.data-row {
    display: flex;
    justify-content: space-between;
    margin-bottom: 6px;
    border-bottom: 1px dashed rgba(255,255,255,0.05);
    padding-bottom: 4px;
}

.data-row:last-of-type {
    border-bottom: none;
    margin-bottom: 0;
    padding-bottom: 0;
}

.label {
    color: #8899aa;
}

.value {
    font-weight: 500;
    color: #ffffff;
}

/* 🌟 按钮专属样式 */
.blog-btn {
    width: 100%;
    margin-top: 16px;
    padding: 10px 0;
    background: rgba(68, 170, 255, 0.15);
    border: 1px solid rgba(68, 170, 255, 0.4);
    color: #66ccff;
    border-radius: 6px;
    cursor: pointer;
    font-size: 14px;
    font-weight: 600;
    transition: all 0.3s ease;
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 8px;
    font-family: var(--sr-font-family);
}

.blog-btn:hover {
    background: rgba(68, 170, 255, 0.3);
    border-color: #66ccff;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(68, 170, 255, 0.2);
    color: #ffffff;
}

.blog-btn:active {
    transform: translateY(0);
}

.create-message-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.45);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 400;
}

.create-message-modal {
    position: relative;
    width: min(92vw, 420px);
    background: rgba(15, 20, 30, 0.96);
    border: 1px solid rgba(132, 102, 255, 0.4);
    border-radius: 12px;
    padding: 18px 16px 16px;
    box-shadow: 0 12px 28px rgba(0, 0, 0, 0.45);
}

.create-message-close {
    top: 6px;
    right: 10px;
}

.create-message-title {
    color: #d8ccff;
    font-size: 16px;
    font-weight: 700;
}

.create-message-subtitle {
    color: #9fb1c4;
    font-size: 12px;
    margin-top: 2px;
    margin-bottom: 12px;
}

.form-label {
    display: block;
    color: #aebcd1;
    font-size: 12px;
    margin-bottom: 6px;
}

.form-input,
.form-textarea {
    width: 100%;
    box-sizing: border-box;
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.14);
    color: #ffffff;
    border-radius: 8px;
    padding: 8px 10px;
    margin-bottom: 10px;
    font-size: 13px;
    font-family: var(--sr-font-family, 'Inter', sans-serif);
}

.form-textarea {
    resize: vertical;
    min-height: 90px;
}

.form-input:focus,
.form-textarea:focus {
    outline: none;
    border-color: rgba(132, 102, 255, 0.72);
}

.form-error {
    color: #ff8e9b;
    font-size: 12px;
    margin-bottom: 8px;
}

.submit-btn {
    width: 100%;
    border: 1px solid rgba(132, 102, 255, 0.42);
    background: rgba(132, 102, 255, 0.2);
    color: #e5dcff;
    border-radius: 8px;
    padding: 8px 0;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
}

.submit-btn:disabled {
    opacity: 0.65;
    cursor: not-allowed;
}

.created-id-box {
    margin-top: 12px;
    padding: 10px;
    border-radius: 8px;
    border: 1px dashed rgba(102, 204, 255, 0.42);
    background: rgba(102, 204, 255, 0.08);
}

.created-id-label {
    color: #9fb1c4;
    font-size: 12px;
    margin-bottom: 4px;
}

.created-id-value {
    color: #fff;
    font-size: 13px;
    word-break: break-all;
    margin-bottom: 8px;
}

.copy-btn {
    width: 100%;
    border: 1px solid rgba(102, 204, 255, 0.5);
    background: rgba(102, 204, 255, 0.18);
    color: #d9f4ff;
    border-radius: 8px;
    padding: 7px 0;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
}

.copy-success {
    margin-top: 6px;
    color: #9fffba;
    font-size: 12px;
    text-align: center;
}
</style>