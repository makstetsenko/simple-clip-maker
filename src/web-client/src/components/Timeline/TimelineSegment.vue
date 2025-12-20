<template>
  <div
    :class="{ segment: true, selected: selected }"
    @mousedown.exact="() => onClick(false)"
    @mousedown.shift="() => onClick(true)"
    :style="{ height: segmentHeight + 'px', top: segmentTopPosition + 'px' }"
  >
    <div v-if="model?.index! > 0" class="drag-line-top-head"></div>
    <div
      v-if="model?.index! > 0"
      class="drag-line-top"
      @mousedown="onDragLineMouseDown"
      @mouseup="onDragLineMouseUp"
      @mousemove="onDragLineMouseMove"
    ></div>
    <div class="segment-label">
      <div class="segment-number" v-if="segmentHeight > 20">
        s{{ model?.index }} {{ secondsToTimeSpanFractionalFormat(model?.startTime) }}
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
  position: absolute;
  width: 100%;
  left: 0px;
  top: 0px;
  z-index: 100;
}

.segment:hover {
  background: #999999;
}

.selected {
  z-index: 100;
  background: #373737;
}

.segment-label {
  text-align: left;
  color: #d1d1d1;
  font-weight: 700;
  font-size: 14px;
}

.segment-number {
  font-size: 14px;
  margin-bottom: 4px;
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
  background: rgb(174, 174, 174);
  width: 100%;
}
</style>
