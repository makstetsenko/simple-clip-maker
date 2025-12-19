<template>
  <Card v-if="effectModel">
    <template #content>
      <FloatLabel variant="on">
        <Select
          fluid
          v-model="effectModel.effectType"
          :options="getEffectTypesFields()"
          option-label="label"
          option-value="value"
          size="small"
          inputId="effect-type"
        />
        <label for="effect-type">Effect</label>
      </FloatLabel>
      <FloatLabel variant="on">
        <Select
          fluid
          v-model="effectModel.method"
          :options="getEffectMethodFields(effectModel.effectType)"
          option-label="label"
          option-value="value"
          size="small"
          inputId="effect-method"
          @change="onEffectMethodChange"
        />
        <label for="effect-method">Method</label>
      </FloatLabel>

      <EffectArgsProps
        v-if="effectModel.args"
        v-model="effectModel.args"
        :descriptors="getDescriptors(effectModel.effectType, effectModel.method)"
      />
    </template>

    <template #footer>
      <Button
        icon="pi pi-trash"
        @click="onRemoveClick"
        size="small"
        variant="text"
        severity="danger"
      />
      <Button
        icon="pi pi-clone"
        @click="onCopyClick"
        size="small"
        variant="text"
        severity="contrast"
      />
    </template>
  </Card>

  <Divider v-if="effectModel" />
</template>

<script setup lang="ts">
import { watch } from 'vue'
import { getEffectMethodFields, getEffectTypesFields } from './effectFields'
import { type EffectModel } from '@/shared/models/TimelineModel'
import EffectArgsProps from './EffectArgProps.vue'
import { getDescriptors } from './effectArgsDescriptors'
import Card from 'primevue/card'
import Button from 'primevue/button'
import Divider from 'primevue/divider'
import FloatLabel from 'primevue/floatlabel'
import Select from 'primevue/select'
import { getDefaultArgs } from './effectArgsDefaults'

const emits = defineEmits(['onRemove'])

const effectModel = defineModel<EffectModel>()

function onRemoveClick() {
  emits('onRemove', effectModel.value?.id)
}

watch(
  () => effectModel.value!.effectType,
  (val) => {
    const methods = getEffectMethodFields(val)
    if (!methods) return

    effectModel.value!.method = methods[0]!.value
    onEffectMethodChange()
  },
)

function onEffectMethodChange() {
  if (Object.keys(effectModel.value!.args!).length > 0) return
  if (!effectModel.value) return
  if (!effectModel.value.effectType) return
  if (!effectModel.value.method) return

  effectModel.value!.args = getDefaultArgs(effectModel.value!.effectType, effectModel.value!.method)
}

function onCopyClick() {
  
}
</script>
