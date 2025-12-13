export interface TimelineModel {
  fps: number
  duration: number
  effects: EffectModel[] | null | undefined
  segments: TimelineSegmentModel[]
}

export interface TimelineSegmentModel {
  id: string
  index: number
  startTime: number
  duration: number
  endTime: number
  splitScreen: boolean
  effects: EffectModel[] | null | undefined
  videos: SegmentVideoModel[]
}

export interface EffectModel {
  id: string
  effectType: EffectType
  method: EffectMethod
  args: object | null
}

export interface SegmentVideoModel {
  id: string
  path: string
  startTime: number
}

export enum EffectType {
  Zoom,
  Flash,
  Crop,
  Pan,
  Playback,
}

export enum EffectMethod {
  ZOOM_IN__ZOOM_OUT,
  ZOOM_OUT__ZOOM_IN,
  ZOOM_IN_AT_CLIP_STARTS,
  ZOOM_IN_AT_CLIP_ENDS,
  ZOOM_BUMP,

  PAN_SIDE_TO_SIDE,

  FLASH,
  BURST_FLASH,

  LINE_CROP,
  BURST_LINE_CROP,
  FIT_VIDEO_INTO_FRAME_SIZE,

  RAMP_SPEED_SEGMENTS,
  FORWARD_REVERSE,
}
