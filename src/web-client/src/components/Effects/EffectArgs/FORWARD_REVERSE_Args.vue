<template>
  <div>
    <input type="number" name="start-speed" id="start-speed" v-model="startSpeed" />
    <input type="checkbox" name="fast-slow-mode" id="fast-slow-mode" v-model="fastSlowMode" />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch, type Ref } from 'vue'

const props = defineProps({
  args: Object,
})

onMounted(() => {
  startSpeed.value = props.args?.start_speed
  fastSlowMode.value = props.args?.fast_slow_mode
})

const startSpeed: Ref<number> = ref(0)
const fastSlowMode: Ref<boolean> = ref(false)

watch([startSpeed, fastSlowMode], () => onChange())

const emits = defineEmits(['onArgsChanged'])

const onChange = () => {
  emits('onArgsChanged', {
    start_speed: startSpeed.value,
    fast_slow_mode: fastSlowMode.value,
  })
}
</script>
