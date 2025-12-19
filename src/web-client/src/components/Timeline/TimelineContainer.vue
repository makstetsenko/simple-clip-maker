<template>
  <div class="timeline-item" @click="onMouseClick">
    <div class="timeline-and-segment-config-grid">
      <div class="timeline-container">
        <div class="timeline no-select" :style="{ height: timelineHeight + 'px' }">
          <TimelineSegment
            v-for="(s, i) in timelineStore.timeline!.segments"
            :key="s.id"
            v-model="timelineStore.timeline!.segments[i]"
            :timelineHeight="3000"
            :timelineDuration="timelineStore.timeline!.duration"
            :selected="timelineStore.selectedSegments.some((x) => x.id === s.id)"
            @onSegmentClick="onSegmentClick"
            @mouseenter="onMouseEnterTimeline"
            @mouseleave="onMouseLeaveTimeline"
          />
        </div>
      </div>

      <div class="segment-config-container"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, type Ref } from 'vue'
import TimelineSegment from './TimelineSegment.vue'
import { useTimelineStore } from '@/stores/timeline'

const timelineStore = useTimelineStore()
const isMouseOverTimeline: Ref<boolean> = ref(false)

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
  }
  timelineStore.appendSelectSegment(segmentId)
}

const onMouseEnterTimeline = () => {
  isMouseOverTimeline.value = true
}

const onMouseLeaveTimeline = () => {
  isMouseOverTimeline.value = false
}

const timelineHeight = 3000 // px
</script>

<style scoped>
.timeline-item {
  background: #eee;
  position: relative;
}
.timeline-container {
  height: 1000px;
  overflow-y: scroll;
  overflow-x: hidden;
  width: 250px;
}
.timeline {
  width: 200px;
  border: 6px solid black;
  display: flex;
  flex-direction: column;
  background: #f1f1f1;
  position: relative;
  background: #6fb49c;
}

.segment-config-container {
}

.timeline-and-segment-config-grid {
  display: grid;
  grid-template-columns: 250px 1fr; /* 30% width + flexible remainder */
  gap: 10px; /* optional spacing */
}

.no-select {
  -webkit-user-select: none; /* Safari */
  -moz-user-select: none; /* Firefox */
  -ms-user-select: none; /* IE/Edge Legacy */
  user-select: none; /* Standard */
}
</style>
