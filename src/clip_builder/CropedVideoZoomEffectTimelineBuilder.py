import src.video_clip_transform as video_clip_transform
from src.clip_builder.ClipBuilderHelper import ClipBuilderHelper


from moviepy import VideoClip


class CropedVideoZoomEffectTimelineBuilder:
    def __init__(self, video_resolution: tuple[int,int], time_stops: list[float], repeat_clips: bool, fps: int, video_clips: list[VideoClip]):
        self.timeline_clips: list[VideoClip] = []
        self.used_video_clips: list[VideoClip] = []

        self.used_clip_start_time = 0
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
                end_time=self.time_stops[i]
            )


    def build__clip_bewteen_time_stops(self, start_time: float, end_time: float):
        duration = end_time - start_time

        clip: VideoClip = ClipBuilderHelper.compose_clip_with_min_duration(
            clips=self.video_clips,
            duration=duration,
            used_video_clips=self.used_video_clips,
            repeat_clips=self.repeat_clips
        )

        self.used_clip_start_time = self.used_clip_start_time \
            if ClipBuilderHelper.can_repeat_clip(self.used_video_clips, self.repeat_clips) \
            else ClipBuilderHelper.get_random_start_time_for_desired_of_clip_duration(clip.duration, duration)


        subclipped = clip.subclipped(
            start_time=ClipBuilderHelper.round_time_to_fps(self.used_clip_start_time, self.fps),
            end_time=ClipBuilderHelper.round_time_to_fps(self.used_clip_start_time + duration, self.fps),
        )

        timeline_clip = video_clip_transform.crop_video(self.video_resolution[0], self.video_resolution[1], subclipped)

        self.timeline_clips.append(timeline_clip)
        self.used_video_clips.append(clip)



    def close(self):
        for c in self.timeline_clips + self.used_video_clips:
            c.close()