<template>
  <h3>Timeline config</h3>
  <button @click="onLoadTimelineClick">Load timeline</button>

  <TimelineItem
    v-if="timelineConfig"
    :fps="timelineConfig.fps"
    :duration="timelineConfig.duration"
    :effects="timelineConfig.effects"
    :segments="timelineConfig.segments"
  />
</template>

<script setup lang="ts">
import { ref, type Ref } from 'vue'
import apiClient from '../services/apiClient'
import TimelineItem from '../components/Timeline/TimelineItem.vue'
import { type TimelineConfig } from '../models/Timeline'

const timelineConfig: Ref<TimelineConfig | null> = ref<TimelineConfig | null>(null)

async function onLoadTimelineClick() {
  const url = 'api/timeline/config'

  try {
    const resp = await apiClient.get(url)
    timelineConfig.value = resp.data
  } catch (error) {
    console.error(error)
  }
}
</script>
