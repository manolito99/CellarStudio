<template>
  <div>
    <h1 class="text-2xl font-bold text-[#2B2E2E] mb-6">Horarios y disponibilidad</h1>

    <!-- Barber selector -->
    <div class="mb-6">
      <label class="block text-sm text-dark-300 mb-2">Barbero</label>
      <select
        v-model="selectedBarberId"
        @change="loadSchedule"
        class="px-3 py-2 bg-white border border-gray-200 rounded-lg text-[#2B2E2E] focus:border-brand-400 focus:outline-none"
      >
        <option value="">Seleccionar barbero</option>
        <option v-for="b in barbers" :key="b.id" :value="b.id">{{ b.name }}</option>
      </select>
    </div>

    <div v-if="selectedBarberId" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Weekly Schedule -->
      <div class="bg-white border border-gray-200 rounded-xl p-6">
        <h2 class="text-lg font-bold text-[#2B2E2E] mb-4">Horario semanal</h2>
        <div class="space-y-3">
          <div v-for="(day, index) in dayNames" :key="index" class="flex items-center gap-3">
            <span class="w-24 text-sm text-dark-300">{{ day }}</span>
            <label class="flex items-center gap-2">
              <input
                type="checkbox"
                :checked="scheduleMap[index]?.enabled"
                @change="toggleDay(index)"
                class="rounded border-gray-300 text-brand-500"
              />
            </label>
            <template v-if="scheduleMap[index]?.enabled">
              <input
                type="time"
                :value="scheduleMap[index]?.start"
                @change="updateTime(index, 'start', ($event.target as HTMLInputElement).value)"
                class="px-2 py-1 bg-[#F2F0E9] border border-gray-200 rounded text-sm text-[#2B2E2E] focus:border-brand-400 focus:outline-none"
              />
              <span class="text-dark-500">-</span>
              <input
                type="time"
                :value="scheduleMap[index]?.end"
                @change="updateTime(index, 'end', ($event.target as HTMLInputElement).value)"
                class="px-2 py-1 bg-[#F2F0E9] border border-gray-200 rounded text-sm text-[#2B2E2E] focus:border-brand-400 focus:outline-none"
              />
            </template>
            <span v-else class="text-dark-500 text-sm">Cerrado</span>
          </div>
        </div>
        <button
          @click="saveSchedule"
          class="mt-4 px-4 py-2 bg-brand-500 hover:bg-brand-600 text-white text-sm font-medium rounded-lg transition-colors"
        >
          Guardar horario
        </button>
      </div>

      <!-- Blocked Slots -->
      <div class="bg-white border border-gray-200 rounded-xl p-6">
        <h2 class="text-lg font-bold text-[#2B2E2E] mb-4">Bloqueos</h2>

        <form @submit.prevent="addBlock" class="mb-4 space-y-3">
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs text-dark-400 mb-1">Fecha</label>
              <input v-model="blockForm.date" type="date" required class="w-full px-2 py-1.5 bg-[#F2F0E9] border border-gray-200 rounded text-sm text-[#2B2E2E] focus:border-brand-400 focus:outline-none" />
            </div>
            <div>
              <label class="block text-xs text-dark-400 mb-1">Motivo</label>
              <input v-model="blockForm.reason" placeholder="Ej: Vacaciones" class="w-full px-2 py-1.5 bg-[#F2F0E9] border border-gray-200 rounded text-sm text-[#2B2E2E] focus:border-brand-400 focus:outline-none" />
            </div>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs text-dark-400 mb-1">Desde</label>
              <input v-model="blockForm.start_time" type="time" required class="w-full px-2 py-1.5 bg-[#F2F0E9] border border-gray-200 rounded text-sm text-[#2B2E2E] focus:border-brand-400 focus:outline-none" />
            </div>
            <div>
              <label class="block text-xs text-dark-400 mb-1">Hasta</label>
              <input v-model="blockForm.end_time" type="time" required class="w-full px-2 py-1.5 bg-[#F2F0E9] border border-gray-200 rounded text-sm text-[#2B2E2E] focus:border-brand-400 focus:outline-none" />
            </div>
          </div>
          <button type="submit" class="w-full px-3 py-2 bg-red-500/10 hover:bg-red-500/20 text-red-400 text-sm font-medium rounded-lg transition-colors border border-red-500/20">
            + Agregar bloqueo
          </button>
        </form>

        <div class="space-y-2">
          <div
            v-for="block in blockedSlots"
            :key="block.id"
            class="flex items-center justify-between p-3 bg-[#F2F0E9] rounded-lg"
          >
            <div>
              <p class="text-[#2B2E2E] text-sm font-medium">{{ formatDate(block.date) }}</p>
              <p class="text-dark-400 text-xs">{{ block.start_time.substring(0, 5) }} - {{ block.end_time.substring(0, 5) }} {{ block.reason ? `(${block.reason})` : '' }}</p>
            </div>
            <button
              @click="removeBlock(block.id)"
              class="p-1 text-dark-500 hover:text-red-400 transition-colors"
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
import { adminApi, type Barber, type ScheduleEntry, type BlockedSlot } from '@/services/adminApi'

const dayNames = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
const barbers = ref<Barber[]>([])
const selectedBarberId = ref('')
const blockedSlots = ref<BlockedSlot[]>([])

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
})

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
  alert('Horario guardado')
}

async function addBlock() {
  await adminApi.createBlockedSlot({
    barber_id: selectedBarberId.value,
    date: blockForm.date,
    start_time: blockForm.start_time + ':00',
    end_time: blockForm.end_time + ':00',
    reason: blockForm.reason || null,
  })
  blockForm.date = ''
  blockForm.reason = ''
  blockedSlots.value = await adminApi.getBlockedSlots(selectedBarberId.value)
}

async function removeBlock(id: string) {
  await adminApi.deleteBlockedSlot(id)
  blockedSlots.value = await adminApi.getBlockedSlots(selectedBarberId.value)
}

function formatDate(d: string): string {
  return new Date(d + 'T12:00:00').toLocaleDateString('es-AR', { weekday: 'short', day: '2-digit', month: '2-digit' })
}

onMounted(async () => {
  barbers.value = await adminApi.getBarbers()
  initScheduleMap()
})
</script>
