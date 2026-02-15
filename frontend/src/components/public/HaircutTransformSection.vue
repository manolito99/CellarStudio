<template>
  <section ref="wrapper" class="relative" :style="{ height: `${stagesCount * 100}vh` }">
    <div class="sticky top-0 h-screen w-full overflow-hidden bg-black">
      <!-- Stage images with clip-path reveal -->
      <div
        v-for="(stage, i) in stages"
        :key="i"
        class="absolute inset-0"
        :style="getImageStyle(i)"
      >
        <img
          :src="stage.image"
          :alt="stage.title"
          class="w-full h-full object-cover"
          loading="eager"
        />
      </div>

      <!-- Dark overlay -->
      <div class="absolute inset-0 bg-gradient-to-t from-black/60 via-black/20 to-black/40"></div>

      <!-- Stage text -->
      <div
        v-for="(stage, i) in stages"
        :key="'text-' + i"
        class="absolute inset-0 flex flex-col items-center justify-center px-4"
        :style="getTextStyle(i)"
      >
        <span class="text-white/50 text-xs sm:text-sm uppercase tracking-[0.3em] font-medium mb-3">
          {{ stage.label }}
        </span>
        <h3 class="text-white text-4xl md:text-6xl lg:text-7xl font-heading font-semibold tracking-tight text-center leading-tight">
          {{ stage.title }}
        </h3>
        <p class="text-white/60 text-base md:text-lg mt-4 max-w-md mx-auto text-center">
          {{ stage.subtitle }}
        </p>
        <!-- CTA on last stage -->
        <router-link
          v-if="i === stagesCount - 1"
          to="/booking"
          class="mt-8 btn-primary px-10 py-4 bg-white text-[#1d1d1f] text-lg font-semibold rounded-2xl"
          :style="{ opacity: getStageProgress(i) > 0.4 ? 1 : 0, transition: 'opacity 0.5s' }"
        >
          Reserva tu transformación
        </router-link>
      </div>

      <!-- Progress dots -->
      <div class="absolute right-5 md:right-8 top-1/2 -translate-y-1/2 flex flex-col gap-2.5 z-10">
        <button
          v-for="(stage, i) in stages"
          :key="'dot-' + i"
          class="w-2 rounded-full transition-all duration-500 ease-out"
          :class="currentStage === i ? 'h-7 bg-white' : 'h-2 bg-white/30 hover:bg-white/50'"
          :aria-label="stage.title"
        />
      </div>

      <!-- Progress bar bottom -->
      <div class="absolute bottom-0 left-0 right-0 h-[2px] bg-white/10 z-10">
        <div
          class="h-full bg-white/60 transition-[width] duration-100"
          :style="{ width: `${progress * 100}%` }"
        />
      </div>

      <!-- Scroll hint -->
      <Transition name="fade">
        <div
          v-if="progress < 0.03"
          class="absolute bottom-10 left-1/2 -translate-x-1/2 flex flex-col items-center gap-3 z-10"
        >
          <span class="text-white/40 text-sm tracking-wide">Desliza para ver la transformación</span>
          <div class="scroll-chevrons">
            <svg class="w-5 h-5 text-white/40 chevron-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
            <svg class="w-5 h-5 text-white/30 chevron-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </div>
        </div>
      </Transition>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

const wrapper = ref<HTMLElement>()
const progress = ref(0)

const stages = [
  {
    image: 'https://images.unsplash.com/photo-1564944940214-93fd718ebabd?auto=format&fit=crop&w=1920&q=80',
    label: 'Paso 01',
    title: 'Tu estilo actual',
    subtitle: 'Todos empezamos aquí. Es hora de un cambio.',
  },
  {
    image: 'https://images.unsplash.com/photo-1596513057998-040d410e4623?auto=format&fit=crop&w=1920&q=80',
    label: 'Paso 02',
    title: 'Comienza la magia',
    subtitle: 'Nuestros barberos expertos toman el control.',
  },
  {
    image: 'https://images.unsplash.com/photo-1541533848490-bc8115cd6522?auto=format&fit=crop&w=1920&q=80',
    label: 'Paso 03',
    title: 'Fade perfecto',
    subtitle: 'Precisión milimétrica en cada pasada.',
  },
  {
    image: 'https://images.unsplash.com/photo-1618049049816-43a00d5b0c3d?auto=format&fit=crop&w=1920&q=80',
    label: 'Paso 04',
    title: 'Estilo definido',
    subtitle: 'Tu personalidad reflejada en tu corte.',
  },
  {
    image: 'https://images.unsplash.com/photo-1535129219082-ba638579daa1?auto=format&fit=crop&w=1920&q=80',
    label: 'Paso 05',
    title: 'Tu mejor versión',
    subtitle: 'Confianza que se nota desde el primer momento.',
  },
]

