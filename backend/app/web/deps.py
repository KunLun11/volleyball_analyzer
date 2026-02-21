from fastapi import Depends, Request

from app.application.queries.matches import MatchQueries
from app.application.services.advice_service import AdviceService
from app.application.services.context_builder import ContextBuilder
from app.application.services.prompt_templates import PromptTemplates
from app.config import settings
from app.infrastructure.event_bus.kafka_bus import KafkaEventBus
from app.infrastructure.event_bus.rabbitmq_bus import RabbitMQEventBus
from app.infrastructure.external.ollama_client import OllamaClient
from app.infrastructure.uow.postgres_uow import PostgresUnitOfWork


def get_uow(request: Request) -> PostgresUnitOfWork:
    pool = request.app.state.postgres_pool
    return PostgresUnitOfWork(pool)


def get_event_bus(request: Request) -> KafkaEventBus:
    return request.app.state.event_bus


def get_queries(request: Request) -> MatchQueries:
    conn = request.app.state.postgres_pool
    queries = MatchQueries(conn)
    return queries


def get_uow_with_events(request: Request) -> tuple[PostgresUnitOfWork, KafkaEventBus]:
    uow = get_uow(request)
    event_bus = get_event_bus(request)
    return (uow, event_bus)


def get_ollama_client() -> OllamaClient:
    return OllamaClient(
        base_url=settings.OLLAMA_URL,
        model=settings.OLLAMA_MODEL,
        timeout=settings.OLLAMA_TIMEOUT,
        max_retries=settings.OLLAMA_MAX_RETRIES,
    )


def get_context_builder() -> ContextBuilder:
    return ContextBuilder()


def get_prompt_templates() -> PromptTemplates:
    return PromptTemplates()


def get_advice_service(
    ollama_client: OllamaClient = Depends(get_ollama_client),
    context_builder: ContextBuilder = Depends(get_context_builder),
    prompt_templates: PromptTemplates = Depends(get_prompt_templates),
) -> AdviceService:
    return AdviceService(
        ollama_client=ollama_client,
        context_builder=context_builder,
        prompt_templates=prompt_templates,
    )


def get_rabbitmq_bus() -> RabbitMQEventBus:
    return RabbitMQEventBus(settings.RABBITMQ_URL)


def get_manager(request: Request):
    return request.app.state.websocket_manager
