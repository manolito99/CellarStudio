<template>
  <div>

    <!-- ── Page header ──────────────────────────────────────────────── -->
    <div class="flex items-center justify-between mb-4">
      <h1 class="text-xl sm:text-2xl font-bold text-gray-900">Citas</h1>

      <div class="flex items-center gap-2">
        <!-- View toggle -->
        <div class="flex bg-gray-100 rounded-lg p-0.5">
          <button
            @click="viewMode = 'calendar'"
            class="px-3 py-1.5 text-xs font-medium rounded-md transition-colors"
            :class="viewMode === 'calendar' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-400 hover:text-gray-700'"
          >
            <svg class="w-4 h-4 inline-block mr-1 -mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
            </svg>
            Calendario
          </button>
          <button
            @click="viewMode = 'list'"
            class="px-3 py-1.5 text-xs font-medium rounded-md transition-colors"
            :class="viewMode === 'list' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-400 hover:text-gray-700'"
          >
            <svg class="w-4 h-4 inline-block mr-1 -mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16"/>
            </svg>
            Lista
          </button>
        </div>

        <!-- Export button (list view, with download icon) -->
        <button
          v-if="viewMode === 'list' && appointments.length > 0"
          @click="exportAll"
          class="flex items-center gap-1.5 px-3 py-2 bg-gray-100 text-gray-600 text-sm font-medium rounded-lg hover:bg-gray-200 active:bg-gray-300 transition-colors"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/>
          </svg>
          <span class="hidden sm:inline">Exportar</span>
        </button>

        <!-- Nueva cita button -->
        <button
          @click="showCreateModal = true"
          class="flex items-center gap-1.5 px-3 py-2 bg-black text-white text-sm font-semibold rounded-lg hover:bg-gray-800 active:bg-gray-900 transition-colors"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
          </svg>
          <span class="hidden sm:inline">Nueva cita</span>
        </button>
      </div>
    </div>

    <!-- ═══════ CALENDAR VIEW ═══════ -->
    <CalendarGrid
      v-if="viewMode === 'calendar'"
      ref="calendarRef"
      @click-appointment="openModal"
    />

    <!-- ═══════ LIST VIEW ═══════ -->
    <template v-else>

      <!-- Filters row -->
      <div class="flex flex-wrap gap-2 mb-4">
        <!-- Search by client name -->
        <div class="relative flex-1 min-w-[160px]">
          <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
          </svg>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Buscar cliente..."
            class="w-full pl-9 pr-3 py-2 bg-white border border-gray-200 rounded-lg text-sm text-gray-800 placeholder-gray-400 focus:border-black focus:outline-none transition-colors"
          />
        </div>

        <select
          v-model="filters.status"
          class="flex-1 min-w-[120px] px-3 py-2 bg-white border border-gray-200 rounded-lg text-sm text-gray-800 focus:border-black focus:outline-none transition-colors"
        >
          <option value="">Todos los estados</option>
          <option value="pending">Pendiente</option>
          <option value="confirmed">Confirmada</option>
          <option value="completed">Completada</option>
          <option value="cancelled">Cancelada</option>
          <option value="noshow">No asistió</option>
        </select>

        <input
          v-model="filters.date_from"
          type="date"
          class="flex-1 min-w-[130px] px-3 py-2 bg-white border border-gray-200 rounded-lg text-sm text-gray-800 focus:border-black focus:outline-none transition-colors"
        />
        <input
          v-model="filters.date_to"
          type="date"
          class="flex-1 min-w-[130px] px-3 py-2 bg-white border border-gray-200 rounded-lg text-sm text-gray-800 focus:border-black focus:outline-none transition-colors"
        />
      </div>

      <!-- Loading -->
      <div v-if="loading" class="py-12 text-center text-sm text-gray-400">Cargando citas...</div>

      <!-- Empty state -->
      <div v-else-if="groupedAppointments.length === 0" class="py-12 text-center text-gray-400">
        <svg class="w-10 h-10 mx-auto mb-3 text-gray-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
        </svg>
        <p class="text-sm">No hay citas con estos filtros</p>
      </div>

      <!-- Grouped list -->
      <template v-else>
        <template v-for="group in groupedAppointments" :key="group.date">

          <!-- Date separator -->
          <div class="flex items-center gap-3 mt-5 mb-2 first:mt-0">
            <span class="text-xs font-semibold text-gray-400 uppercase tracking-wide whitespace-nowrap">
              {{ group.label }}
            </span>
            <div class="flex-1 h-px bg-gray-100" />
            <span class="text-xs text-gray-400 whitespace-nowrap">
              {{ group.items.length }} cita{{ group.items.length !== 1 ? 's' : '' }}
            </span>
          </div>

          <!-- Cards for this day -->
          <div class="space-y-2.5">
            <div
              v-for="appt in group.items"
              :key="appt.id"
              class="bg-white border border-gray-200 rounded-xl p-4 hover:border-gray-300 transition-colors"
            >
              <!-- Top row: time + client + status -->
              <div class="flex items-start justify-between mb-3">
                <div class="flex items-center gap-3 min-w-0">
                  <!-- Time badge -->
                  <div class="flex-shrink-0 text-center bg-gray-100 rounded-lg px-2.5 py-1.5">
                    <p class="text-xs font-bold text-gray-800 leading-none">{{ formatTime(appt.start_time) }}</p>
                    <p class="text-[10px] text-gray-400 leading-none mt-0.5">{{ formatTime(appt.end_time) }}</p>
                  </div>
                  <!-- Client name -->
                  <div class="min-w-0">
                    <p class="font-semibold text-gray-900 truncate">{{ appt.client.name }}</p>
                    <p class="text-sm text-gray-400">{{ appt.service.name }}</p>
                  </div>
                </div>
                <!-- Status selector -->
                <select
                  :value="appt.status"
                  @change="changeStatus(appt.id, ($event.target as HTMLSelectElement).value)"
                  class="ml-2 flex-shrink-0 px-2 py-1 rounded-lg text-xs font-medium border-0 focus:outline-none cursor-pointer"
                  :class="statusClasses[appt.status] || 'bg-gray-100 text-gray-500'"
                >
                  <option value="pending">Pendiente</option>
                  <option value="confirmed">Confirmada</option>
                  <option value="completed">Completada</option>
                  <option value="cancelled">Cancelada</option>
                  <option value="noshow">No asistió</option>
                </select>
              </div>

              <!-- Details row -->
              <div class="flex flex-wrap gap-x-4 gap-y-1 text-sm text-gray-500 mb-3">
                <span><span class="text-gray-400">Barbero:</span> <span class="text-gray-700">{{ appt.barber.name }}</span></span>
                <span><span class="text-gray-400">Precio:</span> <span class="font-medium text-gray-700">{{ appt.service.price }}€</span></span>
                <a :href="'tel:' + appt.client.phone" class="hover:text-black transition-colors">
                  {{ appt.client.phone }}
                </a>
                <span v-if="appt.client.email" class="truncate max-w-[180px]">{{ appt.client.email }}</span>
              </div>

              <!-- Actions -->
              <div class="flex items-center gap-2 pt-2.5 border-t border-gray-100">
                <button
                  @click="openModal(appt)"
                  class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-black/5 text-gray-700 hover:bg-black/10 active:bg-black/15 transition-colors"
                >
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                  </svg>
                  Editar
                </button>
                <button
                  @click="exportSingle(appt)"
                  class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-blue-50 text-blue-600 hover:bg-blue-100 active:bg-blue-200 transition-colors"
                >
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                  </svg>
                  .ics
                </button>
                <a
                  :href="'tel:' + appt.client.phone"
                  class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-green-50 text-green-700 hover:bg-green-100 active:bg-green-200 transition-colors"
                >
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/>
                  </svg>
                  Llamar
                </a>
                <div class="flex-1" />
                <button
                  @click="deleteAppointment(appt.id)"
                  class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-red-500 hover:bg-red-50 active:bg-red-100 transition-colors"
                >
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                  </svg>
                  Eliminar
                </button>
              </div>
            </div>
          </div>

        </template>
      </template>

    </template>
    <!-- /List view -->

    <!-- ── Edit Modal ──────────────────────────────────────────────── -->
    <AppointmentEditModal
      v-if="selectedAppointment"
      :appointment="selectedAppointment"
      @close="selectedAppointment = null"
      @saved="onModalSaved"
      @deleted="onModalDeleted"
    />

    <!-- ── Create Modal ────────────────────────────────────────────── -->
    <AppointmentCreateModal
      v-if="showCreateModal"
      @close="showCreateModal = false"
      @saved="onCreateSaved"
    />

  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { adminApi, type Appointment } from '@/services/adminApi'
