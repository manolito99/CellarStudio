import { ref, type Ref } from 'vue'

export function useCountUp(
  target: number,
  duration = 2000,
  suffix = '',
): { display: Ref<string>; start: () => void } {
  const display = ref('0' + suffix)

  function start() {
    const startTime = performance.now()

    function update(currentTime: number) {
      const elapsed = currentTime - startTime
      const progress = Math.min(elapsed / duration, 1)
      const eased = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress)
      const current = Math.round(eased * target)

      display.value = current.toLocaleString() + suffix

      if (progress < 1) {
        requestAnimationFrame(update)
      }
    }

    requestAnimationFrame(update)
  }

  return { display, start }
}
