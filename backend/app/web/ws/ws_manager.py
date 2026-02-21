import logging
from uuid import UUID

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self._connections: dict[UUID, list[WebSocket]] = {}
        self._all_matches_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket, match_id: UUID):
        await websocket.accept()
        self._connections.setdefault(match_id, []).append(websocket)
        logger.info(f"WS: Client connected to match {match_id}. Total connections: {len(self._connections[match_id])}")

    async def connect_all_matches(self, websocket: WebSocket):
        await websocket.accept()
        self._all_matches_connections.append(websocket)
        logger.info(f"WS: Client connected to all matches. Total connections: {len(self._all_matches_connections)}")

    async def disconnect(self, websocket: WebSocket, match_id: UUID):
        if match_id in self._connections:
            self._connections[match_id].remove(websocket)
            if not self._connections[match_id]:
                del self._connections[match_id]
            logger.info(f"WS: Client disconnected from match {match_id}. Remaining: {len(self._connections.get(match_id, []))}")

    async def disconnect_all_matches(self, websocket: WebSocket):
        if websocket in self._all_matches_connections:
            self._all_matches_connections.remove(websocket)
            logger.info(f"WS: Client disconnected from all matches. Remaining: {len(self._all_matches_connections)}")

    async def broadcast(self, match_id: UUID, data: dict):
        if match_id not in self._connections:
            logger.warning(f"WS: No subscribers for match {match_id}")
            return
        success_count = 0
        for ws in self._connections[match_id]:
            try:
                await ws.send_json(data)
                success_count += 1
            except Exception as e:
                logger.error(f"WS: Failed to send to client: {e}")
        logger.info(f"WS: Broadcast to match {match_id}: {success_count}/{len(self._connections[match_id])} clients")

    async def broadcast_all_matches(self, data: dict):
        if not self._all_matches_connections:
            logger.warning(f"WS: No subscribers for all matches")
            return
        success_count = 0
        for ws in self._all_matches_connections:
            try:
                await ws.send_json(data)
                success_count += 1
            except Exception as e:
                logger.error(f"WS: Failed to send to client: {e}")
        logger.info(f"WS: Broadcast to all matches: {success_count}/{len(self._all_matches_connections)} clients")
