import librosa
import numpy as np
from moviepy import *
import src.peaks_detector as peaks_detector
import random 
import glob
import uuid
import os
import math
import datetime


class VideoClipEnriched:
    def __init__(self, clip: VideoClip, fps: int, path: str | None = None, full_name: str | None = None, dir_path: str | None = None):
        self.clip = clip
        self.duration = clip.duration
        self.aspect_ratio = clip.aspect_ratio
        self.fps = fps
        

        if path != None:
            self.path: str = path
            
            self.full_name: str = path.split("/")[-1]
            self.name: str = self.full_name.split(".")[0]
            self.ext: str = self.full_name.split(".")[1]
            self.dir_path: str = path.rstrip(self.full_name)
            self.duration_frames = int(self.clip.duration * fps)
            
            return
        
        if full_name != None and dir_path != None:
            self.full_name: str = full_name
            self.name: str = self.full_name.split(".")[0]
            self.ext: str = self.full_name.split(".")[1]
            self.dir_path: str = dir_path
            self.path: str = self.dir_path + "/" + self.full_name
            self.duration_frames = int(self.clip.duration * fps)

            return

        raise Exception("Either (path) or (full_name and dir_path) should be defined")
    
        
    def is_aspect_ration_same_as_target(self, target_aspect_ratio: float) -> bool:
        return self.clip.aspect_ratio >= 1 and target_aspect_ratio >= 1 or self.clip.aspect_ratio < 1 and target_aspect_ratio < 1

    
    def is_vertical(self) -> bool:
        return self.clip.aspect_ratio < 1


    def is_horizontal(self) -> bool:
        return self.clip.aspect_ratio >= 1
    
    
    def close_clip(self):
        self.clip.close()

        
    def subclipped(self, start_time : float, end_time : float):
        return VideoClipEnriched(
            clip=self.clip.subclipped(start_time, end_time), 
            full_name=f"{self.name}.{self.ext}", 
            dir_path=self.dir_path)

        
    def write_videofile(self, video_path: str, audio_path: str | None = None):
        self.clip.write_videofile(video_path, audio=audio_path, audio_codec="aac", fps=self.fps)
        



class VideoTimeline:
    
    def __init__(self):
        self.clips: list[VideoClipEnriched] = []
        
        
    def append(self, clip: VideoClipEnriched):
        self.clips.append(clip)


    def append_list(self, clips: list[VideoClipEnriched]):
        for c in clips:
            self.clips.append(c)
    


class VideoProject:
    
    def __init__(self, resolution: tuple[int,int], fps: int, video_files_path_template: str, audio_file_path_template: str):
        video_width, video_height = resolution
        
        self.video_width = video_width
        self.video_height = video_height
        self.fps = fps
        self.aspect_ratio = video_width / video_height
        self.is_horizontal_video = self.aspect_ratio >= 1
        self.is_vertical_video = self.aspect_ratio < 1
        
        self._audio_file_path = glob.glob(audio_file_path_template)[0]
        self._audio_peak_times = self.get_peak_times(self._audio_file_path)
        
        self.clips: list[VideoClipEnriched] = self.get_clips(video_files_path_template)
        
        self.timeline: VideoTimeline = VideoTimeline()
        self.clip_to_save_extend_time = 0.009 # when saving as separate clip add some extra time to avoid cutting vide earlier than expected, Idk why this value, it just works
        
        
    def get_clips(self, path_template: str):
        clips = []
        for template in path_template.split(","):
            for g in glob.glob(template):
                clips.append(VideoClipEnriched(clip=VideoFileClip(g).with_fps(self.fps), path=g))
        return clips
        
        
    def get_peak_times(self, audio_file_path):    
        peaks, sample_rate, _, amplitude_values = peaks_detector.get_peaks_with_sample_rate_with_normalized_energy_with_amplitude_values(audio_file_path)

        # Convert peak indices to times
        peak_times = librosa.frames_to_time(peaks, sr=sample_rate, hop_length=peaks_detector.hop_length)

        duration = librosa.get_duration(y=amplitude_values, sr=sample_rate)
        peak_times = np.append(peak_times, duration)
        
        return peak_times
    
    
    
    
def make_clip(video_files_path_template: str, audio_file_path_template: str, store_sub_clips: bool):
    
    project = VideoProject(
        resolution=(1280, 720),
        fps=24,
        video_files_path_template = video_files_path_template,
        audio_file_path_template=audio_file_path_template
    )
    
    
    