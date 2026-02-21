export interface Match {
  id: string
  team_a_name: string
  team_b_name: string
  composition_a: number[]
  composition_b: number[]
  status: MatchStatus
  created_at: string
  current_set: number
  score_a: number
  score_b: number
}

export type MatchStatus = 'SCHEDULED' | 'LIVE' | 'COMPLETED' | 'CANCELLED'

export interface MatchState {
  match_id: string
  status: MatchStatus
  current_set: number
  score_a: number
  score_b: number
  rotation_a: number
  rotation_b: number
  changes: string[]
}

export interface MatchResult {
  match_id: string
  winner: number | null
  total_sets: number
  set_scores: [number, number][]
  team_a_name: string
  team_b_name: string
}

export interface Advice {
  advice: string
  generated_at: string
  match_id: string
}
