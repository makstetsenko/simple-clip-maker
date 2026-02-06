<template>
  <Panel v-if="!projectSetupStore.hasSelectedProject"> Select project to start work </Panel>

  <Splitter v-if="projectSetupStore.hasSelectedProject">
    <SplitterPanel :size="15">
      <TimelineConfigurator />
    </SplitterPanel>

    <SplitterPanel :size="65">
      <Splitter layout="vertical">
        <SplitterPanel :size="100">
          <!-- [Video / Segment editing / Media] placeholder -->

          <Tabs value="0">
            <TabList>
              <Tab value="0"> Segment editing </Tab>
              <Tab value="1"> Media </Tab>
              <Tab value="2"> Render </Tab>
            </TabList>

            <TabPanels>
              <TabPanel value="0">
                <SegmentConfig
                  v-if="timelineStore.selectedSegments.length > 0"
                  v-model="timelineStore.selectedSegments[0]"
                />
              </TabPanel>
              <TabPanel value="1">
                <MediaManager />
              </TabPanel>

              <TabPanel value="2"> <RenderManager /></TabPanel>
            </TabPanels>
          </Tabs>
        </SplitterPanel>
      </Splitter>
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
              @on-effect-change="onSegmentEffectChange"
            />
          </TabPanel>
          <TabPanel value="1">
            <EffectsSelector
              v-if="timelineStore.timelineExists"
              v-model="timelineStore.timeline!.effects!"
              @on-effect-change="onGlobalEffectsChange"
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
import RenderManager from './RenderManager.vue'
import { v4 as uuidv4 } from 'uuid'

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

function onGlobalEffectsChange() {
  if (!timelineStore.timeline) return

  timelineStore.timeline.segments.forEach((s) => {
    s.etag = uuidv4()
  })
}

function onSegmentEffectChange() {
  if (timelineStore.selectedSegments.length == 0) return
  timelineStore.selectedSegments[0]!.etag = uuidv4()
}
</script>
