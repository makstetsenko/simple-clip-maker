<template>
  <h3>Timeline config</h3>
  <Button @click="upsertTimeline" v-if="timelineModel">Save</Button>
  <TimelineItem v-if="timelineModel" v-model="timelineModel" />

  <div v-if="!timelineModel">
    <Button @click="onGenerateTimelineClick" :loading="generateTimelineLoading"
      >Generate timeline</Button
    >
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch, type Ref } from 'vue'
import apiClient from '../services/apiClient'
import TimelineItem from '../components/Timeline/TimelineItem.vue'
import type { TimelineModel } from '@/shared/models/TimelineModel'
import { mapTimelineModel } from '@/shared/mappers/timelineModelMapper'
import { mapTimeline } from '@/shared/mappers/timelineMapper'
import { useProjectSetupStore } from '@/stores/projectSetup'
import Button from 'primevue/button'

const timelineModel: Ref<TimelineModel | null> = ref<TimelineModel | null>(null)
const projectSetupStore = useProjectSetupStore()
const generateTimelineLoading: Ref<boolean> = ref(false)

onMounted(() => {
  reloadTimeline()
})

watch(
  () => projectSetupStore.project,
  () => {
    reloadTimeline()
  },
)

async function reloadTimeline() {
  timelineModel.value = null

  const url = `/api/${projectSetupStore.getProjectName}/timeline/`

  try {
    const resp = await apiClient.get(url)
    timelineModel.value = mapTimelineModel(resp.data)
  } catch (error) {
    console.error(error)
  }
}

async function upsertTimeline() {
  if (!timelineModel.value) return
  const timelineObj = mapTimeline(timelineModel.value)

  const url = `/api/${projectSetupStore.getProjectName}/timeline/upsert`
  await apiClient.post(url, timelineObj)
}

async function onGenerateTimelineClick() {
  if (timelineModel.value) return

  generateTimelineLoading.value = true
  try {
    await apiClient.post(`/api/${projectSetupStore.getProjectName}/timeline`)
    await reloadTimeline()
  } finally {
    generateTimelineLoading.value = false
  }
}
</script>
