<template>
  <div v-if="effectItems">
    <EffectItem
      v-for="(e, i) in effectItems"
      :key="e.id"
      v-model="effectItems[i]"
      @on-remove="onRemove"
      @on-duplicate="onDuplicate"
      @on-swap-up="onSwapUp"
      @on-swap-down="onSwapDown"
    />
  </div>

  <Button @click="onNewClick" variant="outlined">New</Button>
  <Button @click="onPasteClick" variant="outlined" v-if="!!effectsStore.rememberedEffect"
    >Paste</Button
  >
</template>

<script setup lang="ts">
import EffectItem from './EffectItem.vue'
import { EffectMethod, EffectType, type EffectModel } from '@/shared/models/TimelineModel'
import { v4 as uuidv4 } from 'uuid'
import Button from 'primevue/button'
import { useEffectsStore } from '@/stores/effects'
import { getEffectArgDescriptor } from './effectArgsDescriptors'

const effectItems = defineModel<EffectModel[] | null>()
const effectsStore = useEffectsStore()

function onRemove(id: string) {
  const index = effectItems.value!.findIndex((x) => x.id === id)
  effectItems.value?.splice(index, 1)
}

function onNewClick() {
  if (effectItems.value === null || effectItems.value === undefined) {
    effectItems.value = []
  }

  const effectType = EffectType.Crop
  const method = EffectMethod.FIT_VIDEO_INTO_FRAME_SIZE

  effectItems.value.push({
    id: uuidv4(),
    effectType: effectType,
    method: method,
    args: getEffectArgDescriptor(effectType, method).default,
  })
}

function onDuplicate(e: EffectModel) {
  effectsStore.rememberEffect(e)
  effectItems.value?.push(effectsStore.pasteAsNewEffect()!)
}

function onPasteClick() {
  if (!effectsStore.rememberedEffect) return
  effectItems.value?.push(effectsStore.pasteAsNewEffect()!)
}

function onSwapUp(effectId: string) {
  if (!effectItems.value) return
  const index = effectItems.value.findIndex((x) => x.id === effectId)

  if (index == 0) return

  const effect = effectItems.value.splice(index, 1)[0]!
  effectItems.value.splice(index - 1, 0, effect)
}
function onSwapDown(effectId: string) {
  if (!effectItems.value) return
  const index = effectItems.value.findIndex((x) => x.id === effectId)

  if (index == effectItems.value.length - 1) return

  const effect = effectItems.value.splice(index, 1)[0]!
  effectItems.value.splice(index + 1, 0, effect)
}
</script>
