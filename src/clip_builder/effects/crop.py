from moviepy import VideoClip


def fit_video_into_frame_size(size: tuple[int, int], clip: VideoClip):
    video_width, video_height = size

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


def crop(clip: VideoClip, top_left_point: tuple[int, int], size: tuple[int, int]):
    return clip.cropped(
        x1=top_left_point[0],
        y1=top_left_point[1],
        x2=top_left_point[0] + size[0],
        y2=top_left_point[1] + size[1],
    )


def line_crop(clip: VideoClip, line_number: int, total_lines: int, is_vertical_line: bool):

    if is_vertical_line:
        offset = clip.w / total_lines * (line_number - 1)
        crop_w = clip.w / total_lines
        crop_h = clip.w

        return crop(clip, top_left_point=(offset, 0), size=(crop_w, crop_h))

    offset = clip.h / total_lines * (line_number - 1)
    crop_w = clip.w
    crop_h = clip.h / total_lines

    return crop(clip, top_left_point=(0, offset), size=(crop_w, crop_h))
