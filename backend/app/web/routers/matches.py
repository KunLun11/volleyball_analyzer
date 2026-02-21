from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.application.commands.end_match import (
    CompleteMatchCommand,
    CompleteMatchHandler,
)
from app.application.commands.record_event import RecordEventCommand, RecordEventHandler
from app.application.commands.start_match import StartMatchCommand, StartMatchHandler
from app.application.queries.dto import MatchDTO, MatchResultDTO, MatchStateDTO
from app.application.queries.matches import MatchQueries
from app.application.services.advice_service import AdviceService
from app.domain.values.identifiers import MatchID
from app.infrastructure.event_bus.kafka_bus import KafkaEventBus
from app.infrastructure.uow.postgres_uow import PostgresUnitOfWork
from app.web.deps import get_advice_service, get_event_bus, get_queries, get_uow
from app.web.schemas.advice import AdviceResponse
from app.web.schemas.matches import (
    CompleteMatchSchema,
    MatchResponse,
    MatchResultResponse,
    MatchStateResponse,
    RecordEventSchema,
    StartMatchSchema,
)

router = APIRouter(prefix="/matches", tags=["matches"])


@router.post("/", response_model=MatchResponse)
async def create_match(
    schema: StartMatchSchema,
    uow: PostgresUnitOfWork = Depends(get_uow),
    event_bus: KafkaEventBus = Depends(get_event_bus),
):
    async with uow:
        command = StartMatchCommand(**schema.model_dump())
        handler = StartMatchHandler(uow, event_bus)
        return await handler.handle(command)


@router.get("/live", response_model=list[MatchResponse])
async def get_live_matches(
    chat_id: Optional[int] = None,
    quieries: MatchQueries = Depends(get_queries),
):
    if chat_id:
        return await quieries.get_by_chat_id(chat_id)
    return await quieries.get_live()


@router.get("/{match_id}", response_model=MatchResponse)
async def get_match(match_id: UUID, queries: MatchQueries = Depends(get_queries)):
    result = await queries.get_by_id(match_id=match_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Match not found")
    return result


@router.post("/{match_id}/events", response_model=MatchStateResponse)
async def record_event(
    match_id: UUID,
    schema: RecordEventSchema,
    uow: PostgresUnitOfWork = Depends(get_uow),
    event_bus: KafkaEventBus = Depends(get_event_bus),
):
    async with uow:
        command = RecordEventCommand(match_id=match_id, **schema.model_dump())
        handler = RecordEventHandler(uow, event_bus)
        return await handler.handle(command)


@router.post("/{match_id}/complete", response_model=MatchResultResponse)
async def complete_match(
    match_id: UUID,
    schema: CompleteMatchSchema,
    uow: PostgresUnitOfWork = Depends(get_uow),
    event_bus: KafkaEventBus = Depends(get_event_bus),
):
    async with uow:
        command = CompleteMatchCommand(
            match_id=match_id,
            winner=schema.winner,
        )
        handler = CompleteMatchHandler(uow, event_bus)
        return await handler.handle(command)


@router.get("/{match_id}/advice", response_model=AdviceResponse)
async def get_match_advice(
    match_id: UUID,
    uow: PostgresUnitOfWork = Depends(get_uow),
    queries: MatchQueries = Depends(get_queries),
    advice_service: AdviceService = Depends(get_advice_service),
):
    match_dto = await queries.get_by_id(match_id)
    if not match_dto:
        raise HTTPException(status_code=404, detail="Match not found")

    if match_dto.status != "LIVE":
        raise HTTPException(status_code=400, detail="Match is not live")

    match = await uow.matches().get(MatchID(match_id))

    # Получить совет
    advice = await advice_service.get_advice(match)

    return AdviceResponse(
        advice=advice.text,
        generated_at=advice.generated_at,
        match_id=match_id,
    )
