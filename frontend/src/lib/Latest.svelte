<script lang="ts">
  import { onMount } from 'svelte'
  let reports: Array<{ id: number; title: string; summary: string; date: string }> = []
  let loading = false

  onMount(async () => {
    loading = true
    try {
      const res = await fetch('/api/reports')
      if (res.ok) {
        reports = await res.json()
      }
    } catch (_) {
      // ignore in mock
    } finally {
      loading = false
    }
  })
</script>

<section aria-label="Latest reports">
  <h2>Latest Reports</h2>
  {#if loading}
    <p>Loading...</p>
  {:else}
    <div class="grid">
      {#each reports as r}
      <article class="card" aria-label={r.title}>
        <h3 class="card-title">{r.title}</h3>
        <p class="card-desc">{r.summary}</p>
        <span class="card-date">{r.date}</span>
      </article>
      {/each}
    </div>
  {/if}
  </section>

<style>
  .grid { display: grid; grid-template-columns: 1fr; gap: 12px; margin: 8px 0; }
  .card { border: 1px solid #e5f0ff; padding: 12px; border-radius: 12px; background: #fff; }
  .card-title { margin: 0 0 6px; font-size: 1.02rem; }
  .card-desc { color: #555; margin: 0 0 6px; }
  .card-date { font-size: 0.85rem; color: #888; }
  @media (min-width: 640px) {
    .grid { grid-template-columns: repeat(2, 1fr); }
  }
</style>
