<script lang="ts">
  import { translations } from './i18n'
  import { locale, translations as _tr } from './i18n'
  // Simple local t helper to avoid TS issues; we'll use the string keys with current lang
  import { get } from 'svelte/store'
  type Locale = 'ru' | 'en'
  const mapFor = (lang: Locale) => (translations as any)[lang] || (translations as any).ru
  $: lang = get(locale) as Locale
  function t(key: string): string {
    const m = mapFor(lang)
    return m[key] ?? key
  }
  export let visible: boolean = false
</script>
{#if visible}
<section aria-label={t('instructions_title')}>
  <h2>{t('instructions_title')}</h2>
  <p>{t('instructions_intro')}</p>
  <ol>
    <li>{t('instructions_step1')}</li>
    <li>{t('instructions_step2')}</li>
    <li>{t('instructions_step3')}</li>
  </ol>
</section>
{/if}
