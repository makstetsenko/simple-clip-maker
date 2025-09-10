import numpy as np
from moviepy import *

def get_average_color(frame):
    # Downscale for performance
    small = frame[::10, ::10]  # Sample every 10th pixel
    return small.mean(axis=(0, 1))  # (R, G, B)

def detect_color_changes(colors, threshold=15):
    changes = [0]
    for i in range(1, len(colors)):
        diff = np.linalg.norm(colors[i] - colors[i-1])
        if diff > threshold:
            changes.append(i)
    changes.append(len(colors) - 1)
    return changes

def split_clip_by_frame_changes(clip: VideoClip, sample_rate=0.01):
    duration = clip.duration

    # Sample frames every X seconds
    timestamps = np.arange(0, duration, sample_rate)
    colors = [get_average_color(clip.get_frame(t)) for t in timestamps]

    # Detect where color changes
    change_indices = detect_color_changes(colors)
    
    subclips = []
    for i in range(len(change_indices) - 1):
        start = timestamps[change_indices[i]]
        end = timestamps[change_indices[i+1]]
        subclips.append(clip.subclipped(start, end))

    return subclips
