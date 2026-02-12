<template>
  <section id="gallery" class="py-20 px-4 bg-[#F2F0E9]">
    <div class="max-w-6xl mx-auto">
      <div class="text-center mb-14">
        <span class="text-brand-400 text-sm font-semibold uppercase tracking-wider">Galería</span>
        <h2 class="text-4xl md:text-5xl font-heading font-bold text-[#2B2E2E] mt-3">
          Nuestro trabajo
        </h2>
        <div class="w-20 h-1 bg-brand-400 mx-auto mt-4 rounded-full"></div>
      </div>

      <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
        <div
          v-for="(item, index) in galleryItems"
          :key="index"
          class="relative aspect-square rounded-2xl overflow-hidden cursor-pointer group"
          :class="{ 'md:col-span-2 md:row-span-2': index === 0 }"
          @click="openLightbox(index)"
        >
          <div class="w-full h-full bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center">
            <svg class="w-12 h-12 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
          <div class="absolute inset-0 bg-brand-500/0 group-hover:bg-brand-500/20 transition-all duration-300 flex items-center justify-center">
            <svg class="w-8 h-8 text-white opacity-0 group-hover:opacity-100 transition-opacity" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7" />
            </svg>
          </div>
        </div>
      </div>
    </div>

    <!-- Lightbox -->
    <div
      v-if="lightboxOpen"
      class="fixed inset-0 z-50 bg-black/90 flex items-center justify-center p-4"
      @click="lightboxOpen = false"
    >
      <button class="absolute top-4 right-4 text-white hover:text-brand-400 transition-colors">
        <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
      <div class="max-w-4xl w-full aspect-video bg-white rounded-2xl flex items-center justify-center">
        <p class="text-dark-500">Imagen {{ selectedIndex + 1 }}</p>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const galleryItems = ref(Array.from({ length: 6 }, (_, i) => ({ id: i })))
const lightboxOpen = ref(false)
const selectedIndex = ref(0)

function openLightbox(index: number) {
  selectedIndex.value = index
  lightboxOpen.value = true
}
</script>
