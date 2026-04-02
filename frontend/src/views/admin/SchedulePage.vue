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
              @click="toggleDay(day)"
              :disabled="togglingDate === dateStr(day)"
              class="w-full aspect-square rounded-xl text-sm font-medium transition-all disabled:opacity-60 flex items-center justify-center"
              :class="dayClass(day)"
            >
              <span>{{ day.getDate() }}</span>
            </button>
            <div v-else class="w-full aspect-square" />
          </div>
        </div>

        <!-- Legend -->
        <div class="flex items-center gap-5 mt-4 text-xs text-[#86868b]">
          <span class="flex items-center gap-1.5">
            <span class="w-3 h-3 rounded-full bg-[#1d1d1f] inline-block"></span>
            Disponible
          </span>
          <span class="flex items-center gap-1.5">
            <span class="w-3 h-3 rounded-full bg-[#f5f5f7] border border-gray-300 inline-block"></span>
            No disponible
          </span>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { adminApi, type ScheduleEntry, type BlockedSlot, type AvailableDay } from '@/services/adminApi'

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
  blocks: TimeBlock[]
}

// ── State ────────────────────────────────────────────────────────────────────
const barbers = ref<{ id: string; name: string }[]>([])
const selectedBarberId = ref('')

const dayConfigs = ref<DayConfig[]>(
  DAY_FULL_NAMES.map((name, i) => ({
    day: i,
    name,
    isOpen: false,
    blocks: [{ start: '09:00', end: '20:00' }],
  }))
)

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
        }))
      )
    await adminApi.updateBarberSchedule(selectedBarberId.value, schedules)
  } finally {
    savingRecurring.value = false
  }
}

// ── Toggle individual day ────────────────────────────────────────────────────
async function toggleDay(d: Date) {
  if (!selectedBarberId.value) return
  const ds = dateStr(d)
  togglingDate.value = ds

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
        })
      )
    )
    availableDays.value.push(...newDays)

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
