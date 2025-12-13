<template>
  <div>
    <ZOOM_IN__ZOOM_OUT_Args
      @on-args-changed="onArgsChanged"
      :args="props.args!"
      v-if="props.effectType === EffectType.Zoom && props.method === EffectMethod.ZOOM_IN__ZOOM_OUT"
    />

    <ZOOM_OUT__ZOOM_IN_Args
      @on-args-changed="onArgsChanged"
      :args="props.args!"
      v-if="props.effectType === EffectType.Zoom && props.method === EffectMethod.ZOOM_OUT__ZOOM_IN"
    />

    <ZOOM_IN_AT_CLIP_STARTS_Args
      @on-args-changed="onArgsChanged"
      :args="props.args!"
      v-if="
        props.effectType === EffectType.Zoom && props.method === EffectMethod.ZOOM_IN_AT_CLIP_STARTS
      "
    />

    <ZOOM_IN_AT_CLIP_ENDS_Args
      @on-args-changed="onArgsChanged"
      :args="props.args!"
      v-if="
        props.effectType === EffectType.Zoom && props.method === EffectMethod.ZOOM_IN_AT_CLIP_ENDS
      "
    />

    <ZOOM_BUMP_Args
      @on-args-changed="onArgsChanged"
      :args="props.args!"
      v-if="props.effectType === EffectType.Zoom && props.method === EffectMethod.ZOOM_BUMP"
    />

    <PAN_SIDE_TO_SIDE_Args
      @on-args-changed="onArgsChanged"
      :args="props.args!"
      v-if="props.effectType === EffectType.Pan && props.method === EffectMethod.PAN_SIDE_TO_SIDE"
    />

    <FLASH_Args
      @on-args-changed="onArgsChanged"
      :args="props.args!"
      v-if="props.effectType === EffectType.Flash && props.method === EffectMethod.FLASH"
    />

    <BURST_FLASH_Args
      @on-args-changed="onArgsChanged"
      :args="props.args!"
      v-if="props.effectType === EffectType.Flash && props.method === EffectMethod.BURST_FLASH"
    />

    <LINE_CROP_Args
      @on-args-changed="onArgsChanged"
      :args="props.args!"
      v-if="props.effectType === EffectType.Crop && props.method === EffectMethod.LINE_CROP"
    />

    <BURST_LINE_CROP_Args
      @on-args-changed="onArgsChanged"
      :args="props.args!"
      v-if="props.effectType === EffectType.Crop && props.method === EffectMethod.BURST_LINE_CROP"
    />

    <FORWARD_REVERSE_Args
      @on-args-changed="onArgsChanged"
      :args="props.args!"
      v-if="
        props.effectType === EffectType.Playback && props.method === EffectMethod.FORWARD_REVERSE
      "
    />

    <RAMP_SPEED_SEGMENTS_Args
      @on-args-changed="onArgsChanged"
      :args="props.args!"
      v-if="
        props.effectType === EffectType.Playback &&
        props.method === EffectMethod.RAMP_SPEED_SEGMENTS
      "
    />
  </div>
</template>

<script setup lang="ts">
import ZOOM_IN__ZOOM_OUT_Args from './ZOOM_IN__ZOOM_OUT_Args.vue'
import ZOOM_OUT__ZOOM_IN_Args from './ZOOM_OUT__ZOOM_IN_Args.vue'
import ZOOM_IN_AT_CLIP_STARTS_Args from './ZOOM_IN_AT_CLIP_STARTS_Args.vue'
import ZOOM_IN_AT_CLIP_ENDS_Args from './ZOOM_IN_AT_CLIP_ENDS_Args.vue'
import ZOOM_BUMP_Args from './ZOOM_BUMP_Args.vue'
import PAN_SIDE_TO_SIDE_Args from './PAN_SIDE_TO_SIDE_Args.vue'
import FLASH_Args from './FLASH_Args.vue'
import BURST_FLASH_Args from './BURST_FLASH_Args.vue'
import LINE_CROP_Args from './LINE_CROP_Args.vue'
import BURST_LINE_CROP_Args from './BURST_LINE_CROP_Args.vue'
import FORWARD_REVERSE_Args from './FORWARD_REVERSE_Args.vue'
import RAMP_SPEED_SEGMENTS_Args from './RAMP_SPEED_SEGMENTS_Args.vue'

import { EffectMethod, EffectType } from '@/shared/models/TimelineModel.ts'

interface Props {
  id: string
  effectType: EffectType
  method: EffectMethod
  args: object | null | undefined
}

const props = defineProps<Props>()
const emits = defineEmits(['onArgsChanged'])

const onArgsChanged = (newArgs: object) => {
  emits('onArgsChanged', newArgs)
}
</script>
