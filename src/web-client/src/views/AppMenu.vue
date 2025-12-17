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
          severity="help"
          @click="renderProject"
          :loading="renderingInProgress"
          variant="outlined"
          v-if="projectSetupStore.hasSelectedProject"
        >
          Render
        </Button>
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

const newProjectModalVisible: Ref<boolean> = ref(false)
const renderingInProgress: Ref<boolean> = ref(false)

const projectSetupStore = useProjectSetupStore()

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
}

function onProjectSelectClick(project: ProjectModel) {
  projectSetupStore.setProject(project)
}

async function renderProject() {
  if (!projectSetupStore.hasSelectedProject) return

  renderingInProgress.value = true
  try {
    await apiClient.post(`/api/projects/${projectSetupStore.getProjectName}/render`)
  } finally {
    renderingInProgress.value = false
  }
}
</script>
