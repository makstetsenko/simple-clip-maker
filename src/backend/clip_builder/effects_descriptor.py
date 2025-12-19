from dataclasses import dataclass
from enum import Enum
from typing import Literal, Self


class EffectType(Enum):
    ZOOM = "zoom"
    PAN = "pan"
    FLASH = "flash"
    CROP = "crop"
    PLAYBACK = "playback"


class EffectMethod(Enum):
    # Zoom methods
    ZOOM_IN__ZOOM_OUT = "zoom_in__zoom_out"
    ZOOM_OUT__ZOOM_IN = "zoom_out__zoom_in"
    ZOOM_IN_AT_CLIP_STARTS = "zoom_in_at_clip_starts"
    ZOOM_IN_AT_CLIP_ENDS = "zoom_in_at_clip_ends"
    ZOOM_BUMP = "zoom_bump"

    # Pan methods
    PAN_SIDE_TO_SIDE = "pan_side_to_side"

    # Flash methods
    FLASH = "flash"
    BURST_FLASH = "burst_flash"

    # Crop methods
    LINE_CROP = "line_crop"
    BURST_LINE_CROP = "burst_line_crop"
    FIT_VIDEO_INTO_FRAME_SIZE = "fit_video_into_frame_size"

    # Playback methods
    RAMP_SPEED_SEGMENTS = "ramp_speed_segments"
    FORWARD_REVERSE = "forward_reverse"


# Methods args description

EasingType = Literal["ease_out", "ease_in"]


class EffectArgsBase:
    def to_dict(self) -> dict:
        pass

    @staticmethod
    def from_dict(value: dict) -> Self:
        pass


