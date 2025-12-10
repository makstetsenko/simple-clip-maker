<template>
  <div class="segment">
    <div class="segment-label">
      <div class="segment-number">{{ index }}</div>
      <div class="segment-time">{{ time }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps({
  index: Number,
  time: Number,
})
</script>

<style scoped>
.segment {
  height: 180px;
  border: 6px solid #6a64d8;
  background: #e6e6e6;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.segment-label {
  text-align: center;
  color: #6a64d8;
  font-weight: 700;
  font-size: 20px;
}

.segment-number {
  font-size: 26px;
}

.segment-time {
  margin-top: 4px;
  font-size: 20px;
}
</style>
