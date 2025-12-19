<template>
  <Panel v-if="!projectSetupStore.hasSelectedProject">
      Select project to start work
  </Panel>

  <Splitter v-if="projectSetupStore.hasSelectedProject">
    <SplitterPanel :size="15">
      <TimelineConfigurator />
    </SplitterPanel>

    <SplitterPanel :size="65">
      <!-- [Video / Segment editing / Media] placeholder -->

      <Tabs value="0">
        <TabList>
          <Tab value="0"> Segment editing </Tab>
          <Tab value="1"> Media </Tab>
        </TabList>

        <TabPanels>
          <TabPanel value="0">
            <SegmentConfig
              v-for="(s, i) in timelineStore.selectedSegments"
              :key="s.id"
              v-model="timelineStore.selectedSegments[i]"
            />
          </TabPanel>
          <TabPanel value="1">
            <MediaManager />
          </TabPanel>
        </TabPanels>
      </Tabs>
    </SplitterPanel>

    <SplitterPanel :size="20">
      <!-- General config placeholder -->

      <Tabs value="1">
        <TabList>
          <Tab value="0">Segment effects</Tab>
          <Tab value="1">Global effects</Tab>
        </TabList>

        <TabPanels>
          <TabPanel value="0">
            <EffectsSelector
              v-if="timelineStore.selectedSegments.length > 0"
              v-model="timelineStore.selectedSegments[0]!.effects"
            />
          </TabPanel>
          <TabPanel value="1">
            <EffectsSelector
              v-if="timelineStore.timelineExists"
              v-model="timelineStore.timeline!.effects!"
            />
          </TabPanel>
        </TabPanels>
      </Tabs>
    </SplitterPanel>
  </Splitter>
</template>

<script setup lang="ts">
import { useProjectSetupStore } from '@/stores/projectSetup'
import { useTimelineStore } from '@/stores/timeline'
import TimelineConfigurator from './TimelineConfigurator.vue'
import MediaManager from './MediaManager.vue'
import SegmentConfig from '@/components/Timeline/SegmentEditing.vue'
import EffectsSelector from '@/components/Effects/EffectsSelector.vue'

import Splitter from 'primevue/splitter'
import SplitterPanel from 'primevue/splitterpanel'
import Tabs from 'primevue/tabs'
import TabList from 'primevue/tablist'
import Tab from 'primevue/tab'
import TabPanels from 'primevue/tabpanels'
import TabPanel from 'primevue/tabpanel'

import Panel from 'primevue/panel'

const projectSetupStore = useProjectSetupStore()
const timelineStore = useTimelineStore()
</script>
