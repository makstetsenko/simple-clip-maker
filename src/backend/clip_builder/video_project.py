import datetime
import glob
import json
import logging
import os
import random
import shutil
from typing import Self
import uuid
import subprocess
import pathlib


import yaml
from moviepy import VideoFileClip

from .data_analysis.audio_analyzer import (
    BeatSegment,
    analyze_music_for_editing,
    AudioAnalyzeResult,
)
from .data_analysis.video_analyzer import (
    analyze_on_static_scenes,
    video_details,
    SceneInfo,
)
from .json_cache import JsonCache
from .timeline_config import (
    AudioSegment,
    TimelineConfig,
    TimelineSegmentConfig,
    VideoItem,
    VideoSegmentEffect,
    EffectType,
    EffectMethod,
)
from .video_clip_builder import VideoClipBuilder
from .video_node import VideoNode
from .video_resolution import VideoResolution
from .effects_descriptor import EffectArgs

logger = logging.getLogger(__name__)

audio_exts = ["mp3", "m4a"]
video_exts = ["m4v", "mov", "mp4"]


def get_path_templates(input_dir_path: str, file_ext: list[str]):
    path_prefix = input_dir_path.rstrip("/") + "/*."
    return [path_prefix + x for x in file_ext] + [path_prefix + x.upper() for x in file_ext]


def get_path_list(input_dir_path, file_ext: list[str]) -> str | None:
    timeline_config_path_templates = get_path_templates(input_dir_path, file_ext)

    path_list = []
    for t in timeline_config_path_templates:
        for g in glob.glob(t):
            path_list.append(g)

    return path_list


def get_first_path(input_dir_path, file_ext: list[str]) -> str | None:
    path_list = get_path_list(input_dir_path, file_ext)
    return None if len(path_list) == 0 else path_list[0]


class VideoProjectSetup:
    setup_dir_path = f"./output/setups"

    def __init__(
        self,
        resolution: tuple[int, int],
        fps: int,
        project_name: str | None = None,
        source_files_dir_path: str | None = None,
    ):
        self.project_name = (
            datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") if project_name is None else project_name
        )

        self.resolution = VideoResolution(resolution)
        self.fps = fps

        self.project_dir_path = f"./output/projects/{self.project_name}"
        self.runtime_dir_path = f"{self.project_dir_path}/runtime"
        self.analysis_dir_path = f"{self.project_dir_path}/analysis"
        self.timeline_path = f"{self.project_dir_path}/timeline.yaml"
        self.source_files_dir_path = (
            f"{self.project_dir_path}/source" if source_files_dir_path is None else source_files_dir_path
        )

        self.audio_path = get_first_path(self.source_files_dir_path, audio_exts)
        self.videos_path_list = get_path_list(self.source_files_dir_path, video_exts)

    def setup_dirs(self):
        shutil.rmtree(self.project_dir_path, ignore_errors=True)
        os.makedirs(self.project_dir_path)
        os.makedirs(self.runtime_dir_path)
        os.makedirs(self.analysis_dir_path)
        os.makedirs(self.source_files_dir_path, exist_ok=True)
        os.makedirs(self.setup_dir_path, exist_ok=True)

    def clear_runtime_dirs(self):
        shutil.rmtree(self.runtime_dir_path, ignore_errors=True)
        os.makedirs(self.runtime_dir_path)

    @staticmethod
    def get_setup_config_path(project_name: str) -> str:
        return f"{VideoProjectSetup.setup_dir_path}/{project_name}.yaml"

    def to_dict(self) -> dict:
        return {
            "project_name": self.project_name,
            "fps": self.fps,
            "resolution": [self.resolution.width, self.resolution.height],
        }

    @staticmethod
    def from_dict(value: dict) -> Self:
        resolution = value["resolution"]

        return VideoProjectSetup(
            resolution=(resolution[0], resolution[1]),
            fps=value["fps"],
            project_name=value["project_name"],
        )

    def save(self):
        setup_config_path = VideoProjectSetup.get_setup_config_path(self.project_name)
        with open(setup_config_path, "w") as f:
            f.write(yaml.safe_dump(self.to_dict(), indent=4, sort_keys=False))

    @staticmethod
    def load(project_name: str) -> Self:
        setup_config_path = VideoProjectSetup.get_setup_config_path(project_name)
        with open(setup_config_path, "r") as f:
            value = yaml.safe_load(f)
            return VideoProjectSetup.from_dict(value)


