import { ref, computed } from 'vue'
import { adminApi, type Appointment } from '@/services/adminApi'

export const HOUR_HEIGHT = 60
export const START_HOUR = 7
export const END_HOUR = 21

function getMonday(date: Date): Date {
  const d = new Date(date)
  const day = d.getDay()
  const diff = d.getDate() - day + (day === 0 ? -6 : 1)
  d.setDate(diff)
  d.setHours(0, 0, 0, 0)
  return d
}

export function formatDateKey(d: Date): string {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

export function useCalendar() {
  const currentWeekStart = ref(getMonday(new Date()))
  const appointments = ref<Appointment[]>([])
  const loading = ref(false)

  const weekDays = computed(() => {
    const days: Date[] = []
    for (let i = 0; i < 7; i++) {
      const d = new Date(currentWeekStart.value)
      d.setDate(d.getDate() + i)
      days.push(d)
    }
    return days
  })

  const weekLabel = computed(() => {
    const start = weekDays.value[0]
    const end = weekDays.value[6]
    const opts: Intl.DateTimeFormatOptions = { day: 'numeric', month: 'short' }
    return `${start.toLocaleDateString('es-AR', opts)} — ${end.toLocaleDateString('es-AR', opts)}, ${end.getFullYear()}`
  })

  const appointmentsByDay = computed(() => {
    const map: Record<string, Appointment[]> = {}
    for (const day of weekDays.value) {
      map[formatDateKey(day)] = []
    }
    for (const appt of appointments.value) {
      const key = appt.date
      if (map[key]) {
        map[key].push(appt)
      }
    }
    return map
  })

  function goToPrevWeek() {
    const d = new Date(currentWeekStart.value)
    d.setDate(d.getDate() - 7)
    currentWeekStart.value = d
    fetchWeekAppointments()
  }

  function goToNextWeek() {
    const d = new Date(currentWeekStart.value)
    d.setDate(d.getDate() + 7)
    currentWeekStart.value = d
    fetchWeekAppointments()
  }

  function goToToday() {
    currentWeekStart.value = getMonday(new Date())
    fetchWeekAppointments()
  }

  async function fetchWeekAppointments() {
    loading.value = true
    try {
      const dateFrom = formatDateKey(weekDays.value[0])
      const dateTo = formatDateKey(weekDays.value[6])
      appointments.value = await adminApi.getAppointments({
        date_from: dateFrom,
        date_to: dateTo,
      })
    } finally {
      loading.value = false
    }
  }

  function getPosition(appt: Appointment) {
    const [sh, sm] = appt.start_time.split(':').map(Number)
    const [eh, em] = appt.end_time.split(':').map(Number)
    const startMinutes = (sh - START_HOUR) * 60 + sm
    const endMinutes = (eh - START_HOUR) * 60 + em
    const top = (startMinutes / 60) * HOUR_HEIGHT
    const height = Math.max(((endMinutes - startMinutes) / 60) * HOUR_HEIGHT, 20)
    return { top: `${top}px`, height: `${height}px` }
  }

  return {
    currentWeekStart,
    weekDays,
    weekLabel,
    appointments,
    appointmentsByDay,
    loading,
    goToPrevWeek,
    goToNextWeek,
    goToToday,
    fetchWeekAppointments,
    getPosition,
  }
}
