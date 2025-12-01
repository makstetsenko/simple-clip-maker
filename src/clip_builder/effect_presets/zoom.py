from typing import Literal
from moviepy import VideoClip

from src.clip_builder.effects.zoom_effects import EasingType, PanZoomEffectCriteria, pan_zoom_frame


def zoom_in__fixed_zoom__zoom_out(clip: VideoClip, zoom_factor: float, zoom_duration: float) -> VideoClip:
    zoom_in_criteria = PanZoomEffectCriteria(start_zoom=1.0, end_zoom=zoom_factor, start_time=0, duration=zoom_duration, easing="ease_out")

    middle_zoom = PanZoomEffectCriteria(
        start_zoom=zoom_factor,
        end_zoom=zoom_factor,
        start_time=zoom_duration,
        duration=clip.duration - 2.0 * zoom_duration,
        easing=None,
    )

    zoom_out_criteria = PanZoomEffectCriteria(
        start_zoom=zoom_factor,
        end_zoom=1.0,
        start_time=zoom_duration * 2.0,
        duration=zoom_duration,
        easing="ease_in",
    )

    clip: VideoClip = pan_zoom_frame(clip, zoom_in_criteria)
    clip: VideoClip = pan_zoom_frame(clip, middle_zoom)
    clip: VideoClip = pan_zoom_frame(clip, zoom_out_criteria)

    return clip


def zoom_in__zoom_out(clip: VideoClip, zoom_factor: float) -> VideoClip:
    zoom_in_criteria = PanZoomEffectCriteria(
        start_zoom=1.0, end_zoom=zoom_factor, start_time=0, duration=clip.duration / 2.0, easing="ease_out"
    )

    zoom_out_criteria = PanZoomEffectCriteria(
        start_zoom=zoom_factor,
        end_zoom=1.0,
        start_time=clip.duration / 2.0,
        duration=clip.duration / 2.0,
        easing="ease_in",
    )

    clip: VideoClip = pan_zoom_frame(clip, zoom_in_criteria)
    clip: VideoClip = pan_zoom_frame(clip, zoom_out_criteria)

    return clip


def zoom_out__zoom_in(clip: VideoClip, zoom_factor: float) -> VideoClip:
    zoom_in_criteria = PanZoomEffectCriteria(
        start_zoom=zoom_factor, end_zoom=1.0, start_time=0, duration=clip.duration / 2.0, easing="ease_out"
    )

    zoom_out_criteria = PanZoomEffectCriteria(
        start_zoom=1.0,
        end_zoom=zoom_factor,
        start_time=clip.duration / 2.0,
        duration=clip.duration / 2.0,
        easing="ease_in",
    )

    clip: VideoClip = pan_zoom_frame(clip, zoom_in_criteria)
    clip: VideoClip = pan_zoom_frame(clip, zoom_out_criteria)

    return clip


def zoom_in_at_clip_starts(clip: VideoClip, zoom_factor: float, zoom_duration: float, easing: EasingType = "ease_out") -> VideoClip:

    zoom_in_criteria = PanZoomEffectCriteria(start_zoom=1.0, end_zoom=zoom_factor, start_time=0, duration=zoom_duration, easing=easing)

    static_zoom_criteria = PanZoomEffectCriteria(
        start_zoom=zoom_factor, end_zoom=zoom_factor, start_time=zoom_duration, duration=clip.duration - zoom_duration, easing=None
    )

    clip: VideoClip = pan_zoom_frame(clip, zoom_in_criteria)
    clip: VideoClip = pan_zoom_frame(clip, static_zoom_criteria)

    return clip


def zoom_in_at_clip_ends(clip: VideoClip, zoom_factor: float, zoom_duration: float, easing: EasingType = "ease_out") -> VideoClip:

    zoom_in_criteria = PanZoomEffectCriteria(
        start_zoom=1.0, end_zoom=zoom_factor, start_time=clip.duration - zoom_duration, duration=zoom_duration, easing=easing
    )

    clip: VideoClip = pan_zoom_frame(clip, zoom_in_criteria)

    return clip
