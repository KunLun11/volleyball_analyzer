import type { Match, MatchState, MatchResult, Advice } from '$lib/types/match'
import { ws } from '$lib/stores'

const API_BASE = '/api'

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(error.detail ?? 'Request failed')
  }
  return response.json()
}

export const matchesApi = {
  /** Получить все активные матчи */
  async getLive(chatId?: number): Promise<Match[]> {
    const url = new URL(`${API_BASE}/matches/live`)
    if (chatId) {
      url.searchParams.set('chat_id', chatId.toString())
    }
    const response = await fetch(url.toString())
    return handleResponse<Match[]>(response)
  },

  /** Получить матч по ID */
  async getById(matchId: string): Promise<Match> {
    const response = await fetch(`${API_BASE}/matches/${matchId}`)
    return handleResponse<Match>(response)
  },

  /** Записать событие матча */
  async recordEvent(
    matchId: string,
    event: {
      player_number: number
      team_id: number
      action_type: string
      result: string
      timestamp?: string
    }
  ): Promise<MatchState> {
    const response = await fetch(`${API_BASE}/matches/${matchId}/events`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(event),
    })
    return handleResponse<MatchState>(response)
  },

  /** Завершить матч */
  async complete(matchId: string, winner?: number): Promise<MatchResult> {
    const response = await fetch(`${API_BASE}/matches/${matchId}/complete`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ winner }),
    })
    return handleResponse<MatchResult>(response)
  },

  /** Получить совет для матча */
  async getAdvice(matchId: string): Promise<Advice> {
    const response = await fetch(`${API_BASE}/matches/${matchId}/advice`)
    return handleResponse<Advice>(response)
  },

  /** Создать новый матч */
  async create(data: {
    team_a_name: string
    team_b_name: string
    composition_a: number[]
    composition_b: number[]
    chat_id: number
  }): Promise<Match> {
    const response = await fetch(`${API_BASE}/matches/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    })
    return handleResponse<Match>(response)
  },
}

export const healthApi = {
  async check(): Promise<{ status: string }> {
    const response = await fetch(`${API_BASE}/health`)
    return handleResponse<{ status: string }>(response)
  },
}

// Export WebSocket instance
export { ws }
