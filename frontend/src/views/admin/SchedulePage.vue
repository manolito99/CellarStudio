<template>
  <div>
    <h1 class="text-xl sm:text-2xl font-bold text-[#1d1d1f] mb-6">Horarios y disponibilidad</h1>

    <!-- Barber selector -->
    <div class="mb-6">
      <label class="block text-sm text-[#86868b] mb-2">Barbero</label>
      <select
        v-model="selectedBarberId"
        @change="loadData"
        class="px-3 py-2 bg-white border border-gray-200 rounded-lg text-[#1d1d1f] focus:border-[#1d1d1f] focus:outline-none"
      >
        <option value="">Seleccionar barbero</option>
        <option v-for="b in barbers" :key="b.id" :value="b.id">{{ b.name }}</option>
      </select>
    </div>

    <div v-if="selectedBarberId" class="space-y-4">

      <!-- Weekly schedule card — per-day split shifts -->
      <div class="bg-white border border-gray-200 rounded-xl p-5">
        <div class="flex items-center justify-between mb-4">
          <div>
            <h3 class="text-sm font-semibold text-[#1d1d1f]">Horario semanal recurrente</h3>
            <p class="text-xs text-[#86868b] mt-0.5">Podés configurar varios tramos por día (turno partido)</p>
          </div>
          <button
            @click="saveRecurring"
            :disabled="savingRecurring"
            class="px-3 py-1.5 bg-[#1d1d1f] text-white text-xs font-medium rounded-lg disabled:opacity-50 shrink-0"
          >
            {{ savingRecurring ? 'Guardando...' : 'Guardar horario' }}
          </button>
        </div>

        <!-- Row per day -->
        <div
          v-for="cfg in dayConfigs"
          :key="cfg.day"
          class="py-3 border-b border-gray-50 last:border-0"
        >
          <!-- Day header: name + toggle -->
          <div class="flex items-center justify-between">
            <span
              class="text-sm font-medium"
              :class="cfg.isOpen ? 'text-[#1d1d1f]' : 'text-[#86868b]'"
            >
              {{ cfg.name }}
            </span>
            <button
              @click="toggleDayOpen(cfg)"
              :disabled="savingRecurring"
              class="w-10 h-6 rounded-full transition-colors relative shrink-0"
              :class="cfg.isOpen ? 'bg-[#1d1d1f]' : 'bg-[#e5e5ea]'"
            >
              <span
                class="absolute top-1 w-4 h-4 bg-white rounded-full shadow transition-all"
                :class="cfg.isOpen ? 'left-5' : 'left-1'"
              />
            </button>
          </div>

          <!-- Blocks (when open) -->
          <div v-if="cfg.isOpen" class="mt-2 space-y-2">
            <div
              v-for="(block, bi) in cfg.blocks"
              :key="bi"
              class="flex items-center gap-2"
            >
              <!-- Start time -->
              <input
                type="time"
                v-model="block.start"
                :disabled="savingRecurring"
                class="w-24 px-2 py-1.5 bg-[#f5f5f7] border border-gray-200 rounded-lg text-sm text-[#1d1d1f] focus:border-[#1d1d1f] focus:outline-none disabled:opacity-30 disabled:cursor-not-allowed"
              />
              <span class="text-[#86868b] text-sm select-none">–</span>
              <!-- End time -->
              <input
                type="time"
                v-model="block.end"
                :disabled="savingRecurring"
                class="w-24 px-2 py-1.5 bg-[#f5f5f7] border border-gray-200 rounded-lg text-sm text-[#1d1d1f] focus:border-[#1d1d1f] focus:outline-none disabled:opacity-30 disabled:cursor-not-allowed"
              />
              <!-- Remove block -->
              <button
                v-if="cfg.blocks.length > 1"
                @click="removeBlock(cfg, bi)"
                :disabled="savingRecurring"
                class="w-6 h-6 flex items-center justify-center rounded-full text-[#86868b] hover:bg-[#f5f5f7] hover:text-[#ff3b30] transition-colors disabled:opacity-30"
                title="Eliminar tramo"
              >
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M6 18L18 6M6 6l12 12"/>
                </svg>
              </button>
            </div>

            <!-- Add block -->
            <button
              @click="addBlock(cfg)"
              :disabled="savingRecurring"
              class="flex items-center gap-1 text-xs text-[#86868b] hover:text-[#1d1d1f] transition-colors mt-1 disabled:opacity-30"
            >
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 4v16m8-8H4"/>
              </svg>
              Agregar tramo
            </button>

            <!-- Intervalo entre citas -->
            <div class="flex flex-wrap items-center gap-2 pt-3 mt-1 border-t border-gray-50">
              <label class="text-xs text-[#86868b]">Intervalo entre citas</label>
              <select
                v-model.number="cfg.interval"
                :disabled="savingRecurring"
                class="px-2 py-1 bg-[#f5f5f7] border border-gray-200 rounded-lg text-sm text-[#1d1d1f] focus:border-[#1d1d1f] focus:outline-none disabled:opacity-30"
              >
                <option v-for="opt in INTERVAL_OPTIONS" :key="opt" :value="opt">{{ opt }} min</option>
              </select>
              <button
                type="button"
                @click="applyIntervalToAll(cfg.interval)"
                :disabled="savingRecurring"
                class="text-xs text-[#1d1d1f] underline hover:no-underline disabled:opacity-30"
              >
                Aplicar a todos los días
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Calendar card -->
      <div class="bg-white border border-gray-200 rounded-xl p-5">

        <!-- Month navigation -->
        <div class="flex items-center justify-between mb-5">
          <button
            @click="prevMonth"
            class="w-8 h-8 flex items-center justify-center rounded-full hover:bg-[#f5f5f7] text-[#1d1d1f]"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
            </svg>
          </button>
          <h2 class="text-base font-semibold text-[#1d1d1f] capitalize">
            {{ monthLabel }}
          </h2>
          <button
            @click="nextMonth"
            class="w-8 h-8 flex items-center justify-center rounded-full hover:bg-[#f5f5f7] text-[#1d1d1f]"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
            </svg>
          </button>
        </div>

        <!-- Day headers -->
        <div class="grid grid-cols-7 mb-1">
          <div
            v-for="name in DAY_NAMES"
            :key="name"
            class="text-center text-xs font-medium text-[#86868b] py-1"
          >
            {{ name }}
          </div>
        </div>

        <!-- Calendar grid -->
        <div v-if="loading" class="text-center py-8 text-[#86868b] text-sm">Cargando...</div>
        <div v-else class="grid grid-cols-7 gap-1">
          <div v-for="(day, idx) in calendarDays" :key="idx">
            <button
              v-if="day"
              @click="openDay(day)"
              class="w-full aspect-square rounded-xl text-sm font-medium transition-all flex flex-col items-center justify-center gap-0.5"
              :class="dayClass(day)"
            >
              <span>{{ day.getDate() }}</span>
              <!-- Punto: el dia esta abierto pero tiene horas sueltas bloqueadas -->
              <span
                class="w-1.5 h-1.5 rounded-full"
                :class="partialBlocks(day).length > 0
                  ? (isDayAvailable(day) ? 'bg-white/80' : 'bg-[#86868b]')
                  : 'bg-transparent'"
              />
            </button>
            <div v-else class="w-full aspect-square" />
          </div>
        </div>

        <!-- Legend -->
        <div class="flex flex-wrap items-center gap-x-5 gap-y-2 mt-4 text-xs text-[#86868b]">
          <span class="flex items-center gap-1.5">
            <span class="w-3 h-3 rounded-full bg-[#1d1d1f] inline-block"></span>
            Disponible
          </span>
          <span class="flex items-center gap-1.5">
            <span class="w-3 h-3 rounded-full bg-[#f5f5f7] border border-gray-300 inline-block"></span>
            No disponible
          </span>
          <span class="flex items-center gap-1.5">
            <span class="w-3 h-3 rounded-full bg-[#1d1d1f] inline-flex items-center justify-center">
              <span class="w-1 h-1 rounded-full bg-white inline-block"></span>
            </span>
            Con horas bloqueadas
          </span>
        </div>

        <p class="mt-3 text-xs text-[#86868b]">Toca un día para abrirlo, cerrarlo o bloquear horas sueltas.</p>
      </div>

    </div>

    <!-- ── Panel del día ────────────────────────────────────────────────────
         Teleport a <body> + dvh + acciones sticky: dentro de <ion-content> la
         tab bar del AdminLayout tapa los botones al abrirse el teclado.
         Ver CLAUDE.md > "Modales del admin". -->
    <Teleport to="body">
    <div
      v-if="selectedDay"
      class="fixed inset-0 z-50 flex items-center justify-center p-4 pb-[max(1rem,env(safe-area-inset-bottom))]"
      @click.self="selectedDay = null"
    >
      <div class="absolute inset-0 bg-black/40" @click="selectedDay = null" />

      <div class="relative flex flex-col bg-white rounded-2xl shadow-xl w-full max-w-md max-h-[90dvh]">

        <!-- Cabecera -->
        <div class="flex-shrink-0 flex items-center justify-between px-4 py-3 border-b border-gray-200">
          <h2 class="text-base font-bold text-[#1d1d1f] capitalize">{{ selectedDayLabel }}</h2>
          <button @click="selectedDay = null" class="p-1.5 rounded-lg hover:bg-gray-100 transition-colors">
            <svg class="w-5 h-5 text-[#86868b]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>

        <!-- Cuerpo -->
        <div class="flex-1 overflow-y-auto p-4 space-y-5">

          <p v-if="dayError" class="px-3 py-2 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600">
            {{ dayError }}
          </p>

          <!-- Estado del día -->
          <div>
            <p class="text-xs font-medium text-[#86868b] mb-2">Estado del día</p>
            <button
              @click="toggleDay(selectedDay)"
              :disabled="togglingDate !== null"
              class="w-full min-h-[44px] px-4 rounded-xl text-sm font-semibold transition-colors disabled:opacity-50"
              :class="selectedDayOpen
                ? 'bg-[#f5f5f7] text-[#1d1d1f] hover:bg-[#e8e8ed]'
                : 'bg-[#1d1d1f] text-white hover:bg-[#3a3a3c]'"
            >
              {{ togglingDate !== null ? 'Guardando...' : (selectedDayOpen ? 'Cerrar todo el día' : 'Abrir el día') }}
            </button>
            <p class="mt-1.5 text-xs text-[#86868b]">
              {{ selectedDayOpen ? 'Ahora mismo se puede reservar este día.' : 'Ahora mismo no se puede reservar este día.' }}
            </p>
          </div>

          <!-- Horas bloqueadas -->
          <div v-if="selectedDayOpen">
            <p class="text-xs font-medium text-[#86868b] mb-2">Horas bloqueadas</p>

            <div v-if="selectedDayBlocks.length === 0" class="text-sm text-[#86868b] mb-3">
              Ninguna. El día está libre entero.
            </div>

            <div v-else class="space-y-2 mb-3">
              <div
                v-for="b in selectedDayBlocks"
                :key="b.id"
                class="flex items-center justify-between gap-2 px-3 py-2 bg-[#f5f5f7] rounded-lg"
              >
                <div class="min-w-0">
                  <p class="text-sm font-medium text-[#1d1d1f]">
                    {{ b.start_time.substring(0, 5) }} – {{ b.end_time.substring(0, 5) }}
                  </p>
                  <p v-if="b.reason" class="text-xs text-[#86868b] truncate">{{ b.reason }}</p>
                </div>
                <button
                  @click="removeBlockedSlot(b.id)"
                  :disabled="deletingBlockId === b.id"
                  class="flex-shrink-0 p-2 rounded-lg text-red-500 hover:bg-red-50 transition-colors disabled:opacity-40"
                  title="Desbloquear"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                  </svg>
                </button>
              </div>
            </div>

            <!-- Nueva franja -->
            <div class="pt-3 border-t border-gray-100 space-y-2">
              <p class="text-xs font-medium text-[#86868b]">Bloquear una franja</p>
              <div class="flex items-center gap-2">
                <input
                  type="time"
                  v-model="blockForm.start"
                  step="900"
                  class="flex-1 min-w-0 px-2 py-2 bg-[#f5f5f7] border border-gray-200 rounded-lg text-sm text-[#1d1d1f] focus:border-[#1d1d1f] focus:outline-none"
                />
                <span class="text-[#86868b] text-sm select-none">–</span>
                <input
                  type="time"
                  v-model="blockForm.end"
                  step="900"
                  class="flex-1 min-w-0 px-2 py-2 bg-[#f5f5f7] border border-gray-200 rounded-lg text-sm text-[#1d1d1f] focus:border-[#1d1d1f] focus:outline-none"
                />
              </div>
              <input
                type="text"
                v-model="blockForm.reason"
                maxlength="200"
                placeholder="Motivo (opcional)"
                class="w-full px-3 py-2 bg-[#f5f5f7] border border-gray-200 rounded-lg text-sm text-[#1d1d1f] placeholder-gray-400 focus:border-[#1d1d1f] focus:outline-none"
              />
              <p v-if="blockError" class="text-xs text-red-500">{{ blockError }}</p>
              <p class="text-xs text-[#86868b]">
                Solo impide reservas nuevas. Si ya hay una cita en esa franja, sigue en pie: cancélala desde Citas.
              </p>
            </div>
          </div>

          <p v-else class="text-sm text-[#86868b]">
            El día está cerrado entero, así que no hace falta bloquear horas sueltas.
          </p>
        </div>

        <!-- Acciones -->
        <div class="flex-shrink-0 flex items-center justify-end gap-2 px-4 py-3 border-t border-gray-200">
          <button
            @click="selectedDay = null"
            class="px-4 min-h-[44px] text-sm font-medium text-[#86868b] hover:bg-gray-100 rounded-xl transition-colors"
          >
            Cerrar
          </button>
          <button
            v-if="selectedDayOpen"
            @click="createBlock"
            :disabled="savingBlock"
            class="px-4 min-h-[44px] text-sm font-semibold text-white bg-[#1d1d1f] hover:bg-[#3a3a3c] rounded-xl transition-colors disabled:opacity-50"
          >
            {{ savingBlock ? 'Bloqueando...' : 'Bloquear franja' }}
          </button>
        </div>
      </div>
    </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref, onMounted } from 'vue'
