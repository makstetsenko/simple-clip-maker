from typing import Callable
from moviepy import CompositeVideoClip, VideoClip


def apply_transformations(clip: VideoClip, frame_transformations: list[Callable]) -> VideoClip:
    def make_frame(get_frame, t):
        frame = get_frame(t)

        for f in frame_transformations:
            frame = f(frame, t)

        return frame

    return clip.transform(make_frame, apply_to=["mask", "audio"])


def apply_composition(clip: VideoClip, overlay_clips: list[VideoClip]) -> VideoClip:
    return CompositeVideoClip([clip] + overlay_clips, size=clip.size)
