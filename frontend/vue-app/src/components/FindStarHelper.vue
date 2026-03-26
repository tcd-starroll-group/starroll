<script setup lang="ts">
import { computed } from 'vue';

const props = withDefaults(
	defineProps<{
		angleDeg: number | null;
		absoluteAngleDeg: number | null;
		thresholdDeg?: number;
	}>(),
	{
		thresholdDeg: 20,
	},
);

const shouldShow = computed(() => {
	if (props.angleDeg === null || props.absoluteAngleDeg === null) return false;
	return props.absoluteAngleDeg > props.thresholdDeg;
});

const arrowRotationDeg = computed(() => {
	if (props.angleDeg === null) return 0;
	return props.angleDeg;
});

const arrowLengthPx = computed(() => {
	if (props.absoluteAngleDeg === null) return 72;
	const minLength = 72;
	const maxLength = 180;
	const maxAngle = 180;
	const clamped = Math.max(
		0,
		Math.min(1, (props.absoluteAngleDeg - props.thresholdDeg) / (maxAngle - props.thresholdDeg)),
	);
	return minLength + clamped * (maxLength - minLength);
});

const arrowLineStyle = computed(() => ({
	width: `${arrowLengthPx.value}px`,
}));

const arrowHeadStyle = computed(() => ({
	left: `${arrowLengthPx.value}px`,
}));
</script>

<template>
	<div v-if="shouldShow" class="find-star-helper">
		<div class="guide-arrow-wrap" :style="{ transform: `rotate(${arrowRotationDeg}deg)` }">
			<div class="guide-arrow-line" :style="arrowLineStyle"></div>
			<div class="guide-arrow-head" :style="arrowHeadStyle"></div>
		</div>
	</div>
</template>

<style scoped>
.find-star-helper {
	position: absolute;
	top: 0;
	left: 0;
	width: 100%;
	height: 100%;
	pointer-events: none;
	z-index: 30;
}

.guide-arrow-wrap {
	position: absolute;
	left: 50%;
	top: 50%;
	transform-origin: center center;
}

.guide-arrow-line {
	position: absolute;
	left: 0;
	top: 50%;
	width: 96px;
	height: 2px;
	transform: translateY(-50%);
	background: linear-gradient(90deg, rgba(68, 170, 255, 0.25), rgba(68, 170, 255, 0.95));
	box-shadow: 0 0 12px rgba(68, 170, 255, 0.65);
	transition: width 0.15s ease;
}

.guide-arrow-head {
	position: absolute;
	left: 96px;
	top: 50%;
	transform: translateY(-50%);
	width: 0;
	height: 0;
	border-top: 8px solid transparent;
	border-bottom: 8px solid transparent;
	border-left: 14px solid var(--sr-accent-color);
	filter: drop-shadow(0 0 8px rgba(68, 170, 255, 0.8));
	transition: left 0.15s ease;
}
</style>
