<script lang="ts">
  import { onMount, onDestroy } from 'svelte'
  import { showLiveModal, liveMatchesCount, ws } from '$lib/stores'
  import { t } from '$lib/i18n'
  import LiveMatchesModal from '$lib/LiveMatchesModal.svelte'
  import FloatingCards from '$lib/FloatingCards.svelte'

  let showInstructions = $state(false)

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
  let matches = $state<Match[]>([])

  onMount(() => {
    // Connect to WebSocket
    ws.connect()
    loadMatches()

    // Subscribe to WebSocket matches updates
    const unsubscribe = ws.matches.subscribe((wsMatches) => {
      if (wsMatches && wsMatches.length > 0) {
        matches = wsMatches as Match[]
      }
    })

    return () => {
      unsubscribe()
    }
  })

  onDestroy(() => {
    ws.disconnect()
  })

  async function loadMatches() {
    try {
      const res = await fetch('/api/reports/')
      if (!res.ok) throw new Error('Failed to fetch: ' + res.status)
      const fetchedMatches = await res.json()
      matches = fetchedMatches
      liveMatchesCount.set(matches.filter(m => m.status === 'LIVE').length)
    } catch (e) {
      console.error('Error loading matches:', e)
    }
  }

  function openLiveModal() {
    showLiveModal.set(true)
  }

  function closeLiveModal() {
    showLiveModal.set(false)
  }
</script>

<LiveMatchesModal
  matches={matches}
  visible={$showLiveModal}
  on:close={closeLiveModal}
/>

