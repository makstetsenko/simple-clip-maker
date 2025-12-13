from moviepy import VideoClip

from ..effects.zoom_effects import EasingType, PanZoomEffectCriteria, pan_zoom_frame


def zoom_in__fixed_zoom__zoom_out(clip: VideoClip, zoom_factor: float, zoom_in_duration: float) -> VideoClip:
    zoom_in_criteria = PanZoomEffectCriteria(
        start_zoom=1.0, end_zoom=zoom_factor, start_time=0, duration=zoom_in_duration, easing="ease_out"
    )

    middle_zoom = PanZoomEffectCriteria(
        start_zoom=zoom_factor,
        end_zoom=zoom_factor,
        start_time=zoom_in_duration,
        duration=clip.duration - 2.0 * zoom_in_duration,
        easing=None,
    )

    zoom_out_criteria = PanZoomEffectCriteria(
        start_zoom=zoom_factor,
        end_zoom=1.0,
        start_time=zoom_in_duration * 2.0,
        duration=zoom_in_duration,
        easing="ease_in",
    )

    for criteria in [zoom_in_criteria, middle_zoom, zoom_out_criteria]:
        clip = pan_zoom_frame(clip, criteria)

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

    for criteria in [zoom_in_criteria, zoom_out_criteria]:
        clip = pan_zoom_frame(clip, criteria)

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

    for criteria in [zoom_out_criteria, zoom_in_criteria]:
        clip = pan_zoom_frame(clip, criteria)

    return clip


def zoom_in_at_clip_starts(
    clip: VideoClip,
    zoom_factor: float,
    zoom_duration: float,
    easing: EasingType = "ease_out",
) -> VideoClip:
    zoom_in_criteria = PanZoomEffectCriteria(
        start_zoom=1.0, end_zoom=zoom_factor, start_time=0, duration=zoom_duration, easing=easing
    )

    static_zoom_criteria = PanZoomEffectCriteria(
        start_zoom=zoom_factor,
        end_zoom=zoom_factor,
        start_time=zoom_duration,
        duration=clip.duration - zoom_duration,
        easing=None,
    )

    for criteria in [zoom_in_criteria, static_zoom_criteria]:
        clip = pan_zoom_frame(clip, criteria)

    return clip


def zoom_in_at_clip_ends(
    clip: VideoClip,
    zoom_factor: float,
    zoom_duration: float,
    easing: EasingType = "ease_out",
) -> VideoClip:
    zoom_in_criteria = PanZoomEffectCriteria(
        start_zoom=1.0,
        end_zoom=zoom_factor,
        start_time=clip.duration - zoom_duration,
        duration=zoom_duration,
        easing=easing,
    )

    return pan_zoom_frame(clip, zoom_in_criteria)


def zoom_bump(clip: VideoClip, zoom_factor: float, bump_count: int, reverse: bool = False):
    bump_duration = clip.duration / bump_count

    for i in range(bump_count):

        if reverse:

            zoom_out_criteria = PanZoomEffectCriteria(
                start_zoom=zoom_factor,
                end_zoom=1.0,
                start_time=i * bump_duration,
                duration=bump_duration / 2.0,
                easing="ease_out",
            )

            zoom_in_criteria = PanZoomEffectCriteria(
                start_zoom=1.0,
                end_zoom=zoom_factor,
                start_time=bump_duration * i + bump_duration / 2,
                duration=bump_duration / 2.0,
                easing="ease_in",
            )

        else:

            zoom_in_criteria = PanZoomEffectCriteria(
                start_zoom=1.0,
                end_zoom=zoom_factor,
                start_time=i * bump_duration,
                duration=bump_duration / 2.0,
                easing="ease_in",
            )

            zoom_out_criteria = PanZoomEffectCriteria(
                start_zoom=zoom_factor,
                end_zoom=1.0,
                start_time=bump_duration * i + bump_duration / 2,
                duration=bump_duration / 2.0,
                easing="ease_out",
            )

        for criteria in [zoom_in_criteria, zoom_out_criteria]:
            clip = pan_zoom_frame(clip, criteria)

    return clip
