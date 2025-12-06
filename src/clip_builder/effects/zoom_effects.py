from typing import Callable, Literal
from moviepy import VideoClip, CompositeVideoClip
import cv2
import math

EasingType = Literal["ease_in", "ease_out"]


class PanZoomEffectCriteria:
    def __init__(
        self,
        start_time: float,
        duration: float,
        easing: EasingType | None,
        start_zoom: float = 1.0,
        end_zoom: float = 1.5,
        start_pan_position: tuple[int, int] = (0, 0),
        end_pan_position: tuple[int, int] = (0, 0),
    ):
        self.start_zoom = start_zoom
        self.end_zoom = end_zoom
        self.start_pan_position = start_pan_position
        self.end_pan_position = end_pan_position
        self.duration = duration
        self.start_time = start_time
        self.easing: EasingType | None = easing


def pan_zoom_frame(clip: VideoClip, criteria: PanZoomEffectCriteria) -> VideoClip:
    video_width = clip.size[0]
    video_height = clip.size[1]

    start = criteria.start_time
    end = criteria.start_time + criteria.duration

    def make_frame(get_frame, t):
        frame = get_frame(t)
        if t < start or t >= end:
            return frame

        linear_progress = (t - start) / criteria.duration
        linear_progress = max(0.0, min(1.0, linear_progress))

        if criteria.easing == "ease_in":
            eased = 1 - math.cos((linear_progress * math.pi) / 2)
        elif criteria.easing == "ease_out":
            eased = math.sin(linear_progress * math.pi / 2)
        else:
            eased = linear_progress

        # zoom interpolation
        zoom = criteria.start_zoom + (criteria.end_zoom - criteria.start_zoom) * eased
        new_w = int(video_width / zoom)
        new_h = int(video_height / zoom)

        # pan interpolation
        pan_x = criteria.start_pan_position[0] + int(criteria.end_pan_position[0] * eased)
        pan_y = criteria.start_pan_position[1] + int(criteria.end_pan_position[1] * eased)

        # cropping box relative to center + pan
        x1 = (video_width - new_w) // 2 + pan_x
        y1 = (video_height - new_h) // 2 + pan_y
        x1, y1 = min(max(0, x1), video_width - new_w), min(max(0, y1), video_height - new_h)

        x2 = x1 + new_w
        y2 = y1 + new_h
        x2, y2 = min(video_width, x2), min(video_height, y2)

        cropped = frame[y1:y2, x1:x2]

        # resize back to original
        frame = cv2.resize(cropped, (video_width, video_height))
        return frame

    return clip.transform(make_frame, apply_to=["mask", "audio"])
