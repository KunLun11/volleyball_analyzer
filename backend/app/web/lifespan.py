import asyncio
import json
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from uuid import UUID

import aio_pika
import asynch
import asyncpg
from fastapi import FastAPI

from app.application.commands.request_advice import (
    RequestAdviceCommand,
    RequestAdviceHandler,
)
from app.application.commands.start_match import StartMatchCommand, StartMatchHandler
from app.application.services.advice_service import AdviceService
from app.application.services.context_builder import ContextBuilder
from app.application.services.prompt_templates import PromptTemplates
from app.config import settings
from app.domain.values.identifiers import ChatID, MatchID
from app.infrastructure.event_bus.kafka_bus import KafkaEventBus
from app.infrastructure.event_bus.rabbitmq_bus import RabbitMQEventBus
from app.infrastructure.external.ollama_client import OllamaClient, OpenAIClient
from app.infrastructure.uow.postgres_uow import PostgresUnitOfWork
from app.web.ws.ws_manager import ConnectionManager
from app.web.ws.ws_publisher import FastAPIWebSocketPublisher

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.postgres_pool = await asyncpg.create_pool(dsn=settings.POSTGRES_URL)

    app.state.event_bus = KafkaEventBus(settings.KAFKA_URL)
    await app.state.event_bus.start()

    conn = asynch.Connection(
        host=settings.CLICKHOUSE_HOST,
        port=settings.CLICKHOUSE_PORT,
        database=settings.CLICKHOUSE_DB,
        CLICKHOUSE_USER=settings.CLICKHOUSE_USER,
        CLICKHOUSE_PASSWORD=settings.CLICKHOUSE_PASSWORD,
    )
    await conn.connect()
    app.state.clickhouse_conn = conn

    if settings.LLM_TYPE == "openai":
        llm_client = OpenAIClient(
            base_url=settings.OPENAI_BASE_URL,
            api_key=settings.OPENAI_API_KEY,
            model=settings.OPENAI_MODEL,
            timeout=settings.OPENAI_TIMEOUT,
            max_retries=settings.OPENAI_MAX_RETRIES,
            max_tokens=settings.OPENAI_MAX_TOKENS,
        )
        logger.info("OpenAI client created")
        if not await llm_client.health():
            logger.warning("OpenAI API not available, AI advice will use fallback")
    else:
        llm_client = OllamaClient(
            base_url=settings.OLLAMA_URL,
            model=settings.OLLAMA_MODEL,
            timeout=settings.OLLAMA_TIMEOUT,
            max_retries=settings.OLLAMA_MAX_RETRIES,
        )
        logger.info("Ollama client created")
        model_ready = await llm_client.ensure_model()
        if not model_ready:
            logger.warning("Ollama not available, AI advice will use fallback")
        else:
            logger.info("Ollama ready, model loaded")

    app.state.llm_client = llm_client

    context_builder = ContextBuilder()
    prompt_templates = PromptTemplates()
    app.state.context_builder = context_builder
    app.state.prompt_templates = prompt_templates

    advice_service = AdviceService(
        llm_client=llm_client,
        context_builder=context_builder,
        prompt_templates=prompt_templates,
        config=settings,
    )
    app.state.advice_service = advice_service

    rabbitmq_bus = RabbitMQEventBus(settings.RABBITMQ_URL)
    await rabbitmq_bus.start()
    app.state.rabbitmq_bus = rabbitmq_bus
    logger.info("RabbitMQ event bus started")

    async def handle_bot_request(payload: dict, message):
        logger.info(f"ПОЛУЧЕН ЗАПРОС: {payload.get('action')}")
        logger.info(f"Полный payload: {payload}")

        try:
            action = payload.get("action")
            correlation_id = payload.get("correlation_id")
            reply_to = payload.get("reply_to")

            if not action:
                logger.error(f"Missing action in payload: {payload}")
                return

            if not correlation_id or not reply_to:
                logger.error(f"Missing correlation_id or reply_to: {payload}")
                return

            if action == "get_live_match":
                chat_id = payload.get("chat_id")
                if not chat_id:
                    logger.error(f"Missing chat_id in payload: {payload}")
                    error_response = {
                        "correlation_id": correlation_id,
                        "error": "Missing chat_id",
                        "matches": [],
                    }
                    await rabbitmq_bus._channel.default_exchange.publish(
                        aio_pika.Message(
                            body=json.dumps(error_response).encode(),
                            correlation_id=correlation_id,
                            content_type="application/json",
                        ),
                        routing_key=reply_to,
                    )
                    return

                async with PostgresUnitOfWork(app.state.postgres_pool) as uow:
                    chat_id_obj = ChatID(chat_id)
                    match = await uow.matches().get_live_by_chat(chat_id_obj)

                if match:
                    composition_a = [p.value for p in match.composition_a.get_players()]
                    composition_b = [p.value for p in match.composition_b.get_players()]

                    match_data = {
                        "id": str(match.id.value),
                        "team_a_name": match.team_a_name.value,
                        "team_b_name": match.team_b_name.value,
                        "composition_a": composition_a,
                        "composition_b": composition_b,
                        "status": match.status.name,
                        "created_at": match.created_at.isoformat(),
                        "current_set": match.current_set.value,
                        "score_a": match.score.a.value,
                        "score_b": match.score.b.value,
                        "rotation_a": match.rotation.team_a.value,
                        "rotation_b": match.rotation.team_b.value,
                    }
                    matches_list = [match_data]
                else:
                    matches_list = []

                response_payload = {
                    "correlation_id": correlation_id,
                    "matches": matches_list,
                }

                await rabbitmq_bus._channel.default_exchange.publish(
                    aio_pika.Message(
                        body=json.dumps(response_payload).encode(),
                        correlation_id=correlation_id,
                        content_type="application/json",
                    ),
                    routing_key=reply_to,
                )

            elif action == "create_match":
                team_a_name = payload.get("team_a_name")
                team_b_name = payload.get("team_b_name")
                composition_a = payload.get("composition_a")
                composition_b = payload.get("composition_b")
                chat_id = payload.get("chat_id")

                if not all(
                    [team_a_name, team_b_name, composition_a, composition_b, chat_id]
                ):
                    logger.error(f"Missing required fields in payload: {payload}")
                    error_response = {
                        "correlation_id": correlation_id,
                        "error": "Missing required fields",
                    }
                    await rabbitmq_bus._channel.default_exchange.publish(
                        aio_pika.Message(
                            body=json.dumps(error_response).encode(),
                            correlation_id=correlation_id,
                            content_type="application/json",
                        ),
                        routing_key=reply_to,
                    )
                    return

                try:
                    async with PostgresUnitOfWork(app.state.postgres_pool) as uow:
                        handler = StartMatchHandler(uow, rabbitmq_bus)
                        cmd = StartMatchCommand(
                            team_a_name=team_a_name,
                            team_b_name=team_b_name,
                            composition_a=composition_a,
                            composition_b=composition_b,
                            chat_id=chat_id,
                        )
                        result = await handler.handle(cmd)

                    match_data = {
                        "id": str(result.id),
                        "team_a_name": result.team_a_name,
                        "team_b_name": result.team_b_name,
                        "composition_a": result.composition_a,
                        "composition_b": result.composition_b,
                        "status": result.status,
                        "created_at": result.created_at.isoformat(),
                        "current_set": result.current_set,
                        "score_a": result.score_a,
                        "score_b": result.score_b,
                    }

                    response_payload = {
                        "correlation_id": correlation_id,
                        "match": match_data,
                    }

                    await rabbitmq_bus._channel.default_exchange.publish(
                        aio_pika.Message(
                            body=json.dumps(response_payload).encode(),
                            correlation_id=correlation_id,
                            content_type="application/json",
                        ),
                        routing_key=reply_to,
                    )
                except Exception as e:
                    logger.error(f"Error creating match: {e}")
                    error_response = {
                        "correlation_id": correlation_id,
                        "error": str(e),
                    }
                    await rabbitmq_bus._channel.default_exchange.publish(
                        aio_pika.Message(
                            body=json.dumps(error_response).encode(),
                            correlation_id=correlation_id,
                            content_type="application/json",
                        ),
                        routing_key=reply_to,
                    )

            elif action == "request_advice":
                match_id = payload.get("match_id")
                chat_id = payload.get("chat_id")
                if not match_id or not chat_id:
                    logger.error(f"Missing match_id or chat_id: {payload}")
                    return

                async with PostgresUnitOfWork(app.state.postgres_pool) as uow:
                    advice_service = app.state.advice_service
                    handler = RequestAdviceHandler(
                        uow=uow,
                        advice_service=advice_service,
                        event_bus=rabbitmq_bus,
                    )

                    cmd = RequestAdviceCommand(
                        match_id=UUID(match_id),
                        chat_id=chat_id,
                        correlation_id=correlation_id,
                        reply_to=reply_to,
                    )

                    await handler.handle(cmd)
                    logger.info(f"Advice request processed: {correlation_id}")

            elif action == "record_event":
                from app.application.commands.record_event import (
                    RecordEventCommand,
                    RecordEventHandler,
                )
                from app.application.exeptions import ConflictError, NotFoundError
                from app.infrastructure.event_bus.kafka_bus import KafkaEventBus

                kafka_bus = app.state.event_bus
                match_id = payload.get("match_id")
                if not match_id:
                    logger.error(f"Missing match_id: {payload}")
                    error_response = {
                        "correlation_id": correlation_id,
                        "error": "Missing match_id",
                        "match_state": None,
                    }
                    await rabbitmq_bus._channel.default_exchange.publish(
                        aio_pika.Message(
                            body=json.dumps(error_response).encode(),
                            correlation_id=correlation_id,
                            content_type="application/json",
                        ),
                        routing_key=reply_to,
                    )
                    return

                timestamp_str = payload.get("timestamp")
                if timestamp_str:
                    timestamp = datetime.fromisoformat(timestamp_str)
                    if timestamp.tzinfo is None:
                        timestamp = timestamp.replace(tzinfo=timezone.utc)
                else:
                    timestamp = None

                cmd = RecordEventCommand(
                    match_id=UUID(match_id),
                    player_number=payload["player_number"],
                    team_id=payload["team_id"],
                    action_type=payload["action_type"],
                    result=payload["result"],
                    timestamp=timestamp,
                )

                try:
                    ws_publisher = app.state.ws_publisher
                    async with PostgresUnitOfWork(app.state.postgres_pool) as uow:
                        handler = RecordEventHandler(uow, kafka_bus, ws_publisher)
                        result = await handler.handle(cmd)

                    response_payload = {
                        "correlation_id": correlation_id,
                        "match_state": {
                            "match_id": str(result.match_id),
                            "status": result.status,
                            "current_set": result.current_set,
                            "score_a": result.score_a,
                            "score_b": result.score_b,
                            "rotation_a": result.rotation_a,
                            "rotation_b": result.rotation_b,
                            "changes": result.changes,
                        },
                    }
                except ConflictError as e:
                    logger.warning(f"ConflictError: {e}")
                    response_payload = {
                        "correlation_id": correlation_id,
                        "error": str(e),
                        "match_state": {
                            "status": "COMPLETED",
                            "error": "match_completed",
                        },
                    }
                except NotFoundError as e:
                    logger.warning(f"NotFoundError: {e}")
                    response_payload = {
                        "correlation_id": correlation_id,
                        "error": str(e),
                        "match_state": None,
                    }
                except Exception as e:
                    logger.error(f"Unexpected error: {e}")
                    response_payload = {
                        "correlation_id": correlation_id,
                        "error": f"Internal error: {str(e)}",
                        "match_state": None,
                    }

                await rabbitmq_bus._channel.default_exchange.publish(
                    aio_pika.Message(
                        body=json.dumps(response_payload).encode(),
                        correlation_id=correlation_id,
                        content_type="application/json",
                    ),
                    routing_key=reply_to,
                )

            elif action == "complete_match":
                from app.application.commands.end_match import (
                    CompleteMatchCommand,
                    CompleteMatchHandler,
                )
                from app.infrastructure.event_bus.kafka_bus import KafkaEventBus

                match_id = payload.get("match_id")
                if not match_id:
                    logger.error(f"Missing match_id: {payload}")
                    return
                kafka_bus = app.state.event_bus

                ws_publisher = app.state.ws_publisher
                async with PostgresUnitOfWork(app.state.postgres_pool) as uow:
                    cmd = CompleteMatchCommand(
                        match_id=UUID(match_id), winner=payload.get("winner")
                    )

                    handler = CompleteMatchHandler(uow, kafka_bus, ws_publisher)
                    result = await handler.handle(cmd)

                    response_payload = {
                        "correlation_id": correlation_id,
                        "result": {
                            "match_id": str(result.match_id),
                            "winner": result.winner,
                            "total_sets": result.total_sets,
                            "set_scores": result.set_scores,
                            "team_a_name": result.team_a_name,
                            "team_b_name": result.team_b_name,
                        },
                    }

                    await rabbitmq_bus._channel.default_exchange.publish(
                        aio_pika.Message(
                            body=json.dumps(response_payload).encode(),
                            correlation_id=correlation_id,
                            content_type="application/json",
                        ),
                        routing_key=reply_to,
                    )

            elif action == "get_match":
                from app.application.queries.matches import MatchQueries

                match_id = payload.get("match_id")
                if not match_id:
                    logger.error(f"Missing match_id in get_match payload: {payload}")
                    error_response = {
                        "correlation_id": correlation_id,
                        "error": "Missing match_id",
                        "match": None,
                    }
                    await rabbitmq_bus._channel.default_exchange.publish(
                        aio_pika.Message(
                            body=json.dumps(error_response).encode(),
                            correlation_id=correlation_id,
                            content_type="application/json",
                        ),
                        routing_key=reply_to,
                    )
                    return

                try:
                    queries = MatchQueries(app.state.postgres_pool)
                    match_dto = await queries.get_by_id(UUID(match_id))
                except Exception as e:
                    logger.error(f"Error fetching match {match_id}: {e}")
                    error_response = {
                        "correlation_id": correlation_id,
                        "error": f"Match not found: {e}",
                        "match": None,
                    }
                    await rabbitmq_bus._channel.default_exchange.publish(
                        aio_pika.Message(
                            body=json.dumps(error_response).encode(),
                            correlation_id=correlation_id,
                            content_type="application/json",
                        ),
                        routing_key=reply_to,
                    )
                    return

                response_payload = {
                    "correlation_id": correlation_id,
                    "match": {
                        "id": str(match_dto.id),
                        "team_a_name": match_dto.team_a_name,
                        "team_b_name": match_dto.team_b_name,
                        "composition_a": match_dto.composition_a,
                        "composition_b": match_dto.composition_b,
                        "status": match_dto.status,
                        "created_at": match_dto.created_at.isoformat(),
                        "current_set": match_dto.current_set,
                        "score_a": match_dto.score_a,
                        "score_b": match_dto.score_b,
                    }
                    if match_dto
                    else None,
                }

                await rabbitmq_bus._channel.default_exchange.publish(
                    aio_pika.Message(
                        body=json.dumps(response_payload).encode(),
                        correlation_id=correlation_id,
                        content_type="application/json",
                    ),
                    routing_key=reply_to,
                )

            else:
                logger.warning(f"Unknown action: {action}")
                return

        except Exception as e:
            logger.error(f"Error handling bot request: {e}", exc_info=True)
            return

    asyncio.create_task(rabbitmq_bus.consume_bot_requests(handle_bot_request))
    logger.info("RabbitMQ consumer started for bot.to.backend")

    websocket_manager = ConnectionManager()
    app.state.websocket_manager = websocket_manager
    ws_publisher = FastAPIWebSocketPublisher(websocket_manager)
    app.state.ws_publisher = ws_publisher

    logger.info("WebSocket initialized")

    logger.info("Application started")
    yield

    if hasattr(app.state, "rabbitmq_bus"):
        await app.state.rabbitmq_bus.stop_consuming()
        await app.state.rabbitmq_bus.stop()
        logger.info("RabbitMQ stopped")

    if hasattr(app.state, "event_bus"):
        await app.state.event_bus.stop()
        logger.info("Kafka event bus stopped")

    if hasattr(app.state, "clickhouse_conn"):
        await app.state.clickhouse_conn.close()
        logger.info("ClickHouse disconnected")

    if hasattr(app.state, "postgres_pool"):
        await app.state.postgres_pool.close()
        logger.info("PostgreSQL disconnected")
    logger.info("Application stopped")
