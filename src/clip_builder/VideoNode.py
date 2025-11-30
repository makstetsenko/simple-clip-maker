from typing import Callable, Self
from src.clip_builder.VideoResolution import VideoResolution
from src.clip_builder.video_analyzer import SceneInfo


class VideoNode:
    def __init__(self, path: str, scenes: list[SceneInfo], resolution: VideoResolution, fps: int):
        self.path: str = path
        self.name: str = path.split("/")[-1]
        self.scenes: list[SceneInfo] = scenes
        self.resolution: VideoResolution = resolution
        self.fps: int = fps
        self.next = None

    def find_next(self, predicate: Callable[[Self], bool]) -> Self:  # type: ignore
        current: VideoNode = self.next
        path = self.path

        while current.path != path:
            if predicate(current):
                return current
            current = current.next

        return self

    def to_json(self):
        return {
            "path": self.path,
            "resolution": self.resolution.resolution,
            "fps": self.fps,
            "scenes": [s.to_json() for s in self.scenes],
        }

    @staticmethod
    def from_json(value: dict):
        return VideoNode(
            path=value["path"],
            resolution=VideoResolution(value["resolution"]),
            fps=value["fps"],
            scenes=[SceneInfo.from_json(s) for s in value["scenes"]],
        )
