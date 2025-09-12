import src.peaks_detector as peaks_detector
from src.clip_builder.VideoTimeline import VideoTimeline


import librosa
import numpy as np
from moviepy import VideoClip, VideoFileClip, concatenate_videoclips


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
            c.end += 0.01
            c.duration += 0.01
            c.write_videofile(f"{dir_path}/clip_{index}.mp4", audio_codec="aac", logger=None, fps=self.fps)

        print("Save timeline clips. Done.")


    def close(self):
        self.video_timeline.close()