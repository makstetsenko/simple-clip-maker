import { EffectType, EffectMethod } from '@/shared/models/TimelineModel'

export enum ArgPropType {
  Text,
  Number,
  Bool,
  Color,
  Tuple,
  NumberArray,
}

export interface ArgPropDescriptor {
  key: string
  label: string
  propType: ArgPropType
}

export function getDescriptors(
  effectType: EffectType,
  effectMethod: EffectMethod,
): ArgPropDescriptor[] {
  if (effectType == EffectType.Zoom) {
    if (effectMethod === EffectMethod.ZOOM_IN__ZOOM_OUT) {
      return [
        {
          key: 'zoom_factor',
          label: 'Zoom',
          propType: ArgPropType.Number,
        },
      ]
    }
    if (effectMethod === EffectMethod.ZOOM_OUT__ZOOM_IN) {
      return [
        {
          key: 'zoom_factor',
          label: 'Zoom',
          propType: ArgPropType.Number,
        },
      ]
    }
    if (effectMethod === EffectMethod.ZOOM_IN_AT_CLIP_STARTS) {
      return [
        {
          key: 'zoom_factor',
          label: 'Zoom',
          propType: ArgPropType.Number,
        },
        {
          key: 'zoom_duration',
          label: 'Duration',
          propType: ArgPropType.Number,
        },
        {
          key: 'easing',
          label: 'Easing',
          propType: ArgPropType.Text,
        },
      ]
    }
    if (effectMethod === EffectMethod.ZOOM_IN_AT_CLIP_ENDS) {
      return [
        {
          key: 'zoom_factor',
          label: 'Zoom',
          propType: ArgPropType.Number,
        },
        {
          key: 'zoom_duration',
          label: 'Duration',
          propType: ArgPropType.Number,
        },
        {
          key: 'easing',
          label: 'Easing',
          propType: ArgPropType.Text,
        },
      ]
    }
    if (effectMethod === EffectMethod.ZOOM_BUMP) {
      return [
        {
          key: 'zoom_factor',
          label: 'Zoom',
          propType: ArgPropType.Number,
        },
        {
          key: 'bump_count',
          label: 'Bump count',
          propType: ArgPropType.Number,
        },
        {
          key: 'reverse',
          label: 'Reverse?',
          propType: ArgPropType.Bool,
        },
      ]
    }
  }

  if (effectType == EffectType.Pan) {
    if (effectMethod === EffectMethod.PAN_SIDE_TO_SIDE) {
      return [
        {
          key: 'pan',
          label: 'Pan',
          propType: ArgPropType.Tuple,
        },
        {
          key: 'easing',
          label: 'Easing',
          propType: ArgPropType.Text,
        },
      ]
    }
  }

  if (effectType == EffectType.Flash) {
    if (effectMethod === EffectMethod.FLASH) {
      return [
        {
          key: 'time',
          label: 'Flash at time',
          propType: ArgPropType.Number,
        },
        {
          key: 'flash_duration',
          label: 'Duration',
          propType: ArgPropType.Number,
        },
        {
          key: 'color',
          label: 'Color',
          propType: ArgPropType.Color,
        },
        {
          key: 'pick_random_flash_color',
          label: 'Random color?',
          propType: ArgPropType.Bool,
        },
      ]
    }
    if (effectMethod === EffectMethod.BURST_FLASH) {
      return [
        {
          key: 'flashes_count',
          label: 'Count',
          propType: ArgPropType.Number,
        },
        {
          key: 'color',
          label: 'Color',
          propType: ArgPropType.Color,
        },
        {
          key: 'pick_random_flash_color',
          label: 'Random color?',
          propType: ArgPropType.Bool,
        },
      ]
    }
  }

  if (effectType == EffectType.Crop) {
    if (effectMethod === EffectMethod.LINE_CROP) {
      return [
        {
          key: 'line_number',
          label: 'Lines number',
          propType: ArgPropType.Number,
        },
        {
          key: 'total_lines',
          label: 'Total lines',
          propType: ArgPropType.Number,
        },
        {
          key: 'is_vertical',
          label: 'Vertical lines?',
          propType: ArgPropType.Bool,
        },
      ]
    }
    if (effectMethod === EffectMethod.FIT_VIDEO_INTO_FRAME_SIZE) {
      return []
    }
    if (effectMethod === EffectMethod.BURST_LINE_CROP) {
      return [
        {
          key: 'reverse_ordering',
          label: 'Reverse?',
          propType: ArgPropType.Bool,
        },
        {
          key: 'total_lines',
          label: 'Total lines',
          propType: ArgPropType.Number,
        },
        {
          key: 'is_vertical',
          label: 'Vertical lines?',
          propType: ArgPropType.Bool,
        },
      ]
    }
  }

  if (effectType == EffectType.Playback) {
    if (effectMethod === EffectMethod.FORWARD_REVERSE) {
      return [
        {
          key: 'start_speed',
          label: 'Start speed',
          propType: ArgPropType.Number,
        },
        {
          key: 'fast_slow_mode',
          label: 'Fast -> Slow -> Fast?',
          propType: ArgPropType.Bool,
        },
      ]
    }
    if (effectMethod === EffectMethod.RAMP_SPEED_SEGMENTS) {
      return [
        {
          key: 'speeds',
          label: 'Speeds',
          propType: ArgPropType.NumberArray,
        },
        {
          key: 'scale_speed_to_original_duration',
          label: 'Scale to original duration?',
          propType: ArgPropType.Bool,
        },
        {
          key: 'ramps_count_between_speed',
          label: 'Ramps between speeds',
          propType: ArgPropType.Number,
        },
      ]
    }
  }

  return []
  // throw new Error('Cannot get args descriptor')
}
