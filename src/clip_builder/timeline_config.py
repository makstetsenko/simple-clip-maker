from dataclasses import dataclass
from typing import Self


@dataclass
class VideoSegmentEffect:
    def to_dict(self) -> dict:
        return {}

    @staticmethod
    def from_dict(value: dict) -> Self:
        return VideoSegmentEffect()


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
            "effects": [e.to_dict() for e in self.effects],
            "videos": [v.to_dict() for v in self.videos],
        }

    @staticmethod
    def from_dict(value: dict) -> Self:
        return TimelineSegmentConfig(
            duration=value["duration"],
            index=value["index"],
            is_split_screen=value["is_split_screen"],
            videos=[VideoItem.from_dict(j) for j in value["videos"]],
            effects=[VideoSegmentEffect.to_dict(j) for j in value["effects"]],
        )


@dataclass
class TimelineConfig:
    effects: list[VideoSegmentEffect]
    segments: list[TimelineSegmentConfig]

    def to_dict(self) -> dict:
        return {
            "effects": [x.to_dict() for x in self.effects],
            "segments": [x.to_dict() for x in self.segments],
        }

    @staticmethod
    def from_dict(value: dict) -> Self:
        return VideoSegmentEffect(
            effects=[VideoSegmentEffect.to_dict(x) for x in value["effects"]],
            segments=[TimelineSegmentConfig.to_dict(x) for x in value["segments"]],
        )
