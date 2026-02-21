from dataclasses import dataclass
from uuid import UUID

from app.application.exeptions import (
    ConflictError,
    NotFoundError,
    ValidationError,
)
from app.application.ports.event_bus import EventBus
from app.application.ports.uow import UnitOfWork
from app.application.ports.websocket_publisher import WebSocketPublisher
from app.application.queries.dto import MatchResultDTO
from app.domain.entities.matches import Match
from app.domain.enums import MatchStatusEnum
from app.domain.events import DomainEvent
from app.domain.values.composites import MatchEvent
from app.domain.values.identifiers import MatchID


@dataclass
class CompleteMatchCommand:
    match_id: UUID
    winner: int | None = None


class CompleteMatchHandler:
    def __init__(
        self,
        uow: UnitOfWork,
        event_bus: EventBus,
        ws_publisher: WebSocketPublisher | None = None,
    ):
        self._uow = uow
        self._event_bus = event_bus
        self._ws_publisher = ws_publisher

    def _ensure_match_live(self, match: Match) -> None:
        if match.status != MatchStatusEnum.LIVE:
            raise ConflictError(f"Cannot complete match: status is {match.status.name}")

    def _count_sets(self, match: Match) -> tuple[int, int]:
        sets_a = 0
        sets_b = 0
        for set_score in match.set_scores:
            if set_score.a > set_score.b:
                sets_a += 1
            else:
                sets_b += 1
        return (sets_a, sets_b)

    def _validate_winner(self, winner: int, match: Match) -> None:
        if winner not in (1, 2):
            raise ValidationError(f"Winner must be 1 or 2")
        sets_a, sets_b = self._count_sets(match)
        if winner == 1 and sets_a < 3:
            raise ValidationError(f"Team 1 has only {sets_a} sets, cannot be winner")
        if winner == 2 and sets_b < 3:
            raise ValidationError(f"Team 2 has only {sets_b} sets, cannot be winner")

    async def _process_event(
        self,
        match: Match,
        winner: int,
    ) -> list[DomainEvent]:
        match.complete(winner)
        await self._uow.matches().add(match)
        await self._uow.commit()
        events = match.domain_events
        match.clear_domain_events()
        await self._event_bus.publish(events)

        if self._ws_publisher:
            # Отправляем полное состояние матча после завершения
            match_state = {
                "type": "match_state",
                "match_state": {
                    "match_id": str(match.id.value),
                    "status": match.status.name,
                    "current_set": match.current_set.value,
                    "score_a": match.score.a.value,
                    "score_b": match.score.b.value,
                    "rotation_a": match.rotation.team_a.value,
                    "rotation_b": match.rotation.team_b.value,
                    "changes": ["match_completed"],
                }
            }
            await self._ws_publisher.publish(match.id, match_state)
        return events

    async def _load_match(self, raw_id: UUID) -> Match:
        match_id = MatchID(raw_id)
        match = await self._uow.matches().get(match_id)
        if match is None:
            raise NotFoundError(f"Match {raw_id} not found")
        return match

    async def handle(self, cmd: CompleteMatchCommand) -> MatchResultDTO:
        match = await self._load_match(cmd.match_id)
        self._ensure_match_live(match)
        winner = cmd.winner
        if winner is not None:
            self._validate_winner(winner, match)
        await self._process_event(match, winner)

        return MatchResultDTO.from_domain(match, winner)
