<template>
  <div>
    <h3 class="text-2xl font-heading font-bold text-[#1d1d1f] mb-2">Confirma tu reserva</h3>
    <p class="text-dark-400 mb-6">Revisa los datos antes de confirmar</p>

    <div class="bg-white border border-gray-200 rounded-2xl p-6 max-w-md space-y-4">
      <div class="flex justify-between items-center pb-4 border-b border-gray-200">
        <span class="text-[#86868b]">Servicio</span>
        <span class="text-[#1d1d1f] font-medium">{{ service?.name }}</span>
      </div>
      <div class="flex justify-between items-center pb-4 border-b border-gray-200">
        <span class="text-[#86868b]">Barbero</span>
        <span class="text-[#1d1d1f] font-medium">{{ barber?.name }}</span>
      </div>
      <div class="flex justify-between items-center pb-4 border-b border-gray-200">
        <span class="text-[#86868b]">Fecha</span>
        <span class="text-[#1d1d1f] font-medium">{{ formatDate(date) }}</span>
      </div>
      <div class="flex justify-between items-center pb-4 border-b border-gray-200">
        <span class="text-[#86868b]">Hora</span>
        <span class="text-[#1d1d1f] font-medium">{{ slot ? formatTime(slot.start_time) : '' }}</span>
      </div>
      <div class="flex justify-between items-center pb-4 border-b border-gray-200">
        <span class="text-[#86868b]">Duración</span>
        <span class="text-[#1d1d1f] font-medium">{{ service && service.duration_minutes >= 120 ? 'Consultar' : service?.duration_minutes + ' min' }}</span>
      </div>
      <div class="flex justify-between items-center pb-4 border-b border-gray-200">
        <span class="text-[#86868b]">Cliente</span>
        <span class="text-[#1d1d1f] font-medium">{{ clientName }}</span>
      </div>
      <div class="flex justify-between items-center">
        <span class="text-[#86868b]">Teléfono</span>
        <span class="text-[#1d1d1f] font-medium">{{ clientPhone }}</span>
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
  return d.toLocaleDateString('es-ES', {
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
