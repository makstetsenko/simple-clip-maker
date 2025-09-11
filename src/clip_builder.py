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
from enum import Enum
import src.video_clip_transform as video_clip_transform


class VideoPosition(Enum):
    CROP = 1
    SPLIT_SCREEN = 2
    

class VideoTimelinePart:
    def __init__(self, video_resolution: tuple[int,int], time_stops: list[float], repeat_clips: bool):
        self.timeline_clips: list[VideoClip] = []
        self.timeline_clips_to_write_to_file: list[VideoClip] = []
        self.full_length_concataneted_clips: list[VideoClip] = []
        self.time_stops = time_stops
        self.video_position = VideoPosition.CROP
        self.video_resolution = video_resolution
        self.concataneted_clip_start_time = 0
        self.repeat_clips = repeat_clips
        self.clip_to_save_extend_time = 0.009 # when saving as separate clip add some extra time to avoid cutting vide earlier than expected, Idk why this value, it just works
        

    def with_video_position(self, video_position: VideoPosition):
        self.video_position = video_position
    
    
    def find_clip_with_min_duration(self, min_duration: float,  clips: list[VideoClip]):
        filtered = [c for c in clips if c.duration > min_duration]
        
        if len(filtered) == 0:
            return None
        
        return random.choice(filtered)
        
    
    def build_clip_bewteen_time_stops(self, start_time: float, end_time: float, clips: list[VideoClip]):
        duration = end_time - start_time
            
        selected_clips: list[VideoClip] = []
        selected_clips_duration = 0
        
        can_repeat_clips = self.repeat_clips and len(self.full_length_concataneted_clips) > 0
        
        while selected_clips_duration <= duration:
            clip = self.full_length_concataneted_clips[-1] \
                if can_repeat_clips \
                else self.find_clip_with_min_duration(duration, clips)
                
            if clip == None:
                clip = random.choice(clips)
            
            selected_clips.append(clip)
            selected_clips_duration += clip.duration

        self.concataneted_clip_start_time = self.concataneted_clip_start_time if can_repeat_clips else random.randint(0, math.floor((selected_clips_duration - duration) * 100)) / 100.0

        concatenated_clip: VideoClip = concatenate_videoclips(clips=selected_clips)
        self.full_length_concataneted_clips.append(concatenated_clip)

        
        subclipped = concatenated_clip.subclipped(
            start_time=self.concataneted_clip_start_time,
            end_time=self.concataneted_clip_start_time + duration
        )
        timeline_clip = video_clip_transform.crop_video(self.video_resolution[0], self.video_resolution[1], subclipped)
        self.timeline_clips.append(timeline_clip)
            
        
        subclipped_to_store = concatenated_clip.subclipped(
            start_time=self.concataneted_clip_start_time,
            end_time=self.concataneted_clip_start_time + duration + self.clip_to_save_extend_time
        )
        timeline_clip_to_store = video_clip_transform.crop_video(self.video_resolution[0], self.video_resolution[1], subclipped_to_store)
        self.timeline_clips_to_write_to_file.append(timeline_clip_to_store)
        



    def build_timeline_clips(self, clips: list[VideoClip]):
        if len(self.time_stops) == 0:
            raise Exception("time_stops is empty. Cannot select clips for empty time stops")        
        
        for i in range(1, len(self.time_stops)):
            self.build_clip_bewteen_time_stops(
                start_time=self.time_stops[i-1],
                end_time=self.time_stops[i],
                clips=clips
            )
        
    
    def close(self):
        for c in self.timeline_clips + self.full_length_concataneted_clips + self.timeline_clips_to_write_to_file:
            c.close()


