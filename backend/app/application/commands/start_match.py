from dataclasses import dataclass

from app.application.exeptions import ConflictError, ValidationError
from app.application.ports.event_bus import EventBus
from app.application.ports.uow import UnitOfWork
from app.application.queries.dto import MatchDTO
from app.domain.entities.matches import Match
from app.domain.values.composites import TeamComposition
from app.domain.values.identifiers import ChatID
from app.domain.values.primitives import PlayerNumber, TeamName


@dataclass
class StartMatchCommand:
    team_a_name: str
    team_b_name: str
    composition_a: list[int]
    composition_b: list[int]
    chat_id: int


class StartMatchHandler:
    def __init__(self, uow: UnitOfWork, event_bus: EventBus):
        self._uow = uow
        self._event_bus = event_bus

    def _validate_composition(self, composition: list[int]) -> None:
        seen = set()
        for num in composition:
            if num in seen:
                raise ValidationError(f"Name has duplicate player number {num}")
            seen.add(num)

    def _validate_command(self, cmd: StartMatchCommand) -> None:
        self._validate_composition(cmd.composition_a)
        self._validate_composition(cmd.composition_b)

    async def _create_and_save_match(self, cmd: StartMatchCommand):
        team_a = TeamName(cmd.team_a_name)
        team_b = TeamName(cmd.team_b_name)
        comp_a = TeamComposition([PlayerNumber(n) for n in cmd.composition_a])
        comp_b = TeamComposition([PlayerNumber(n) for n in cmd.composition_b])
        chat_id = ChatID(cmd.chat_id)
        match = Match.start(
            team_a,
            team_b,
            comp_a,
            comp_b,
            chat_id,
        )
        await self._uow.matches().add(match)
        await self._uow.commit()
        events = match.domain_events
        match.clear_domain_events()
        await self._event_bus.publish(events)
        return match

    async def _ensure_no_live_match(self, raw_id: int) -> None:
        chat_id = ChatID(raw_id)
        existing = await self._uow.matches().get_live_by_chat(chat_id)
        if existing is not None:
            raise ConflictError(f"Chat {raw_id} already has live match")

    async def handle(self, cmd: StartMatchCommand) -> MatchDTO:
        self._validate_command(cmd)
        await self._ensure_no_live_match(cmd.chat_id)
        match = await self._create_and_save_match(cmd)
        return MatchDTO.from_domain(match)
