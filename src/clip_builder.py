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
    def get_random_start_time_for_desired_of_clip_duration(full_clip_duration: float, desired_duration: float):
        return random.randint(0, math.floor((full_clip_duration - desired_duration) * 100)) / 100.0
    
    
    @staticmethod
    def is_vertical(video_resolution: tuple[int,int]):
        return video_resolution[0] / video_resolution[1] < 1
        
    
    @staticmethod
    def is_horizontal(video_resolution: tuple[int,int]):
        return not ClipBuilderHelper.is_vertical(video_resolution)
    
    
    @staticmethod
    def are_matching_aspect_ratios(aspect_ratios: list[float]):
        return all(a >= 1 for a in aspect_ratios) or all(a < 1 for a in aspect_ratios)
        

class CropedVideoTimelineBuilder:
    def __init__(self, video_resolution: tuple[int,int], time_stops: list[float], repeat_clips: bool, fps: int, video_clips: list[VideoClip]):
        self.timeline_clips: list[VideoClip] = []
        self.used_video_clips: list[VideoClip] = []
        
        self.used_clip_start_time = 0
        self.time_stops = time_stops
        self.video_resolution = video_resolution
        self.repeat_clips = repeat_clips 
        self.fps = fps
        self.video_clips = video_clips
        
        
    def build_timeline_clips(self):
        if len(self.time_stops) == 0:
            raise Exception("time_stops is empty. Cannot select clips for empty time stops")        
        
        
        for i in range(1, len(self.time_stops)):
            self.build__clip_bewteen_time_stops(
                start_time=self.time_stops[i-1],
                end_time=self.time_stops[i]
            )
        
        
    def build__clip_bewteen_time_stops(self, start_time: float, end_time: float):
        duration = end_time - start_time
            
        clip: VideoClip = ClipBuilderHelper.compose_clip_with_min_duration(
            clips=self.video_clips,
            duration=duration,
            used_video_clips=self.used_video_clips,
            repeat_clips=self.repeat_clips
        )
        
        self.used_clip_start_time = self.used_clip_start_time \
            if ClipBuilderHelper.can_repeat_clip(self.used_video_clips, self.repeat_clips) \
            else ClipBuilderHelper.get_random_start_time_for_desired_of_clip_duration(clip.duration, duration)

        
        subclipped = clip.subclipped(
            start_time=ClipBuilderHelper.round_time_to_fps(self.used_clip_start_time, self.fps),
            end_time=ClipBuilderHelper.round_time_to_fps(self.used_clip_start_time + duration, self.fps),
        )
        
        timeline_clip = video_clip_transform.crop_video(self.video_resolution[0], self.video_resolution[1], subclipped)
        
        self.timeline_clips.append(timeline_clip)
        self.used_video_clips.append(clip)


    
    def close(self):
        for c in self.timeline_clips + self.used_video_clips:
            c.close()



class SplitScreenVideoTimelineBuilder:
    def __init__(self, video_resolution: tuple[int,int], time_stops: list[float], repeat_clips: bool, fps: int, video_clips: list[VideoClip]):
        self.timeline_clips: list[VideoClip] = []
        self.used_video_clips_1: list[VideoClip] = []
        self.used_video_clips_2: list[VideoClip] = []
        
        self.used_clip_start_time_1 = 0
        self.used_clip_start_time_2 = 0
        self.time_stops = time_stops
        self.video_resolution = video_resolution
        self.repeat_clips = repeat_clips
        self.fps = fps
        self.video_clips = video_clips
        
        
    def build_timeline_clips(self):
        if len(self.time_stops) == 0:
            raise Exception("time_stops is empty. Cannot select clips for empty time stops")        
        
        for i in range(1, len(self.time_stops)):
            self.build__clip_bewteen_time_stops(
                start_time=self.time_stops[i-1],
                end_time=self.time_stops[i]
            )
        
        
    def build__clip_bewteen_time_stops(self, start_time: float, end_time: float, center_clip: VideoClip | None=None):
        duration = end_time - start_time
            
        clip_1: VideoClip = ClipBuilderHelper.compose_clip_with_min_duration(
            clips=self.video_clips,
            duration=duration,
            used_video_clips=self.used_video_clips_1,
            repeat_clips=self.repeat_clips
        )
        
        clip_2: VideoClip = ClipBuilderHelper.compose_clip_with_min_duration(
            clips=self.video_clips,
            duration=duration,
            used_video_clips=self.used_video_clips_2,
            repeat_clips=self.repeat_clips
        )
        
        self.used_clip_start_time_1 = self.get_clip_start_time(self.used_clip_start_time_1, self.used_video_clips_1, self.repeat_clips, clip_1.duration, duration)
        self.used_clip_start_time_2 = self.get_clip_start_time(self.used_clip_start_time_2, self.used_video_clips_2, self.repeat_clips, clip_2.duration, duration)

        
        subclipped_1 = clip_1.subclipped(
            start_time=ClipBuilderHelper.round_time_to_fps(self.used_clip_start_time_1, self.fps),
            end_time=ClipBuilderHelper.round_time_to_fps(self.used_clip_start_time_1 + duration, self.fps),
        )
        subclipped_2 = clip_2.subclipped(
            start_time=ClipBuilderHelper.round_time_to_fps(self.used_clip_start_time_2, self.fps),
            end_time=ClipBuilderHelper.round_time_to_fps(self.used_clip_start_time_2 + duration, self.fps),
        )
        
        timeline_clip = video_clip_transform.split_screen_clips(
            video_width=self.video_resolution[0],
            video_height=self.video_resolution[1],
            clips=[subclipped_1, subclipped_2, subclipped_1] if center_clip is None else [subclipped_1, center_clip, subclipped_2],
            max_position=(3, 1) if ClipBuilderHelper.is_horizontal(self.video_resolution) else (1, 3)
        )
        
        self.timeline_clips.append(timeline_clip)
        self.used_video_clips_1.append(clip_1)
        self.used_video_clips_2.append(clip_2)


    
    def get_clip_start_time(self, used_clip_start_time: float, used_video_clips: list[VideoClip], repeat_clips: bool, full_clip_duration, desired_duration):
        return used_clip_start_time \
            if ClipBuilderHelper.can_repeat_clip(used_video_clips, repeat_clips) \
            else ClipBuilderHelper.get_random_start_time_for_desired_of_clip_duration(full_clip_duration, desired_duration)
            
    
    
    def close(self):
        for c in self.timeline_clips + self.used_video_clips_1 + self.used_video_clips_2:
            c.close()


