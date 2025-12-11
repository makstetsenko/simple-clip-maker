<template>
  <div
    class="segment"
    @click="() => onSegmentClick && onSegmentClick(index)"
    :style="{ height: segmentHeight + 'px' }"
  >
    <div class="segment-label">
      <div class="segment-number"># {{ index }}</div>
      <div class="segment-time">Time: {{ startTime?.toFixed(2) }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps({
  index: Number,
  startTime: Number,
  duration: Number,
  endTime: Number,
  timelineDuration: Number,
  timelineHeight: Number,
  onSegmentClick: Function,
})

const segmentHeight = computed(() => {
  const scale = props.duration! / props.timelineDuration!
  return scale * props.timelineHeight! - getSegmentPadding()
})

const getSegmentPadding = () => {
  const borderWidth = 2
  return 2 * borderWidth
}
</script>

<style scoped>
.segment {
  cursor: pointer;
  border: 2px solid #6a64d8;
  background: #e6e6e6;
  display: flex;
  align-items: start;
  justify-content: start;
  position: relative;
}

.segment-label {
  text-align: left;
  color: #6a64d8;
  font-weight: 700;
  font-size: 20px;
}

.segment-number {
  font-size: 20px;
  margin-bottom: 4px;
}

.segment-time {
  font-size: 14px;
}
</style>
