<template>
  <div
    :class="{ segment: true, selected: selected }"
    @click.exact="() => onClick(false)"
    @click.shift="() => onClick(true)"
    :style="{ height: segmentHeight + 'px', top: segmentTopPosition + 'px' }"
  >
    <div class="segment-label">
      <div class="segment-number"># {{ index }}</div>
      <div class="segment-time">
        {{ secondsToTimeSpanFractionalFormat(startTime) }} -
        {{ secondsToTimeSpanFractionalFormat(endTime) }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { secondsToTimeSpanFractionalFormat } from '@/services/time'
import { computed } from 'vue'

const props = defineProps({
  id: String,
  index: Number,
  startTime: Number,
  duration: Number,
  endTime: Number,
  timelineDuration: Number,
  timelineHeight: Number,
  onSegmentClick: Function,
  selected: Boolean,
})

const emits = defineEmits(['onSegmentClick'])

const onClick = (multiselect: boolean) => {
  emits('onSegmentClick', props.id, multiselect)
}

const segmentHeight = computed(() => {
  const scale = props.duration! / props.timelineDuration!
  return scale * props.timelineHeight!
})

const segmentTopPosition = computed(() => {
  const topPosition =
    ((props.startTime || 0) * (props.timelineHeight || 0)) / (props.timelineDuration || 0)
  return topPosition
})
</script>

<style scoped>
.segment {
  cursor: pointer;
  border: 4px solid #6a64d8;
  background: #e6e6e6;
  position: absolute;
  width: 150px;
  left: 0px;
  top: 0px;
  z-index: 100;
}

.selected {
  width: 200px;
  z-index: 101;
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
