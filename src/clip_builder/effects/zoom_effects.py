from moviepy import VideoClip


def ease_out_zoom_on_time_stops(frame_time, clip: VideoClip, time_stops: list[float], video_resolution: tuple[int,int], bump_duration_seconds: float = 0.25, zoom_amount_percent: int = 10):
    video_width, video_height = video_resolution
    
    for time_stop in time_stops:
        time_diff = frame_time - time_stop
        if 0 <= time_diff <= bump_duration_seconds:
            progress = time_diff / bump_duration_seconds
            bump = (1 - progress) ** 2  # ease-out
            scale = 1 - 1.0 * bump * zoom_amount_percent / 100
            w_crop = int(video_width * scale)
            h_crop = int(video_height * scale)
            x1 = (video_width - w_crop) // 2
            y1 = (video_height - h_crop) // 2
            x2 = x1 + w_crop
            y2 = y1 + h_crop
            return clip.cropped(x1=x1, y1=y1, x2=x2, y2=y2).resized((video_width, video_height)).get_frame(frame_time)
        
    return clip.get_frame(frame_time)


def pan_zoom_frame(frame_time: float, clip: VideoClip, video_resolution: tuple[int,int], start_zoom: int = 1.0, end_zoom: int = 1.1, pan: tuple[int,int] = (50, 0)):    
    video_width, video_height = video_resolution
    
    progress = min(frame_time / clip.duration, 1)
    
    # Easing function (smooth in/out)
    ease = 3 * progress**2 - 2 * progress**3

    # Interpolate zoom and pan
    zoom = start_zoom + (end_zoom - start_zoom) * ease
    pan_x = int(pan[0] * ease)
    pan_y = int(pan[1] * ease)

    # Compute crop area
    crop_w = video_width // zoom
    crop_h = video_height // zoom

    x_center = video_width // 2 + pan_x
    y_center = video_height // 2 + pan_y

    return clip.cropped(x_center=x_center,y_center=y_center,width=crop_w,height=crop_h).resized((video_width, video_height)).get_frame(frame_time)

