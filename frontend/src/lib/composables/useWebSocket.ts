import { onMount, onDestroy } from 'svelte'
import { writable, get } from 'svelte/store'
import { liveMatchesCount } from '$lib/stores'

type MatchStatus = 'LIVE' | 'SCHEDULED' | 'COMPLETED' | 'CANCELLED'

export type Match = {
  id: string
  team_a_name: string
  team_b_name: string
  score_a: number
  score_b: number
  status: MatchStatus
  current_set: number
  created_at: string
  composition_a: number[]
  composition_b: number[]
  rotation_a?: number
  rotation_b?: number
}

export type WSMessage = {
  type: 'match_update' | 'match_state'
  match_id?: string
  data?: Partial<Match>
  match_state?: {
    match_id: string
    status: MatchStatus
    current_set: number
    score_a: number
    score_b: number
    rotation_a?: number
    rotation_b?: number
    changes?: string[]
  }
}

export function createWebSocket() {
  let ws: WebSocket | null = null
  let reconnectTimeout: ReturnType<typeof setTimeout> | null = null
  let reconnectAttempts = 0
  const MAX_RECONNECT_ATTEMPTS = 5
  const RECONNECT_DELAY = 3000

  const connected = writable(false)
  const error = writable<string | null>(null)
  const matches = writable<Match[]>([])

  function connect() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.host || 'localhost:8000'
    const wsUrl = `${protocol}//${host}/api/ws/matches`
    
    console.log('[WebSocket] Connecting to:', wsUrl)

    try {
      ws = new WebSocket(wsUrl)

      ws.onopen = () => {
        console.log('[WebSocket] Connected successfully')
        connected.set(true)
        error.set(null)
        reconnectAttempts = 0
      }

      ws.onmessage = (event) => {
        console.log('[WebSocket] Raw message:', event.data)
        try {
          const message: WSMessage & { type: string; match_id?: string; data?: any } = JSON.parse(event.data)
          console.log('[WebSocket] Parsed message:', message)
          console.log('[WebSocket] Message type:', message.type)
          console.log('[WebSocket] Message data:', message.data)

          // Сообщение может быть в формате:
          // 1. {"type": "match_update", "match_id": "...", "data": {...}}
          // 2. {"type": "match_state", "match_state": {...}}

          console.log('[WebSocket] Checking conditions...')
          console.log('[WebSocket] type === match_update:', message.type === 'match_update')
          console.log('[WebSocket] has data:', !!message.data)

          if (message.type === 'match_update' && message.data) {
            console.log('[WebSocket] Inside match_update block')
            // Это обёрнутое сообщение от ws_publisher
            const innerData = message.data
            console.log('[WebSocket] innerData:', innerData)
            console.log('[WebSocket] innerData.match_state:', innerData.match_state)

            if (innerData.match_state) {
              console.log('[WebSocket] Processing match_state:', innerData.match_state)
              const state = innerData.match_state
              
              // Получаем текущие матчи и обновляем
              const currentMatches = get(matches)
              console.log('[WebSocket] Current matches count:', currentMatches?.length)
              
              if (currentMatches && currentMatches.length > 0) {
                const existingIndex = currentMatches.findIndex(m => m.id === state.match_id)
                console.log('[WebSocket] Found match at index:', existingIndex)
                
                if (existingIndex >= 0) {
                  const updated = [...currentMatches]
                  updated[existingIndex] = {
                    ...updated[existingIndex],
                    status: state.status,
                    current_set: state.current_set,
                    score_a: state.score_a,
                    score_b: state.score_b,
                    rotation_a: state.rotation_a,
                    rotation_b: state.rotation_b,
                  }
                  console.log('[WebSocket] Updated matches:', updated)
                  matches.set(updated)
                  console.log('[WebSocket] Store updated, new value:', get(matches))
                  updateLiveCount(updated)
                } else {
                  console.log('[WebSocket] Match not found in current matches')
                }
              } else {
                console.log('[WebSocket] No current matches in store')
              }
            } else {
              console.log('[WebSocket] No match_state in innerData')
            }
          } else {
            console.log('[WebSocket] Condition not met')
          }
        } catch (e) {
          console.error('Error parsing WebSocket message:', e)
          error.set('Error parsing message')
        }
      }

      ws.onclose = () => {
        console.log('[WebSocket] Disconnected')
        connected.set(false)

        // Attempt to reconnect
        if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
          reconnectAttempts++
          console.log(`[WebSocket] Reconnecting... Attempt ${reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS}`)
          reconnectTimeout = setTimeout(connect, RECONNECT_DELAY)
        }
      }

      ws.onerror = (e) => {
        console.error('[WebSocket] Error:', e)
        error.set('Connection error')
      }
    } catch (e) {
      console.error('[WebSocket] Failed to create connection:', e)
      error.set('Failed to connect')
    }
  }

  function updateLiveCount(currentMatches: Match[]) {
    const count = currentMatches.filter(m => m.status === 'LIVE').length
    liveMatchesCount.set(count)
  }

  function disconnect() {
    if (reconnectTimeout) {
      clearTimeout(reconnectTimeout)
      reconnectTimeout = null
    }
    if (ws) {
      ws.close()
      ws = null
    }
    connected.set(false)
  }

  function send(data: unknown) {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(data))
    }
  }

  return {
    connect,
    disconnect,
    send,
    connected,
    error,
    matches,
  }
}

export type WebSocketStore = ReturnType<typeof createWebSocket>
