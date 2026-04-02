<template>
  <div class="bg-white border border-gray-200 rounded-xl overflow-hidden">

    <!-- ── Navigation bar ──────────────────────────────────────────────── -->
    <div class="flex items-center justify-between px-4 py-3 border-b border-gray-200">
      <div class="flex items-center gap-1">
        <button
          @click="prevWeek"
          class="p-1.5 rounded-lg hover:bg-gray-100 transition-colors"
          aria-label="Semana anterior"
        >
          <svg class="w-4 h-4 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
          </svg>
        </button>
        <button
          @click="jumpToToday"
          class="px-2.5 py-1 text-xs font-medium text-black bg-black/5 rounded-lg hover:bg-black/10 transition-colors"
        >
          Hoy
        </button>
        <button
          @click="nextWeek"
          class="p-1.5 rounded-lg hover:bg-gray-100 transition-colors"
          aria-label="Semana siguiente"
        >
          <svg class="w-4 h-4 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
          </svg>
        </button>
      </div>
      <span class="text-sm font-medium text-gray-800 tabular-nums select-none">{{ weekLabel }}</span>
    </div>

    <!-- ── Unified scroll container (both axes) ───────────────────────── -->
    <div ref="scrollEl" class="overflow-auto" style="max-height:620px;">
      <!-- Inner wrapper enforces the minimum total width -->
      <div :style="{ minWidth: totalWidth + 'px' }">

        <!-- ── Sticky day-header row ─────────────────────────────────── -->
        <div
          class="flex bg-white border-b border-gray-200"
          style="position:sticky;top:0;z-index:20;"
        >
          <!-- Corner cell: sticky on BOTH top and left -->
          <div
            class="flex-shrink-0 bg-white border-r border-gray-100"
            :style="{ width: TIME_COL_W + 'px', position:'sticky', left:0, zIndex:30 }"
          />

          <!-- Day header cells -->
          <div
            v-for="(day, i) in weekDays"
            :key="i"
            class="flex-1 flex flex-col items-center pt-2 pb-2.5 border-l border-gray-100 select-none"
            :class="isToday(day) ? 'bg-gray-50' : ''"
            :style="{ minWidth: DAY_COL_W + 'px' }"
          >
            <span class="text-[10px] font-semibold uppercase tracking-widest text-gray-400 leading-none">
              {{ shortDayNames[day.getDay()] }}
            </span>
            <!-- Date circle: filled black when today -->
            <span
              class="mt-1 w-7 h-7 flex items-center justify-center rounded-full text-sm font-semibold leading-none transition-colors"
              :class="isToday(day) ? 'bg-black text-white' : 'text-gray-800'"
            >
              {{ day.getDate() }}
            </span>
            <!-- Appointment-count dots (max 3) -->
            <div class="flex gap-0.5 mt-1.5" style="min-height:4px;">
              <span
                v-for="n in Math.min((appointmentsByDay[formatDateKey(day)] || []).length, 3)"
                :key="n"
                class="w-1 h-1 rounded-full inline-block"
                :class="isToday(day) ? 'bg-black/50' : 'bg-gray-300'"
              />
            </div>
          </div>
        </div>

        <!-- ── Grid body ─────────────────────────────────────────────── -->
        <div class="relative flex" :style="{ height: gridHeight + 'px' }">

          <!-- Time-label column: sticky left -->
          <div
            class="flex-shrink-0 bg-white border-r border-gray-100 relative"
            :style="{ width: TIME_COL_W + 'px', position:'sticky', left:0, zIndex:10 }"
          >
            <div
              v-for="h in hours"
              :key="h"
              class="absolute right-2 text-[11px] text-gray-400 select-none"
              style="transform:translateY(-50%);"
              :style="{ top: (h - START_HOUR) * HOUR_HEIGHT + 'px' }"
            >
              {{ h }}:00
            </div>
          </div>

          <!-- All day columns -->
          <div class="relative flex flex-1">

            <!-- Full-hour grid lines (span all columns) -->
            <div class="absolute inset-0 pointer-events-none">
              <div
                v-for="h in hours"
                :key="'hr' + h"
                class="absolute left-0 right-0 border-t border-gray-100"
                :style="{ top: (h - START_HOUR) * HOUR_HEIGHT + 'px' }"
              />
              <!-- Half-hour dashed lines -->
              <div
                v-for="h in hoursHalf"
                :key="'hh' + h"
                class="absolute left-0 right-0 border-t border-dashed border-gray-50"
                :style="{ top: ((h - START_HOUR) + 0.5) * HOUR_HEIGHT + 'px' }"
              />
            </div>

            <!-- Current-time red line -->
            <div
              v-if="nowLineTop !== null"
              class="absolute left-0 right-0 z-10 pointer-events-none"
              :style="{ top: nowLineTop + 'px' }"
            >
              <div class="relative w-full" style="height:2px;background:#f87171;">
                <div
                  class="absolute rounded-full bg-red-400"
                  style="width:10px;height:10px;left:-5px;top:-4px;"
                />
              </div>
            </div>

            <!-- Day columns -->
            <div
              v-for="(day, i) in weekDays"
              :key="i"
              class="relative border-l border-gray-100"
              :class="isToday(day) ? 'bg-black/[0.018]' : ''"
              :style="{ minWidth: DAY_COL_W + 'px', flex: '1' }"
            >
              <!-- Appointment blocks -->
              <div
                v-for="appt in (appointmentsByDay[formatDateKey(day)] || [])"
                :key="appt.id"
                class="absolute left-0.5 right-0.5 rounded-md px-1.5 py-0.5 overflow-hidden cursor-pointer text-xs leading-tight border transition-all hover:opacity-80 hover:shadow-sm active:scale-[0.98]"
                :class="statusClasses[appt.status] || 'bg-gray-100 text-gray-600 border-gray-200'"
                :style="getPosition(appt)"
                @click="$emit('clickAppointment', appt)"
              >
                <p class="font-semibold truncate">{{ appt.start_time.substring(0, 5) }} · {{ appt.client.name }}</p>
                <p class="truncate opacity-60" style="font-size:10px;">{{ appt.service.name }}</p>
              </div>
            </div>

          </div>
        </div>
        <!-- /Grid body -->

      </div>
    </div>
    <!-- /Scroll container -->

    <!-- States (loading / error / empty) -->
    <div v-if="loading" class="px-4 py-3 text-center text-sm text-gray-400">Cargando...</div>
    <div v-else-if="error" class="px-4 py-3 text-center text-sm text-red-500">
      {{ error }}
      <button @click="fetchWeekAppointments" class="ml-2 underline hover:text-red-700">Reintentar</button>
    </div>
    <div v-else-if="!loading && totalAppointments === 0" class="px-4 py-3 text-center text-sm text-gray-400">
      No hay citas esta semana
    </div>

  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref } from 'vue'
