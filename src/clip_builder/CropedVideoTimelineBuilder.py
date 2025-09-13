import src.video_clip_transform as video_clip_transform
from src.clip_builder.ClipBuilderHelper import ClipBuilderHelper
import random


from moviepy import VideoClip


class CropedVideoTimelineBuilder:
    def __init__(self, video_resolution: tuple[int,int], time_stops: list[float], repeat_clips: bool, fps: int, video_clips: list[VideoClip]):
        self.timeline_clips: list[VideoClip] = []
        self.used_video_clips: list[VideoClip] = []

        self.used_clip_start_time = 0
        self.time_stops = time_stops
        self.video_resolution = video_resolution
        self.repeat_clips = repeat_clips
        self.fps = fps
        self.video_clips = video_clips
        
        
        # Target zoom factor and pan shift (in pixels)
        self.start_zoom = 1.0
        self.end_zoom = 1.1

        self.start_pos = (0, 0)  # center
        self.end_pos = (random.choice([-50, 50]), random.choice([-50, 50]))  # pan to right and down


    def build_timeline_clips(self):
        if len(self.time_stops) == 0:
            raise Exception("time_stops is empty. Cannot select clips for empty time stops")


        for i in range(1, len(self.time_stops)):
            self.build__clip_bewteen_time_stops(
                start_time=self.time_stops[i-1],
                end_time=self.time_stops[i]
            )


    def build__clip_bewteen_time_stops(self, start_time: float, end_time: float):
        duration = round(end_time - start_time, 2)

        clip: VideoClip = ClipBuilderHelper.compose_clip_with_min_duration(
            clips=self.video_clips,
            duration=duration,
            used_video_clips=self.used_video_clips,
            repeat_clips=self.repeat_clips
        )

        self.used_clip_start_time = self.used_clip_start_time \
            if ClipBuilderHelper.can_repeat_clip(self.used_video_clips, self.repeat_clips) \
            else ClipBuilderHelper.get_random_start_time_for_desired_of_clip_duration(full_clip_duration=round(clip.duration, 2), desired_duration=duration)


        subclipped: VideoClip = clip.subclipped(
            start_time=ClipBuilderHelper.round_time_to_fps(self.used_clip_start_time, self.fps),
            end_time=ClipBuilderHelper.round_time_to_fps(self.used_clip_start_time + duration, self.fps),
        )

        timeline_clip = video_clip_transform.crop_video(self.video_resolution[0], self.video_resolution[1], subclipped)

        # clip_with_effect = VideoClip(frame_function=lambda t: self.panzoom_frame(t=t, clip=timeline_clip, video_width=self.video_resolution[0], video_height=self.video_resolution[1]), duration=timeline_clip.duration)

        timeline_clip.close()

        self.timeline_clips.append(timeline_clip)
        self.used_video_clips.append(clip)



    def close(self):
        for c in self.timeline_clips + self.used_video_clips:
            c.close()
            
            
    def panzoom_frame(self, t, clip: VideoClip, video_width: int, video_height: int):
        duration = clip.duration
        progress = min(t / duration, 1)
        
        # Easing function (smooth in/out)
        ease = 3 * progress**2 - 2 * progress**3

        # Interpolate zoom and pan
        zoom = self.start_zoom + (self.end_zoom - self.start_zoom) * ease
        pan_x = self.start_pos[0] + (self.end_pos[0] - self.start_pos[0]) * ease
        pan_y = self.start_pos[1] + (self.end_pos[1] - self.start_pos[1]) * ease

        # Compute crop area
        crop_w = int(video_width / zoom)
        crop_h = int(video_height / zoom)
        x1 = (video_width - crop_w) // 2 + int(pan_x)
        y1 = (video_height - crop_h) // 2 + int(pan_y)
        x2 = x1 + crop_w
        y2 = y1 + crop_h

        return clip.cropped(x1=x1, y1=y1, x2=x2, y2=y2).resized((video_width, video_height)).get_frame(t)