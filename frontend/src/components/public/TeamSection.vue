<template>
  <section id="team" class="py-20 px-4 bg-white/50">
    <div class="max-w-6xl mx-auto">
      <div class="text-center mb-14">
        <span class="text-brand-400 text-sm font-semibold uppercase tracking-wider">Nuestro equipo</span>
        <h2 class="text-4xl md:text-5xl font-heading font-bold text-[#2B2E2E] mt-3">
          Los mejores barberos
        </h2>
        <div class="w-20 h-1 bg-brand-400 mx-auto mt-4 rounded-full"></div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div
          v-for="barber in barbers"
          :key="barber.id"
          class="text-center group"
        >
          <div class="relative w-40 h-40 mx-auto mb-6">
            <div class="w-full h-full rounded-full bg-gradient-to-br from-brand-400 to-brand-600 p-1">
              <div class="w-full h-full rounded-full bg-[#F2F0E9] flex items-center justify-center overflow-hidden">
                <img
                  v-if="barber.photo_url"
                  :src="barber.photo_url"
                  :alt="barber.name"
                  class="w-full h-full object-cover rounded-full"
                />
                <span v-else class="text-4xl font-heading font-bold text-brand-400">
                  {{ barber.name.charAt(0) }}
                </span>
              </div>
            </div>
          </div>
          <h3 class="text-xl font-bold text-[#2B2E2E] mb-2">{{ barber.name }}</h3>
          <p class="text-dark-400 text-sm leading-relaxed max-w-xs mx-auto">{{ barber.bio }}</p>
          <div class="flex flex-wrap gap-2 justify-center mt-4">
            <span
              v-for="service in barber.services.slice(0, 3)"
              :key="service.id"
              class="px-3 py-1 bg-brand-500/10 text-brand-400 text-xs rounded-full"
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
