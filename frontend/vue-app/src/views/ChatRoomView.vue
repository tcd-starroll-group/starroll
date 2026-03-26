<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import StarBackground from '@/components/StarBackground.vue'
import { chatClient, type ChatMessageItem } from '@/api/chatApi'

const router = useRouter()
const route = useRoute()

// room id comes from the route – e.g. /chat/27989 where 27989 is a HIP number
const roomId = Number(route.params.roomId)
const roomLabel = `HIP ${roomId}`

const messages = ref<ChatMessageItem[]>([])
const inputText = ref('')
const isConnected = ref(false)
const errorBanner = ref('')
const messageListRef = ref<HTMLElement | null>(null)

// track the smallest received message_id for "load older" pagination
const oldestMessageId = ref<number | undefined>(undefined)
const isLoadingOlder = ref(false)
// Current user's username, used to distinguish own messages
const currentUsername = localStorage.getItem('username') ?? ''

function normalizeMessagesOrder(incoming: ChatMessageItem[]): ChatMessageItem[] {
	return [...incoming].sort((left, right) => {
		const leftId = left.message_id
		const rightId = right.message_id

		if (leftId !== undefined && rightId !== undefined && leftId !== rightId) {
			return leftId - rightId
		}

		if (left.timestamp !== right.timestamp) {
			return left.timestamp - right.timestamp
		}

		if (leftId !== undefined && rightId !== undefined) {
			return leftId - rightId
		}

		return 0
	})
}

function scrollToBottom(smooth = true) {
	nextTick(() => {
		if (messageListRef.value) {
			messageListRef.value.scrollTo({
				top: messageListRef.value.scrollHeight,
				behavior: smooth ? 'smooth' : 'instant',
			})
		}
	})
}

function formatTime(ts: number): string {
	return new Date(ts * 1000).toLocaleTimeString('zh-CN', {
		hour: '2-digit',
		minute: '2-digit',
		hour12: false,
	})
}

function sendMessage() {
	const text = inputText.value.trim()
	if (!text) return
	chatClient.sendMessage(text)
	inputText.value = ''
}

function loadOlderMessages() {
	if (isLoadingOlder.value || oldestMessageId.value === undefined) return
	isLoadingOlder.value = true
	chatClient.listMessages(roomId, { beforeMessageId: oldestMessageId.value })
}

function goBack() {
	chatClient.exitRoom()
	router.back()
}

onMounted(() => {
	chatClient.setCallbacks({
		onConnect() {
			isConnected.value = true
			errorBanner.value = ''
			chatClient.joinRoom(roomId)
		},
		onDisconnect(_code, reason) {
			isConnected.value = false
			if (reason && reason !== 'client disconnect') {
				errorBanner.value = `Disconnected: ${reason}`
			}
		},
		onMessages(incoming) {
			if (incoming.length === 0) {
				isLoadingOlder.value = false
				return
			}

			const orderedIncoming = normalizeMessagesOrder(incoming)

			const minId = orderedIncoming.reduce(
				(m, msg) => (msg.message_id !== undefined && msg.message_id < m ? msg.message_id : m),
				Infinity,
			)

			// If we were paginating, prepend; otherwise append
			if (isLoadingOlder.value) {
				messages.value = [...orderedIncoming, ...messages.value]
				isLoadingOlder.value = false
				// keep scroll position roughly stable – jump to the top of old content
				nextTick(() => {
					if (messageListRef.value) {
						messageListRef.value.scrollTop = 0
					}
				})
			} else {
				messages.value = [...messages.value, ...orderedIncoming]
				scrollToBottom()
			}

			if (minId !== Infinity) {
				oldestMessageId.value =
					oldestMessageId.value === undefined
						? minId
						: Math.min(oldestMessageId.value, minId)
			}
		},
		onError(msg) {
			errorBanner.value = msg
			isLoadingOlder.value = false
			setTimeout(() => (errorBanner.value = ''), 4000)
		},
	})

	chatClient.connect()
	// If the socket is already open (e.g. reconnected), join the room directly
	if (chatClient.isOpen()) {
		isConnected.value = true
		chatClient.joinRoom(roomId)
	}
})

