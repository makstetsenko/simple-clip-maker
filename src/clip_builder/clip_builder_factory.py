from src.clip_builder.video_project import VideoProject


async def build(
    video_files_path_template: str,
    audio_file_path_template: str,
    store_timeline_clips: bool,
    video_resolution: tuple[int, int] = (1280, 720),
    fps: int = 25,
    debug: bool = False,
    timeline_config_path: str | None = None,
):
    project = VideoProject(
        resolution=video_resolution,
        fps=fps,
        video_files_path_template=video_files_path_template,
        audio_file_path_template=audio_file_path_template,
    )

    clip_builder = project.get_clip_builder()
    clip_builder.debug = debug

    # Use config as separate object to be able to load it from external file
    timeline_config = (
        project.get_default_timeline_config()
        if timeline_config_path is None
        else project.load_timeline_config(timeline_config_path)
    )

    project.store_timeline_config(timeline_config)

    clip_path = await clip_builder.build_clip(timeline_config)

    project.save_clip_with_audio(clip_path=clip_path)
