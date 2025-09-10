import librosa
import numpy as np
from moviepy import *
import src.peaks_detector as peaks_detector
import random 
import glob
from skimage.filters import gaussian
import uuid
import os
import math
import datetime


# video_width = 720
# video_height = 1280

video_width = 1280
video_height = 720

aspect_ratio = video_width / video_height

is_horizontal_video = aspect_ratio >= 1
is_vertical_video = aspect_ratio < 1

fps=24
 
sub_clip_extend_time = 0.009 # when saving as separate clip add some extra time to avoid cutting vide earlier than expected, Idk why this value, it just works

class VideoClipEnriched:
    def __init__(self, clip: VideoClip, path: str | None = None, full_name: str | None = None, dir_path: str | None = None):
        self.clip = clip
        self.duration = clip.duration
        self.aspect_ratio = clip.aspect_ratio
        

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
        

class ClipMakerState:
    def __init__(self):
        self.should_change_clip: bool = True
        self.should_use_same_clip_start: bool = False
        self.sub_clip_counter: int = 1
        self.clip_info: VideoClipEnriched | None = None
        self.sub_clip_start_frame: int | None = None
        
        
    def choose_clip(self, clips: list[VideoClipEnriched], minimum_duration_frames: int) -> VideoClipEnriched:
        # choose clip that has duration more than duration between peaks
        if self.should_change_clip:
            self.sub_clip_counter = 1
            
            while 1:
                self.clip_info = random.choice(clips)
                
                if self.clip_info.duration_frames > minimum_duration_frames:
                    return self.clip_info
        
        
        self.sub_clip_counter += 1 
        
        return self.clip_info
        
    def choose_start_frame(self, minimum_duration_frames: int) -> int | None:
        if self.should_use_same_clip_start:
            return self.sub_clip_start_frame
    
        while 1:
            self.sub_clip_start_frame = random.randint(1, self.clip_info.duration_frames)
            
            if self.sub_clip_start_frame + minimum_duration_frames < self.clip_info.duration_frames:
                return self.sub_clip_start_frame
            
        # Default return state
        return None
    
    def recalculate_state(self) -> None:
        self.should_change_clip = random.random() < 0.3 or self.sub_clip_counter > 3
        self.should_use_same_clip_start = not self.should_change_clip and random.random() > 0.7

        
class VideoTimeline:
    
    def __init__(self):
        self.clips: list[VideoClipEnriched] = []

class VideoProject:
    
    def __init__(self, video_width: int, video_height: int, fps: int, audio_file_path_template: str):
        self.video_width = video_width
        self.video_height = video_height
        self.fps = fps
        self.aspect_ratio = video_width / video_height
        self.is_horizontal_video = aspect_ratio >= 1
        self.is_vertical_video = aspect_ratio < 1
        self._audio_file_path = glob.glob(audio_file_path_template)[0]
        
        self.clips: list[VideoClipEnriched] = []
        
        self.timeline: VideoTimeline = VideoTimeline()
        self.clip_to_save_extend_time = 0.009 # when saving as separate clip add some extra time to avoid cutting vide earlier than expected, Idk why this value, it just works
        
    def load_clips(self, path_template: str):
        for template in path_template.split(","):
            for g in glob.glob(template):
                self.clips.append(VideoClipEnriched(clip=VideoFileClip(g).with_fps(self.fps), path=g))
        

def crop_video(clip: VideoClip):
    clip_aspect = clip.w / clip.h

    if clip_aspect < aspect_ratio:
        scaled_clip: VideoClip = clip.resized(width=video_width)
    else:
        scaled_clip: VideoClip = clip.resized(height=video_height)

    return scaled_clip.cropped(
        x_center=scaled_clip.w / 2,
        y_center=scaled_clip.h / 2,
        width=video_width,
        height=video_height
    )
    
    
def set_clip_position(clip: VideoClip, position: tuple[int,int], max_position: tuple[int,int]) -> VideoClip:
    clip_aspect = clip.w / clip.h
    
    rows, cols = max_position
    
    clip_width = int(video_width / rows)
    clip_height = int(video_height / cols)
    
    if clip_aspect > aspect_ratio:
        scaled_clip: VideoClip = clip.resized(height=clip_height)
    else:
        scaled_clip: VideoClip = clip.resized(width=clip_width)
                
    cropped_clip = scaled_clip.cropped(
        x_center=scaled_clip.w / 2,
        y_center=scaled_clip.h / 2,
        width=clip_width,
        height=clip_height
    )
    
    clip_x = int((position[0] - 1) * clip_width) # top left corner
    clip_y = int((position[1] - 1) * clip_height) # top left corner
    
    return cropped_clip.with_position((clip_x, clip_y))

def split_screen_clips(clips: list[VideoClip], max_position: tuple[int,int], manual_positions: list[tuple[int,int]] | None = None):
    rows, cols = max_position
    
    positions = []
    
    if manual_positions == None:    
        for r in range(1, rows + 1):
            for c in range(1, cols + 1):
                positions.append((r, c))
    else:
        positions = manual_positions
    
    positioned_clips = []
    for i, c in enumerate(clips):
        pos_clip = set_clip_position(c, position=positions[i], max_position=max_position)
        positioned_clips.append(pos_clip)
    
    return CompositeVideoClip(
        clips=positioned_clips, 
        size=(video_width, video_height),
        bg_color=(0,0,0),
    ).with_duration(clips[0].duration)
    
    
def release_resources(clips: list[VideoClipEnriched]):
    for c in clips:
        c.clip.close()
        
        
