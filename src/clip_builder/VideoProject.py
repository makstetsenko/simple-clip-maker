import src.peaks_detector as peaks_detector
from src.clip_builder.VideoTimeline import VideoTimeline
import src.video_clip_transform as video_clip_transform


import librosa
import numpy as np
from moviepy import VideoClip, VideoFileClip, concatenate_videoclips, vfx, CompositeVideoClip


import datetime
import glob
import os


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
        self._audio_peak_times = self.get_peak_times(self._audio_file_path, criteria=peaks_detector.GetPeaksCriteria(
            peaks_distance=50,
            peaks_prominence=0.4,
            peaks_height=[0.5, 1]
        ))

        self.project_name = self._audio_file_path.split("/")[-1].split(".")[0]
        self.save_dir_path = f"output/{self.project_name}-{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
        os.makedirs(self.save_dir_path, exist_ok=True)


        self.video_clips: list[VideoClip] = self.load_clips(video_files_path_template)
        self.video_timeline: VideoTimeline = VideoTimeline(time_stops=[0] + [float(c) for c in list(self._audio_peak_times)], video_resolution=resolution, fps=fps, video_clips=self.video_clips)
        
        
        self.bump_duration = 0.25  # seconds
        self.bump_magnitude = 0.1  # zoom amount 


    def load_clips(self, path_template: str):
        clips = []
        for template in path_template.split(","):
            for g in glob.glob(template):
                clips.append(VideoFileClip(g))

        print("Loaded clips.")
        return clips


    def get_peak_times(self, audio_file_path, criteria: peaks_detector.GetPeaksCriteria):
        peaks_response = peaks_detector.get_peaks_with_sample_rate_with_normalized_energy_with_amplitude_values(audio_file_path, criteria)

        # Convert peak indices to times
        peak_times = librosa.frames_to_time(peaks_response.peaks, sr=peaks_response.sample_rate, hop_length=criteria.hop_length)

        duration = librosa.get_duration(y=peaks_response.amplitude_values, sr=peaks_response.sample_rate)
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
        concatenated: VideoClip = concatenate_videoclips(self.get_timeline_clips())
        peak_times_for_zoom = self.get_peak_times(self._audio_file_path, criteria=peaks_detector.GetPeaksCriteria(
            peaks_distance=20,
            peaks_prominence=0.4,
            peaks_height=[0.5, 1]
        ))
        
        # clip = concatenated
        clip = VideoClip(frame_function=lambda t: self.zoom_frame_on_peak(t, concatenated, peak_times_for_zoom), duration=concatenated.duration)
        clip.write_videofile(f"{self.save_dir_path}/{self.project_name}.mp4", audio=self._audio_file_path, audio_codec="aac", fps=self.fps)
        
        concatenated.close()
        clip.close()
        
        print("Save project video clip. Done.")
        

    def write_timeline_clips_to_files(self):
        dir_path = f"{self.save_dir_path}/timeline_clips"
        os.makedirs(dir_path, exist_ok=True)

        for index, c in enumerate(self.get_timeline_clips()):
            c.end += 0.01
            c.duration += 0.01
            c.write_videofile(f"{dir_path}/clip_{index}.mp4", audio_codec="aac", logger=None, fps=self.fps)

        print("Save timeline clips. Done.")


    def close(self):
        self.video_timeline.close()
        
    
    def zoom_frame_on_peak(self, t, clip: VideoClip, peak_times):
        for peak_time in peak_times:
            dt = t - peak_time
            if 0 <= dt <= self.bump_duration:
                progress = dt / self.bump_duration
                bump = (1 - progress) ** 2  # ease-out
                scale = 1 - bump * self.bump_magnitude
                w_crop = int(self.video_width * scale)
                h_crop = int(self.video_height * scale)
                x1 = (self.video_width - w_crop) // 2
                y1 = (self.video_height - h_crop) // 2
                x2 = x1 + w_crop
                y2 = y1 + h_crop
                return clip.cropped(x1=x1, y1=y1, x2=x2, y2=y2).resized((self.video_width, self.video_height)).get_frame(t)
        return clip.get_frame(t)