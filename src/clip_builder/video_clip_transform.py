from moviepy import *
import random

color_presets = [
    (255,255,255),
    (255, 133, 255),
    (113, 233, 255)
]

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
        height=video_height
    )
    
    
def set_clip_position(video_width, video_height, clip: VideoClip, position: tuple[int,int], max_position: tuple[int,int], offset_x:int=0, offset_y:int=0) -> VideoClip:
    cols, rows = max_position
    
    clip_width = int(video_width / cols)
    clip_height = int(video_height / rows)
    
    if clip_width > clip_height:
        scaled_clip: VideoClip = clip.resized(width=clip_width)
    else:
        scaled_clip: VideoClip = clip.resized(height=clip_height)
    
    cropped_clip = scaled_clip.cropped(
        x_center=max(scaled_clip.w, clip_width) / 2,
        y_center=max(scaled_clip.h, clip_height) / 2,
        width=clip_width,
        height=clip_height
    )
    
    p_col, p_row = position

    clip_x = int((p_col - 1) * clip_width) + (clip_width - cropped_clip.w) // 2 + offset_x # top left corner
    clip_y = int((p_row - 1) * clip_height) + (clip_height - cropped_clip.h) // 2 + offset_y # top left corner
    
    return cropped_clip.with_position((clip_x, clip_y))


def split_screen_clips(video_width, video_height, clips: list[VideoClip], max_position: tuple[int,int], manual_positions: list[tuple[int,int]] | None = None, clips_margin: int = 0, clip_duration: float | None = None):
    cols, rows = max_position
    
    positions = []
    
    if manual_positions == None:
        for r in range(1, rows + 1):
            for c in range(1, cols + 1):
                positions.append((c, r))
    else:
        positions = manual_positions
    
    positioned_clips = []
    for i, c in enumerate(clips):
        pos_clip = set_clip_position(clip=c, position=positions[i], max_position=max_position, video_height=video_height, video_width=video_width)
        positioned_clips.append(pos_clip)
        
    duration = clips[0].duration if clip_duration == None else clip_duration
    
    return CompositeVideoClip(
        clips=positioned_clips, 
        size=(video_width, video_height),
        bg_color=random.choice(color_presets),
    ).with_duration(duration)
    