def get_peak_times(audio_file_path):    
    peaks, sample_rate, _, amplitude_values = peaks_detector.get_peaks_with_sample_rate_with_normalized_energy_with_amplitude_values(audio_file_path)

    # Convert peak indices to times
    peak_times = librosa.frames_to_time(peaks, sr=sample_rate, hop_length=peaks_detector.hop_length)

    duration = librosa.get_duration(y=amplitude_values, sr=sample_rate)
    peak_times = np.append(peak_times, duration)
    
    return peak_times

def get_sub_clip_for_peak(sub_clip_frames_duration, clips: list[VideoClipEnriched], original_clip: VideoClipEnriched | None, clip_start_frame: int | None) -> VideoClipEnriched | None:
    clip_end_frame =  clip_start_frame + sub_clip_frames_duration
    
    
    sub_clip_start_time = round(clip_start_frame / fps, 2)
    sub_clip_end_time = round(clip_end_frame / fps, 2)
        
    
    if original_clip.is_aspect_ration_same_as_target(aspect_ratio):
        sub_clip = crop_video(original_clip.clip.subclipped(sub_clip_start_time, sub_clip_end_time))
        return VideoClipEnriched(clip=sub_clip, full_name=f"{original_clip.name}.{original_clip.ext}", dir_path=original_clip.dir_path)
    
    
    max_positions = (3,1) if original_clip.is_vertical() and is_horizontal_video else (1,3)

    rows, cols = max_positions
    
    original_sub_clip = original_clip.clip.subclipped(sub_clip_start_time, sub_clip_end_time)
    
    # in 70% just return single clip in random place
    if random.random() < 0.7:
        cell_number = 2
        sub_clip_position = (cell_number,1) if original_clip.is_vertical() and is_horizontal_video else (1,cell_number)
        sub_clip = split_screen_clips([original_sub_clip], max_position=max_positions, manual_positions=[sub_clip_position])
        return VideoClipEnriched(clip=sub_clip, full_name=f"{original_clip.name}.{original_clip.ext}", dir_path=original_clip.dir_path)
    
    
    filtered_clips = [c.clip for c in clips if c.is_vertical() and c.path != original_clip.path and c.clip.duration >= original_clip.clip.duration]
    
    if len(filtered_clips) == 0:
        filtered_clips.append(original_sub_clip)
        
    choosed_clips = [c.subclipped(sub_clip_start_time, sub_clip_end_time) for c in random.choices(filtered_clips, k=max(cols, rows)-1)]
    choosed_clips.insert(int(len(choosed_clips) / 2), original_sub_clip)
    
    sub_clip = split_screen_clips(choosed_clips, max_position=(rows, cols))
    return VideoClipEnriched(clip=sub_clip, full_name=f"{original_clip.name}.{original_clip.ext}", dir_path=original_clip.dir_path)
    

def build_music_clip(args):
    audio_file_path = glob.glob(args.music_file)[0]
    
    clips: list[VideoClipEnriched] = []
    sub_clips: list[VideoClipEnriched] = []
    sub_clips_to_save: list[VideoClipEnriched] = []
    
    for template in args.video_files_path_template.split(","):
        for g in glob.glob(template):
            clips.append(VideoClipEnriched(clip=VideoFileClip(g).with_fps(fps), path=g))

    print("Loaded videos")

    peak_times = get_peak_times(audio_file_path)   
    peak_frames = []
    total_peaks = len(peak_times)
    
    for p in peak_times:
        peak_frames.append(math.floor(p * fps)) # snap time to frames
    
    clip_maker_state = ClipMakerState()
    
    print("Genereated peaks")
    
    for index, peak_frame in enumerate(peak_frames):    
        start_frame = peak_frames[index-1] if index > 0 else 0
        end_frame = peak_frame
        
        sub_clip_frames_duration = end_frame - start_frame
                    
        original_clip_info = clip_maker_state.choose_clip(clips, sub_clip_frames_duration)
        original_clip_start_frame = clip_maker_state.choose_start_frame(sub_clip_frames_duration)

        sub_clip = get_sub_clip_for_peak(
            sub_clip_frames_duration=sub_clip_frames_duration,
            clips=clips,
            original_clip=original_clip_info,
            clip_start_frame=original_clip_start_frame
        )

        clip_maker_state.recalculate_state()
        
        sub_clips.append(sub_clip)
        sub_clips_to_save.append(VideoClipEnriched(original_clip_info.clip.subclipped(original_clip_start_frame / fps, (original_clip_start_frame + sub_clip_frames_duration + sub_clip_extend_time) / fps), path=original_clip_info.path))
        
        print(f"Generated sub_clip {index+1}/{len(peak_frames)}")    
    
    print("Genereated sub_clips")
    
    final_clip_name = audio_file_path.split("/")[-1].split(".")[0]
    save_dir_path = f"output/{final_clip_name}-{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
    
    os.makedirs(save_dir_path, exist_ok=True)
    
    final_clip: VideoClip = concatenate_videoclips(list(map(lambda x: x.clip, sub_clips)))
    final_clip.write_videofile(f"{save_dir_path}/{final_clip_name}.mp4", audio=audio_file_path, audio_codec="aac", fps=fps)
    
    if args.store_sub_clips:
        print("Saving sub clips...")
        save_sub_clips_dir_path = f"{save_dir_path}/sub_clips"
        os.makedirs(save_sub_clips_dir_path, exist_ok=True)
        for index, c in enumerate(sub_clips_to_save):
            c.clip.write_videofile(f"{save_sub_clips_dir_path}/{index}_{c.name}.mp4", audio_codec="aac", logger=None, fps=fps)


    release_resources(sub_clips + clips + sub_clips_to_save)
    print("Done")
