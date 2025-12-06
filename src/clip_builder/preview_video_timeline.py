import json
import logging

from moviepy import VideoFileClip, concatenate_videoclips, ImageClip, TextClip, CompositeVideoClip
from tqdm import tqdm

from src.clip_builder.audio_analyzer import AudioAnalyzeResult, BeatSegment
from src.clip_builder.effects.crop import fit_video_into_frame_size
from src.clip_builder.effects.playback import forward_reverse
from src.clip_builder.video_resolution import VideoResolution

logger = logging.getLogger(__name__)


class PreviewVideoTimeline:

    def __init__(
        self,
        fps: int,
        resolution: VideoResolution,
        audio_analysis: AudioAnalyzeResult,
        temp_path: str,
    ):
        self.fps = fps
        self.resolution = resolution
        self.audio_analysis = audio_analysis
        self.temp_path = temp_path

    def build_timeline_clip(self) -> str:
        segments = self.build_segment_clips()
        clips = [VideoFileClip(s) for s in segments]

        chained_clip_path = f"{self.temp_path}/preview_chained_clip.mp4"
        chained_clip = concatenate_videoclips(clips=clips, method="compose")
        chained_clip.write_videofile(chained_clip_path, audio=None, fps=self.fps)

        for c in clips:
            c.close()

        chained_clip.close()

        return chained_clip_path

    def build_segment_clips(self):
        segment_clips = []

        with tqdm(total=len(self.audio_analysis.beat_segments)) as progress_bar:
            progress_bar.set_description("Building segments")
            for segment in self.audio_analysis.beat_segments:
                segment_clips.append(self.get_segment_clip(segment))
                progress_bar.update(1)

        return segment_clips

    def get_segment_clip(self, segment: BeatSegment):
        requires_frame_drift = segment.duration <= 0.5
        padding = (1.0 / self.fps) if requires_frame_drift else 0

        clip_duration = segment.duration + padding

        clip = ImageClip("./static/preview-frame.jpg", duration=clip_duration).with_fps(self.fps)
        clip = fit_video_into_frame_size(self.resolution.size, clip)
        text_clip_overlay = TextClip(
            text=json.dumps(segment.to_json(), indent=4, sort_keys=False, ensure_ascii=False),
            text_align="left",
            font_size=24,
            size=self.resolution.size,
            duration=clip_duration,
        ).with_fps(self.fps)

        clip_path = f"{self.temp_path}/preview_{segment.index}.mp4"

        # if segment.reverse_candidate:
        #     frame_transformations = zoom_effect_preset.zoom_out__zoom_in(clip.duration, self.resolution.size, 1.1)
        # else:
        #     frame_transformations = zoom_effect_preset.zoom_in__zoom_out(clip.duration, self.resolution.size, 1.1)

        # frame_transformations = zoom_effect_preset.zoom_in_at_clip_starts(
        #     clip_duration=clip.duration, clip_size=self.resolution.size, zoom_duration=clip.duration, zoom_factor=1.5
        # )

        # clip: VideoClip = apply_transformations(
        #     clip=clip,
        #     frame_transformations=frame_transformations,
        # )

        # clip = apply_composition(clip, overlay_clips=get_flash_clips(self.resolution.size, [0], 0.15))

        # clip = line_crop(clip, segment.index % 5 + 1, 5,is_vertical_line=True)

        # clip = crop_effect_preset.line_crop(clip, segment.index % 5 + 1, 5,is_vertical=True)

        # clip = crop_effect_preset.burst_line_crop(clip, 3,is_vertical=True, reverse_ordering=True)

        # clip = crop_effect_preset.burst_line_crop(clip, 10,is_vertical=False)

        # clip = flash_effect_preset.burst_flash(clip, 4)

        # clip = flash_effect_preset.burst_flash(clip, 4, color=(234, 55, 151))

        # clip = flash_effect_preset.burst_flash(clip, 4, pick_random_flash_color=True)

        # clip = flash_effect_preset.flash_at_clip_start(clip, flash_duration=0.15, pick_random_flash_color=True)

        clip = forward_reverse(clip)

        composed_clip = CompositeVideoClip(clips=[clip, text_clip_overlay], size=self.resolution.size)
        composed_clip.write_videofile(filename=clip_path, audio=None, logger=None, fps=self.fps)

        clip.close()
        composed_clip.close()
        return clip_path
