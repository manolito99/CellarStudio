import type { Appointment } from '@/services/adminApi'

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
    'LOCATION:Cellar Studio',
    `STATUS:${appt.status === 'confirmed' ? 'CONFIRMED' : appt.status === 'cancelled' ? 'CANCELLED' : 'TENTATIVE'}`,
    'END:VEVENT',
  ].join('\r\n')
}

function generateICSContent(appointments: Appointment[]): string {
  const events = appointments.map(appointmentToVEVENT).join('\r\n')
  return [
    'BEGIN:VCALENDAR',
    'VERSION:2.0',
    'PRODID:-//Cellar Studio//Barbería//ES',
    'CALSCALE:GREGORIAN',
    'METHOD:PUBLISH',
    'X-WR-CALNAME:Cellar Studio Citas',
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
