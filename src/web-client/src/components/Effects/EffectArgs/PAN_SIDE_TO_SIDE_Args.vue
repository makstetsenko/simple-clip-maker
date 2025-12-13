<template>
  <div>
    <InputField type="number" label="pan-x" v-model="panX" />
    <InputField type="number" label="pan-y" v-model="panY" />
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
  if (props.args?.pan) {
    panX.value = props.args?.pan[0] as number
    panY.value = props.args?.pan[1] as number
  }
  easing.value = props.args?.reverse as string
})

const panX: Ref<number> = ref(0)
const panY: Ref<number> = ref(0)
const easing: Ref<string> = ref('')

watch([panX, panY, easing], () => onChange())

const emits = defineEmits(['onArgsChanged'])

const onChange = () => {
  emits('onArgsChanged', {
    pan: [panX.value, panY.value],
    easing: easing.value,
  })
}
</script>
