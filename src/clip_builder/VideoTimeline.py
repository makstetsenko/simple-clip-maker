from tqdm import tqdm
from src.clip_builder.effects.zoom_effects import PanZoomEffectCriteria, pan_zoom_frame
from src.clip_builder.video_analyzer import SceneInfo
from src.clip_builder import video_clip_transform
from src.clip_builder.VideoNode import VideoNode
from src.clip_builder.VideoResolution import VideoResolution
from src.clip_builder.audio_analyzer import AudioAnalyzeResult, BeatSegment, IntensityBand

import src.clip_builder.effect_presets.zoom as zoom_effect_preset
import src.clip_builder.effect_presets.pan as pan_effect_preset

from moviepy import VideoClip, VideoFileClip, vfx, concatenate_videoclips


import random
import logging


logger = logging.getLogger(__name__)


class VideoTimeline:

    def __init__(
        self,
        fps: int,
        resolution: VideoResolution,
        audio_analysis: AudioAnalyzeResult,
        video_analysis: list[VideoNode],
        temp_path: str,
    ):
        self.fps = fps
        self.resolution = resolution
        self.audio_analysis = audio_analysis
        self.video_analysis = video_analysis
        self.temp_path = temp_path

    def build_timeline_clip(self) -> str:
        segments = self.build_segment_clips()
        clips = [VideoFileClip(s) for s in segments]

        chained_clip_path = f"{self.temp_path}/chained_clip.mp4"
        chained_clip = concatenate_videoclips(clips=clips, method="compose")
        chained_clip.write_videofile(chained_clip_path, audio=None, fps=self.fps)

        for c in clips:
            c.close()

        chained_clip.close()

        return chained_clip_path

    def build_segment_clips(self):
        segment_clips = []
        video_node = self.video_analysis[0]

        with tqdm(total=len(self.audio_analysis.beat_segments)) as progress_bar:
            progress_bar.set_description("Building segments")

            for segment in self.audio_analysis.beat_segments:
                if self.resolution.matches_aspect_ratio(video_node.resolution):
                    segment_clips.append(self.get_crop_segment_clip(video_node, segment))
                else:
                    segment_clips.append(self.get_split_screen_segment_clip(video_node, segment))

                video_node = video_node.next

                progress_bar.update(1)

        return segment_clips

    def get_crop_segment_clip(self, video_node: VideoNode, segment: BeatSegment):
        scene = self.get_video_scene(video_node, segment)

        clip = self.get_clip(video_node, segment)
        subclipped = self.get_sub_clip(segment, scene, clip)

        segment_clip_path = f"{self.temp_path}/{segment.index}.mp4"
        segment_clip = video_clip_transform.crop_video(self.resolution.width, self.resolution.height, subclipped)

        segment_clip = pan_effect_preset.pan_side_to_side(segment_clip, pan=(0, 2000), easing=None)

        segment_clip.write_videofile(filename=segment_clip_path, audio=None, logger=None, fps=self.fps)

        segment_clip.close()
        subclipped.close()
        clip.close()
        return segment_clip_path

    def get_split_screen_segment_clip(self, video_node: VideoNode, segment: BeatSegment):
        video_node_2 = video_node.find_next(lambda x: x.resolution.matches_aspect_ratio(video_node.resolution))

        scene_1 = self.get_video_scene(video_node, segment)
        scene_2 = self.get_video_scene(video_node_2, segment)

        clip_1 = VideoFileClip(video_node.path)
        clip_2 = VideoFileClip(video_node_2.path)

        subclipped_1: VideoClip = self.get_sub_clip(segment, scene_1, clip_1)
        subclipped_2: VideoClip = self.get_sub_clip(segment, scene_2, clip_2)

        position_layout = (1, 3) if self.resolution.is_vertical else (3, 1)
        clip_positions = video_clip_transform.get_positions_from_layout(position_layout)

        segment_clip_path = f"{self.temp_path}/{segment.index}.mp4"
        segment_clip: VideoClip = video_clip_transform.split_screen_clips(
            video_width=self.resolution.width,
            video_height=self.resolution.height,
            clips_criteria=[
                video_clip_transform.SplitScreenCriteria(
                    clip=subclipped_1,
                    position=clip_positions[0],
                    scale_factor=0.95,
                ),
                video_clip_transform.SplitScreenCriteria(
                    clip=subclipped_2,
                    scale_factor=1.1,
                    position=clip_positions[1],
                ),
                video_clip_transform.SplitScreenCriteria(
                    clip=subclipped_1.with_effects([vfx.MirrorX()]),
                    position=clip_positions[2],
                    scale_factor=0.95,
                ),
            ],
            position_layout=position_layout,
            clip_duration=segment.duration,
        )

        segment_clip.write_videofile(filename=segment_clip_path, audio=None, logger=None, fps=self.fps)

        segment_clip.close()
        subclipped_1.close()
        subclipped_2.close()
        clip_1.close()
        clip_2.close()
        return segment_clip_path

    def get_video_scene(self, video_node: VideoNode, segment: BeatSegment) -> SceneInfo:
        return random.choice(video_node.scenes)

    def get_clip(self, video_node: VideoNode, segment: BeatSegment) -> VideoClip:
        return VideoFileClip(video_node.path)

    def get_sub_clip(self, segment: BeatSegment, scene: SceneInfo, clip: VideoClip) -> VideoClip:
        requires_frame_drift = segment.duration <= 0.55
        padding = (1.0 / self.fps) if requires_frame_drift else 0

        return clip.subclipped(start_time=scene.start_time, end_time=scene.start_time + segment.duration + padding)
