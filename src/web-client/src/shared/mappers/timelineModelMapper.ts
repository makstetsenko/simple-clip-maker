import type { Effect, SegmentVideo, Timeline, TimelineSegment } from '@/services/models/Timeline'
import { EffectMethod, EffectType } from '../models/TimelineModel'
import type {
  EffectModel,
  SegmentVideoModel,
  TimelineModel,
  TimelineSegmentModel,
} from '../models/TimelineModel'

export const mapTimelineModel = (timelineConfig: Timeline): TimelineModel => {
  return {
    fps: timelineConfig.fps,
    duration: timelineConfig.duration,
    effects: timelineConfig.effects.map((x) => mapEffectModel(x)),
    segments: timelineConfig.segments.map((x) => mapSegmentModel(x)),
    size: [...timelineConfig.size],
  } as TimelineModel
}

export const mapSegmentModel = (segment: TimelineSegment): TimelineSegmentModel => {
  return {
    id: segment.id,
    duration: segment.duration,
    endTime: segment.end_time,
    startTime: segment.start_time,
    index: segment.index,
    splitScreen: segment.is_split_screen,
    videos: segment.videos.map((v) => mapVideoModel(v)),
    effects: segment.effects?.map((e) => mapEffectModel(e)) || [],
  } as TimelineSegmentModel
}

export const mapVideoModel = (video: SegmentVideo): SegmentVideoModel => {
  return { id: video.id, path: video.path, startTime: video.start_time } as SegmentVideoModel
}

export const mapEffectModel = (effect: Effect): EffectModel => {
  return {
    id: effect.id,
    effectType: mapEffectType(effect.effect_type),
    method: mapEffectMethod(effect.method),
    args: effect.args || {},
  } as EffectModel
}

const mapEffectMethod = (method: string): EffectMethod => {
  if (method === 'zoom_in__zoom_out') return EffectMethod.ZOOM_IN__ZOOM_OUT
  if (method === 'zoom_out__zoom_in') return EffectMethod.ZOOM_OUT__ZOOM_IN
  if (method === 'zoom_in_at_clip_starts') return EffectMethod.ZOOM_IN_AT_CLIP_STARTS
  if (method === 'zoom_in_at_clip_ends') return EffectMethod.ZOOM_IN_AT_CLIP_ENDS
  if (method === 'zoom_bump') return EffectMethod.ZOOM_BUMP
  if (method === 'pan_side_to_side') return EffectMethod.PAN_SIDE_TO_SIDE
  if (method === 'flash') return EffectMethod.FLASH
  if (method === 'burst_flash') return EffectMethod.BURST_FLASH
  if (method === 'line_crop') return EffectMethod.LINE_CROP
  if (method === 'burst_line_crop') return EffectMethod.BURST_LINE_CROP
  if (method === 'fit_video_into_frame_size') return EffectMethod.FIT_VIDEO_INTO_FRAME_SIZE
  if (method === 'ramp_speed_segments') return EffectMethod.RAMP_SPEED_SEGMENTS
  if (method === 'forward_reverse') return EffectMethod.FORWARD_REVERSE

  throw new Error(`Cannot map method ${method}`)
}

const mapEffectType = (effectType: string): EffectType => {
  if (effectType === 'zoom') return EffectType.Zoom
  if (effectType === 'pan') return EffectType.Pan
  if (effectType === 'flash') return EffectType.Flash
  if (effectType === 'crop') return EffectType.Crop
  if (effectType === 'playback') return EffectType.Playback

  throw new Error(`Cannot map effectType ${effectType}`)
}
