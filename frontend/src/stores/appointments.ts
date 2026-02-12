import { defineStore } from 'pinia'
import { ref } from 'vue'
import { adminApi, type Appointment } from '@/services/adminApi'

export const useAppointmentsStore = defineStore('appointments', () => {
  const appointments = ref<Appointment[]>([])
  const loading = ref(false)

  async function fetchAppointments(params?: Record<string, string>) {
    loading.value = true
    try {
      appointments.value = await adminApi.getAppointments(params)
    } finally {
      loading.value = false
    }
  }

  async function updateStatus(id: string, status: string) {
    const updated = await adminApi.updateAppointmentStatus(id, status)
    const index = appointments.value.findIndex((a) => a.id === id)
    if (index !== -1) {
      appointments.value[index] = updated
    }
  }

  return { appointments, loading, fetchAppointments, updateStatus }
})
