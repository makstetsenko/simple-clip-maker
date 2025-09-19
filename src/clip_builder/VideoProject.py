import src.peaks_detector as peaks_detector
from src.clip_builder.VideoTimeline import VideoTimeline
import src.clip_builder.video_clip_transform as video_clip_transform
from src.clip_builder.effects.zoom_effects import ease_out_zoom_on_time_stops

import librosa
import numpy as np
from moviepy import VideoClip, VideoFileClip, concatenate_videoclips, vfx, CompositeVideoClip


import datetime
import glob
import os
import logging

logger = logging.getLogger(__name__)


class VideoProject:

    def __init__(self, resolution: tuple[int,int], fps: int, video_files_path_template: str, audio_file_path_template: str):
        video_width, video_height = resolution

        self.video_width = video_width
        self.video_height = video_height
        self.fps = fps

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


    def load_clips(self, path_template: str):
        clips = []
        for template in path_template.split(","):
            for g in glob.glob(template):
                clips.append(VideoFileClip(g))

        logger.info("Loaded clips.")
        return clips


    def get_peak_times(self, audio_file_path, criteria: peaks_detector.GetPeaksCriteria):
        peaks_response = peaks_detector.get_peaks_with_sample_rate_with_normalized_energy_with_amplitude_values(audio_file_path, criteria)

        # Convert peak indices to times
        peak_times = librosa.frames_to_time(peaks_response.peaks, sr=peaks_response.sample_rate, hop_length=criteria.hop_length)

        duration = librosa.get_duration(y=peaks_response.amplitude_values, sr=peaks_response.sample_rate)
        peak_times = np.append(peak_times, duration)

        logger.info("Got music time peaks.")
        return peak_times


    def build_timeline_clips(self):
        self.video_timeline.build_timeline_clips()

    def split_timeline_into_parts(self):
        self.video_timeline.split_timeline_into_parts()


    def get_timeline_clips(self) -> list[VideoClip]:
        return self.video_timeline.get_timeline_clips()


    def write_video_project_to_file(self, apply_zoom_bump_effect: bool = False):
        concatenated: VideoClip = concatenate_videoclips(self.get_timeline_clips())
        
        if apply_zoom_bump_effect:
            peak_times_for_zoom = self.get_peak_times(self._audio_file_path, criteria=peaks_detector.GetPeaksCriteria(
                peaks_distance=20,
                peaks_prominence=0.4,
                peaks_height=[0.7, 1]
            ))
            
            # clip = concatenated
            clip = VideoClip(
                frame_function=lambda t: ease_out_zoom_on_time_stops(
                    frame_time=t, 
                    clip=concatenated, 
                    time_stops=peak_times_for_zoom,
                    video_resolution=(self.video_width, self.video_height)), 
                duration=concatenated.duration)
        else:
            clip = concatenated
        
        clip.write_videofile(f"{self.save_dir_path}/{self.project_name}.mp4", audio=self._audio_file_path, audio_codec="aac", fps=self.fps)
        
        concatenated.close()
        clip.close()
        
        logger.info("Save project video clip. Done.")
        

    def write_timeline_clips_to_files(self):
        dir_path = f"{self.save_dir_path}/timeline_clips"
        os.makedirs(dir_path, exist_ok=True)

        for index, c in enumerate(self.get_timeline_clips()):
            c.end += 0.01
            c.duration += 0.01
            c.write_videofile(f"{dir_path}/clip_{index}.mp4", audio_codec="aac", logger=None, fps=self.fps)

        logger.info("Save timeline clips. Done.")

    def close(self):
        self.video_timeline.close()