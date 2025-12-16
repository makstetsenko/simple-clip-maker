<template>
  <div v-if="projectSetupStore.hasSelectedProject">
    <Accordion value="0">
      <AccordionPanel value="0">
        <AccordionHeader>Project configuration setup</AccordionHeader>
        <AccordionContent>
          <Chip :label="projectSetupStore.project?.name" />
          <Chip :label="projectSetupStore.project?.fps + ' fps'" />
          <Chip
            :label="
              projectSetupStore.project?.resolution[0] +
              'px X ' +
              projectSetupStore.project?.resolution[1] +
              'px'
            "
          />
        </AccordionContent>
      </AccordionPanel>
    </Accordion>
  </div>
</template>

<script setup lang="ts">
import { useProjectSetupStore } from '@/stores/projectSetup'
import Accordion from 'primevue/accordion'
import AccordionPanel from 'primevue/accordionpanel'
import AccordionHeader from 'primevue/accordionheader'
import AccordionContent from 'primevue/accordioncontent'
import Chip from 'primevue/chip'

const projectSetupStore = useProjectSetupStore()
</script>
