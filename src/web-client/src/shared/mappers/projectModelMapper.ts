import type { Project } from '@/services/models/Project'
import type { ProjectModel } from '../models/ProjectModel'

export function mapProjectModel(project: Project): ProjectModel {
  return {
    fps: project.fps,
    name: project.project_name,
    resolution: [...project.resolution],
  } as ProjectModel
}
