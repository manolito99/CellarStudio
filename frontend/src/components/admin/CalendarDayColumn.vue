<template>
  <div class="relative h-full">
    <div
      v-for="appt in appointments"
      :key="appt.id"
      :style="getPosition(appt)"
      class="absolute left-0.5 right-0.5 rounded px-1.5 py-0.5 overflow-hidden cursor-pointer text-xs leading-tight border transition-opacity hover:opacity-80"
      :class="statusClasses[appt.status] || 'bg-gray-100 text-gray-600 border-gray-200'"
      @click="$emit('clickAppointment', appt)"
    >
      <p class="font-medium truncate">{{ formatTime(appt.start_time) }} {{ appt.client.name }}</p>
      <p class="truncate opacity-75">{{ appt.service.name }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Appointment } from '@/services/adminApi'

defineProps<{
  date: Date
  appointments: Appointment[]
  getPosition: (appt: Appointment) => { top: string; height: string }
}>()

defineEmits<{
  clickAppointment: [appt: Appointment]
}>()

const statusClasses: Record<string, string> = {
  pending: 'bg-yellow-500/15 text-yellow-700 border-yellow-500/30',
  confirmed: 'bg-blue-500/15 text-blue-700 border-blue-500/30',
  completed: 'bg-green-500/15 text-green-700 border-green-500/30',
  cancelled: 'bg-red-500/15 text-red-700 border-red-500/30',
  noshow: 'bg-gray-200 text-gray-500 border-gray-300',
}

function formatTime(t: string): string {
  return t.substring(0, 5)
}
</script>
