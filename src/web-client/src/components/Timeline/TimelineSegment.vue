<template>
  <div
    :class="{ segment: true, selected: selected }"
    @mousedown.exact="() => onClick(false)"
    @mousedown.shift="() => onClick(true)"
    :style="{ height: segmentHeight + 'px', top: segmentTopPosition + 'px' }"
  >
  <div class="drag-line-top-head"></div>
    <div
      class="drag-line-top"
      @mousedown="onDragLineMouseDown"
      @mouseup="onDragLineMouseUp"
      @mousemove="onDragLineMouseMove"
    ></div>
    <div class="segment-label">
      <div class="segment-number"># {{ model?.index }}</div>
      <div class="segment-time">
        {{ secondsToTimeSpanFractionalFormat(model?.startTime) }} -
        {{ secondsToTimeSpanFractionalFormat(model?.endTime) }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { secondsToTimeSpanFractionalFormat } from '@/services/time'
import type { TimelineSegmentModel } from '@/shared/models/TimelineModel'
import { computed } from 'vue'

const props = defineProps({
  timelineHeight: Number,
  timelineDuration: Number,
  selected: Boolean,
})
const model = defineModel<TimelineSegmentModel>()
const emits = defineEmits(['onSegmentClick', 'onSegmentStartTimeDrag'])

const onClick = (multiselect: boolean) => {
  emits('onSegmentClick', model.value!.id, multiselect)
}

const segmentHeight = computed(() => {
  const scale = model.value!.duration! / props.timelineDuration!
  return scale * props.timelineHeight!
})

const segmentTopPosition = computed(() => {
  const topPosition =
    ((model.value!.startTime || 0) * (props.timelineHeight || 0)) / (props.timelineDuration || 0)
  return topPosition
})

let segmentDragging = false
function onDragLineMouseDown() {
  segmentDragging = true
}
function onDragLineMouseUp() {
  segmentDragging = false
}
function onDragLineMouseMove(e: MouseEvent) {
  if (!segmentDragging) return
  emits('onSegmentStartTimeDrag', model.value, e.clientY)
}
</script>

<style scoped>
.segment {
  cursor: pointer;
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

.drag-line-top {
  background: black;
  height: 20px;
  width: 100%;
  position: absolute;
  top: -10px;
  cursor: all-scroll;
  opacity: 0%;
}
.drag-line-top-head {
  position: absolute;
  top: -1px;
  height: 2px;
  background: blue;
  width: 100%;
}
</style>
