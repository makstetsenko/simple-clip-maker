from src.backend.clip_builder.timeline_config import TimelineConfig
from .video_project import VideoProject


async def build_from_cli(
    input_dir: str,
    video_resolution: tuple[int, int] = (1280, 720),
    fps: int = 25,
    debug: bool = False,
    timeline_config_path: str | None = None,
):
    project = VideoProject(resolution=video_resolution, fps=fps, source_files_dir_path=input_dir)

    clip_builder = project.get_clip_builder()
    clip_builder.set_debug(debug)

    # Use config as separate object to be able to load it from external file
    timeline_config = (
        project.analyze_source_and_generate_timeline()
        if timeline_config_path is None
        else TimelineConfig.load(timeline_config_path)
    )

    timeline_config.save(project.setup.timeline_path)

    clip_path = await clip_builder.build_clip(timeline_config)

    project.save_clip_with_audio(clip_path=clip_path)
