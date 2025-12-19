<template>
  <div class="timeline-root">
    <button v-if="!isPlaying" class="play-btn" type="button" @click="onPlay">
      <span class="play-icon">▶</span>
    </button>
    <button v-if="isPlaying" class="pause-btn" type="button" @click="onPause">
      <span class="pause-icon">||</span>
    </button>

    <div
      class="timeline-area"
      ref="timeline-area"
      @mousemove="onTimelineAreaMouseMove"
      @mousedown="onTimelineAreaMouseDown"
      @mouseup="onTimelineAreaMouseUp"
      @click="onTimelineAreaMouseClick"
    >
      <div class="track">
        <div
          class="segment"
          :style="{ left: segmentStartX + 'px', width: segmentWidth + 'px' }"
        ></div>

        <div class="playhead" :style="{ left: playheadX + 'px' }">
          <div class="playhead-label">{{ secondsToTimeSpanFractionalFormat(playheadTime) }}</div>
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

const props = defineProps({
  duration: Number,
  segmentStartTime: Number,
  segmentDuration: Number,
  playbackTime: Number,
})

const emits = defineEmits(['onSeeked', 'onPlay', 'onPause'])

watch(
  () => props.duration,
  (duration) => {
    if (!timelineAreaRef.value) return
    if (!duration) return
    const rect = timelineAreaRef.value.getBoundingClientRect()
    segmentStartX.value = (props.segmentStartTime! / duration) * rect.width
  },
)

watch(
  () => props.playbackTime,
  (time) => {
    if (!timelineAreaRef.value) return
    if (!time) return
    if (!props.duration) return

    const rect = timelineAreaRef.value.getBoundingClientRect()

    playbackHeadX.value = (time / props.duration) * rect.width
  },
)

onMounted(() => {
  onPlay()
})

const isPlaying: Ref<boolean> = ref(false)

const timelineAreaRef = useTemplateRef<HTMLElement>('timeline-area')

const playheadX: Ref<number> = ref(0)
const playheadTime: Ref<number> = ref(0)

const playbackHeadX: Ref<number> = ref(0)

const segmentWidth = computed(() => {
  if (!timelineAreaRef.value) return
  if (!props.duration) return
  const rect = timelineAreaRef.value.getBoundingClientRect()
  return (props.segmentDuration! / props.duration!) * rect.width
})

const segmentStartX: Ref<number> = ref(0)
const segmentStartTime = computed(() => {
  if (!timelineAreaRef.value) return 0
  const rect = timelineAreaRef.value.getBoundingClientRect()
  return (segmentStartX.value / rect.width) * props.duration!
})

let allowSegmentMove = false

const onTimelineAreaMouseMove = (e: MouseEvent) => {
  movePlayhead(e)
  moveSegmentIfAllowed(e)
  emits('onSeeked', playheadTime.value)
}

const onTimelineAreaMouseDown = () => {
  allowSegmentMove = true
}

const onTimelineAreaMouseUp = () => {
  allowSegmentMove = false
}

const onTimelineAreaMouseClick = (e: MouseEvent) => {
  allowSegmentMove = true
  movePlayhead(e)
  moveSegmentIfAllowed(e)
  allowSegmentMove = false
  emits('onSeeked', playheadTime.value, true)
}

const onPlay = () => {
  emits('onSeeked', segmentStartTime.value, false)
  isPlaying.value = true
  emits('onPlay')
}
const onPause = () => {
  isPlaying.value = false
  emits('onPause')
}

const movePlayhead = (e: MouseEvent) => {
  if (!timelineAreaRef.value) return

  const rect = timelineAreaRef.value.getBoundingClientRect()
  playheadX.value = e.clientX - rect.left

  if (playheadX.value < 0) {
    playheadX.value = 0
  }

  if (playheadX.value > rect.width) {
    playheadX.value = rect.width
  }

  if (allowSegmentMove && playheadX.value + segmentWidth.value! > rect.width) {
    playheadX.value = rect.width - segmentWidth.value!
  } else if (playheadX.value > rect.width) {
    playheadX.value = rect.width
  }

  playheadTime.value = (playheadX.value * props.duration!) / rect.width
}

const moveSegmentIfAllowed = (e: MouseEvent) => {
  if (!allowSegmentMove) {
    return
  }

  if (!timelineAreaRef.value) return

  const rect = timelineAreaRef.value.getBoundingClientRect()
  segmentStartX.value = e.clientX - rect.left

  if (segmentStartX.value < 0) {
    segmentStartX.value = 0
  }

  if (segmentStartX.value + segmentWidth.value! > rect.width) {
    segmentStartX.value = rect.width - segmentWidth.value!
  }
}
</script>

<style scoped>
.timeline-root {
  display: flex;
  align-items: center;
  gap: 12px;
  background: #a97f7f;
  margin-top: 24px;
  margin-bottom: 24px;
}

.play-btn {
  flex: 0 0 auto;
}

.timeline-area {
  flex: 1 1 auto;
  min-width: 0;
  background: #c5b380;
}

.track {
  position: relative;
  height: 60px;
  background: #7fa988;
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
  background: #ff0000;
}

.playback-head {
  position: absolute;
  top: 0;
  bottom: 0;
  transform: translateX(-50%);
  background: #1c0000;
}

.playhead-label {
  position: absolute;
  top: -30px;
  left: 50%;
  transform: translateX(-50%);
  background: #ff0000;
}

.playhead-line {
  position: absolute;
  top: -12px;
  bottom: -12px;
  left: 50%;
  transform: translateX(-50%);
  width: 6px;
  background: #ff0000;
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
