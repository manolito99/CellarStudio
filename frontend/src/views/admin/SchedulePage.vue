<template>
  <div>
    <h1 class="text-xl sm:text-2xl font-bold text-[#1d1d1f] mb-6">Horarios y disponibilidad</h1>

    <!-- Barber selector -->
    <div class="mb-6">
      <label class="block text-sm text-dark-300 mb-2">Barbero</label>
      <select
        v-model="selectedBarberId"
        @change="loadSchedule"
        class="px-3 py-2 bg-white border border-gray-200 rounded-lg text-[#1d1d1f] focus:border-brand-400 focus:outline-none"
      >
        <option value="">Seleccionar barbero</option>
        <option v-for="b in barbers" :key="b.id" :value="b.id">{{ b.name }}</option>
      </select>
    </div>

    <div v-if="selectedBarberId" class="space-y-6">
      <!-- Weekly Schedule -->
      <div class="bg-white border border-gray-200 rounded-xl p-4 sm:p-6">
        <h2 class="text-lg font-bold text-[#1d1d1f] mb-4">Horario semanal</h2>

        <div class="space-y-2">
          <div
            v-for="(day, index) in dayNames"
            :key="index"
            class="flex items-center gap-3 p-2 rounded-lg transition-colors"
            :class="scheduleMap[index]?.enabled ? 'bg-white' : 'bg-[#f5f5f7]'"
          >
            <!-- Toggle -->
            <button
              @click="toggleDay(index)"
              class="relative w-10 h-6 rounded-full transition-colors flex-shrink-0"
              :class="scheduleMap[index]?.enabled ? 'bg-brand-500' : 'bg-gray-300'"
            >
              <span
                class="absolute left-0 top-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform"
                :class="scheduleMap[index]?.enabled ? 'translate-x-[18px]' : 'translate-x-0.5'"
              ></span>
            </button>

            <!-- Day name -->
            <span class="w-20 text-sm font-medium" :class="scheduleMap[index]?.enabled ? 'text-[#1d1d1f]' : 'text-dark-400'">
              {{ day }}
            </span>

            <template v-if="scheduleMap[index]?.enabled">
              <!-- Time inputs -->
              <input
                type="time"
                :value="scheduleMap[index]?.start"
                @change="updateTime(index, 'start', ($event.target as HTMLInputElement).value)"
                class="px-2 py-1 bg-[#f5f5f7] border border-gray-200 rounded text-sm text-[#1d1d1f] focus:border-brand-400 focus:outline-none"
              />
              <span class="text-dark-500 text-sm">—</span>
              <input
                type="time"
                :value="scheduleMap[index]?.end"
                @change="updateTime(index, 'end', ($event.target as HTMLInputElement).value)"
                class="px-2 py-1 bg-[#f5f5f7] border border-gray-200 rounded text-sm text-[#1d1d1f] focus:border-brand-400 focus:outline-none"
              />

              <!-- Visual bar (desktop) -->
              <div class="hidden lg:block flex-1 relative h-6 bg-[#f5f5f7] rounded-full overflow-hidden ml-2">
                <!-- Timeline ticks 6am-10pm -->
                <div
                  v-for="h in timelineTicks"
                  :key="h"
                  class="absolute top-0 bottom-0 w-px bg-gray-200"
                  :style="{ left: tickPosition(h) }"
                ></div>
                <!-- Active range bar -->
                <div
                  class="absolute top-0.5 bottom-0.5 bg-brand-500/20 border border-brand-500/40 rounded-full"
                  :style="barStyle(index)"
                ></div>
              </div>
            </template>
            <span v-else class="text-dark-400 text-sm italic">Cerrado</span>
          </div>
        </div>

        <div class="flex items-center gap-3 mt-5">
          <button
            @click="saveSchedule"
            :disabled="saving"
            class="px-4 py-2 bg-brand-500 hover:bg-brand-600 text-white text-sm font-medium rounded-lg transition-colors disabled:opacity-50"
          >
            {{ saving ? 'Guardando...' : 'Guardar horario' }}
          </button>
          <span v-if="saveMsg" class="text-sm text-green-500 font-medium">{{ saveMsg }}</span>
        </div>
      </div>

      <!-- Blocked Slots -->
      <div class="bg-white border border-gray-200 rounded-xl p-4 sm:p-6">
        <h2 class="text-lg font-bold text-[#1d1d1f] mb-4">Bloqueos</h2>

        <form @submit.prevent="addBlock" class="mb-4 space-y-3">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label class="block text-xs text-dark-400 mb-1">Fecha</label>
              <input v-model="blockForm.date" type="date" required class="w-full px-2 py-1.5 bg-[#f5f5f7] border border-gray-200 rounded text-sm text-[#1d1d1f] focus:border-brand-400 focus:outline-none" />
            </div>
            <div>
              <label class="block text-xs text-dark-400 mb-1">Motivo</label>
              <input v-model="blockForm.reason" placeholder="Ej: Vacaciones" class="w-full px-2 py-1.5 bg-[#f5f5f7] border border-gray-200 rounded text-sm text-[#1d1d1f] focus:border-brand-400 focus:outline-none" />
            </div>
          </div>

          <!-- All day toggle -->
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              v-model="blockForm.allDay"
              class="rounded border-gray-300 text-brand-500"
            />
            <span class="text-sm text-dark-400">Todo el día</span>
          </label>

          <div v-if="!blockForm.allDay" class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs text-dark-400 mb-1">Desde</label>
              <input v-model="blockForm.start_time" type="time" required class="w-full px-2 py-1.5 bg-[#f5f5f7] border border-gray-200 rounded text-sm text-[#1d1d1f] focus:border-brand-400 focus:outline-none" />
            </div>
            <div>
              <label class="block text-xs text-dark-400 mb-1">Hasta</label>
              <input v-model="blockForm.end_time" type="time" required class="w-full px-2 py-1.5 bg-[#f5f5f7] border border-gray-200 rounded text-sm text-[#1d1d1f] focus:border-brand-400 focus:outline-none" />
            </div>
          </div>

          <button type="submit" class="w-full sm:w-auto px-4 py-2 bg-red-500/10 hover:bg-red-500/20 text-red-400 text-sm font-medium rounded-lg transition-colors border border-red-500/20">
            + Agregar bloqueo
          </button>
        </form>

        <div class="space-y-2">
          <div
            v-for="block in blockedSlots"
            :key="block.id"
            class="flex items-center justify-between p-3 bg-[#f5f5f7] rounded-lg"
          >
            <div>
              <p class="text-[#1d1d1f] text-sm font-medium">{{ formatDate(block.date) }}</p>
              <p class="text-dark-400 text-xs">
                {{ isAllDay(block) ? 'Todo el día' : block.start_time.substring(0, 5) + ' - ' + block.end_time.substring(0, 5) }}
                {{ block.reason ? `(${block.reason})` : '' }}
              </p>
            </div>
            <button
              @click="removeBlock(block.id)"
              class="p-1.5 text-dark-500 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-colors"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
            </button>
          </div>
          <p v-if="blockedSlots.length === 0" class="text-dark-500 text-sm text-center py-4">
            Sin bloqueos configurados
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { adminApi, type ScheduleEntry, type BlockedSlot } from '@/services/adminApi'

