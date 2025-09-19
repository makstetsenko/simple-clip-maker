from moviepy import *
from src.clip_builder.VideoProject import VideoProject


def build(video_files_path_template: str, audio_file_path_template: str, store_timeline_clips: bool, video_resolution:tuple[int,int]=(1280,720), fps:int=25):
    
    project = VideoProject(
        resolution=video_resolution,
        fps=fps,
        video_files_path_template = video_files_path_template,
        audio_file_path_template=audio_file_path_template
    )
    
    project.split_timeline_into_parts()
    project.build_timeline_clips()
    project.write_video_project_to_file(apply_zoom_bump_effect=False)
    
    if store_timeline_clips:
        project.write_timeline_clips_to_files()

    project.close()
    
    
    