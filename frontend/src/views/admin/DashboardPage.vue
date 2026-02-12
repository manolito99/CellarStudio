<template>
  <div>
    <h1 class="text-2xl font-bold text-[#2B2E2E] mb-6">Dashboard</h1>

    <!-- KPI Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      <StatsCard
        label="Citas hoy"
        :value="stats.appointments_today"
        icon='<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>'
        iconBg="bg-blue-500/10"
        iconColor="text-blue-400"
      />
      <StatsCard
        label="Ingresos hoy"
        :value="stats.revenue_today"
        prefix="$"
        icon='<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>'
        iconBg="bg-green-500/10"
        iconColor="text-green-400"
      />
      <StatsCard
        label="Ingresos semana"
        :value="stats.revenue_week"
        prefix="$"
        icon='<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"/></svg>'
        iconBg="bg-brand-500/10"
        iconColor="text-brand-400"
      />
      <StatsCard
        label="Clientes nuevos (mes)"
        :value="stats.new_clients_month"
        icon='<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"/></svg>'
        iconBg="bg-purple-500/10"
        iconColor="text-purple-400"
        :subtitle="`${stats.total_clients} clientes totales`"
      />
    </div>

    <!-- Today's appointments -->
    <div class="bg-white border border-gray-200 rounded-xl overflow-hidden">
      <div class="px-4 sm:px-6 py-4 border-b border-gray-200 flex items-center justify-between gap-2">
        <h2 class="text-lg font-bold text-[#2B2E2E]">Citas de hoy</h2>
        <div class="flex items-center gap-3">
          <button
            v-if="todayAppointments.length > 0"
            @click="downloadICS(todayAppointments, 'citas-hoy.ics')"
            class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-blue-500/10 text-blue-400 hover:bg-blue-500/20 active:bg-blue-500/30 transition-colors"
          >
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
            </svg>
            Calendario
          </button>
          <router-link to="/admin/appointments" class="text-sm text-brand-400 hover:text-brand-300">
            Ver todas
          </router-link>
        </div>
      </div>

      <div v-if="todayAppointments.length === 0" class="p-8 text-center text-dark-500">
        No hay citas programadas para hoy
      </div>

      <div v-else class="divide-y divide-gray-200">
        <div
          v-for="appt in todayAppointments"
          :key="appt.id"
          class="px-4 sm:px-6 py-4 flex items-center justify-between gap-3 hover:bg-gray-50 transition-colors"
        >
          <div class="flex items-center gap-3 min-w-0">
            <div class="text-center min-w-[50px] flex-shrink-0">
              <p class="text-base sm:text-lg font-bold text-[#2B2E2E]">{{ formatTime(appt.start_time) }}</p>
              <p class="text-xs text-dark-500">{{ formatTime(appt.end_time) }}</p>
            </div>
            <div class="min-w-0">
              <p class="text-[#2B2E2E] font-medium truncate">{{ appt.client.name }}</p>
              <p class="text-sm text-dark-400 truncate">{{ appt.service.name }} - {{ appt.barber.name }}</p>
            </div>
          </div>
          <span
            class="px-2 sm:px-3 py-1 rounded-full text-xs font-medium flex-shrink-0"
            :class="statusClasses[appt.status] || 'bg-gray-100 text-[#595959]'"
          >
            {{ statusLabels[appt.status] || appt.status }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { adminApi, type Appointment, type DashboardStats } from '@/services/adminApi'
import StatsCard from '@/components/admin/StatsCard.vue'
import { downloadICS } from '@/utils/icsExport'

const stats = reactive<DashboardStats>({
  appointments_today: 0,
  revenue_today: 0,
  revenue_week: 0,
  revenue_month: 0,
  new_clients_month: 0,
  total_clients: 0,
})

const todayAppointments = ref<Appointment[]>([])

const statusLabels: Record<string, string> = {
  pending: 'Pendiente',
  confirmed: 'Confirmada',
  completed: 'Completada',
  cancelled: 'Cancelada',
  noshow: 'No asistió',
}

const statusClasses: Record<string, string> = {
  pending: 'bg-yellow-500/10 text-yellow-400',
  confirmed: 'bg-blue-500/10 text-blue-400',
  completed: 'bg-green-500/10 text-green-400',
  cancelled: 'bg-red-500/10 text-red-400',
  noshow: 'bg-gray-100 text-[#595959]',
}

function formatTime(time: string): string {
  return time.substring(0, 5)
}

onMounted(async () => {
  const [s, a] = await Promise.all([adminApi.getStats(), adminApi.getAppointmentsToday()])
  Object.assign(stats, s)
  todayAppointments.value = a
})
</script>
