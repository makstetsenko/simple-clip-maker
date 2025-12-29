import asyncio
import logging
from dataclasses import dataclass

from moviepy import ColorClip, VideoClip, VideoFileClip, vfx, concatenate_videoclips, TextClip, CompositeVideoClip
from tqdm import tqdm
import pathlib
import subprocess


from .effect_presets import crop as crop_effect_preset
from .effect_presets import flash as flash_effect_preset
from .effect_presets import pan as pan_effect_preset
from .effect_presets import zoom as zoom_effect_preset
from .effects import crop as crop_effects
from .effects import playback as playback_effects
from .effects.split_screen import split_screen_clips, get_positions_from_layout, SplitScreenCriteria
from .timeline_config import TimelineConfig, EffectType, EffectMethod, VideoSegmentEffect
from .video_project import TimelineSegmentConfig
from .video_resolution import VideoResolution
from .effects_descriptor import EffectArgs

logger = logging.getLogger(__name__)


@dataclass
class VideoClipBuilder:
    fps: int
    resolution: VideoResolution
    temp_path: str
    debug: bool = False

    async def build_clip(self, config: TimelineConfig) -> str:
        segments = await self.build_segment_clips(config)

        list_file = pathlib.Path(pathlib.Path(self.temp_path).joinpath("concat_list.txt"))
        list_file.write_text("\n".join([f"file '{pathlib.Path(p).resolve()}'" for p in segments]) + "\n")

        chained_clip_path = str(pathlib.Path(self.temp_path).joinpath("chained_clip.mp4").resolve())

        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(list_file.resolve()),
                "-c",
                "copy",
                chained_clip_path,
            ],
            check=True,
        )

        return chained_clip_path

    def set_debug(self, debug: bool):
        self.debug = debug

        if not debug:
            return

        debug_height = 240
        scale = self.resolution.height / debug_height
        debug_width = int(self.resolution.width / scale)
        if debug_width % 2 != 0:
            debug_width += 1

        self.resolution = VideoResolution(size=(debug_width, debug_height))
        self.fps = 12

    async def build_segment_clips(self, config: TimelineConfig):

        progress_bar = tqdm(total=len(config.segments))
        progress_bar.set_description("Building segments")
        segment_clips: list[str] = []

        try:
            for segment in config.segments:
                segment_clip_path = f"{self.temp_path}/{segment.etag}.mp4"

                segment_clips.append(segment_clip_path)
                progress_bar.update(1)

                if pathlib.Path(segment_clip_path).exists():
                    continue

                if segment.is_split_screen:
                    await self.write_spit_screen_clip(segment_clip_path, segment, config.effects)
                else:
                    await self.write_single_panel_clip(segment_clip_path, segment, config.effects)

            return segment_clips

        finally:
            progress_bar.close()

    async def write_single_panel_clip(
        self, path: str, segment_config: TimelineSegmentConfig, global_effects: list[VideoSegmentEffect]
    ) -> tuple[int, str]:
        video = segment_config.videos[0]

        merged_clip = self.load_clip(video.path)

        subclip = self.get_subclip(merged_clip, video.start_time, segment_config.duration)

        segment_clip = self.apply_effects(subclip, global_effects + segment_config.effects)
        segment_clip = self.add_debug_info_if_requested(segment_clip, segment_config)
        self.write_video_file(segment_clip, path)

        segment_clip.close()
        subclip.close()
        merged_clip.close()

        await asyncio.sleep(0)
        return (segment_config.index, path)

    async def write_spit_screen_clip(
        self, path: str, segment_config: TimelineSegmentConfig, global_effects: list[VideoSegmentEffect]
    ) -> tuple[int, str]:

        if segment_config.videos is None or len(segment_config.videos) == 0:
            raise Exception("Videos list is empty or null")

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
            self.write_video_file(segment_clip, path)

            subclipped.close()
            clip.close()

            await asyncio.sleep(0)
            return (segment_config.index, path)

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
            self.write_video_file(segment_clip, path)

            subclipped_1.close()
            subclipped_2.close()
            clip_1.close()
            clip_2.close()

            await asyncio.sleep(0)
            return (segment_config.index, path)

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
        self.write_video_file(segment_clip, path)

        for c in subclips + clips:
            c.close()

        await asyncio.sleep(0)
        return (segment_config.index, path)

    def get_clip_padding(self, duration: float):
        requires_frame_drift = duration <= 0.55
        return (1.0 / self.fps) if requires_frame_drift else 0

    def get_subclip(self, clip: VideoClip, start_time: float, duration: float) -> VideoClip:
        return clip[start_time : start_time + duration + self.get_clip_padding(duration)].with_duration(duration)

    def apply_effects(self, segment_clip: VideoClip, effects: list[VideoSegmentEffect]):
        for e in effects:

            if e.effect_type == EffectType.ZOOM:

                if e.method == EffectMethod.ZOOM_IN__ZOOM_OUT:
                    effect_args: EffectArgs.ZOOM.ZOOM_IN__ZOOM_OUT = e.args
                    segment_clip = zoom_effect_preset.zoom_in__zoom_out(
                        segment_clip, zoom_factor=effect_args.zoom_factor
                    )

                if e.method == EffectMethod.ZOOM_OUT__ZOOM_IN:
                    effect_args: EffectArgs.ZOOM.ZOOM_OUT__ZOOM_IN = e.args
                    segment_clip = zoom_effect_preset.zoom_out__zoom_in(segment_clip, effect_args.zoom_factor)

                if e.method == EffectMethod.ZOOM_IN_AT_CLIP_STARTS:
                    effect_args: EffectArgs.ZOOM.ZOOM_IN_AT_CLIP_STARTS = e.args
                    segment_clip = zoom_effect_preset.zoom_in_at_clip_starts(
                        segment_clip, effect_args.zoom_factor, effect_args.zoom_duration, effect_args.easing
                    )

                if e.method == EffectMethod.ZOOM_IN_AT_CLIP_ENDS:
                    effect_args: EffectArgs.ZOOM.ZOOM_IN_AT_CLIP_ENDS = e.args
                    segment_clip = zoom_effect_preset.zoom_in_at_clip_ends(
                        segment_clip, effect_args.zoom_factor, effect_args.zoom_duration, effect_args.easing
                    )

                if e.method == EffectMethod.ZOOM_BUMP:
                    effect_args: EffectArgs.ZOOM.ZOOM_BUMP = e.args
                    segment_clip = zoom_effect_preset.zoom_bump(
                        clip=segment_clip,
                        zoom_factor=effect_args.zoom_factor,
                        bump_count=effect_args.bump_count,
                        reverse=effect_args.reverse,
                    )

            if e.effect_type == EffectType.PAN:

                if e.method == EffectMethod.PAN_SIDE_TO_SIDE:
                    effect_args: EffectArgs.ZOOM.PAN_SIDE_TO_SIDE = e.args
                    segment_clip = pan_effect_preset.pan_side_to_side(
                        clip=segment_clip,
                        pan=effect_args.pan,
                        easing=effect_args.easing,
                    )

            if e.effect_type == EffectType.FLASH:

                if e.method == EffectMethod.FLASH:
                    effect_args: EffectArgs.FLASH.FLASH = e.args
                    segment_clip = flash_effect_preset.flash(
                        clip=segment_clip,
                        time=effect_args.time,
                        flash_duration=effect_args.flash_duration,
                        color=effect_args.color,
                        pick_random_flash_color=effect_args.pick_random_flash_color,
                    )

                if e.method == EffectMethod.BURST_FLASH:
                    effect_args: EffectArgs.FLASH.BURST_FLASH = e.args
                    segment_clip = flash_effect_preset.burst_flash(
                        clip=segment_clip,
                        flashes_count=effect_args.flashes_count,
                        color=effect_args.color,
                        pick_random_flash_color=effect_args.pick_random_flash_color,
                    )

            if e.effect_type == EffectType.CROP:

                if e.method == EffectMethod.LINE_CROP:
                    effect_args: EffectArgs.CROP.LINE_CROP = e.args
                    segment_clip = crop_effect_preset.line_crop(
                        clip=segment_clip,
                        line_number=effect_args.line_number,
                        total_lines=effect_args.total_lines,
                        is_vertical=effect_args.is_vertical,
                    )

                if e.method == EffectMethod.BURST_LINE_CROP:
                    effect_args: EffectArgs.CROP.BURST_LINE_CROP = e.args
                    segment_clip = crop_effect_preset.burst_line_crop(
                        clip=segment_clip,
                        total_lines=effect_args.total_lines,
                        is_vertical=effect_args.is_vertical,
                        reverse_ordering=effect_args.reverse_ordering,
                    )

                if e.method == EffectMethod.FIT_VIDEO_INTO_FRAME_SIZE:
                    segment_clip = crop_effects.fit_video_into_frame_size(clip=segment_clip, size=self.resolution.size)

            if e.effect_type == EffectType.PLAYBACK:

                if e.method == EffectMethod.FORWARD_REVERSE:
                    effect_args: EffectArgs.PLAYBACK.FORWARD_REVERSE = e.args
                    segment_clip = playback_effects.forward_reverse(
                        clip=segment_clip, start_speed=float(effect_args.start_speed), fast_slow_mode=True
                    )

                if e.method == EffectMethod.RAMP_SPEED_SEGMENTS:
                    effect_args: EffectArgs.PLAYBACK.RAMP_SPEED_SEGMENTS = e.args
                    segment_clip = playback_effects.ramp_speed_segments(
                        clip=segment_clip,
                        speeds=effect_args.speeds,
                        scale_speed_to_original_duration=effect_args.scale_speed_to_original_duration,
                        ramps_count_between_speed=effect_args.ramps_count_between_speed,
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
                    text=str(round(segment_config.start_time, 3)),
                    text_align="left",
                    font_size=14,
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
