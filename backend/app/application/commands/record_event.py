from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.application.exeptions import (
    ConflictError,
    NotFoundError,
    ValidationError,
)
from app.application.ports.event_bus import EventBus
from app.application.ports.uow import UnitOfWork
from app.application.ports.websocket_publisher import WebSocketPublisher
from app.application.queries.dto import MatchStateDTO
from app.domain.entities.matches import Match
from app.domain.enums import ActionTypeEnum, MatchStatusEnum, ResultEnum
from app.domain.events import (
    DomainEvent,
    MatchCompleted,
    PointScored,
    SetCompleted,
)
from app.domain.utils import now
from app.domain.values.composites import MatchEvent
from app.domain.values.identifiers import MatchID, PlayerID
from app.domain.values.primitives import PlayerNumber, RotationPosition
from app.domain.values.timestamps import Timestamp


@dataclass
class RecordEventCommand:
    match_id: UUID
    player_number: int
    team_id: int
    action_type: str
    result: str
    timestamp: datetime | None = None


class RecordEventHandler:
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
            raise ConflictError(f"Cannot record event: status is {match.status.name}")

    def _validate_team_id(self, team_id: int) -> None:
        if team_id not in (1, 2):
            raise ValidationError(f"team_id must be 1 or 2, got {team_id}")

    def _validate_player_in_composition(
        self, player_number: int, team_id: int, match: Match
    ) -> None:
        player_num = PlayerNumber(player_number)
        if team_id == 1:
            composition = match.composition_a
        else:
            composition = match.composition_b
        if not composition.has_player(player_num):
            raise ValidationError(f"Player {player_number} not in team {composition}")

    def _get_current_rotation(self, match: Match, team_id: int) -> RotationPosition:
        if team_id == 1:
            return match.rotation.team_a
        return match.rotation.team_b

    def _detect_changes(self, events: list[DomainEvent]) -> list[str]:
        changes = []
        for event in events:
            if isinstance(event, PointScored):
                changes.append("point_scored")
            if isinstance(event, SetCompleted):
                changes.append("set_completed")
            if isinstance(event, MatchCompleted):
                changes.append("match_completed")
        return changes

    def _validate_command(self, cmd: RecordEventCommand, match: Match) -> None:
        self._ensure_match_live(match)
        self._validate_team_id(cmd.team_id)
        self._validate_player_in_composition(cmd.player_number, cmd.team_id, match)

    def _create_match_event(self, cmd: RecordEventCommand, match: Match) -> MatchEvent:
        try:
            action_type = ActionTypeEnum[cmd.action_type.upper()]
        except KeyError:
            raise ValidationError(f"Unknown action_type: {cmd.action_type}")
        try:
            result = ResultEnum[cmd.result.upper()]
        except KeyError:
            raise ValidationError(f"Unknown result: {cmd.result}")
        timestamp = Timestamp(cmd.timestamp or now())
        player_id = PlayerID(cmd.player_number)
        rotation_position = self._get_current_rotation(match, cmd.team_id)
        return MatchEvent(
            timestamp,
            player_id,
            cmd.team_id,
            action_type,
            result,
            rotation_position,
        )

    async def _process_event(
        self,
        match: Match,
        event: MatchEvent,
    ) -> list[DomainEvent]:
        match.record_event(event)
        await self._uow.matches().add(match)
        await self._uow.commit()
        events = match.domain_events
        match.clear_domain_events()
        await self._event_bus.publish(events)
        return events

    async def _load_match(self, raw_id: UUID) -> Match:
        match_id = MatchID(raw_id)
        match = await self._uow.matches().get(match_id)
        if match is None:
            raise NotFoundError(f"Match {raw_id} not found")
        return match

    async def handle(self, cmd: RecordEventCommand) -> MatchStateDTO:
        match = await self._load_match(cmd.match_id)
        self._validate_command(cmd, match)
        match_event = self._create_match_event(cmd, match)
        events = await self._process_event(match, match_event)
        changes = self._detect_changes(events)
        if self._ws_publisher:
            # Отправляем полное состояние матча после каждого события
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
                    "changes": changes,
                }
            }
            await self._ws_publisher.publish(match.id, match_state)
        return MatchStateDTO.from_domain(match, changes)