class VideoProject:
    def __init__(
        self,
        resolution: tuple[int, int] | None = None,
        fps: int | None = None,
        source_files_dir_path: str | None = None,
        project_setup: VideoProjectSetup | None = None,
    ):

        self.setup = (
            VideoProjectSetup(
                project_name=None,
                fps=fps,
                resolution=resolution,
                source_files_dir_path=source_files_dir_path,
            )
            if project_setup is None
            else project_setup
        )

        self.json_cache: JsonCache = JsonCache()

        if project_setup is None:
            self.setup.setup_dirs()

    def get_clip_builder(self) -> VideoClipBuilder:
        return VideoClipBuilder(
            fps=self.setup.fps,
            resolution=self.setup.resolution,
            temp_path=self.setup.runtime_dir_path,
        )

    def save_clip_with_audio(self, clip_path) -> str:
        output_clip_path = str(
            pathlib.Path(self.setup.project_dir_path).joinpath(f"output-{str(uuid.uuid4())}.mp4").resolve()
        )
        clip_full_path = str(pathlib.Path(clip_path).resolve())
        audio_full_path = str(pathlib.Path(self.setup.audio_path).resolve())

        logger.info(f"Saving clip {output_clip_path}")

        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                clip_full_path,
                "-i",
                audio_full_path,
                "-map",
                "0:v:0",
                "-map",
                "1:a:0",
                "-c:v",
                "copy",  # no re-encode video
                "-c:a",
                "aac",
                "-shortest",
                output_clip_path,
            ],
            check=True,
        )

        return output_clip_path

    def get_audio_analysis(self) -> AudioAnalyzeResult:
        logger.info(f"Analyzing audio {self.get_file_name(self.setup.audio_path)}")

        cache_key = self.get_cache_key_from_path(self.setup.audio_path)
        cached_value = self.json_cache.get(cache_key)

        if cached_value is None:
            analysis = analyze_music_for_editing(self.setup.audio_path, similarity_threshold=0.6)

            self.json_cache.set(cache_key, analysis.to_json())

            return analysis

        return AudioAnalyzeResult.from_json(cached_value)

    def get_video_analysis(self) -> list[VideoNode]:
        res: list[VideoNode] = []

        for i, p in enumerate(self.setup.videos_path_list):
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

    def analyze_source_and_generate_timeline(self) -> TimelineConfig:
        audio_analysis = self.get_audio_analysis()
        video_analysis = self.get_video_analysis()

        self.store_analysis_to_temp(audio_analysis, video_analysis)

        video_node = video_analysis[0]

        timeline_segments = []
        audio_segments: list[AudioSegment] = []
        for beat_segment in audio_analysis.beat_segments:
            start_time = self.get_video_start_time(video_node, beat_segment)

            audio_segments.append(
                AudioSegment(
                    index=beat_segment.index,
                    duration=beat_segment.duration,
                    start_time=beat_segment.start_time,
                    end_time=beat_segment.end_time,
                    energy=beat_segment.energy,
                    intensity_band=beat_segment.intensity_band,
                    energy_delta=beat_segment.energy_delta,
                    trend=beat_segment.trend,
                    similar_group=beat_segment.similar_group,
                    reverse_candidate=beat_segment.reverse_candidate,
                )
            )

            if video_node.resolution.matches_aspect_ratio(self.setup.resolution):

                timeline_segments.append(
                    TimelineSegmentConfig(
                        id=str(uuid.uuid4()),
                        index=beat_segment.index,
                        is_split_screen=False,
                        videos=[VideoItem(id=str(uuid.uuid4()), path=video_node.path, start_time=start_time)],
                        effects=[],
                        duration=beat_segment.duration,
                        start_time=beat_segment.start_time,
                        end_time=beat_segment.end_time,
                        etag=str(uuid.uuid4()),
                    )
                )
            else:
                video_node_2 = video_node.find_next(lambda v: v.resolution.matches_aspect_ratio(video_node.resolution))
                start_time_2 = self.get_video_start_time(video_node_2, beat_segment)

                timeline_segments.append(
                    TimelineSegmentConfig(
                        id=str(uuid.uuid4()),
                        index=beat_segment.index,
                        is_split_screen=True,
                        videos=[
                            VideoItem(id=str(uuid.uuid4()), path=video_node.path, start_time=start_time),
                            VideoItem(id=str(uuid.uuid4()), path=video_node_2.path, start_time=start_time_2),
                        ],
                        effects=[],
                        duration=beat_segment.duration,
                        start_time=beat_segment.start_time,
                        end_time=beat_segment.end_time,
                        etag=str(uuid.uuid4()),
                    )
                )

            video_node = video_node.next

        return TimelineConfig(
            size=self.setup.resolution.size,
            fps=self.setup.fps,
            duration=timeline_segments[-1].end_time,
            segments=timeline_segments,
            audio_segments=audio_segments,
            effects=[
                VideoSegmentEffect(
                    id=str(uuid.uuid4()),
                    effect_type=EffectType.CROP,
                    method=EffectMethod.FIT_VIDEO_INTO_FRAME_SIZE,
                    args=None,
                ),
                VideoSegmentEffect(
                    id=str(uuid.uuid4()),
                    effect_type=EffectType.ZOOM,
                    method=EffectMethod.ZOOM_IN_AT_CLIP_STARTS,
                    args=EffectArgs.ZOOM.ZOOM_IN_AT_CLIP_STARTS(zoom_factor=1.3, zoom_duration=0.1),
                ),
                VideoSegmentEffect(
                    id=str(uuid.uuid4()),
                    effect_type=EffectType.FLASH,
                    method=EffectMethod.FLASH,
                    args=EffectArgs.FLASH.FLASH(time=0, flash_duration=0.06, color=(255, 255, 255)),
                ),
            ],
        )

    @staticmethod
    def get_video_start_time(video_node: VideoNode, beat_segment: BeatSegment):
        if len(video_node.scenes) > 0:
            scene: SceneInfo = random.choice(video_node.scenes)
            start_time = random.random() * (scene.end_time - beat_segment.duration - 0.1)
            return start_time
        return 0

    @staticmethod
    def get_file_name(path: str):
        return path.split("/")[-1]

    def store_analysis_to_temp(self, audio_analysis, video_analysis):
        for n in video_analysis:
            with open(f"{self.setup.analysis_dir_path}/video_{n.name}.json", "w") as f:
                f.write(json.dumps(n.to_json(), indent=4, sort_keys=False))

        with open(f"{self.setup.analysis_dir_path}/audio_{self.get_file_name(self.setup.audio_path)}.json", "w") as f:
            f.write(json.dumps(audio_analysis.to_json(), indent=4, sort_keys=False))

    @staticmethod
    def get_cache_key_from_path(path: str):
        return path.replace("/", "_").replace(" ", "_").replace(".", "_")
