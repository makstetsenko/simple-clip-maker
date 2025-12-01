from src.clip_builder.effects.zoom_effects import EasingType, PanZoomEffectCriteria, pan_zoom_frame


def pan_side_to_side(
    clip_duration: float, clip_size: tuple[int, int], pan: tuple[int, int], easing: EasingType = "ease_out"
):
    new_w = clip_size[0] - pan[0]
    new_h = clip_size[1] - pan[1]

    scale_x = clip_size[0] / new_w
    scale_y = clip_size[1] / new_h

    scale = max(scale_x, scale_y)

    pan_criteria = PanZoomEffectCriteria(
        start_pan_position=(-int(pan[0] / 2), -int(pan[1] / 2)),
        end_pan_position=(int(pan[0]), int(pan[1])),
        start_time=0,
        duration=clip_duration,
        easing=easing,
        start_zoom=scale,
        end_zoom=scale,
    )

    return [pan_zoom_frame(clip_size, criteria=pan_criteria)]