const dayNames = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
const barbers = ref<{ id: string; name: string }[]>([])
const selectedBarberId = ref('')
const blockedSlots = ref<BlockedSlot[]>([])
const saving = ref(false)
const saveMsg = ref('')

interface DaySchedule {
  enabled: boolean
  start: string
  end: string
}

const scheduleMap = ref<Record<number, DaySchedule>>({})

const blockForm = reactive({
  date: '',
  start_time: '09:00',
  end_time: '20:00',
  reason: '',
  allDay: false,
})

// Visual timeline: 6am to 10pm (16h range)
const TIMELINE_START = 6
const TIMELINE_END = 22
const TIMELINE_RANGE = TIMELINE_END - TIMELINE_START

const timelineTicks = [6, 8, 10, 12, 14, 16, 18, 20, 22]

function tickPosition(h: number): string {
  return ((h - TIMELINE_START) / TIMELINE_RANGE * 100) + '%'
}

function barStyle(dayIndex: number) {
  const day = scheduleMap.value[dayIndex]
  if (!day?.enabled) return { left: '0%', width: '0%' }
  const [sh, sm] = day.start.split(':').map(Number)
  const [eh, em] = day.end.split(':').map(Number)
  const startH = sh + sm / 60
  const endH = eh + em / 60
  const left = ((startH - TIMELINE_START) / TIMELINE_RANGE * 100)
  const width = ((endH - startH) / TIMELINE_RANGE * 100)
  return {
    left: Math.max(0, left) + '%',
    width: Math.min(100 - Math.max(0, left), Math.max(0, width)) + '%',
  }
}

