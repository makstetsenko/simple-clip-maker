<template>
  <div>
    <InputField type="number" label="zoom-factor" v-model="zoomFactor" />
    <InputField type="number" label="bump-count" v-model="bumpCount" />
    <InputField type="checkbox" label="reverse" v-model="reverse" />
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
  bumpCount.value = props.args?.bump_count as number
  reverse.value = props.args?.reverse as number
})

const zoomFactor: Ref<number> = ref(0)
const bumpCount: Ref<number> = ref(0)
const reverse: Ref<number> = ref(0)

watch([zoomFactor, bumpCount, reverse], () => onChange())

const emits = defineEmits(['onArgsChanged'])

const onChange = () => {
  emits('onArgsChanged', {
    zoom_factor: zoomFactor.value,
    bump_count: bumpCount.value,
    reverse: reverse.value,
  })
}
</script>
