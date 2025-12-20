<template>
  <div>
    <Card>
      <template #title>Project Media</template>
      <template #subtitle>Total: {{ mediaStore.getMediaNames.length }} items</template>
      <template #content>
        <Chip v-for="e in mediaStore.getMediaNames" :key="e" :label="e" />
        <div v-if="mediaStore.getMediaNames.length == 0">No media imported</div>
      </template>
    </Card>

    <Card>
      <template #title>Import Media</template>
      <template #subtitle>
        Allowed <Chip v-for="m in mediaExt" :key="m">{{ m }}</Chip></template
      >
      <template #content>
        <FileUploading @on-upload="onUpload" />
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import Chip from 'primevue/chip'
import FileUploading from '@/components/Media/FileUploading.vue'
import { type FileUploadUploaderEvent } from 'primevue'
import apiClient from '@/services/apiClient'
import { useProjectSetupStore } from '@/stores/projectSetup'
import { onMounted, watch } from 'vue'
import { Card } from 'primevue'
import { mediaExt, useMediaStore } from '@/stores/mediaStore'

const projectSetupStore = useProjectSetupStore()
const mediaStore = useMediaStore()

onMounted(() => {
  reloadMedia()
})

watch(
  () => projectSetupStore.project,
  () => {
    reloadMedia()
  },
)

async function onUpload(e: FileUploadUploaderEvent) {
  if (!projectSetupStore.hasSelectedProject) return

  const form = new FormData()
  const files: File[] = e.files as File[]

  files.forEach((f) => {
    form.append('files', f)
  })

  await apiClient.postForm(`/api/projects/${projectSetupStore.getProjectName}/media`, form)
  await reloadMedia()
}

async function reloadMedia() {
  mediaStore.mediaPathList = []
  if (!projectSetupStore.hasSelectedProject) return
  const resp = await apiClient.get(`/api/projects/${projectSetupStore.getProjectName}/media`)
  mediaStore.mediaPathList = resp.data
}
</script>
