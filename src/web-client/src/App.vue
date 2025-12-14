<script setup lang="ts">
import FileUploading from './views/FileUploading.vue'
import ProjectSelection from './views/ProjectSelection.vue'
</script>

<template>
  <h1>Simple clip builder</h1>

  <ProjectSelection />

  <FileUploading />

  <RouterView />
</template>

<style scoped></style>
