import glob
from pathlib import Path
from fastapi import APIRouter, UploadFile

from backend.clip_builder.timeline_config import TimelineConfig
from backend.clip_builder.video_project import VideoProject, VideoProjectSetup, get_path_list
from backend.endpoints.project.models import NewProjectRequest

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.post("/")
async def new_project(request: NewProjectRequest):
    setup = VideoProjectSetup(
        resolution=(request.width, request.height),
        fps=request.fps,
        project_name=request.project_name,
        source_files_dir_path=None,
    )

    setup.setup_dirs()
    setup.save()


@router.get("/search")
async def search(name: str | None = None):
    search_path = VideoProjectSetup.setup_dir_path
    files = get_path_list(search_path, ["yaml", "yml"])

    def get_file_name(path: str) -> str:
        return path.split("/")[-1].split(".")[0]

    project_names = [get_file_name(f) for f in files]

    if name is not None:
        project_names = [p for p in project_names if name in p]

    return [VideoProjectSetup.load(n).to_dict() for n in project_names]


@router.post("/{project_name}/media")
async def import_media(project_name: str, files: list[UploadFile]):
    project_setup: VideoProjectSetup = VideoProjectSetup.load(project_name)

    for media_file in files:
        write_file_path = Path(project_setup.source_files_dir_path + "/" + media_file.filename)

        written = 0
        try:
            with write_file_path.open("wb") as out:
                while True:
                    chunk = await media_file.read(1024 * 1024)  # 1MB
                    if not chunk:
                        break
                    written += len(chunk)

                    out.write(chunk)
        finally:
            await media_file.close()


@router.get("/{project_name}/media")
async def get_project_media_info(project_name: str):
    project_setup: VideoProjectSetup = VideoProjectSetup.load(project_name)
    files = project_setup.videos_path_list + [project_setup.audio_path]
    file_names = [Path(f).name for f in files]
    return file_names

@router.post("/{project_name}/render")
async def render_project(project_name: str):
    project_setup: VideoProjectSetup = VideoProjectSetup.load(project_name)
    
    timeline_config = TimelineConfig.load(project_setup.timeline_path)
    project = VideoProject(project_setup=project_setup)
    clip_builder = project.get_clip_builder()
    
    clip_builder.set_debug(True)
    
    clip_path = await clip_builder.build_clip(timeline_config)

    project.save_clip_with_audio(clip_path=clip_path)