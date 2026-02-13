import type { Directive } from 'vue'

export const vReveal: Directive<HTMLElement, string | undefined> = {
  mounted(el, binding) {
    const direction = binding.value || 'up'

    el.style.opacity = '0'
    el.style.willChange = 'opacity, transform, filter'
    el.style.transition =
      'opacity 0.9s cubic-bezier(0.16, 1, 0.3, 1), ' +
      'transform 0.9s cubic-bezier(0.16, 1, 0.3, 1), ' +
      'filter 0.9s cubic-bezier(0.16, 1, 0.3, 1)'

    const transforms: Record<string, string> = {
      up: 'translateY(50px)',
      down: 'translateY(-50px)',
      left: 'translateX(-60px)',
      right: 'translateX(60px)',
      scale: 'scale(0.92)',
      blur: 'translateY(25px)',
    }

    el.style.transform = transforms[direction] || transforms.up
    if (direction === 'blur') {
      el.style.filter = 'blur(8px)'
    }

    const delay = el.dataset.delay || '0'
    el.style.transitionDelay = `${delay}ms`

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          requestAnimationFrame(() => {
            el.style.opacity = '1'
            el.style.transform = 'translateY(0) translateX(0) scale(1)'
            el.style.filter = 'blur(0px)'
          })
          observer.unobserve(el)
        }
      },
      { threshold: 0.1, rootMargin: '0px 0px -40px 0px' },
    )
    observer.observe(el)
  },
}
