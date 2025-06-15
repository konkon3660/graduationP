# ✅ audio_send: 클라이언트 → 서버로 음성 전송 (클라이언트 마이크)
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services.audio_output_service import play_audio_chunk
from datetime import datetime
import asyncio

router = APIRouter()

@router.websocket("/ws/audio_send")
async def audio_send_ws(websocket: WebSocket):
    await websocket.accept()
    print("🎤 클라이언트 마이크 연결됨 (/ws/audio_send)")

    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"received_audio_{now}.pcm"

    try:
        with open(filename, "wb") as f:
            while True:
                chunk = await websocket.receive_bytes()
                f.write(chunk)                  # 원하면 저장 생략 가능
                play_audio_chunk(chunk)         # 서버 스피커로 출력
    except WebSocketDisconnect:
        print("🔌 클라이언트 마이크 연결 종료")
