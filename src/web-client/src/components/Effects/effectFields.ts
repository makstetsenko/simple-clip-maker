import { EffectMethod, EffectType } from '@/shared/models/TimelineModel'

export function getEffectTypesFields(): { label: string; value: EffectType }[] {
  return [
    {
      label: EffectType[EffectType.Crop],
      value: EffectType.Crop,
    },
    {
      label: EffectType[EffectType.Flash],
      value: EffectType.Flash,
    },
    {
      label: EffectType[EffectType.Pan],
      value: EffectType.Pan,
    },
    {
      label: EffectType[EffectType.Playback],
      value: EffectType.Playback,
    },
    {
      label: EffectType[EffectType.Zoom],
      value: EffectType.Zoom,
    },
  ]
}

export function getEffectMethodFields(
  effectType: EffectType,
): { label: string; value: EffectMethod }[] {
  if (effectType == EffectType.Zoom)
    return [
      {
        label: EffectMethod[EffectMethod.ZOOM_IN__ZOOM_OUT],
        value: EffectMethod.ZOOM_IN__ZOOM_OUT,
      },
      {
        label: EffectMethod[EffectMethod.ZOOM_OUT__ZOOM_IN],
        value: EffectMethod.ZOOM_OUT__ZOOM_IN,
      },
      {
        label: EffectMethod[EffectMethod.ZOOM_IN_AT_CLIP_STARTS],
        value: EffectMethod.ZOOM_IN_AT_CLIP_STARTS,
      },
      {
        label: EffectMethod[EffectMethod.ZOOM_IN_AT_CLIP_ENDS],
        value: EffectMethod.ZOOM_IN_AT_CLIP_ENDS,
      },
      {
        label: EffectMethod[EffectMethod.ZOOM_BUMP],
        value: EffectMethod.ZOOM_BUMP,
      },
    ]

  if (effectType == EffectType.Pan)
    return [
      {
        label: EffectMethod[EffectMethod.PAN_SIDE_TO_SIDE],
        value: EffectMethod.PAN_SIDE_TO_SIDE,
      },
    ]

  if (effectType == EffectType.Flash)
    return [
      {
        label: EffectMethod[EffectMethod.FLASH],
        value: EffectMethod.FLASH,
      },
      {
        label: EffectMethod[EffectMethod.BURST_FLASH],
        value: EffectMethod.BURST_FLASH,
      },
    ]

  if (effectType == EffectType.Crop)
    return [
      {
        label: EffectMethod[EffectMethod.LINE_CROP],
        value: EffectMethod.LINE_CROP,
      },
      {
        label: EffectMethod[EffectMethod.BURST_LINE_CROP],
        value: EffectMethod.BURST_LINE_CROP,
      },
      {
        label: EffectMethod[EffectMethod.FIT_VIDEO_INTO_FRAME_SIZE],
        value: EffectMethod.FIT_VIDEO_INTO_FRAME_SIZE,
      },
    ]

  if (effectType == EffectType.Playback)
    return [
      {
        label: EffectMethod[EffectMethod.FORWARD_REVERSE],
        value: EffectMethod.FORWARD_REVERSE,
      },
      {
        label: EffectMethod[EffectMethod.RAMP_SPEED_SEGMENTS],
        value: EffectMethod.RAMP_SPEED_SEGMENTS,
      },
    ]

  throw new Error(`Cannot get effect methods for effectType ${effectType}`)
}
