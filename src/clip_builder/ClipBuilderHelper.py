from moviepy import VideoClip, concatenate_videoclips


import math
import random


class ClipBuilderHelper:
    @staticmethod
    def find_clip_with_min_duration(min_duration: float,  clips: list[VideoClip]) -> VideoClip:
        filtered = [c for c in clips if c.duration > min_duration]

        if len(filtered) == 0:
            return None

        return random.choice(filtered)


    @staticmethod
    def compose_clip_with_min_duration(duration: float, clips: list[VideoClip], used_video_clips: list[VideoClip], repeat_clips) -> VideoClip:
        selected_clips: list[VideoClip] = []
        selected_clips_duration = 0

        while selected_clips_duration <= duration:
            clip = used_video_clips[-1] \
                if ClipBuilderHelper.can_repeat_clip(used_video_clips, repeat_clips) \
                else ClipBuilderHelper.find_clip_with_min_duration(duration, clips)

            if clip == None:
                clip = random.choice(clips)

            selected_clips.append(clip)
            selected_clips_duration += clip.duration

        return concatenate_videoclips(clips=selected_clips)


    @staticmethod
    def can_repeat_clip(used_video_clips: list[VideoClip], repeat_clips) -> bool:
        return repeat_clips and len(used_video_clips) > 0

    @staticmethod
    def round_time_to_fps(time: float, fps: int):
        return round(int(math.ceil(time * fps)) / fps, ndigits=2)


    @staticmethod
    def get_random_start_time_for_desired_of_clip_duration(full_clip_duration: float, desired_duration: float):
        return random.randint(0, math.floor((full_clip_duration - desired_duration) * 100)) / 100.0


    @staticmethod
    def is_vertical(video_resolution: tuple[int,int]):
        return video_resolution[0] / video_resolution[1] < 1


    @staticmethod
    def is_horizontal(video_resolution: tuple[int,int]):
        return not ClipBuilderHelper.is_vertical(video_resolution)


    @staticmethod
    def are_matching_aspect_ratios(aspect_ratios: list[float]):
        return all(a >= 1 for a in aspect_ratios) or all(a < 1 for a in aspect_ratios)