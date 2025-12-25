<template>
  <div class="timeline-root">
    <Button
      v-if="!isPlaying"
      icon="pi pi-play"
      size="small"
      variant="text"
      severity="contrast"
      class="control-btn play-btn"
      @click="onPlay"
    />
    <Button
      v-if="isPlaying"
      icon="pi pi-pause"
      size="small"
      variant="text"
      severity="contrast"
      class="control-btn pause-btn"
      @click="onPause"
    />

    <div
      class="timeline-area"
      ref="timeline-area"
      @mousemove="onTimelineAreaMouseMove"
      @mouseleave="onTimelineAreaMouseLeave"
      @click="onTimelineAreaMouseClick"
    >
      <div class="track">
        <div
          class="segment"
          :style="{ left: segmentHeadStartX + 'px', width: segmentHeadWidth + 'px' }"
        ></div>

        <div class="playhead" :style="{ left: seekHeadX + 'px' }">
          <div class="playhead-label">{{ secondsToTimeSpanFractionalFormat(seekHeadTime) }}</div>
          <div class="playhead-line" />
        </div>

        <div class="playback-head" :style="{ left: playbackHeadX + 'px' }">
          <div class="playback-line" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { secondsToTimeSpanFractionalFormat } from '@/services/time'
import { ref, useTemplateRef, type Ref, computed, watch, onMounted } from 'vue'
import Button from 'primevue/button'

const props = defineProps({
  duration: Number,
  videoSegmentStartTime: Number,
  videoSegmentDuration: Number,
  playbackTime: Number,
})

const emits = defineEmits(['onSeeked', 'onPlay', 'onPause'])

watch(
  () => props.duration,
  (duration) => {
    if (!duration) return
    segmentHeadStartTime.value = props.videoSegmentStartTime ?? 0
    playbackHeadTime.value = props.videoSegmentStartTime ?? 0
    seekHeadTime.value = props.videoSegmentStartTime ?? 0
  },
)

watch(
  () => props.playbackTime,
  (time) => {
    if (!timelineAreaRef.value) return
    if (!time) return
    if (!props.duration) return

    playbackHeadTime.value = time
  },
)

onMounted(() => {
  onPlay()
})

const isPlaying: Ref<boolean> = ref(false)

const timelineAreaRef = useTemplateRef<HTMLElement>('timeline-area')

const seekHeadTime: Ref<number> = ref(0)
const seekHeadX = computed(() => {
  if (!seekHeadTime.value) return 0
  if (!props.duration) return 0
  if (!timelineAreaRef.value) return 0

  const rect = timelineAreaRef.value.getBoundingClientRect()
  const timeScale = seekHeadTime.value / props.duration

  return rect.width * timeScale
})

const playbackHeadTime: Ref<number> = ref(0)
const playbackHeadX = computed(() => {
  if (!playbackHeadTime.value) return 0
  if (!props.duration) return 0
  if (!timelineAreaRef.value) return 0

  const rect = timelineAreaRef.value.getBoundingClientRect()
  const timeScale = playbackHeadTime.value / props.duration

  return rect.width * timeScale
})

const segmentHeadWidth = computed(() => {
  if (!timelineAreaRef.value) return
  if (!props.duration) return
  const rect = timelineAreaRef.value.getBoundingClientRect()
  return (props.videoSegmentDuration! / props.duration!) * rect.width
})

const segmentHeadStartTime: Ref<number> = ref(0)
const segmentHeadStartX = computed(() => {
  if (!segmentHeadStartTime.value) return 0
  if (!props.duration) return 0
  if (!timelineAreaRef.value) return 0

  const rect = timelineAreaRef.value.getBoundingClientRect()
  const timeScale = segmentHeadStartTime.value / props.duration

  return rect.width * timeScale
})

const onTimelineAreaMouseMove = (e: MouseEvent) => {
  setSeekHeadTime(e)
  emits('onSeeked', seekHeadTime.value)
}

const onTimelineAreaMouseLeave = () => {
  emits('onSeeked', segmentHeadStartTime.value)
}

const onTimelineAreaMouseClick = (e: MouseEvent) => {
  setSeekHeadTime(e)
  moveSegmentIfAllowed(e)
  emits('onSeeked', seekHeadTime.value, true)
}

const onPlay = () => {
  isPlaying.value = true
  emits('onPlay')
}
const onPause = () => {
  isPlaying.value = false
  emits('onPause')
}

const setSeekHeadTime = (e: MouseEvent) => {
  if (!timelineAreaRef.value) return

  const rect = timelineAreaRef.value.getBoundingClientRect()
  let seekHeadX = e.clientX - rect.left

  if (seekHeadX < 0) {
    seekHeadX = 0
  }

  if (seekHeadX > rect.width) {
    seekHeadX = rect.width
  }

  if (seekHeadX + segmentHeadWidth.value! > rect.width) {
    seekHeadX = rect.width - segmentHeadWidth.value!
  } else if (seekHeadX > rect.width) {
    seekHeadX = rect.width
  }

  seekHeadTime.value = (seekHeadX / rect.width) * props.duration!
}

const moveSegmentIfAllowed = (e: MouseEvent) => {
  if (!timelineAreaRef.value) return

  const rect = timelineAreaRef.value.getBoundingClientRect()
  let segmentHeadStartX = e.clientX - rect.left

  if (segmentHeadStartX < 0) {
    segmentHeadStartX = 0
  }

  if (segmentHeadStartX + segmentHeadWidth.value! > rect.width) {
    segmentHeadStartX = rect.width - segmentHeadWidth.value!
  }

  segmentHeadStartTime.value = (segmentHeadStartX / rect.width) * props.duration!
}
</script>

<style scoped>
.timeline-root {
  display: flex;
  align-items: center;
  gap: 12px;
  background: #3c4962;
  margin-top: 34px;
  margin-bottom: 24px;
  border-radius: 6px;
}

.control-btn {
  flex: 0 0 auto;
  margin-left: 10px;
}

.timeline-area {
  flex: 1 1 auto;
  min-width: 0;
}

.track {
  position: relative;
  height: 60px;
}

.segment {
  position: absolute;
  top: -12px;
  bottom: -12px;
  background: #a97fa85b;
  border: 2px rgb(88, 104, 194) solid;
}

.playhead {
  position: absolute;
  top: 0;
  bottom: 0;
  transform: translateX(-50%);
}

.playback-head {
  position: absolute;
  top: 0;
  bottom: 0;
  transform: translateX(-50%);
}

.playhead-label {
  position: absolute;
  top: -30px;
  left: 50%;
  transform: translateX(-50%);
  background: #ffc508;
  color: black;
  padding: 2px 6px;
  border-radius: 4px;
}

.playhead-line {
  position: absolute;
  top: -12px;
  bottom: -12px;
  left: 50%;
  transform: translateX(-50%);
  width: 6px;
  background: #ffc508;
  border-radius: 4px;
}

.playback-line {
  position: absolute;
  top: -12px;
  bottom: -12px;
  left: 50%;
  transform: translateX(-50%);
  width: 2px;
  background: #1c0000;
}
</style>
