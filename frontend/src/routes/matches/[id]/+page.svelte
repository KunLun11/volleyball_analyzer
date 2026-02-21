<script lang="ts">
  import { onMount, onDestroy } from 'svelte'
  import { get } from 'svelte/store'
  import { page } from '$app/stores'
  import { locale, t } from '$lib/i18n'
  import { matchesApi, ws } from '$lib/api/client'
  import type { Match, Advice } from '$lib/types/match'

  let match = $state<Match | null>(null)
  let advice = $state<Advice | null>(null)
  let loading = $state(false)
  let adviceLoading = $state(false)
  let error = $state<string | null>(null)
  let adviceError = $state<string | null>(null)

  let matchId = $derived($page.params.id)

  onMount(async () => {
    console.log('[Match Page] onMount called, matchId:', matchId)

    // Сначала загружаем матч
    await loadMatch()

    // Подключаемся к глобальному WebSocket
    ws.connect()

    // Подписываемся на WebSocket обновления для этого матча
    const unsubscribe = ws.matches.subscribe((wsMatches) => {
      console.log('[Match Page] WebSocket matches updated:', wsMatches?.length)
      if (wsMatches && wsMatches.length > 0) {
        const updatedMatch = wsMatches.find(m => m.id === matchId)
        if (updatedMatch) {
          console.log('[Match Page] Found matching match, updating:', updatedMatch)
          match = { ...match!, ...updatedMatch } as Match
        }
      }
    })

    return () => {
      console.log('[Match Page] Cleanup: unsubscribing')
      unsubscribe()
    }
  })

  $effect(() => {
    if (matchId) {
      loadMatch()
    }
  })

  async function loadMatch() {
    if (!matchId) return
    loading = true
    error = null
    try {
      const loadedMatch = await matchesApi.getById(matchId)
      match = loadedMatch

      // Добавляем матч в WebSocket store для обновлений
      if (ws && loadedMatch.status === 'LIVE') {
        // Получаем текущие матчи из store
        ws.matches.update((currentMatches) => {
          const existingMatch = currentMatches.find(m => m.id === matchId)
          if (!existingMatch) {
            return [...currentMatches, loadedMatch]
          }
          return currentMatches
        })
      }
    } catch (e) {
      error = e instanceof Error ? e.message : t('matches_load_error')
    } finally {
      loading = false
    }
  }

  async function loadAdvice() {
    if (!matchId) return
    adviceLoading = true
    adviceError = null
    try {
      advice = await matchesApi.getAdvice(matchId)
    } catch (e) {
      adviceError = e instanceof Error ? e.message : t('advice_load_error')
    } finally {
      adviceLoading = false
    }
  }

  function formatTime(dateString: string): string {
    const date = new Date(dateString)
    const lang = get(locale)
    return new Intl.DateTimeFormat(lang === 'ru' ? 'ru-RU' : 'en-US', {
      hour: '2-digit',
      minute: '2-digit',
      day: 'numeric',
      month: 'short',
    }).format(date)
  }

  function getStatusLabel(status: string): string {
    const labels: Record<string, string> = {
      LIVE: t('match_status_live'),
      SCHEDULED: t('match_status_scheduled'),
      COMPLETED: t('match_status_completed'),
      CANCELLED: t('match_status_cancelled'),
    }
    return labels[status] ?? status
  }
</script>

<svelte:head>
  <title>{match ? `${match.team_a_name} vs ${match.team_b_name}` : t('match_details_title')}</title>
</svelte:head>

