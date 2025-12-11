<!-- <template>
  <video-player
    src="/your-path/video.mp4"
    poster="/your-path/poster.jpg"
    controls
    :loop="true"
    :volume="0.6"
    ...
    @mounted="..."
    @ready="..."
    @play="..."
    @pause="..."
    @ended="..."
    @seeking="..."
    ...
  />
</template>

<script>
  import { defineComponent } from 'vue'
  import { VideoPlayer } from '@videojs-player/vue'
  import 'video.js/dist/video-js.css'

  export default defineComponent({
    components: {
      VideoPlayer
    }
  })
</script> -->

<template>
  <div>
    <video-player
      :src="videoUri"
      :controls="true"
      :width="400"
      :muted="true"
      :loop="true"
      :inactivity-timeout="60 * 1000"
      :disable-picture-in-picture="true"
      :playback-rates="[0.75, 1, 1.25, 1.5, 2, 4]"
      @seeked="onSeeked"
      @mounted="handleMounted"
    />
    <div>Seek time: {{ seekTime }}</div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, shallowRef, type Ref } from 'vue'
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
    url: '/files' + props.videoPath,
  }),
)

const seekTime: Ref<number> = ref(0)

const onSeeked = () => {
  seekTime.value = state.value!.currentTime
}

const handleMounted = (payload: any) => {
  player.value = payload.player
  state.value = payload.state
}
</script>

<style scoped></style>
