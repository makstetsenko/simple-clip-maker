<template>
  <div>
    <div>{{ label }}</div>
    <div><input :type="type" v-model="value" /></div>
  </div>
</template>

<script setup lang="ts">
defineProps({
  label: String,
  type: String,
})
const value = defineModel()
</script>
