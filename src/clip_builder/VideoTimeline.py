from src.clip_builder.ClipBuilderHelper import ClipBuilderHelper
from src.clip_builder.CropedVideoTimelineBuilder import CropedVideoTimelineBuilder
from src.clip_builder.SplitScreenVideoTimelineBuilder import SplitScreenVideoTimelineBuilder


from moviepy import VideoClip


import random


class VideoTimeline:

    def __init__(self, time_stops: list[float], video_resolution: tuple[int,int], fps: int, video_clips: list[VideoClip]):
        self.timelime_builders: list = []
        self.time_stops = time_stops
        self.video_resolution = video_resolution
        self.video_aspect_ratio = video_resolution[0] / video_resolution[1]
        self.fps = fps
        self.video_clips = video_clips

    def split_timeline_into_parts(self):
        part_time_stops_total_counts = [2,3,4,5]

        part_time_stops = []
        part_time_stops_count = random.choice(part_time_stops_total_counts)

        matched_aspect_ratio_clips = [c for c in self.video_clips if ClipBuilderHelper.are_matching_aspect_ratios([c.aspect_ratio, self.video_aspect_ratio])]
        not_matched_aspect_ratio_clips = [c for c in self.video_clips if not ClipBuilderHelper.are_matching_aspect_ratios([c.aspect_ratio, self.video_aspect_ratio])]

        matched_aspect_ratio_clips_count = len(matched_aspect_ratio_clips)
        total_clips_count = len(self.video_clips)

        for index, time_stop in enumerate(self.time_stops):
            part_time_stops.append(time_stop)

            if len(part_time_stops) == part_time_stops_count or index == len(self.time_stops) - 1:
                if random.random() < 1.0 * matched_aspect_ratio_clips_count / total_clips_count:
                    self.timelime_builders.append(
                        CropedVideoTimelineBuilder(
                            video_resolution=self.video_resolution,
                            time_stops=[x for x in part_time_stops],
                            repeat_clips=False,
                            fps=self.fps,
                            video_clips=matched_aspect_ratio_clips))

                else:
                    self.timelime_builders.append(
                        SplitScreenVideoTimelineBuilder(
                            video_resolution=self.video_resolution,
                            time_stops=[x for x in part_time_stops],
                            repeat_clips=False,
                            fps=self.fps,
                            video_clips=not_matched_aspect_ratio_clips))


                part_time_stops = [time_stop]
                part_time_stops_count = random.choice(part_time_stops_total_counts)


        print("Split video timeline. Done.")


    def build_timeline_clips(self):
        for b in self.timelime_builders:
            b.build_timeline_clips()

        print("Build timeline clips. Done.")

    def get_timeline_clips(self):
        clips = []

        for p in self.timelime_builders:
            for c in p.timeline_clips:
                clips.append(c)

        return clips


    def close(self):
        for p in self.timelime_builders:
            p.close()

        print("Closed clips.")