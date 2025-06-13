from fastapi import APIRouter, WebSocket
from datetime import datetime

router = APIRouter()

@router.websocket("/ws")
async def control_ws(websocket: WebSocket):
    await websocket.accept()
    print("🎮 제어 WebSocket 연결됨")
    try:
        while True:
            message = await websocket.receive_text()
            print(f"[제어 명령 수신] {message}")
            await websocket.send_text(f"명령 수신: {message}")
    except Exception as e:
        print(f"제어 연결 종료: {e}")

@router.websocket("/ws/audio")
async def audio_ws(websocket: WebSocket):
    await websocket.accept()
    print("🎤 오디오 WebSocket 연결됨")

    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"received_audio_{now}.pcm"

    try:
        with open(filename, "wb") as f:
            while True:
                chunk = await websocket.receive_bytes()
                f.write(chunk)
    except Exception as e:
        print(f"오디오 연결 종료: {e}")
