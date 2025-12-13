<template>
  <div v-if="effectItems">
    <EffectItem
      v-for="(e, i) in effectItems"
      :key="e.id"
      v-model="effectItems[i]"
      @on-remove="onRemove"
    />
  </div>

  <button @click="onNewClick">New effect</button>
</template>

<script setup lang="ts">
import EffectItem from './EffectItem.vue'
import { EffectMethod, EffectType, type EffectModel } from '@/shared/models/TimelineModel'
import { v4 as uuidv4 } from 'uuid'

const effectItems = defineModel<EffectModel[] | null>()

function onRemove(id: string) {
  const index = effectItems.value!.findIndex((x) => x.id === id)
  effectItems.value?.splice(index, 1)
}

function onNewClick() {
  if (effectItems.value === null || effectItems.value === undefined) {
    effectItems.value = []
  }

  effectItems.value.push({
    id: uuidv4(),
    method: EffectMethod.FIT_VIDEO_INTO_FRAME_SIZE,
    effectType: EffectType.Crop,
    args: {},
  })
}
</script>
