<template>
  <div>
    <input type="number" name="zoom-factor" id="zoom-factor" v-model="zoomFactor" />
    <input type="number" name="bump-count" id="bump-count" v-model="bumpCount" />
    <input type="checkbox" name="reverse" id="reverse" v-model="reverse" />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch, type Ref } from 'vue'

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
