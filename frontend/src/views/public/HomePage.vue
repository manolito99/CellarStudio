<template>
  <ion-page>
    <ion-header class="ion-no-border home-header" :class="{ 'header-scrolled': scrolled }">
      <ion-toolbar>
        <div class="max-w-6xl mx-auto px-4 flex items-center justify-between" style="height: 56px;">
          <img src="/icons/CellarStudio_Logo.png" alt="Cellar Studio" class="h-9 w-auto" />
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
      <HeroSection />
      <HaircutTransformSection />
      <ServicesGrid />
      <TeamSection />
      <GallerySection />
      <LocationSection />
    </ion-content>
  </ion-page>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { IonPage, IonContent, IonHeader, IonToolbar } from '@ionic/vue'
import HeroSection from '@/components/public/HeroSection.vue'
import HaircutTransformSection from '@/components/public/HaircutTransformSection.vue'
import ServicesGrid from '@/components/public/ServicesGrid.vue'
import TeamSection from '@/components/public/TeamSection.vue'
import GallerySection from '@/components/public/GallerySection.vue'
import LocationSection from '@/components/public/LocationSection.vue'

const scrolled = ref(false)

function onScroll(e: CustomEvent) {
  scrolled.value = e.detail.scrollTop > 50
}
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
</style>
