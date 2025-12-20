<template>
  <div class="segment-config">
    <Card>
      <template #title>
        Seg: #{{ model?.index }}
        <ToggleButton
          v-model="timelineStore.autoScrollOn"
          onLabel="Auto scrolling"
          offLabel="Stay on segment"
          size="small"
        />
        <ToggleButton
          v-model="model!.splitScreen"
          onLabel="Split screen"
          offLabel="Normal"
          size="small"
        />
      </template>
      <template #subtitle>
        {{ secondsToTimeSpanFractionalFormat(model?.duration) }}
        ({{ secondsToTimeSpanFractionalFormat(model?.startTime) }} -
        {{ secondsToTimeSpanFractionalFormat(model?.endTime) }})
      </template>
      <template #content>
        <Splitter>
          <SplitterPanel>
            <ScrollPanel style="width: 100%; height: 1000px">
              <Card :key="v.id" v-for="v in model?.videos">
                <template #content
                  ><VideoPlayer
                    :videoPath="v.path"
                    :videoSegmentStartTime="v.startTime"
                    :videoSegmentDuration="model?.duration"
                    @onSegmentStartTimeChanged="(t) => (v.startTime = t)"
                    @onSegmentPlayingEnd="onSegmentPlayingEnd"
                /></template>

                <template #footer>
                  <Button @click="() => onSelectAnotherVideoBtnClick(v.id)" size="small"
                    >Replace video</Button
                  >
                  <Button @click="() => onRemoveVideo(v.id)" size="small" severity="danger"
                    >Remove</Button
                  >
                  <Button
                    icon="pi pi-arrow-up"
                    @click="() => onSwapUp(v.id)"
                    size="small"
                    variant="text"
                    severity="contrast"
                  />
                  <Button
                    icon="pi pi-arrow-down"
                    @click="() => onSwapDown(v.id)"
                    size="small"
                    variant="text"
                    severity="contrast"
                  />
                </template>
              </Card>
            </ScrollPanel>
          </SplitterPanel>

          <SplitterPanel>
            <Button @click="onBuildPreview" :loading="previewLoading" size="small"
              >Generate preview</Button
            >
            <div v-if="previewVideoPath">
              <ClipPreviewPlayer :videoPath="previewVideoPath" />
            </div>
            <div v-else>No preview</div>
          </SplitterPanel>
        </Splitter>
      </template>
      <template #footer>
        <Button @click="onAddVideo" size="small" severity="success">Add video</Button>
      </template>
    </Card>

    <VideoSelectModal v-model="videoSelectModalVisible" @onVideoSelect="onVideoSelect" />
  </div>
</template>

<script setup lang="ts">
import VideoPlayer from '../Video/SegmentSelectionPlayer.vue'
import type { SegmentVideoModel, TimelineSegmentModel } from '@/shared/models/TimelineModel'
import { secondsToTimeSpanFractionalFormat } from '@/services/time'
import ClipPreviewPlayer from '../Video/ClipPreviewPlayer.vue'
import apiClient from '@/services/apiClient'

import Card from 'primevue/card'
import { ref, type Ref } from 'vue'
import { useProjectSetupStore } from '@/stores/projectSetup'
import Button from 'primevue/button'

import Splitter from 'primevue/splitter'
import SplitterPanel from 'primevue/splitterpanel'
import { useTimelineStore } from '@/stores/timeline'
import ToggleButton from 'primevue/togglebutton'
import { mapTimeline } from '@/shared/mappers/timelineMapper'
import VideoSelectModal from './VideoModal.vue'
import { v4 as uuidv4 } from 'uuid'

import ScrollPanel from 'primevue/scrollpanel'

const model = defineModel<TimelineSegmentModel>()
const projectSetupStore = useProjectSetupStore()
const timelineStore = useTimelineStore()
const previewVideoPath: Ref<string | null> = ref(null)
const previewLoading: Ref<boolean> = ref(false)
const videoSelectModalVisible: Ref<boolean> = ref(false)

async function onBuildPreview() {
  await upsertTimeline()
  previewVideoPath.value = null
  previewLoading.value = true
  const url = `/api/projects/${projectSetupStore.getProjectName}/segment/${model.value!.id}/render/preview?debug=${projectSetupStore.debugMode}`
  const resp = await apiClient.post(url)
  previewVideoPath.value = resp.data
  previewLoading.value = false
}

async function upsertTimeline() {
  if (!timelineStore.timelineExists) return
  const timelineObj = mapTimeline(timelineStore.timeline!)

  const url = `/api/${projectSetupStore.getProjectName}/timeline/upsert`
  await apiClient.post(url, timelineObj)
}

function onSegmentPlayingEnd() {
  if (!model.value) return
  if (!timelineStore.autoScrollOn) return

  let nextSegmentIndex = model.value.index + 1

  if (nextSegmentIndex >= timelineStore.timeline!.segments.length) {
    nextSegmentIndex = 0
  }

  timelineStore.clearSelectedSegments()
  timelineStore.appendSelectSegmentByIndex(nextSegmentIndex)
}

let videoIdToReplace: string | null = null
function onSelectAnotherVideoBtnClick(videoId: string) {
  videoIdToReplace = videoId
  videoSelectModalVisible.value = true
}
function onRemoveVideo(videoId: string) {
  if (!model.value) return

  const videoIndex = model.value.videos.findIndex((x) => x.id === videoId)

  if (videoIndex < 0) return

  model.value.videos.splice(videoIndex, 1)
}

function onVideoSelect(videoPath: string) {
  if (!model.value) return

  const newVideo = {
    id: uuidv4(),
    path: videoPath,
    startTime: 0,
  } as SegmentVideoModel

  if (!videoIdToReplace) {
    // Means we just add new video
    model.value.videos.push(newVideo)
    return
  }

  const videoIndex = model.value.videos.findIndex((x) => x.id === videoIdToReplace)
  if (videoIndex < 0) return

  model.value.videos.splice(videoIndex, 1, newVideo)
}

function onAddVideo() {
  videoIdToReplace = null
  videoSelectModalVisible.value = true
}

function onSwapUp(videoId: string) {
  if (!model.value) return
  const index = model.value.videos.findIndex((x) => x.id === videoId)

  if (index == 0) return

  const video = model.value.videos.splice(index, 1)[0]!
  model.value.videos.splice(index - 1, 0, video)
}
function onSwapDown(videoId: string) {
  if (!model.value) return
  const index = model.value.videos.findIndex((x) => x.id === videoId)

  if (index == model.value.videos.length - 1) return

  const video = model.value.videos.splice(index, 1)[0]!
  model.value.videos.splice(index + 1, 0, video)
}
</script>

<style scoped>
.segment-config {
  background: #9cadbb;
}
</style>
