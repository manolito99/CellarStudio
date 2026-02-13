<template>
  <div class="bg-white border border-gray-200 rounded-xl overflow-hidden">
    <!-- Header: nav + week label -->
    <div class="flex items-center justify-between p-3 border-b border-gray-200">
      <div class="flex items-center gap-1.5">
        <button @click="goToPrevWeek" class="p-1.5 rounded-lg hover:bg-gray-100 transition-colors">
          <svg class="w-4 h-4 text-[#1d1d1f]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
          </svg>
        </button>
        <button @click="goToToday" class="px-2.5 py-1 text-xs font-medium text-brand-400 bg-brand-500/10 rounded-lg hover:bg-brand-500/20 transition-colors">
          Hoy
        </button>
        <button @click="goToNextWeek" class="p-1.5 rounded-lg hover:bg-gray-100 transition-colors">
          <svg class="w-4 h-4 text-[#1d1d1f]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
          </svg>
        </button>
      </div>
      <span class="text-sm font-medium text-[#1d1d1f]">{{ weekLabel }}</span>
    </div>

    <!-- Desktop day headers (7 cols) -->
    <div class="hidden md:grid grid-cols-[60px_repeat(7,1fr)] border-b border-gray-200">
      <div></div>
      <div
        v-for="(day, i) in weekDays"
        :key="i"
        class="py-2 text-center border-l border-gray-100"
        :class="{ 'bg-brand-500/5': isToday(day) }"
      >
        <p class="text-xs text-dark-400">{{ shortDayNames[day.getDay()] }}</p>
        <p class="text-sm font-semibold" :class="isToday(day) ? 'text-brand-400' : 'text-[#1d1d1f]'">
          {{ day.getDate() }}
        </p>
      </div>
    </div>

    <!-- Mobile day headers (3 cols) -->
    <div class="grid md:hidden grid-cols-[40px_repeat(3,1fr)] border-b border-gray-200">
      <div></div>
      <div
        v-for="(day, i) in mobileDays"
        :key="i"
        class="py-2 text-center border-l border-gray-100"
        :class="{ 'bg-brand-500/5': isToday(day) }"
      >
        <p class="text-xs text-dark-400">{{ shortDayNames[day.getDay()] }}</p>
        <p class="text-sm font-semibold" :class="isToday(day) ? 'text-brand-400' : 'text-[#1d1d1f]'">
          {{ day.getDate() }}
        </p>
      </div>
    </div>

    <!-- Grid body -->
    <div class="overflow-y-auto" style="max-height: 600px">
      <!-- Desktop grid -->
      <div class="relative hidden md:grid grid-cols-[60px_repeat(7,1fr)]" :style="{ height: gridHeight + 'px' }">
        <!-- Hour labels -->
        <div class="relative">
          <div
            v-for="h in hours"
            :key="h"
            class="absolute right-2 text-xs text-dark-400 -translate-y-1/2"
            :style="{ top: (h - START_HOUR) * HOUR_HEIGHT + 'px' }"
          >
            {{ h }}:00
          </div>
        </div>
        <!-- Horizontal grid lines -->
        <div class="absolute left-[60px] right-0 top-0 pointer-events-none" :style="{ height: gridHeight + 'px' }">
          <div
            v-for="h in hours"
            :key="h"
            class="absolute left-0 right-0 border-t border-gray-100"
            :style="{ top: (h - START_HOUR) * HOUR_HEIGHT + 'px' }"
          ></div>
        </div>
        <!-- Current time red line -->
        <div
          v-if="nowLineTop !== null"
          class="absolute left-[60px] right-0 h-0.5 bg-red-400 z-10 pointer-events-none"
          :style="{ top: nowLineTop + 'px' }"
        >
          <div class="absolute -left-1.5 -top-1 w-3 h-3 bg-red-400 rounded-full"></div>
        </div>
        <!-- Day columns -->
        <div
          v-for="(day, i) in weekDays"
          :key="i"
          class="relative border-l border-gray-100"
          :class="{ 'bg-brand-500/5': isToday(day) }"
        >
          <CalendarDayColumn
            :date="day"
            :appointments="appointmentsByDay[formatDateKey(day)] || []"
            :get-position="getPosition"
            @click-appointment="$emit('clickAppointment', $event)"
          />
        </div>
      </div>

      <!-- Mobile grid (3 cols) -->
      <div class="relative md:hidden grid grid-cols-[40px_repeat(3,1fr)]" :style="{ height: gridHeight + 'px' }">
        <div class="relative">
          <div
            v-for="h in hours"
            :key="h"
            class="absolute right-1 text-[10px] text-dark-400 -translate-y-1/2"
            :style="{ top: (h - START_HOUR) * HOUR_HEIGHT + 'px' }"
          >
            {{ h }}
          </div>
        </div>
        <div class="absolute left-[40px] right-0 top-0 pointer-events-none" :style="{ height: gridHeight + 'px' }">
          <div
            v-for="h in hours"
            :key="h"
            class="absolute left-0 right-0 border-t border-gray-100"
            :style="{ top: (h - START_HOUR) * HOUR_HEIGHT + 'px' }"
          ></div>
        </div>
        <div
          v-if="nowLineTop !== null"
          class="absolute left-[40px] right-0 h-0.5 bg-red-400 z-10 pointer-events-none"
          :style="{ top: nowLineTop + 'px' }"
        ></div>
        <div
          v-for="(day, i) in mobileDays"
          :key="i"
          class="relative border-l border-gray-100"
          :class="{ 'bg-brand-500/5': isToday(day) }"
        >
          <CalendarDayColumn
            :date="day"
            :appointments="appointmentsByDay[formatDateKey(day)] || []"
            :get-position="getPosition"
            @click-appointment="$emit('clickAppointment', $event)"
          />
        </div>
      </div>
    </div>

    <div v-if="loading" class="p-4 text-center text-dark-500 text-sm">Cargando...</div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import type { Appointment } from '@/services/adminApi'
