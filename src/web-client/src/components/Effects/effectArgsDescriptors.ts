import { EffectType, EffectMethod } from '@/shared/models/TimelineModel'

export enum ArgPropType {
  Text,
  Number,
  Bool,
  Color,
  Tuple,
  NumberArray,
}

export interface EffectArg {
  props: ArgPropDescriptor[]
  default: object
}

export interface ArgPropDescriptor {
  key: string
  label: string
  propType: ArgPropType
}

export function getEffectArgDescriptor(
  effectType: EffectType,
  effectMethod: EffectMethod,
): EffectArg {
  if (map.has(effectType) && map.get(effectType)!.has(effectMethod)) {
    return map.get(effectType)!.get(effectMethod)!
  }

  return {
    default: {},
    props: [],
  }
}

const map = new Map<EffectType, Map<EffectMethod, EffectArg>>([
  [
    EffectType.Zoom,
    new Map([
      [
        EffectMethod.ZOOM_IN__ZOOM_OUT,
        {
          default: { zoom_factor: 1.2 },
          props: [
            {
              key: 'zoom_factor',
              label: 'Zoom',
              propType: ArgPropType.Number,
            },
          ],
        },
      ],

      [
        EffectMethod.ZOOM_OUT__ZOOM_IN,
        {
          default: { zoom_factor: 1.2 },
          props: [
            {
              key: 'zoom_factor',
              label: 'Zoom',
              propType: ArgPropType.Number,
            },
          ],
        },
      ],

      [
        EffectMethod.ZOOM_IN_AT_CLIP_STARTS,
        {
          default: {
            zoom_factor: 1.2,
            zoom_duration: 0.25,
            easing: 'ease_out',
          },
          props: [
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
          ],
        },
      ],
      [
        EffectMethod.ZOOM_IN_AT_CLIP_ENDS,
        {
          default: {
            zoom_factor: 1.2,
            zoom_duration: 0.25,
            easing: 'ease_out',
          },
          props: [
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
          ],
        },
      ],

      [
        EffectMethod.ZOOM_BUMP,
        {
          default: {
            zoom_factor: 1.2,
            bump_count: 3,
            reverse: false,
          },
          props: [
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
          ],
        },
      ],
    ]),
  ],

  [
    EffectType.Pan,
    new Map([
      [
        EffectMethod.PAN_SIDE_TO_SIDE,
        {
          default: {
            pan: [0, 0],
            easing: 'ease_out',
          },
          props: [
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
          ],
        },
      ],
    ]),
  ],

  [
    EffectType.Flash,
    new Map([
      [
        EffectMethod.FLASH,
        {
          default: {
            time: 0,
            flash_duration: 0.25,
            color: [255, 255, 255],
            pick_random_flash_color: false,
          },
          props: [
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
          ],
        },
      ],

      [
        EffectMethod.BURST_FLASH,
        {
          default: {
            flashes_count: 3,
            color: [255, 255, 255],
            pick_random_flash_color: true,
          },
          props: [
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
          ],
        },
      ],
    ]),
  ],

  [
    EffectType.Crop,
    new Map([
      [
        EffectMethod.LINE_CROP,
        {
          default: {
            line_number: 1,
            total_lines: 3,
            is_vertical: true,
          },
          props: [
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
          ],
        },
      ],
      [
        EffectMethod.FIT_VIDEO_INTO_FRAME_SIZE,
        {
          default: {},
          props: [],
        },
      ],

      [
        EffectMethod.BURST_LINE_CROP,
        {
          default: {
            reverse_ordering: false,
            total_lines: 3,
            is_vertical: true,
          },
          props: [
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
          ],
        },
      ],
    ]),
  ],

  [
    EffectType.Playback,
    new Map([
      [
        EffectMethod.FORWARD_REVERSE,
        {
          default: {
            start_speed: 1.2,
            fast_slow_mode: true,
          },
          props: [
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
          ],
        },
      ],

      [
        EffectMethod.RAMP_SPEED_SEGMENTS,
        {
          default: {
            scale_speed_to_original_duration: true,
            ramps_count_between_speed: 5,
            speeds: [1, 1],
          },
          props: [
            {
              key: 'ramps_count_between_speed',
              label: 'Ramps between speeds',
              propType: ArgPropType.Number,
            },
            {
              key: 'scale_speed_to_original_duration',
              label: 'Scale to original duration?',
              propType: ArgPropType.Bool,
            },
            {
              key: 'speeds',
              label: 'Speeds',
              propType: ArgPropType.NumberArray,
            },
          ],
        },
      ],
    ]),
  ],
])
