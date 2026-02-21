from typing import Any, Optional
from uuid import UUID
from app.infrastructure.client import RabbitMQClient
from app.infrastructure.models import (
    AdviceResponse,
    CompleteMatchResponse,
    EventResponse,
    LiveMatchesResponse,
    MatchResponse,
)


class RabbitMQAPIAdapter:
    def __init__(self, client: RabbitMQClient):
        self._client = client

    async def create_match(
        self,
        team_a_name: str,
        team_b_name: str,
        composition_a: list[int],
        composition_b: list[int],
        chat_id: int,
    ) -> dict[str, Any]:
        payload = {
            "team_a_name": team_a_name,
            "team_b_name": team_b_name,
            "composition_a": composition_a,
            "composition_b": composition_b,
            "chat_id": chat_id,
        }
        response = await self._client.publish_request("create_match", payload)
        return response.get("match", {})

    async def request_advice(self, match_id: UUID, chat_id: int) -> str:
        payload = {
            "match_id": str(match_id),
            "chat_id": chat_id,
        }
        response = await self._client.publish_request("request_advice", payload)
        return response.get("advice", "")

    async def get_match(self, match_id: UUID) -> dict[str, Any]:
        payload = {"match_id": str(match_id)}
        response = await self._client.publish_request("get_match", payload)
        return response.get("match", {})

    async def get_live_match_by_chat_id(self, chat_id: int) -> list[dict[str, Any]]:
        payload = {"chat_id": chat_id}
        response = await self._client.publish_request("get_live_match", payload)
        return response.get("matches", [])

    async def record_event(
        self,
        match_id: UUID,
        player_number: int,
        team_id: int,
        action_type: str,
        result: str,
    ) -> dict[str, Any]:
        payload = {
            "match_id": str(match_id),
            "player_number": player_number,
            "team_id": team_id,
            "action_type": action_type,
            "result": result,
        }
        response = await self._client.publish_request("record_event", payload)
        return response.get("match_state", {})

    async def complete_match(
        self,
        match_id: UUID,
        winner: Optional[int] = None,
    ) -> dict[str, Any]:
        payload = {"match_id": str(match_id), "winner": winner}
        response = await self._client.publish_request("complete_match", payload)
        return response.get("result", {})
