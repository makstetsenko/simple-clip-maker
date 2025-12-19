import { defineStore } from 'pinia'
import type { TimelineModel, TimelineSegmentModel } from '@/shared/models/TimelineModel'

interface TimelineStoreState {
  timeline: TimelineModel | null
  selectedSegments: TimelineSegmentModel[]
}

export const useTimelineStore = defineStore('timeline', {
  state: (): TimelineStoreState => {
    return {
      timeline: null,
      selectedSegments: [],
    }
  },
  actions: {
    setProject(timeline: TimelineModel) {
      this.timeline = timeline
    },
    appendSelectSegment(id: string) {
      if (!this.timeline) return

      const index = this.timeline.segments.findIndex((x) => x.id === id)!
      this.selectedSegments.push(this.timeline.segments[index]!)
    },
    appendSelectSegmentByIndex(index: number) {
      if (!this.timeline) return
      this.selectedSegments.push(this.timeline.segments[index]!)
    },
    clearSelectedSegments() {
      this.selectedSegments.splice(0, this.selectedSegments.length)
    },
    insertSegmentIntoTimeline(segment: TimelineSegmentModel, index: number) {
      if (!this.timeline) return
      this.timeline.segments.splice(index, 0, segment)
    },
    reindexSegmentsInTimeline() {
      if (!this.timeline) return
      for (let i = 0; i < this.timeline.segments.length; i++) {
        this.timeline.segments[i]!.index = i
      }
    },
  },
  getters: {
    timelineExists(state) {
      return !!state.timeline
    },
    selectedSegmentEffects(state) {
      if (state.selectedSegments.length == 0) return null

      return state.selectedSegments[0]!.effects
    },
  },
})