const stagesCount = stages.length

const currentStage = computed(() => {
  return Math.min(Math.floor(progress.value * stagesCount), stagesCount - 1)
})

function getStageProgress(index: number): number {
  const stageSize = 1 / stagesCount
  const stageStart = index * stageSize
  const stageEnd = stageStart + stageSize
  if (progress.value <= stageStart) return 0
  if (progress.value >= stageEnd) return 1
  return (progress.value - stageStart) / stageSize
}

function getImageStyle(index: number) {
  if (index === 0) {
    return { zIndex: 0 }
  }

  const sp = getStageProgress(index)
  // Circle reveal: expand from 0% to 150% to ensure full coverage
  const radius = sp * 150
  return {
    clipPath: `circle(${radius}% at 50% 50%)`,
    zIndex: index,
  }
}

function getTextStyle(index: number) {
  const sp = getStageProgress(index)
  const isFirst = index === 0
  const isLast = index === stagesCount - 1

  let opacity: number
  let translateY: number

  if (isFirst) {
    // First stage: visible from the start, fade out at end
    if (progress.value < 0.01) {
      opacity = 1
      translateY = 0
    } else if (sp > 0.7) {
      opacity = (1 - sp) / 0.3
      translateY = -40 * ((sp - 0.7) / 0.3)
    } else {
      opacity = 1
      translateY = 0
    }
  } else if (isLast) {
    // Last stage: fade in, stay visible
    if (sp < 0.3) {
      opacity = sp / 0.3
      translateY = 40 * (1 - sp / 0.3)
    } else {
      opacity = 1
      translateY = 0
    }
  } else {
    // Middle stages: fade in then fade out
    if (sp < 0.2) {
      opacity = sp / 0.2
      translateY = 40 * (1 - sp / 0.2)
    } else if (sp > 0.8) {
      opacity = (1 - sp) / 0.2
      translateY = -40 * ((sp - 0.8) / 0.2)
    } else {
      opacity = 1
      translateY = 0
    }
  }

  return {
    opacity,
    transform: `translateY(${translateY}px)`,
    zIndex: stagesCount + 1,
    pointerEvents: (opacity > 0.5 ? 'auto' : 'none') as 'auto' | 'none',
  }
}

// Scroll tracking
let scrollEl: HTMLElement | null = null
let rafId: number

function onScroll() {
  if (!wrapper.value) return
  rafId = requestAnimationFrame(() => {
    const rect = wrapper.value!.getBoundingClientRect()
    const scrollableHeight = rect.height - window.innerHeight
    if (scrollableHeight <= 0) return
    const scrolled = -rect.top
    progress.value = Math.max(0, Math.min(1, scrolled / scrollableHeight))
  })
}

onMounted(async () => {
  const ionContent = wrapper.value?.closest('ion-content') as any
  if (ionContent?.getScrollElement) {
    scrollEl = await ionContent.getScrollElement()
    scrollEl!.addEventListener('scroll', onScroll, { passive: true })
    onScroll()
  } else {
    // Fallback: native scroll
    window.addEventListener('scroll', onScroll, { passive: true })
  }
})

onUnmounted(() => {
  if (rafId) cancelAnimationFrame(rafId)
  if (scrollEl) {
    scrollEl.removeEventListener('scroll', onScroll)
  } else {
    window.removeEventListener('scroll', onScroll)
  }
})
</script>

<style scoped>
/* Fade transition for scroll hint */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Scroll chevrons animation */
.scroll-chevrons {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0;
  margin-top: -4px;
}

.chevron-1 {
  animation: chevronBounce 2s ease-in-out infinite;
}

.chevron-2 {
  margin-top: -10px;
  animation: chevronBounce 2s ease-in-out infinite 0.15s;
}

@keyframes chevronBounce {
  0%, 100% { transform: translateY(0); opacity: 0.5; }
  50% { transform: translateY(6px); opacity: 1; }
}

/* White CTA button overrides */
:deep(.btn-primary.bg-white) {
  --btn-bg: white;
}
.btn-primary.bg-white:hover {
  box-shadow:
    0 10px 40px rgba(255, 255, 255, 0.3),
    0 0 0 1px rgba(255, 255, 255, 0.2) inset;
}
</style>
