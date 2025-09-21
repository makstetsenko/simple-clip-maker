from src.clip_builder.effects.effect_types import VideoEffectType
from src.clip_builder.ClipBuilderHelper import ClipBuilderHelper
from src.clip_builder.timeline_builders.CropedVideoTimelineBuilder import CropedVideoTimelineBuilder
from src.clip_builder.timeline_builders.SplitScreenVideoTimelineBuilder import SplitScreenVideoTimelineBuilder


from moviepy import VideoClip


import random
import numpy as np
import logging

logger = logging.getLogger(__name__)


class VideoTimeline:

    def __init__(self, time_stops: list[float], video_resolution: tuple[int,int], fps: int, video_clips: list[VideoClip]):
        self.timelime_builders: list = []
        self.time_stops = time_stops
        self.video_resolution = video_resolution
        self.video_aspect_ratio = video_resolution[0] / video_resolution[1]
        self.fps = fps
        self.video_clips = video_clips

    def split_timeline_into_parts(self):
        groups, threshold = self.group_nearby_time_stops(self.time_stops)
        time_stop_groups = self.connect_fast_slow_time_stops(groups)
        

        matched_aspect_ratio_clips = [c for c in self.video_clips if ClipBuilderHelper.are_matching_aspect_ratios([c.aspect_ratio, self.video_aspect_ratio])]
        not_matched_aspect_ratio_clips = [c for c in self.video_clips if not ClipBuilderHelper.are_matching_aspect_ratios([c.aspect_ratio, self.video_aspect_ratio])]

        matched_aspect_ratio_clips_count = len(matched_aspect_ratio_clips)
        total_clips_count = len(self.video_clips)
        
        for times_group in time_stop_groups:
            if random.random() < 1.0 * matched_aspect_ratio_clips_count / total_clips_count:
                
                is_fast_changing = np.median(np.diff(times_group)) <= threshold
                
                apply_effects = []
                use_single_clip = False
                
                if is_fast_changing:
                    apply_effects.append(VideoEffectType.PanZoom)
                else:
                    apply_effects.append(VideoEffectType.BumpZoomOnTimeStops)
                    use_single_clip = True

                self.timelime_builders.append(
                    CropedVideoTimelineBuilder(
                        video_resolution=self.video_resolution,
                        time_stops=[x for x in times_group],
                        repeat_clips=False,
                        fps=self.fps,
                        video_clips=matched_aspect_ratio_clips,
                        apply_effects=apply_effects,
                        use_single_clip=use_single_clip
                    ))

            else:
                self.timelime_builders.append(
                    SplitScreenVideoTimelineBuilder(
                        video_resolution=self.video_resolution,
                        time_stops=[x for x in times_group],
                        repeat_clips=False,
                        fps=self.fps,
                        video_clips=not_matched_aspect_ratio_clips))


        logger.info("Split video timeline. Done.")


    def build_timeline_clips(self):
        for b in self.timelime_builders:
            b.build_timeline_clips()

        logger.info("Build timeline clips. Done.")

    def get_timeline_clips(self):
        clips = []

        for p in self.timelime_builders:
            for c in p.timeline_clips:
                clips.append(c)

        return clips


    def close(self):
        for p in self.timelime_builders:
            p.close()

        logger.info("Closed clips.")
        
        
    def group_nearby_time_stops(self, values):
        values = sorted(values)
        if len(values) < 2:
            return [values]

        threshold = np.median(np.diff(values))

        groups = [[values[0]]]
        for v in values[1:]:
            if v - groups[-1][-1] <= threshold:
                groups[-1].append(round(v, ndigits=2))
            else:
                groups.append([round(v, ndigits=2)])
        return groups, threshold
    
    
    def connect_fast_slow_time_stops(self, groups):
        connected = []
        for i, g in enumerate(groups):
            
            if i == 0:
                connected.append(g)
                continue
            
            if len(g) == 1 and len(groups[i-1]) == 1:
                connected[-1].append(g[0])
                continue
                
            if len(g) > 1 and len(groups[i-1]) == 1:
                connected[-1].append(g[0])
                continue
                
            if len(groups[i-1]) > 1:
                connected.append(groups[i-1])
                connected.append([groups[i-1][-1], g[0]])
                continue

        return connected