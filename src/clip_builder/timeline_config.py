from dataclasses import dataclass
from enum import Enum
from typing import Self


class EffectType(Enum):
    ZOOM = "zoom"
    PAN = "pan"
    FLASH = "flash"
    CROP = "crop"


class EffectMethod(Enum):
    # Zoom methods
    ZOOM_IN__ZOOM_OUT = "zoom_in__zoom_out"
    ZOOM_OUT__ZOOM_IN = "zoom_out__zoom_in"
    ZOOM_IN_AT_CLIP_STARTS = "zoom_in_at_clip_starts"
    ZOOM_IN_AT_CLIP_ENDS = "zoom_in_at_clip_ends"
    ZOOM_BUMP = "zoom_bump"

    # Pan methods
    PAN_SIDE_TO_SIDE = "pan_side_to_side"

    # Flash methods
    FLASH = "flash"
    BURST_FLASH = "burst_flash"

    # Crop methods
    LINE_CROP = "line_crop"
    BURST_LINE_CROP = "burst_line_crop"
    FIT_VIDEO_INTO_FRAME_SIZE = "fit_video_into_frame_size"


@dataclass
class VideoSegmentEffect:
    effect_type: EffectType | None
    method: EffectMethod | None
    args: list | None

    def to_dict(self) -> dict:
        if self.effect_type is None:
            raise Exception("VideoSegmentEffect: effect_type is None")

        if self.method is None:
            raise Exception("VideoSegmentEffect: method is None")

        return {
            "effect_type": self.effect_type.value,
            "method": self.method.value,
            "args": None if self.args is None else [a for a in self.args],
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

        return VideoSegmentEffect(
            effect_type=EffectType(effect_type_value),
            method=EffectMethod(method_value),
            args=[a for a in args_value] if args_value is not None else [],
        )


@dataclass
class VideoItem:
    path: str
    start_time: float

    def to_dict(self) -> dict:
        return {"path": self.path, "start_time": self.start_time}

    @staticmethod
    def from_dict(value: dict) -> Self:
        return VideoItem(
            path=value["path"],
            start_time=value["start_time"],
        )


@dataclass
class TimelineSegmentConfig:
    index: int
    effects: list[VideoSegmentEffect]
    duration: float
    videos: list[VideoItem]
    is_split_screen: bool

    def to_dict(self) -> dict:
        return {
            "index": self.index,
            "duration": self.duration,
            "is_split_screen": self.is_split_screen,
            "effects": [e.to_dict() for e in self.effects] if len(self.effects) > 0 else None,
            "videos": [v.to_dict() for v in self.videos],
        }

    @staticmethod
    def from_dict(value: dict) -> Self:
        effects = value.get("effects")
        return TimelineSegmentConfig(
            duration=value["duration"],
            index=value["index"],
            is_split_screen=value.get("is_split_screen", False),
            videos=[VideoItem.from_dict(j) for j in value["videos"]],
            effects=[VideoSegmentEffect.from_dict(j) for j in effects] if effects is not None else [],
        )


@dataclass
class TimelineConfig:
    effects: list[VideoSegmentEffect]
    segments: list[TimelineSegmentConfig]

    def to_dict(self) -> dict:
        return {
            "effects": [x.to_dict() for x in self.effects] if len(self.effects) > 0 else None,
            "segments": [x.to_dict() for x in self.segments],
        }

    @staticmethod
    def from_dict(value: dict) -> Self:
        segments = value.get("segments")

        if segments is None:
            raise Exception("TimelineConfig: segments list is required")

        return TimelineConfig(
            effects=[VideoSegmentEffect.from_dict(x) for x in value.get("effects", [])],
            segments=[TimelineSegmentConfig.from_dict(x) for x in segments],
        )
