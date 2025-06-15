# ✅ audio_send: 클라이언트 → 서버로 음성 전송 (클라이언트 마이크)
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services.audio_output_service import play_audio_chunk
from datetime import datetime
from asyncio import Queue

audio_queue = Queue(maxsize=100)
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
                try:
                    chunk = await audio_queue.get()
                    play_audio_chunk(chunk)
                except Exception as e:
                    print(f"❌ 오디오 출력 중 예외 발생: {e}")
    except WebSocketDisconnect:
        print("🔌 클라이언트 마이크 연결 종료")

async def audio_output_loop():
    while True:
        chunk = await audio_queue.get()
        play_audio_chunk(chunk)