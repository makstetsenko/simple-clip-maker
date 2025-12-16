<template>
  <div v-if="projectSetupStore.hasSelectedProject">
    <ProjectOverview />

    <MediaManager />

    <TimelineConfigurator />
  </div>
</template>

<script setup lang="ts">
import { useProjectSetupStore } from '@/stores/projectSetup'
import TimelineConfigurator from './TimelineConfigurator.vue'
import ProjectOverview from '@/components/Project/ProjectOverview.vue'
import MediaManager from './MediaManager.vue'

const projectSetupStore = useProjectSetupStore()
</script>
