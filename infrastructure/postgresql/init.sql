CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS matches (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chat_id BIGINT NOT NULL,
    team_a_name VARCHAR(50),
    team_b_name VARCHAR(50),
    composition_a INTEGER[], 
    composition_b INTEGER[],
    status VARCHAR(20),
    current_set SMALLINT,
    score_a SMALLINT, 
    score_b SMALLINT, 
    set_scores JSONB,
    rotation_a SMALLINT,
    rotation_b SMALLINT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_matches_chat_id ON matches(chat_id);
CREATE INDEX IF NOT EXISTS idx_matches_status ON matches(status);
CREATE INDEX IF NOT EXISTS idx_matches_chat_status ON matches(chat_id, status);

CREATE TABLE IF NOT EXISTS match_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    match_id UUID REFERENCES matches(id) ON DELETE CASCADE,
    player_number INTEGER NOT NULL,
    team_id INTEGER NOT NULL CHECK (team_id IN (1, 2)),
    action_type VARCHAR(50) NOT NULL,
    result VARCHAR(50) NOT NULL,
    set_number INTEGER NOT NULL DEFAULT 1,
    score_a INTEGER NOT NULL,
    score_b INTEGER NOT NULL,
    rotation_a INTEGER,
    rotation_b INTEGER,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_match_events_match_id ON match_events(match_id);
CREATE INDEX IF NOT EXISTS idx_match_events_timestamp ON match_events(timestamp);
CREATE INDEX IF NOT EXISTS idx_match_events_match_set ON match_events(match_id, set_number);