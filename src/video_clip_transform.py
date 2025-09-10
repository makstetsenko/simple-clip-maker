from moviepy import *

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
    
    
def set_clip_position(video_width, video_height, clip: VideoClip, position: tuple[int,int], max_position: tuple[int,int]) -> VideoClip:
    clip_aspect = clip.w / clip.h
    aspect_ratio = video_width / video_height
    
    rows, cols = max_position
    
    clip_width = int(video_width / rows)
    clip_height = int(video_height / cols)
    
    if clip_aspect > aspect_ratio:
        scaled_clip: VideoClip = clip.resized(height=clip_height)
    else:
        scaled_clip: VideoClip = clip.resized(width=clip_width)
                
    cropped_clip = scaled_clip.cropped(
        x_center=scaled_clip.w / 2,
        y_center=scaled_clip.h / 2,
        width=clip_width,
        height=clip_height
    )
    
    clip_x = int((position[0] - 1) * clip_width) # top left corner
    clip_y = int((position[1] - 1) * clip_height) # top left corner
    
    return cropped_clip.with_position((clip_x, clip_y))


def split_screen_clips(video_width, video_height, clips: list[VideoClip], max_position: tuple[int,int], manual_positions: list[tuple[int,int]] | None = None):
    rows, cols = max_position
    
    positions = []
    
    if manual_positions == None:    
        for r in range(1, rows + 1):
            for c in range(1, cols + 1):
                positions.append((r, c))
    else:
        positions = manual_positions
    
    positioned_clips = []
    for i, c in enumerate(clips):
        pos_clip = set_clip_position(c, position=positions[i], max_position=max_position)
        positioned_clips.append(pos_clip)
    
    return CompositeVideoClip(
        clips=positioned_clips, 
        size=(video_width, video_height),
        bg_color=(0,0,0),
    ).with_duration(clips[0].duration)
    