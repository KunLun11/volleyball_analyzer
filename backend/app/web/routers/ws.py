from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.web.ws.ws_manager import ConnectionManager

router = APIRouter(prefix="/ws")


@router.websocket("/matches/{match_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    match_id: UUID,
):
    manager = websocket.scope["app"].state.websocket_manager
    await manager.connect(websocket, match_id)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        await manager.disconnect(websocket, match_id)


@router.websocket("/matches")
async def websocket_all_matches_endpoint(
    websocket: WebSocket,
):
    manager = websocket.scope["app"].state.websocket_manager
    await manager.connect_all_matches(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        await manager.disconnect_all_matches(websocket)