import type { Appointment } from '@/services/adminApi'
import { useCalendar, formatDateKey, START_HOUR, END_HOUR, HOUR_HEIGHT } from '@/composables/useCalendar'

defineEmits<{ clickAppointment: [appt: Appointment] }>()

// ── Layout constants ──────────────────────────────────────────────────────────
const TIME_COL_W = 52   // px — sticky time-label column
const DAY_COL_W  = 112  // px — min width per day column

const shortDayNames = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb']

const statusClasses: Record<string, string> = {
  pending:   'bg-yellow-50  text-yellow-700 border-yellow-300',
  confirmed: 'bg-blue-50    text-blue-700   border-blue-300',
  completed: 'bg-green-50   text-green-700  border-green-300',
  cancelled: 'bg-red-50     text-red-600    border-red-300',
  noshow:    'bg-gray-100   text-gray-500   border-gray-300',
}

// ── Calendar composable ───────────────────────────────────────────────────────
const {
  weekDays,
  weekLabel,
  appointmentsByDay,
  totalAppointments,
  loading,
  error,
  goToPrevWeek,
  goToNextWeek,
  goToToday,
  fetchWeekAppointments,
  getPosition,
} = useCalendar()

// ── Derived ───────────────────────────────────────────────────────────────────
const hours = computed<number[]>(() => {
  const h: number[] = []
  for (let i = START_HOUR; i <= END_HOUR; i++) h.push(i)
  return h
})

const hoursHalf = computed<number[]>(() => {
  const h: number[] = []
  for (let i = START_HOUR; i < END_HOUR; i++) h.push(i)
  return h
})

const gridHeight = (END_HOUR - START_HOUR) * HOUR_HEIGHT
const totalWidth = computed(() => TIME_COL_W + weekDays.value.length * DAY_COL_W)
const todayKey   = computed(() => formatDateKey(new Date()))

function isToday(d: Date): boolean {
  return formatDateKey(d) === todayKey.value
}

// ── Current-time red line ─────────────────────────────────────────────────────
const nowLineTop = ref<number | null>(null)
let   nowInterval: ReturnType<typeof setInterval> | null = null

function updateNowLine() {
  const now = new Date()
  const isThisWeek = weekDays.value.some(d => formatDateKey(d) === formatDateKey(now))
  if (!isThisWeek) { nowLineTop.value = null; return }
  const h = now.getHours()
  const m = now.getMinutes()
  if (h < START_HOUR || h > END_HOUR) { nowLineTop.value = null; return }
  nowLineTop.value = ((h - START_HOUR) * 60 + m) / 60 * HOUR_HEIGHT
}

// ── Scroll to today ───────────────────────────────────────────────────────────
const scrollEl = ref<HTMLElement | null>(null)

async function scrollToToday() {
  await nextTick()
  const idx = weekDays.value.findIndex(d => formatDateKey(d) === todayKey.value)
  if (idx < 0 || !scrollEl.value) return
  const containerW = scrollEl.value.clientWidth
  const dayLeft    = TIME_COL_W + idx * DAY_COL_W
  // Center today column horizontally
  scrollEl.value.scrollLeft = Math.max(0, dayLeft - (containerW - DAY_COL_W) / 2)
  // Scroll vertically so 08:00 is near the top
  scrollEl.value.scrollTop  = Math.max(0, (8 - START_HOUR) * HOUR_HEIGHT - 48)
}

// ── Navigation wrappers (also update now-line after data refresh) ─────────────
async function prevWeek() {
  goToPrevWeek()
  await nextTick()
  updateNowLine()
}

async function nextWeek() {
  goToNextWeek()
  await nextTick()
  updateNowLine()
}

async function jumpToToday() {
  goToToday()
  await nextTick()
  updateNowLine()
  scrollToToday()
}

// ── Lifecycle ─────────────────────────────────────────────────────────────────
onMounted(async () => {
  await fetchWeekAppointments()
  updateNowLine()
  nowInterval = setInterval(updateNowLine, 60_000)
  scrollToToday()
})

onUnmounted(() => {
  if (nowInterval) clearInterval(nowInterval)
})

defineExpose({ refresh: fetchWeekAppointments })
</script>
