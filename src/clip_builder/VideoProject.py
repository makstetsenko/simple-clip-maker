from dataclasses import dataclass
from typing import Any
from src.clip_builder.VideoNode import VideoNode
from src.clip_builder.VideoResolution import VideoResolution
import src.peaks_detector as peaks_detector
from src.clip_builder.VideoTimeline import VideoTimeline
import src.clip_builder.video_clip_transform as video_clip_transform
from src.clip_builder.effects.zoom_effects import bump_zoom_on_time_stops

from moviepy import VideoClip, VideoFileClip, concatenate_videoclips, vfx, CompositeVideoClip
from src.clip_builder.audio_analyzer import analyze_music_for_editing, AudioAnalyzeResult
from src.clip_builder.video_analyzer import analyze_on_static_scenes, SceneInfo, video_details, VideoFileDetails

import datetime
import glob
import os
import logging
import json
import shutil

logger = logging.getLogger(__name__)



class VideoProject:
    def __init__(
            self, 
            resolution: tuple[int,int], 
            fps: int, 
            video_files_path_template: str, 
            audio_file_path_template: str
        ):
        self.resolution = VideoResolution(resolution)
        self.fps = fps
        self.project_name = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        
        self.project_dir_path = f"./output/projects/{self.project_name}"
        self.temp_dir_path = f"{self.project_dir_path}/temp"
        self.temp_analysis_dir_path = f"{self.temp_dir_path}/analysis"
        
        self.audio_path = glob.glob(audio_file_path_template)[0]
        
        self.videos_path_list = []
        for p in video_files_path_template.split(","):
            self.videos_path_list += glob.glob(p)
            
        self.prepare_dirs()
            
            
    def create_timeline(self) -> VideoTimeline:
        audio_analysis=self.get_audio_analysis()
        video_analysis=self.get_video_analysis()
        
        for n in video_analysis:
            with open(f"{self.temp_analysis_dir_path}/video_{n.name}.json", "w") as f:
                f.write(json.dumps(n.to_json(), indent=4, sort_keys=False))
                
        with open(f"{self.temp_analysis_dir_path}/audio_{self.get_file_name(self.audio_path)}.json", "w") as f:
            f.write(json.dumps(audio_analysis.to_json(), indent=4, sort_keys=False))
    
        
        return VideoTimeline(
            fps=self.fps, 
            resolution=self.resolution, 
            audio_analysis=audio_analysis,
            video_analysis=video_analysis,
            temp_path=self.temp_dir_path)

    def save_clip_with_audio(self, clip_path):
        output_clip_path = f"{self.project_dir_path}/output.mp4"
        
        logger.info(f"Saving clip {output_clip_path}")
        
        clip = VideoFileClip(clip_path)
        clip.write_videofile(output_clip_path, audio=self.audio_path, audio_codec="aac", fps=self.fps)
        clip.close()


    def get_audio_analysis(self) -> AudioAnalyzeResult:
        logger.info(f"Analyzing audio {self.get_file_name(self.audio_path)}")
        return analyze_music_for_editing(self.audio_path, similarity_threshold=0.6)

    
    def get_video_analysis(self) -> list[VideoNode]:
        res: list[VideoNode]= []

        for i, p in enumerate(self.videos_path_list):
            logger.info(f"Analyzing for video {self.get_file_name(p)}")
            
            scenes = analyze_on_static_scenes(p, time_step=0.3, scene_duration_threshold=3)
            details = video_details(p)
            
            res.append(VideoNode(
                path=p,
                fps=details.fps,
                resolution=VideoResolution(details.resolution),
                scenes=[s for s in scenes if s.is_static == False]
            ))


        for i in range(0, len(res)-1):
            res[i].next = res[i+1]

        res[-1].next = res[0]

        return res
    
    
    def get_file_name(self, path: str):
        return path.split("/")[-1]
    
    
    def prepare_dirs(self):
        shutil.rmtree(self.project_dir_path, ignore_errors=True)
        os.makedirs(self.project_dir_path)
        os.makedirs(self.temp_dir_path)
        os.makedirs(self.temp_analysis_dir_path)