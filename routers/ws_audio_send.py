# ✅ audio_send: 클라이언트 → 서버로 음성 전송 (클라이언트 마이크)
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services.audio_output_service import play_audio_chunk
from datetime import datetime
from queue import Queue

audio_queue = Queue()
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
                f.write(chunk)
                audio_queue.put(chunk)  # ✅ 올바르게 큐에 추가
    except WebSocketDisconnect:
        print("🔌 클라이언트 마이크 연결 종료")

async def audio_output_loop():
    import asyncio
    loop = asyncio.get_event_loop()
    while True:
        try:
            # ✅ blocking read → 비동기 wait으로 감싸기
            chunk = await loop.run_in_executor(None, audio_queue.get)
            play_audio_chunk(chunk)
        except Exception as e:
            print(f"❌ 오디오 출력 오류: {e}")