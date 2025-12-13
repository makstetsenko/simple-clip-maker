<template>
  <div>
    <InputField type="number" label="zoom-factor" v-model="zoomFactor" />
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
})

const zoomFactor: Ref<number> = ref(0)

watch(zoomFactor, () => onChange())

const emits = defineEmits(['onArgsChanged'])

const onChange = () => {
  emits('onArgsChanged', {
    zoom_factor: zoomFactor.value,
  })
}
</script>
