from src.clip_builder import video_clip_transform
from src.clip_builder.VideoNode import VideoNode
from src.clip_builder.VideoResolution import VideoResolution
from src.clip_builder.audio_analyzer import AudioAnalyzeResult

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
        self.padding = 1.0 / self.fps  # 1 frame duration padding

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

        for segment in self.audio_analysis.beat_segments:
            logger.info(f"Building segment {segment.index}/{len(self.audio_analysis.beat_segments)}")

            if self.resolution.matches_aspect_ratio(video_node.resolution):
                scene = random.choice([s for s in video_node.scenes if s.duration >= segment.duration])

                clip = VideoFileClip(video_node.path)
                subclipped: VideoClip = clip.subclipped(
                    start_time=scene.start_time,
                    end_time=scene.start_time + segment.duration + self.padding,
                )

                segment_clip_path = f"{self.temp_path}/{segment.index}.mp4"
                segment_clip = video_clip_transform.crop_video(self.resolution.width, self.resolution.height, subclipped)
                segment_clip.write_videofile(filename=segment_clip_path, audio=None, logger=None, fps=self.fps)
                segment_clips.append(segment_clip_path)

                segment_clip.close()
                subclipped.close()
                clip.close()
            else:
                video_node_2 = video_node.find_next(lambda x: not x.resolution.matches_aspect_ratio(self.resolution))

                scene_1 = random.choice(video_node.scenes)
                scene_2 = random.choice(video_node_2.scenes)

                clip_1 = VideoFileClip(video_node.path)
                clip_2 = VideoFileClip(video_node_2.path)

                subclipped_1: VideoClip = clip_1.subclipped(
                    start_time=scene_1.start_time,
                    end_time=scene_1.start_time + segment.duration + self.padding,
                )
                subclipped_2: VideoClip = clip_2.subclipped(
                    start_time=scene_2.start_time,
                    end_time=scene_2.start_time + segment.duration + self.padding,
                )

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
                segment_clips.append(segment_clip_path)

                segment_clip.close()
                subclipped_1.close()
                subclipped_2.close()
                clip_1.close()
                clip_2.close()

            video_node = video_node.next

        return segment_clips
