<template>
  <div>
    <h3 class="text-2xl font-heading font-bold text-[#1d1d1f] mb-2">Elige fecha y hora</h3>
    <p class="text-dark-400 mb-6">Selecciona cuándo quieres tu cita</p>

    <!-- Loading state on first load -->
    <div v-if="loadingDates && availableDatesMap.size === 0" class="flex justify-center py-12">
      <ion-spinner name="crescent" color="dark" />
    </div>

    <div v-else class="space-y-6">

      <!-- Calendar + Recommendations -->
      <!-- Mobile: stacked. Desktop: side by side -->
      <div class="flex flex-col lg:grid lg:grid-cols-5 gap-4 lg:gap-6">

        <!-- Calendar (3/5 on desktop, full width on mobile) -->
        <div class="lg:col-span-3">
          <!-- Month navigation -->
          <div class="flex items-center justify-between mb-4">
            <button
              @click="prevMonth"
              class="w-8 h-8 flex items-center justify-center rounded-full hover:bg-[#f5f5f7] text-[#1d1d1f]"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
              </svg>
            </button>
            <span class="text-sm font-semibold text-[#1d1d1f] capitalize">{{ monthLabel }}</span>
            <button
              @click="nextMonth"
              class="w-8 h-8 flex items-center justify-center rounded-full hover:bg-[#f5f5f7] text-[#1d1d1f]"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
              </svg>
            </button>
          </div>

          <!-- Day name headers -->
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
          <div class="grid grid-cols-7 gap-1">
            <div v-for="(day, idx) in calendarDays" :key="idx">
              <button
                v-if="day"
                :disabled="!canSelectDay(day)"
                @click="onCalendarDayClick(day)"
                class="w-full aspect-square rounded-xl text-sm font-medium transition-all flex items-center justify-center"
                :class="calDayClass(day)"
              >
                {{ day.getDate() }}
              </button>
              <div v-else class="w-full aspect-square" />
            </div>
          </div>
        </div>

        <!-- Recommendations (2/5 on desktop) -->
        <div class="lg:col-span-2">
          <h4 class="text-sm font-semibold text-[#1d1d1f] mb-3">
            Próximas fechas disponibles
          </h4>

          <div v-if="loadingDates" class="space-y-2">
            <div v-for="i in 4" :key="i" class="h-14 bg-[#f5f5f7] rounded-xl animate-pulse" />
          </div>

          <div v-else-if="displayList.length === 0" class="text-sm text-[#86868b] py-4 text-center">
            No hay fechas disponibles próximamente
          </div>

          <!-- Mobile: horizontal scroll. Desktop: vertical list -->
          <div v-else class="flex lg:flex-col gap-2 overflow-x-auto lg:overflow-x-visible pb-1 lg:pb-0">
            <div
              v-for="rec in displayList"
              :key="rec.date"
              class="rounded-xl border overflow-hidden transition-all flex-shrink-0 w-40 lg:w-auto"
              :class="selectedDate === rec.date
                ? 'border-[#1d1d1f]'
                : 'border-gray-200'"
            >
              <!-- Date header — clickable -->
              <button
                @click="selectDateStr(rec.date)"
                class="w-full text-left px-3 py-2.5 transition-all"
                :class="selectedDate === rec.date
                  ? 'bg-[#1d1d1f] text-white'
                  : 'bg-white hover:bg-[#f5f5f7] text-[#1d1d1f]'"
              >
                <div class="text-sm font-semibold capitalize">{{ formatRecDate(rec.date) }}</div>
                <div
                  class="text-xs mt-0.5"
                  :class="selectedDate === rec.date ? 'text-gray-300' : 'text-[#86868b]'"
                >
                  {{ rec.slots_count }} {{ rec.slots_count === 1 ? 'hueco' : 'huecos' }} · primer hueco {{ rec.first_slot }}
                </div>
              </button>

              <!-- Inline time slots — only for the selected date -->
              <div v-if="selectedDate === rec.date" class="px-2 py-2 bg-[#f5f5f7] border-t border-gray-200">
                <div v-if="loading" class="flex justify-center py-3">
                  <ion-spinner name="crescent" color="dark" />
                </div>
                <div v-else-if="slots.length === 0" class="text-[#86868b] text-xs py-2 text-center">
                  No hay horarios
                </div>
                <div v-else class="grid grid-cols-2 lg:grid-cols-3 gap-1">
                  <button
                    v-for="slot in slots"
                    :key="slot.start_time"
                    @click="$emit('selectSlot', slot)"
                    class="px-2 py-1.5 rounded-lg text-xs font-medium transition-all"
                    :class="selectedSlot?.start_time === slot.start_time
                      ? 'bg-[#1d1d1f] text-white'
                      : 'bg-white border border-gray-200 text-[#1d1d1f] hover:border-[#1d1d1f]'"
                  >
                    {{ slot.start_time.substring(0, 5) }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch, onMounted } from 'vue'
import { IonSpinner } from '@ionic/vue'
import { publicApi, type TimeSlot, type AvailableDateInfo } from '@/services/publicApi'

const DAY_NAMES = ['Lu', 'Ma', 'Mi', 'Ju', 'Vi', 'Sa', 'Do']
const MONTH_NAMES = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']