<main class="container" role="main">
  <!-- Hero Section -->
  <section class="hero">
    <div class="hero-content">
      <div class="hero-badge glass">
        <span class="sparkle">✨</span>
        <span>{t('welcome_badge')}</span>
      </div>
      <h1 class="title gradient-text">{t('welcome_title')}</h1>
      <p class="subtitle">
        {t('welcome_subtitle')}
      </p>

      <div class="hero-stats">
        <div class="stat-card glass">
          <div class="stat-icon">🔴</div>
          <div class="stat-value">{matches.filter(m => m.status === 'LIVE').length}</div>
          <div class="stat-label">{t('live_matches_short')}</div>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-card glass">
          <div class="stat-icon">📊</div>
          <div class="stat-value">{matches.length}</div>
          <div class="stat-label">{t('total_matches')}</div>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-card glass">
          <div class="stat-icon">🤖</div>
          <div class="stat-value">AI</div>
          <div class="stat-label">{t('ai_powered')}</div>
        </div>
      </div>

      <div class="hero-actions">
        <button class="btn-primary glow-on-hover" onclick={openLiveModal}>
          <span class="btn-icon">🔴</span>
          {t('live_matches_title')}
          {#if matches.filter(m => m.status === 'LIVE').length > 0}
            <span class="badge">{matches.filter(m => m.status === 'LIVE').length}</span>
          {/if}
        </button>
      </div>
    </div>

    <!-- Volleyball Icon -->
    <div class="hero-volleyball">
      <span class="volleyball-icon">🏐</span>
    </div>
  </section>

  <!-- Floating Cards Section -->
  <FloatingCards />

  <!-- How It Works Section -->
  <section class="how-it-works">
    <h2 class="section-title">{t('how_it_works_title')}</h2>
    <div class="steps-container">
      <div class="step glass">
        <div class="step-number">1</div>
        <div class="step-content">
          <h3>{t('step1_title')}</h3>
          <p>{t('step1_desc')}</p>
        </div>
      </div>
      <div class="step-line"></div>
      <div class="step glass">
        <div class="step-number">2</div>
        <div class="step-content">
          <h3>{t('step2_title')}</h3>
          <p>{t('step2_desc')}</p>
        </div>
      </div>
      <div class="step-line"></div>
      <div class="step glass">
        <div class="step-number">3</div>
        <div class="step-content">
          <h3>{t('step3_title')}</h3>
          <p>{t('step3_desc')}</p>
        </div>
      </div>
    </div>
  </section>
</main>

<style>
  .container {
    padding: 0;
    max-width: 1200px;
    margin: 0 auto;
  }

  /* Hero Section */
  .hero {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 40px;
    padding: 60px 40px;
    align-items: center;
    min-height: 80vh;
  }

  .hero-content {
    animation: slideInLeft 0.8s ease-out;
  }

  .hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 16px;
    border-radius: 999px;
    font-size: 0.85rem;
    font-weight: 600;
    color: #667eea;
    margin-bottom: 20px;
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(102, 126, 234, 0.2);
  }

  .sparkle {
    animation: bounce 1.5s ease-in-out infinite;
  }

  .title {
    font-size: 3rem;
    margin: 0 0 16px;
    color: #2c5282;
    line-height: 1.2;
    font-weight: 800;
  }

  .subtitle {
    color: #4a5568;
    margin: 0 0 32px;
    font-size: 1.2rem;
    line-height: 1.6;
  }

  .hero-stats {
    display: flex;
    align-items: center;
    gap: 20px;
    padding: 24px;
    border-radius: 20px;
    margin-bottom: 32px;
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(102, 126, 234, 0.2);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  }

  .stat-card {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
    padding: 12px 20px;
  }

  .stat-icon {
    font-size: 1.5rem;
  }

  .stat-value {
    font-size: 1.8rem;
    font-weight: 700;
    color: #2c5282;
  }

  .stat-label {
    font-size: 0.75rem;
    color: #718096;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    text-align: center;
  }

  .stat-divider {
    width: 1px;
    height: 50px;
    background: linear-gradient(to bottom, transparent, rgba(102, 126, 234, 0.3), transparent);
  }

  .hero-actions {
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
  }

  .btn-primary {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    padding: 16px 28px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: none;
    border-radius: 16px;
    color: white;
    font-weight: 700;
    font-size: 1rem;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
  }

  .btn-primary:hover:not(:disabled) {
    transform: translateY(-3px);
    box-shadow: 0 12px 32px rgba(102, 126, 234, 0.6);
  }

  .btn-primary:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .btn-secondary {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    padding: 16px 28px;
    background: rgba(255, 255, 255, 0.95);
    border: 2px solid rgba(102, 126, 234, 0.3);
    border-radius: 16px;
    color: #667eea;
    font-weight: 700;
    font-size: 1rem;
    cursor: pointer;
    transition: all 0.3s ease;
    backdrop-filter: blur(10px);
  }

  .btn-secondary:hover {
    background: rgba(102, 126, 234, 0.1);
    border-color: rgba(102, 126, 234, 0.5);
    transform: translateY(-3px);
  }

  .btn-icon {
    font-size: 1.2rem;
  }

  .badge {
    background: rgba(255, 255, 255, 0.3);
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 700;
  }

  /* Volleyball Icon */
  .hero-volleyball {
    display: flex;
    align-items: center;
    justify-content: center;
    animation: slideInRight 0.8s ease-out;
  }

  .volleyball-icon {
    font-size: 10rem;
    filter: drop-shadow(0 10px 25px rgba(0, 0, 0, 0.2));
  }

  /* Features Section */
  .features {
    padding: 60px 40px;
  }

  .section-title {
    font-size: 2.5rem;
    text-align: center;
    margin: 0 0 50px;
    color: #2c5282;
    font-weight: 800;
  }

  /* Reports Section */
  .reports {
    margin: 40px;
    padding: 32px;
    border-radius: 24px;
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(102, 126, 234, 0.2);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  }

  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
  }

  .section-header .section-title {
    margin: 0;
    font-size: 1.8rem;
  }

  .btn-close {
    background: rgba(239, 68, 68, 0.1);
    border: none;
    width: 36px;
    height: 36px;
    border-radius: 50%;
    color: #dc2626;
    font-size: 1.2rem;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .btn-close:hover {
    background: rgba(239, 68, 68, 0.2);
    transform: rotate(90deg);
  }

  .matches-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 20px;
  }

  .match-card {
    padding: 24px;
    border-radius: 16px;
    background: white;
    border: 1px solid rgba(102, 126, 234, 0.2);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  }

  .match-card:hover {
    box-shadow: 0 12px 40px rgba(102, 126, 234, 0.2);
    border-color: rgba(102, 126, 234, 0.4);
  }

  .match-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
  }

  .status {
    padding: 6px 14px;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    display: inline-flex;
    align-items: center;
    gap: 6px;
  }

  .status-live {
    background: rgba(239, 68, 68, 0.1);
    color: #dc2626;
  }

  .status-scheduled {
    background: rgba(102, 126, 234, 0.1);
    color: #667eea;
  }

  .status-completed {
    background: rgba(107, 114, 128, 0.1);
    color: #6b7280;
  }

  .live-dot-small {
    width: 6px;
    height: 6px;
    background: currentColor;
    border-radius: 50%;
    animation: pulse 1.5s ease-in-out infinite;
  }

  .match-time {
    font-size: 0.8rem;
    color: #666;
  }

  .match-teams {
    display: flex;
    flex-direction: column;
    gap: 12px;
    margin-bottom: 16px;
  }

  .team-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 16px;
    background: rgba(102, 126, 234, 0.05);
    border-radius: 10px;
  }

  .team-name {
    font-weight: 600;
    color: #1a202c;
  }

  .score {
    font-size: 1.5rem;
    font-weight: 700;
    color: #667eea;
  }

  .match-info {
    text-align: center;
    padding: 12px 0;
    border-top: 1px solid rgba(102, 126, 234, 0.1);
    border-bottom: 1px solid rgba(102, 126, 234, 0.1);
    margin-bottom: 16px;
  }

  .set-badge {
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
    color: #667eea;
    padding: 6px 14px;
    border-radius: 999px;
    font-size: 0.85rem;
    font-weight: 600;
  }

  .details-link {
    color: #667eea;
    text-decoration: none;
    font-weight: 600;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 10px 16px;
    background: rgba(102, 126, 234, 0.1);
    border-radius: 10px;
    transition: all 0.2s ease;
  }

  .details-link:hover {
    background: rgba(102, 126, 234, 0.2);
    transform: translateX(4px);
  }

  /* How It Works */
  .how-it-works {
    padding: 60px 40px;
  }

  .steps-container {
    max-width: 800px;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    gap: 20px;
  }

  .step {
    display: flex;
    gap: 24px;
    padding: 24px;
    border-radius: 20px;
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(102, 126, 234, 0.2);
    align-items: flex-start;
  }

  .step-number {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    width: 48px;
    height: 48px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: 1.3rem;
    flex-shrink: 0;
  }

  .step-content h3 {
    font-size: 1.3rem;
    margin: 0 0 8px;
    color: #2d3748;
  }

  .step-content p {
    color: #4a5568;
    line-height: 1.6;
    margin: 0;
  }

  .step-line {
    width: 2px;
    height: 40px;
    background: linear-gradient(to bottom, rgba(102, 126, 234, 0.5), transparent);
    margin: 0 auto;
  }

  /* Footer */
  .footer {
    margin: 60px 40px;
    padding: 40px;
    border-radius: 24px;
    background: rgba(26, 32, 44, 0.95);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.1);
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
    margin: 0 0 24px;
  }

  .footer-links {
    display: flex;
    justify-content: center;
    gap: 24px;
  }

  .footer-link {
    color: rgba(255, 255, 255, 0.7);
    text-decoration: none;
    transition: color 0.2s ease;
  }

  .footer-link:hover {
    color: white;
  }

  /* Loading & Empty States */
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

  .error-card {
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid rgba(239, 68, 68, 0.3);
    border-radius: 12px;
    padding: 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 16px;
  }

  .error-content {
    display: flex;
    align-items: center;
    gap: 12px;
    color: #dc2626;
  }

  .error-icon {
    font-size: 1.5rem;
  }

  .retry-btn {
    padding: 10px 20px;
    background: #dc2626;
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 600;
    transition: all 0.2s ease;
  }

  .retry-btn:hover {
    background: #b91c1c;
    transform: translateY(-2px);
  }

  /* Responsive */
  @media (max-width: 900px) {
    .hero {
      grid-template-columns: 1fr;
      text-align: center;
      padding: 40px 20px;
    }

    .hero-animation {
      display: none;
    }

    .hero-stats {
      justify-content: center;
    }

    .hero-actions {
      justify-content: center;
    }

    .title {
      font-size: 2.2rem;
    }

    .features-grid {
      grid-template-columns: 1fr;
    }

    .matches-grid {
      grid-template-columns: 1fr;
    }
  }
</style>
