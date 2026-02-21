from datetime import datetime
from typing import Optional
from uuid import UUID
import httpx

from app.config import settings
from app.infrastructure.api_adapter import RabbitMQAPIAdapter
from app.infrastructure.client import RabbitMQClient


class ValidationError(Exception):
    pass


class ConflictError(Exception):
    pass


class NotFoundError(Exception):
    pass


class APIClient:
    def __init__(
        self,
        base_url: Optional[str] = None,
        use_rabbitmq: bool = False,
        rabbitmq_client: Optional[RabbitMQClient] = None,
    ):
        self.base_url = base_url or settings.API_URL
        self.use_rabbitmq = use_rabbitmq
        self.session = httpx.AsyncClient(follow_redirects=True)
        self._rabbitmq_client = rabbitmq_client
        self._rabbitmq_adapter = None

    async def _init_rabbitmq(self):
        if not self.use_rabbitmq:
            return
        if not self._rabbitmq_client:
            from app.infrastructure.client import RabbitMQClient

            self._rabbitmq_client = RabbitMQClient(
                url=settings.RABBITMQ_URL,
                timeout=settings.RABBITMQ_TIMEOUT,
            )
            await self._rabbitmq_client.start()
        if not self._rabbitmq_adapter:
            self._rabbitmq_adapter = RabbitMQAPIAdapter(self._rabbitmq_client)

    async def start(self):
        if self.use_rabbitmq:
            await self._init_rabbitmq()

    async def stop(self):
        if self._rabbitmq_client:
            await self._rabbitmq_client.stop()

    async def request_advice(self, match_id: UUID, chat_id: int) -> str:
        if self.use_rabbitmq:
            await self._init_rabbitmq()
            return await self._rabbitmq_adapter.request_advice(match_id, chat_id)
        url = f"{self.base_url}/api/matches/{match_id}/advice"
        response = await self.session.get(url)
        response.raise_for_status()
        data = response.json()
        return data["advice"]

    async def get_match(self, match_id: UUID) -> dict:
        if self.use_rabbitmq:
            await self._init_rabbitmq()
            return await self._rabbitmq_adapter.get_match(match_id)

        url = f"{self.base_url}/api/matches/{match_id}"
        response = await self.session.get(url)
        if response.status_code == 404:
            raise NotFoundError("Match not found")
        response.raise_for_status()
        return response.json()

    async def get_live_match_by_chat_id(self, chat_id: int) -> list[dict]:
        if self.use_rabbitmq:
            await self._init_rabbitmq()
            return await self._rabbitmq_adapter.get_live_match_by_chat_id(chat_id)

        url = f"{self.base_url}/api/matches/live"
        response = await self.session.get(url, params={"chat_id": chat_id})
        response.raise_for_status()
        return response.json()

    async def create_match(
        self,
        team_a_name: str,
        team_b_name: str,
        composition_a: list[int],
        composition_b: list[int],
        chat_id: int,
    ) -> dict:
        if self.use_rabbitmq:
            await self._init_rabbitmq()
            return await self._rabbitmq_adapter.create_match(
                team_a_name, team_b_name, composition_a, composition_b, chat_id
            )

        url = f"{self.base_url}/api/matches/"
        body = {
            "team_a_name": team_a_name,
            "team_b_name": team_b_name,
            "composition_a": composition_a,
            "composition_b": composition_b,
            "chat_id": chat_id,
        }

        response = await self.session.post(url, json=body)
        if response.status_code == 400:
            raise ValidationError(response.text)
        if response.status_code == 409:
            raise ConflictError("Chat already has live match")
        response.raise_for_status()
        return response.json()

    async def record_event(
        self,
        match_id: UUID,
        player_number: int,
        team_id: int,
        action_type: str,
        result: str,
        timestamp: datetime | None = None,
    ) -> dict:
        if self.use_rabbitmq:
            await self._init_rabbitmq()
            return await self._rabbitmq_adapter.record_event(
                match_id, player_number, team_id, action_type, result
            )

        url = f"{self.base_url}/api/matches/{match_id}/events"
        body = {
            "player_number": player_number,
            "team_id": team_id,
            "action_type": action_type,
            "result": result,
            "timestamp": timestamp.isoformat() if timestamp else None,
        }

        response = await self.session.post(url, json=body)
        if response.status_code == 404:
            raise NotFoundError("Match not found")
        if response.status_code == 409:
            raise ConflictError("Match not live")
        response.raise_for_status()
        return response.json()

    async def complete_match(
        self,
        match_id: UUID,
        winner: int | None = None,
    ):
        if self.use_rabbitmq:
            await self._init_rabbitmq()
            return await self._rabbitmq_adapter.complete_match(match_id, winner)

        url = f"{self.base_url}/api/matches/{match_id}/complete"
        body = {
            "winner": winner,
        }
        response = await self.session.post(url, json=body)
        response.raise_for_status()
        return response.json()

    async def get_live_matches(self) -> list[dict]:
        url = f"{self.base_url}/api/matches/live"
        response = await self.session.get(url)
        response.raise_for_status()
        return response.json()
