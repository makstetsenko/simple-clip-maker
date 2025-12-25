<template>
  <Dialog v-model:visible="visible" modal header="Chose video" :style="{ width: '50rem' }">
    <div>
      <label for="">Playback speed</label>
      <Slider v-model="videosPlaybackSpeed" class="w-56" :min="1" :max="10" :step="0.5" />
    </div>
    <div class="grid">
      <div class="col-12 md:col-6 lg:col-4" v-for="v in mediaStore.getVideoPathList" :key="v">
        <Card>
          <template #content>
            <ClipPreviewPlayer :video-path="v" :width="150" :playback-rate="videosPlaybackSpeed" :autoplay="true" :muted="true"/>
          </template>
          <template #footer>
            <Button size="small" @click="() => onVideoSelect(v)">Select</Button></template
          >
        </Card>
      </div>
    </div>
  </Dialog>
</template>

<script setup lang="ts">
import Dialog from 'primevue/dialog'
import ClipPreviewPlayer from '../Video/ClipPreviewPlayer.vue'
import { useMediaStore } from '@/stores/mediaStore'

import Slider from 'primevue/slider'

import Button from 'primevue/button'

import Card from 'primevue/card'
import { ref, type Ref } from 'vue'

const visible = defineModel<boolean>()
const mediaStore = useMediaStore()
const emits = defineEmits(['onVideoSelect'])

const videosPlaybackSpeed: Ref<number> = ref(3)

function onVideoSelect(videoPath: string) {
  emits('onVideoSelect', videoPath)
  visible.value = false
}
</script>
