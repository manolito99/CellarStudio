<template>
  <section id="gallery" class="py-24 px-4 bg-[#f5f5f7]">
    <div class="max-w-6xl mx-auto">
      <div class="text-center mb-16">
        <span v-reveal="'blur'" class="text-[#86868b] text-sm font-semibold uppercase tracking-[0.2em]">Galería</span>
        <h2 v-reveal="'blur'" data-delay="100" class="text-4xl md:text-5xl font-heading font-semibold text-[#1d1d1f] mt-3 tracking-tight">
          Nuestro trabajo
        </h2>
        <div v-reveal data-delay="200" class="divider-shimmer w-16 mx-auto mt-5"></div>
      </div>

      <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
        <div
          v-for="(item, index) in galleryItems"
          :key="index"
          v-reveal="'scale'"
          :data-delay="index * 80"
          class="relative rounded-2xl overflow-hidden cursor-pointer group"
          :class="index === 0 ? 'aspect-auto md:col-span-2 md:row-span-2' : 'aspect-square'"
          @click="openLightbox(index)"
        >
          <img
            :src="item.src"
            :alt="item.alt"
            class="w-full h-full object-cover transition-transform duration-800 ease-out-expo group-hover:scale-105"
            loading="lazy"
          />
          <div class="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-all duration-600 ease-out-expo flex items-center justify-center">
            <svg class="w-10 h-10 text-white opacity-0 group-hover:opacity-100 transition-all duration-500 transform scale-75 group-hover:scale-100" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7" />
            </svg>
          </div>
        </div>
      </div>
    </div>

    <!-- Lightbox -->
    <Teleport to="body">
      <Transition name="lightbox">
        <div
          v-if="lightboxOpen"
          class="fixed inset-0 z-50 bg-black/90 backdrop-blur-sm flex items-center justify-center p-4"
          @click.self="lightboxOpen = false"
        >
          <button
            class="absolute top-6 right-6 text-white/70 hover:text-white transition-colors duration-300 z-10"
            @click="lightboxOpen = false"
          >
            <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>

          <!-- Navigation arrows -->
          <button
            v-if="selectedIndex > 0"
            class="absolute left-4 md:left-8 text-white/50 hover:text-white transition-colors duration-300 z-10"
            @click.stop="selectedIndex--"
          >
            <svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <button
            v-if="selectedIndex < galleryItems.length - 1"
            class="absolute right-4 md:right-8 text-white/50 hover:text-white transition-colors duration-300 z-10"
            @click.stop="selectedIndex++"
          >
            <svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 5l7 7-7 7" />
            </svg>
          </button>

          <Transition name="lightbox-img" mode="out-in">
            <img
              :key="selectedIndex"
              :src="galleryItems[selectedIndex].srcFull"
              :alt="galleryItems[selectedIndex].alt"
              class="max-w-[90vw] max-h-[85vh] object-contain rounded-2xl"
              @click.stop
            />
          </Transition>
        </div>
      </Transition>
    </Teleport>
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const galleryItems = ref([
  {
    src: 'https://images.unsplash.com/photo-1605497788044-5a32c7078486?auto=format&fit=crop&w=800&q=80',
    srcFull: 'https://images.unsplash.com/photo-1605497788044-5a32c7078486?auto=format&fit=crop&w=1600&q=80',
    alt: 'Corte de pelo en progreso',
  },
  {
    src: 'https://images.unsplash.com/photo-1599351431613-18ef1fdd27e1?auto=format&fit=crop&w=600&q=80',
    srcFull: 'https://images.unsplash.com/photo-1599351431613-18ef1fdd27e1?auto=format&fit=crop&w=1400&q=80',
    alt: 'Herramientas de barbería',
  },
  {
    src: 'https://images.unsplash.com/photo-1593702233354-259d1f794ed1?auto=format&fit=crop&w=600&q=80',
    srcFull: 'https://images.unsplash.com/photo-1593702233354-259d1f794ed1?auto=format&fit=crop&w=1400&q=80',
    alt: 'Resultado de corte estilizado',
  },
  {
    src: 'https://images.unsplash.com/photo-1593702275687-f8b402bf1fb5?auto=format&fit=crop&w=600&q=80',
    srcFull: 'https://images.unsplash.com/photo-1593702275687-f8b402bf1fb5?auto=format&fit=crop&w=1400&q=80',
    alt: 'Barbero trabajando',
  },
  {
    src: 'https://images.unsplash.com/photo-1589985494639-69e60c82cab2?auto=format&fit=crop&w=600&q=80',
    srcFull: 'https://images.unsplash.com/photo-1589985494639-69e60c82cab2?auto=format&fit=crop&w=1400&q=80',
    alt: 'Detalle de corte fade',
  },
  {
    src: 'https://images.unsplash.com/photo-1549663369-22ac6b052faf?auto=format&fit=crop&w=600&q=80',
    srcFull: 'https://images.unsplash.com/photo-1549663369-22ac6b052faf?auto=format&fit=crop&w=1400&q=80',
    alt: 'Ambiente de barbería',
  },
])

const lightboxOpen = ref(false)
const selectedIndex = ref(0)

function openLightbox(index: number) {
  selectedIndex.value = index
  lightboxOpen.value = true
}
</script>

<style scoped>
.lightbox-enter-active,
.lightbox-leave-active {
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

.lightbox-enter-from,
.lightbox-leave-to {
  opacity: 0;
  backdrop-filter: blur(0);
}

.lightbox-img-enter-active,
.lightbox-img-leave-active {
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.lightbox-img-enter-from {
  opacity: 0;
  transform: scale(0.95);
}

.lightbox-img-leave-to {
  opacity: 0;
  transform: scale(1.02);
}
</style>
