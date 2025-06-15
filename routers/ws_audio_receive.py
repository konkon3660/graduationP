# routers/ws_audio_route.py

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
from services.microphone_sender_instance import mic_streamer  # 👈 전역 객체 import

router = APIRouter()

@router.websocket("/ws/audio_receive")
async def audio_receive_ws(websocket: WebSocket):
    await websocket.accept()
    print("🔈 클라이언트 스피커 연결됨 (/ws/audio_receive)")

    mic_streamer.register(websocket)

    try:
        while True:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        print("🔌 클라이언트 스피커 연결 종료")
    finally:
        mic_streamer.unregister(websocket)
