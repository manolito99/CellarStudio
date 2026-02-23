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

      <!-- Working hours + recurring weekdays card -->
      <div class="bg-white border border-gray-200 rounded-xl p-5">

        <!-- Hours row -->
        <div class="flex flex-wrap items-center gap-3 mb-5">
          <span class="text-sm font-medium text-[#1d1d1f]">Horario de trabajo:</span>
          <input
            type="time" v-model="workStart"
            class="px-2 py-1 bg-[#f5f5f7] border border-gray-200 rounded text-sm text-[#1d1d1f] focus:border-[#1d1d1f] focus:outline-none"
          />
          <span class="text-[#86868b] text-sm">—</span>
          <input
            type="time" v-model="workEnd"
            class="px-2 py-1 bg-[#f5f5f7] border border-gray-200 rounded text-sm text-[#1d1d1f] focus:border-[#1d1d1f] focus:outline-none"
          />
          <button
            @click="saveRecurring"
            :disabled="savingRecurring"
            class="ml-auto px-3 py-1.5 bg-[#1d1d1f] text-white text-xs font-medium rounded-lg disabled:opacity-50"
          >
            {{ savingRecurring ? 'Guardando...' : 'Guardar horario' }}
          </button>
        </div>

        <!-- Recurring weekday toggles -->
        <div>
          <p class="text-xs text-[#86868b] mb-2">Días recurrentes — se repiten cada semana. Clic para activar/desactivar.</p>
          <div class="flex gap-1.5 flex-wrap">
            <button
              v-for="(name, i) in DAY_NAMES"
              :key="i"
              @click="toggleWeekday(i)"
              :disabled="savingRecurring"
              class="w-10 h-10 rounded-full text-sm font-semibold transition-all disabled:opacity-50"
              :class="activeWeekdays.has(i)
                ? 'bg-[#1d1d1f] text-white'
                : 'bg-[#f5f5f7] text-[#86868b] hover:bg-[#e8e8ed]'"
            >
              {{ name }}
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
const MONTH_NAMES = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']

// ── State ────────────────────────────────────────────────────────────────────
const barbers = ref<{ id: string; name: string }[]>([])
const selectedBarberId = ref('')

const workStart = ref('09:00')
const workEnd = ref('20:00')
const activeWeekdays = ref<Set<number>>(new Set())
const scheduleEntries = ref<ScheduleEntry[]>([])
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
  return activeWeekdays.value.has(weekdayOf(d))
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

    scheduleEntries.value = entries
    availableDays.value = avDays
    blockedSlots.value = blocks

    const wds = new Set<number>()
    for (const e of entries) {
      wds.add(e.day_of_week)
    }
    activeWeekdays.value = wds

    // Use existing schedule time as default for work hours
    if (entries.length > 0) {
      workStart.value = entries[0].start_time.substring(0, 5)
      workEnd.value = entries[0].end_time.substring(0, 5)
    }
  } finally {
    loading.value = false
  }
}

// ── Toggle weekday (recurring) ───────────────────────────────────────────────
async function toggleWeekday(wd: number) {
  if (!selectedBarberId.value) return
  const next = new Set(activeWeekdays.value)
  if (next.has(wd)) {
    next.delete(wd)
  } else {
    next.add(wd)
  }
  activeWeekdays.value = next
  await saveRecurring()
}

async function saveRecurring() {
  savingRecurring.value = true
  try {
    const schedules = Array.from(activeWeekdays.value).map(day => ({
      day_of_week: day,
      start_time: workStart.value + ':00',
      end_time: workEnd.value + ':00',
    }))
    const updated = await adminApi.updateBarberSchedule(selectedBarberId.value, schedules)
    scheduleEntries.value = updated
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

    // 2. Has a specific AvailableDay? → remove it (close the day)
    const specificAvail = availableDays.value.find(a => a.date === ds)
    if (specificAvail) {
      await adminApi.deleteAvailableDay(specificAvail.id)
      availableDays.value = availableDays.value.filter(a => a.id !== specificAvail.id)
      return
    }

    // 3. Is available via recurring weekday? → add full-day block (exception closure)
    if (activeWeekdays.value.has(weekdayOf(d))) {
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

    // 4. Not available at all? → add specific AvailableDay (exception opening)
    const newDay = await adminApi.createAvailableDay({
      barber_id: selectedBarberId.value,
      date: ds,
      start_time: workStart.value + ':00',
      end_time: workEnd.value + ':00',
    })
    availableDays.value.push(newDay)

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
})
</script>
