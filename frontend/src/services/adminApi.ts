import api from './api'

export interface DashboardStats {
  appointments_today: number
  revenue_today: number
  revenue_week: number
  revenue_month: number
  new_clients_month: number
  total_clients: number
}

export interface RevenueData {
  date: string
  revenue: number
  count: number
}

export interface Client {
  id: string
  name: string
  phone: string
  email: string | null
  notes: string | null
  created_at: string
}

export interface Appointment {
  id: string
  client_id: string
  barber_id: string
  service_id: string
  date: string
  start_time: string
  end_time: string
  status: string
  notes: string | null
  created_at: string
  updated_at?: string
  client: { id: string; name: string; phone: string; email: string | null }
  barber: { id: string; name: string }
  service: { id: string; name: string; price: number; duration_minutes: number }
}

export interface ScheduleEntry {
  id?: string
  barber_id?: string
  day_of_week: number
  start_time: string
  end_time: string
}

export interface BlockedSlot {
  id: string
  barber_id: string
  date: string
  start_time: string
  end_time: string
  reason: string | null
}

export const adminApi = {
  // Dashboard
  getStats(): Promise<DashboardStats> {
    return api.get('/admin/dashboard/stats').then((r) => r.data)
  },
  getRevenue(period: string = 'week'): Promise<RevenueData[]> {
    return api.get('/admin/dashboard/revenue', { params: { period } }).then((r) => r.data)
  },
  getAppointmentsToday(): Promise<Appointment[]> {
    return api.get('/admin/dashboard/appointments-today').then((r) => r.data)
  },

  // Appointments
  getAppointments(params?: Record<string, string>): Promise<Appointment[]> {
    return api.get('/admin/appointments/', { params }).then((r) => r.data)
  },
  getAppointment(id: string): Promise<Appointment> {
    return api.get(`/admin/appointments/${id}`).then((r) => r.data)
  },
  createAppointment(data: Record<string, unknown>): Promise<Appointment> {
    return api.post('/admin/appointments/', data).then((r) => r.data)
  },
  updateAppointment(id: string, data: Record<string, unknown>): Promise<Appointment> {
    return api.put(`/admin/appointments/${id}`, data).then((r) => r.data)
  },
  deleteAppointment(id: string): Promise<void> {
    return api.delete(`/admin/appointments/${id}`)
  },
  updateAppointmentStatus(id: string, status: string): Promise<Appointment> {
    return api.patch(`/admin/appointments/${id}/status`, { status }).then((r) => r.data)
  },

  // Services
  getServices() {
    return api.get('/admin/services/').then((r) => r.data)
  },
  createService(data: Record<string, unknown>) {
    return api.post('/admin/services/', data).then((r) => r.data)
  },
  updateService(id: string, data: Record<string, unknown>) {
    return api.put(`/admin/services/${id}`, data).then((r) => r.data)
  },
  deleteService(id: string) {
    return api.delete(`/admin/services/${id}`)
  },

  // Barbers
  getBarbers() {
    return api.get('/admin/barbers/').then((r) => r.data)
  },
  getBarber(id: string) {
    return api.get(`/admin/barbers/${id}`).then((r) => r.data)
  },
  createBarber(data: Record<string, unknown>) {
    return api.post('/admin/barbers/', data).then((r) => r.data)
  },
  updateBarber(id: string, data: Record<string, unknown>) {
    return api.put(`/admin/barbers/${id}`, data).then((r) => r.data)
  },
  deleteBarber(id: string) {
    return api.delete(`/admin/barbers/${id}`)
  },

  // Clients
  getClients(params?: Record<string, string | number>) {
    return api.get('/admin/clients/', { params }).then((r) => r.data)
  },
  getClient(id: string): Promise<Client> {
    return api.get(`/admin/clients/${id}`).then((r) => r.data)
  },
  updateClient(id: string, data: Record<string, unknown>) {
    return api.put(`/admin/clients/${id}`, data).then((r) => r.data)
  },
  getClientAppointments(id: string): Promise<Appointment[]> {
    return api.get(`/admin/clients/${id}/appointments`).then((r) => r.data)
  },

  // Schedules
  getBarberSchedule(barberId: string): Promise<ScheduleEntry[]> {
    return api.get(`/admin/barbers/${barberId}/schedule`).then((r) => r.data)
  },
  updateBarberSchedule(barberId: string, schedules: ScheduleEntry[]) {
    return api.put(`/admin/barbers/${barberId}/schedule`, { schedules }).then((r) => r.data)
  },

  // Blocked Slots
  getBlockedSlots(barberId?: string): Promise<BlockedSlot[]> {
    return api.get('/admin/blocked-slots', { params: barberId ? { barber_id: barberId } : {} }).then((r) => r.data)
  },
  createBlockedSlot(data: Record<string, unknown>): Promise<BlockedSlot> {
    return api.post('/admin/blocked-slots', data).then((r) => r.data)
  },
  deleteBlockedSlot(id: string) {
    return api.delete(`/admin/blocked-slots/${id}`)
  },
}
