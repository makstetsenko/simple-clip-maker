from moviepy import *
from src.clip_builder.VideoProject import VideoProject


def build(
    video_files_path_template: str,
    audio_file_path_template: str,
    store_timeline_clips: bool,
    video_resolution: tuple[int, int] = (1280, 720),
    fps: int = 25,
    preview: bool = False,
):

    project = VideoProject(
        resolution=video_resolution,
        fps=fps,
        video_files_path_template=video_files_path_template,
        audio_file_path_template=audio_file_path_template,
        preview=preview,
    )

    timeline = project.create_timeline()
    clip_path = timeline.build_timeline_clip()
    project.save_clip_with_audio(clip_path=clip_path)
