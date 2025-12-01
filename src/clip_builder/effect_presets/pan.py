from typing import Literal
from moviepy import VideoClip

from src.clip_builder.effects.zoom_effects import EasingType, PanZoomEffectCriteria, pan_zoom_frame


def pan_side_to_side(clip: VideoClip, pan: tuple[int, int], easing: EasingType = "ease_out"):
    new_w = clip.w - pan[0]
    new_h = clip.h - pan[1]

    scale_x = clip.w / new_w
    scale_y = clip.h / new_h

    scale = max(scale_x, scale_y)

    pan_criteria = PanZoomEffectCriteria(
        start_pan_position=(-int(pan[0] / 2), -int(pan[1] / 2)),
        end_pan_position=(int(pan[0]), int(pan[1])),
        start_time=0,
        duration=clip.duration,
        easing=easing,
        start_zoom=scale,
        end_zoom=scale,
    )

    return pan_zoom_frame(clip, criteria=pan_criteria)
