from moviepy import *
import random

color_presets = [(255, 255, 255), (255, 133, 255), (113, 233, 255)]


def crop_video(video_width, video_height, clip: VideoClip):
    clip_aspect = clip.w / clip.h
    aspect_ratio = video_width / video_height

    if clip_aspect < aspect_ratio:
        scaled_clip: VideoClip = clip.resized(width=video_width)
    else:
        scaled_clip: VideoClip = clip.resized(height=video_height)

    return scaled_clip.cropped(
        x_center=scaled_clip.w / 2,
        y_center=scaled_clip.h / 2,
        width=video_width,
        height=video_height,
    )


def set_clip_position(
    video_width,
    video_height,
    clip: VideoClip,
    position: tuple[int, int],
    position_layout: tuple[int, int],
    offset_x: int = 0,
    offset_y: int = 0,
    scale_factor: float = 1.0,
) -> VideoClip:
    cols, rows = position_layout

    cell_width = int(video_width / cols)
    cell_height = int(video_height / rows)

    clip_width = int(cell_width * scale_factor)
    clip_height = int(cell_height * scale_factor)

    if clip_width > clip_height:
        scaled_clip: VideoClip = clip.resized(width=clip_width)
    else:
        scaled_clip: VideoClip = clip.resized(height=clip_height)

    cropped_clip = scaled_clip.cropped(
        x_center=max(scaled_clip.w, clip_width) / 2,
        y_center=max(scaled_clip.h, clip_height) / 2,
        width=clip_width,
        height=clip_height,
    )

    p_col, p_row = position

    clip_x = int((p_col - 1) * cell_width) + (cell_width - cropped_clip.w) // 2 + offset_x  # top left corner
    clip_y = int((p_row - 1) * cell_height) + (cell_height - cropped_clip.h) // 2 + offset_y  # top left corner

    return cropped_clip.with_position((clip_x, clip_y))


class SplitScreenCriteria:
    def __init__(
        self,
        clip: VideoClip,
        position: tuple[int, int] | None = None,
        scale_factor: float = 1,
    ):
        self.clip = clip
        self.position = position
        self.scale_factor = scale_factor


def get_positions_from_layout(position_layout: tuple[int, int]):
    cols, rows = position_layout

    positions = []

    for r in range(1, rows + 1):
        for c in range(1, cols + 1):
            positions.append((c, r))

    return positions


def split_screen_clips(
    video_width,
    video_height,
    clips_criteria: list[SplitScreenCriteria],
    position_layout: tuple[int, int],
    clips_margin: int = 0,
    clip_duration: float | None = None,
):
    default_positions = get_positions_from_layout(position_layout)

    positioned_clips = []
    for i, clip_criteria in enumerate(clips_criteria):
        clip_position = clip_criteria.position if clip_criteria.position != None else default_positions[i]

        pos_clip = set_clip_position(
            clip=clip_criteria.clip,
            position=clip_position,
            position_layout=position_layout,
            video_height=video_height,
            video_width=video_width,
            scale_factor=clip_criteria.scale_factor,
        )
        positioned_clips.append(pos_clip)

    duration = clips_criteria[0].clip.duration if clip_duration == None else clip_duration

    return CompositeVideoClip(
        clips=positioned_clips,
        size=(video_width, video_height),
        bg_color=random.choice(color_presets),
    ).with_duration(duration)
