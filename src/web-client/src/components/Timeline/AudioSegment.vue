<template>
  <div
    :class="{ segment: true }"
    :style="{
      height: segmentHeight + 'px',
      top: segmentTopPosition + 'px',
      background: backgroundColor,
    }"
  >
    <div class="segment-header"></div>
    <div class="segment-label">
      <div class="segment-number" v-if="segmentHeight > 20"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { AudioSegmentModel } from '@/shared/models/TimelineModel'
import { computed } from 'vue'

const props = defineProps({
  timelineHeight: Number,
  timelineDuration: Number,
})
const model = defineModel<AudioSegmentModel>()

const segmentHeight = computed(() => {
  const scale = model.value!.duration! / props.timelineDuration!
  return scale * props.timelineHeight!
})

const segmentTopPosition = computed(() => {
  const topPosition =
    ((model.value!.startTime || 0) * (props.timelineHeight || 0)) / (props.timelineDuration || 0)
  return topPosition
})

const intensityColorCodes: Map<string, string> = new Map([
  ['low', '#60e6889c'],
  ['medium', '#e4e6609c'],
  ['high', '#e664609c'],
])

const backgroundColor = computed(() => {
  if (!model.value) return intensityColorCodes.get('low')
  return intensityColorCodes.get(model.value.intensity_band)
})
</script>

<style scoped>
.segment {
  cursor: pointer;
  position: absolute;
  width: 20px;
  left: 0px;
  top: 0px;
  z-index: 101;
  pointer-events: none;
  opacity: 30%;
  border-radius: 10px;
}

.segment-header {
  height: 4px;
  /* background: #eee; */
  top: -2px;
  width: 100%;
}
</style>
