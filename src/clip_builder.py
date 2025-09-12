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

class ClipBuildResult:
    def __init__(self, timeline_clips: list[VideoClip]):
        self.timeline_clips: list[VideoClip] = timeline_clips


class ClipBuilderHelper:
    @staticmethod
    def find_clip_with_min_duration(min_duration: float,  clips: list[VideoClip]) -> VideoClip:
        filtered = [c for c in clips if c.duration > min_duration]
        
        if len(filtered) == 0:
            return None
        
        return random.choice(filtered)


    @staticmethod
    def compose_clip_with_min_duration(duration: float, clips: list[VideoClip], used_video_clips: list[VideoClip], repeat_clips) -> VideoClip:
        selected_clips: list[VideoClip] = []
        selected_clips_duration = 0
                
        while selected_clips_duration <= duration:
            clip = used_video_clips[-1] \
                if ClipBuilderHelper.can_repeat_clip(used_video_clips, repeat_clips) \
                else ClipBuilderHelper.find_clip_with_min_duration(duration, clips)
                
            if clip == None:
                clip = random.choice(clips)
            
            selected_clips.append(clip)
            selected_clips_duration += clip.duration

        return concatenate_videoclips(clips=selected_clips)
    
    
    @staticmethod
    def can_repeat_clip(used_video_clips: list[VideoClip], repeat_clips) -> bool:
        return repeat_clips and len(used_video_clips) > 0
    
    @staticmethod
    def round_time_to_fps(time: float, fps: int):
        return round(int(math.ceil(time * fps)) / fps, ndigits=2)


    @staticmethod
    def get_random_start_time_for_part_of_clip_duration(clip_duration: float, part_duration: float):
        return random.randint(0, math.floor((clip_duration - part_duration) * 100)) / 100.0


class CropClipBuilder:

    def __init__(self, video_resolution: tuple[int,int], time_stops: list[float], repeat_clips: bool, fps: int):
        self.timeline_clips: list[VideoClip] = []
        self.used_video_clips: list[VideoClip] = []
        
        self.used_clip_start_time = 0
        self.time_stops = time_stops
        self.video_resolution = video_resolution
        self.repeat_clips = repeat_clips
        self.fps = fps

    def build__clip_bewteen_time_stops(self, start_time: float, end_time: float, clips: list[VideoClip]):
        duration = end_time - start_time
            
        clip: VideoClip = ClipBuilderHelper.compose_clip_with_min_duration(
            clips=clips,
            duration=duration,
            used_video_clips=self.used_video_clips,
            repeat_clips=self.repeat_clips
        )
        
        self.used_clip_start_time = self.used_clip_start_time \
            if ClipBuilderHelper.can_repeat_clip(self.used_video_clips, self.repeat_clips) \
            else ClipBuilderHelper.get_random_start_time_for_part_of_clip_duration(clip.duration, duration)

        
        subclipped = clip.subclipped(
            start_time=ClipBuilderHelper.round_time_to_fps(self.used_clip_start_time, self.fps),
            end_time=ClipBuilderHelper.round_time_to_fps(self.used_clip_start_time + duration, self.fps),
        )
        
        timeline_clip = video_clip_transform.crop_video(self.video_resolution[0], self.video_resolution[1], subclipped)
        
        self.timeline_clips.append(timeline_clip)
        self.used_video_clips.append(clip)


    def build(self, clips: list[VideoClip]) -> ClipBuildResult:
        if len(self.time_stops) == 0:
            raise Exception("time_stops is empty. Cannot select clips for empty time stops")        
        
        
        for i in range(1, len(self.time_stops)):
            self.build__clip_bewteen_time_stops(
                start_time=self.time_stops[i-1],
                end_time=self.time_stops[i],
                clips=clips
            )
            
        return ClipBuildResult(
            timeline_clips=self.timeline_clips,
        )
            
    
    def close(self):
        for c in self.timeline_clips + self.used_video_clips:
            c.close()
        

class VideoTimelinePart:
    def __init__(self, video_resolution: tuple[int,int], time_stops: list[float], repeat_clips: bool, fps: int):
        self.timeline_clips: list[VideoClip] = []
        
        self.crop_clip_builder = CropClipBuilder(
            video_resolution=video_resolution,
            repeat_clips=repeat_clips,
            time_stops=time_stops,
            fps=fps
        )
        
    def build_timeline_clips(self, clips: list[VideoClip]):
        build_result = self.crop_clip_builder.build(clips=clips)
        
        for c in build_result.timeline_clips:
            self.timeline_clips.append(c)
        
    
    def close(self):
        self.crop_clip_builder.close()


class VideoTimeline:
    
    def __init__(self, time_stops: list[float], video_resolution: tuple[int,int], fps: int):
        self.parts: list[VideoTimelinePart] = []
        self.time_stops = time_stops
        self.video_resolution = video_resolution
        self.fps = fps
        
    
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
                        repeat_clips=True if random.random() < 0.3 and part_time_stops_count <= 3 else False,
                        fps=self.fps))
                
                part_time_stops = [time_stop]
                part_time_stops_count = random.choice(part_time_stops_total_counts)        
            
                

    def get_timeline_clips(self):
        clips = []
        
        for p in self.parts:
            for c in p.timeline_clips:
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

        
        self.video_clips: list[VideoClip] = self.load_clips(video_files_path_template)
        self.video_timeline: VideoTimeline = VideoTimeline(time_stops=[0] + [float(c) for c in list(self._audio_peak_times)], video_resolution=resolution, fps=fps)
        
        
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
        for p in self.video_timeline.parts:
            p.build_timeline_clips(clips=self.video_clips)
            
    def split_timeline_into_parts(self):
        self.video_timeline.split_timeline_into_parts()
        
        
    def get_timeline_clips(self) -> list[VideoClip]:
        return self.video_timeline.get_timeline_clips()
    
    
    def write_video_project_to_file(self):
        clip = concatenate_videoclips(self.get_timeline_clips())
        clip.write_videofile(f"{self.save_dir_path}/{self.project_name}.mp4", audio=self._audio_file_path, audio_codec="aac", fps=self.fps)
        
        
    def write_timeline_clips_to_files(self):
        dir_path = f"{self.save_dir_path}/timeline_clips"
        os.makedirs(dir_path, exist_ok=True)
        
        for index, c in enumerate(self.get_timeline_clips()):
            c.end += 0.25 / self.fps
            c.duration += 0.25 / self.fps
            c.write_videofile(f"{dir_path}/clip_{index}.mp4", audio_codec="aac", logger=None, fps=self.fps)

    
    def close(self):
        self.video_timeline.close()
    
    

    
def build(video_files_path_template: str, audio_file_path_template: str, store_timeline_clips: bool):
    
    project = VideoProject(
        resolution=(1280, 720),
        fps=25,
        video_files_path_template = video_files_path_template,
        audio_file_path_template=audio_file_path_template
    )
    
    project.split_timeline_into_parts()
    project.build_timeline_clips()
    project.write_video_project_to_file()
    
    if store_timeline_clips:
        project.write_timeline_clips_to_files()

    project.close()
    
    
    