<template>
  <section class="relative min-h-screen flex items-center justify-center overflow-hidden">
    <!-- Background -->
    <div class="absolute inset-0 bg-gradient-to-br from-[#F2F0E9] via-[#ebe8e0] to-[#F2F0E9]"></div>
    <div class="absolute inset-0 opacity-20">
      <div class="absolute top-1/4 left-1/4 w-96 h-96 bg-brand-500/30 rounded-full blur-3xl"></div>
      <div class="absolute bottom-1/4 right-1/4 w-96 h-96 bg-brand-400/20 rounded-full blur-3xl"></div>
    </div>

    <!-- Content -->
    <div class="relative z-10 text-center px-4 max-w-4xl mx-auto">
      <div class="mb-6 inline-flex items-center gap-2 px-4 py-2 bg-brand-500/10 border border-brand-500/20 rounded-full">
        <span class="w-2 h-2 bg-brand-400 rounded-full animate-pulse"></span>
        <span class="text-brand-400 text-sm font-medium">Barbería Premium</span>
      </div>

      <h1 class="text-5xl md:text-7xl lg:text-8xl font-heading font-light text-[#2B2E2E] mb-6 leading-tight tracking-[0.15em] uppercase">
        Cellar <span class="text-brand-400">Studio</span>
      </h1>

      <p class="text-lg md:text-xl text-[#595959] mb-10 max-w-2xl mx-auto leading-relaxed">
        Donde el estilo clásico se encuentra con las tendencias modernas.
        Experiencia premium en cada corte.
      </p>

      <div class="flex flex-col sm:flex-row gap-4 justify-center">
        <router-link
          to="/booking"
          class="px-8 py-4 bg-brand-500 hover:bg-brand-600 active:bg-brand-700 text-white text-lg font-semibold rounded-xl transition-colors"
        >
          Reserva tu cita
        </router-link>
        <button
          @click="scrollToServices"
          class="px-8 py-4 border-2 border-[#2B2E2E] hover:border-brand-400 text-[#2B2E2E] hover:text-brand-400 text-lg font-semibold rounded-xl transition-colors"
        >
          Ver servicios
        </button>
      </div>

      <!-- Stats -->
      <div class="mt-16 grid grid-cols-3 gap-8 max-w-md mx-auto">
        <div>
          <p class="text-3xl font-bold text-brand-400">5+</p>
          <p class="text-sm text-[#595959]">Años de experiencia</p>
        </div>
        <div>
          <p class="text-3xl font-bold text-brand-400">3K+</p>
          <p class="text-sm text-[#595959]">Clientes satisfechos</p>
        </div>
        <div>
          <p class="text-3xl font-bold text-brand-400">5</p>
          <p class="text-sm text-[#595959]">Servicios premium</p>
        </div>
      </div>
    </div>

    <!-- Scroll indicator -->
    <div class="absolute bottom-8 left-1/2 -translate-x-1/2 animate-bounce">
      <svg class="w-6 h-6 text-[#595959]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3" />
      </svg>
    </div>
  </section>
</template>

<script setup lang="ts">
function scrollToServices() {
  document.getElementById('services')?.scrollIntoView({ behavior: 'smooth' })
}
</script>
