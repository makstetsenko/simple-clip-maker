<template>
  <div>
    <EffectItem v-for="(e, i) in effectItems" :key="e.id" v-model="effectItems![i]!" />
  </div>
</template>

<script setup lang="ts">
import EffectItem from './EffectItem.vue'
import type { EffectModel } from '@/shared/models/TimelineModel'

const effectItems = defineModel<EffectModel[]>()
</script>
