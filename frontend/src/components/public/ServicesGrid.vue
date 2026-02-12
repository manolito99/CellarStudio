<template>
  <section id="services" class="py-20 px-4 bg-[#F2F0E9]">
    <div class="max-w-6xl mx-auto">
      <div class="text-center mb-14">
        <span class="text-brand-400 text-sm font-semibold uppercase tracking-wider">Nuestros servicios</span>
        <h2 class="text-4xl md:text-5xl font-heading font-bold text-[#2B2E2E] mt-3">
          Lo que ofrecemos
        </h2>
        <div class="w-20 h-1 bg-brand-400 mx-auto mt-4 rounded-full"></div>
      </div>

      <div v-if="loading" class="flex justify-center py-20">
        <ion-spinner name="crescent" color="warning" />
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <ion-card
          v-for="service in services"
          :key="service.id"
          class="bg-white border border-gray-200 rounded-2xl overflow-hidden hover:border-brand-500/30 transition-all duration-300 hover:-translate-y-1"
        >
          <div class="p-6">
            <div class="w-12 h-12 bg-brand-500/10 rounded-xl flex items-center justify-center mb-4">
              <svg class="w-6 h-6 text-brand-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.121 14.121L19 19m-7-7l7-7m-7 7l-2.879 2.879M12 12L9.121 9.121m0 5.758a3 3 0 10-4.243-4.243 3 3 0 004.243 4.243z" />
              </svg>
            </div>
            <h3 class="text-xl font-bold text-[#2B2E2E] mb-2">{{ service.name }}</h3>
            <p class="text-dark-400 text-sm mb-4 leading-relaxed">{{ service.description }}</p>
            <div class="flex items-center justify-between">
              <span class="text-2xl font-bold text-brand-400">${{ service.price.toLocaleString() }}</span>
              <span class="text-sm text-dark-500">{{ service.duration_minutes }} min</span>
            </div>
          </div>
        </ion-card>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { IonCard, IonSpinner } from '@ionic/vue'
import { publicApi, type Service } from '@/services/publicApi'

const services = ref<Service[]>([])
const loading = ref(true)

onMounted(async () => {
  try {
    services.value = await publicApi.getServices()
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
ion-card {
  --background: transparent;
  margin: 0;
  box-shadow: none;
}
</style>
