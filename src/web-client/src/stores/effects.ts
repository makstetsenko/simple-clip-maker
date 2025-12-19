import type { EffectModel } from '@/shared/models/TimelineModel'
import { defineStore } from 'pinia'
import { v4 as uuidv4 } from 'uuid'

interface EffectsStore {
  rememberedEffect: EffectModel | null
}

export const useEffectsStore = defineStore('effects', {
  state: (): EffectsStore => {
    return {
      rememberedEffect: null,
    }
  },
  actions: {
    rememberEffect(effect: EffectModel) {
      this.rememberedEffect = effect
    },
    pasteAsNewEffect(): EffectModel | null {
      if (!this.rememberedEffect) return null

      return {
        id: uuidv4(),
        args: { ...this.rememberedEffect.args },
        effectType: this.rememberedEffect.effectType,
        method: this.rememberedEffect.method,
      } as EffectModel
    },
  },
  getters: {},
})
