<template>
  <Card>
    <template #title> Timeline</template>
    <template #subtitle>
      <span v-if="timelineStore.timelineExists">{{
        secondsToTimeSpanFractionalFormat(timelineStore.timeline!.duration)
      }}</span>
    </template>
    <template #content>
      <Toolbar v-if="timelineStore.selectedSegments.length > 0">
        <template #start>
          <Button variant="outlined" @click="splitSelectedSegment"> Split </Button>
          <Button
            variant="outlined"
            @click="mergeSelectedSegments"
            v-if="timelineStore.selectedSegments.length > 1"
          >
            Merge
          </Button>
        </template>
      </Toolbar>

      <Card>
        <template #content>
          <Slider v-model="timelineZoom" :min="0.25" :max="10" :step="0.05" />
        </template>
      </Card>

      <TimelineContainer v-if="timelineStore.timelineExists" :timeline-zoom="timelineZoom" />
    </template>
    <template #footer>
      <Button
        v-if="allowGenerateTimeline"
        @click="onGenerateTimelineClick"
        :loading="generateTimelineLoading"
        >Generate timeline</Button
      >
    </template>
  </Card>
</template>

<script setup lang="ts">
import { v4 as uuidv4 } from 'uuid'

import { computed, onMounted, ref, watch, type Ref } from 'vue'
import apiClient from '../services/apiClient'
import TimelineContainer from '../components/Timeline/TimelineContainer.vue'
import { mapTimelineModel } from '@/shared/mappers/timelineModelMapper'
import { useProjectSetupStore } from '@/stores/projectSetup'
import Button from 'primevue/button'
import { useTimelineStore } from '@/stores/timeline'
import { Card } from 'primevue'
import { secondsToTimeSpanFractionalFormat } from '@/services/time'
import type {
  EffectModel,
  SegmentVideoModel,
  TimelineSegmentModel,
} from '@/shared/models/TimelineModel'

import Toolbar from 'primevue/toolbar'
import Slider from 'primevue/slider'

const timelineStore = useTimelineStore()
const projectSetupStore = useProjectSetupStore()
const generateTimelineLoading: Ref<boolean> = ref(false)
const allowGenerateTimeline = computed(() => projectSetupStore.hasSelectedProject)

const timelineZoom: Ref<number> = ref(1.0)

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
  timelineStore.timeline = null

  if (!projectSetupStore.hasSelectedProject) return

  const url = `/api/${projectSetupStore.getProjectName}/timeline/`

  try {
    const resp = await apiClient.get(url)
    timelineStore.timeline = mapTimelineModel(resp.data)
  } catch (error) {
    console.error(error)
  }
}

async function onGenerateTimelineClick() {
  generateTimelineLoading.value = true
  try {
    await apiClient.post(`/api/${projectSetupStore.getProjectName}/timeline`)
    await reloadTimeline()
  } finally {
    generateTimelineLoading.value = false
  }
}

function splitSelectedSegment() {
  for (const segment of timelineStore.selectedSegments) {
    const middleTime = segment.startTime + segment.duration / 2
    const halfDuration = segment.duration / 2

    const newSegment: TimelineSegmentModel = {
      id: uuidv4(),
      index: segment.index + 1,
      startTime: middleTime,
      duration: halfDuration,
      endTime: segment.endTime,
      splitScreen: segment.splitScreen,
      effects: segment.effects
        ? segment.effects.map((x) => ({
            id: uuidv4(),
            args: !!x.args ? Object.assign({}, x.args) : null,
            method: x.method,
            effectType: x.effectType,
          }))
        : null,
      videos: segment.videos.map(
        (x) =>
          ({
            id: x.id,
            path: x.path,
            startTime: x.startTime,
          }) as SegmentVideoModel,
      ),
      etag: uuidv4()
    }

    segment.endTime = middleTime
    segment.duration = halfDuration
    segment.etag = uuidv4()

    timelineStore.insertSegmentIntoTimeline(newSegment, newSegment.index)

    timelineStore.reindexSegmentsInTimeline()
  }
  timelineStore.clearSelectedSegments()
}

function mergeSelectedSegments() {
  const sortedSegments = timelineStore.selectedSegments.sort((a, b) => a.index - b.index)
  const startTime = sortedSegments[0]!.startTime
  const endTime = sortedSegments[sortedSegments.length - 1]!.endTime

  const videos = sortedSegments[0]?.videos || []

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
    etag: uuidv4()
  }

  timelineStore.timeline!.segments.splice(
    sortedSegments[0]!.index,
    sortedSegments.length,
    newSegment,
  )
  timelineStore.reindexSegmentsInTimeline()
  timelineStore.clearSelectedSegments()
}
</script>
