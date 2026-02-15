<template>
  <div>
    <h3 class="text-2xl font-heading font-bold text-[#1d1d1f] mb-2">Elige fecha y hora</h3>
    <p class="text-dark-400 mb-6">Selecciona cuándo quieres tu cita</p>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
      <!-- Date picker -->
      <div>
        <label class="block text-sm font-medium text-dark-300 mb-2">Fecha</label>
        <input
          type="date"
          :value="selectedDate"
          :min="minDate"
          @input="onDateChange"
          class="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-[#1d1d1f] focus:border-brand-400 focus:outline-none focus:ring-1 focus:ring-brand-400"
        />
      </div>

      <!-- Time slots -->
      <div>
        <label class="block text-sm font-medium text-dark-300 mb-2">Hora disponible</label>

        <div v-if="loading" class="flex justify-center py-8">
          <ion-spinner name="crescent" color="dark" />
        </div>

        <div v-else-if="!selectedDate" class="text-dark-500 text-sm py-8 text-center">
          Selecciona una fecha primero
        </div>

        <div v-else-if="slots.length === 0" class="text-dark-500 text-sm py-8 text-center">
          No hay horarios disponibles para esta fecha
        </div>

        <div v-else class="grid grid-cols-3 sm:grid-cols-4 gap-2 max-h-64 overflow-y-auto pr-2">
          <button
            v-for="slot in slots"
            :key="slot.start_time"
            @click="$emit('selectSlot', slot)"
            class="px-3 py-2 rounded-lg text-sm font-medium transition-all"
            :class="[
              selectedSlot?.start_time === slot.start_time
                ? 'bg-brand-400 text-white'
                : 'bg-white border border-gray-200 text-[#1d1d1f] hover:border-brand-400',
            ]"
          >
            {{ formatTime(slot.start_time) }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { IonSpinner } from '@ionic/vue'
import type { TimeSlot } from '@/services/publicApi'

const props = defineProps<{
  selectedDate: string
  slots: TimeSlot[]
  selectedSlot: TimeSlot | null
  loading: boolean
}>()

const emit = defineEmits<{
  selectDate: [date: string]
  selectSlot: [slot: TimeSlot]
}>()

const minDate = computed(() => {
  const today = new Date()
  return today.toISOString().split('T')[0]
})

function onDateChange(e: Event) {
  const target = e.target as HTMLInputElement
  emit('selectDate', target.value)
}

function formatTime(time: string): string {
  return time.substring(0, 5)
}
</script>
