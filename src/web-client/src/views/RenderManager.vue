<template>
  <div class="grid">
    <div class="col">
      <Button
        severity="help"
        @click="renderProject"
        :loading="renderingInProgress"
        variant="outlined"
        v-if="timelineStore.timelineExists"
      >
        Render
      </Button>
    </div>

    <div class="col-12">
      <span v-if="!previewVideoPath"> No preview</span>

      <ClipPreviewPlayer
        v-if="previewVideoPath"
        :video-path="previewVideoPath"
        :width="1100"
        :height="720"
        :volume-panel="true"
        :muted="false"
        @on-seeked="onSeeked"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import apiClient from '@/services/apiClient'
import { useProjectSetupStore } from '@/stores/projectSetup'
import { useTimelineStore } from '@/stores/timeline'
import Button from 'primevue/button'
import { ref, type Ref } from 'vue'
import ClipPreviewPlayer from '@/components/Video/ClipPreviewPlayer.vue'

const renderingInProgress: Ref<boolean> = ref(false)

const projectSetupStore = useProjectSetupStore()
const timelineStore = useTimelineStore()

const previewVideoPath: Ref<string | null> = ref(null)

async function renderProject() {
  if (!projectSetupStore.hasSelectedProject) return

  previewVideoPath.value = null
  renderingInProgress.value = true
  try {
    await upsertTimeline()
    const resp = await apiClient.post(
      `/api/projects/${projectSetupStore.getProjectName}/render?debug=${projectSetupStore.debugMode}`,
    )
    previewVideoPath.value = resp.data
  } finally {
    renderingInProgress.value = false
  }
}

async function upsertTimeline() {
  await timelineStore.upsert(projectSetupStore.getProjectName!)
}

function onSeeked(time: number) {
  if (!timelineStore.timeline) return

  const index = timelineStore.timeline.segments.findIndex(
    (x) => x.startTime <= time && x.endTime > time,
  )

  if (index < 0) return
  timelineStore.clearSelectedSegments()
  timelineStore.appendSelectSegmentByIndex(index)
}
</script>
