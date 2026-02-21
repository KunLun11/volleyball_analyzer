from uuid import UUID

import asyncpg

from app.application.queries.dto import MatchDTO, MatchEventDTO


class MatchQueries:
    def __init__(self, pool: asyncpg.Pool):
        self._pool = pool

    async def get_by_id(self, match_id: UUID) -> MatchDTO | None:
        query = """
            SELECT id, team_a_name, team_b_name, status, created_at, 
                current_set, score_a, score_b,
                composition_a, composition_b
            FROM matches
            WHERE id = $1
        """
        row = await self._pool.fetchrow(query, str(match_id))
        if row is None:
            return None

        raw_uuid = row["id"]
        if hasattr(raw_uuid, "hex"):
            uuid_obj = UUID(hex=raw_uuid.hex)
        else:
            uuid_obj = UUID(str(raw_uuid))

        return MatchDTO(
            id=uuid_obj,
            team_a_name=row["team_a_name"],
            team_b_name=row["team_b_name"],
            composition_a=row["composition_a"],
            composition_b=row["composition_b"],
            status=row["status"],
            created_at=row["created_at"],
            current_set=row["current_set"],
            score_a=row["score_a"],
            score_b=row["score_b"],
        )

    async def get_live(self) -> list[MatchDTO]:
        query = """
            SELECT id, team_a_name, team_b_name, status, created_at,
                current_set, score_a, score_b,
                composition_a, composition_b
            FROM matches
            WHERE status = 'LIVE'
            ORDER BY created_at DESC
        """
        rows = await self._pool.fetch(query)
        result = []
        for row in rows:
            raw_uuid = row["id"]
            if hasattr(raw_uuid, "hex"):
                uuid_obj = UUID(hex=raw_uuid.hex)
            else:
                uuid_obj = UUID(str(raw_uuid))
            result.append(
                MatchDTO(
                    id=uuid_obj,
                    team_a_name=row["team_a_name"],
                    team_b_name=row["team_b_name"],
                    composition_a=row["composition_a"],
                    composition_b=row["composition_b"],
                    status=row["status"],
                    created_at=row["created_at"],
                    current_set=row["current_set"],
                    score_a=row["score_a"],
                    score_b=row["score_b"],
                )
            )
        return result

    async def get_by_chat_id(self, chat_id: int) -> list[MatchDTO]:
        query = """
            SELECT id, team_a_name, team_b_name, status, created_at,
                current_set, score_a, score_b,
                composition_a, composition_b
            FROM matches
            WHERE chat_id = $1
            ORDER BY created_at DESC
        """
        rows = await self._pool.fetch(query, chat_id)
        result = []
        for row in rows:
            raw_uuid = row["id"]
            if hasattr(raw_uuid, "hex"):
                uuid_obj = UUID(hex=raw_uuid.hex)
            else:
                uuid_obj = UUID(str(raw_uuid))
            result.append(
                MatchDTO(
                    id=uuid_obj,
                    team_a_name=row["team_a_name"],
                    team_b_name=row["team_b_name"],
                    composition_a=row["composition_a"],
                    composition_b=row["composition_b"],
                    status=row["status"],
                    created_at=row["created_at"],
                    current_set=row["current_set"],
                    score_a=row["score_a"],
                    score_b=row["score_b"],
                )
            )
        return result

    async def get_match_events(self, match_id: UUID) -> list[MatchEventDTO]:
        query = """
            SELECT match_id, timestamp, player_id, team_id, action_type,
                result, rotation, set_number 
            FROM matches
            WHERE match_id = $1
            ORDER BY timestamp ASC
        """
        rows = await self._pool.fetch(query, str(match_id))
        return [
            MatchEventDTO(
                timestamp=row["timestamp"],
                player_id=row["player_id"],
                team_id=row["team_id"],
                action_type=row["action_type"],
                result=row["result"],
                rotation=row["rotation"],
            )
            for row in rows
        ]
