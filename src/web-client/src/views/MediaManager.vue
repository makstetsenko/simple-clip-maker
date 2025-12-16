<template>
  <div>
    <Inplace>
      <template #display>
        <div>Import media</div>
        <Chip v-for="e in mediaExt" :key="e" :label="e" />
      </template>
      <template #content="{ closeCallback }">
        <Button severity="danger" @click="closeCallback"> Close uploader </Button>
        <FileUploading @on-upload="onUpload" />
      </template>
    </Inplace>

    <div v-if="mediaItems.length > 0">
      <div>Media</div>
      <Chip v-for="e in mediaItems" :key="e" :label="e" />
    </div>
  </div>
</template>

<script setup lang="ts">
import Inplace from 'primevue/inplace'
import Chip from 'primevue/chip'
import FileUploading from '@/components/Media/FileUploading.vue'
import { Button, type FileUploadUploaderEvent } from 'primevue'
import apiClient from '@/services/apiClient'
import { useProjectSetupStore } from '@/stores/projectSetup'
import { onMounted, ref, type Ref } from 'vue'

const mediaExt = ['.mp3', '.m4a', '.mp4', '.mov', '.m4v']
const projectSetupStore = useProjectSetupStore()
const mediaItems: Ref<string[]> = ref([])

onMounted(() => {
  reloadMedia()
})

async function onUpload(e: FileUploadUploaderEvent) {
  const form = new FormData()
  const files: File[] = e.files as File[]

  files.forEach((f) => {
    form.append('files', f)
  })

  await apiClient.postForm(`/api/projects/${projectSetupStore.getProjectName}/media`, form)
  await reloadMedia()
}

async function reloadMedia() {
  const resp = await apiClient.get(`/api/projects/${projectSetupStore.getProjectName}/media`)
  mediaItems.value = resp.data
}
</script>
