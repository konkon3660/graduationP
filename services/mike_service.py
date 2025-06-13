# services/mic_service.py

class MicSender:
    def __init__(self):
        self.clients = set()  # 예: WebSocket 클라이언트들

    def register(self, websocket):
        self.clients.add(websocket)

    def unregister(self, websocket):
        self.clients.discard(websocket)

    async def broadcast(self, data: bytes):
        for ws in list(self.clients):
            try:
                await ws.send_bytes(data)
            except Exception:
                self.unregister(ws)
