from abc import ABC, abstractmethod
from uuid import UUID


class WebSocketPublisher(ABC):
    @abstractmethod
    async def publish(self, match_id: UUID, data: dict): ...
