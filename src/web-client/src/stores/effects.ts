import { defineStore } from 'pinia'

interface Timeline

export const useProjectSetupStore = defineStore('project-setup', {
  state: (): => {
    return { project: null, debugMode: false }
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
