<script lang="ts">
  import { createEventDispatcher } from 'svelte'
  import { t } from './i18n'

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

  let { matches = [], visible = false } = $props()

  const dispatch = createEventDispatcher()

  function close() {
    dispatch('close')
  }

  function formatTime(dateString: string): string {
    const date = new Date(dateString)
    return new Intl.DateTimeFormat('ru-RU', {
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

{#if visible}
  <div class="modal-overlay" onclick={close} role="dialog" aria-modal="true" aria-labelledby="modal-title">
    <div class="modal-content" onclick={(e) => e.stopPropagation()}>
      <div class="modal-header">
        <div class="modal-title-wrapper">
          <span class="live-indicator">
            <span class="live-dot"></span>
            {t('live_matches_title')}
          </span>
          <h2 id="modal-title" class="modal-title">
            {matches.length} {matches.length === 1 ? 'матч' : matches.length < 5 ? 'матча' : 'матчей'}
          </h2>
        </div>
        <button class="modal-close" onclick={close} aria-label="Close">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M18 6L6 18M6 6l12 12"/>
          </svg>
        </button>
      </div>

      <div class="modal-body">
        {#if matches.length === 0}
          <div class="empty-state">
            <div class="empty-icon">🏐</div>
            <p>{t('no_live_matches')}</p>
          </div>
        {:else}
          <div class="matches-grid">
            {#each matches as match, i (match.id)}
              <article 
                class="match-card animate-slide-in-up" 
                style="animation-delay: {i * 0.1}s"
              >
                <div class="match-card-header">
                  <span class="status-badge status-live">
                    <span class="live-dot-small"></span>
                    {getStatusLabel(match.status)}
                  </span>
                  <span class="match-time">{formatTime(match.created_at)}</span>
                </div>

                <div class="match-card-body">
                  <div class="team">
                    <span class="team-name">{match.team_a_name}</span>
                    <div class="team-composition">
                      {#each match.composition_a.slice(0, 3) as num}
                        <span class="player-number">{num}</span>
                      {/each}
                      {#if match.composition_a.length > 3}
                        <span class="player-number more">+{match.composition_a.length - 3}</span>
                      {/if}
                    </div>
                  </div>
                  
                  <div class="score-display">
                    <span class="score score-a">{match.score_a}</span>
                    <span class="score-separator">:</span>
                    <span class="score score-b">{match.score_b}</span>
                  </div>

                  <div class="team">
                    <span class="team-name">{match.team_b_name}</span>
                    <div class="team-composition">
                      {#each match.composition_b.slice(0, 3) as num}
                        <span class="player-number">{num}</span>
                      {/each}
                      {#if match.composition_b.length > 3}
                        <span class="player-number more">+{match.composition_b.length - 3}</span>
                      {/if}
                    </div>
                  </div>
                </div>

                <div class="match-card-footer">
                  <span class="set-info">
                    {t('set')} {match.current_set}
                  </span>
                  <a href="/matches/{match.id}" class="view-btn">
                    {t('view_details')}
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M5 12h14M12 5l7 7-7 7"/>
                    </svg>
                  </a>
                </div>
              </article>
            {/each}
          </div>
        {/if}
      </div>
    </div>
  </div>
{/if}

<style>
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.6);
    backdrop-filter: blur(5px);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    padding: 20px;
    animation: fadeIn 0.3s ease-out;
  }

  .modal-content {
    background: white;
    border-radius: 20px;
    max-width: 800px;
    width: 100%;
    max-height: 85vh;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    box-shadow: 0 25px 80px rgba(0, 0, 0, 0.3);
    animation: slideInUp 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  }

  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px 24px;
    border-bottom: 1px solid rgba(102, 126, 234, 0.2);
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
  }

  .modal-title-wrapper {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .modal-title {
    margin: 0;
    font-size: 1.5rem;
    font-weight: 700;
    color: #1a202c;
  }

  .live-indicator {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 14px;
    background: rgba(239, 68, 68, 0.1);
    border-radius: 999px;
    font-size: 0.8rem;
    font-weight: 600;
    color: #dc2626;
    width: fit-content;
  }

  .modal-close {
    background: rgba(102, 126, 234, 0.1);
    border: none;
    border-radius: 12px;
    padding: 8px;
    cursor: pointer;
    transition: all 0.2s ease;
    color: #667eea;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .modal-close:hover {
    background: rgba(102, 126, 234, 0.2);
    transform: rotate(90deg);
  }

  .modal-body {
    padding: 24px;
    overflow-y: auto;
    flex: 1;
  }

  .loading-state,
  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 60px 20px;
    text-align: center;
    color: #666;
  }

  .spinner {
    width: 48px;
    height: 48px;
    border: 4px solid rgba(102, 126, 234, 0.2);
    border-top-color: #667eea;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: 16px;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  .empty-icon {
    font-size: 4rem;
    margin-bottom: 16px;
    animation: bounce 2s ease-in-out infinite;
  }

  .matches-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .match-card {
    border: 1px solid rgba(102, 126, 234, 0.2);
    border-radius: 16px;
    overflow: hidden;
    background: white;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  }

  .match-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 30px rgba(102, 126, 234, 0.2);
    border-color: rgba(102, 126, 234, 0.4);
  }

  .match-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 16px;
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
    border-bottom: 1px solid rgba(102, 126, 234, 0.1);
  }

  .status-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    border-radius: 999px;
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .status-live {
    background: rgba(239, 68, 68, 0.1);
    color: #dc2626;
  }

  .live-dot-small {
    width: 6px;
    height: 6px;
    background: #dc2626;
    border-radius: 50%;
    animation: pulse 1.5s ease-in-out infinite;
  }

  .match-time {
    font-size: 0.8rem;
    color: #666;
  }

  .match-card-body {
    padding: 20px 16px;
  }

  .team {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
  }

  .team-name {
    font-weight: 600;
    font-size: 1rem;
    color: #1a202c;
  }

  .team-composition {
    display: flex;
    gap: 4px;
  }

  .player-number {
    background: rgba(102, 126, 234, 0.1);
    color: #667eea;
    font-size: 0.7rem;
    font-weight: 600;
    padding: 2px 6px;
    border-radius: 4px;
    min-width: 20px;
    text-align: center;
  }

  .player-number.more {
    background: rgba(118, 75, 162, 0.1);
    color: #764ba2;
  }

  .score-display {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    padding: 16px 0;
    margin: 12px 0;
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
    border-radius: 12px;
  }

  .score {
    font-size: 2rem;
    font-weight: 700;
    min-width: 40px;
    text-align: center;
  }

  .score-a {
    color: #667eea;
  }

  .score-separator {
    color: #999;
    font-weight: 300;
  }

  .score-b {
    color: #764ba2;
  }

  .match-card-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 16px;
    border-top: 1px solid rgba(102, 126, 234, 0.1);
    background: rgba(102, 126, 234, 0.02);
  }

  .set-info {
    font-size: 0.85rem;
    color: #666;
    font-weight: 500;
  }

  .view-btn {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    color: #667eea;
    text-decoration: none;
    font-weight: 600;
    font-size: 0.85rem;
    padding: 8px 14px;
    border-radius: 8px;
    background: rgba(102, 126, 234, 0.1);
    transition: all 0.2s ease;
  }

  .view-btn:hover {
    background: rgba(102, 126, 234, 0.2);
    transform: translateX(4px);
  }

  @media (min-width: 640px) {
    .matches-grid {
      grid-template-columns: repeat(2, 1fr);
    }
  }

  @media (max-width: 640px) {
    .modal-content {
      max-height: 90vh;
      border-radius: 16px;
    }

    .modal-header {
      padding: 16px;
    }

    .modal-body {
      padding: 16px;
    }

    .modal-title {
      font-size: 1.2rem;
    }
  }
</style>
