from src.clip_builder.effects.effect_types import VideoEffectType
from src.clip_builder.ClipBuilderHelper import ClipBuilderHelper
from src.clip_builder.timeline_builders.CropedVideoTimelineBuilder import CropedVideoTimelineBuilder
from src.clip_builder.timeline_builders.SplitScreenVideoTimelineBuilder import SplitScreenVideoTimelineBuilder
import json

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
        
        logger.info(f"Splitted timeline into groups (threshold {threshold}s)")
        logger.info(f"Groups:\n{json.dumps(time_stop_groups)}")
        

        matched_aspect_ratio_clips = [c for c in self.video_clips if ClipBuilderHelper.are_matching_aspect_ratios([c.aspect_ratio, self.video_aspect_ratio])]
        not_matched_aspect_ratio_clips = [c for c in self.video_clips if not ClipBuilderHelper.are_matching_aspect_ratios([c.aspect_ratio, self.video_aspect_ratio])]

        matched_aspect_ratio_clips_count = len(matched_aspect_ratio_clips)
        not_matched_aspect_ratio_clips_count = len(not_matched_aspect_ratio_clips)
        total_clips_count = len(self.video_clips)

        matching_ratio_multiplier = 4.0
        matching_clip_appearign_freq = matching_ratio_multiplier * matched_aspect_ratio_clips_count / (matched_aspect_ratio_clips_count * matching_ratio_multiplier + not_matched_aspect_ratio_clips_count)
        
        for times_group in time_stop_groups:
            if random.random() < matching_clip_appearign_freq:
                
                time_diff_median = np.median(np.diff(times_group))
                
                is_fast_changing = time_diff_median <= threshold * 1.2
                is_slow_changing = time_diff_median > threshold * 2
                
                apply_effects = []
                use_single_clip = False

                if 3 < len(time_stop_groups) <= 10:
                    use_single_clip = True
                    apply_effects.append(VideoEffectType.BumpZoomOnTimeStops)
                else:
                    apply_effects.append(VideoEffectType.PanZoom)
                    
                    
                # if is_slow_changing:
                #     apply_effects.append(VideoEffectType.BumpZoomOnTimeStops)

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

        threshold = np.median(np.diff(values)) * 0.8

        groups = [[values[0]]]
        for v in values[1:]:
            if v - groups[-1][-1] <= threshold:
                groups[-1].append(v)
            else:
                groups.append([v])

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