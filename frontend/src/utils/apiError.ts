/** Human-readable message out of an Axios error from the FastAPI backend. */
export function errorMessage(err: unknown, fallback: string): string {
  const detail = (err as { response?: { data?: { detail?: unknown } } })?.response?.data?.detail

  if (typeof detail === 'string') return detail

  // Structured 409s (e.g. the hidden-client conflict) carry a `message`.
  if (detail && typeof detail === 'object' && !Array.isArray(detail)) {
    const message = (detail as { message?: unknown }).message
    if (typeof message === 'string') return message
  }

  // FastAPI 422: detail is a list of validation errors. Name the offending
  // field, otherwise the user sees a bare "Value error, ..." with no context.
  if (Array.isArray(detail) && detail.length > 0) {
    const first = detail[0] as { msg?: string; loc?: unknown[] }
    if (typeof first?.msg === 'string') {
      const field = Array.isArray(first.loc) ? first.loc[first.loc.length - 1] : undefined
      const label = typeof field === 'string' ? FIELD_LABELS[field] || field : ''
      const msg = first.msg.replace(/^Value error,\s*/, '')
      return label ? `${label}: ${msg}` : msg
    }
  }

  return fallback
}

/** Detail code of a structured error response, if any. */
export function errorCode(err: unknown): string | null {
  const detail = (err as { response?: { data?: { detail?: unknown } } })?.response?.data?.detail
  if (detail && typeof detail === 'object' && !Array.isArray(detail)) {
    const code = (detail as { code?: unknown }).code
    if (typeof code === 'string') return code
  }
  return null
}

const FIELD_LABELS: Record<string, string> = {
  name: 'Nombre',
  phone: 'Teléfono',
  email: 'Email',
  notes: 'Notas',
  client_name: 'Nombre',
  client_phone: 'Teléfono',
  client_email: 'Email',
}