onUnmounted(() => {
	chatClient.exitRoom()
	// Clear callbacks so stale handlers don't fire after leaving the page
	chatClient.setCallbacks({})
})
</script>

<template>
	<StarBackground>
		<div class="chat-container">

			<!-- Header -->
			<div class="chat-header glass-panel">
				<button class="back-btn" @click="goBack">← Back</button>
				<div class="header-center">
					<div class="room-title">{{ roomLabel }}</div>
					<div class="room-subtitle">Star Chat Room</div>
				</div>
				<div class="connection-dot" :class="{ connected: isConnected }" :title="isConnected ? 'Connected' : 'Connecting…'"></div>
			</div>

			<!-- Error banner -->
			<transition name="slide-down">
				<div v-if="errorBanner" class="error-banner">{{ errorBanner }}</div>
			</transition>

			<!-- Load older -->
			<button class="load-older-btn" @click="loadOlderMessages" :disabled="isLoadingOlder || oldestMessageId === undefined">
				<span v-if="isLoadingOlder">Loading…</span>
				<span v-else>↑ Load older messages</span>
			</button>

			<!-- Message list -->
			<div class="message-list glass-panel" ref="messageListRef">
				<div v-if="messages.length === 0 && isConnected" class="empty-hint">
					No messages yet. Be the first to transmit!
				</div>
				<div
					v-for="(msg, idx) in messages"
					:key="msg.message_id ?? idx"
					class="message-item"
					:class="{ 'is-self': msg.username === currentUsername }"
				>
					<div class="msg-meta">
						<span class="msg-username">{{ msg.username }}</span>
						<span class="msg-time">{{ formatTime(msg.timestamp) }}</span>
					</div>
					<div class="msg-bubble">{{ msg.message }}</div>
				</div>
			</div>

			<!-- Input area -->
			<div class="input-area glass-panel">
				<input
					v-model="inputText"
					class="message-input"
					type="text"
					placeholder="Transmit a message…"
					maxlength="500"
					:disabled="!isConnected"
					@keydown.enter.prevent="sendMessage"
				/>
				<button class="send-btn" :disabled="!isConnected || !inputText.trim()" @click="sendMessage">
					Send
				</button>
			</div>

		</div>
	</StarBackground>
</template>

<style scoped>
.chat-container {
	width: 100%;
	max-width: 720px;
	height: calc(100vh - 40px);
	max-height: calc(100vh - 40px);
	min-height: 0;
	display: flex;
	flex-direction: column;
	padding: 16px;
	gap: 12px;
	box-sizing: border-box;
}

@supports (height: 100dvh) {
	.chat-container {
		height: calc(100dvh - 40px);
		max-height: calc(100dvh - 40px);
	}
}

/* ── Header ── */
.chat-header {
	display: flex;
	align-items: center;
	gap: 12px;
	padding: 12px 16px;
	border-radius: 16px;
	flex-shrink: 0;
}

.back-btn {
	background: transparent;
	border: 1px solid rgba(100, 200, 255, 0.3);
	color: #66ccff;
	border-radius: 8px;
	padding: 6px 12px;
	cursor: pointer;
	font-size: 13px;
	transition: background 0.2s;
	white-space: nowrap;
}
.back-btn:hover {
	background: rgba(100, 200, 255, 0.15);
}

.header-center {
	flex: 1;
	text-align: center;
}
.room-title {
	font-size: 18px;
	font-weight: 700;
	color: #66ccff;
	text-shadow: 0 0 10px rgba(102, 204, 255, 0.5);
	letter-spacing: 1px;
}
.room-subtitle {
	font-size: 11px;
	color: rgba(255, 255, 255, 0.45);
	text-transform: uppercase;
	letter-spacing: 2px;
	margin-top: 2px;
}

.connection-dot {
	width: 10px;
	height: 10px;
	border-radius: 50%;
	background: #555;
	flex-shrink: 0;
	transition: background 0.3s;
}
.connection-dot.connected {
	background: #00ff88;
	box-shadow: 0 0 8px #00ff88;
}

