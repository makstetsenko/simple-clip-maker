<template>
  <div class="timeline-container">
    <div>FPS: {{ props.fps }}</div>
    <div>Duration: {{ props.duration }}</div>

    <div>
      Global Effects

      <div :key="effect.effectType" v-for="effect in props.effects">
        {{ effect.method }}
        {{ effect.effectType }}
        {{ effect.args }}
      </div>
    </div>

    <div class="timeline" :style="{ height: timelineHeight + 'px' }">
      <TimelineSegment
        :key="s.index"
        v-for="s in props.segments"
        :index="s.index"
        :startTime="s.startTime"
        :duration="s.duration"
        :endTime="s.endTime"
        :timelineDuration="props.duration"
        :timelineHeight="timelineHeight"
        :onSegmentClick="(segmentId: number | null) => (selectedSegmentId = segmentId)"
      />
    </div>

    <SegmentConfig
      v-if="selectedSegment"
      :index="selectedSegment.index"
      :startTime="selectedSegment.startTime"
      :endTime="selectedSegment.endTime"
      :duration="selectedSegment.duration"
      :effects="
        selectedSegment.effects?.map((x) => ({
          method: x.method,
          effectType: x.effectType,
          args: x.args,
        }))
      "
      :videos="
        selectedSegment.videos.map((x) => ({
          path: x.path,
          startTime: x.startTime,
        }))
      "
    />
  </div>
</template>

<script setup lang="ts">
import { computed, ref, type Ref } from 'vue'
import TimelineSegment from './TimelineSegment.vue'
import SegmentConfig from './SegmentConfig.vue'

export interface TimelineItemProps {
  fps: number
  duration: number
  effects: TimelineSegmentEffectProps[] | null | undefined
  segments: TimelineSegmentProps[]
}

interface TimelineSegmentProps {
  index: number
  startTime: number
  duration: number
  endTime: number
  splitScreen: boolean
  effects: TimelineSegmentEffectProps[] | null
  videos: TimelineSegmentVideoProps[]
}

interface TimelineSegmentEffectProps {
  effectType: string
  method: string
  args: []
}

interface TimelineSegmentVideoProps {
  path: string
  startTime: number
}

const props = defineProps<TimelineItemProps>()

const selectedSegmentId: Ref<number | null> = ref<number | null>(null)
const selectedSegment = computed<TimelineSegmentProps | null>(() => {
  if (selectedSegmentId.value === null || selectedSegmentId.value === undefined) {
    return null
  }

  return props.segments[selectedSegmentId.value] as TimelineSegmentProps
})

const timelineHeight = 2000 // px
</script>

<style scoped>
.timeline-container {
  width: 400px;
  background: #d3d3d3;
}

.timeline {
  width: 200px;
  border: 6px solid black;
  display: flex;
  flex-direction: column;
  background: #f1f1f1;
}
</style>
