<template>
  <div v-if="effectModel">
    - {{ EffectType[effectModel.effectType] }}.{{ EffectMethod[effectModel.method] }}

    <EffectArgsContainer
      :args="effectModel!.args"
      :effect-type="effectModel.effectType"
      :method="effectModel.method"
      :id="effectModel.id"
      @on-args-changed="onArgsChanged"
    />
  </div>
</template>

<script setup lang="ts">
import EffectArgsContainer from './EffectArgs/EffectArgsContainer.vue'
import { EffectMethod, EffectType, type EffectModel } from '@/shared/models/TimelineModel'

const emits = defineEmits(['onEffectChanged'])

const effectModel = defineModel<EffectModel>()

const onArgsChanged = (newArgs: object) => {
  effectModel.value!.args = newArgs
  emits('onEffectChanged', effectModel.value)
}
</script>
