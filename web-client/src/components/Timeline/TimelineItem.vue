<template>
  <div class="timeline-item" @click="onMouseClick">
    <div>FPS: {{ props.fps }}</div>
    <div>Duration: {{ props.duration }}</div>

    <div>
      Global Effects

      <div :key="effect.effectType" v-for="effect in props.effects">
        - {{ effect.effectType }}.{{ effect.method }}({{ effect.args }})
      </div>
    </div>

    <div v-if="selectedSegmentIds.size > 0">
      <div>Merge Tools</div>
      <div>
        <button @click="splitSelectedSegment" v-if="selectedSegmentIds.size == 1">
          Split segment
        </button>
        <button @click="mergeSelectedSegments" v-if="selectedSegmentIds.size > 1">
          Merge selected segments
        </button>
      </div>
    </div>

    <div class="timeline-and-segment-config-grid">
      <div class="timeline-container">
        <div class="timeline no-select" :style="{ height: timelineHeight + 'px' }">
          <TimelineSegment
          v-for="s in timelineSegments"
          :key="s.id"
          :id="s.id"
          :index="s.index"
          :startTime="s.startTime"
          :duration="s.duration"
          :endTime="s.endTime"
          :timelineDuration="props.duration"
          :timelineHeight="timelineHeight"
          :selected="selectedSegmentIds.has(s.id)"
          @onSegmentClick="onSegmentClick"
          @mouseenter="onMouseEnterTimeline"
          @mouseleave="onMouseLeaveTimeline"
          />
        </div>
      </div>

      <div class="segment-config-container">
        <SegmentConfig
          @mouseenter="onMouseEnterTimeline"
          @mouseleave="onMouseLeaveTimeline"
          v-for="s in selectedSegments"
          :key="s.id"
          :id="s.id"
          :index="s.index"
          :startTime="s.startTime"
          :endTime="s.endTime"
          :duration="s.duration"
          :effects="
            s.effects?.map((x) => ({
              id: x.id,
              method: x.method,
              effectType: x.effectType,
              args: x.args,
            }))
          "
          :videos="
            s.videos.map((x) => ({
              id: x.id,
              path: x.path,
              startTime: x.startTime,
            }))
          "
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, type Ref } from 'vue'
import { v4 as uuidv4 } from 'uuid'
import TimelineSegment from './TimelineSegment.vue'
import SegmentConfig from './SegmentConfig.vue'

export interface TimelineItemProps {
  fps: number
  duration: number
  effects: TimelineSegmentEffectProps[] | null | undefined
  segments: TimelineSegmentProps[]
}

interface TimelineSegmentProps {
  id: string
  index: number
  startTime: number
  duration: number
  endTime: number
  splitScreen: boolean
  effects: TimelineSegmentEffectProps[] | null
  videos: TimelineSegmentVideoProps[]
}

interface TimelineSegmentEffectProps {
  id: string
  effectType: string
  method: string
  args: object | null
}

interface TimelineSegmentVideoProps {
  id: string
  path: string
  startTime: number
}

const props = defineProps<TimelineItemProps>()

const timelineSegments: Ref<TimelineSegmentProps[]> = ref([...props.segments])

const isMouseOverTimeline: Ref<boolean> = ref(false)

const selectedSegmentIds: Ref<Set<string>> = ref(new Set<string>())

const selectedSegments = computed<TimelineSegmentProps[]>(() => {
  if (selectedSegmentIds.value.size == 0) {
    return []
  }

  return timelineSegments.value.filter((x) => selectedSegmentIds.value.has(x.id))
})

const onMouseClick = () => {
  if (isMouseOverTimeline.value) {
    return
  }

  selectedSegmentIds.value.clear()
}

const onSegmentClick = (segmentId: string | null, multiselect: boolean) => {
  if (!segmentId) {
    return
  }

  if (!multiselect) {
    selectedSegmentIds.value.clear()
  }
  selectedSegmentIds.value.add(segmentId)
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

  const newSegment: TimelineSegmentProps = {
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

  timelineSegments.value.splice(newSegment.index, 0, newSegment)

  for (let i = 0; i < timelineSegments.value.length; i++) {
    timelineSegments.value[i]!.index = i
  }
  selectedSegmentIds.value.clear()
}

const mergeSelectedSegments = () => {
  const sortedSegments = selectedSegments.value.sort((a, b) => a.index - b.index)
  const startTime = sortedSegments[0]!.startTime
  const endTime = sortedSegments[sortedSegments.length - 1]!.endTime

  const videos = sortedSegments.reduce(
    (video_items: TimelineSegmentVideoProps[], seg: TimelineSegmentProps) => {
      video_items.push(...seg.videos)
      return video_items
    },
    [],
  )

  const effects = sortedSegments.reduce(
    (effect_items: TimelineSegmentEffectProps[], seg: TimelineSegmentProps) => {
      if (seg.effects) effect_items.push(...seg.effects)
      return effect_items
    },
    [],
  )

  const newSegment: TimelineSegmentProps = {
    id: uuidv4(),
    index: sortedSegments[0]!.index,
    startTime: startTime,
    duration: endTime - startTime,
    endTime: endTime,
    splitScreen: sortedSegments[0]!.splitScreen,
    effects: effects,
    videos: videos,
  }

  timelineSegments.value.splice(sortedSegments[0]!.index, sortedSegments.length, newSegment)

  for (let i = 0; i < timelineSegments.value.length; i++) {
    timelineSegments.value[i]!.index = i
  }
  selectedSegmentIds.value.clear()
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
