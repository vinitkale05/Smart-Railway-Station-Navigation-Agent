from starlette.websockets import WebSocket, WebSocketDisconnect
from backend.events.pubsub import manager

async def websocket_session_endpoint(websocket: WebSocket):
    session_id = websocket.path_params["id"]
    await manager.connect(session_id, websocket)
    try:
        # Send initial confirmation event
        await websocket.send_json({
            "event_type": "connected",
            "title": "Connected to Live Station Dispatch",
            "message": f"Real-time alerts active for session {session_id}.",
            "data": {"session_id": session_id}
        })
        while True:
            # Keep connection alive & accept any client ping/pongs
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(session_id, websocket)
    except Exception:
        manager.disconnect(session_id, websocket)