import { adminApi, type ScheduleEntry, type BlockedSlot, type AvailableDay } from '@/services/adminApi'
import { errorMessage } from '@/utils/apiError'

const DAY_NAMES = ['Lu', 'Ma', 'Mi', 'Ju', 'Vi', 'Sa', 'Do']
const DAY_FULL_NAMES = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
const MONTH_NAMES = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']

// ── Types ─────────────────────────────────────────────────────────────────────
interface TimeBlock {
  start: string  // 'HH:MM'
  end: string    // 'HH:MM'
}

interface DayConfig {
  day: number     // 0 = Lunes … 6 = Domingo
  name: string
  isOpen: boolean
  interval: number  // minutos entre citas
  blocks: TimeBlock[]
}

const INTERVAL_OPTIONS = [15, 30, 45, 60]

// ── State ────────────────────────────────────────────────────────────────────
const barbers = ref<{ id: string; name: string }[]>([])
const selectedBarberId = ref('')

const dayConfigs = ref<DayConfig[]>(
  DAY_FULL_NAMES.map((name, i) => ({
    day: i,
    name,
    isOpen: false,
    interval: 60,
    blocks: [{ start: '09:00', end: '20:00' }],
  }))
)

function applyIntervalToAll(interval: number) {
  dayConfigs.value.forEach((c) => { c.interval = interval })
}

