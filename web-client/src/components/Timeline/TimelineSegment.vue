<template>
  <div class="segment" :style="{ height: segmentHeight + 'px' }">
    <div class="segment-label">
      <div class="segment-number"># {{ index }}</div>
      <div class="segment-time">Time: {{ start_time?.toFixed(2) }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps({
  index: Number,
  start_time: Number,
  duration: Number,
  end_time: Number,
  timeline_duration: Number,
  timeline_height: Number,
})

const segmentHeight = computed(() => {
  const scale = props.duration! / props.timeline_duration!
  console.log(scale)
  return scale * props.timeline_height! - 4 // 4 here is border width
})
</script>

<style scoped>
.segment {
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
