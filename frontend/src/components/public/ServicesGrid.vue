<template>
  <section id="services" class="py-24 px-4 bg-[#f5f5f7]">
    <div class="max-w-6xl mx-auto">
      <div class="text-center mb-16">
        <span v-reveal="'blur'" class="text-[#86868b] text-sm font-semibold uppercase tracking-[0.2em]">Nuestros servicios</span>
        <h2 v-reveal="'blur'" data-delay="100" class="text-4xl md:text-5xl font-heading font-semibold text-[#1d1d1f] mt-3 tracking-tight">
          Lo que ofrecemos
        </h2>
        <div v-reveal data-delay="200" class="divider-shimmer w-16 mx-auto mt-5"></div>
      </div>

      <div v-if="loading" class="flex justify-center py-20">
        <ion-spinner name="crescent" color="dark" />
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <ion-card
          v-for="(service, index) in services"
          :key="service.id"
          v-reveal="'up'"
          :data-delay="index * 100"
          class="card-premium bg-white rounded-2xl overflow-hidden"
        >
          <div class="p-7">
            <div class="w-12 h-12 bg-[#f5f5f7] rounded-2xl flex items-center justify-center mb-5 transition-all duration-600 ease-out-expo group-hover:scale-110">
              <svg class="w-6 h-6 text-[#1d1d1f]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M14.121 14.121L19 19m-7-7l7-7m-7 7l-2.879 2.879M12 12L9.121 9.121m0 5.758a3 3 0 10-4.243-4.243 3 3 0 004.243 4.243z" />
              </svg>
            </div>
            <h3 class="text-xl font-semibold text-[#1d1d1f] mb-2">{{ service.name }}</h3>
            <p class="text-[#86868b] text-sm mb-5 leading-relaxed">{{ service.description }}</p>
            <div class="flex items-center justify-between pt-4 border-t border-[#e8e8ed]">
              <span class="text-2xl font-bold text-[#1d1d1f]">${{ service.price.toLocaleString() }}</span>
              <span class="text-sm text-[#86868b] bg-[#f5f5f7] px-3 py-1 rounded-full">{{ service.duration_minutes }} min</span>
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
