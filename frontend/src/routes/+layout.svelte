<script lang="ts">
  import { onDestroy, onMount } from 'svelte'
  import Nav from '$lib/Nav.svelte'
  import LiveMatchesModal from '$lib/LiveMatchesModal.svelte'
  import { showLiveModal, liveMatchesCount } from '$lib/stores'
  import { locale } from '$lib/i18n'

  let lang: 'ru' | 'en' = 'ru'
  const unsub = locale.subscribe((l) => (lang = l))

  type Match = {
    id: string
    team_a_name: string
    team_b_name: string
    score_a: number
    score_b: number
    status: string
    current_set: number
    created_at: string
    composition_a: number[]
    composition_b: number[]
  }

  let matches: Match[] = []
  let modalLoading = false

  onMount(async () => {
    await loadMatches()
  })

  onDestroy(() => unsub())

  async function loadMatches() {
    try {
      const res = await fetch('/api/reports/')
      if (!res.ok) throw new Error('Failed to fetch')
      matches = await res.json()
      const liveCount = matches.filter(m => m.status === 'LIVE').length
      liveMatchesCount.set(liveCount)
    } catch (e) {
      console.error('Error loading matches:', e)
    }
  }

  function toggleLang() {
    locale.update((l) => (l === 'ru' ? 'en' : 'ru'))
  }

  async function openLiveModal() {
    if (matches.length === 0) {
      modalLoading = true
      await loadMatches()
      modalLoading = false
    }
    showLiveModal.set(true)
  }

  function closeLiveModal() {
    showLiveModal.set(false)
  }
</script>

<svelte:head>
  <link rel="icon" href="/favicon.svg" type="image/svg+xml" />
</svelte:head>

<LiveMatchesModal
  matches={matches}
  visible={$showLiveModal}
  loading={modalLoading}
  on:close={closeLiveModal}
/>

<Nav {lang} />

<slot />

<footer class="footer">
  <div class="footer-content">
    <div class="footer-brand">
      <span class="footer-icon">🏐</span>
      <span>VolleyLab</span>
    </div>
    <p class="footer-text">
      VolleyLab — Ваш персональный аналитик волейбольных матчей
    </p>
  </div>
</footer>

<style>
  :global(html) {
    background: linear-gradient(-45deg, #667eea, #764ba2, #a855f7) !important;
    background-size: 400% 400% !important;
    animation: gradient 20s ease infinite !important;
    min-height: 100vh;
  }

  :global(body) {
    background: transparent !important;
  }

  @keyframes gradient {
    0% {
      background-position: 0% 50%;
    }
    50% {
      background-position: 100% 50%;
    }
    100% {
      background-position: 0% 50%;
    }
  }

  .footer {
    margin: 60px 40px;
    padding: 40px;
    border-radius: 24px;
    background: rgba(26, 32, 44, 0.95) !important;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
  }

  .footer-content {
    text-align: center;
  }

  .footer-brand {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    font-weight: 700;
    font-size: 1.3rem;
    color: white;
    margin-bottom: 16px;
  }

  .footer-icon {
    font-size: 1.8rem;
  }

  .footer-text {
    color: rgba(255, 255, 255, 0.7);
    margin: 0;
  }
</style>
