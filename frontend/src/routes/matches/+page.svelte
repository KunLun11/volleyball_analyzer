<script lang="ts">
  import { onMount } from 'svelte'
  import { get } from 'svelte/store'
  import { locale, t } from '$lib/i18n'
  import { matchesApi } from '$lib/api/client'
  import type { Match } from '$lib/types/match'

  let matches = $state<Match[]>([])
  let loading = $state(false)
  let error = $state<string | null>(null)

  onMount(async () => {
    await loadMatches()
  })

  async function loadMatches() {
    loading = true
    error = null
    try {
      matches = await matchesApi.getLive()
    } catch (e) {
      error = e instanceof Error ? e.message : t('matches_load_error')
    } finally {
      loading = false
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
  <title>{t('matches_page_title')}</title>
</svelte:head>

<main class="container">
  <header class="header">
    <h1 class="title">{t('matches_page_title')}</h1>
    <button class="refresh-btn" onclick={loadMatches} disabled={loading}>
      {loading ? t('loading') : t('refresh')}
    </button>
  </header>

  {#if error}
    <div class="error" role="alert">
      <p>{error}</p>
      <button onclick={loadMatches}>{t('retry')}</button>
    </div>
  {/if}

  {#if loading && matches.length === 0}
    <div class="loading">{t('loading')}</div>
  {:else if matches.length === 0}
    <div class="empty">
      <p>{t('no_live_matches')}</p>
    </div>
  {:else}
    <div class="grid">
      {#each matches as match (match.id)}
        <article class="card" aria-label="{match.team_a_name} vs {match.team_b_name}">
          <div class="card-header">
            <span class="status status-{match.status.toLowerCase()}">
              {getStatusLabel(match.status)}
            </span>
            <span class="time">{formatTime(match.created_at)}</span>
          </div>

          <div class="teams">
            <div class="team team-a">
              <span class="team-name">{match.team_a_name}</span>
              <span class="score">{match.score_a}</span>
            </div>
            <div class="set-info">
              {t('set')} {match.current_set}
            </div>
            <div class="team team-b">
              <span class="team-name">{match.team_b_name}</span>
              <span class="score">{match.score_b}</span>
            </div>
          </div>

          <div class="card-footer">
            <a class="details-link" href="/matches/{match.id}">
              {t('view_details')} →
            </a>
          </div>
        </article>
      {/each}
    </div>
  {/if}
</main>

<style>
  .container {
    padding: 16px;
    max-width: 1000px;
    margin: 0 auto;
  }

  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
  }

  .title {
    font-size: 1.6rem;
    margin: 0;
  }

  .refresh-btn {
    padding: 8px 16px;
    border-radius: 8px;
    border: 1px solid #ddd;
    background: #fff;
    cursor: pointer;
    font-size: 0.9rem;
  }

  .refresh-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .error {
    background: #fee;
    border: 1px solid #fcc;
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 16px;
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

  .loading, .empty {
    text-align: center;
    padding: 48px 16px;
    color: #666;
  }

  .grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .card {
    border: 1px solid #eee;
    border-radius: 12px;
    padding: 16px;
    background: #fff;
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
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

  .teams {
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin-bottom: 12px;
  }

  .team {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .team-name {
    font-weight: 500;
  }

  .score {
    font-size: 1.5rem;
    font-weight: 700;
    color: #333;
  }

  .set-info {
    text-align: center;
    font-size: 0.85rem;
    color: #666;
    padding: 4px 0;
  }

  .card-footer {
    border-top: 1px solid #eee;
    padding-top: 12px;
  }

  .details-link {
    color: #1967d2;
    text-decoration: none;
    font-weight: 500;
  }

  .details-link:hover {
    text-decoration: underline;
  }

  @media (min-width: 640px) {
    .title { font-size: 2rem; }
    .grid { grid-template-columns: repeat(2, 1fr); }
  }
</style>
