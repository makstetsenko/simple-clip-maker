<template>
  <div>
    <button @click="onNewProjectClick">New project</button>
    <button @click="onLoadProjectsClick">Load projects</button>

    <div>
      <div v-for="p in recentProjects" :key="p.name">
        <button @click="onSelectProject(p)">
          Select {{ p.name }} ({{ p.fps }}fps {{ p.resolution[0] }}x{{ p.resolution[1] }})
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, type Ref } from 'vue'
import apiClient from '@/services/apiClient'
import type { ProjectModel } from '@/shared/models/ProjectModel'
import type { Project } from '@/services/models/Project'
import { mapProjectModel } from '@/shared/mappers/projectModelMapper'

const recentProjects: Ref<ProjectModel[]> = ref([])

function onNewProjectClick() {}

async function onLoadProjectsClick() {
  const url = '/api/projects/search'

  try {
    const resp = await apiClient.get(url)

    const projects: Project[] = resp.data

    recentProjects.value = projects.map((x) => mapProjectModel(x))
  } catch (e) {
    console.log(e)
  }
}

function onSelectProject(project: ProjectModel) {}
</script>
