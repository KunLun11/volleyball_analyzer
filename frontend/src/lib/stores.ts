import { writable } from 'svelte/store'

export const showLiveModal = writable(false)
export const liveMatchesCount = writable(0)

// Global WebSocket store
import { createWebSocket } from './composables/useWebSocket'

export const ws = createWebSocket()