import { downloadICS, downloadSingleICS } from '@/utils/icsExport'
import CalendarGrid from '@/components/admin/CalendarGrid.vue'
import AppointmentEditModal from '@/components/admin/AppointmentEditModal.vue'
import AppointmentCreateModal from '@/components/admin/AppointmentCreateModal.vue'

// ── View state ────────────────────────────────────────────────────────────────
const viewMode          = ref<'calendar' | 'list'>('calendar')
const calendarRef       = ref<InstanceType<typeof CalendarGrid> | null>(null)
const selectedAppointment = ref<Appointment | null>(null)
const showCreateModal   = ref(false)

// ── List data ─────────────────────────────────────────────────────────────────
const appointments = ref<Appointment[]>([])
const loading      = ref(false)
const searchQuery  = ref('')

function todayStr(): string {
  const d = new Date()
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

const filters = reactive({ status: '', date_from: todayStr(), date_to: '' })

// ── Status display ────────────────────────────────────────────────────────────
const statusClasses: Record<string, string> = {
  pending:   'bg-yellow-100 text-yellow-700',
  confirmed: 'bg-blue-100   text-blue-700',
  completed: 'bg-green-100  text-green-700',
  cancelled: 'bg-red-100    text-red-600',
  noshow:    'bg-gray-100   text-gray-500',
}

// ── Formatting helpers ────────────────────────────────────────────────────────
function formatTime(t: string): string {
  return t.substring(0, 5)
}

function formatDateLabel(dateStr: string): string {
  const date  = new Date(dateStr + 'T12:00:00')
  const today = new Date(); today.setHours(0, 0, 0, 0)
  const diff  = Math.round((date.getTime() - today.getTime()) / 86_400_000)
  const label = date.toLocaleDateString('es-ES', { weekday: 'long', day: 'numeric', month: 'short' })
  if (diff === 0)  return `Hoy · ${label}`
  if (diff === 1)  return `Mañana · ${label}`
  if (diff === -1) return `Ayer · ${label}`
  return label.charAt(0).toUpperCase() + label.slice(1)
}

// ── Filtered + grouped appointments ──────────────────────────────────────────
const filteredAppointments = computed(() => {
  if (!searchQuery.value.trim()) return appointments.value
  const q = searchQuery.value.toLowerCase().trim()
  return appointments.value.filter(a =>
    a.client.name.toLowerCase().includes(q) ||
    a.client.phone.includes(q)
  )
})

const groupedAppointments = computed(() => {
  const result: Array<{ date: string; label: string; items: Appointment[] }> = []
  let lastDate = ''
  for (const appt of filteredAppointments.value) {
    if (appt.date !== lastDate) {
      lastDate = appt.date
      result.push({ date: appt.date, label: formatDateLabel(appt.date), items: [] })
    }
    result[result.length - 1].items.push(appt)
  }
  return result
})

// ── API calls ─────────────────────────────────────────────────────────────────
async function loadAppointments() {
  loading.value = true
  try {
    const params: Record<string, string> = {}
    if (filters.status)    params.status    = filters.status
    if (filters.date_from) params.date_from = filters.date_from
    if (filters.date_to)   params.date_to   = filters.date_to
    appointments.value = await adminApi.getAppointments(params)
  } catch (err) {
    console.error('[AppointmentsPage] loadAppointments error:', err)
    appointments.value = []
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

// ── Modal handlers ────────────────────────────────────────────────────────────
function openModal(appt: Appointment) {
  selectedAppointment.value = appt
}

function onModalSaved() {
  selectedAppointment.value = null
  viewMode.value === 'calendar' ? calendarRef.value?.refresh() : loadAppointments()
}

function onModalDeleted() {
  selectedAppointment.value = null
  viewMode.value === 'calendar' ? calendarRef.value?.refresh() : loadAppointments()
}

function onCreateSaved() {
  showCreateModal.value = false
  viewMode.value === 'calendar' ? calendarRef.value?.refresh() : loadAppointments()
}

// ── Export ────────────────────────────────────────────────────────────────────
function exportSingle(appt: Appointment) { downloadSingleICS(appt) }
function exportAll()                     { downloadICS(appointments.value) }

// ── Lifecycle + watchers ──────────────────────────────────────────────────────
onMounted(() => {
  if (viewMode.value === 'list') loadAppointments()
})

watch(viewMode, (mode) => {
  if (mode === 'list') loadAppointments()
})

watch(
  () => [filters.status, filters.date_from, filters.date_to],
  () => { if (viewMode.value === 'list') loadAppointments() }
)
</script>