const availableDays = ref<AvailableDay[]>([])
const blockedSlots = ref<BlockedSlot[]>([])

const loading = ref(false)
const savingRecurring = ref(false)
const togglingDate = ref<string | null>(null)

// Calendar navigation
const calNav = ref(new Date())

// ── Computed ─────────────────────────────────────────────────────────────────
const monthLabel = computed(() =>
  `${MONTH_NAMES[calNav.value.getMonth()]} ${calNav.value.getFullYear()}`
)

const calendarDays = computed(() => {
  const year = calNav.value.getFullYear()
  const month = calNav.value.getMonth()
  const firstDay = new Date(year, month, 1)
  const lastDay = new Date(year, month + 1, 0)
  const startPad = (firstDay.getDay() + 6) % 7 // 0 = Monday

  const days: (Date | null)[] = []
  for (let i = 0; i < startPad; i++) days.push(null)
  for (let d = 1; d <= lastDay.getDate(); d++) days.push(new Date(year, month, d))
  while (days.length % 7 !== 0) days.push(null)
  return days
})

// ── Block helpers ─────────────────────────────────────────────────────────────
function toggleDayOpen(cfg: DayConfig) {
  cfg.isOpen = !cfg.isOpen
  if (cfg.isOpen && cfg.blocks.length === 0) {
    cfg.blocks = [{ start: '09:00', end: '20:00' }]
  }
}

