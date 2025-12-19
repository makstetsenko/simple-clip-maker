import { EffectMethod, EffectType } from '@/shared/models/TimelineModel'

export function getDefaultArgs(effectType: EffectType, effectMethod: EffectMethod) {
  if (effectType == EffectType.Zoom) {
    if (effectMethod === EffectMethod.ZOOM_IN__ZOOM_OUT) {
      return { zoom_factor: 0 }
    }
    if (effectMethod === EffectMethod.ZOOM_OUT__ZOOM_IN) {
      return { zoom_factor: 0 }
    }
    if (effectMethod === EffectMethod.ZOOM_IN_AT_CLIP_STARTS) {
      return {
        zoom_factor: 0,
        zoom_duration: 0,
        easing: 'ease_out',
      }
    }
    if (effectMethod === EffectMethod.ZOOM_IN_AT_CLIP_ENDS) {
      return {
        zoom_factor: 0,
        zoom_duration: 0,
        easing: 'ease_out',
      }
    }
    if (effectMethod === EffectMethod.ZOOM_BUMP) {
      return {
        zoom_factor: 0,
        bump_count: 0,
        reverse: 0,
      }
    }
  }

  if (effectType == EffectType.Pan) {
    if (effectMethod === EffectMethod.PAN_SIDE_TO_SIDE) {
      return {
        pan: [0, 0],
        easing: 'ease_out',
      }
    }
  }

  if (effectType == EffectType.Flash) {
    if (effectMethod === EffectMethod.FLASH) {
      return {
        time: 0,
        flash_duration: 0,
        color: [0, 0, 0],
        pick_random_flash_color: 0,
      }
    }
    if (effectMethod === EffectMethod.BURST_FLASH) {
      return {
        flashes_count: 0,
        color: [0, 0, 0],
        pick_random_flash_color: 0,
      }
    }
  }

  if (effectType == EffectType.Crop) {
    if (effectMethod === EffectMethod.LINE_CROP) {
      return {
        line_number: 0,
        total_lines: 0,
        is_vertical: 0,
      }
    }
    if (effectMethod === EffectMethod.FIT_VIDEO_INTO_FRAME_SIZE) {
      return {}
    }
    if (effectMethod === EffectMethod.BURST_LINE_CROP) {
      return {
        reverse_ordering: 0,
        total_lines: 0,
        is_vertical: 0,
      }
    }
  }

  if (effectType == EffectType.Playback) {
    if (effectMethod === EffectMethod.FORWARD_REVERSE) {
      return {
        start_speed: 0,
        fast_slow_mode: 0,
      }
    }
    if (effectMethod === EffectMethod.RAMP_SPEED_SEGMENTS) {
      return {
        speeds: 0,
        scale_speed_to_original_duration: 0,
        ramps_count_between_speed: 0,
      }
    }
  }

  return null
  // throw new Error('Cannot get default args object')
}
