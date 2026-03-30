/**
 * Persists client profile (name, phone, email) in localStorage so booking
 * forms and the "Mis reservas" lookup are pre-filled on subsequent visits.
 */

const STORAGE_KEY = 'cellar_client_profile'

export interface ClientProfile {
  name: string
  phone: string
  email: string
}

export function useClientProfile() {
  function load(): ClientProfile | null {
    try {
      const raw = localStorage.getItem(STORAGE_KEY)
      if (!raw) return null
      const parsed = JSON.parse(raw) as Partial<ClientProfile>
      if (!parsed.phone) return null // phone is the minimum required field
      return {
        name: parsed.name ?? '',
        phone: parsed.phone ?? '',
        email: parsed.email ?? '',
      }
    } catch {
      return null
    }
  }

  function save(profile: ClientProfile) {
    try {
      // Only persist if at least phone is filled
      if (!profile.phone.trim()) return
      localStorage.setItem(STORAGE_KEY, JSON.stringify({
        name: profile.name.trim(),
        phone: profile.phone.trim(),
        email: profile.email.trim(),
      }))
    } catch {
      // Silently ignore (e.g. private browsing with storage disabled)
    }
  }

  function clear() {
    try {
      localStorage.removeItem(STORAGE_KEY)
    } catch {
      // ignore
    }
  }

  function hasSaved(): boolean {
    return load() !== null
  }

  return { load, save, clear, hasSaved }
}
