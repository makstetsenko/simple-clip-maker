<template>
  <div class="segment-config">
    <Card>
      <template #title> Seg: #{{ model?.index }} </template>
      <template #subtitle>
        ({{ secondsToTimeSpanFractionalFormat(model?.startTime) }} -
        {{ secondsToTimeSpanFractionalFormat(model?.endTime) }})

        <Button @click="onBuildPreview" :loading="previewLoading">Build preview</Button>
      </template>
      <template #content>
        <Splitter>
          <SplitterPanel>
            <div :key="v.id" v-for="v in model?.videos">
              <VideoPlayer
                :videoPath="v.path"
                :segmentStartTime="v.startTime"
                :segmentDuration="model?.duration"
                @onSegmentStartTimeChanged="(t) => (v.startTime = t)"
              />
            </div>
          </SplitterPanel>

          <SplitterPanel>
            <div v-if="previewVideoPath">
              <ClipPreviewPlayer :videoPath="previewVideoPath" />
            </div>
            <div v-else>No preview clip</div>
          </SplitterPanel>
        </Splitter>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import VideoPlayer from '../Video/SegmentSelectionPlayer.vue'
import type { TimelineSegmentModel } from '@/shared/models/TimelineModel'
import { secondsToTimeSpanFractionalFormat } from '@/services/time'
import ClipPreviewPlayer from '../Video/ClipPreviewPlayer.vue'
import apiClient from '@/services/apiClient'

import Card from 'primevue/card'
import { ref, type Ref } from 'vue'
import { useProjectSetupStore } from '@/stores/projectSetup'
import Button from 'primevue/button'

import Splitter from 'primevue/splitter'
import SplitterPanel from 'primevue/splitterpanel'

const model = defineModel<TimelineSegmentModel>()
const projectSetupStore = useProjectSetupStore()
const previewVideoPath: Ref<string | null> = ref(null)
const previewLoading: Ref<boolean> = ref(false)

async function onBuildPreview() {
  previewVideoPath.value = null
  previewLoading.value = true
  const url = `/api/projects/${projectSetupStore.getProjectName}/segment/${model.value!.id}/render/preview?debug=false`
  const resp = await apiClient.post(url)
  previewVideoPath.value = resp.data
  previewLoading.value = false
}
</script>

<style scoped>
.segment-config {
  background: #9cadbb;
}
</style>
