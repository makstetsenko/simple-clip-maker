from typing import Literal
from moviepy import VideoClip

from src.clip_builder.effects.zoom_effects import EasingType, PanZoomEffectCriteria, pan_zoom_frame


def pan(clip: VideoClip, pan: tuple[int, int], easing: EasingType = "ease_out"):
    new_w = clip.w + pan[0] * 1.0
    new_h = clip.h + pan[1] * 1.0

    scale_x = new_w / clip.w
    scale_y = new_h / clip.h

    scale = max(scale_x, scale_y)

    pan_criteria = PanZoomEffectCriteria(
        start_pan_position=(-pan[0] // 4, -pan[1] // 4),
        end_pan_position=(pan[0] // 2, pan[1] // 2),
        start_time=0,
        duration=clip.duration,
        easing=easing,
        start_zoom=scale,
        end_zoom=scale,
    )

    return pan_zoom_frame(clip, criteria=pan_criteria)
