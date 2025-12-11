<template>
  <h3>Timeline config</h3>
  <button @click="onLoadTimelineClick">Load timeline</button>

  <TimelineItem
    v-if="timelineProps"
    :fps="timelineProps.fps"
    :duration="timelineProps.duration"
    :effects="timelineProps.effects"
    :segments="timelineProps.segments"
  />
</template>

<script setup lang="ts">
import { computed, ref, type Ref } from 'vue'
import apiClient from '../services/apiClient'
import TimelineItem from '../components/Timeline/TimelineItem.vue'
import { type TimelineItemProps } from '../components/Timeline/TimelineItem.vue'
import { type TimelineConfig } from '../models/Timeline'

const timelineConfig: Ref<TimelineConfig | null> = ref<TimelineConfig | null>(null)

const timelineProps = computed<TimelineItemProps | null>(() => {
  if (!timelineConfig.value) return null

  return {
    fps: timelineConfig.value.fps,
    duration: timelineConfig.value.duration,
    effects: timelineConfig.value.effects.map((x) => ({
      method: x.method,
      args: x.args,
      effectType: x.effect_type,
    })),
    segments: timelineConfig.value.segments.map((x) => ({
      duration: x.duration,
      endTime: x.end_time,
      startTime: x.start_time,
      index: x.index,
      splitScreen: x.is_split_screen,
      videos: x.videos.map((v) => ({
        path: v.path,
        startTime: v.start_time,
      })),
      effects: x.effects?.map((e) => ({
        effectType: e.effect_type,
        method: e.method,
        args: e.args,
      })),
    })),
  } as TimelineItemProps
})

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
