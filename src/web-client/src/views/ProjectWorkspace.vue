<template>
  <div v-if="projectSetupStore.hasSelectedProject"></div>
  <Splitter>
    <SplitterPanel :size="15">
      <TimelineConfigurator />
    </SplitterPanel>

    <SplitterPanel :size="65">
      [Video / Segment editing / Media] placeholder
      <MediaManager />
    </SplitterPanel>

    <SplitterPanel :size="20"> General config placeholder </SplitterPanel>
  </Splitter>
</template>

<script setup lang="ts">
import { useProjectSetupStore } from '@/stores/projectSetup'
import TimelineConfigurator from './TimelineConfigurator.vue'
import MediaManager from './MediaManager.vue'

import Splitter from 'primevue/splitter'
import SplitterPanel from 'primevue/splitterpanel'

const projectSetupStore = useProjectSetupStore()
</script>