class EffectArgs:

    class ZOOM:

        @dataclass
        class ZOOM_IN__ZOOM_OUT(EffectArgsBase):
            zoom_factor: float

            def to_dict(self) -> dict:
                return {"zoom_factor": self.zoom_factor}

            @staticmethod
            def from_dict(value: dict) -> Self:
                return EffectArgs.ZOOM.ZOOM_IN__ZOOM_OUT(zoom_factor=value["zoom_factor"])

        @dataclass
        class ZOOM_OUT__ZOOM_IN(EffectArgsBase):
            zoom_factor: float

            def to_dict(self) -> dict:
                return {"zoom_factor": self.zoom_factor}

            @staticmethod
            def from_dict(value: dict) -> Self:
                return EffectArgs.ZOOM.ZOOM_OUT__ZOOM_IN(zoom_factor=value["zoom_factor"])

        @dataclass
        class ZOOM_IN_AT_CLIP_STARTS(EffectArgsBase):
            zoom_factor: float
            zoom_duration: float
            easing: EasingType | None = "ease_out"

            def to_dict(self) -> dict:
                return {
                    "zoom_factor": self.zoom_factor,
                    "zoom_duration": self.zoom_duration,
                    "easing": self.easing,
                }

            @staticmethod
            def from_dict(value: dict) -> Self:
                return EffectArgs.ZOOM.ZOOM_IN_AT_CLIP_STARTS(
                    zoom_factor=value["zoom_factor"],
                    zoom_duration=value["zoom_duration"],
                    easing=value["easing"],
                )

        @dataclass
        class ZOOM_IN_AT_CLIP_ENDS(EffectArgsBase):
            zoom_factor: float
            zoom_duration: float
            easing: EasingType | None = "ease_out"

            def to_dict(self) -> dict:
                return {
                    "zoom_factor": self.zoom_factor,
                    "zoom_duration": self.zoom_duration,
                    "easing": self.easing,
                }

            @staticmethod
            def from_dict(value: dict) -> Self:
                return EffectArgs.ZOOM.ZOOM_IN_AT_CLIP_ENDS(
                    zoom_factor=value["zoom_factor"],
                    zoom_duration=value["zoom_duration"],
                    easing=value["easing"],
                )

        @dataclass
        class ZOOM_BUMP(EffectArgsBase):
            zoom_factor: float
            bump_count: int
            reverse: bool = False

            def to_dict(self) -> dict:
                return {
                    "zoom_factor": self.zoom_factor,
                    "bump_count": self.bump_count,
                    "reverse": self.reverse,
                }

            @staticmethod
            def from_dict(value: dict) -> Self:
                return EffectArgs.ZOOM.ZOOM_BUMP(
                    zoom_factor=value["zoom_factor"],
                    bump_count=value["bump_count"],
                    reverse=value["reverse"],
                )

    class PAN:

        @dataclass
        class PAN_SIDE_TO_SIDE(EffectArgsBase):
            pan: tuple[int, int]
            easing: EasingType = "ease_out"

            def to_dict(self) -> dict:
                return {
                    "pan": list(self.pan),
                    "easing": self.easing,
                }

            @staticmethod
            def from_dict(value: dict) -> Self:
                return EffectArgs.PAN.PAN_SIDE_TO_SIDE(
                    pan=(value["pan"][0], value["pan"][1]),
                    easing=value["easing"],
                )

    class FLASH:

        @dataclass
        class FLASH(EffectArgsBase):
            time: float
            flash_duration: float
            color: tuple[int, int, int] | None
            pick_random_flash_color: bool = False

            def to_dict(self) -> dict:
                return {
                    "time": self.time,
                    "flash_duration": self.flash_duration,
                    "color": list(self.color),
                    "pick_random_flash_color": self.pick_random_flash_color,
                }

            @staticmethod
            def from_dict(value: dict) -> Self:
                return EffectArgs.FLASH.FLASH(
                    time=value["time"],
                    flash_duration=value["flash_duration"],
                    color=(value["color"][0], value["color"][1], value["color"][2]),
                    pick_random_flash_color=value["pick_random_flash_color"],
                )

        @dataclass
        class BURST_FLASH(EffectArgsBase):
            flashes_count: int
            color: tuple[int, int, int] | None
            pick_random_flash_color: bool = False

            def to_dict(self) -> dict:
                return {
                    "flashes_count": self.flashes_count,
                    "color": list(self.color),
                    "pick_random_flash_color": self.pick_random_flash_color,
                }

            @staticmethod
            def from_dict(value: dict) -> Self:
                return EffectArgs.FLASH.BURST_FLASH(
                    flashes_count=value["flashes_count"],
                    color=(value["color"][0], value["color"][1], value["color"][2]),
                    pick_random_flash_color=value["pick_random_flash_color"],
                )

    class CROP:

        @dataclass
        class LINE_CROP(EffectArgsBase):
            line_number: int
            total_lines: int
            is_vertical: bool = True

            def to_dict(self) -> dict:
                return {
                    "line_number": self.line_number,
                    "total_lines": self.total_lines,
                    "is_vertical": self.is_vertical,
                }

            @staticmethod
            def from_dict(value: dict) -> Self:
                return EffectArgs.CROP.LINE_CROP(
                    line_number=value["line_number"],
                    total_lines=value["total_lines"],
                    is_vertical=value["is_vertical"],
                )

        @dataclass
        class BURST_LINE_CROP(EffectArgsBase):
            total_lines: int
            is_vertical: bool = True
            reverse_ordering: bool = False

            def to_dict(self) -> dict:
                return {
                    "total_lines": self.total_lines,
                    "is_vertical": self.is_vertical,
                    "reverse_ordering": self.reverse_ordering,
                }

            @staticmethod
            def from_dict(value: dict) -> Self:
                return EffectArgs.CROP.BURST_LINE_CROP(
                    total_lines=value["total_lines"],
                    is_vertical=value["is_vertical"],
                    reverse_ordering=value["reverse_ordering"],
                )

        @dataclass
        class FIT_VIDEO_INTO_FRAME_SIZE(EffectArgsBase):
            def to_dict(self) -> dict:
                return {}

            @staticmethod
            def from_dict(value: dict) -> Self:
                return EffectArgs.CROP.FIT_VIDEO_INTO_FRAME_SIZE()

    class PLAYBACK:

        @dataclass
        class FORWARD_REVERSE(EffectArgsBase):
            start_speed: float
            fast_slow_mode: bool = True

            def to_dict(self) -> dict:
                return {
                    "start_speed": self.start_speed,
                    "fast_slow_mode": self.fast_slow_mode,
                }

            @staticmethod
            def from_dict(value: dict) -> Self:
                return EffectArgs.PLAYBACK.FORWARD_REVERSE(
                    start_speed=value["start_speed"],
                    fast_slow_mode=value["fast_slow_mode"],
                )

        @dataclass
        class RAMP_SPEED_SEGMENTS(EffectArgsBase):
            speeds: list[float]
            scale_speed_to_original_duration: bool = True
            ramps_count_between_speed: int = 5

            def to_dict(self) -> dict:
                return {
                    "speeds": self.speeds,
                    "scale_speed_to_original_duration": self.scale_speed_to_original_duration,
                    "ramps_count_between_speed": self.ramps_count_between_speed,
                }

            @staticmethod
            def from_dict(value: dict) -> Self:
                return EffectArgs.PLAYBACK.RAMP_SPEED_SEGMENTS(
                    speeds=value["speeds"],
                    scale_speed_to_original_duration=value["scale_speed_to_original_duration"],
                    ramps_count_between_speed=value["ramps_count_between_speed"],
                )


