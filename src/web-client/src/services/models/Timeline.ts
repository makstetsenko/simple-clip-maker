export type Timeline = {
  fps: number
  duration: number
  effects: Effect[]
  segments: TimelineSegment[]
  size: number[]
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
}

export type SegmentVideo = {
  id: string
  path: string
  start_time: number
}
