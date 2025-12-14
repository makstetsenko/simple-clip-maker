<script setup lang="ts">
import type { FileUploadStyle } from 'primevue'
import FileUploading from './views/FileUploading.vue'
</script>

<template>
  <h1>Simple clip builder</h1>

  <FileUploading />

  <RouterView />
</template>

<style scoped></style>
