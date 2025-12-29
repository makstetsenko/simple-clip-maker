import type {
  AudioSegment,
  Effect,
  SegmentVideo,
  Timeline,
  TimelineSegment,
} from '@/services/models/Timeline'
import { EffectMethod, EffectType } from '../models/TimelineModel'
import type {
  AudioSegmentModel,
  EffectModel,
  SegmentVideoModel,
  TimelineModel,
  TimelineSegmentModel,
} from '../models/TimelineModel'
import { v4 as uuidv4 } from 'uuid'


export const mapTimeline = (model: TimelineModel): Timeline => {
  return {
    fps: model.fps,
    duration: model.duration,
    effects: model.effects?.map((x) => mapEffect(x)),
    segments: model.segments.map((x) => mapSegment(x)),
    audio_segments: model.audioSegments?.map((x) => mapAudioSegment(x)) || [],
    size: [...model.size],
  } as Timeline
}

export const mapAudioSegment = (model: AudioSegmentModel): AudioSegment => {
  return {
    index: model.index,
    duration: model.duration,
    start_time: model.startTime,
    end_time: model.endTime,
    energy: model.energy,
    intensity_band: model.intensity_band,
    energy_delta: model.energyDelta,
    trend: model.trend,
    similar_group: model.similar_group,
    reverse_candidate: model.reverse_candidate,
  } as AudioSegment
}

export const mapSegment = (model: TimelineSegmentModel): TimelineSegment => {
  return {
    id: model.id,
    duration: model.duration,
    end_time: model.endTime,
    start_time: model.startTime,
    index: model.index,
    is_split_screen: model.splitScreen,
    videos: model.videos.map((v) => mapVideo(v)),
    effects: model.effects?.map((e) => mapEffect(e)),
    etag: model.etag ?? uuidv4()
  } as TimelineSegment
}

export const mapVideo = (model: SegmentVideoModel): SegmentVideo => {
  return { id: model.id, path: model.path, start_time: model.startTime } as SegmentVideo
}

export const mapEffect = (model: EffectModel): Effect => {
  return {
    id: model.id,
    effect_type: mapEffectType(model.effectType),
    method: mapEffectMethod(model.method),
    args: model.args,
  } as Effect
}

const mapEffectMethod = (method: EffectMethod): string => {
  if (method === EffectMethod.ZOOM_IN__ZOOM_OUT) return 'zoom_in__zoom_out'
  if (method === EffectMethod.ZOOM_OUT__ZOOM_IN) return 'zoom_out__zoom_in'
  if (method === EffectMethod.ZOOM_IN_AT_CLIP_STARTS) return 'zoom_in_at_clip_starts'
  if (method === EffectMethod.ZOOM_IN_AT_CLIP_ENDS) return 'zoom_in_at_clip_ends'
  if (method === EffectMethod.ZOOM_BUMP) return 'zoom_bump'
  if (method === EffectMethod.PAN_SIDE_TO_SIDE) return 'pan_side_to_side'
  if (method === EffectMethod.FLASH) return 'flash'
  if (method === EffectMethod.BURST_FLASH) return 'burst_flash'
  if (method === EffectMethod.LINE_CROP) return 'line_crop'
  if (method === EffectMethod.BURST_LINE_CROP) return 'burst_line_crop'
  if (method === EffectMethod.FIT_VIDEO_INTO_FRAME_SIZE) return 'fit_video_into_frame_size'
  if (method === EffectMethod.RAMP_SPEED_SEGMENTS) return 'ramp_speed_segments'
  if (method === EffectMethod.FORWARD_REVERSE) return 'forward_reverse'

  throw new Error(`Cannot map method ${method}`)
}

const mapEffectType = (effectType: EffectType): string => {
  if (effectType === EffectType.Zoom) return 'zoom'
  if (effectType === EffectType.Pan) return 'pan'
  if (effectType === EffectType.Flash) return 'flash'
  if (effectType === EffectType.Crop) return 'crop'
  if (effectType === EffectType.Playback) return 'playback'

  throw new Error(`Cannot map effectType ${effectType}`)
}
