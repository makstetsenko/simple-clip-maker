import src.clip_builder.video_clip_transform as video_clip_transform
from src.clip_builder.ClipBuilderHelper import ClipBuilderHelper
from src.clip_builder.effects.zoom_effects import PanZoomEffectCriteria, pan_zoom_frame, bump_zoom_on_time_stops
from src.clip_builder.effects.effect_types import VideoEffectType


from moviepy import VideoClip
import logging

logger = logging.getLogger(__name__)

class CropedVideoTimelineBuilder:
    def __init__(
            self,
            video_resolution: tuple[int,int],
            time_stops: list[float],
            repeat_clips: bool,
            fps: int,
            video_clips: list[VideoClip],
            apply_effects: list[VideoEffectType] = [],
            use_single_clip: bool = False
        ):
        self.timeline_clips: list[VideoClip] = []
        self.used_video_clips: list[VideoClip] = []

        self.used_clip_start_time = 0
        self.time_stops = time_stops
        self.video_resolution = video_resolution
        self.repeat_clips = repeat_clips
        self.fps = fps
        self.video_clips = video_clips
        self.apply_effects_list = apply_effects
        self.use_single_clip = use_single_clip
        

    def build_timeline_clips(self):
        if len(self.time_stops) == 0:
            raise Exception("time_stops is empty. Cannot select clips for empty time stops")

        if self.use_single_clip:
            self.build_single_clip_timeline()
            return

        for i in range(1, len(self.time_stops)):
            self.build__clip_bewteen_time_stops(
                start_time=self.time_stops[i-1],
                end_time=self.time_stops[i],
                iteration=i
            )
            
    def build_single_clip_timeline(self):
        logger.info(f"Buildting single clip ({round(self.time_stops[0], ndigits=2)}, {round(self.time_stops[-1], ndigits=2)}). Time stops: {len(self.time_stops)}")
        duration = round(self.time_stops[-1] - self.time_stops[0], 2)
        
        clip: VideoClip = ClipBuilderHelper.compose_clip_with_min_duration(
            clips=self.video_clips,
            duration=duration,
            used_video_clips=[],
            repeat_clips=False
        )
        
        start_time = ClipBuilderHelper.get_random_start_time_for_minimum_required_duration(full_clip_duration=clip.duration, required_duration=duration)
        
        subclipped: VideoClip = clip.subclipped(
            start_time=start_time,
            end_time=start_time + duration,
        )
        
        cropped = video_clip_transform.crop_video(self.video_resolution[0], self.video_resolution[1], subclipped)

        timeline_clip = self.apply_effects(cropped)
        
        self.timeline_clips.append(timeline_clip)
        self.used_video_clips.append(clip)


    def build__clip_bewteen_time_stops(self, start_time: float, end_time: float, iteration: int):
        logger.info(f"Buildting clips btween time stops ({round(start_time, ndigits=2)}, {round(end_time, ndigits=2)})")
        
        duration = round(end_time - start_time, 2)

        clip: VideoClip = ClipBuilderHelper.compose_clip_with_min_duration(
            clips=self.video_clips,
            duration=duration,
            used_video_clips=self.used_video_clips,
            repeat_clips=self.repeat_clips
        )

        self.used_clip_start_time = self.used_clip_start_time \
            if ClipBuilderHelper.can_repeat_clip(self.used_video_clips, self.repeat_clips) \
            else ClipBuilderHelper.get_random_start_time_for_minimum_required_duration(full_clip_duration=clip.duration, required_duration=duration)


        subclipped: VideoClip = clip.subclipped(
            start_time=self.used_clip_start_time,
            end_time=self.used_clip_start_time + duration,
        )

        cropped = video_clip_transform.crop_video(self.video_resolution[0], self.video_resolution[1], subclipped)

        timeline_clip = self.apply_effects(cropped)

        if len(self.apply_effects_list) == 0:
            timeline_clip = cropped

        self.timeline_clips.append(timeline_clip)
        self.used_video_clips.append(clip)


    def apply_effects(self, clip: VideoClip):
        
        diff_time = self.time_stops[0]
        relative_time_stops = [t - diff_time for t in self.time_stops]
        
        clip_with_effect = clip
        
        for effect in self.apply_effects_list:
            
            if effect == VideoEffectType.PanZoom:
                logger.info("Applying PanZoom effect")
                
                criteria = PanZoomEffectCriteria(end_zoom=1.1)
                
                clip_with_effect = pan_zoom_frame(
                    clip=clip_with_effect, 
                    criteria=criteria,
                )
                
            if effect == VideoEffectType.BumpZoomOnTimeStops:
                logger.info("Applying BumpZoomOnTimeStops effect")
                clip_with_effect = bump_zoom_on_time_stops(
                    clip=clip_with_effect, 
                    video_resolution=self.video_resolution,
                    time_stops=relative_time_stops,
                    zoom_amount_percent=5,
                    bump_duration_seconds=0.25
                )
                
        return clip_with_effect
        
    def copy_clip(self, clip: VideoClip):
        return clip.close()

    def close(self):
        for c in self.timeline_clips + self.used_video_clips:
            c.close()
            