<template>
  <div>
    <InputField type="number" label="time" v-model="time" />
    <InputField type="number" label="flash-duration" v-model="flashDuration" />
    <InputField type="number" label="color-r" v-model="colorR" />
    <InputField type="number" label="color-g" v-model="colorG" />
    <InputField type="number" label="color-b" v-model="colorB" />
    <InputField type="checkbox" label="Random color" v-model="pickRandomColor" />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch, type Ref } from 'vue'
import InputField from '@/shared/components/InputField.vue'

const props = defineProps({
  args: Object,
})

onMounted(() => {
  time.value = props.args?.time
  flashDuration.value = props.args?.flash_duration
  if (props.args?.color) {
    colorR.value = props.args?.color[0]
    colorG.value = props.args?.color[1]
    colorB.value = props.args?.color[2]
  }
  pickRandomColor.value = props.args?.pick_random_flash_color
})

const time: Ref<number> = ref(0)
const flashDuration: Ref<number> = ref(0)
const colorR: Ref<number> = ref(0)
const colorG: Ref<number> = ref(0)
const colorB: Ref<number> = ref(0)
const pickRandomColor: Ref<boolean> = ref(false)

watch([time, flashDuration, colorR, colorG, colorB, pickRandomColor], () => onChange())

const emits = defineEmits(['onArgsChanged'])

const onChange = () => {
  emits('onArgsChanged', {
    time: time.value,
    flash_duration: flashDuration.value,
    color: [colorR.value, colorG.value, colorB.value],
    pick_random_flash_color: pickRandomColor.value,
  })
}
</script>
