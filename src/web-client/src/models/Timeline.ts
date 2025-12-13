export type TimelineConfig = {
  fps: number
  duration: number
  effects: TimelineSegmentEffect[]
  segments: TimelineSegment[]
}

export type TimelineSegmentEffect = {
  id: string,
  effect_type: string
  method: string
  args: object | null
}

export type TimelineSegment = {
  id: string,
  index: number
  start_time: number
  duration: number
  end_time: number
  is_split_screen: boolean
  effects: TimelineSegmentEffect[] | null
  videos: TimelineSegmentVideo[]
}

export type TimelineSegmentVideo = {
  id: string,
  path: string
  start_time: number
}
