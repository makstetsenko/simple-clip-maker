<template>
  <div :style="{ width: state?.width + 'px' }">
    <video-player
      :src="videoUri"
      :controls="false"
      :width="400"
      :muted="true"
      :loop="true"
      @mounted="handleMounted"
      @timeupdate="onTimeUpdated"
    />

    <VideoPlayerTimelineBar
      :duration="state?.duration"
      :playback-time="state?.currentTime"
      :segment-start-time="playheadTime"
      :segment-duration="segmentDuration"
      @on-seeked="onVideoTimelineSeeked"
      @on-pause="() => player?.pause()"
      @on-play="() => player?.play()"
    />

    <div class="footer">
      <div class="current-time">{{ secondsToTimeSpanFractionalFormat(state?.currentTime) }}</div>
      <div class="video-duration">{{ secondsToTimeSpanFractionalFormat(state?.duration) }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, shallowRef, type Ref } from 'vue'
import apiClient from '@/services/apiClient'
import { VideoPlayer, type VideoPlayerState } from '@videojs-player/vue'
import 'video.js/dist/video-js.css'
import videojs from 'video.js'
import VideoPlayerTimelineBar from './VideoPlayerTimelineBar.vue'
import { secondsToTimeSpanFractionalFormat } from '@/services/time'

type VideoJsPlayer = ReturnType<typeof videojs>

const player = shallowRef<VideoJsPlayer>()
const state = shallowRef<VideoPlayerState>()

const props = defineProps({
  videoPath: String,
  segmentStartTime: Number,
  segmentDuration: Number,
})

onMounted(() => {
  if (player.value) {
    player.value.currentTime(props.segmentStartTime!)
  }
})

const playheadTime: Ref<number> = ref(props.segmentStartTime!)
const segmentDuration = props.segmentDuration

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

const onTimeUpdated = () => {
  const endTime: number = playheadTime.value + segmentDuration!

  if (state.value!.currentTime >= endTime) {
    player.value!.currentTime(playheadTime.value)
  }
}

const onVideoTimelineSeeked = (time: number) => {
  player.value!.currentTime(time)
  playheadTime.value = time
}
</script>

<style scoped>
.footer {
  display: grid;
  grid-template-columns: auto auto;
  justify-content: space-between;
}

.footer.current-time {
  justify-self: start;
}

.footer.video-duration {
  justify-self: end;
}
</style>
