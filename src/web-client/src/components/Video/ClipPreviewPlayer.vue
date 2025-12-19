<template>
  <div :style="{ width: state?.width + 'px' }">
    <video-player
      :src="videoUri"
      :controls="true"
      :width="350"
      :muted="true"
      :loop="true"
      @mounted="handleMounted"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, shallowRef } from 'vue'
import apiClient from '@/services/apiClient'
import { VideoPlayer, type VideoPlayerState } from '@videojs-player/vue'
import 'video.js/dist/video-js.css'
import videojs from 'video.js'

type VideoJsPlayer = ReturnType<typeof videojs>

const player = shallowRef<VideoJsPlayer>()
const state = shallowRef<VideoPlayerState>()

const props = defineProps({
  videoPath: String,
})

const videoUri = computed(() =>
  apiClient.getUri({
    url: `/api/media?file_path=${props.videoPath}`,
  }),
)

const handleMounted = (payload: {
  player: VideoJsPlayer | undefined
  state: VideoPlayerState | undefined
}) => {
  player.value = payload.player
  state.value = payload.state
}
</script>

<style scoped></style>
