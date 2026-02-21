from dataclasses import dataclass
from uuid import UUID

from app.application.exeptions import ConflictError, NotFoundError
from app.application.ports.uow import UnitOfWork
from app.application.queries.dto import AdviceDTO
from app.application.services.advice_service import AdviceService
from app.config import settings
from app.domain.enums import MatchStatusEnum
from app.domain.values.identifiers import MatchID
from app.infrastructure.event_bus.rabbitmq_bus import RabbitMQEventBus


@dataclass
class RequestAdviceCommand:
    match_id: UUID
    chat_id: int
    correlation_id: str
    reply_to: str


class RequestAdviceHandler:
    def __init__(
        self,
        uow: UnitOfWork,
        advice_service: AdviceService,
        event_bus: RabbitMQEventBus,
    ):
        self._uow = uow
        self._advice_service = advice_service
        self._event_bus = event_bus

    async def handle(self, cmd: RequestAdviceCommand) -> AdviceDTO:
        match = await self._uow.matches().get(MatchID(cmd.match_id))
        if not match:
            raise NotFoundError("Match not found")
        if match.status != MatchStatusEnum.LIVE:
            raise ConflictError("Match not live")

        advice = await self._advice_service.build(match)
        await self._event_bus.publish_to_bot(
            chat_id=cmd.chat_id,
            advice=advice.text,
            correlation_id=cmd.correlation_id,
            match_id=str(cmd.match_id),
            reply_to=cmd.reply_to,
        )
        return AdviceDTO(
            match_id=cmd.match_id,
            advice=advice.text,
            generated_at=advice.generated_at,
        )
