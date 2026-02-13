<template>
  <section class="relative min-h-screen flex items-center justify-center overflow-hidden">
    <!-- Background image -->
    <div class="absolute inset-0">
      <img
        src="https://images.unsplash.com/photo-1638383259008-28b70d3bc676?auto=format&fit=crop&w=1920&q=80"
        alt=""
        class="w-full h-full object-cover"
      />
      <div class="absolute inset-0 bg-gradient-to-b from-white/85 via-white/75 to-white/95"></div>
    </div>

    <!-- Floating orbs -->
    <div class="absolute inset-0 overflow-hidden">
      <div class="orb orb-1"></div>
      <div class="orb orb-2"></div>
    </div>

    <!-- Content -->
    <div class="relative z-10 text-center px-4 max-w-4xl mx-auto">
      <!-- Badge -->
      <div class="hero-enter hero-delay-1 mb-8 inline-flex items-center gap-2 px-5 py-2.5 bg-white/60 backdrop-blur-md border border-[#d2d2d7]/60 rounded-full shadow-sm">
        <span class="w-2 h-2 bg-[#1d1d1f] rounded-full animate-pulse"></span>
        <span class="text-[#1d1d1f] text-sm font-medium tracking-wide">Barbería Premium</span>
      </div>

      <!-- Title -->
      <h1 class="hero-enter hero-delay-2 text-5xl md:text-7xl lg:text-[5.5rem] font-heading font-semibold mb-6 leading-[0.95] tracking-tight">
        <span class="gradient-text">Cellar Studio</span>
      </h1>

      <!-- Subtitle -->
      <p class="hero-enter hero-delay-3 text-lg md:text-xl text-[#6e6e73] mb-12 max-w-2xl mx-auto leading-relaxed">
        Donde el estilo clásico se encuentra con las tendencias modernas.
        <br class="hidden sm:block" />
        Experiencia premium en cada corte.
      </p>

      <!-- Instagram link -->
      <div class="hero-enter hero-delay-4 mb-5 flex justify-center">
        <a
          href="https://www.instagram.com/maxiiii_29?utm_source=ig_web_button_share_sheet&igsh=ZDNlZDc0MzIxNw=="
          target="_blank"
          rel="noopener noreferrer"
          class="inline-flex items-center gap-2.5 px-5 py-2.5 bg-white/60 backdrop-blur-md border border-[#d2d2d7]/60 rounded-full shadow-sm group ig-link"
        >
          <svg class="w-[18px] h-[18px] text-[#1d1d1f] transition-transform duration-500 ease-out group-hover:scale-110" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16a4 4 0 110-8 4 4 0 010 8zm6.406-11.845a1.44 1.44 0 100 2.881 1.44 1.44 0 000-2.881z"/>
          </svg>
          <span class="text-[#1d1d1f] text-sm font-medium tracking-wide">@maxiiii_29</span>
          <span class="text-[#86868b] text-xs hidden sm:inline">· Mirá nuestros cortes</span>
          <svg class="w-3.5 h-3.5 text-[#86868b] transition-transform duration-500 ease-out group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </a>
      </div>

      <!-- CTAs -->
      <div class="hero-enter hero-delay-4 flex flex-col sm:flex-row gap-4 justify-center">
        <router-link
          to="/booking"
          class="btn-primary px-10 py-4 bg-[#1d1d1f] text-white text-lg font-semibold rounded-2xl"
        >
          Reserva tu cita
        </router-link>
        <button
          @click="scrollToServices"
          class="btn-secondary px-10 py-4 border border-[#d2d2d7] bg-white/50 backdrop-blur-sm text-[#1d1d1f] text-lg font-semibold rounded-2xl hover:border-[#86868b]"
        >
          Ver servicios
        </button>
      </div>

      <!-- Stats -->
      <div class="hero-enter hero-delay-5 mt-20 grid grid-cols-3 gap-8 max-w-lg mx-auto">
        <div>
          <p class="text-3xl md:text-4xl font-bold text-[#1d1d1f] tabular-nums">{{ years.display.value }}</p>
          <p class="text-sm text-[#86868b] mt-1">Años experiencia</p>
        </div>
        <div>
          <p class="text-3xl md:text-4xl font-bold text-[#1d1d1f] tabular-nums">{{ clients.display.value }}</p>
          <p class="text-sm text-[#86868b] mt-1">Clientes felices</p>
        </div>
        <div>
          <p class="text-3xl md:text-4xl font-bold text-[#1d1d1f] tabular-nums">{{ services.display.value }}</p>
          <p class="text-sm text-[#86868b] mt-1">Servicios premium</p>
        </div>
      </div>
    </div>

    <!-- Scroll indicator -->
    <div class="hero-enter hero-delay-5 absolute bottom-8 left-1/2 -translate-x-1/2">
      <div class="scroll-indicator">
        <div class="scroll-dot"></div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useCountUp } from '@/composables/useCountUp'

const years = useCountUp(5, 1500, '+')
const clients = useCountUp(3000, 2200, '+')
const services = useCountUp(5, 1200)

function scrollToServices() {
  document.getElementById('services')?.scrollIntoView({ behavior: 'smooth' })
}

onMounted(() => {
  setTimeout(() => {
    years.start()
    clients.start()
    services.start()
  }, 1100)
})
</script>

<style scoped>
/* Instagram link hover */
.ig-link {
  transition: all 0.5s cubic-bezier(0.16, 1, 0.3, 1);
}

.ig-link:hover {
  transform: translateY(-2px);
  border-color: rgba(225, 48, 108, 0.3);
  box-shadow: 0 8px 30px rgba(225, 48, 108, 0.1);
  background: rgba(255, 255, 255, 0.8);
}

.ig-link:hover svg:first-child {
  color: #E1306C;
}

/* Floating background orbs */
.orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.15;
  will-change: transform;
}

.orb-1 {
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, #d2d2d7 0%, transparent 70%);
  top: 10%;
  left: 15%;
  animation: float 20s ease-in-out infinite;
}

.orb-2 {
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, #e8e8ed 0%, transparent 70%);
  bottom: 15%;
  right: 10%;
  animation: float 25s ease-in-out infinite reverse;
}

@keyframes float {
  0%, 100% { transform: translate(0, 0) scale(1); }
  25% { transform: translate(40px, -40px) scale(1.05); }
  50% { transform: translate(-20px, 30px) scale(0.97); }
  75% { transform: translate(30px, 20px) scale(1.03); }
}

/* Scroll indicator (Apple-style mouse shape) */
.scroll-indicator {
  width: 26px;
  height: 42px;
  border: 2px solid #86868b;
  border-radius: 13px;
  display: flex;
  justify-content: center;
  padding-top: 8px;
  opacity: 0.6;
  transition: opacity 0.3s;
}

.scroll-indicator:hover {
  opacity: 1;
}

.scroll-dot {
  width: 3px;
  height: 8px;
  background: #86868b;
  border-radius: 2px;
  animation: scrollDown 2s ease-in-out infinite;
}

@keyframes scrollDown {
  0% { opacity: 1; transform: translateY(0); }
  50% { opacity: 0.3; transform: translateY(12px); }
  100% { opacity: 1; transform: translateY(0); }
}
</style>
