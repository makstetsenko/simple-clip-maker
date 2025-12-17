<template>
  <Dialog v-model:visible="model" modal header="New project">
    <template #header>
      <div class="inline-flex items-center justify-center gap-2">New project setup</div>
    </template>

    <Fluid>
      <FloatLabel variant="on">
        <InputText id="project-name" v-model="projectSetup.name" />
        <label for="project-name">Name</label>
      </FloatLabel>

      <FloatLabel variant="on">
        <InputNumber id="project-fps" v-model="projectSetup.fps" showButtons :min="12" />
        <label for="project-fps">FPS</label>
      </FloatLabel>

      <FloatLabel variant="on">
        <label for="project-fps">FPS</label>
      </FloatLabel>

      <InputGroup>
        <FloatLabel variant="on">
          <InputNumber
            v-model="projectSetup.resolution[0]"
            :min="360"
            suffix="px"
            :step="40"
            :show-buttons="true"
          />
          <label for="project-width">Width</label>
        </FloatLabel>
        <InputGroupAddon>
          <Button
            icon="pi pi-arrow-right-arrow-left"
            aria-label="Swap"
            @click="onSwapResolutionClick"
            severity="secondary"
          />
        </InputGroupAddon>
        <FloatLabel variant="on">
          <InputNumber
            v-model="projectSetup.resolution[1]"
            :min="360"
            suffix="px"
            :step="40"
            :show-buttons="true"
          />
          <label for="project-height">Height</label>
        </FloatLabel>
      </InputGroup>
    </Fluid>

    <template #footer>
      <Button label="Cancel" text severity="secondary" @click="model = false" autofocus />
      <Button
        label="Create"
        variant="outlined"
        severity="secondary"
        @click="onCreateClick"
        autofocus
      />
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import FloatLabel from 'primevue/floatlabel'
import InputGroup from 'primevue/inputgroup'
import InputGroupAddon from 'primevue/inputgroupaddon'
import Fluid from 'primevue/fluid'
import 'primeicons/primeicons.css'

import { type ProjectModel } from '@/shared/models/ProjectModel'
import { ref, type Ref } from 'vue'

const props = defineProps({
  onNewProjectCreate: Function,
})
const model = defineModel<boolean>()
const projectSetup: Ref<ProjectModel> = ref({
  name: new Date().toISOString(),
  fps: 30,
  resolution: [1280, 720],
})

function onCreateClick() {
  model.value = false
  if (props.onNewProjectCreate) props.onNewProjectCreate(projectSetup.value)
}

function onSwapResolutionClick() {
  const res = [...projectSetup.value.resolution]
  projectSetup.value.resolution[0] = res[1]!
  projectSetup.value.resolution[1] = res[0]!
}
</script>
