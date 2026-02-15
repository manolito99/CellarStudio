<template>
  <div>
    <h3 class="text-2xl font-heading font-bold text-[#1d1d1f] mb-2">Elige tu servicio</h3>
    <p class="text-dark-400 mb-6">Selecciona el servicio que necesitas</p>

    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <button
        v-for="service in services"
        :key="service.id"
        @click="$emit('select', service)"
        class="p-5 rounded-xl border-2 text-left transition-all duration-200"
        :class="[
          selected?.id === service.id
            ? 'border-brand-400 bg-brand-500/10'
            : 'border-gray-200 bg-white hover:border-gray-400',
        ]"
      >
        <div class="flex items-start justify-between">
          <div>
            <h4 class="font-bold text-[#1d1d1f] text-lg">{{ service.name }}</h4>
            <p class="text-dark-400 text-sm mt-1">{{ service.description }}</p>
          </div>
          <div
            class="w-6 h-6 rounded-full border-2 flex-shrink-0 flex items-center justify-center ml-3"
            :class="[
              selected?.id === service.id
                ? 'border-brand-400 bg-brand-400'
                : 'border-gray-300',
            ]"
          >
            <svg
              v-if="selected?.id === service.id"
              class="w-3 h-3 text-dark-950"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                fill-rule="evenodd"
                d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                clip-rule="evenodd"
              />
            </svg>
          </div>
        </div>
        <div class="flex items-center gap-4 mt-3">
          <span class="text-xl font-bold text-brand-400">${{ service.price.toLocaleString() }}</span>
          <span class="text-sm text-dark-500">{{ service.duration_minutes }} min</span>
        </div>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Service } from '@/services/publicApi'

defineProps<{
  services: Service[]
  selected: Service | null
}>()

defineEmits<{
  select: [service: Service]
}>()
</script>
