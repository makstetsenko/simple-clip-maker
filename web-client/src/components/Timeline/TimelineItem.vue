<template>
  <div class="timeline-container">
    <div>FPS: {{ props.fps }}</div>
    <div>Duration: {{ props.duration }}</div>

    <div>
      Effects

      <div :key="effect.effect_type" v-for="effect in props.effects">
        {{ effect.method }}
        {{ effect.effect_type }}
        {{ effect.args }}
      </div>
    </div>

    <div class="timeline" :style="{ height: timelineHeight + 'px' }">
      <TimelineSegment
        :key="s.index"
        v-for="s in props.segments"
        :index="s.index"
        :start_time="s.start_time"
        :duration="s.duration"
        :end_time="s.end_time"
        :timeline_duration="props.duration"
        :timeline_height="timelineHeight"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import type { TimelineConfig } from '../../models/Timeline'
import TimelineSegment from './TimelineSegment.vue'

const props = defineProps<TimelineConfig>()

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
