<template>
  <div>
    <Menubar :model="projectMenuItems">
      <template #start>
        <div>Simple clip builder</div>
        <Chip v-if="projectSetupStore.hasSelectedProject">
          <strong>Project:</strong>
          {{ projectSetupStore.project?.name }} | {{ projectSetupStore.project?.resolution[0] }}x{{
            projectSetupStore.project?.resolution[1]
          }}
          | {{ projectSetupStore.project?.fps }}fps
        </Chip>
      </template>
      <template #end>
        <Button
          severity="success"
          @click="upsertTimeline"
          v-if="timelineStore.timelineExists"
          variant="outlined"
          >Save</Button
        >
        <Button
          severity="help"
          @click="renderProject"
          :loading="renderingInProgress"
          variant="outlined"
          v-if="projectSetupStore.hasSelectedProject"
        >
          Render
        </Button>
        <ToggleButton
          v-model="projectSetupStore.debugMode"
          onLabel="DEBUG ON"
          offLabel="debug off"
          size="small"
        />
      </template>
    </Menubar>

    <NewProjectModal v-model="newProjectModalVisible" @new-project-create="onNewProjectCreate" />
  </div>
</template>

<script setup lang="ts">
import NewProjectModal from '@/components/Project/NewProjectModal.vue'
import apiClient from '@/services/apiClient'
import type { Project } from '@/services/models/Project'
import { mapProjectModel } from '@/shared/mappers/projectModelMapper'
import type { ProjectModel } from '@/shared/models/ProjectModel'
import { useProjectSetupStore } from '@/stores/projectSetup'
import Menubar from 'primevue/menubar'
import type { MenuItem } from 'primevue/menuitem'
import { onMounted, ref, type Ref } from 'vue'
import Chip from 'primevue/chip'
import Button from 'primevue/button'
import { useTimelineStore } from '@/stores/timeline'
import { mapTimeline } from '@/shared/mappers/timelineMapper'
import ToggleButton from 'primevue/togglebutton'

const newProjectModalVisible: Ref<boolean> = ref(false)
const renderingInProgress: Ref<boolean> = ref(false)

const projectSetupStore = useProjectSetupStore()
const timelineStore = useTimelineStore()

const projectMenuItems: Ref<MenuItem[]> = ref([
  {
    label: 'New',
    command: () => (newProjectModalVisible.value = true),
  },
  {
    label: 'Open',
    items: [
      {
        label: 'Recent projects',
      },
    ],
  },
])

onMounted(() => {
  loadProjects()
})

async function loadProjects() {
  const url = '/api/projects/search'

  try {
    const resp = await apiClient.get(url)

    const projects: Project[] = resp.data
    const models = projects.map((x) => mapProjectModel(x))

    projectMenuItems.value[1]!.items![0]!.items = models.map((x) => ({
      label: `${x.name} (${x.fps}fps ${x.resolution[0]}x${x.resolution[1]})`,
      command: () => onProjectSelectClick(x),
    }))
  } catch (e) {
    console.error(e)
  }
}

async function onNewProjectCreate(project: ProjectModel) {
  const url = '/api/projects'
  await apiClient.post(url, {
    width: project.resolution[0],
    height: project.resolution[1],
    fps: project.fps,
    project_name: project.name,
  })
  await loadProjects()
  onProjectSelectClick(project)
  timelineStore.clearSelectedSegments()
}

function onProjectSelectClick(project: ProjectModel) {
  projectSetupStore.setProject(project)
  timelineStore.clearSelectedSegments()
}

async function renderProject() {
  if (!projectSetupStore.hasSelectedProject) return

  renderingInProgress.value = true
  try {
    await upsertTimeline()
    await apiClient.post(
      `/api/projects/${projectSetupStore.getProjectName}/render?debug=${projectSetupStore.debugMode}`,
    )
  } finally {
    renderingInProgress.value = false
  }
}

async function upsertTimeline() {
  if (!timelineStore.timelineExists) return
  const timelineObj = mapTimeline(timelineStore.timeline!)

  const url = `/api/${projectSetupStore.getProjectName}/timeline/upsert`
  await apiClient.post(url, timelineObj)
}
</script>
