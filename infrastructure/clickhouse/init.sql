CREATE DATABASE IF NOT EXISTS volleyball;

USE volleyball;

CREATE TABLE IF NOT EXISTS domain_events (
    event_id UUID,
    event_type String,
    match_id UUID,
    payload String,
    occurred_at DateTime64(3),
    processed_at DateTime64(3) DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (occurred_at, event_type);

CREATE TABLE IF NOT EXISTS match_events_log (
    match_id UUID,
    player_number UInt8,
    team_id UInt8,
    action_type String,
    result String,
    set_number UInt8,
    score_a UInt8,
    score_b UInt8,
    rotation_a UInt8,
    rotation_b UInt8,
    timestamp DateTime64(3)
) ENGINE = MergeTree()
ORDER BY (match_id, timestamp);