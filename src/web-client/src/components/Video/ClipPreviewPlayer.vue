<template>
  <div :style="{ width: state?.width + 'px' }">
    <video-player
      :src="videoUri"
      :controls="true"
      :width="width ?? 350"
      :height="height"
      :muted="muted ?? true"
      :loop="true"
      :autoplay="autoplay ?? true"
      @mounted="handleMounted"
      :control-bar="{
        audioTrackButton: false,
        captionsButton: false,
        chaptersButton: false,
        descriptionsButton: false,
        remainingTimeDisplay: false,
        pictureInPictureToggle: false,
        fullscreenToggle: false,
        playToggle: playToggle ?? false,
        volumePanel: volumePanel ?? false,
      }"
      :inactivity-timeout="60_000"
      :playback-rate="playbackRate ?? 1"
      @seeked="onSeeked"
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
const emits = defineEmits(['onSeeked'])

const props = defineProps({
  videoPath: String,
  width: Number,
  playbackRate: Number,
  volumePanel: Boolean,
  muted: Boolean,
  height: Number,
  playToggle: Boolean,
  autoplay: Boolean
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

function onSeeked() {
  if (!player.value) return

  const currentTime = player.value.currentTime()
  emits('onSeeked', currentTime)
}
</script>

<style scoped></style>
