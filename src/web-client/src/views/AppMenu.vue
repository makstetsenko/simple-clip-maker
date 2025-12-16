<template>
  <div>
    <Menubar :model="menuItems" />
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

const recentProjects: Ref<ProjectModel[]> = ref([])
const newProjectModalVisible: Ref<boolean> = ref(false)

const projectSetupStore = useProjectSetupStore()

const menuItems: Ref<MenuItem[]> = ref([
  {
    label: 'New Project',
    command: () => (newProjectModalVisible.value = true),
  },
  {
    label: 'Open recent',
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

    recentProjects.value = models
    menuItems.value[1]!.visible = models.length > 0
    menuItems.value[1]!.items = models.map((x) => ({
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
</script>
