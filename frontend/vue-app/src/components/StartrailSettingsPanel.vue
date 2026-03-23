<script setup lang="ts">
import { computed, ref } from 'vue'

export type StartrailSettings = {
	shotIntervalSeconds: number
	startTimestampMs: number
	durationSeconds: number
	twinkleMultiplier: number
	renderStarSizeMultiplier: number
	renderStarBrightnessMultiplier: number
}

const emit = defineEmits<{
	(e: 'start', payload: StartrailSettings): void
	(e: 'stop'): void
}>()

const panelVisible = ref(false)
const shotIntervalSeconds = ref(60)
const durationMinutes = ref(240)
const startTimestampMs = ref(Date.now())
const twinkleMultiplier = ref(0.5)
const renderStarSizeMultiplier = ref(0.5)
const renderStarBrightnessMultiplier = ref(0.8)

const pad = (value: number) => String(value).padStart(2, '0')

const localDateTimeInput = computed({
	get: () => {
		const date = new Date(startTimestampMs.value)
		const year = date.getFullYear()
		const month = pad(date.getMonth() + 1)
		const day = pad(date.getDate())
		const hour = pad(date.getHours())
		const minute = pad(date.getMinutes())
		const second = pad(date.getSeconds())
		return `${year}-${month}-${day}T${hour}:${minute}:${second}`
	},
	set: (value: string) => {
		const parsed = new Date(value).getTime()
		if (!Number.isNaN(parsed)) {
			startTimestampMs.value = parsed
		}
	},
})

const useCurrentTime = () => {
	startTimestampMs.value = Date.now()
}

const startGenerate = () => {
	const safeShotInterval = Math.max(1, Number(shotIntervalSeconds.value) || 30)
	const safeDurationMinutes = Math.max(1, Number(durationMinutes.value) || 30)
	const safeTwinkleMultiplier = Math.max(0, Number(twinkleMultiplier.value) || 1)
	const safeRenderStarSizeMultiplier = Math.max(0.01, Number(renderStarSizeMultiplier.value) || 1)
	const safeRenderStarBrightnessMultiplier = Math.max(
		0.01,
		Number(renderStarBrightnessMultiplier.value) || 1,
	)

	shotIntervalSeconds.value = safeShotInterval
	durationMinutes.value = safeDurationMinutes
	twinkleMultiplier.value = safeTwinkleMultiplier
	renderStarSizeMultiplier.value = safeRenderStarSizeMultiplier
	renderStarBrightnessMultiplier.value = safeRenderStarBrightnessMultiplier

	emit('start', {
		shotIntervalSeconds: safeShotInterval,
		startTimestampMs: startTimestampMs.value,
		durationSeconds: safeDurationMinutes * 60,
		twinkleMultiplier: safeTwinkleMultiplier,
		renderStarSizeMultiplier: safeRenderStarSizeMultiplier,
		renderStarBrightnessMultiplier: safeRenderStarBrightnessMultiplier,
	})

	panelVisible.value = false
}

const stopGenerate = () => {
	emit('stop')
}
</script>

<template>
	<button class="startrail-toggle" @click="panelVisible = !panelVisible">
		<img src="/images/star_trail.png" alt="Startrail settings" />
	</button>

	<div v-if="panelVisible" class="startrail-panel sr-glass-panel">
		<div class="header-row">
			<div class="sr-title">Startrail Settings</div>
			<button class="close-btn" @click="panelVisible = false">×</button>
		</div>

		<label>
			拍摄间隔（秒）
			<input v-model.number="shotIntervalSeconds" type="number" min="1" step="1" />
		</label>

		<label>
			开始时间
			<input v-model="localDateTimeInput" type="datetime-local" step="1" />
		</label>

		<button class="sr-glass-btn" @click="useCurrentTime">使用当前时间</button>

		<label>
			拍摄时长（分钟）
			<input v-model.number="durationMinutes" type="number" min="1" step="1" />
		</label>

		<label>
			twinkleMultiplier
			<input v-model.number="twinkleMultiplier" type="number" min="0" step="0.1" />
		</label>

		<label>
			renderStarSizeMultiplier
			<input v-model.number="renderStarSizeMultiplier" type="number" min="0.01" step="0.1" />
		</label>

		<label>
			renderStarBrightnessMultiplier
			<input v-model.number="renderStarBrightnessMultiplier" type="number" min="0.01" step="0.1" />
		</label>

		<button class="sr-glass-btn" @click="startGenerate">开始生成</button>
		<button class="sr-glass-btn" @click="stopGenerate">退出星轨模式</button>
	</div>
</template>

<style scoped>
.startrail-toggle {
	position: absolute;
	top: 20px;
	right: 76px;
	z-index: 21;
	width: 40px;
	height: 40px;
	border: none;
	border-radius: 10px;
	background: transparent;
	display: flex;
	align-items: center;
	justify-content: center;
	cursor: pointer;
}

.startrail-toggle img {
	width: 24px;
	height: 24px;
}

.startrail-panel {
	position: absolute;
	top: 68px;
	right: 76px;
	z-index: 20;
	padding: 12px;
	display: grid;
	gap: 8px;
	width: 280px;
}

.header-row {
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.close-btn {
	border: 1px solid var(--sr-border-glass);
	border-radius: 6px;
	background: rgba(255, 255, 255, 0.05);
	color: var(--sr-text-primary);
	width: 24px;
	height: 24px;
	line-height: 20px;
	cursor: pointer;
}

label {
	display: grid;
	gap: 4px;
	font-size: 12px;
}

input {
	width: 100%;
}
</style>
