<template>
  <h3>Timeline config</h3>
  <button @click="onLoadTimelineClick">Load timeline</button>
  <button @click="onBuildClick">Build timeline</button>

  <TimelineItem v-if="timelineItem" v-model="timelineItem" />
</template>

<script setup lang="ts">
import { ref, type Ref } from 'vue'
import apiClient from '../services/apiClient'
import TimelineItem from '../components/Timeline/TimelineItem.vue'
import type { TimelineModel } from '@/shared/models/TimelineModel'
import { mapTimelineModel } from '@/shared/mappers/timelineModelMapper'
import { mapTimeline } from '@/shared/mappers/timelineMapper'

const timelineItem: Ref<TimelineModel | null> = ref<TimelineModel | null>(null)

async function onLoadTimelineClick() {
  const url = '/api/timeline/config'

  try {
    const resp = await apiClient.get(url)
    timelineItem.value = mapTimelineModel(resp.data)
  } catch (error) {
    console.error(error)
  }
}

function onBuildClick() {
  if (!timelineItem.value) return
  const timelineObj = mapTimeline(timelineItem.value)
  console.log(timelineObj)
}
</script>
