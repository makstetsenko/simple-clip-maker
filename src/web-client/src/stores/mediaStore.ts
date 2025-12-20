import { defineStore } from 'pinia'

const videoExt = ['.mp4', '.mov', '.m4v']
export const mediaExt = ['.mp3', '.m4a', ...videoExt]

interface MediaStore {
  mediaPathList: string[]
}

export const useMediaStore = defineStore('project-media', {
  state: (): MediaStore => {
    return { mediaPathList: [] }
  },
  actions: {},
  getters: {
    getVideoPathList(state) {
      return state.mediaPathList.filter((x) => videoExt.some((e) => fileStemFromPath(x) === e))
    },

    getMediaNames(state) {
      return state.mediaPathList.map((x) => fileNameFromPath(x))
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

export function fileStemFromPath(p: string): string {
  const name = fileNameFromPath(p)
  const match = name.match(/\.([^.]+)$/);
  const a = match ? `.${match[1]}` : "";
  console.log(a);

  return a
}
