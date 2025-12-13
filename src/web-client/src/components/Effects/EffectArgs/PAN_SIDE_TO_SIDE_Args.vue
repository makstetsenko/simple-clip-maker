<template>
  <div>
    <input type="number" name="pan-x" id="pan-x" v-model="panX" />
    <input type="number" name="pan-y" id="pan-y" v-model="panY" />
    <input type="text" name="easing" id="easing" v-model="easing" />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch, type Ref } from 'vue'

const props = defineProps({
  args: Object,
})

onMounted(() => {
  panX.value = props.args?.pan[0] as number
  panY.value = props.args?.pan[1] as number
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
