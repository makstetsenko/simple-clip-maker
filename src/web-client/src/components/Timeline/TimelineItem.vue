<template>
  <div class="timeline-item" @click="onMouseClick">
    <div>FPS: {{ timelineModel!.fps }}</div>
    <div>Duration: {{ timelineModel!.duration }}</div>

    <div @mouseenter="onMouseEnterTimeline" @mouseleave="onMouseLeaveTimeline">
      Global Effects
      <EffectsSelector v-model="timelineModel!.effects!" />
    </div>

    <div v-if="selectedSegments.length > 0">
      <div>Merge Tools</div>
      <div>
        <button @click="splitSelectedSegment" v-if="selectedSegments.length == 1">
          Split segment
        </button>
        <button @click="mergeSelectedSegments" v-if="selectedSegments.length > 1">
          Merge selected segments
        </button>
      </div>
    </div>

    <div class="timeline-and-segment-config-grid">
      <div class="timeline-container">
        <div class="timeline no-select" :style="{ height: timelineHeight + 'px' }">
          <TimelineSegment
            v-for="(s, i) in timelineModel!.segments"
            :key="s.id"
            v-model="timelineModel!.segments[i]"
            :timelineHeight="3000"
            :timelineDuration="timelineModel!.duration"
            :selected="selectedSegments.some((x) => x.id === s.id)"
            @onSegmentClick="onSegmentClick"
            @mouseenter="onMouseEnterTimeline"
            @mouseleave="onMouseLeaveTimeline"
          />
        </div>
      </div>

      <div class="segment-config-container">
        <SegmentConfig
          v-for="(s, i) in selectedSegments"
          :key="s.id"
          v-model="selectedSegments[i]"
          @mouseenter="onMouseEnterTimeline"
          @mouseleave="onMouseLeaveTimeline"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, type Ref } from 'vue'
import { v4 as uuidv4 } from 'uuid'
import TimelineSegment from './TimelineSegment.vue'
import SegmentConfig from './SegmentConfig.vue'
import EffectsSelector from '../Effects/EffectsSelector.vue'
import type {
  EffectModel,
  SegmentVideoModel,
  TimelineModel,
  TimelineSegmentModel,
} from '@/shared/models/TimelineModel'

const timelineModel = defineModel<TimelineModel>()

const selectedSegments: Ref<TimelineSegmentModel[]> = ref([])
const isMouseOverTimeline: Ref<boolean> = ref(false)

const onMouseClick = () => {
  if (isMouseOverTimeline.value) {
    return
  }

  selectedSegments.value.splice(0, selectedSegments.value.length)
}

const onSegmentClick = (segmentId: string | null, multiselect: boolean) => {
  if (!segmentId) {
    return
  }
  if (!multiselect) {
    selectedSegments.value.splice(0, selectedSegments.value.length)
  }
  const index = timelineModel.value!.segments.findIndex((x) => x.id === segmentId)!
  selectedSegments.value.push(timelineModel.value!.segments[index]!)
}

const onMouseEnterTimeline = () => {
  isMouseOverTimeline.value = true
}

const onMouseLeaveTimeline = () => {
  isMouseOverTimeline.value = false
}

const timelineHeight = 3000 // px

const splitSelectedSegment = () => {
  const segment = selectedSegments.value[0]!

  const middleTime = segment.startTime + segment.duration / 2
  const halfDuration = segment.duration / 2

  const newSegment: TimelineSegmentModel = {
    id: uuidv4(),
    index: segment.index + 1,
    startTime: middleTime,
    duration: halfDuration,
    endTime: segment.endTime,
    splitScreen: segment.splitScreen,
    effects: segment.effects ? [...segment.effects] : null,
    videos: [...segment.videos],
  }

  segment.endTime = middleTime
  segment.duration = halfDuration

  timelineModel.value!.segments.splice(newSegment.index, 0, newSegment)

  for (let i = 0; i < timelineModel.value!.segments.length; i++) {
    timelineModel.value!.segments[i]!.index = i
  }
  selectedSegments.value.splice(0, selectedSegments.value.length)
}

const mergeSelectedSegments = () => {
  const sortedSegments = selectedSegments.value.sort((a, b) => a.index - b.index)
  const startTime = sortedSegments[0]!.startTime
  const endTime = sortedSegments[sortedSegments.length - 1]!.endTime

  const videos = sortedSegments.reduce(
    (video_items: SegmentVideoModel[], seg: TimelineSegmentModel) => {
      video_items.push(...seg.videos)
      return video_items
    },
    [],
  )

  const effects = sortedSegments.reduce(
    (effect_items: EffectModel[], seg: TimelineSegmentModel) => {
      if (seg.effects) effect_items.push(...seg.effects)
      return effect_items
    },
    [],
  )

  const newSegment: TimelineSegmentModel = {
    id: uuidv4(),
    index: sortedSegments[0]!.index,
    startTime: startTime,
    duration: endTime - startTime,
    endTime: endTime,
    splitScreen: sortedSegments[0]!.splitScreen,
    effects: effects,
    videos: videos,
  }

  timelineModel.value!.segments.splice(sortedSegments[0]!.index, sortedSegments.length, newSegment)

  for (let i = 0; i < timelineModel.value!.segments.length; i++) {
    timelineModel.value!.segments[i]!.index = i
  }
  selectedSegments.value.splice(0, selectedSegments.value.length)
}
</script>

<style scoped>
.timeline-item {
  background: #eee;
}
.timeline-container {
  height: 60vh;
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
