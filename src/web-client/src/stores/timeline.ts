import { defineStore } from 'pinia'
import type { TimelineModel, TimelineSegmentModel } from '@/shared/models/TimelineModel'
import { mapTimeline } from '@/shared/mappers/timelineMapper'
import apiClient from '@/services/apiClient'

interface TimelineStoreState {
  timeline: TimelineModel | null
  selectedSegments: TimelineSegmentModel[]
  autoScrollOn: boolean
}

export const useTimelineStore = defineStore('timeline', {
  state: (): TimelineStoreState => {
    return {
      timeline: null,
      selectedSegments: [],
      autoScrollOn: false,
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
    async upsert(projectName: string) {
      if (!this.timelineExists) return
      const timelineObj = mapTimeline(this.timeline!)

      const url = `/api/${projectName}/timeline/upsert`
      await apiClient.post(url, timelineObj)
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
