import src.clip_builder.video_clip_transform as video_clip_transform
from src.clip_builder.ClipBuilderHelper import ClipBuilderHelper
from src.clip_builder.effects.zoom_effects import PanZoomEffectCriteria, pan_zoom_frame, bump_zoom_on_time_stops


from moviepy import VideoClip, vfx
import logging

logger = logging.getLogger(__name__)

class SplitScreenVideoTimelineBuilder:
    def __init__(self, video_resolution: tuple[int,int], time_stops: list[float], repeat_clips: bool, fps: int, video_clips: list[VideoClip]):
        self.timeline_clips: list[VideoClip] = []
        self.used_video_clips_1: list[VideoClip] = []
        self.used_video_clips_2: list[VideoClip] = []

        self.used_clip_start_time_1 = 0
        self.used_clip_start_time_2 = 0
        self.time_stops = time_stops
        self.video_resolution = video_resolution
        self.repeat_clips = repeat_clips
        self.fps = fps
        self.video_clips = video_clips


    def build_timeline_clips(self):
        if len(self.time_stops) == 0:
            raise Exception("time_stops is empty. Cannot select clips for empty time stops")

        for i in range(1, len(self.time_stops)):
            self.build__clip_bewteen_time_stops(
                start_time=self.time_stops[i-1],
                end_time=self.time_stops[i],
                iteraton=i
            )


    def build__clip_bewteen_time_stops(self, start_time: float, end_time: float, iteraton: int):
        duration = end_time - start_time

        clip_1: VideoClip = ClipBuilderHelper.compose_clip_with_min_duration(
            clips=self.video_clips,
            duration=duration,
            used_video_clips=self.used_video_clips_1,
            repeat_clips=self.repeat_clips
        )

        clip_2: VideoClip = ClipBuilderHelper.compose_clip_with_min_duration(
            clips=self.video_clips,
            duration=duration,
            used_video_clips=self.used_video_clips_2,
            repeat_clips=self.repeat_clips
        )

        self.used_clip_start_time_1 = self.get_clip_start_time(self.used_clip_start_time_1, self.used_video_clips_1, self.repeat_clips, clip_1.duration, duration)
        self.used_clip_start_time_2 = self.get_clip_start_time(self.used_clip_start_time_2, self.used_video_clips_2, self.repeat_clips, clip_2.duration, duration)


        subclipped_1: VideoClip = clip_1.subclipped(
            start_time=ClipBuilderHelper.round_time_to_fps(self.used_clip_start_time_1, self.fps),
            end_time=ClipBuilderHelper.round_time_to_fps(self.used_clip_start_time_1 + duration, self.fps),
        )
        subclipped_2: VideoClip = clip_2.subclipped(
            start_time=ClipBuilderHelper.round_time_to_fps(self.used_clip_start_time_2, self.fps),
            end_time=ClipBuilderHelper.round_time_to_fps(self.used_clip_start_time_2 + duration, self.fps),
        )
        
        position_layout = (3, 1) if ClipBuilderHelper.is_horizontal(self.video_resolution) else (1,3)
        clip_positions = video_clip_transform.get_positions_from_layout(position_layout)
        
        zoom_effect_criteria = PanZoomEffectCriteria(start_zoom=1.0, end_zoom=1.1)
        zoom_effect_criteria_reversed = PanZoomEffectCriteria(start_zoom=1.1, end_zoom=1.0)

        timeline_clip = video_clip_transform.split_screen_clips(
            video_width=self.video_resolution[0],
            video_height=self.video_resolution[1],
            clips_criterias=[
                video_clip_transform.SplitScreenCriteria(clip=subclipped_1, position=clip_positions[0], scale_factor=0.9),
                video_clip_transform.SplitScreenCriteria(clip=subclipped_1.with_effects([vfx.MirrorX()]), position=clip_positions[2], scale_factor=0.9),
                video_clip_transform.SplitScreenCriteria(clip=pan_zoom_frame(subclipped_2, zoom_effect_criteria), scale_factor=1.15, position=clip_positions[1]),
            ],
            position_layout=position_layout,
            clip_duration=duration,
        )
        
        timeline_clip = pan_zoom_frame(timeline_clip, zoom_effect_criteria if iteraton % 2 == 0 else zoom_effect_criteria_reversed)

        self.timeline_clips.append(timeline_clip)
        self.used_video_clips_1.append(clip_1)
        self.used_video_clips_2.append(clip_2)



    def get_clip_start_time(self, used_clip_start_time: float, used_video_clips: list[VideoClip], repeat_clips: bool, full_clip_duration, desired_duration):
        return used_clip_start_time \
            if ClipBuilderHelper.can_repeat_clip(used_video_clips, repeat_clips) \
            else ClipBuilderHelper.get_random_start_time_for_minimum_required_duration(full_clip_duration, desired_duration)



    def close(self):
        for c in self.timeline_clips + self.used_video_clips_1 + self.used_video_clips_2:
            c.close()