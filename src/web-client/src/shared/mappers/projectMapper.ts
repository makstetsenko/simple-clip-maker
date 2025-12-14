import type { Project } from '@/services/models/Project'
import type { ProjectModel } from '../models/ProjectModel'

export function mapProject(project: ProjectModel): Project {
  return {
    fps: project.fps,
    project_name: project.name,
    resolution: [...project.resolution],
  } as Project
}
