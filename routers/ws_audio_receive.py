# routers/ws_audio_route.py
import anasyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services.audio_output_service import play_audio_chunk
from services.audio_service import get_audio_streaming

router = APIRouter()

@router.websocket("/ws/audio_receive")
async def audio_receive_ws(websocket: WebSocket):
    await websocket.accept()
    print("🔈 클라이언트 스피커 연결됨 (/ws/audio_receive)")

    try:
        while True:
            data = await websocket.receive_bytes()

            if get_audio_streaming():
                play_audio_chunk(data)

    except WebSocketDisconnect:
        print("🔌 클라이언트 스피커 연결 종료")

    except asyncio.CancelledError:
        print("🛑 서버 종료로 인해 클라이언트 오디오 수신 종료됨")

    finally:
        print("❎ 클라이언트 해제됨")

