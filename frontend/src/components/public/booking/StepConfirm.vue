<template>
  <div>
    <h3 class="text-2xl font-heading font-bold text-[#2B2E2E] mb-2">Confirmá tu reserva</h3>
    <p class="text-dark-400 mb-6">Revisá los datos antes de confirmar</p>

    <div class="bg-white border border-gray-200 rounded-2xl p-6 max-w-md space-y-4">
      <div class="flex justify-between items-center pb-4 border-b border-gray-200">
        <span class="text-[#595959]">Servicio</span>
        <span class="text-[#2B2E2E] font-medium">{{ service?.name }}</span>
      </div>
      <div class="flex justify-between items-center pb-4 border-b border-gray-200">
        <span class="text-[#595959]">Barbero</span>
        <span class="text-[#2B2E2E] font-medium">{{ barber?.name }}</span>
      </div>
      <div class="flex justify-between items-center pb-4 border-b border-gray-200">
        <span class="text-[#595959]">Fecha</span>
        <span class="text-[#2B2E2E] font-medium">{{ formatDate(date) }}</span>
      </div>
      <div class="flex justify-between items-center pb-4 border-b border-gray-200">
        <span class="text-[#595959]">Hora</span>
        <span class="text-[#2B2E2E] font-medium">{{ slot ? formatTime(slot.start_time) : '' }}</span>
      </div>
      <div class="flex justify-between items-center pb-4 border-b border-gray-200">
        <span class="text-[#595959]">Duración</span>
        <span class="text-[#2B2E2E] font-medium">{{ service?.duration_minutes }} min</span>
      </div>
      <div class="flex justify-between items-center pb-4 border-b border-gray-200">
        <span class="text-[#595959]">Cliente</span>
        <span class="text-[#2B2E2E] font-medium">{{ clientName }}</span>
      </div>
      <div class="flex justify-between items-center pb-4 border-b border-gray-200">
        <span class="text-[#595959]">Teléfono</span>
        <span class="text-[#2B2E2E] font-medium">{{ clientPhone }}</span>
      </div>
      <div class="flex justify-between items-center pt-2">
        <span class="text-lg font-bold text-[#2B2E2E]">Total</span>
        <span class="text-2xl font-bold text-brand-400">${{ service?.price.toLocaleString() }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Service, Barber, TimeSlot } from '@/services/publicApi'

defineProps<{
  service: Service | null
  barber: Barber | null
  date: string
  slot: TimeSlot | null
  clientName: string
  clientPhone: string
}>()

function formatDate(dateStr: string): string {
  if (!dateStr) return ''
  const d = new Date(dateStr + 'T12:00:00')
  return d.toLocaleDateString('es-AR', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

function formatTime(time: string): string {
  return time.substring(0, 5)
}
</script>
