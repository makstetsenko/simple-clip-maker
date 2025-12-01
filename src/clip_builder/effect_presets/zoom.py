from typing import Callable

from src.clip_builder.effects.zoom_effects import EasingType, PanZoomEffectCriteria, pan_zoom_frame


def zoom_in__fixed_zoom__zoom_out(
    clip_duration: float, clip_size: tuple[int, int], zoom_factor: float, zoom_in_duration: float
) -> list[Callable]:
    zoom_in_criteria = PanZoomEffectCriteria(
        start_zoom=1.0, end_zoom=zoom_factor, start_time=0, duration=zoom_in_duration, easing="ease_out"
    )

    middle_zoom = PanZoomEffectCriteria(
        start_zoom=zoom_factor,
        end_zoom=zoom_factor,
        start_time=zoom_in_duration,
        duration=clip_duration - 2.0 * zoom_in_duration,
        easing=None,
    )

    zoom_out_criteria = PanZoomEffectCriteria(
        start_zoom=zoom_factor,
        end_zoom=1.0,
        start_time=zoom_in_duration * 2.0,
        duration=zoom_in_duration,
        easing="ease_in",
    )

    return [
        pan_zoom_frame(clip_size, zoom_in_criteria),
        pan_zoom_frame(clip_size, middle_zoom),
        pan_zoom_frame(clip_size, zoom_out_criteria),
    ]


def zoom_in__zoom_out(clip_duration: float, clip_size: tuple[int, int], zoom_factor: float) -> list[Callable]:
    zoom_in_criteria = PanZoomEffectCriteria(
        start_zoom=1.0, end_zoom=zoom_factor, start_time=0, duration=clip_duration / 2.0, easing="ease_out"
    )

    zoom_out_criteria = PanZoomEffectCriteria(
        start_zoom=zoom_factor,
        end_zoom=1.0,
        start_time=clip_duration / 2.0,
        duration=clip_duration / 2.0,
        easing="ease_in",
    )

    return [pan_zoom_frame(clip_size, zoom_in_criteria), pan_zoom_frame(clip_size, zoom_out_criteria)]


def zoom_out__zoom_in(clip_duration: float, clip_size: tuple[int, int], zoom_factor: float) -> list[Callable]:
    zoom_in_criteria = PanZoomEffectCriteria(
        start_zoom=zoom_factor, end_zoom=1.0, start_time=0, duration=clip_duration / 2.0, easing="ease_out"
    )

    zoom_out_criteria = PanZoomEffectCriteria(
        start_zoom=1.0,
        end_zoom=zoom_factor,
        start_time=clip_duration / 2.0,
        duration=clip_duration / 2.0,
        easing="ease_in",
    )

    return [pan_zoom_frame(clip_size, zoom_in_criteria), pan_zoom_frame(clip_size, zoom_out_criteria)]


def zoom_in_at_clip_starts(
    clip_duration: float,
    clip_size: tuple[int, int],
    zoom_factor: float,
    zoom_duration: float,
    easing: EasingType = "ease_out",
) -> list[Callable]:

    zoom_in_criteria = PanZoomEffectCriteria(
        start_zoom=1.0, end_zoom=zoom_factor, start_time=0, duration=zoom_duration, easing=easing
    )

    static_zoom_criteria = PanZoomEffectCriteria(
        start_zoom=zoom_factor,
        end_zoom=zoom_factor,
        start_time=zoom_duration,
        duration=clip_duration - zoom_duration,
        easing=None,
    )

    return [pan_zoom_frame(clip_size, zoom_in_criteria), pan_zoom_frame(clip_size, static_zoom_criteria)]


def zoom_in_at_clip_ends(
    clip_duration: float,
    clip_size: tuple[int, int],
    zoom_factor: float,
    zoom_duration: float,
    easing: EasingType = "ease_out",
) -> list[Callable]:

    zoom_in_criteria = PanZoomEffectCriteria(
        start_zoom=1.0,
        end_zoom=zoom_factor,
        start_time=clip_duration - zoom_duration,
        duration=zoom_duration,
        easing=easing,
    )

    return [pan_zoom_frame(clip_size, zoom_in_criteria)]


def zoom_bump(
    clip_duration: float, clip_size: tuple[int, int], zoom_factor: float, bump_count: int, reverse: bool = False
):
    transforms = []
    bump_duration = clip_duration / bump_count

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

        transforms += [pan_zoom_frame(clip_size, zoom_in_criteria), pan_zoom_frame(clip_size, zoom_out_criteria)]

    return transforms
