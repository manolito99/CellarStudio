<template>
  <ion-page>
    <ion-header class="ion-no-border home-header" :class="{ 'header-scrolled': scrolled }">
      <ion-toolbar>
        <div class="max-w-6xl mx-auto px-4 flex items-center justify-between" style="height: 56px;">
          <img src="/icons/logo.svg" alt="Cellar Studio" class="h-9 w-auto" />
          <div class="hidden md:flex items-center gap-6">
            <a href="#services" class="text-sm text-dark-400 hover:text-[#2B2E2E] transition-colors">Servicios</a>
            <a href="#team" class="text-sm text-dark-400 hover:text-[#2B2E2E] transition-colors">Equipo</a>
            <a href="#gallery" class="text-sm text-dark-400 hover:text-[#2B2E2E] transition-colors">Galería</a>
            <a href="#location" class="text-sm text-dark-400 hover:text-[#2B2E2E] transition-colors">Ubicación</a>
          </div>
          <div class="flex items-center gap-2">
            <router-link
              to="/admin/login"
              class="px-3 py-2 border border-dark-300 hover:border-[#2B2E2E] text-dark-400 hover:text-[#2B2E2E] text-sm font-medium rounded-lg transition-colors"
            >
              Admin
            </router-link>
            <router-link
              to="/booking"
              class="px-4 py-2 bg-brand-500 hover:bg-brand-600 text-white text-sm font-semibold rounded-lg transition-colors"
            >
              Reservar
            </router-link>
          </div>
        </div>
      </ion-toolbar>
    </ion-header>

    <ion-content :fullscreen="true" :scroll-events="true" @ionScroll="onScroll">
      <HeroSection />
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
  --background: #F2F0E9;
}
ion-toolbar {
  --background: transparent;
  --border-color: transparent;
  --padding-start: 0;
  --padding-end: 0;
}
.header-scrolled ion-toolbar {
  --background: rgba(242, 240, 233, 0.95);
  --border-color: #d1d1d1;
}
ion-header {
  transition: all 0.3s ease;
}
</style>
