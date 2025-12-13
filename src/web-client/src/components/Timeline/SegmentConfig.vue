<template>
  <div class="segment-config">
    <h3>
      Seg: #{{ model?.index }} ({{ secondsToTimeSpanFractionalFormat(model?.startTime) }} -
      {{ secondsToTimeSpanFractionalFormat(model?.endTime) }})
    </h3>

    <div>
      Videos
      <div :key="v.id" v-for="v in model?.videos">
        <div>{{ v.startTime }} - {{ v.path }}</div>
        <VideoPlayer
          :videoPath="v.path"
          :segmentStartTime="v.startTime"
          :segmentDuration="model?.duration"
        />
      </div>
    </div>

    <div v-if="model?.effects">
      Effects

      <EffectsSelector v-model="model!.effects" />
    </div>
  </div>
</template>

<script setup lang="ts">
import VideoPlayer from '../Video/VideoPlayer.vue'
import EffectsSelector from '../Effects/EffectsSelector.vue'
import type { TimelineSegmentModel } from '@/shared/models/TimelineModel'
import { secondsToTimeSpanFractionalFormat } from '@/services/time'

const model = defineModel<TimelineSegmentModel>()
</script>

<style scoped>
.segment-config {
  background: #9cadbb;
}
</style>
