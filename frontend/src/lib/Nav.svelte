<script lang="ts">
  import { showLiveModal, liveMatchesCount } from '$lib/stores'
  import { locale } from '$lib/i18n'
  import { t } from './i18n'

  export let lang: string = 'ru'

  function openLiveMatches() {
    showLiveModal.update(v => !v)
  }

  $: count = $liveMatchesCount
</script>

<nav aria-label="Main navigation" class="nav">
  <div class="nav-inner">
    <a href="/" class="brand" aria-label="VolleyLab brand">
      <span class="brand-icon">🏐</span>
      <span class="brand-text">VolleyLab</span>
    </a>

    <button
      class="live-btn"
      onclick={openLiveMatches}
      aria-label={t('live_matches_title')}
    >
      <span class="live-dot"></span>
      <span class="live-text">{t('live_matches_title')}</span>
      {#if count > 0}
        <span class="live-count">{count}</span>
      {/if}
    </button>

    <div class="spacer"></div>

    <button class="lang-btn" onclick={() => locale.update(l => l === 'ru' ? 'en' : 'ru')}>
      {#if lang === 'ru'}
        <span class="lang-icon">🇬🇧</span>
        <span>EN</span>
      {:else}
        <span class="lang-icon">🇷🇺</span>
        <span>RU</span>
      {/if}
    </button>
  </div>
</nav>

<style>
  .nav {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    position: sticky;
    top: 0;
    z-index: 50;
    border-bottom: 1px solid rgba(102, 126, 234, 0.2);
    box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
  }

  .nav-inner {
    display: flex;
    align-items: center;
    padding: 12px 20px;
    max-width: 1200px;
    margin: 0 auto;
    gap: 12px;
  }

  .brand {
    display: flex;
    align-items: center;
    gap: 10px;
    font-weight: 700;
    font-size: 1.1rem;
    text-decoration: none;
    color: inherit;
    transition: transform 0.2s ease;
  }

  .brand:hover {
    transform: scale(1.05);
  }

  .brand-icon {
    font-size: 1.5rem;
    animation: bounce 2s ease-in-out infinite;
  }

  .brand-text {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  .live-btn {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 10px 18px;
    background: linear-gradient(135deg, rgba(220, 38, 38, 0.1) 0%, rgba(239, 68, 68, 0.1) 100%);
    border: 2px solid rgba(220, 38, 38, 0.3);
    border-radius: 999px;
    cursor: pointer;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
  }

  .live-btn:hover {
    background: linear-gradient(135deg, rgba(220, 38, 38, 0.2) 0%, rgba(239, 68, 68, 0.2) 100%);
    border-color: rgba(220, 38, 38, 0.5);
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(220, 38, 38, 0.3);
  }

  .live-btn:active {
    transform: translateY(0);
  }

  .live-dot {
    width: 8px;
    height: 8px;
    background: #dc2626;
    border-radius: 50%;
    animation: pulse 1.5s ease-in-out infinite;
  }

  .live-text {
    font-weight: 600;
    font-size: 0.85rem;
    color: #dc2626;
  }

  .live-count {
    background: #dc2626;
    color: white;
    font-size: 0.7rem;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 999px;
    animation: bounce 1s ease-in-out infinite;
  }

  .spacer {
    flex: 1;
  }

  .lang-btn {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(102, 126, 234, 0.1);
    border: 1px solid rgba(102, 126, 234, 0.3);
    padding: 8px 14px;
    border-radius: 999px;
    cursor: pointer;
    transition: all 0.2s ease;
    font-weight: 600;
    color: #667eea;
    font-size: 0.85rem;
  }

  .lang-btn:hover {
    background: rgba(102, 126, 234, 0.2);
    border-color: rgba(102, 126, 234, 0.5);
    transform: translateY(-1px);
  }

  .lang-icon {
    font-size: 1rem;
  }

  @media (max-width: 640px) {
    .nav-inner {
      flex-wrap: wrap;
      gap: 12px;
    }

    .live-text {
      display: none;
    }

    .live-btn {
      padding: 8px 12px;
    }
  }
</style>
