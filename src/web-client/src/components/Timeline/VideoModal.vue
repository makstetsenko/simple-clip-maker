<template>
  <Dialog v-model:visible="visible" modal header="Chose video" :style="{ width: '50rem' }">
    <Card v-for="v in mediaStore.getVideoPathList" :key="v">
      <template #content>
        <ClipPreviewPlayer :video-path="v" :width="400" />
      </template>
      <template #footer>
        <Button size="small" @click="() => onVideoSelect(v)">Select</Button></template
      >
    </Card>
  </Dialog>
</template>

<script setup lang="ts">
import Dialog from 'primevue/dialog'
import ClipPreviewPlayer from '../Video/ClipPreviewPlayer.vue'
import { useMediaStore } from '@/stores/mediaStore'

import Button from 'primevue/button'

import Card from 'primevue/card'

const visible = defineModel<boolean>()
const mediaStore = useMediaStore()
const emits = defineEmits(['onVideoSelect'])

function onVideoSelect(videoPath: string) {
  emits('onVideoSelect', videoPath)
  visible.value = false
}
</script>