class VideoTimeline:
    
    def __init__(self, time_stops: list[float], video_resolution: tuple[int,int], fps: int, video_clips: list[VideoClip]):
        self.timelime_builders: list = []
        self.time_stops = time_stops
        self.video_resolution = video_resolution
        self.video_aspect_ratio = video_resolution[0] / video_resolution[1]
        self.fps = fps
        self.video_clips = video_clips
    
    def split_timeline_into_parts(self):
        part_time_stops_total_counts = [2,3,4,5]
        
        part_time_stops = []
        part_time_stops_count = random.choice(part_time_stops_total_counts)
        
        matched_aspect_ratio_clips = [c for c in self.video_clips if ClipBuilderHelper.are_matching_aspect_ratios([c.aspect_ratio, self.video_aspect_ratio])]
        not_matched_aspect_ratio_clips = [c for c in self.video_clips if not ClipBuilderHelper.are_matching_aspect_ratios([c.aspect_ratio, self.video_aspect_ratio])]
        
        matched_aspect_ratio_clips_count = len(matched_aspect_ratio_clips)
        total_clips_count = len(self.video_clips)
        
        for index, time_stop in enumerate(self.time_stops):
            part_time_stops.append(time_stop)
            
            if len(part_time_stops) == part_time_stops_count or index == len(self.time_stops) - 1:
                if random.random() < 1.0 * matched_aspect_ratio_clips_count / total_clips_count:
                    self.timelime_builders.append(
                        CropedVideoTimelineBuilder(
                            video_resolution=self.video_resolution,
                            time_stops=[x for x in part_time_stops],
                            repeat_clips=False,
                            fps=self.fps,
                            video_clips=matched_aspect_ratio_clips))
                    
                else:
                    self.timelime_builders.append(
                        SplitScreenVideoTimelineBuilder(
                            video_resolution=self.video_resolution,
                            time_stops=[x for x in part_time_stops],
                            repeat_clips=False,
                            fps=self.fps,
                            video_clips=not_matched_aspect_ratio_clips))
                    
                
                part_time_stops = [time_stop]
                part_time_stops_count = random.choice(part_time_stops_total_counts)     
                
            
        print("Split video timeline. Done.")   
            
    
    def build_timeline_clips(self):
        for b in self.timelime_builders:
            b.build_timeline_clips()
        
        print("Build timeline clips. Done.")   

    def get_timeline_clips(self):
        clips = []
        
        for p in self.timelime_builders:
            for c in p.timeline_clips:
                clips.append(c)

        return clips
                

    def close(self):
        for p in self.timelime_builders:
            p.close()
        
        print("Closed clips.")   
                


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
        self.video_timeline: VideoTimeline = VideoTimeline(time_stops=[0] + [float(c) for c in list(self._audio_peak_times)], video_resolution=resolution, fps=fps, video_clips=self.video_clips)
        
        
    def load_clips(self, path_template: str):
        clips = []
        for template in path_template.split(","):
            for g in glob.glob(template):
                clips.append(VideoFileClip(g))
                
        print("Loaded clips.")
        return clips
        
        
    def get_peak_times(self, audio_file_path):    
        peaks, sample_rate, _, amplitude_values = peaks_detector.get_peaks_with_sample_rate_with_normalized_energy_with_amplitude_values(audio_file_path)

        # Convert peak indices to times
        peak_times = librosa.frames_to_time(peaks, sr=sample_rate, hop_length=peaks_detector.hop_length)

        duration = librosa.get_duration(y=amplitude_values, sr=sample_rate)
        peak_times = np.append(peak_times, duration)
        
        print("Got music time peaks.")
        return peak_times
    
    
    def build_timeline_clips(self):
        self.video_timeline.build_timeline_clips()
            
    def split_timeline_into_parts(self):
        self.video_timeline.split_timeline_into_parts()
        
        
    def get_timeline_clips(self) -> list[VideoClip]:
        return self.video_timeline.get_timeline_clips()
    
    
    def write_video_project_to_file(self):
        clip = concatenate_videoclips(self.get_timeline_clips())
        clip.write_videofile(f"{self.save_dir_path}/{self.project_name}.mp4", audio=self._audio_file_path, audio_codec="aac", fps=self.fps)
        print("Save project video clip. Done.")   
        
        
    def write_timeline_clips_to_files(self):
        dir_path = f"{self.save_dir_path}/timeline_clips"
        os.makedirs(dir_path, exist_ok=True)
        
        for index, c in enumerate(self.get_timeline_clips()):
            c.end += 0.25 / self.fps
            c.duration += 0.25 / self.fps
            c.write_videofile(f"{dir_path}/clip_{index}.mp4", audio_codec="aac", logger=None, fps=self.fps)
            
        print("Save timeline clips. Done.")   

    
    def close(self):
        self.video_timeline.close()
    
    

    
def build(video_files_path_template: str, audio_file_path_template: str, store_timeline_clips: bool):
    
    project = VideoProject(
        # resolution=(720, 1280),
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
    
    
    