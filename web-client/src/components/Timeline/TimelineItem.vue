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

    <div class="timeline">
      <TimelineSegment
        :key="s.index"
        v-for="s in props.segments"
        :index="s.index"
        :time="s.start_time"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import type { TimelineConfig } from '../../models/Timeline'
import TimelineSegment from './TimelineSegment.vue'

const props = defineProps<TimelineConfig>()
</script>

<style scoped>
.timeline-container {
  width: 400px;
  padding: 40px;
  background: #d3d3d3;
}

.timeline {
  width: 200px;
  border: 6px solid black;
  padding: 10px 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
  background: #f1f1f1;
}
</style>
