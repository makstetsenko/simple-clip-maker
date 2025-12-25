<template>
  <div class="grid">
    <div class="col-2">
      <span>Select time on music to select appropriate segment</span>
    </div>
    <div class="col-10">
      <ClipPreviewPlayer
        v-if="audioFilePath"
        :video-path="audioFilePath"
        :width="800"
        :height="60"
        :volume-panel="true"
        :muted="true"
        :play-toggle="true"
        :autoplay="false"
        @on-seeked="onSeeked"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useTimelineStore } from '@/stores/timeline'
import { computed } from 'vue'
import ClipPreviewPlayer from '@/components/Video/ClipPreviewPlayer.vue'
import { useMediaStore } from '@/stores/mediaStore'

const timelineStore = useTimelineStore()
const mediaStore = useMediaStore()

const audioFilePath = computed(() => {
  if (!mediaStore.getAudioPathList) return null
  if (mediaStore.getAudioPathList.length == 0) return null

  return mediaStore.getAudioPathList[0]
})

function onSeeked(time: number) {
  if (!timelineStore.timeline) return

  const index = timelineStore.timeline.segments.findIndex(
    (x) => x.startTime <= time && x.endTime > time,
  )

  if (index < 0) return
  timelineStore.clearSelectedSegments()
  timelineStore.appendSelectSegmentByIndex(index)
}
</script>
