<template>
  <div>
    <InputField type="number" label="total-lines" v-model="totalLines" />
    <InputField type="checkbox" label="is-vertical" v-model="isVertical" />
    <InputField
      type="checkbox"
      label="reverse-ordering"
      v-model="reverseOrdering"
    />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch, type Ref } from 'vue'
import InputField from '@/shared/components/InputField.vue'

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
