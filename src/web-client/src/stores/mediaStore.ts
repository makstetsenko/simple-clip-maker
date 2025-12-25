import { defineStore } from 'pinia'

const videoExt = ['.mp4', '.mov', '.m4v']
const audioExt = ['.mp3', '.m4a']
export const mediaExt = [...audioExt, ...videoExt]

interface MediaStore {
  mediaPathList: string[]
}

export interface MediaName {
  name: string
  ext: string
  path: string
  isVideo: boolean
}

export const useMediaStore = defineStore('project-media', {
  state: (): MediaStore => {
    return { mediaPathList: [] }
  },
  actions: {},
  getters: {
    getVideoPathList(state) {
      return state.mediaPathList.filter((x) =>
        videoExt.some((e) => fileExtFromPath(x).toLowerCase() === e),
      )
    },
    getAudioPathList(state) {
      return state.mediaPathList.filter((x) =>
        audioExt.some((e) => fileExtFromPath(x).toLowerCase() === e),
      )
    },

    getMediaNames(state): MediaName[] {
      return state.mediaPathList.map((x) => ({
        name: fileNameFromPath(x),
        ext: fileExtFromPath(x).toLowerCase(),
        path: x,
        isVideo: videoExt.some((e) => fileExtFromPath(x).toLowerCase() === e),
      })) as MediaName[]
    },
  },
})

export function fileNameFromPath(p: string): string {
  // normalize Windows separators to POSIX
  const normalized = p.replace(/\\/g, '/')

  // remove trailing slashes
  const noTrailing = normalized.replace(/\/+$/, '')

  // return last segment
  return noTrailing.split('/').pop() ?? ''
}

export function fileExtFromPath(p: string): string {
  const name = fileNameFromPath(p)
  const match = name.match(/\.([^.]+)$/)
  const a = match ? `.${match[1]}` : ''
  console.log(a)

  return a
}
