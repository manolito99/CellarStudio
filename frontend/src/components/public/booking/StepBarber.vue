<template>
  <div>
    <h3 class="text-2xl font-heading font-bold text-[#2B2E2E] mb-2">Elegí tu barbero</h3>
    <p class="text-dark-400 mb-6">Seleccioná con quién querés atenderte</p>

    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <button
        v-for="barber in barbers"
        :key="barber.id"
        @click="$emit('select', barber)"
        class="p-5 rounded-xl border-2 text-center transition-all duration-200"
        :class="[
          selected?.id === barber.id
            ? 'border-brand-400 bg-brand-500/10'
            : 'border-gray-200 bg-white hover:border-gray-400',
        ]"
      >
        <div class="w-20 h-20 mx-auto mb-3 rounded-full bg-gradient-to-br from-brand-400 to-brand-600 p-0.5">
          <div class="w-full h-full rounded-full bg-[#F2F0E9] flex items-center justify-center">
            <img
              v-if="barber.photo_url"
              :src="barber.photo_url"
              :alt="barber.name"
              class="w-full h-full object-cover rounded-full"
            />
            <span v-else class="text-2xl font-heading font-bold text-brand-400">
              {{ barber.name.charAt(0) }}
            </span>
          </div>
        </div>
        <h4 class="font-bold text-[#2B2E2E]">{{ barber.name }}</h4>
        <p class="text-dark-400 text-sm mt-1 line-clamp-2">{{ barber.bio }}</p>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Barber } from '@/services/publicApi'

defineProps<{
  barbers: Barber[]
  selected: Barber | null
}>()

defineEmits<{
  select: [barber: Barber]
}>()
</script>
