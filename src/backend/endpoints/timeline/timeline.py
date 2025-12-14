from fastapi import APIRouter, HTTPException
import os

from backend.clip_builder.timeline_config import TimelineConfig
from backend.clip_builder.video_project import VideoProject, VideoProjectSetup

router = APIRouter(prefix="/api/{project_name}/timeline", tags=["timeline"])


@router.get("/")
async def get_timeline(project_name: str):
    raise_error_if_project_does_not_exists(project_name)

    project_setup: VideoProjectSetup = VideoProjectSetup.load(project_name)
    if os.path.exists(project_setup.timeline_path):
        timeline: TimelineConfig = TimelineConfig.load(project_setup.timeline_path)
        return timeline.to_dict()

    raise HTTPException(status_code=404, detail=f"Timeline for {project_name} does not exists")

@router.post("/")
async def create_timeline(project_name: str):
    raise_error_if_project_does_not_exists(project_name)

    project_setup: VideoProjectSetup = VideoProjectSetup.load(project_name)
    project = VideoProject(project_setup=project_setup)
    
    timeline = project.analyze_source_and_generate_timeline()
    timeline.save(project_setup.timeline_path)
    return timeline.to_dict()



def raise_error_if_project_does_not_exists(project_name):
    project_path = VideoProjectSetup.get_setup_config_path(project_name)

    if not os.path.exists(project_path):
        raise HTTPException(status_code=404, detail=f"Project {project_name} does not exists")
