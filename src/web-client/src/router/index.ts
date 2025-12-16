import ProjectWorkspace from '@/views/ProjectWorkspace.vue'
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      component: ProjectWorkspace,
    },
  ],
})

export default router
