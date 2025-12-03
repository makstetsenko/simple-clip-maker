from moviepy import ColorClip, VideoClip, vfx


def get_flash_clips(size: tuple[int, int], flashing_times: list[float], flash_duration) -> list[VideoClip]:
    clips = []
    for t in flashing_times:
        clips.append(
            ColorClip(
                size=size,
                duration=flash_duration,
            )
            .with_start(t)
            .with_effects(vfx.FadeOut(flash_duration))
        )