/* ── Error banner ── */
.error-banner {
	background: rgba(255, 60, 60, 0.25);
	border: 1px solid rgba(255, 80, 80, 0.5);
	border-radius: 10px;
	padding: 8px 14px;
	font-size: 13px;
	color: #ffaaaa;
	text-align: center;
	flex-shrink: 0;
}
.slide-down-enter-active, .slide-down-leave-active { transition: all 0.25s ease; }
.slide-down-enter-from, .slide-down-leave-to { opacity: 0; transform: translateY(-6px); }

/* ── Load older ── */
.load-older-btn {
	align-self: center;
	background: transparent;
	border: 1px solid rgba(100, 200, 255, 0.25);
	color: rgba(100, 200, 255, 0.7);
	border-radius: 20px;
	padding: 5px 16px;
	font-size: 12px;
	cursor: pointer;
	flex-shrink: 0;
	transition: background 0.2s;
}
.load-older-btn:hover:not(:disabled) {
	background: rgba(100, 200, 255, 0.1);
}
.load-older-btn:disabled {
	opacity: 0.35;
	cursor: default;
}

/* ── Message list ── */
.message-list {
	flex: 1;
	min-height: 0;
	overflow-y: auto;
	padding: 16px;
	border-radius: 16px;
	display: flex;
	flex-direction: column;
	gap: 12px;
	scrollbar-width: thin;
	scrollbar-color: rgba(100, 200, 255, 0.3) transparent;
}
.message-list::-webkit-scrollbar { width: 4px; }
.message-list::-webkit-scrollbar-thumb { background: rgba(100, 200, 255, 0.3); border-radius: 4px; }

.empty-hint {
	margin: auto;
	color: rgba(255, 255, 255, 0.3);
	font-size: 14px;
	font-style: italic;
	text-align: center;
}

.message-item {
	display: flex;
	flex-direction: column;
	gap: 4px;
	max-width: 80%;
	align-self: flex-start;
}
.message-item.is-self {
	align-self: flex-end;
	align-items: flex-end;
}

.msg-meta {
	display: flex;
	gap: 8px;
	align-items: baseline;
	padding: 0 4px;
}
.msg-username {
	font-size: 12px;
	font-weight: 600;
	color: #66ccff;
}
.msg-time {
	font-size: 11px;
	color: rgba(255, 255, 255, 0.35);
}

.msg-bubble {
	background: rgba(255, 255, 255, 0.08);
	border: 1px solid rgba(255, 255, 255, 0.12);
	border-radius: 12px;
	padding: 8px 12px;
	font-size: 14px;
	line-height: 1.5;
	color: #e8f0ff;
	word-break: break-word;
}
.message-item.is-self .msg-bubble {
	background: rgba(102, 204, 255, 0.15);
	border-color: rgba(102, 204, 255, 0.3);
}

/* ── Input area ── */
.input-area {
	display: flex;
	gap: 10px;
	align-items: center;
	padding: 12px 14px;
	border-radius: 16px;
	flex-shrink: 0;
}

.message-input {
	flex: 1;
	background: rgba(255, 255, 255, 0.07);
	border: 1px solid rgba(100, 200, 255, 0.25);
	border-radius: 10px;
	color: #fff;
	font-size: 14px;
	padding: 9px 14px;
	outline: none;
	transition: border-color 0.2s;
}
.message-input::placeholder {
	color: rgba(255, 255, 255, 0.3);
}
.message-input:focus {
	border-color: rgba(102, 204, 255, 0.6);
}
.message-input:disabled {
	opacity: 0.4;
}

.send-btn {
	background: rgba(102, 204, 255, 0.2);
	border: 1px solid rgba(102, 204, 255, 0.45);
	color: #66ccff;
	border-radius: 10px;
	padding: 9px 20px;
	font-size: 14px;
	font-weight: 600;
	cursor: pointer;
	transition: background 0.2s;
	white-space: nowrap;
}
.send-btn:hover:not(:disabled) {
	background: rgba(102, 204, 255, 0.35);
}
.send-btn:disabled {
	opacity: 0.35;
	cursor: default;
}
</style>
