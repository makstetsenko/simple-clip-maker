from moviepy import ColorClip, CompositeVideoClip, VideoClip
from ..effects.crop import line_crop as line_crop_effect


def line_crop(clip: VideoClip, line_number, total_lines, is_vertical: bool) -> VideoClip:
    return CompositeVideoClip(
        clips=[
            ColorClip(size=clip.size, duration=clip.duration, color=(0, 0, 0)),
            line_crop_effect(clip, line_number, total_lines, is_vertical),
        ]
    )


def burst_line_crop(clip: VideoClip, total_lines, is_vertical: bool, reverse_ordering: bool = False) -> VideoClip:
    sub_clips = []
    sub_duration = clip.duration / total_lines

    for i in range(total_lines):
        start_time = (total_lines - i - 1) * sub_duration if reverse_ordering else i * sub_duration
        c: VideoClip = clip.subclipped(start_time=start_time, end_time=start_time + sub_duration).with_start(start_time)
        sub_clips.append(line_crop_effect(c, i + 1, total_lines, is_vertical))

    return CompositeVideoClip(clips=[ColorClip(size=clip.size, duration=clip.duration, color=(0, 0, 0))] + sub_clips)
