from typing import Callable
from moviepy import CompositeVideoClip, VideoClip


def apply_transformations(clip: VideoClip, frame_transformations: list[Callable]) -> VideoClip:
    for t in frame_transformations:
        clip = clip.transform(t, apply_to=["mask", "audio"])

    return clip


def apply_composition(clip: VideoClip, overlay_clips: list[VideoClip]) -> VideoClip:
    return CompositeVideoClip([clip] + overlay_clips)
