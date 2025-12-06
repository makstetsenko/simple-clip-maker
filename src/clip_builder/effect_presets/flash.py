from moviepy import CompositeVideoClip, VideoClip
from src.clip_builder.effects.flash import get_flash_clips as get_flash_clips_effect
import random


def pick_random_color() -> tuple[int, int, int]:
    return (
        random.randint(65, 255),
        random.randint(65, 255),
        random.randint(65, 255),
    )


def flash(
    clip: VideoClip,
    time: float,
    flash_duration: float,
    color: tuple[int, int, int] = (255, 255, 255),
    pick_random_flash_color: bool = False,
) -> VideoClip:
    if pick_random_flash_color:
        flash_color = pick_random_color()
    else:
        flash_color = color

    return CompositeVideoClip(
        clips=[clip]
        + get_flash_clips_effect(clip.size, flashing_times=[time], flash_duration=flash_duration, color=flash_color)
    )


def burst_flash(
    clip: VideoClip,
    flashes_count: int,
    color: tuple[int, int, int] = (255, 255, 255),
    pick_random_flash_color: bool = False,
) -> VideoClip:
    sub_duration = clip.duration / flashes_count
    flashing_times = []
    for i in range(flashes_count):
        flashing_times.append(i * sub_duration)

    if pick_random_flash_color:
        flash_color = pick_random_color()
    else:
        flash_color = color

    return CompositeVideoClip(
        clips=[clip]
        + get_flash_clips_effect(
            clip.size, flashing_times=flashing_times, flash_duration=sub_duration / 3.0, color=flash_color
        )
    )
