from moviepy import VideoClip, CompositeVideoClip
import cv2
import math

def bump_zoom_on_time_stops(clip: VideoClip, time_stops: list[float], video_resolution: tuple[int,int], bump_duration_seconds: float = 0.25, zoom_amount_percent: int = 10):

    video_width, video_height = video_resolution

    def make_frame(get_frame, t):
        frame = get_frame(t)  # safe reference to underlying clip
        for time_stop in time_stops:
            time_diff = t - time_stop
            if 0 <= time_diff <= bump_duration_seconds:
                progress = time_diff / bump_duration_seconds
                bump = (1 - progress) ** 2  # ease-out
                scale = 1 - bump * zoom_amount_percent / 100

                w_crop = int(video_width * scale)
                h_crop = int(video_height * scale)
                x1 = (video_width - w_crop) // 2
                y1 = (video_height - h_crop) // 2
                x2 = x1 + w_crop
                y2 = y1 + h_crop

                # crop + resize only the current frame
                cropped = frame[y1:y2, x1:x2]
                # resize back to original resolution
                frame = cv2.resize(cropped, (video_width, video_height))
                break
        return frame

    return clip.transform(lambda get_frame, t: make_frame(get_frame, t), apply_to=["mask", "audio"])

    
class PanZoomEffectCriteria:
    def __init__(self, start_zoom: int = 1.0, end_zoom: int = 1.5, pan: tuple[int,int] = (0, 0)):
        self.start_zoom = start_zoom
        self.end_zoom = end_zoom
        self.pan = pan


def pan_zoom_frame(clip: VideoClip, criteria: PanZoomEffectCriteria = PanZoomEffectCriteria()):        
    video_width = clip.w
    video_height = clip.h

    def make_frame(get_frame, t):
        frame = get_frame(t)

        progress = math.sqrt(4.0 * t / clip.duration)

        # zoom interpolation
        zoom = criteria.start_zoom + (criteria.end_zoom - criteria.start_zoom) * progress
        new_w = int(video_width / zoom)
        new_h = int(video_height / zoom)

        # pan interpolation
        pan_x = int(criteria.pan[0] * progress)
        pan_y = int(criteria.pan[1] * progress)

        # cropping box relative to center + pan
        x1 = (video_width - new_w) // 2 + pan_x
        y1 = (video_height - new_h) // 2 + pan_y
        x2 = x1 + new_w
        y2 = y1 + new_h

        # clip to valid bounds
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(video_width, x2), min(video_height, y2)

        cropped = frame[y1:y2, x1:x2]

        # resize back to original
        frame = cv2.resize(cropped, (video_width, video_height))
        return frame

    return clip.transform(make_frame, apply_to=["mask", "audio"])
    