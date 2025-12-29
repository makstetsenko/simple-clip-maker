export type Timeline = {
  fps: number
  duration: number
  effects: Effect[]
  segments: TimelineSegment[]
  size: number[]
  audio_segments: AudioSegment[]
}

export type Effect = {
  id: string
  effect_type: string
  method: string
  args: object | null
}

export type TimelineSegment = {
  id: string
  index: number
  start_time: number
  duration: number
  end_time: number
  is_split_screen: boolean
  effects: Effect[] | null
  videos: SegmentVideo[]
  etag: string
}

export type SegmentVideo = {
  id: string
  path: string
  start_time: number
}

export type AudioSegment = {
  index: number
  duration: number
  start_time: number
  end_time: number
  energy: number
  intensity_band: string
  energy_delta: number
  trend: string
  similar_group: number
  reverse_candidate: boolean
}
