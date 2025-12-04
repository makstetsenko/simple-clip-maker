from moviepy import ColorClip, VideoClip, vfx


def get_flash_clips(
    size: tuple[int, int], flashing_times: list[float], flash_duration, color: tuple[int, int, int] = (255, 255, 255)
) -> list[VideoClip]:
    clips = []
    for t in flashing_times:
        clips.append(
            ColorClip(
                size=size,
                color=color,
                duration=flash_duration,
            )
            .with_position((0, 0))
            .with_start(t)
            .with_effects(effects=[vfx.CrossFadeOut(flash_duration)])
        )
    return clips
