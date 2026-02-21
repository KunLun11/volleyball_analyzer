import type { RequestHandler } from '@sveltejs/kit'

export const GET: RequestHandler = async () => {
  const data = [
    { id: 1, title: 'Set 1 — Quick Analysis', summary: 'Serve patterns and attack correlations identified in Set 1.', date: '2026-02-01' },
    { id: 2, title: 'Match Preview – Team A vs Team B', summary: 'Early insights on player heat maps and defensive shifts.', date: '2026-02-08' },
    { id: 3, title: 'Live Report — Q4 Trends', summary: 'Real-time analytics of rally lengths and serve success.', date: '2026-02-12' },
  ]
  return new Response(JSON.stringify(data), {
    status: 200,
    headers: { 'Content-Type': 'application/json' }
  })
}
