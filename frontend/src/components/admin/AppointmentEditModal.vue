<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center p-4" @click.self="$emit('close')">
    <div class="absolute inset-0 bg-black/40"></div>
    <div class="relative bg-white rounded-2xl shadow-xl w-full max-w-md max-h-[90vh] overflow-y-auto">
      <!-- Header -->
      <div class="flex items-center justify-between p-4 border-b border-gray-200">
        <h2 class="text-lg font-bold text-[#1d1d1f]">Editar cita</h2>
        <button @click="$emit('close')" class="p-1.5 rounded-lg hover:bg-gray-100 transition-colors">
          <svg class="w-5 h-5 text-dark-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </button>
      </div>

      <div class="p-4 space-y-4">
        <!-- Client (read-only) -->
        <div>
          <label class="block text-xs text-dark-400 mb-1">Cliente</label>
          <p class="px-3 py-2 bg-[#f5f5f7] rounded-lg text-sm text-[#1d1d1f]">
            {{ appointment.client.name }} · {{ appointment.client.phone }}
          </p>
        </div>

        <!-- Date -->
        <div>
          <label class="block text-xs text-dark-400 mb-1">Fecha</label>
          <input
            v-model="form.date"
            type="date"
            class="w-full px-3 py-2 bg-white border border-gray-200 rounded-lg text-sm text-[#1d1d1f] focus:border-brand-400 focus:outline-none"
          />
        </div>

        <!-- Time -->
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-xs text-dark-400 mb-1">Hora inicio</label>
            <input
              v-model="form.start_time"
              type="time"
              step="900"
              class="w-full px-3 py-2 bg-white border border-gray-200 rounded-lg text-sm text-[#1d1d1f] focus:border-brand-400 focus:outline-none"
            />
          </div>
          <div>
            <label class="block text-xs text-dark-400 mb-1">Hora fin</label>
            <input
              v-model="form.end_time"
              type="time"
              step="900"
              class="w-full px-3 py-2 bg-white border border-gray-200 rounded-lg text-sm text-[#1d1d1f] focus:border-brand-400 focus:outline-none"
            />
          </div>
        </div>

        <!-- Service -->
        <div>
          <label class="block text-xs text-dark-400 mb-1">Servicio</label>
          <select
            v-model="form.service_id"
            class="w-full px-3 py-2 bg-white border border-gray-200 rounded-lg text-sm text-[#1d1d1f] focus:border-brand-400 focus:outline-none"
          >
            <option v-for="s in services" :key="s.id" :value="s.id">{{ s.name }} (${{ s.price }})</option>
          </select>
        </div>

        <!-- Barber -->
        <div>
          <label class="block text-xs text-dark-400 mb-1">Barbero</label>
          <select
            v-model="form.barber_id"
            class="w-full px-3 py-2 bg-white border border-gray-200 rounded-lg text-sm text-[#1d1d1f] focus:border-brand-400 focus:outline-none"
          >
            <option v-for="b in barbers" :key="b.id" :value="b.id">{{ b.name }}</option>
          </select>
        </div>

        <!-- Status -->
        <div>
          <label class="block text-xs text-dark-400 mb-1">Estado</label>
          <select
            v-model="form.status"
            class="w-full px-3 py-2 bg-white border border-gray-200 rounded-lg text-sm text-[#1d1d1f] focus:border-brand-400 focus:outline-none"
          >
            <option value="pending">Pendiente</option>
            <option value="confirmed">Confirmada</option>
            <option value="completed">Completada</option>
            <option value="cancelled">Cancelada</option>
            <option value="noshow">No asistió</option>
          </select>
        </div>

        <!-- Notes -->
        <div>
          <label class="block text-xs text-dark-400 mb-1">Notas</label>
          <textarea
            v-model="form.notes"
            rows="2"
            placeholder="Notas opcionales..."
            class="w-full px-3 py-2 bg-white border border-gray-200 rounded-lg text-sm text-[#1d1d1f] focus:border-brand-400 focus:outline-none resize-none"
          ></textarea>
        </div>
      </div>

      <!-- Actions -->
      <div class="flex items-center justify-between p-4 border-t border-gray-200">
        <button
          @click="handleDelete"
          class="flex items-center gap-1.5 px-3 py-2 text-sm font-medium text-red-400 hover:bg-red-500/10 rounded-lg transition-colors"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
          </svg>
          Eliminar
        </button>
        <div class="flex items-center gap-2">
          <button
            @click="$emit('close')"
            class="px-4 py-2 text-sm font-medium text-dark-400 hover:bg-gray-100 rounded-lg transition-colors"
          >
            Cancelar
          </button>
          <button
            @click="handleSave"
            :disabled="saving"
            class="px-4 py-2 text-sm font-medium text-white bg-brand-500 hover:bg-brand-600 rounded-lg transition-colors disabled:opacity-50"
          >
            {{ saving ? 'Guardando...' : 'Guardar' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { adminApi, type Appointment } from '@/services/adminApi'

const props = defineProps<{
  appointment: Appointment
}>()

const emit = defineEmits<{
  close: []
  saved: []
  deleted: []
}>()

const saving = ref(false)
const services = ref<{ id: string; name: string; price: number }[]>([])
const barbers = ref<{ id: string; name: string }[]>([])

const form = reactive({
  date: props.appointment.date,
  start_time: props.appointment.start_time.substring(0, 5),
  end_time: props.appointment.end_time.substring(0, 5),
  service_id: props.appointment.service_id,
  barber_id: props.appointment.barber_id,
  status: props.appointment.status,
  notes: props.appointment.notes || '',
})

async function handleSave() {
  saving.value = true
  try {
    const payload: Record<string, unknown> = {}
    if (form.date !== props.appointment.date) payload.date = form.date
    if (form.start_time !== props.appointment.start_time.substring(0, 5)) payload.start_time = form.start_time + ':00'
    if (form.end_time !== props.appointment.end_time.substring(0, 5)) payload.end_time = form.end_time + ':00'
    if (form.service_id !== props.appointment.service_id) payload.service_id = form.service_id
    if (form.barber_id !== props.appointment.barber_id) payload.barber_id = form.barber_id
    if (form.status !== props.appointment.status) payload.status = form.status
    if (form.notes !== (props.appointment.notes || '')) payload.notes = form.notes || null

    if (Object.keys(payload).length > 0) {
      await adminApi.updateAppointment(props.appointment.id, payload)
    }
    emit('saved')
  } finally {
    saving.value = false
  }
}

async function handleDelete() {
  if (!confirm('¿Eliminar esta cita?')) return
  await adminApi.deleteAppointment(props.appointment.id)
  emit('deleted')
}

onMounted(async () => {
  const [s, b] = await Promise.all([adminApi.getServices(), adminApi.getBarbers()])
  services.value = s
  barbers.value = b
})
</script>
