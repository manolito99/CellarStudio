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
}
