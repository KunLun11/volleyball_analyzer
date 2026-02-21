import dataclasses
import json
import re

from aiokafka import AIOKafkaProducer

from app.domain.events import DomainEvent
from app.infrastructure.event_bus.encoder import DomainEventEncoder


class KafkaEventBus:
    def __init__(self, bootstrap_servers: str):
        self._bootstrap_servers = bootstrap_servers
        self._producer = None
        self._started = False

    def _get_topic(self, event: DomainEvent) -> str:
        event_name = type(event).__name__
        pattern = re.compile(r"(?<!^)(?=[A-Z])")
        return pattern.sub("-", event_name).lower()

    def _serialize(self, event: DomainEvent) -> bytes:
        event_dict = dataclasses.asdict(event)
        json_bytes = json.dumps(event_dict, cls=DomainEventEncoder).encode("utf-8")
        return json_bytes

    async def start(self) -> None:
        self._producer = AIOKafkaProducer(bootstrap_servers=self._bootstrap_servers)
        await self._producer.start()
        self._started = True

    async def stop(self) -> None:
        if self._started:
            await self._producer.stop()
            self._started = False

    async def publish(self, events: list[DomainEvent]) -> None:
        if not self._started:
            await self.start()
        for event in events:
            topic = self._get_topic(event)
            data = self._serialize(event)
            await self._producer.send(topic, value=data)
        await self._producer.flush()
