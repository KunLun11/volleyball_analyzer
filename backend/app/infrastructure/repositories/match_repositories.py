import json
import uuid

from asyncpg import Pool
from asyncpg.pgproto import pgproto

from app.domain.entities.matches import Match
from app.domain.enums import MatchStatusEnum
from app.domain.values.composites import Rotation, Score, TeamComposition
from app.domain.values.identifiers import ChatID, MatchID
from app.domain.values.primitives import (
    PlayerNumber,
    RotationPosition,
    ScoreValue,
    SetNumber,
    TeamName,
)


class PostgresMatchRepository:
    def __init__(self, pool: Pool):
        self._pool = pool

    async def add(self, match: Match) -> None:
        match_id = str(match.id.value)
        chat_id = match.chat_id.value
        team_a_name = match.team_a_name.value
        team_b_name = match.team_b_name.value

        composition_a = [comp.value for comp in match.composition_a.get_players()]
        composition_b = [comp.value for comp in match.composition_b.get_players()]

        status = match.status.name
        current_set = match.current_set.value
        score_a = match.score.a.value
        score_b = match.score.b.value

        set_scores = json.dumps(
            [[set_score.a.value, set_score.b.value] for set_score in match.set_scores]
        )

        rotation_a = match.rotation.team_a.value
        rotation_b = match.rotation.team_b.value
        created_at = match.created_at
        updated_at = match.updated_at

        query = """
            INSERT INTO matches (
                id, chat_id, team_a_name, team_b_name,
                composition_a, composition_b, status,
                current_set, score_a, score_b, set_scores,
                rotation_a, rotation_b, created_at, updated_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
            ON CONFLICT (id) DO UPDATE SET
                status = EXCLUDED.status,
                current_set = EXCLUDED.current_set,
                score_a = EXCLUDED.score_a,
                score_b = EXCLUDED.score_b,
                set_scores = EXCLUDED.set_scores,
                rotation_a = EXCLUDED.rotation_a,
                rotation_b = EXCLUDED.rotation_b,
                updated_at = EXCLUDED.updated_at
        """
        await self._pool.execute(
            query,
            match_id,
            chat_id,
            team_a_name,
            team_b_name,
            composition_a,
            composition_b,
            status,
            current_set,
            score_a,
            score_b,
            set_scores,
            rotation_a,
            rotation_b,
            created_at,
            updated_at,
        )

    async def get(self, match_id: MatchID) -> Match | None:
        match_uuid = str(match_id.value)
        query = "SELECT * FROM matches WHERE id=$1"
        row = await self._pool.fetchrow(query, match_uuid)
        if row is None:
            return None

        raw_uuid = row["id"]
        if isinstance(raw_uuid, pgproto.UUID):
            python_uuid = uuid.UUID(bytes=raw_uuid.bytes)
        else:
            python_uuid = uuid.UUID(str(raw_uuid))
        match_id = MatchID(python_uuid)
        chat_id = ChatID(row["chat_id"])
        team_a_name = TeamName(row["team_a_name"])
        team_b_name = TeamName(row["team_b_name"])

        composition_raw_a = row["composition_a"]
        composition_a = TeamComposition(
            [PlayerNumber(comp) for comp in composition_raw_a]
        )

        composition_raw_b = row["composition_b"]
        composition_b = TeamComposition(
            [PlayerNumber(comp) for comp in composition_raw_b]
        )

        status = MatchStatusEnum[row["status"]]
        current_set = SetNumber(row["current_set"])

        score_value_a = ScoreValue(row["score_a"])
        score_value_b = ScoreValue(row["score_b"])
        score = Score(score_value_a, score_value_b)

        parsed = json.loads(row["set_scores"])
        set_scores = []
        for pair in parsed:
            a = pair[0]
            b = pair[1]
            score_value_a = ScoreValue(a)
            score_value_b = ScoreValue(b)
            score = Score(score_value_a, score_value_b)
            set_scores.append(score)

        rotation_position_a = RotationPosition(row["rotation_a"])
        rotation_position_b = RotationPosition(row["rotation_b"])
        rotation = Rotation(rotation_position_a, rotation_position_b)
        created_at = row["created_at"]
        updated_at = row["updated_at"]
        _events = []
        _domain_events = []
        match = Match(
            match_id,
            status,
            created_at,
            updated_at,
            team_a_name,
            team_b_name,
            composition_a,
            composition_b,
            current_set,
            score,
            rotation,
            chat_id,
            set_scores,
            _events,
            _domain_events,
        )
        return match

    async def get_live_by_chat(self, chat_id: ChatID) -> Match | None:
        chat_id_value = chat_id.value
        query = "SELECT id FROM matches WHERE chat_id=$1 AND status='LIVE' LIMIT 1"
        row = await self._pool.fetchrow(query, chat_id_value)
        if not row:
            return None

        raw_uuid = row["id"]
        if isinstance(raw_uuid, pgproto.UUID):
            python_uuid = uuid.UUID(bytes=raw_uuid.bytes)
        else:
            python_uuid = uuid.UUID(str(raw_uuid))
        match_id = MatchID(python_uuid)
        match = await self.get(match_id)
        return match
