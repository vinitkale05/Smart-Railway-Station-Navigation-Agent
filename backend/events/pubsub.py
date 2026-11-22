import asyncio
import json
from typing import Dict, Set, Any
from starlette.websockets import WebSocket

class ConnectionManager:
    def __init__(self):
        # Maps session_id to set of active WebSockets
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # Global broadcast connections
        self.global_connections: Set[WebSocket] = set()

    async def connect(self, session_id: str, websocket: WebSocket):
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = set()
        self.active_connections[session_id].add(websocket)
        self.global_connections.add(websocket)

    def disconnect(self, session_id: str, websocket: WebSocket):
        if session_id in self.active_connections:
            self.active_connections[session_id].discard(websocket)
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
        self.global_connections.discard(websocket)

    async def send_to_session(self, session_id: str, message: Dict[str, Any]):
        if session_id in self.active_connections:
            dead_sockets = set()
            for ws in self.active_connections[session_id]:
                try:
                    await ws.send_text(json.dumps(message))
                except Exception:
                    dead_sockets.add(ws)
            for ws in dead_sockets:
                self.disconnect(session_id, ws)

    async def broadcast_all(self, message: Dict[str, Any]):
        dead_sockets = set()
        for ws in self.global_connections:
            try:
                await ws.send_text(json.dumps(message))
            except Exception:
                dead_sockets.add(ws)
        for ws in dead_sockets:
            self.global_connections.discard(ws)

manager = ConnectionManager()
