from typing import Callable
from moviepy import VideoClip


def apply_transformations(clip: VideoClip, frame_transformations: list[Callable]):
    for t in frame_transformations:
        clip = clip.transform(t, apply_to=["mask", "audio"])

    return clip
