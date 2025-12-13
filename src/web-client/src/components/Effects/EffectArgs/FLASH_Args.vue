<template>
  <div>
    <input type="number" name="time" id="time" v-model="time" />
    <input type="number" name="flash-duration" id="flash-duration" v-model="flashDuration" />
    <input type="number" name="color-r" id="color-r" v-model="colorR" />
    <input type="number" name="color-g" id="color-g" v-model="colorG" />
    <input type="number" name="color-b" id="color-b" v-model="colorB" />
    <input
      type="checkbox"
      name="pick-random-color"
      id="pick-random-color"
      v-model="pickRandomColor"
    />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch, type Ref } from 'vue'

const props = defineProps({
  args: Object,
})

onMounted(() => {
  time.value = props.args?.time
  flashDuration.value = props.args?.flash_duration
  colorR.value = props.args?.color[0]
  colorG.value = props.args?.color[1]
  colorB.value = props.args?.color[2]
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
