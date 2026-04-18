import type { IntakeProfile, IntakeResponse, RoutingResult } from './types'

const BASE = (import.meta.env.VITE_API_BASE as string | undefined) ?? ''

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  })

  if (!res.ok) {
    const detail = await res.json().catch(() => ({ detail: res.statusText }))
    const err = new Error((detail as { detail?: string }).detail ?? 'Request failed')
    ;(err as Error & { status: number }).status = res.status
    throw err
  }

  return res.json() as Promise<T>
}

export async function submitIntake(profile: IntakeProfile): Promise<IntakeResponse> {
  return request<IntakeResponse>('/api/intake', {
    method: 'POST',
    body: JSON.stringify(profile),
  })
}

/** Returns null when the backend responds 202 (still processing). */
export async function fetchResults(sessionId: string): Promise<RoutingResult | null> {
  const res = await fetch(`${BASE}/api/results/${sessionId}`, {
    headers: { 'Content-Type': 'application/json' },
  })

  if (res.status === 202) return null

  if (!res.ok) {
    const detail = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error((detail as { detail?: string }).detail ?? 'Failed to load results')
  }

  return res.json() as Promise<RoutingResult>
}