import CalendarDayColumn from './CalendarDayColumn.vue'
import { useCalendar, formatDateKey, START_HOUR, END_HOUR, HOUR_HEIGHT } from '@/composables/useCalendar'

defineEmits<{
  clickAppointment: [appt: Appointment]
}>()

const {
  weekDays,
  weekLabel,
  appointmentsByDay,
  loading,
  goToPrevWeek,
  goToNextWeek,
  goToToday,
  fetchWeekAppointments,
  getPosition,
} = useCalendar()

const shortDayNames = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb']

const hours = computed(() => {
  const h: number[] = []
  for (let i = START_HOUR; i <= END_HOUR; i++) h.push(i)
  return h
})

const gridHeight = (END_HOUR - START_HOUR) * HOUR_HEIGHT

const todayStr = computed(() => formatDateKey(new Date()))

function isToday(d: Date): boolean {
  return formatDateKey(d) === todayStr.value
}

// Mobile: 3 days centered on today (or first 3 of week)
const mobileDays = computed(() => {
  const todayKey = todayStr.value
  const idx = weekDays.value.findIndex(d => formatDateKey(d) === todayKey)
  if (idx >= 0) {
    const center = Math.max(1, Math.min(idx, 5))
    return weekDays.value.slice(center - 1, center + 2)
  }
  return weekDays.value.slice(0, 3)
})

// Current time red line
const nowLineTop = ref<number | null>(null)
let nowInterval: ReturnType<typeof setInterval> | null = null

function updateNowLine() {
  const now = new Date()
  const todayKey = formatDateKey(now)
  const isThisWeek = weekDays.value.some(d => formatDateKey(d) === todayKey)
  if (!isThisWeek) {
    nowLineTop.value = null
    return
  }
  const h = now.getHours()
  const m = now.getMinutes()
  if (h < START_HOUR || h > END_HOUR) {
    nowLineTop.value = null
    return
  }
  nowLineTop.value = ((h - START_HOUR) * 60 + m) / 60 * HOUR_HEIGHT
}

onMounted(() => {
  fetchWeekAppointments()
  updateNowLine()
  nowInterval = setInterval(updateNowLine, 60000)
})

onUnmounted(() => {
  if (nowInterval) clearInterval(nowInterval)
})

defineExpose({ refresh: fetchWeekAppointments })
</script>