class VideoTimeline:
    
    def __init__(self, time_stops: list[float], video_resolution: tuple[int,int]):
        self.parts: list[VideoTimelinePart] = []
        self.time_stops = time_stops
        self.video_resolution = video_resolution
        
    
    def split_timeline_into_parts(self):
        part_time_stops_total_counts = [2,3,4,5]
        
        part_time_stops = []
        part_time_stops_count = random.choice(part_time_stops_total_counts)
        
        for index, time_stop in enumerate(self.time_stops):
            part_time_stops.append(time_stop)
            
            if len(part_time_stops) == part_time_stops_count or index == len(self.time_stops) - 1:
                
                self.parts.append(
                    VideoTimelinePart(
                        video_resolution=self.video_resolution,
                        time_stops=[x for x in part_time_stops],
                        repeat_clips=True if random.random() < 0.3 else False))
                
                part_time_stops = [time_stop]
                part_time_stops_count = random.choice(part_time_stops_total_counts)        
            
                

    def get_timeline_clips(self):
        clips = []
        
        for p in self.parts:
            for c in p.timeline_clips:
                clips.append(c)

        return clips
                
    
    def get_timeline_clips_to_store(self) -> list[VideoClip]:    
        clips = []
        
        for p in self.parts:
            for c in p.timeline_clips_to_write_to_file:
                clips.append(c)

        return clips
                
                
    def close(self):
        for p in self.parts:
            p.close()
                


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
        
        self.project_name = self._audio_file_path.split("/")[-1].split(".")[0]
        self.save_dir_path = f"output/{self.project_name}-{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
        os.makedirs(self.save_dir_path, exist_ok=True)

        
        self.clips: list[VideoClip] = self.load_clips(video_files_path_template)
        self.timeline: VideoTimeline = VideoTimeline(time_stops=[0] + [float(c) for c in list(self._audio_peak_times)], video_resolution=resolution)
        
        
    def load_clips(self, path_template: str):
        clips = []
        for template in path_template.split(","):
            for g in glob.glob(template):
                clips.append(VideoFileClip(g))
        return clips
        
        
    def get_peak_times(self, audio_file_path):    
        peaks, sample_rate, _, amplitude_values = peaks_detector.get_peaks_with_sample_rate_with_normalized_energy_with_amplitude_values(audio_file_path)

        # Convert peak indices to times
        peak_times = librosa.frames_to_time(peaks, sr=sample_rate, hop_length=peaks_detector.hop_length)

        duration = librosa.get_duration(y=amplitude_values, sr=sample_rate)
        peak_times = np.append(peak_times, duration)
        
        return peak_times
    
    
    def build_timeline_clips(self):
        for p in self.timeline.parts:
            p.build_timeline_clips(clips=self.clips)
            
    def split_timeline_into_parts(self):
        self.timeline.split_timeline_into_parts()
        
        
    def get_timeline_clips(self) -> list[VideoClip]:
        return self.timeline.get_timeline_clips()
    
    
        
    def get_timeline_clips_to_store(self) -> list[VideoClip]:
        return self.timeline.get_timeline_clips_to_store()
    
    
    def write_video_project_to_file(self):
        clip = concatenate_videoclips(self.get_timeline_clips())
        clip.write_videofile(f"{self.save_dir_path}/{self.project_name}.mp4", audio=self._audio_file_path, audio_codec="aac", fps=self.fps)
        
        
    def write_timeline_clips_to_files(self):
        dir_path = f"{self.save_dir_path}/timeline_clips"
        os.makedirs(dir_path, exist_ok=True)
        
        for index, c in enumerate(self.get_timeline_clips_to_store()):
            c.write_videofile(f"{dir_path}/clip_{index}.mp4", audio_codec="aac", logger=None, fps=self.fps)

    
    def close(self):
        self.timeline.close()
    
    

    
def build(video_files_path_template: str, audio_file_path_template: str, store_timeline_clips: bool):
    
    project = VideoProject(
        resolution=(1280, 720),
        fps=24,
        video_files_path_template = video_files_path_template,
        audio_file_path_template=audio_file_path_template
    )
    
    project.split_timeline_into_parts()
    project.build_timeline_clips()
    project.write_video_project_to_file()
    
    if store_timeline_clips:
        project.write_timeline_clips_to_files()

    project.close()
    
    
    