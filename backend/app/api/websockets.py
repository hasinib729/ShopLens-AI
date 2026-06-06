from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List
import json

router = APIRouter(tags=["websockets"])

class ConnectionManager:
    def __init__(self):
        # Maps session_id to list of active WebSocket connections
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
        self.active_connections[session_id].append(websocket)
        print(f"WebSocket connected for session: {session_id}")

    def disconnect(self, websocket: WebSocket, session_id: str):
        if session_id in self.active_connections:
            if websocket in self.active_connections[session_id]:
                self.active_connections[session_id].remove(websocket)
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
        print(f"WebSocket disconnected for session: {session_id}")

    def broadcast_to_session(self, session_id: str, data: dict):
        """Sends data payload to all connections associated with the session_id."""
        if session_id in self.active_connections:
            import asyncio
            message = json.dumps(data)
            for connection in self.active_connections[session_id]:
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        asyncio.run_coroutine_threadsafe(connection.send_text(message), loop)
                    else:
                        loop.run_until_complete(connection.send_text(message))
                except Exception as e:
                    # Quietly ignore connection send errors
                    pass

websocket_manager = ConnectionManager()

@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket_manager.connect(websocket, session_id)
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            # Echo or process incoming ping
            await websocket.send_text(json.dumps({"status": "ping_received"}))
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket, session_id)
    except Exception as e:
        print(f"WebSocket error for session {session_id}: {e}")
        websocket_manager.disconnect(websocket, session_id)
