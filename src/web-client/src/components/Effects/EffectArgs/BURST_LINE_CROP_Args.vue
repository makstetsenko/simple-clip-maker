<template>
  <div>
    <input type="number" name="total-lines" id="total-lines" v-model="totalLines" />
    <input type="checkbox" name="is-vertical" id="is-vertical" v-model="isVertical" />
    <input
      type="checkbox"
      name="reverse-ordering"
      id="reverse-ordering"
      v-model="reverseOrdering"
    />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch, type Ref } from 'vue'

const props = defineProps({
  args: Object,
})

onMounted(() => {
  reverseOrdering.value = props.args?.reverse_ordering
  totalLines.value = props.args?.total_lines
  isVertical.value = props.args?.is_vertical
})

const reverseOrdering: Ref<number> = ref(0)
const totalLines: Ref<number> = ref(0)
const isVertical: Ref<boolean> = ref(false)

watch([reverseOrdering, totalLines, isVertical], () => onChange())

const emits = defineEmits(['onArgsChanged'])

const onChange = () => {
  emits('onArgsChanged', {
    reverse_ordering: reverseOrdering.value,
    total_lines: totalLines.value,
    is_vertical: isVertical.value,
  })
}
</script>