function addBlock(cfg: DayConfig) {
  // Default new block starts after the last one
  const last = cfg.blocks[cfg.blocks.length - 1]
  cfg.blocks.push({ start: last?.end ?? '09:00', end: '20:00' })
}

function removeBlock(cfg: DayConfig, index: number) {
  cfg.blocks.splice(index, 1)
  if (cfg.blocks.length === 0) {
    cfg.isOpen = false
  }
}

// ── Helpers ──────────────────────────────────────────────────────────────────
function dateStr(d: Date): string {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

function weekdayOf(d: Date): number {
  return (d.getDay() + 6) % 7 // 0 = Monday
}

function isFullDayBlock(b: BlockedSlot): boolean {
  return b.start_time.substring(0, 5) === '00:00' && b.end_time.substring(0, 5) === '23:59'
}

function isDayAvailable(d: Date): boolean {
  const ds = dateStr(d)
  const hasFullBlock = blockedSlots.value.some(b => b.date === ds && isFullDayBlock(b))
  if (hasFullBlock) return false
  const hasSpecific = availableDays.value.some(a => a.date === ds)
  if (hasSpecific) return true
  return dayConfigs.value.find(c => c.day === weekdayOf(d))?.isOpen ?? false
}

function isToday(d: Date): boolean {
  const t = new Date()
  return d.getDate() === t.getDate() && d.getMonth() === t.getMonth() && d.getFullYear() === t.getFullYear()
}

function dayClass(d: Date): string {
  const available = isDayAvailable(d)
  const today = isToday(d)
  if (available) {
    return today
      ? 'bg-[#1d1d1f] text-white ring-2 ring-offset-1 ring-[#1d1d1f]'
      : 'bg-[#1d1d1f] text-white hover:bg-[#3a3a3c]'
  }
  return today
    ? 'bg-[#f5f5f7] text-[#1d1d1f] font-bold ring-2 ring-offset-1 ring-[#1d1d1f]'
    : 'bg-[#f5f5f7] text-[#86868b] hover:bg-[#e8e8ed]'
}

// ── Load data ────────────────────────────────────────────────────────────────
async function loadData() {
  if (!selectedBarberId.value) return
  loading.value = true
  try {
    const [entries, avDays, blocks] = await Promise.all([
      adminApi.getBarberSchedule(selectedBarberId.value),
      adminApi.getAvailableDays(selectedBarberId.value),
      adminApi.getBlockedSlots(selectedBarberId.value),
    ])

    availableDays.value = avDays
    blockedSlots.value = blocks

    // Populate per-day configs — group multiple entries per day_of_week
    dayConfigs.value = DAY_FULL_NAMES.map((name, i) => {
      const dayEntries = entries.filter((e: ScheduleEntry) => e.day_of_week === i)
      return {
        day: i,
        name,
        isOpen: dayEntries.length > 0,
        interval: dayEntries[0]?.slot_interval_minutes ?? 60,
        blocks: dayEntries.length > 0
          ? dayEntries.map((e: ScheduleEntry) => ({
              start: e.start_time.substring(0, 5),
              end: e.end_time.substring(0, 5),
            }))
          : [{ start: '09:00', end: '20:00' }],
      }
    })
  } finally {
    loading.value = false
  }
}

// ── Save recurring schedule ───────────────────────────────────────────────────
async function saveRecurring() {
  if (!selectedBarberId.value) return
  savingRecurring.value = true
  try {
    // Flatten: each open day contributes one entry per block
    const schedules = dayConfigs.value
      .filter(c => c.isOpen)
      .flatMap(c =>
        c.blocks.map(b => ({
          day_of_week: c.day,
          start_time: b.start + ':00',
          end_time: b.end + ':00',
          slot_interval_minutes: c.interval,
        }))
      )
    await adminApi.updateBarberSchedule(selectedBarberId.value, schedules)
  } finally {
    savingRecurring.value = false
  }
}

// ── Panel del día ────────────────────────────────────────────────────────────
// Tocar un día abre este panel en vez de alternar abierto/cerrado directamente:
// el toggle solo sabía de días enteros, y no había forma de cerrar una hora
// suelta aunque la API de blocked-slots siempre aceptó franjas.
const selectedDay = ref<Date | null>(null)
const blockForm = reactive({ start: '10:00', end: '11:00', reason: '' })
const blockError = ref('')
const dayError = ref('')
const savingBlock = ref(false)
const deletingBlockId = ref<string | null>(null)

const selectedDayStr = computed(() => (selectedDay.value ? dateStr(selectedDay.value) : ''))

const selectedDayLabel = computed(() =>
  selectedDay.value
    ? selectedDay.value.toLocaleDateString('es-ES', { weekday: 'long', day: 'numeric', month: 'long' })
    : ''
)

const selectedDayOpen = computed(() =>
  selectedDay.value ? isDayAvailable(selectedDay.value) : false
)

const selectedDayBlocks = computed(() =>
  blockedSlots.value
    .filter(b => b.date === selectedDayStr.value && !isFullDayBlock(b))
    .sort((a, b) => a.start_time.localeCompare(b.start_time))
)

/** Franjas sueltas de un día: las que no son el bloqueo de día completo. */
function partialBlocks(d: Date) {
  const ds = dateStr(d)
  return blockedSlots.value.filter(b => b.date === ds && !isFullDayBlock(b))
}

function addHour(hhmm: string): string {
  const [h, m] = hhmm.split(':').map(Number)
  const total = Math.min(h * 60 + m + 60, 23 * 60 + 59)
  return `${String(Math.floor(total / 60)).padStart(2, '0')}:${String(total % 60).padStart(2, '0')}`
}

function openDay(d: Date) {
  selectedDay.value = d
  blockError.value = ''
  dayError.value = ''
  // Arranca en el inicio del turno de ese día: lo normal es bloquear la
  // primera hora, no las 10:00 de un día que empieza a las 9.
  const cfg = dayConfigs.value.find(c => c.day === weekdayOf(d))
  const start = cfg?.blocks[0]?.start ?? '10:00'
  blockForm.start = start
  blockForm.end = addHour(start)
  blockForm.reason = ''
}

async function createBlock() {
  if (!selectedDay.value || !selectedBarberId.value || savingBlock.value) return
  blockError.value = ''

  if (blockForm.end <= blockForm.start) {
    blockError.value = 'La hora de fin debe ser posterior a la de inicio.'
    return
  }

  savingBlock.value = true
  try {
    const created = await adminApi.createBlockedSlot({
      barber_id: selectedBarberId.value,
      date: selectedDayStr.value,
      start_time: blockForm.start + ':00',
      end_time: blockForm.end + ':00',
      reason: blockForm.reason.trim() || null,
    })
    blockedSlots.value.push(created)
    blockForm.reason = ''
  } catch (err) {
    blockError.value = errorMessage(err, 'No se pudo bloquear la franja.')
  } finally {
    savingBlock.value = false
  }
}

async function removeBlockedSlot(id: string) {
  if (deletingBlockId.value) return
  deletingBlockId.value = id
  blockError.value = ''
  try {
    await adminApi.deleteBlockedSlot(id)
    blockedSlots.value = blockedSlots.value.filter(b => b.id !== id)
  } catch (err) {
    blockError.value = errorMessage(err, 'No se pudo desbloquear la franja.')
  } finally {
    deletingBlockId.value = null
  }
}

// ── Toggle individual day ────────────────────────────────────────────────────
async function toggleDay(d: Date) {
  if (!selectedBarberId.value) return
  const ds = dateStr(d)
  togglingDate.value = ds
  dayError.value = ''

  try {
    // 1. Has a full-day block? → remove it (unblock)
    const fullBlock = blockedSlots.value.find(b => b.date === ds && isFullDayBlock(b))
    if (fullBlock) {
      await adminApi.deleteBlockedSlot(fullBlock.id)
      blockedSlots.value = blockedSlots.value.filter(b => b.id !== fullBlock.id)
      return
    }

    // 2. Has specific AvailableDay records? → remove all for this date (close the day)
    const specificAvails = availableDays.value.filter(a => a.date === ds)
    if (specificAvails.length > 0) {
      await Promise.all(specificAvails.map(a => adminApi.deleteAvailableDay(a.id)))
      availableDays.value = availableDays.value.filter(a => a.date !== ds)
      return
    }

    // 3. Is available via recurring weekday? → add full-day block (exception closure)
    const cfg = dayConfigs.value.find(c => c.day === weekdayOf(d))
    if (cfg?.isOpen) {
      const newBlock = await adminApi.createBlockedSlot({
        barber_id: selectedBarberId.value,
        date: ds,
        start_time: '00:00:00',
        end_time: '23:59:00',
        reason: null,
      })
      blockedSlots.value.push(newBlock)
      return
    }

    // 4. Not available at all? → add AvailableDays for this date (one per recurring block)
    const blocks = cfg?.blocks ?? [{ start: '09:00', end: '20:00' }]
    const newDays = await Promise.all(
      blocks.map(b =>
        adminApi.createAvailableDay({
          barber_id: selectedBarberId.value,
          date: ds,
          start_time: b.start + ':00',
          end_time: b.end + ':00',
          slot_interval_minutes: cfg?.interval ?? 60,
        })
      )
    )
    availableDays.value.push(...newDays)

  } catch (err) {
    // Antes fallaba en silencio: el día se quedaba como estaba y no había
    // manera de saber si el cambio se habia guardado o no.
    dayError.value = errorMessage(err, 'No se pudo cambiar el estado del día.')
  } finally {
    togglingDate.value = null
  }
}

// ── Navigation ───────────────────────────────────────────────────────────────
function prevMonth() {
  const d = new Date(calNav.value)
  d.setMonth(d.getMonth() - 1)
  calNav.value = d
}

function nextMonth() {
  const d = new Date(calNav.value)
  d.setMonth(d.getMonth() + 1)
  calNav.value = d
}

onMounted(async () => {
  barbers.value = await adminApi.getBarbers()
  // Auto-select Maxi if present
  const maxi = barbers.value.find(b => b.name.toLowerCase().includes('maxi'))
  if (maxi) {
    selectedBarberId.value = maxi.id
    loadData()
  }
})
</script>
