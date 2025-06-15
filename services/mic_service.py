# services/mic_service.py
from fastapi import WebSocket

class MicSender:
    def __init__(self):
        self.receivers = set()

    def register(self, websocket: WebSocket):
        self.receivers.add(websocket)

    def unregister(self, websocket: WebSocket):
        self.receivers.discard(websocket)

    async def broadcast(self, chunk: bytes):
        for ws in self.receivers.copy():
            try:
                await ws.send_bytes(chunk)
            except Exception:
                self.receivers.discard(ws)
