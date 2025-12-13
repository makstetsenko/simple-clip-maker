<template>
  <div>
    <InputField type="number" label="zoom-factor" v-model="zoomFactor" />
    <InputField type="number" label="zoom-duration" v-model="zoomDuration" />
    <InputField type="text" label="easing" v-model="easing" />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch, type Ref } from 'vue'
import InputField from '@/shared/components/InputField.vue'

const props = defineProps({
  args: Object,
})

onMounted(() => {
  zoomFactor.value = props.args?.zoom_factor as number
  zoomDuration.value = props.args?.zoom_duration as number
  easing.value = props.args?.easing as string
})

const zoomFactor: Ref<number> = ref(0)
const zoomDuration: Ref<number> = ref(0)
const easing: Ref<string> = ref('')

watch([zoomFactor, zoomDuration, easing], () => onChange())

const emits = defineEmits(['onArgsChanged'])

const onChange = () => {
  emits('onArgsChanged', {
    zoom_factor: zoomFactor.value,
    zoom_duration: zoomDuration.value,
    easing: easing.value,
  })
}
</script>
