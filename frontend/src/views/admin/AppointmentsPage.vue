<template>
  <div>
    <div class="flex items-center justify-between mb-4">
      <h1 class="text-xl sm:text-2xl font-bold text-[#2B2E2E]">Citas</h1>
      <button
        v-if="appointments.length > 0"
        @click="exportAll"
        class="flex items-center gap-2 px-3 py-2 bg-brand-500/10 text-brand-400 text-sm font-medium rounded-lg hover:bg-brand-500/20 active:bg-brand-500/30 transition-colors"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
        </svg>
        <span class="hidden sm:inline">Exportar al</span> Calendario
      </button>
    </div>

    <!-- Filters -->
    <div class="flex flex-wrap gap-2 mb-4">
      <select
        v-model="filters.status"
        @change="loadAppointments"
        class="flex-1 min-w-[120px] px-3 py-2 bg-white border border-gray-200 rounded-lg text-sm text-[#2B2E2E] focus:border-brand-400 focus:outline-none"
      >
        <option value="">Todos</option>
        <option value="pending">Pendiente</option>
        <option value="confirmed">Confirmada</option>
        <option value="completed">Completada</option>
        <option value="cancelled">Cancelada</option>
        <option value="noshow">No asistió</option>
      </select>
      <input
        v-model="filters.date_from"
        type="date"
        @change="loadAppointments"
        class="flex-1 min-w-[130px] px-3 py-2 bg-white border border-gray-200 rounded-lg text-sm text-[#2B2E2E] focus:border-brand-400 focus:outline-none"
      />
      <input
        v-model="filters.date_to"
        type="date"
        @change="loadAppointments"
        class="flex-1 min-w-[130px] px-3 py-2 bg-white border border-gray-200 rounded-lg text-sm text-[#2B2E2E] focus:border-brand-400 focus:outline-none"
      />
    </div>

    <!-- Card list (mobile + desktop) -->
    <div class="space-y-3">
      <div
        v-for="appt in appointments"
        :key="appt.id"
        class="bg-white border border-gray-200 rounded-xl p-4 hover:border-gray-300 transition-colors"
      >
        <!-- Top row: date/time + status -->
        <div class="flex items-start justify-between mb-3">
          <div class="flex items-center gap-3">
            <div class="w-12 h-12 rounded-xl bg-gray-100 flex flex-col items-center justify-center flex-shrink-0">
              <span class="text-xs text-dark-400 leading-none">{{ formatDay(appt.date) }}</span>
              <span class="text-sm font-bold text-[#2B2E2E] leading-tight">{{ formatDayNum(appt.date) }}</span>
            </div>
            <div>
              <p class="text-[#2B2E2E] font-semibold">{{ appt.client.name }}</p>
              <p class="text-dark-400 text-sm">{{ formatTime(appt.start_time) }} - {{ formatTime(appt.end_time) }}</p>
            </div>
          </div>
          <select
            :value="appt.status"
            @change="changeStatus(appt.id, ($event.target as HTMLSelectElement).value)"
            class="px-2 py-1 rounded-lg text-xs font-medium border-0 focus:outline-none cursor-pointer"
            :class="statusClasses[appt.status] || 'bg-gray-100 text-[#595959]'"
          >
            <option value="pending">Pendiente</option>
            <option value="confirmed">Confirmada</option>
            <option value="completed">Completada</option>
            <option value="cancelled">Cancelada</option>
            <option value="noshow">No asistió</option>
          </select>
        </div>

        <!-- Details -->
        <div class="flex flex-wrap gap-x-4 gap-y-1 text-sm mb-3">
          <span class="text-dark-400">
            <span class="text-dark-500">Servicio:</span> <span class="text-[#2B2E2E]">{{ appt.service.name }}</span>
          </span>
          <span class="text-dark-400">
            <span class="text-dark-500">Barbero:</span> <span class="text-[#2B2E2E]">{{ appt.barber.name }}</span>
          </span>
          <span class="text-dark-400">
            <span class="text-dark-500">Precio:</span> <span class="text-brand-400">${{ appt.service.price }}</span>
          </span>
        </div>

        <!-- Client info -->
        <div class="flex flex-wrap gap-x-4 gap-y-1 text-sm text-dark-500 mb-3">
          <a :href="'tel:' + appt.client.phone" class="hover:text-brand-400 transition-colors">
            {{ appt.client.phone }}
          </a>
          <span v-if="appt.client.email">{{ appt.client.email }}</span>
        </div>

        <!-- Actions -->
        <div class="flex items-center gap-2 pt-2 border-t border-gray-200">
          <button
            @click="exportSingle(appt)"
            class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-blue-500/10 text-blue-400 hover:bg-blue-500/20 active:bg-blue-500/30 transition-colors"
          >
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
            </svg>
            Calendario
          </button>
          <a
            :href="'tel:' + appt.client.phone"
            class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-green-500/10 text-green-400 hover:bg-green-500/20 active:bg-green-500/30 transition-colors"
          >
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/>
            </svg>
            Llamar
          </a>
          <div class="flex-1"></div>
          <button
            @click="deleteAppointment(appt.id)"
            class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-red-400 hover:bg-red-500/10 active:bg-red-500/20 transition-colors"
          >
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
            Eliminar
          </button>
        </div>
      </div>
    </div>

    <div v-if="!loading && appointments.length === 0" class="p-8 text-center text-dark-500">
      No hay citas con estos filtros
    </div>

    <div v-if="loading" class="p-8 text-center text-dark-500">
      Cargando citas...
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { adminApi, type Appointment } from '@/services/adminApi'
import { downloadICS, downloadSingleICS } from '@/utils/icsExport'

const appointments = ref<Appointment[]>([])
const loading = ref(false)
const filters = reactive({ status: '', date_from: '', date_to: '' })

const statusClasses: Record<string, string> = {
  pending: 'bg-yellow-500/10 text-yellow-400',
  confirmed: 'bg-blue-500/10 text-blue-400',
  completed: 'bg-green-500/10 text-green-400',
  cancelled: 'bg-red-500/10 text-red-400',
  noshow: 'bg-gray-100 text-[#595959]',
}

const dayNames = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb']

function formatDay(d: string): string {
  const date = new Date(d + 'T12:00:00')
  return dayNames[date.getDay()]
}

function formatDayNum(d: string): string {
  const date = new Date(d + 'T12:00:00')
  return date.getDate().toString()
}

function formatTime(t: string): string {
  return t.substring(0, 5)
}

async function loadAppointments() {
  loading.value = true
  try {
    const params: Record<string, string> = {}
    if (filters.status) params.status = filters.status
    if (filters.date_from) params.date_from = filters.date_from
    if (filters.date_to) params.date_to = filters.date_to
    appointments.value = await adminApi.getAppointments(params)
  } finally {
    loading.value = false
  }
}

async function changeStatus(id: string, status: string) {
  await adminApi.updateAppointmentStatus(id, status)
  await loadAppointments()
}

async function deleteAppointment(id: string) {
  if (!confirm('¿Eliminar esta cita?')) return
  await adminApi.deleteAppointment(id)
  await loadAppointments()
}

function exportSingle(appt: Appointment) {
  downloadSingleICS(appt)
}

function exportAll() {
  downloadICS(appointments.value)
}

onMounted(loadAppointments)
</script>
