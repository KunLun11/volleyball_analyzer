import logging
from uuid import UUID

from app.application.ports.websocket_publisher import WebSocketPublisher
from app.web.ws.ws_manager import ConnectionManager

logger = logging.getLogger(__name__)


class FastAPIWebSocketPublisher(WebSocketPublisher):
    def __init__(self, manager: ConnectionManager):
        self._manager = manager

    async def publish(self, match_id: UUID, data: dict):
        logger.info(f"WS: Publishing to match {match_id}: {data}")
        await self._manager.broadcast(match_id, data)
        
        broadcast_data = {
            "type": "match_update",
            "match_id": str(match_id),
            "data": data
        }
        logger.info(f"WS: Broadcasting to all: {broadcast_data}")
        await self._manager.broadcast_all_matches(broadcast_data)
