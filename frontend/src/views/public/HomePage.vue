<template>
  <ion-page>
    <ion-header class="ion-no-border home-header" :class="{ 'header-scrolled': scrolled }">
      <ion-toolbar>
        <div class="max-w-6xl mx-auto px-4 flex items-center justify-between" style="height: 56px;">
          <img src="/icons/CellarStudio_Logo.png" alt="Cellar Barber Studio" class="h-9 w-auto" />
          <div class="hidden md:flex items-center gap-8">
            <a href="#services" class="nav-link text-sm text-[#86868b] hover:text-[#1d1d1f] transition-colors duration-300">Servicios</a>
            <a href="#team" class="nav-link text-sm text-[#86868b] hover:text-[#1d1d1f] transition-colors duration-300">Equipo</a>
            <a href="#gallery" class="nav-link text-sm text-[#86868b] hover:text-[#1d1d1f] transition-colors duration-300">Galería</a>
            <a href="#location" class="nav-link text-sm text-[#86868b] hover:text-[#1d1d1f] transition-colors duration-300">Ubicación</a>
          </div>
          <div class="flex items-center gap-3">
            <router-link
              to="/admin/login"
              class="px-4 py-2 text-[#86868b] hover:text-[#1d1d1f] text-sm font-medium transition-colors duration-300"
            >
              Admin
            </router-link>
            <router-link
              to="/booking"
              class="btn-primary px-5 py-2.5 bg-[#1d1d1f] text-white text-sm font-semibold rounded-full"
            >
              Reservar
            </router-link>
          </div>
        </div>
      </ion-toolbar>
    </ion-header>

    <ion-content :fullscreen="true" :scroll-events="true" @ionScroll="onScroll">
      <HeroSection :next-slot="nextSlot" />
      <HaircutTransformSection />
      <ServicesGrid />
      <TeamSection />
      <GallerySection />
      <LocationSection />
    </ion-content>

    <!-- Sticky mobile CTA — only on mobile, appears after scrolling past hero -->
    <Transition name="slide-up">
      <div
        v-if="scrollPastHero"
        class="md:hidden fixed bottom-0 left-0 right-0 z-50"
        style="padding-bottom: env(safe-area-inset-bottom)"
      >
        <div class="bg-white/95 backdrop-blur-xl border-t border-[#e8e8ed] px-4 py-3 flex items-center gap-3 shadow-[0_-4px_24px_rgba(0,0,0,0.08)]">
          <div class="flex-1 min-w-0">
            <p class="text-[11px] text-[#86868b] leading-none mb-0.5">Cellar Barber Studio</p>
            <p class="text-xs font-semibold text-[#1d1d1f] truncate">
              <template v-if="nextSlot">
                <span class="inline-block w-1.5 h-1.5 rounded-full bg-green-500 mr-1.5 mb-px"></span>Próximo hueco {{ nextSlot }}
              </template>
              <template v-else>Reserva tu cita ahora</template>
            </p>
          </div>
          <router-link
            to="/booking"
            class="flex-shrink-0 px-5 py-2.5 bg-[#1d1d1f] text-white text-sm font-bold rounded-full active:scale-95 transition-transform"
          >
            Reservar
          </router-link>
        </div>
      </div>
    </Transition>
  </ion-page>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { IonPage, IonContent, IonHeader, IonToolbar } from '@ionic/vue'
import { publicApi } from '@/services/publicApi'
import HeroSection from '@/components/public/HeroSection.vue'
import HaircutTransformSection from '@/components/public/HaircutTransformSection.vue'
import ServicesGrid from '@/components/public/ServicesGrid.vue'
import TeamSection from '@/components/public/TeamSection.vue'
import GallerySection from '@/components/public/GallerySection.vue'
import LocationSection from '@/components/public/LocationSection.vue'

const scrolled = ref(false)
const scrollPastHero = ref(false)
const nextSlot = ref('')

function onScroll(e: CustomEvent) {
  const top = e.detail.scrollTop
  scrolled.value = top > 50
  scrollPastHero.value = top > 500
}

function toDateStr(d: Date): string {
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

async function loadNextSlot() {
  try {
    const [barbers, services] = await Promise.all([
      publicApi.getBarbers(),
      publicApi.getServices(),
    ])
    if (!barbers.length || !services.length) return

    const barberId = barbers[0].id
    const serviceId = services[0].id
    const today = new Date()
    const from = toDateStr(today)
    const to7 = new Date(today)
    to7.setDate(to7.getDate() + 13)
    const to = toDateStr(to7)

    const dates = await publicApi.getAvailableDates(barberId, serviceId, from, to)
    if (!dates.length) return

    const d = dates[0]
    const todayStr = from
    const tomorrowDate = new Date(today)
    tomorrowDate.setDate(tomorrowDate.getDate() + 1)
    const tomorrowStr = toDateStr(tomorrowDate)

    let dayLabel: string
    if (d.date === todayStr) {
      dayLabel = 'hoy'
    } else if (d.date === tomorrowStr) {
      dayLabel = 'mañana'
    } else {
      dayLabel = 'el ' + new Date(d.date + 'T12:00:00').toLocaleDateString('es-ES', { weekday: 'long', day: 'numeric', month: 'short' })
    }

    nextSlot.value = `${dayLabel} a las ${d.first_slot}`
  } catch {
    // Silently ignore — the slot text is optional
  }
}

onMounted(() => {
  loadNextSlot()
})
</script>

<style scoped>
ion-content {
  --background: #ffffff;
}
ion-toolbar {
  --background: transparent;
  --border-color: transparent;
  --padding-start: 0;
  --padding-end: 0;
}
.header-scrolled ion-toolbar {
  --background: rgba(255, 255, 255, 0.72);
  backdrop-filter: saturate(180%) blur(20px);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
  --border-color: rgba(0, 0, 0, 0.08);
}
ion-header {
  transition: all 0.5s cubic-bezier(0.16, 1, 0.3, 1);
}

/* Sticky CTA slide-up animation */
.slide-up-enter-active,
.slide-up-leave-active {
  transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.4s ease;
}
.slide-up-enter-from,
.slide-up-leave-to {
  transform: translateY(100%);
  opacity: 0;
}
</style>