def build_effect_args(effectType: EffectType, effectMethod: EffectMethod, value: dict) -> EffectArgsBase:
    if effectType == EffectType.ZOOM:

        if effectMethod == EffectMethod.ZOOM_IN__ZOOM_OUT:
            return EffectArgs.ZOOM.ZOOM_IN__ZOOM_OUT.from_dict(value)

        if effectMethod == EffectMethod.ZOOM_OUT__ZOOM_IN:
            return EffectArgs.ZOOM.ZOOM_OUT__ZOOM_IN.from_dict(value)

        if effectMethod == EffectMethod.ZOOM_IN_AT_CLIP_STARTS:
            return EffectArgs.ZOOM.ZOOM_IN_AT_CLIP_STARTS.from_dict(value)

        if effectMethod == EffectMethod.ZOOM_IN_AT_CLIP_ENDS:
            return EffectArgs.ZOOM.ZOOM_IN_AT_CLIP_ENDS.from_dict(value)

        if effectMethod == EffectMethod.ZOOM_BUMP:
            return EffectArgs.ZOOM.ZOOM_BUMP.from_dict(value)

    if effectType == EffectType.PAN:

        if effectMethod == EffectMethod.PAN_SIDE_TO_SIDE:
            return EffectArgs.ZOOM.PAN_SIDE_TO_SIDE.from_dict(value)

    if effectType == EffectType.FLASH:

        if effectMethod == EffectMethod.FLASH:
            return EffectArgs.FLASH.FLASH.from_dict(value)

        if effectMethod == EffectMethod.BURST_FLASH:
            return EffectArgs.FLASH.BURST_FLASH.from_dict(value)

    if effectType == EffectType.CROP:

        if effectMethod == EffectMethod.LINE_CROP:
            return EffectArgs.CROP.LINE_CROP.from_dict(value)

        if effectMethod == EffectMethod.BURST_LINE_CROP:
            return EffectArgs.CROP.BURST_LINE_CROP.from_dict(value)

        if effectMethod == EffectMethod.FIT_VIDEO_INTO_FRAME_SIZE:
            return EffectArgs.CROP.FIT_VIDEO_INTO_FRAME_SIZE()

    if effectType == EffectType.PLAYBACK:

        if effectMethod == EffectMethod.FORWARD_REVERSE:
            return EffectArgs.PLAYBACK.FORWARD_REVERSE.from_dict(value)

        if effectMethod == EffectMethod.RAMP_SPEED_SEGMENTS:
            return EffectArgs.PLAYBACK.RAMP_SPEED_SEGMENTS.from_dict(value)
