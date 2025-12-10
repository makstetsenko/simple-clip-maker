import asyncio
import logging
from asyncio import Future
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass

import yaml
from moviepy import ColorClip, VideoClip, VideoFileClip, vfx, concatenate_videoclips, TextClip, CompositeVideoClip
from tqdm import tqdm

import src.clip_builder.effect_presets.crop as crop_effect_preset
import src.clip_builder.effect_presets.flash as flash_effect_preset
import src.clip_builder.effect_presets.pan as pan_effect_preset
import src.clip_builder.effect_presets.zoom as zoom_effect_preset
import src.clip_builder.effects.crop as crop_effects
import src.clip_builder.effects.playback as playback_effects
from src.clip_builder.effects.split_screen import split_screen_clips, get_positions_from_layout, SplitScreenCriteria
from src.clip_builder.timeline_config import TimelineConfig, EffectType, EffectMethod, VideoSegmentEffect
from src.clip_builder.video_project import TimelineSegmentConfig
from src.clip_builder.video_resolution import VideoResolution

logger = logging.getLogger(__name__)


process_pool = ProcessPoolExecutor(max_workers=4)


@dataclass
class VideoClipBuilder:
    fps: int
    resolution: VideoResolution
    temp_path: str
    debug: bool = False

    async def build_clip(self, config: TimelineConfig) -> str:
        segments = await self.build_segment_clips(config)
        clips = [VideoFileClip(s) for s in segments]

        chained_clip_path = f"{self.temp_path}/chained_clip.mp4"
        chained_clip = concatenate_videoclips(clips=clips, method="compose")
        self.write_video_file(chained_clip, chained_clip_path)

        for c in clips:
            c.close()

        chained_clip.close()

        return chained_clip_path

    def set_debug(self, debug: bool):
        self.debug = debug

        if not debug:
            return

        self.resolution_backup = VideoResolution(self.resolution.size)

        scale = self.resolution.height / 240.0
        self.resolution = VideoResolution(
            size=(int(self.resolution.width / scale), int(self.resolution.height / scale))
        )
        self.fps = 12

    async def build_segment_clips(self, config: TimelineConfig):

        loop = asyncio.get_running_loop()
        tasks: set[Future[tuple[int, str]]] = set()

        progress_bar = tqdm(total=len(config.segments))
        progress_bar.set_description("Building segments")

        def done_callback(t: Future[tuple[int, str]]):
            tasks.discard(t)
            progress_bar.update(1)

        try:
            for segment in config.segments:
                if segment.is_split_screen:
                    task = loop.run_in_executor(
                        process_pool, self.write_spit_screen_clip, self.temp_path, segment, config.effects
                    )
                else:
                    task = loop.run_in_executor(
                        process_pool, self.write_single_panel_clip, self.temp_path, segment, config.effects
                    )

                task.add_done_callback(done_callback)
                tasks.add(task)

            segment_clips: list[tuple[int, str]] = await asyncio.gather(*tasks)
            segment_clips.sort(key=lambda x: x[0])
            return [s[1] for s in segment_clips]

        finally:
            process_pool.shutdown(wait=True)
            progress_bar.close()

    def write_single_panel_clip(
        self, path: str, segment_config: TimelineSegmentConfig, global_effects: list[VideoSegmentEffect]
    ) -> tuple[int, str]:
        video = segment_config.videos[0]

        merged_clip = self.load_clip(video.path)

        subclip = self.get_subclip(merged_clip, video.start_time, segment_config.duration)

        segment_clip_path = f"{path}/segment_{segment_config.index}.mp4"

        segment_clip = self.apply_effects(subclip, global_effects + segment_config.effects)
        segment_clip = self.add_debug_info_if_requested(segment_clip, segment_config)
        self.write_video_file(segment_clip, segment_clip_path)

        segment_clip.close()
        subclip.close()
        merged_clip.close()

        return (segment_config.index, segment_clip_path)

    def write_spit_screen_clip(
        self, path: str, segment_config: TimelineSegmentConfig, global_effects: list[VideoSegmentEffect]
    ) -> tuple[int, str]:

        if segment_config.videos is None or len(segment_config.videos) == 0:
            raise Exception("Videos list is empty or null")

        segment_clip_path = f"{path}/segment_{segment_config.index}.mp4"

        if len(segment_config.videos) == 1:
            video = segment_config.videos[0]
            clip = self.load_clip(video.path)
            subclipped = self.get_subclip(clip, video.start_time, segment_config.duration)

            position_layout = (1, 3) if self.resolution.is_vertical else (3, 1)
            clip_positions = get_positions_from_layout(position_layout)

            segment_clip: VideoClip = split_screen_clips(
                video_width=self.resolution.width,
                video_height=self.resolution.height,
                clips_criteria=[
                    SplitScreenCriteria(
                        clip=subclipped,
                        position=clip_positions[0],
                        scale_factor=0.95,
                    ),
                    SplitScreenCriteria(
                        clip=subclipped,
                        scale_factor=1.1,
                        position=clip_positions[1],
                    ),
                    SplitScreenCriteria(
                        clip=subclipped.with_effects([vfx.MirrorX()]),
                        position=clip_positions[2],
                        scale_factor=0.95,
                    ),
                ],
                position_layout=position_layout,
                clip_duration=segment_config.duration,
            )

            segment_clip = self.apply_effects(segment_clip, global_effects + segment_config.effects)
            segment_clip = self.add_debug_info_if_requested(segment_clip, segment_config)
            self.write_video_file(segment_clip, segment_clip_path)

            subclipped.close()
            clip.close()

            return (segment_config.index, segment_clip_path)

        if len(segment_config.videos) == 2:
            video_1 = segment_config.videos[0]
            video_2 = segment_config.videos[1]

            clip_1 = self.load_clip(video_1.path)
            clip_2 = self.load_clip(video_2.path)

            subclipped_1: VideoClip = self.get_subclip(clip_1, video_1.start_time, segment_config.duration)
            subclipped_2: VideoClip = self.get_subclip(clip_2, video_2.start_time, segment_config.duration)

            position_layout = (1, 3) if self.resolution.is_vertical else (3, 1)
            clip_positions = get_positions_from_layout(position_layout)

            segment_clip: VideoClip = split_screen_clips(
                video_width=self.resolution.width,
                video_height=self.resolution.height,
                clips_criteria=[
                    SplitScreenCriteria(
                        clip=subclipped_1,
                        position=clip_positions[0],
                        scale_factor=0.95,
                    ),
                    SplitScreenCriteria(
                        clip=subclipped_2,
                        scale_factor=1.1,
                        position=clip_positions[1],
                    ),
                    SplitScreenCriteria(
                        clip=subclipped_1.with_effects([vfx.MirrorX()]),
                        position=clip_positions[2],
                        scale_factor=0.95,
                    ),
                ],
                position_layout=position_layout,
                clip_duration=segment_config.duration,
            )

            segment_clip = self.apply_effects(segment_clip, global_effects + segment_config.effects)
            segment_clip = self.add_debug_info_if_requested(segment_clip, segment_config)
            self.write_video_file(segment_clip, segment_clip_path)

            subclipped_1.close()
            subclipped_2.close()
            clip_1.close()
            clip_2.close()

            return (segment_config.index, segment_clip_path)

        position_layout = (
            (1, len(segment_config.videos)) if self.resolution.is_vertical else (len(segment_config.videos), 1)
        )
        clip_positions = get_positions_from_layout(position_layout)

        split_screen_criteria = []
        clips: list[VideoClip] = []
        subclips: list[VideoClip] = []

        for i, v in enumerate(segment_config.videos):
            c = self.load_clip(v.path)
            s = self.get_subclip(c, v.start_time, segment_config.duration)
            clips.append(c)
            subclips.append(s)
            split_screen_criteria.append(SplitScreenCriteria(clip=s, position=clip_positions[i], scale_factor=1))

        segment_clip: VideoClip = split_screen_clips(
            video_width=self.resolution.width,
            video_height=self.resolution.height,
            clips_criteria=split_screen_criteria,
            position_layout=position_layout,
            clip_duration=segment_config.duration,
        )

        segment_clip = self.apply_effects(segment_clip, global_effects + segment_config.effects)
        segment_clip = self.add_debug_info_if_requested(segment_clip, segment_config)
        self.write_video_file(segment_clip, segment_clip_path)

        for c in subclips + clips:
            c.close()

        return (segment_config.index, segment_clip_path)

    def get_clip_padding(self, duration: float):
        requires_frame_drift = duration <= 0.55
        return (1.0 / self.fps) if requires_frame_drift else 0

    def get_subclip(self, clip: VideoClip, start_time: float, duration: float) -> VideoClip:
        return clip[start_time : start_time + duration + self.get_clip_padding(duration)].with_duration(duration)

    def apply_effects(self, segment_clip: VideoClip, effects: list[VideoSegmentEffect]):
        for e in effects:

            if e.effect_type == EffectType.ZOOM:

                if e.method == EffectMethod.ZOOM_IN__ZOOM_OUT:
                    zoom_factor = float(e.args[0])
                    segment_clip = zoom_effect_preset.zoom_in__zoom_out(segment_clip, zoom_factor)

                if e.method == EffectMethod.ZOOM_OUT__ZOOM_IN:
                    zoom_factor = float(e.args[0])
                    segment_clip = zoom_effect_preset.zoom_out__zoom_in(segment_clip, zoom_factor)

                if e.method == EffectMethod.ZOOM_IN_AT_CLIP_STARTS:
                    zoom_factor = float(e.args[0])
                    zoom_duration = float(e.args[1])
                    easing = e.args[2] if str(len(e.args)) == 3 else "ease_out"
                    segment_clip = zoom_effect_preset.zoom_in_at_clip_starts(
                        segment_clip, zoom_factor, zoom_duration, easing
                    )

                if e.method == EffectMethod.ZOOM_IN_AT_CLIP_ENDS:
                    zoom_factor = float(e.args[0])
                    zoom_duration = float(e.args[1])
                    easing = e.args[2] if str(len(e.args)) == 3 else "ease_out"
                    segment_clip = zoom_effect_preset.zoom_in_at_clip_ends(
                        segment_clip, zoom_factor, zoom_duration, easing
                    )

                if e.method == EffectMethod.ZOOM_BUMP:
                    segment_clip = zoom_effect_preset.zoom_bump(
                        clip=segment_clip,
                        zoom_factor=float(e.args[0]),
                        bump_count=int(e.args[1]),
                        reverse=bool(e.args[2]),
                    )

            if e.effect_type == EffectType.PAN:

                if e.method == EffectMethod.PAN_SIDE_TO_SIDE:
                    segment_clip = pan_effect_preset.pan_side_to_side(
                        clip=segment_clip,
                        pan=(int(e.args[0][0]), int(e.args[0][1])),
                        easing=e.args[1] if str(len(e.args)) == 2 else "ease_out",
                    )

            if e.effect_type == EffectType.FLASH:

                if e.method == EffectMethod.FLASH:
                    segment_clip = flash_effect_preset.flash(
                        clip=segment_clip,
                        time=float(e.args[0]),
                        flash_duration=float(e.args[1]),
                        color=(int(e.args[2][0]), int(e.args[2][1]), int(e.args[2][2])),
                        pick_random_flash_color=bool(e.args[3]),
                    )

                if e.method == EffectMethod.BURST_FLASH:
                    segment_clip = flash_effect_preset.burst_flash(
                        clip=segment_clip,
                        flashes_count=int(e.args[0]),
                        color=(int(e.args[1][0]), int(e.args[1][1]), int(e.args[1][2])),
                        pick_random_flash_color=bool(e.args[2]),
                    )

            if e.effect_type == EffectType.CROP:

                if e.method == EffectMethod.LINE_CROP:
                    segment_clip = crop_effect_preset.line_crop(
                        clip=segment_clip,
                        line_number=int(e.args[0]),
                        total_lines=int(e.args[1]),
                        is_vertical=bool(e.args[2]),
                    )

                if e.method == EffectMethod.BURST_LINE_CROP:
                    segment_clip = crop_effect_preset.burst_line_crop(
                        clip=segment_clip,
                        total_lines=int(e.args[0]),
                        is_vertical=bool(e.args[1]),
                        reverse_ordering=bool(e.args[2]),
                    )

                if e.method == EffectMethod.FIT_VIDEO_INTO_FRAME_SIZE:
                    segment_clip = crop_effects.fit_video_into_frame_size(clip=segment_clip, size=self.resolution.size)

            if e.effect_type == EffectType.PLAYBACK:

                if e.method == EffectMethod.FORWARD_REVERSE:
                    segment_clip = playback_effects.forward_reverse(
                        clip=segment_clip, start_speed=float(e.args[0]), fast_slow_mode=True
                    )

                if e.method == EffectMethod.RAMP_SPEED_SEGMENTS:
                    segment_clip = playback_effects.ramp_speed_segments(
                        clip=segment_clip,
                        speeds=[float(a) for a in e.args],
                        scale_speed_to_original_duration=True,
                        ramps_count_between_speed=5,
                    )

        return segment_clip

    def add_debug_info_if_requested(self, segment_clip, segment_config: TimelineSegmentConfig) -> VideoClip:
        if self.debug:

            text_bg_clip_overlay = (
                ColorClip(
                    color=(255, 255, 255),
                    size=(60, 60),
                    duration=segment_config.duration,
                )
                .with_position((0, 0))
                .with_fps(1)
            )

            text_clip_overlay = (
                TextClip(
                    text=str(segment_config.index),
                    text_align="left",
                    font_size=26,
                    size=(60, 60),
                    duration=segment_config.duration,
                )
                .with_position((0, 0))
                .with_fps(1)
            )
            return (
                CompositeVideoClip(clips=[segment_clip, text_bg_clip_overlay, text_clip_overlay])
                .with_duration(segment_config.duration)
                .with_fps(self.fps)
            )

        return segment_clip

    def write_video_file(self, clip: VideoClip, path: str):

        if self.debug:
            clip.write_videofile(
                path,
                audio=None,
                logger=None,
                fps=self.fps,
                preset="ultrafast",
                ffmpeg_params=["-crf", "34", "-pix_fmt", "yuv420p"],
            )
            return

        clip.write_videofile(path, audio=None, logger=None, fps=self.fps)

    def load_clip(self, path):
        if self.debug:
            return VideoFileClip(path, audio=False, resize_algorithm="fast_bilinear").resized(0.1)

        return VideoFileClip(path)
