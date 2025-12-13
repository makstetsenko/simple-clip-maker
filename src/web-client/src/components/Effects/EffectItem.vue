<template>
  <div v-if="effectModel">
    <select v-model="effectModel.effectType">
      <option v-for="e in getEffectTypesFields()" :key="e.value" :value="e.value">
        {{ e.label }}
      </option>
    </select>

    <select v-model="effectModel.method">
      <option
        v-for="e in getEffectMethodFields(effectModel.effectType)"
        :key="e.value"
        :value="e.value"
      >
        {{ e.label }}
      </option>
    </select>

    <EffectArgsContainer
      :args="effectModel!.args"
      :effect-type="effectModel.effectType"
      :method="effectModel.method"
      :id="effectModel.id"
      @on-args-changed="onArgsChanged"
    />

    <button @click="onRemoveClick">Remove</button>
    <hr />
  </div>
</template>

<script setup lang="ts">
import { watch } from 'vue'
import { getEffectMethodFields, getEffectTypesFields } from './effectFields'
import EffectArgsContainer from './EffectArgs/EffectArgsContainer.vue'
import { type EffectModel } from '@/shared/models/TimelineModel'

const emits = defineEmits(['onRemove'])

const effectModel = defineModel<EffectModel>()

function onArgsChanged(newArgs: object) {
  effectModel.value!.args = newArgs
}

function onRemoveClick() {
  emits('onRemove', effectModel.value?.id)
}

watch(
  () => effectModel.value!.effectType,
  (val) => {
    const methods = getEffectMethodFields(val)
    if (!methods) return

    effectModel.value!.method = getEffectMethodFields(val)[0]!.value
  },
)
</script>
