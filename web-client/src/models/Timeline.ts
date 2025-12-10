export type TimelineConfig = {
  fps: number
  duration: number
  effects: TimelineSegmentEffect[]
  segments: TimelineSegment[]
}

export type TimelineSegmentEffect = {
  effect_type: string
  method: string
  args: []
}

export type TimelineSegment = {
  index: number
  start_time: number
  duration: number
  end_time: number
  is_split_screen: boolean
  effects: TimelineSegmentEffect[] | null
  videos: TimelineSegmentVideo[]
}

export type TimelineSegmentVideo = {
  path: string
  start_time: number
}