const props = defineProps<{
  selectedDate: string
  slots: TimeSlot[]
  selectedSlot: TimeSlot | null
  loading: boolean
  barberId: string
  serviceId: string
}>()

const emit = defineEmits<{
  selectDate: [date: string]
  selectSlot: [slot: TimeSlot]
}>()

// ── Calendar nav ─────────────────────────────────────────────────────────────
const calNav = ref(new Date())

const monthLabel = computed(() =>
  `${MONTH_NAMES[calNav.value.getMonth()]} ${calNav.value.getFullYear()}`
)

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

const calendarDays = computed(() => {
  const year = calNav.value.getFullYear()
  const month = calNav.value.getMonth()
  const firstDay = new Date(year, month, 1)
  const lastDay = new Date(year, month + 1, 0)
  const startPad = (firstDay.getDay() + 6) % 7
  const days: (Date | null)[] = []
  for (let i = 0; i < startPad; i++) days.push(null)
  for (let d = 1; d <= lastDay.getDate(); d++) days.push(new Date(year, month, d))
  while (days.length % 7 !== 0) days.push(null)
  return days
})

// ── Available dates ───────────────────────────────────────────────────────────
const availableDatesMap = ref<Map<string, AvailableDateInfo>>(new Map())
const loadingDates = ref(false)

function toDateStr(d: Date): string {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

async function loadAvailableDates() {
  if (!props.barberId || !props.serviceId) return
  loadingDates.value = true
  try {
    const today = new Date()
    const from = toDateStr(today)
    const to90 = new Date(today)
    to90.setDate(to90.getDate() + 89)
    const to = toDateStr(to90)
    const dates = await publicApi.getAvailableDates(props.barberId, props.serviceId, from, to)
    const map = new Map<string, AvailableDateInfo>()
    for (const d of dates) map.set(d.date, d)
    availableDatesMap.value = map
  } finally {
    loadingDates.value = false
  }
}

// Reload when barber or service changes
watch([() => props.barberId, () => props.serviceId], () => {
  availableDatesMap.value = new Map()
  loadAvailableDates()
})

onMounted(() => {
  loadAvailableDates()
})

// ── Calendar day logic ────────────────────────────────────────────────────────
function isPast(d: Date): boolean {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  return d < today
}

function isAvailable(d: Date): boolean {
  return availableDatesMap.value.has(toDateStr(d))
}

function canSelectDay(d: Date): boolean {
  return !isPast(d) && isAvailable(d)
}

function isToday(d: Date): boolean {
  const t = new Date()
  return d.getDate() === t.getDate() && d.getMonth() === t.getMonth() && d.getFullYear() === t.getFullYear()
}

function calDayClass(d: Date): string {
  const ds = toDateStr(d)
  const selected = props.selectedDate === ds
  const available = isAvailable(d)
  const past = isPast(d)
  const today = isToday(d)

  if (selected) return 'bg-[#1d1d1f] text-white ring-2 ring-offset-1 ring-[#1d1d1f]'
  if (past || !available) return 'text-[#c7c7cc] cursor-not-allowed'
  if (today) return 'bg-[#f5f5f7] text-[#1d1d1f] font-bold ring-1 ring-[#1d1d1f] hover:bg-[#e8e8ed]'
  return 'bg-[#f5f5f7] text-[#1d1d1f] hover:bg-[#1d1d1f] hover:text-white'
}

function onCalendarDayClick(d: Date) {
  if (!canSelectDay(d)) return
  selectDateStr(toDateStr(d))
}

function selectDateStr(ds: string) {
  // Navigate calendar to the month of the selected date
  const [y, m] = ds.split('-').map(Number)
  const target = new Date(y, m - 1, 1)
  if (target.getMonth() !== calNav.value.getMonth() || target.getFullYear() !== calNav.value.getFullYear()) {
    calNav.value = target
  }
  emit('selectDate', ds)
}

// ── Recommendations ───────────────────────────────────────────────────────────
const recommendations = computed<AvailableDateInfo[]>(() => {
  const today = toDateStr(new Date())
  return Array.from(availableDatesMap.value.values())
    .filter(d => d.date >= today)
    .sort((a, b) => a.date.localeCompare(b.date))
    .slice(0, 6)
})

// If the date selected from the calendar is not in the recommendations list,
// prepend it so the inline slots can expand under it
const displayList = computed<AvailableDateInfo[]>(() => {
  const recs = recommendations.value
  if (!props.selectedDate) return recs
  const inList = recs.some(r => r.date === props.selectedDate)
  if (inList) return recs
  const info = availableDatesMap.value.get(props.selectedDate)
  return info ? [info, ...recs] : recs
})

// ── Formatting ────────────────────────────────────────────────────────────────
function formatRecDate(ds: string): string {
  return new Date(ds + 'T12:00:00').toLocaleDateString('es-ES', {
    weekday: 'short', day: 'numeric', month: 'short',
  })
}

const formatSelectedDate = computed(() => {
  if (!props.selectedDate) return ''
  return new Date(props.selectedDate + 'T12:00:00').toLocaleDateString('es-ES', {
    weekday: 'long', day: 'numeric', month: 'long',
  })
})
</script>
