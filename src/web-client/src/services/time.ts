export const secondsToTimeSpanFractionalFormat = (seconds: number | null | undefined): string => {
  if (seconds === null || seconds == undefined) return ''

  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = Math.floor(seconds % 60)
  const fractional = seconds - Math.floor(seconds)

  const fractionalStr = fractional.toFixed(4).substring(1)
  const pad = (n: number) => n.toString().padStart(2, '0')

  return `${pad(hours)}:${pad(minutes)}:${pad(secs)}${fractionalStr}`
}
