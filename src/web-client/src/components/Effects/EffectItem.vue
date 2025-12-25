<template>
  <Card v-if="effectModel">
    <template #content>
      <div class="grid">
        <div class="col-12">
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
        </div>
        <div class="col-12">
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
        </div>
        <div class="col-12">
          <EffectArgsProps
            v-if="effectModel.args"
            v-model="effectModel.args"
            :descriptors="getEffectArgDescriptor(effectModel.effectType, effectModel.method).props"
          />
        </div>
      </div>
    </template>

    <template #footer>
      <div class="grid">
        <div class="col">
          <Button
            icon="pi pi-trash"
            @click="onRemoveClick"
            size="small"
            variant="text"
            severity="danger"
          />
        </div>
        <div class="col">
          <Button
            icon="pi pi-copy"
            @click="onCopyClick"
            size="small"
            variant="text"
            severity="contrast"
          />
        </div>
        <div class="col">
          <Button
            icon="pi pi-clone"
            @click="onDuplicateClick"
            size="small"
            variant="text"
            severity="contrast"
          />
        </div>

        <div class="col">
          <Button
            icon="pi pi-arrow-up"
            @click="onSwapUp"
            size="small"
            variant="text"
            severity="contrast"
          />
        </div>
        <div class="col">
          <Button
            icon="pi pi-arrow-down"
            @click="onSwapDown"
            size="small"
            variant="text"
            severity="contrast"
          />
        </div>
      </div>
    </template>
  </Card>
</template>

<script setup lang="ts">
import { watch } from 'vue'
import { getEffectMethodFields, getEffectTypesFields } from './effectFields'
import { type EffectModel } from '@/shared/models/TimelineModel'
import EffectArgsProps from './EffectArgProps.vue'
import { getEffectArgDescriptor } from './effectArgsDescriptors'
import Card from 'primevue/card'
import Button from 'primevue/button'
import FloatLabel from 'primevue/floatlabel'
import Select from 'primevue/select'
import { useEffectsStore } from '@/stores/effects'

const emits = defineEmits(['onRemove', 'onDuplicate', 'onSwapUp', 'onSwapDown'])

const effectModel = defineModel<EffectModel>()
const effectsStore = useEffectsStore()

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
  if (!effectModel.value) return
  if (!effectModel.value.effectType) return
  if (!effectModel.value.method) return

  effectModel.value!.args = Object.assign(
    {},
    getEffectArgDescriptor(effectModel.value!.effectType, effectModel.value!.method).default,
  )
}

function onCopyClick() {
  if (!effectModel.value) return
  effectsStore.rememberEffect(effectModel.value)
}

function onDuplicateClick() {
  if (!effectModel.value) return
  emits('onDuplicate', effectModel.value)
}

function onSwapUp() {
  if (!effectModel.value) return
  emits('onSwapUp', effectModel.value.id)
}
function onSwapDown() {
  if (!effectModel.value) return
  emits('onSwapDown', effectModel.value.id)
}
</script>
