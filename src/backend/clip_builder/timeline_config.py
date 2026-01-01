from dataclasses import dataclass
import logging
from typing import Self
import uuid

import yaml

from .effects_descriptor import EffectArgsBase, EffectMethod, EffectType, build_effect_args

logger = logging.getLogger(__name__)


@dataclass
class AudioSegment:
    index: int
    duration: float
    start_time: float
    end_time: float
    energy: float
    intensity_band: str
    energy_delta: float
    trend: str
    similar_group: int
    reverse_candidate: bool

    def to_dict(self):
        return {
            "index": self.index,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "energy": self.energy,
            "intensity_band": self.intensity_band,
            "energy_delta": self.energy_delta,
            "trend": self.trend,
            "similar_group": self.similar_group,
            "reverse_candidate": self.reverse_candidate,
        }

    @staticmethod
    def from_dict(value: dict):
        segment = AudioSegment(
            index=value["index"],
            start_time=value["start_time"],
            end_time=value["end_time"],
            duration=value["duration"],
            energy=value["energy"],
            intensity_band=value["intensity_band"],
            energy_delta=value["energy_delta"],
            trend=value["trend"],
            similar_group=value["similar_group"],
            reverse_candidate=value["reverse_candidate"],
        )
        return segment


@dataclass
class VideoSegmentEffect:
    id: str
    effect_type: EffectType | None
    method: EffectMethod | None
    args: EffectArgsBase | None

    def to_dict(self) -> dict:
        if self.effect_type is None:
            raise Exception("VideoSegmentEffect: effect_type is None")

        if self.method is None:
            raise Exception("VideoSegmentEffect: method is None")

        return {
            "id": self.id,
            "effect_type": self.effect_type.value,
            "method": self.method.value,
            "args": None if self.args is None else self.args.to_dict(),
        }

    @staticmethod
    def from_dict(value: dict) -> Self:
        effect_type_value = value.get("effect_type")
        method_value = value.get("method")
        args_value = value.get("args")

        if effect_type_value is None:
            raise Exception("VideoSegmentEffect: effect_type_value is None")

        if method_value is None:
            raise Exception("VideoSegmentEffect: method_value is None")
        effect_type = EffectType(effect_type_value)
        method = EffectMethod(method_value)
        return VideoSegmentEffect(
            id=value["id"],
            effect_type=effect_type,
            method=method,
            args=build_effect_args(effect_type, method, args_value) if args_value is not None else None,
        )


@dataclass
class VideoItem:
    id: str
    path: str
    start_time: float

    def to_dict(self) -> dict:
        return {"id": self.id, "path": self.path, "start_time": self.start_time}

    @staticmethod
    def from_dict(value: dict) -> Self:
        return VideoItem(
            id=value["id"],
            path=value["path"],
            start_time=value["start_time"],
        )


@dataclass
class TimelineSegmentConfig:
    id: str
    index: int
    effects: list[VideoSegmentEffect]
    duration: float
    videos: list[VideoItem]
    is_split_screen: bool
    start_time: float
    end_time: float
    etag: str
    
    start_frame: int
    end_frame: int
    duration_frame: int

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "index": self.index,
            "start_time": self.start_time,
            "duration": self.duration,
            "end_time": self.end_time,
            "is_split_screen": self.is_split_screen,
            "effects": [e.to_dict() for e in self.effects] if len(self.effects) > 0 else None,
            "videos": [v.to_dict() for v in self.videos],
            "etag": self.etag,
            "start_frame": self.start_frame,
            "end_frame": self.end_frame,
            "duration_frame": self.duration_frame,
        }

    @staticmethod
    def from_dict(value: dict, index: int) -> Self:
        effects = value.get("effects")

        return TimelineSegmentConfig(
            id=value["id"],
            index=index,
            start_time=value["start_time"],
            end_time=value["end_time"],
            duration=value["duration"],
            is_split_screen=value.get("is_split_screen", False),
            videos=[VideoItem.from_dict(j) for j in value["videos"]],
            effects=[VideoSegmentEffect.from_dict(j) for j in effects] if effects is not None else [],
            etag=value.get("etag"),
            start_frame=value.get("start_frame", 0),
            end_frame=value.get("end_frame", 0),
            duration_frame=value.get("duration_frame", 0)
        )


@dataclass
class TimelineConfig:
    effects: list[VideoSegmentEffect]
    segments: list[TimelineSegmentConfig]
    duration: float
    fps: int
    size: tuple[int, int]
    audio_segments: list[AudioSegment]

    def to_dict(self) -> dict:
        return {
            "fps": self.fps,
            "size": list(self.size),
            "duration": self.duration,
            "effects": [x.to_dict() for x in self.effects] if len(self.effects) > 0 else None,
            "segments": [x.to_dict() for x in self.segments],
            "audio_segments": [x.to_dict() for x in self.audio_segments],
        }

    @staticmethod
    def from_dict(value: dict) -> Self:
        segment_values = value.get("segments")

        if segment_values is None:
            raise Exception("TimelineConfig: segments list is required")

        timeline_duration = value["duration"]

        segments = []

        for i, v in enumerate(segment_values):
            segments.append(TimelineSegmentConfig.from_dict(v, index=i))

        return TimelineConfig(
            duration=timeline_duration,
            effects=[VideoSegmentEffect.from_dict(x) for x in value.get("effects", [])],
            segments=segments,
            fps=value["fps"],
            size=(value["size"][0], value["size"][1]),
            audio_segments=[AudioSegment.from_dict(x) for x in value.get("audio_segments", [])],
        )

    def save(self, path: str):
        with open(path, "w") as f:
            f.write(yaml.dump(self.to_dict(), sort_keys=False, indent=2))

    @staticmethod
    def load(path):
        logger.info(f"Load timeline config {path}")
        with open(path, "r") as f:
            return TimelineConfig.from_dict(value=yaml.safe_load(f))

    def copy_to_single_segment_timeline(self, segment_id: str):

        segment = [s for s in self.segments if s.id == segment_id][0]
        segment.start_time = 0
        segment.end_time = segment.duration
        segment.etag = str(uuid.uuid4())

        return TimelineConfig(
            effects=self.effects,
            duration=segment.duration,
            fps=self.fps,
            segments=[segment],
            size=self.size,
            audio_segments=self.audio_segments,
        )
