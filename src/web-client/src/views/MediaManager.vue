<template>
  <div>
    <Card>
      <template #title>Project Media</template>
      <template #subtitle>Total: {{ mediaItems.length }} items</template>
      <template #content>
        <Chip v-for="e in mediaItems" :key="e" :label="e" />
        <div v-if="mediaItems.length == 0">No media imported</div>
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
import { onMounted, ref, watch, type Ref } from 'vue'
import { Card } from 'primevue'

const mediaExt = ['.mp3', '.m4a', '.mp4', '.mov', '.m4v']
const projectSetupStore = useProjectSetupStore()
const mediaItems: Ref<string[]> = ref([])

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
  mediaItems.value = []
  if (!projectSetupStore.hasSelectedProject) return
  const resp = await apiClient.get(`/api/projects/${projectSetupStore.getProjectName}/media`)
  mediaItems.value = resp.data
}
</script>
