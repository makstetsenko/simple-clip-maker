<template>
  <div class="grid" v-if="model && Object.keys(model).length > 0">
    <div class="col-6" v-for="d in descriptors" :key="d.key">
      <!-- Number input -->

      <FloatLabel variant="on" :key="d.key" v-if="d.propType === ArgPropType.Number">
        <InputNumber
          :label="d.label"
          v-model="model[d.key]"
          fluid
          :minFractionDigits="2"
          size="small"
        />
        <label for="on_label">{{ d.label }}</label>
      </FloatLabel>

      <!-- Text input -->

      <FloatLabel variant="on" :key="d.key" v-if="d.propType === ArgPropType.Text">
        <InputText :label="d.label" v-model="model[d.key]" fluid size="small" />
        <label for="on_label">{{ d.label }}</label>
      </FloatLabel>

      <!-- Bool input -->

      <div :key="d.key" v-if="d.propType === ArgPropType.Bool">
        <label :for="'switch-' + d.key">{{ d.label }}</label>
        <ToggleSwitch :inputId="'switch-' + d.key" v-model="model[d.key]" size="small" />
      </div>

      <!-- Color input -->

      <div :key="d.key" v-if="d.propType === ArgPropType.Color">
        <label :for="'color-' + d.key">{{ d.label }}</label>
        <ColorPicker
          :inputId="'color-' + d.key"
          format="rgb"
          :model-value="getRgbColorObj(model[d.key])"
          @change="(e) => setRgbColorObj(e, model[d.key])"
          size="small"
        />
      </div>

      <!-- NumberArray input -->

      <FloatLabel variant="on" :key="d.key" v-if="d.propType === ArgPropType.NumberArray">
        <InputText
          :label="d.label"
          :model-value="numbersToCsv(model[d.key])"
          fluid
          size="small"
          @value-change="(val) => csvToNumbers(val, d.key)"
        />
        <label for="on_label">{{ d.label }}</label>
      </FloatLabel>

      <!-- Tuple input -->

      <FloatLabel variant="on" :key="d.key" v-if="d.propType === ArgPropType.Tuple">
        <InputText
          :label="d.label"
          :model-value="numbersToCsv(model[d.key])"
          fluid
          size="small"
          @value-change="(val) => csvToNumbers(val, d.key)"
        />
        <label for="on_label">{{ d.label }}</label>
      </FloatLabel>
    </div>
  </div>
</template>

<script setup lang="ts">
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import FloatLabel from 'primevue/floatlabel'
import ToggleSwitch from 'primevue/toggleswitch'
import ColorPicker, { type ColorPickerChangeEvent } from 'primevue/colorpicker'

import { ArgPropType, type ArgPropDescriptor } from './effectArgsDescriptors'

interface Props {
  descriptors: ArgPropDescriptor[]
}

defineProps<Props>()

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const model = defineModel<any>({})

function getRgbColorObj(value: number[]) {
  return {
    r: value[0],
    g: value[1],
    b: value[2],
  }
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function setRgbColorObj(e: ColorPickerChangeEvent, item: any) {
  item[0] = e.value.r
  item[1] = e.value.g
  item[2] = e.value.b
}

function numbersToCsv(numbers: number[]) {
  return numbers.join(',')
}

function csvToNumbers(csv: string | null | undefined, modelKey: string) {
  if (!csv) {
    model.value[modelKey] = []
    return
  }

  model.value[modelKey] = csv.split(',').map((x) => Number(x.trim()))
}
</script>