<main class="container">
  <header class="header">
    <a href="/" class="back-button">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M19 12H5M12 19l-7-7 7-7"/>
      </svg>
      <span>{t('back_to_matches')}</span>
    </a>
    <h1 class="title">{t('match_details_title')}</h1>
  </header>

  {#if loading}
    <div class="loading">{t('loading')}</div>
  {:else if error}
    <div class="error" role="alert">
      <p>{error}</p>
      <button onclick={loadMatch}>{t('retry')}</button>
    </div>
  {:else if match}
    <article class="match-card">
      <div class="card-header">
        <span class="status status-{match.status.toLowerCase()}">
          {getStatusLabel(match.status)}
        </span>
        <span class="time">{formatTime(match.created_at)}</span>
      </div>

      <div class="scoreboard">
        <div class="team team-a">
          <span class="team-name">{match.team_a_name}</span>
          <span class="score">{match.score_a}</span>
        </div>
        <div class="set-info">
          <div class="set-badge">{t('set')} {match.current_set}</div>
        </div>
        <div class="team team-b">
          <span class="team-name">{match.team_b_name}</span>
          <span class="score">{match.score_b}</span>
        </div>
      </div>

      <div class="compositions">
        <div class="composition">
          <h3>{match.team_a_name}</h3>
          <div class="players">
            {#each match.composition_a as player}
              <span class="player-badge">#{player}</span>
            {/each}
          </div>
        </div>
        <div class="composition">
          <h3>{match.team_b_name}</h3>
          <div class="players">
            {#each match.composition_b as player}
              <span class="player-badge">#{player}</span>
            {/each}
          </div>
        </div>
      </div>
    </article>

    {#if match.status === 'LIVE'}
      <section class="advice-section">
        <h2>{t('advice_title')}</h2>
        {#if adviceLoading}
          <div class="loading-advice">{t('loading_advice')}</div>
        {:else if adviceError}
          <div class="error-small">{adviceError}</div>
        {:else if advice}
          <div class="advice-content">
            <p class="advice-text">{advice.advice}</p>
            <span class="advice-time">
              {new Date(advice.generated_at).toLocaleString(get(locale) === 'ru' ? 'ru-RU' : 'en-US')}
            </span>
          </div>
        {:else}
          <button class="advice-btn" onclick={loadAdvice}>
            {t('get_advice')}
          </button>
        {/if}
      </section>
    {/if}
  {/if}
</main>

<style>
  .container {
    padding: 16px;
    max-width: 800px;
    margin: 0 auto;
  }

  .header {
    margin-bottom: 24px;
  }

  .back-button {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 10px 18px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    text-decoration: none;
    border-radius: 10px;
    font-weight: 600;
    font-size: 0.9rem;
    margin-bottom: 16px;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
  }

  .back-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
  }

  .back-button:active {
    transform: translateY(0);
  }

  .back-button svg {
    transition: transform 0.3s ease;
  }

  .back-button:hover svg {
    transform: translateX(-4px);
  }

  .title {
    font-size: 1.6rem;
    margin: 8px 0;
  }

  .loading {
    text-align: center;
    padding: 48px 16px;
    color: #666;
  }

  .error {
    background: #fee;
    border: 1px solid #fcc;
    border-radius: 8px;
    padding: 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .error button {
    padding: 8px 16px;
    background: #c00;
    color: #fff;
    border: none;
    border-radius: 6px;
    cursor: pointer;
  }

  .match-card {
    border: 1px solid #eee;
    border-radius: 12px;
    padding: 20px;
    background: #fff;
    margin-bottom: 24px;
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
  }

  .status {
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
  }

  .status-live {
    background: #e6f4ea;
    color: #1e8e3e;
  }

  .status-scheduled {
    background: #e8f0fe;
    color: #1967d2;
  }

  .status-completed {
    background: #f1f3f4;
    color: #5f6368;
  }

  .status-cancelled {
    background: #fce8e6;
    color: #c5221f;
  }

  .time {
    font-size: 0.8rem;
    color: #666;
  }

  .scoreboard {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px 0;
    border-bottom: 1px solid #eee;
    margin-bottom: 20px;
  }

  .team {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
  }

  .team-name {
    font-weight: 600;
    font-size: 1.1rem;
  }

  .score {
    font-size: 2.5rem;
    font-weight: 700;
    color: #333;
  }

  .set-badge {
    background: #f0f4ff;
    color: #1967d2;
    padding: 6px 12px;
    border-radius: 8px;
    font-weight: 600;
  }

  .compositions {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
  }

  .composition h3 {
    font-size: 0.95rem;
    margin: 0 0 8px;
    color: #555;
  }

  .players {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
  }

  .player-badge {
    background: #f5f5f5;
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 0.85rem;
    font-weight: 500;
  }

  .advice-section {
    border: 1px solid #e5f0ff;
    border-radius: 12px;
    padding: 20px;
    background: #f8fbff;
  }

  .advice-section h2 {
    font-size: 1.1rem;
    margin: 0 0 16px;
    color: #1967d2;
  }

  .loading-advice {
    color: #666;
    font-style: italic;
  }

  .error-small {
    color: #c5221f;
    font-size: 0.9rem;
  }

  .advice-content {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .advice-text {
    line-height: 1.6;
    color: #333;
  }

  .advice-time {
    font-size: 0.8rem;
    color: #666;
  }

  .advice-btn {
    background: #1967d2;
    color: #fff;
    border: none;
    padding: 12px 24px;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
  }

  .advice-btn:hover {
    background: #1557b0;
  }

  @media (max-width: 600px) {
    .compositions {
      grid-template-columns: 1fr;
    }
  }
</style>
