from dataclasses import dataclass
import random
from typing import Self
from src.clip_builder.timeline_config import (
    TimelineConfig,
    TimelineSegmentConfig,
    VideoItem,
    VideoSegmentEffect,
    EffectType,
    EffectMethod,
)
from src.clip_builder.effects.crop import fit_video_into_frame_size
from src.clip_builder.effects.split_screen import SplitScreenCriteria, get_positions_from_layout, split_screen_clips
from src.clip_builder.preview_video_timeline import PreviewVideoTimeline
from src.clip_builder.json_cache import JsonCache
from src.clip_builder.video_node import VideoNode
from src.clip_builder.video_resolution import VideoResolution
from src.clip_builder.video_clip_builder import VideoClipBuilder

from moviepy import VideoClip, VideoFileClip, vfx
from src.clip_builder.audio_analyzer import (
    BeatSegment,
    analyze_music_for_editing,
    AudioAnalyzeResult,
)
from src.clip_builder.video_analyzer import (
    analyze_on_static_scenes,
    video_details,
)

import datetime
import glob
import os
import logging
import json
import shutil
import yaml

logger = logging.getLogger(__name__)


class VideoProject:
    def __init__(
        self,
        resolution: tuple[int, int],
        fps: int,
        video_files_path_template: str,
        audio_file_path_template: str,
        preview: bool = False,
    ):
        self.resolution = VideoResolution(resolution)
        self.fps = fps
        self.project_name = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        self.project_dir_path = f"./output/projects/{self.project_name}"
        self.temp_dir_path = f"{self.project_dir_path}/temp"
        self.temp_analysis_dir_path = f"{self.temp_dir_path}/analysis"

        self.json_cache: JsonCache = JsonCache()

        self.audio_path = glob.glob(audio_file_path_template)[0]

        self.videos_path_list = []
        for p in video_files_path_template.split(","):
            self.videos_path_list += glob.glob(p)

        self.preview = preview
        self.prepare_dirs()

    def get_clip_builder(self) -> VideoClipBuilder:
        return VideoClipBuilder(
            fps=self.fps,
            resolution=self.resolution,
            temp_path=self.temp_dir_path,
        )

    def save_clip_with_audio(self, clip_path):
        output_clip_path = f"{self.project_dir_path}/output.mp4"

        logger.info(f"Saving clip {output_clip_path}")

        clip = VideoFileClip(clip_path)
        clip.write_videofile(output_clip_path, audio=self.audio_path, audio_codec="aac", fps=self.fps)
        clip.close()

    def get_audio_analysis(self) -> AudioAnalyzeResult:
        logger.info(f"Analyzing audio {self.get_file_name(self.audio_path)}")

        cache_key = self.get_cache_key_from_path(self.audio_path)
        cached_value = self.json_cache.get(cache_key)

        if cached_value is None:
            analysis = analyze_music_for_editing(self.audio_path, similarity_threshold=0.6)

            self.json_cache.set(cache_key, analysis.to_json())

            return analysis

        return AudioAnalyzeResult.from_json(cached_value)

    def get_video_analysis(self) -> list[VideoNode]:
        res: list[VideoNode] = []

        for i, p in enumerate(self.videos_path_list):
            logger.info(f"Analyzing for video {self.get_file_name(p)}")

            cache_key = self.get_cache_key_from_path(p)
            cached_value = self.json_cache.get(cache_key)

            if cached_value is None:
                scenes = analyze_on_static_scenes(p, time_step=0.3, scene_duration_threshold=3)
                details = video_details(p)

                video_node = VideoNode(
                    path=p,
                    fps=details.fps,
                    resolution=VideoResolution(details.resolution),
                    scenes=[s for s in scenes if s.is_static == False],
                )

                self.json_cache.set(cache_key, video_node.to_json())

                res.append(video_node)
            else:
                res.append(VideoNode.from_json(cached_value))

        for i in range(0, len(res) - 1):
            res[i].next = res[i + 1]

        res[-1].next = res[0]

        return res

    def get_default_timeline_config(self) -> TimelineConfig:
        audio_analysis = self.get_audio_analysis()
        video_analysis = self.get_video_analysis()

        self.store_analysis_to_temp(audio_analysis, video_analysis)

        video_node = video_analysis[0]

        timeline_segments = []
        for beat_segment in audio_analysis.beat_segments:
            start_time = self.get_video_start_time(video_node, beat_segment)

            if video_node.resolution.matches_aspect_ratio(self.resolution):

                timeline_segments.append(
                    TimelineSegmentConfig(
                        index=beat_segment.index,
                        is_split_screen=False,
                        videos=[VideoItem(path=video_node.path, start_time=start_time)],
                        effects=[],
                        duration=beat_segment.duration,
                    )
                )
            else:
                video_node_2 = video_node.find_next(lambda v: v.resolution.matches_aspect_ratio(video_node.resolution))
                start_time_2 = self.get_video_start_time(video_node_2, beat_segment)

                timeline_segments.append(
                    TimelineSegmentConfig(
                        index=beat_segment.index,
                        is_split_screen=True,
                        videos=[
                            VideoItem(path=video_node.path, start_time=start_time),
                            VideoItem(path=video_node_2.path, start_time=start_time_2),
                        ],
                        effects=[],
                        duration=beat_segment.duration,
                    )
                )

            video_node = video_node.next

        return TimelineConfig(
            effects=[
                VideoSegmentEffect(
                    effect_type=EffectType.CROP,
                    method=EffectMethod.FIT_VIDEO_INTO_FRAME_SIZE,
                    args=[self.resolution.width, self.resolution.height],
                ),
                VideoSegmentEffect(effect_type=EffectType.ZOOM, method=EffectMethod.ZOOM_IN__ZOOM_OUT, args=[1.1]),
                VideoSegmentEffect(
                    effect_type=EffectType.FLASH, method=EffectMethod.FLASH, args=[0, 0.1, [255, 255, 255], False]
                ),
            ],
            segments=timeline_segments,
        )

    def load_timeline_config(self, config_path):
        logger.info(f"Load timeline config {config_path}")
        with open(config_path, "r") as f:
            return TimelineConfig.from_dict(value=yaml.safe_load(f))

    @staticmethod
    def get_video_start_time(video_node: VideoNode, beat_segment: BeatSegment):
        scene = random.choice(video_node.scenes)
        start_time = random.random() * (scene.duration - beat_segment.duration - 0.1)
        return start_time

    @staticmethod
    def get_file_name(path: str):
        return path.split("/")[-1]

    def prepare_dirs(self):
        shutil.rmtree(self.project_dir_path, ignore_errors=True)
        os.makedirs(self.project_dir_path)
        os.makedirs(self.temp_dir_path)
        os.makedirs(self.temp_analysis_dir_path)

    def store_analysis_to_temp(self, audio_analysis, video_analysis):
        for n in video_analysis:
            with open(f"{self.temp_analysis_dir_path}/video_{n.name}.json", "w") as f:
                f.write(json.dumps(n.to_json(), indent=4, sort_keys=False))

        with open(f"{self.temp_analysis_dir_path}/audio_{self.get_file_name(self.audio_path)}.json", "w") as f:
            f.write(json.dumps(audio_analysis.to_json(), indent=4, sort_keys=False))

    def store_timeline_config(self, config: TimelineConfig):
        with open(f"{self.project_dir_path}/timeline_config.yaml", "w") as f:
            f.write(yaml.dump(config.to_dict(), sort_keys=False, indent=2))

    @staticmethod
    def get_cache_key_from_path(path: str):
        return path.replace("/", "_").replace(" ", "_").replace(".", "_")