function initScheduleMap() {
  for (let i = 0; i < 7; i++) {
    scheduleMap.value[i] = { enabled: false, start: '09:00', end: '20:00' }
  }
}

async function loadSchedule() {
  if (!selectedBarberId.value) return
  initScheduleMap()

  const [entries, blocks] = await Promise.all([
    adminApi.getBarberSchedule(selectedBarberId.value),
    adminApi.getBlockedSlots(selectedBarberId.value),
  ])

  for (const entry of entries) {
    scheduleMap.value[entry.day_of_week] = {
      enabled: true,
      start: entry.start_time.substring(0, 5),
      end: entry.end_time.substring(0, 5),
    }
  }

  blockedSlots.value = blocks
}

function toggleDay(day: number) {
  scheduleMap.value[day].enabled = !scheduleMap.value[day].enabled
}

function updateTime(day: number, field: 'start' | 'end', value: string) {
  scheduleMap.value[day][field] = value
}

async function saveSchedule() {
  saving.value = true
  saveMsg.value = ''
  try {
    const schedules: ScheduleEntry[] = []
    for (let i = 0; i < 7; i++) {
      const day = scheduleMap.value[i]
      if (day.enabled) {
        schedules.push({
          day_of_week: i,
          start_time: day.start + ':00',
          end_time: day.end + ':00',
        })
      }
    }
    await adminApi.updateBarberSchedule(selectedBarberId.value, schedules)
    saveMsg.value = 'Guardado \u2713'
    setTimeout(() => { saveMsg.value = '' }, 2000)
  } finally {
    saving.value = false
  }
}

function isAllDay(block: BlockedSlot): boolean {
  return block.start_time.substring(0, 5) === '00:00' && block.end_time.substring(0, 5) === '23:59'
}

async function addBlock() {
  const startTime = blockForm.allDay ? '00:00' : blockForm.start_time
  const endTime = blockForm.allDay ? '23:59' : blockForm.end_time
  await adminApi.createBlockedSlot({
    barber_id: selectedBarberId.value,
    date: blockForm.date,
    start_time: startTime + ':00',
    end_time: endTime + ':00',
    reason: blockForm.reason || null,
  })
  blockForm.date = ''
  blockForm.reason = ''
  blockForm.allDay = false
  blockedSlots.value = await adminApi.getBlockedSlots(selectedBarberId.value)
}

async function removeBlock(id: string) {
  await adminApi.deleteBlockedSlot(id)
  blockedSlots.value = await adminApi.getBlockedSlots(selectedBarberId.value)
}

function formatDate(d: string): string {
  return new Date(d + 'T12:00:00').toLocaleDateString('es-ES', { weekday: 'short', day: '2-digit', month: '2-digit' })
}

onMounted(async () => {
  barbers.value = await adminApi.getBarbers()
  initScheduleMap()
})
</script>
