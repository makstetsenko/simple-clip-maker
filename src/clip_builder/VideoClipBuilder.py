from dataclasses import dataclass
from tqdm import tqdm
from src.clip_builder.TimelineConfig import TimelineConfig
from src.clip_builder.VideoProject import TimelineSegmentConfig
from src.clip_builder.effects.zoom_effects import PanZoomEffectCriteria, pan_zoom_frame
from src.clip_builder.video_analyzer import SceneInfo
from src.clip_builder.effects.crop import fit_video_into_frame_size
from src.clip_builder.effects.split_screen import split_screen_clips, get_positions_from_layout, SplitScreenCriteria
from src.clip_builder.VideoNode import VideoNode
from src.clip_builder.VideoResolution import VideoResolution
from src.clip_builder.audio_analyzer import AudioAnalyzeResult, BeatSegment, IntensityBand

import src.clip_builder.effect_presets.zoom as zoom_effect_preset
import src.clip_builder.effect_presets.pan as pan_effect_preset


from src.clip_builder.effects.playback import forward_reverse, ramp_speed, ramp_speed_segments


from moviepy import VideoClip, VideoFileClip, vfx, concatenate_videoclips


import random
import logging


logger = logging.getLogger(__name__)


@dataclass
class VideoClipBuilder:
    fps: int
    resolution: VideoResolution
    temp_path: str

    def build_clip(self, config: TimelineConfig) -> str:
        segments = self.build_segment_clips(config)
        clips = [VideoFileClip(s) for s in segments]

        chained_clip_path = f"{self.temp_path}/chained_clip.mp4"
        chained_clip = concatenate_videoclips(clips=clips, method="compose")
        chained_clip.write_videofile(chained_clip_path, audio=None, fps=self.fps)

        for c in clips:
            c.close()

        chained_clip.close()

        return chained_clip_path

    def build_segment_clips(self, config: TimelineConfig):
        segment_clips: list[str] = []

        with tqdm(total=len(config.segments)) as progress_bar:
            progress_bar.set_description("Building segments")

            for segment in config.segments:
                if segment.is_split_screen:
                    segment_clips.append(self.write_spit_screen_clip(self.temp_path, segment))
                else:
                    segment_clips.append(self.write_single_panel_clip(self.temp_path, segment))

                progress_bar.update(1)

        return segment_clips

    def write_single_panel_clip(self, path: str, segment_config: TimelineSegmentConfig) -> str:
        video = segment_config.videos[0]

        merged_clip: VideoClip = VideoFileClip(video.path)
        subclip = self.get_subclip(merged_clip, video.start_time, segment_config.duration)
        segment_clip = fit_video_into_frame_size(self.resolution.size, subclip)

        segment_clip_path = f"{path}/segment_{segment_config.index}.mp4"
        segment_clip.write_videofile(segment_clip_path, audio=None, logger=None, fps=self.fps)

        segment_clip.close()
        subclip.close()
        merged_clip.close()

        return segment_clip_path

    def write_spit_screen_clip(self, path: str, segment_config: TimelineSegmentConfig) -> str:

        if segment_config.videos == None or len(segment_config.videos) == 0:
            raise Exception("Videos list is empty or null")

        segment_clip_path = f"{path}/segment_{segment_config.index}.mp4"

        if len(segment_config.videos) == 1:
            video = segment_config.videos[0]
            clip = VideoFileClip(video.path)
            subclipped = self.get_subclip(clip, video.start_time, segment_config.duration)

            position_layout = (1, 3) if self.resolution.is_vertical else (3, 1)
            clip_positions = get_positions_from_layout(position_layout)

            segment_clip: VideoClip = split_screen_clips(
                video_width=self.resolution.width,
                video_height=self.resolution.height,
                clips_criteria=[
                    SplitScreenCriteria(
                        clip=subclipped,
                        position=clip_positions[0],
                        scale_factor=0.95,
                    ),
                    SplitScreenCriteria(
                        clip=subclipped,
                        scale_factor=1.1,
                        position=clip_positions[1],
                    ),
                    SplitScreenCriteria(
                        clip=subclipped.with_effects([vfx.MirrorX()]),
                        position=clip_positions[2],
                        scale_factor=0.95,
                    ),
                ],
                position_layout=position_layout,
                clip_duration=segment_config.duration,
            )

            segment_clip.write_videofile(filename=segment_clip_path, audio=None, logger=None, fps=self.fps)

            subclipped.close()
            clip.close()

            return segment_clip_path

        if len(segment_config.videos) == 2:
            video_1 = segment_config.videos[0]
            video_2 = segment_config.videos[1]

            clip_1 = VideoFileClip(video_1.path)
            clip_2 = VideoFileClip(video_2.path)

            subclipped_1: VideoClip = self.get_subclip(clip_1, video_1.start_time, segment_config.duration)
            subclipped_2: VideoClip = self.get_subclip(clip_2, video_2.start_time, segment_config.duration)

            position_layout = (1, 3) if self.resolution.is_vertical else (3, 1)
            clip_positions = get_positions_from_layout(position_layout)

            segment_clip: VideoClip = split_screen_clips(
                video_width=self.resolution.width,
                video_height=self.resolution.height,
                clips_criteria=[
                    SplitScreenCriteria(
                        clip=subclipped_1,
                        position=clip_positions[0],
                        scale_factor=0.95,
                    ),
                    SplitScreenCriteria(
                        clip=subclipped_2,
                        scale_factor=1.1,
                        position=clip_positions[1],
                    ),
                    SplitScreenCriteria(
                        clip=subclipped_1.with_effects([vfx.MirrorX()]),
                        position=clip_positions[2],
                        scale_factor=0.95,
                    ),
                ],
                position_layout=position_layout,
                clip_duration=segment_config.duration,
            )

            segment_clip.write_videofile(filename=segment_clip_path, audio=None, logger=None, fps=self.fps)

            subclipped_1.close()
            subclipped_2.close()
            clip_1.close()
            clip_2.close()

            return segment_clip_path

        position_layout = (
            (1, len(segment_config.videos)) if self.resolution.is_vertical else (len(segment_config.videos), 1)
        )
        clip_positions = get_positions_from_layout(position_layout)

        split_screen_criteria = []
        clips: list[VideoClip] = []
        subclips: list[VideoClip] = []

        for i, v in enumerate(segment_config.videos):
            c = VideoFileClip(v.path)
            s = self.get_subclip(c, v.start_time, segment_config.duration)
            clips.append(c)
            subclips.append(s)
            split_screen_criteria.append(SplitScreenCriteria(clip=s, position=clip_positions[i], scale_factor=1))

        segment_clip: VideoClip = split_screen_clips(
            video_width=self.resolution.width,
            video_height=self.resolution.height,
            clips_criteria=split_screen_criteria,
            position_layout=position_layout,
            clip_duration=segment_config.duration,
        )

        segment_clip.write_videofile(filename=segment_clip_path, audio=None, logger=None, fps=self.fps)

        for c in subclips + clips:
            c.close()

        return segment_clip_path

    def get_clip_padding(self, duration: float):
        requires_frame_drift = duration <= 0.55
        return (1.0 / self.fps) if requires_frame_drift else 0

    def get_subclip(self, clip: VideoClip, start_time: float, duration: float) -> VideoClip:
        return clip[start_time : start_time + duration + self.get_clip_padding(duration)].with_duration(duration)
