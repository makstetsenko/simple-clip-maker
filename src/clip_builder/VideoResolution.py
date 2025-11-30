from typing import Self


class VideoResolution:
    def __init__(self, resolution: tuple[int, int]):
        self.resolution = resolution
        self.width = resolution[0]
        self.height = resolution[1]
        self.aspect_ration = resolution[0] / resolution[1]
        self.is_vertical = self.aspect_ration < 1
        self.is_near_square = abs(self.aspect_ration - 1) <= 0.02

    def matches_aspect_ratio(self, resolution: Self):
        return (resolution.aspect_ration >= 1 and self.aspect_ration >= 1) or (resolution.aspect_ration < 1 and self.aspect_ration < 1)
