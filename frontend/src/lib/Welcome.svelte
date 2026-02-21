<script lang="ts">
  import { t } from './i18n'
</script>

<section class="welcome" aria-label="Welcome">
  <h1 class="title">{t('welcome_title')}</h1>
  <p class="subtitle">{t('welcome_subtitle')}</p>
</section>

<style>
  .welcome { padding: 16px 8px; }
  .title { font-size: 1.8rem; margin: 6px 0; }
  .subtitle { color: #444; margin: 0; }
  @media (min-width: 640px) {
    .title { font-size: 2.2rem; }
  }
</style>
