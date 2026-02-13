<template>
  <section id="team" class="py-24 px-4 bg-white">
    <div class="max-w-6xl mx-auto">
      <div class="text-center mb-16">
        <span v-reveal="'blur'" class="text-[#86868b] text-sm font-semibold uppercase tracking-[0.2em]">Nuestro equipo</span>
        <h2 v-reveal="'blur'" data-delay="100" class="text-4xl md:text-5xl font-heading font-semibold text-[#1d1d1f] mt-3 tracking-tight">
          Los mejores barberos
        </h2>
        <div v-reveal data-delay="200" class="divider-shimmer w-16 mx-auto mt-5"></div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-10">
        <div
          v-for="(barber, index) in barbers"
          :key="barber.id"
          v-reveal="'up'"
          :data-delay="index * 120"
          class="text-center group"
        >
          <div class="relative w-40 h-40 mx-auto mb-6">
            <div class="avatar-ring w-full h-full rounded-full p-[3px] transition-transform duration-600 ease-out-expo group-hover:scale-105">
              <div class="w-full h-full rounded-full bg-white flex items-center justify-center overflow-hidden">
                <img
                  v-if="barber.photo_url"
                  :src="barber.photo_url"
                  :alt="barber.name"
                  class="w-full h-full object-cover rounded-full transition-transform duration-800 ease-out-expo group-hover:scale-110"
                />
                <span v-else class="text-4xl font-heading font-semibold text-[#1d1d1f]">
                  {{ barber.name.charAt(0) }}
                </span>
              </div>
            </div>
          </div>
          <h3 class="text-xl font-semibold text-[#1d1d1f] mb-2">{{ barber.name }}</h3>
          <p class="text-[#86868b] text-sm leading-relaxed max-w-xs mx-auto">{{ barber.bio }}</p>
          <div class="flex flex-wrap gap-2 justify-center mt-4">
            <span
              v-for="service in barber.services.slice(0, 3)"
              :key="service.id"
              class="px-3 py-1 bg-[#f5f5f7] text-[#6e6e73] text-xs font-medium rounded-full transition-colors duration-300 hover:bg-[#e8e8ed]"
            >
              {{ service.name }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { publicApi, type Barber } from '@/services/publicApi'

const barbers = ref<Barber[]>([])

onMounted(async () => {
  barbers.value = await publicApi.getBarbers()
})
</script>

<style scoped>
.avatar-ring {
  background: linear-gradient(135deg, #1d1d1f, #86868b, #1d1d1f);
  background-size: 200% 200%;
  animation: ringShift 4s ease-in-out infinite;
}

@keyframes ringShift {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}
</style>
