<template>
  <div>
    <InputField
      v-for="s in speedWithIndexes"
      :key="s.index"
      type="number"
      :label="'speed-' + s.index.toString()"
      v-model="s.value"
    />
    <InputField
      type="checkbox"
      label="scale_speed_to_original_duration"
      v-model="scaleSpeedToOriginalDuration"
    />
    <InputField type="number" label="ramps_count_between_speed" v-model="rampsCountBetweenSpeed" />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch, type Ref } from 'vue'
import InputField from '@/shared/components/InputField.vue'

const props = defineProps({
  args: Object,
})

onMounted(() => {
  speeds.value = props.args?.speeds as number[]
  scaleSpeedToOriginalDuration.value = props.args?.scale_speed_to_original_duration as boolean
  rampsCountBetweenSpeed.value = props.args?.ramps_count_between_speed as number
})

const speeds: Ref<number[]> = ref([])
const scaleSpeedToOriginalDuration: Ref<boolean> = ref(true)
const rampsCountBetweenSpeed: Ref<number> = ref(5)

watch([speeds, scaleSpeedToOriginalDuration, rampsCountBetweenSpeed], () => onChange())

const emits = defineEmits(['onArgsChanged'])

const onChange = () => {
  emits('onArgsChanged', {
    speeds: speeds.value,
    scale_speed_to_original_duration: scaleSpeedToOriginalDuration.value,
    ramps_count_between_speed: rampsCountBetweenSpeed.value,
  })
}

const speedWithIndexes = computed(() => {
  const items: { index: number; value: number }[] = []

  speeds.value.forEach((value, index) => {
    items.push({ index, value })
  })

  return items
})
</script>
