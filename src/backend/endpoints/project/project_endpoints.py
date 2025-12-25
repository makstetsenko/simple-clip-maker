import glob
from pathlib import Path
import uuid
from fastapi import APIRouter, UploadFile
from fastapi.responses import FileResponse

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
        file_name = str(uuid.uuid4()) + Path(media_file.filename).suffix
        write_file_path = Path(project_setup.source_files_dir_path + "/" + file_name)

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
    file_names = [f for f in files if f != "" and f != None]
    return file_names


@router.post("/{project_name}/render")
async def render_project(project_name: str, debug: bool = False):
    project_setup: VideoProjectSetup = VideoProjectSetup.load(project_name)

    timeline_config = TimelineConfig.load(project_setup.timeline_path)
    project = VideoProject(project_setup=project_setup)
    clip_builder = project.get_clip_builder()

    clip_builder.set_debug(debug)

    project_setup.clear_runtime_dirs()
    clip_path = await clip_builder.build_clip(timeline_config)

    output_clip_path = project.save_clip_with_audio(clip_path=clip_path)
    
    return output_clip_path


@router.post("/{project_name}/segment/{segment_id}/render/preview")
async def render_project(project_name: str, segment_id: str, debug: bool = False):
    project_setup: VideoProjectSetup = VideoProjectSetup.load(project_name)

    timeline_config: TimelineConfig = TimelineConfig.load(project_setup.timeline_path)
    project = VideoProject(project_setup=project_setup)
    clip_builder = project.get_clip_builder()

    clip_builder.set_debug(debug)

    project_setup.clear_runtime_dirs()

    single_segment_timeline_config = timeline_config.copy_to_single_segment_timeline(segment_id)
    print(single_segment_timeline_config.to_dict())

    clip_path = await clip_builder.build_clip(single_segment_timeline_config)

    return clip_path
