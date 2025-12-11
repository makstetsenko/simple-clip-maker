<template>
  <h3>Segment config</h3>

  <div>index: {{ index }}</div>
  <div>startTime: {{ startTime }}</div>
  <div>duration: {{ duration }}</div>
  <div>endTime: {{ endTime }}</div>

  <div>
    Videos
    <div :key="v.path" v-for="v in videos">{{ v.startTime }} - {{ v.path }}</div>
  </div>

  <div v-if="effects">
    Effects
    <div :key="e.effectType" v-for="e in effects">
      {{ e.effectType }}.{{ e.method }}({{ e.args }})
    </div>
  </div>
</template>

<script setup lang="ts">
interface SegmentConfigProps {
  index: number
  startTime: number
  duration: number
  endTime: number
  videos: SegmentVideoProps[]
  effects: SegmentEffectProps[] | null | undefined
}

interface SegmentEffectProps {
  effectType: string
  method: string
  args: []
}

interface SegmentVideoProps {
  path: string
  startTime: number
}

defineProps<SegmentConfigProps>()
</script>
