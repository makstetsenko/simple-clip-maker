from typing import Self


class VideoResolution:
    def __init__(self, size: tuple[int, int]):
        self.size = size
        self.width = size[0]
        self.height = size[1]
        self.aspect_ration = size[0] / size[1]
        self.is_vertical = self.aspect_ration < 1
        self.is_near_square = abs(self.aspect_ration - 1) <= 0.02

    def matches_aspect_ratio(self, resolution: Self):
        return (resolution.aspect_ration >= 1 and self.aspect_ration >= 1) or (
            resolution.aspect_ration < 1 and self.aspect_ration < 1
        )
