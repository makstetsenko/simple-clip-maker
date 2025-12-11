from dataclasses import dataclass
from typing import Self

from src.clip_builder.effects_descriptor import EffectArgsBase, EffectMethod, EffectType, build_effect_args


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
        )


@dataclass
class TimelineConfig:
    effects: list[VideoSegmentEffect]
    segments: list[TimelineSegmentConfig]
    duration: float
    fps: int
    size: tuple[int, int]

    def to_dict(self) -> dict:
        return {
            "fps": self.fps,
            "size": list(self.size),
            "duration": self.duration,
            "effects": [x.to_dict() for x in self.effects] if len(self.effects) > 0 else None,
            "segments": [x.to_dict() for x in self.segments],
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
        )
