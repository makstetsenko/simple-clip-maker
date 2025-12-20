<template>
  <div class="timeline-item" @click="onMouseClick">
    <div class="timeline-and-segment-config-grid">
      <div class="timeline-container" ref="timeline-container">
        <div class="timeline no-select" :style="{ height: timelineHeight + 'px' }" ref="timeline">
          <TimelineSegment
            v-for="(s, i) in timelineStore.timeline!.segments"
            :key="s.id"
            v-model="timelineStore.timeline!.segments[i]"
            :timelineHeight="timelineHeight"
            :timelineDuration="timelineStore.timeline!.duration"
            :selected="timelineStore.selectedSegments.some((x) => x.id === s.id)"
            @onSegmentClick="onSegmentClick"
            @mouseenter="onMouseEnterTimeline"
            @mouseleave="onMouseLeaveTimeline"
            @onSegmentStartTimeDrag="onSegmentStartTimeDrag"
          />
        </div>
      </div>

      <div class="segment-config-container"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, useTemplateRef, type Ref } from 'vue'
import TimelineSegment from './TimelineSegment.vue'
import { useTimelineStore } from '@/stores/timeline'
import type { TimelineSegmentModel } from '@/shared/models/TimelineModel'

const timelineStore = useTimelineStore()
const isMouseOverTimeline: Ref<boolean> = ref(false)

const timelineContainerRef = useTemplateRef('timeline-container')
const timelineRef = useTemplateRef('timeline')

const timelineHeight = computed(() => (props.timelineZoom ?? 1.0) * 3000)

const props = defineProps({
  timelineZoom: Number,
})

const onMouseClick = () => {
  if (isMouseOverTimeline.value) {
    return
  }

  timelineStore.clearSelectedSegments()
}

const onSegmentClick = (segmentId: string | null, multiselect: boolean) => {
  if (!segmentId) {
    return
  }
  if (!multiselect) {
    timelineStore.clearSelectedSegments()
    timelineStore.appendSelectSegment(segmentId)
    return
  }

  console.log('multiselect')

  if (timelineStore.selectedSegments.length < 1) return

  const firstIndex = timelineStore.selectedSegments[0]!.index!
  const currentIndex = timelineStore.timeline!.segments.findIndex((x) => x.id === segmentId)

  const start = firstIndex > currentIndex ? currentIndex : firstIndex
  const end = firstIndex < currentIndex ? currentIndex : firstIndex

  timelineStore.clearSelectedSegments()

  for (let i = start; i <= end; i++) {
    timelineStore.appendSelectSegmentByIndex(i)
  }
}

const onMouseEnterTimeline = () => {
  isMouseOverTimeline.value = true
}

const onMouseLeaveTimeline = () => {
  isMouseOverTimeline.value = false
}

function handleKeyboard(event: KeyboardEvent) {
  if (timelineStore.selectedSegments.length == 0) return
  if (timelineStore.selectedSegments.length > 1) return

  let multiplier = null
  if (event.key === 'ArrowUp') multiplier = -1
  else if (event.key === 'ArrowDown') multiplier = 1

  if (multiplier == null) return

  let nextIndex = timelineStore.selectedSegments[0]!.index! + 1 * multiplier
  if (nextIndex < 0) nextIndex = 0
  if (nextIndex >= timelineStore.timeline!.segments.length)
    nextIndex = timelineStore.timeline!.segments.length - 1

  timelineStore.clearSelectedSegments()
  timelineStore.appendSelectSegmentByIndex(nextIndex)

  event.preventDefault()
  event.stopPropagation()
}

onMounted(() => {
  document.addEventListener('keydown', handleKeyboard)
})
onBeforeUnmount(() => {
  if (!timelineContainerRef.value) return
  document.removeEventListener('keydown', handleKeyboard)
})

function onSegmentStartTimeDrag(segment: TimelineSegmentModel, mouseY: number) {
  if (!timelineRef.value) return
  if (segment.index == 0) return

  const rect = timelineRef.value.getBoundingClientRect()
  const segmentTopY = mouseY - rect.top

  const segmentEndTime = segment.duration + segment.startTime
  const newStartTime = (segmentTopY / timelineHeight.value) * timelineStore.timeline!.duration!

  segment.startTime = newStartTime
  segment.duration = segmentEndTime - newStartTime

  const segmentAbove = timelineStore.timeline!.segments[segment.index - 1]!
  segmentAbove.endTime = segment.startTime
  segmentAbove.duration = segment.startTime - segmentAbove.startTime
}
</script>

<style scoped>
.timeline-item {
  position: relative;
  background: #515151;
}
.timeline-container {
  height: 1000px;
  overflow-y: scroll;
  overflow-x: hidden;
  width: 250px;
}
.timeline {
  width: 100%;
  display: flex;
  flex-direction: column;
  position: relative;
}

.segment-config-container {
}


.no-select {
  -webkit-user-select: none; /* Safari */
  -moz-user-select: none; /* Firefox */
  -ms-user-select: none; /* IE/Edge Legacy */
  user-select: none; /* Standard */
}
</style>
