import type { Appointment } from '@/services/adminApi'

// ─── Public booking (confirmation page) ───────────────────────────────────────

export interface PublicBookingData {
  serviceName: string
  barberName: string
  date: string       // "2026-02-23"
  startTime: string  // "10:00:00"
  endTime: string    // "11:00:00"
}

export function downloadPublicBookingICS(data: PublicBookingData): void {
  const dtStart = toICSDate(data.date, data.startTime)
  const dtEnd   = toICSDate(data.date, data.endTime)
  const content = [
    'BEGIN:VCALENDAR',
    'VERSION:2.0',
    'PRODID:-//Cellar Barber Studio//ES',
    'CALSCALE:GREGORIAN',
    'METHOD:PUBLISH',
    'BEGIN:VEVENT',
    `UID:booking-${data.date}-${data.startTime.replace(/:/g, '')}@cellarbarberstudio`,
    `DTSTART:${dtStart}`,
    `DTEND:${dtEnd}`,
    'SUMMARY:Cita en Cellar Barber Studio',
    `DESCRIPTION:Servicio: ${escapeICS(data.serviceName)}\\nBarbero: ${escapeICS(data.barberName)}`,
    'LOCATION:Cellar Barber Studio',
    'STATUS:TENTATIVE',
    'END:VEVENT',
    'END:VCALENDAR',
  ].join('\r\n')

  const blob = new Blob([content], { type: 'text/calendar;charset=utf-8' })
  const url  = URL.createObjectURL(blob)
  const a    = document.createElement('a')
  a.href     = url
  a.download = `cita-${data.date}.ics`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

export function getGoogleCalendarUrl(data: PublicBookingData): string {
  const dtStart = toICSDate(data.date, data.startTime)
  const dtEnd   = toICSDate(data.date, data.endTime)
  const params  = new URLSearchParams({
    action:   'TEMPLATE',
    text:     'Cita en Cellar Barber Studio',
    dates:    `${dtStart}/${dtEnd}`,
    details:  `Servicio: ${data.serviceName}\nBarbero: ${data.barberName}`,
    location: 'Cellar Barber Studio',
  })
  return `https://calendar.google.com/calendar/render?${params.toString()}`
}

function pad(n: number): string {
  return n.toString().padStart(2, '0')
}

function toICSDate(date: string, time: string): string {
  // date: "2026-02-08", time: "10:00:00" -> "20260208T100000"
  const d = date.replace(/-/g, '')
  const t = time.replace(/:/g, '').substring(0, 6)
  return `${d}T${t}`
}

function escapeICS(text: string): string {
  return text.replace(/\\/g, '\\\\').replace(/;/g, '\\;').replace(/,/g, '\\,').replace(/\n/g, '\\n')
}

function generateUID(appt: Appointment): string {
  return `${appt.id}@cellarstudio`
}

function appointmentToVEVENT(appt: Appointment): string {
  const dtStart = toICSDate(appt.date, appt.start_time)
  const dtEnd = toICSDate(appt.date, appt.end_time)
  const summary = `${appt.service.name} - ${appt.client.name}`
  const description = [
    `Cliente: ${appt.client.name}`,
    `Teléfono: ${appt.client.phone}`,
    appt.client.email ? `Email: ${appt.client.email}` : '',
    `Barbero: ${appt.barber.name}`,
    `Servicio: ${appt.service.name}`,
    `Precio: $${appt.service.price}`,
    `Estado: ${appt.status}`,
    appt.notes ? `Notas: ${appt.notes}` : '',
  ].filter(Boolean).join('\\n')

  return [
    'BEGIN:VEVENT',
    `UID:${generateUID(appt)}`,
    `DTSTART:${dtStart}`,
    `DTEND:${dtEnd}`,
    `SUMMARY:${escapeICS(summary)}`,
    `DESCRIPTION:${escapeICS(description)}`,
    'LOCATION:Cellar Barber Studio',
    `STATUS:${appt.status === 'confirmed' ? 'CONFIRMED' : appt.status === 'cancelled' ? 'CANCELLED' : 'TENTATIVE'}`,
    'END:VEVENT',
  ].join('\r\n')
}

function generateICSContent(appointments: Appointment[]): string {
  const events = appointments.map(appointmentToVEVENT).join('\r\n')
  return [
    'BEGIN:VCALENDAR',
    'VERSION:2.0',
    'PRODID:-//Cellar Barber Studio//Barbería//ES',
    'CALSCALE:GREGORIAN',
    'METHOD:PUBLISH',
    'X-WR-CALNAME:Cellar Barber Studio Citas',
    events,
    'END:VCALENDAR',
  ].join('\r\n')
}

export function downloadICS(appointments: Appointment[], filename?: string): void {
  const content = generateICSContent(appointments)
  const blob = new Blob([content], { type: 'text/calendar;charset=utf-8' })
  const url = URL.createObjectURL(blob)

  const a = document.createElement('a')
  a.href = url
  a.download = filename || 'cellarstudio-citas.ics'
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

export function downloadSingleICS(appt: Appointment): void {
  const dateStr = appt.date.replace(/-/g, '')
  const clientName = appt.client.name.replace(/\s+/g, '-').toLowerCase()
  downloadICS([appt], `cita-${clientName}-${dateStr}.ics`)
}
