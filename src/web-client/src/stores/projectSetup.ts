// stores/counter.js
import { defineStore } from 'pinia'
import { type ProjectModel } from '@/shared/models/ProjectModel'

export const useProjectSetupStore = defineStore('project-setup', {
  state: (): { project: ProjectModel | null } => {
    return { project: null }
  },
  actions: {
    setProject(project: ProjectModel) {
      this.project = project
    },
  },
  getters: {
    getProjectName(state) {
      return state.project?.name
    },
    hasSelectedProject(state) {
      return !!state.project
    },
  },
})
