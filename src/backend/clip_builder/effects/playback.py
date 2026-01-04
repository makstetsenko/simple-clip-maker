from moviepy import VideoClip, vfx, concatenate_videoclips


def ramp_speed(
    clip: VideoClip,
    start_speed: float = 1.0,
    end_speed: float = 0.0,
    ramps: int = 5,
    scale_speed_to_original_duration: bool = False,
) -> VideoClip:
    sub_duration = 1.0 * clip.duration / ramps
    speed_diff = 1.0 * (start_speed - end_speed) / ramps

    clips = []

    for i in range(ramps):
        clips.append(
            clip[i * sub_duration : i * sub_duration + sub_duration].with_speed_scaled(
                factor=start_speed - (i * speed_diff)
            )
        )

    res = concatenate_videoclips(clips=clips, method="compose")

    if scale_speed_to_original_duration:
        res = res.with_speed_scaled(final_duration=clip.duration)
    else:
        # just cut extra duration
        res = res.with_duration(clip.duration)

    return res


def forward_reverse(clip: VideoClip, start_speed: float = 1.0, fast_slow_mode: bool = True) -> VideoClip:
    sub_duration = clip.duration / 2.0
    sub_clip: VideoClip = clip.with_speed_scaled(final_duration=sub_duration)

    if fast_slow_mode:
        sub_clip = ramp_speed(
            sub_clip, start_speed=start_speed, end_speed=0.1, ramps=5, scale_speed_to_original_duration=False
        )

    return concatenate_videoclips(
        clips=[
            sub_clip,
            sub_clip.with_effects(effects=[vfx.TimeMirror()]),
        ],
        method="compose",
    ).with_duration(clip.duration)


def ramp_speed_segments(
    clip: VideoClip,
    speeds: list[float] = [1, 0],
    ramps_count_between_speed: int = 5,
    scale_speed_to_original_duration: bool = False,
) -> VideoClip:
    sub_duration = clip.duration / (len(speeds) - 1)

    clips = []

    for i in range(len(speeds) - 1):
        start_speed = speeds[i]
        end_speed = speeds[i + 1]

        sub_clip = clip[i * sub_duration : i * sub_duration + sub_duration]

        clips.append(ramp_speed(sub_clip, start_speed, end_speed, ramps_count_between_speed))

    res = concatenate_videoclips(clips, method="compose")

    if scale_speed_to_original_duration:
        res = res.with_speed_scaled(final_duration=clip.duration)
    else:
        # just cut extra duration
        res = res.with_duration(clip.duration)

    return res
