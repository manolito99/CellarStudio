import api from './api'

export interface Service {
  id: string
  name: string
  description: string | null
  price: number
  duration_minutes: number
  image_url: string | null
  is_active: boolean
  sort_order: number
  created_at: string
}

export interface Barber {
  id: string
  name: string
  photo_url: string | null
  bio: string | null
  is_active: boolean
  sort_order: number
  services: Service[]
  created_at: string
}

export interface TimeSlot {
  start_time: string
  end_time: string
  available: boolean
}

export interface AvailabilityResponse {
  barber_id: string
  date: string
  slots: TimeSlot[]
}

export interface AvailableDateInfo {
  date: string        // "2026-03-15"
  first_slot: string  // "09:00"
  slots_count: number
}

export interface AppointmentCreate {
  client_name: string
  client_phone: string
  client_email?: string
  barber_id: string
  service_id: string
  date: string
  start_time: string
  notes?: string
}

export interface MyAppointmentClient {
  id: string
  name: string
  phone: string
  email: string | null
}

export interface MyAppointment {
  id: string
  date: string
  start_time: string
  end_time: string
  status: string
  service: Service
  barber: Barber
  client: MyAppointmentClient
}

export const publicApi = {
  getServices(): Promise<Service[]> {
    return api.get('/public/services').then((r) => r.data)
  },

  getBarbers(): Promise<Barber[]> {
    return api.get('/public/barbers').then((r) => r.data)
  },

  getAvailability(barberId: string, date: string, serviceId: string): Promise<AvailabilityResponse> {
    return api.get('/public/availability', {
      params: { barber_id: barberId, date, service_id: serviceId },
    }).then((r) => r.data)
  },

  createAppointment(data: AppointmentCreate) {
    return api.post('/public/appointments', data).then((r) => r.data)
  },

  getAvailableDates(barberId: string, serviceId: string, from: string, to: string): Promise<AvailableDateInfo[]> {
    return api.get('/public/availability/dates', {
      params: { barber_id: barberId, service_id: serviceId, from, to },
    }).then((r) => r.data)
  },

  lookupMyAppointments(phone: string, email: string): Promise<MyAppointment[]> {
    return api.post('/public/my-appointments/lookup', { phone, email }).then((r) => r.data)
  },

  cancelMyAppointment(appointmentId: string, phone: string, email: string): Promise<MyAppointment> {
    return api.patch(`/public/my-appointments/${appointmentId}/cancel`, { phone, email }).then((r) => r.data)
  },

  modifyMyAppointment(
    appointmentId: string,
    phone: string,
    email: string,
    serviceId: string,
    barberId: string,
    date: string,
    startTime: string,
  ): Promise<MyAppointment> {
    return api.put(`/public/my-appointments/${appointmentId}/modify`, {
      phone,
      email,
      service_id: serviceId,
      barber_id: barberId,
      date,
      start_time: startTime,
    }).then((r) => r.data)
  },
}
