<template>
  <div>
    <input type="number" name="line-number" id="line-number" v-model="lineNumber" />
    <input type="number" name="total-lines" id="total-lines" v-model="totalLines" />
    <input type="checkbox" name="is-vertical" id="is-vertical" v-model="isVertical" />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch, type Ref } from 'vue'

const props = defineProps({
  args: Object,
})

onMounted(() => {
  lineNumber.value = props.args?.line_number
  totalLines.value = props.args?.total_lines
  isVertical.value = props.args?.is_vertical
})

const lineNumber: Ref<number> = ref(0)
const totalLines: Ref<number> = ref(0)
const isVertical: Ref<boolean> = ref(false)

watch([lineNumber, totalLines, isVertical], () => onChange())

const emits = defineEmits(['onArgsChanged'])

const onChange = () => {
  emits('onArgsChanged', {
    line_number: lineNumber.value,
    total_lines: totalLines.value,
    is_vertical: isVertical.value,
  })
}
</script>
