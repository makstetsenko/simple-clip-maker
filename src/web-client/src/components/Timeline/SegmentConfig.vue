<template>
  <div class="segment-config">
    <h3>
      Seg: #{{ index }} ({{ secondsToTimeSpanFractionalFormat(startTime) }} -
      {{ secondsToTimeSpanFractionalFormat(endTime) }})
    </h3>

    <div>
      Videos
      <div :key="v.id" v-for="v in videos">
        <div>{{ v.startTime }} - {{ v.path }}</div>
        <VideoPlayer
          :videoPath="v.path"
          :segmentStartTime="v.startTime"
          :segmentDuration="duration"
        />
      </div>
    </div>

    <div v-if="effects">
      Effects
      <div :key="e.id" v-for="e in effects">{{ e.effectType }}.{{ e.method }}({{ e.args }})</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { secondsToTimeSpanFractionalFormat } from '@/services/time'
import VideoPlayer from '../Video/VideoPlayer.vue'

interface SegmentConfigProps {
  id: string
  index: number
  startTime: number
  duration: number
  endTime: number
  videos: SegmentVideoProps[]
  effects: SegmentEffectProps[] | null | undefined
}

interface SegmentEffectProps {
  id: string
  effectType: string
  method: string
  args: object | null
}

interface SegmentVideoProps {
  id: string
  path: string
  startTime: number
}

defineProps<SegmentConfigProps>()
</script>

<style scoped>
.segment-config {
  background: #9cadbb;
}
</style>
